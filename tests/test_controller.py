"""Tests for the FlowKit Codex workflow controller helper."""

from __future__ import annotations

import importlib.util
import json
import os
import io
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import yaml


ROOT = Path(__file__).parents[1]
CONTROLLER_DIR = ROOT / "controllers/flow-kit/scripts/python"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def find_workflow_step(steps: list[dict], step_id: str) -> dict:
    for step in steps:
        if step.get("id") == step_id:
            return step
        nested = list(step.get("steps", []))
        for branch in step.get("cases", {}).values():
            nested.extend(branch)
        nested.extend(step.get("default", []))
        try:
            return find_workflow_step(nested, step_id)
        except StopIteration:
            pass
    raise StopIteration(step_id)


class RuntimeDiscoveryTests(unittest.TestCase):
    """Runtime discovery must fail closed before loading a workflow."""

    def setUp(self) -> None:
        self.controller = load_module("flowkit_controller_runtime", CONTROLLER_DIR / "controller.py")

    def test_locateRuntime_prefersMiseSelectedExecutable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            selected = Path(temporary) / "mise-specify"
            other = Path(temporary) / "path-specify"
            selected.write_text("#!/bin/sh\n", encoding="utf-8")
            other.write_text("#!/bin/sh\n", encoding="utf-8")
            selected.chmod(0o755)
            other.chmod(0o755)
            self.assertEqual(selected, self.controller.select_specify_executable(selected, [selected, other]))

    def test_locateRuntime_acceptsOneOrdinaryExecutable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            selected = Path(temporary) / "specify"
            selected.write_text("#!/bin/sh\n", encoding="utf-8")
            selected.chmod(0o755)
            self.assertEqual(selected, self.controller.select_specify_executable(None, [selected]))

    def test_locateRuntime_rejectsMissingOrAmbiguousExecutables(self) -> None:
        with self.assertRaisesRegex(ValueError, "not found"):
            self.controller.select_specify_executable(None, [])
        with tempfile.TemporaryDirectory() as temporary:
            first = Path(temporary) / "first"
            second = Path(temporary) / "second"
            first.write_text("#!/bin/sh\n", encoding="utf-8")
            second.write_text("#!/bin/sh\n", encoding="utf-8")
            first.chmod(0o755)
            second.chmod(0o755)
            with self.assertRaisesRegex(ValueError, "ambiguous"):
                self.controller.select_specify_executable(None, [first, second])

    def test_locateRuntime_rejectsVersionMismatch(self) -> None:
        with self.assertRaisesRegex(ValueError, "expected Specify"):
            self.controller.check_specify_version("specify 1.0.9", "1.0.10.dev0+pegagio.2")


class InstalledDefinitionTests(unittest.TestCase):
    """The controller reads the composed definition without native execution."""

    def setUp(self) -> None:
        self.controller = load_module("flowkit_controller_definition", CONTROLLER_DIR / "controller.py")

    def test_loadDefinition_usesSelectedProjectAndReturnsProvenance(self) -> None:
        selected = Path("/consumer/project")
        definition = {"workflow": {"id": "speckit-flow-tasks", "version": "0.2.0"}, "steps": []}
        with patch.object(self.controller, "WorkflowEngine") as engine_class:
            engine_class.return_value.load_workflow.return_value = type(
                "Definition", (), {"data": definition, "source_path": Path("/consumer/project/.specify/workflows/tasks/workflow.yml"), "version": "0.2.0"}
            )()
            result = self.controller.load_installed_definition(selected, "speckit-flow-tasks")
        engine_class.assert_called_once_with(selected)
        engine_class.return_value.load_workflow.assert_called_once_with("speckit-flow-tasks")
        self.assertEqual("0.2.0", result["version"])
        self.assertEqual("speckit-flow-tasks", result["workflow"]["id"])
        self.assertTrue(result["source_path"].endswith("workflow.yml"))

    def test_loadDefinition_neverExecutesNativeWorkflow(self) -> None:
        with patch.object(self.controller, "WorkflowEngine") as engine_class:
            engine = engine_class.return_value
            engine.load_workflow.return_value = type(
                "Definition", (), {"data": {"workflow": {"id": "test", "version": "1"}, "steps": []}, "source_path": Path("workflow.yml"), "version": "1"}
            )()
            self.controller.load_installed_definition(Path("/consumer"), "test")
            engine.execute.assert_not_called()

    def test_fingerprint_recordsContentAndFileIdentity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "record.json"
            path.write_text("{}", encoding="utf-8")
            result = self.controller.file_fingerprint(path)
        self.assertEqual({"sha256", "device", "inode"}, set(result))

    def test_verifyInstall_requiresInstalledBindingAndUnchangedHelper(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            paths = [
                ".agents/skills/flow-kit-tasks/SKILL.md",
                ".agents/skills/flow-kit-tasks/agents/openai.yaml",
                ".specify/flow-kit/manifest.yml",
                ".specify/flow-kit/controller-protocol.md",
                ".specify/flow-kit/scripts/bootstrap.sh",
                ".specify/flow-kit/scripts/python/controller.py",
                ".specify/flow-kit/scripts/python/recovery.py",
            ]
            files = {}
            for relative in paths:
                target = project / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                content = f"name: flow-kit-tasks\n" if relative.endswith("SKILL.md") else "fixture\n"
                if relative.endswith("manifest.yml"):
                    content = 'package:\n  version: "0.1.0"\n'
                target.write_text(content, encoding="utf-8")
                files[relative] = __import__("hashlib").sha256(content.encode()).hexdigest()
            record = {
                "package": "flow-kit-controllers", "version": "0.1.0", "status": "installed", "files": files,
                "controllers": [{"skill_id": "flow-kit-tasks", "workflow_id": "speckit-flow-tasks"}],
            }
            record_path = project / ".specify/flow-kit/skills-install.json"
            record_path.write_text(json.dumps(record), encoding="utf-8")
            self.controller.verify_controller_install(project, "flow-kit-tasks", "speckit-flow-tasks")
            (project / paths[0]).write_text("changed", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "was changed"):
                self.controller.verify_controller_install(project, "flow-kit-tasks", "speckit-flow-tasks")


class NamedAgentAssignmentTests(unittest.TestCase):
    """Delegated steps resolve only to their reviewed native Codex agent names."""

    def setUp(self) -> None:
        self.controller = load_module("flowkit_controller_agents", CONTROLLER_DIR / "controller.py")

    def test_collectAgentAssignments_preservesDistinctNamesPerStep(self) -> None:
        steps = [
            {"id": "edit", "type": "prompt", "flow_kit": {"delegated": True, "agent": "FlowKit-Coder"}},
            {"id": "review", "type": "command", "flow_kit": {"delegated": True, "agent": "FlowKit-Reviewer"}},
            {"id": "summary", "type": "prompt", "prompt": "Summarize in the main task."},
        ]
        assignments = self.controller.collect_agent_assignments(steps)
        self.assertEqual(
            [
                self.controller.StepAssignmentIntent("edit", "FlowKit-Coder"),
                self.controller.StepAssignmentIntent("review", "FlowKit-Reviewer"),
            ],
            assignments,
        )

    def test_collectAgentAssignments_includesDelegatedStepsInEveryBranch(self) -> None:
        steps = [
            {
                "id": "route",
                "type": "switch",
                "cases": {"review": [{"id": "verify", "type": "prompt", "flow_kit": {"delegated": True, "agent": "FlowKit-Reviewer"}}]},
                "default": [{"id": "build", "type": "prompt", "flow_kit": {"delegated": True, "agent": "FlowKit-Code Reviewer"}}],
            }
        ]
        assignments = self.controller.collect_agent_assignments(steps)
        self.assertEqual(
            [("verify", "FlowKit-Reviewer"), ("build", "FlowKit-Code Reviewer")],
            [(row.step_id, row.agent_name) for row in assignments],
        )

    def test_inspectRejectsPerRunAssignmentOverrides(self) -> None:
        with redirect_stdout(io.StringIO()), patch("sys.stderr", io.StringIO()), patch.object(
            self.controller, "verify_controller_install", side_effect=AssertionError("preflight must not run")
        ), self.assertRaises(SystemExit) as error:
            self.controller.main(
                [
                    "inspect",
                    "--project", "/consumer",
                    "--workflow-id", "speckit-flow-tasks",
                    "--specify", "/usr/bin/specify",
                    "--expected-version", "1.0.10.dev0+pegagio.2",
                    "--skill-id", "flow-kit-tasks",
                    "--override", "agent=FlowKit-Coder",
                ]
            )
        self.assertEqual(2, error.exception.code)


class GraphPreflightTests(unittest.TestCase):
    """Graph validation covers nested branches before any execution starts."""

    def setUp(self) -> None:
        self.controller = load_module("flowkit_controller_graph", CONTROLLER_DIR / "controller.py")
        self.workflow = {
            "inputs": {"feature_context": {"required": True}},
            "steps": [
                {"id": "delegated-prompt", "type": "prompt", "flow_kit": {"delegated": True, "agent": "FlowKit-Coder"}},
                {"id": "review-verdict", "type": "gate", "options": ["approve", "defer"]},
                {"id": "route-result", "type": "switch", "cases": {"primary": [
                    {"id": "nested-delegated-command", "command": "speckit.fixture", "flow_kit": {"delegated": True, "agent": "FlowKit-Reviewer"}}
                ]}, "default": [
                    {"id": "alternate-agent", "type": "prompt", "flow_kit": {"delegated": True, "agent": "FlowKit-Code Reviewer"}}
                ]},
            ],
        }

    def test_collectAgentAssignments_includesUntakenNestedBranches(self) -> None:
        assignments = self.controller.collect_agent_assignments(self.workflow["steps"])
        self.assertEqual(
            [("delegated-prompt", "FlowKit-Coder"), ("nested-delegated-command", "FlowKit-Reviewer"), ("alternate-agent", "FlowKit-Code Reviewer")],
            [(item.step_id, item.agent_name) for item in assignments],
        )

    def test_requiredInputs_failBeforeWorkflowExecution(self) -> None:
        with self.assertRaisesRegex(ValueError, "feature_context"):
            self.controller.validate_required_inputs(self.workflow, {})

    def test_requiredInputs_rejectBlankValues(self) -> None:
        for value in ("", "  "):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "feature_context"):
                self.controller.validate_required_inputs(self.workflow, {"feature_context": value})

    def test_validateDefinition_rejectsUnsupportedTemplateInLaterBranch(self) -> None:
        definition = {
            "workflow": {"id": "probe", "version": "1.0"},
            "inputs": {"feature_context": {"required": True, "type": "string"}},
            "steps": [
                {"id": "first", "type": "prompt", "prompt": "Start {{ inputs.feature_context }}"},
                {"id": "route", "type": "switch", "expression": "{{ steps.first.output.choice }}", "cases": {
                    "later": [{"id": "bad", "type": "prompt", "prompt": "{{ unsupported.value }}"}],
                }},
            ],
        }
        with self.assertRaisesRegex(ValueError, "unsupported template"):
            self.controller.validate_workflow_definition(definition)

    def test_validateGraph_rejectsDuplicateStepIDs(self) -> None:
        graph = [{"id": "same", "type": "prompt"}, {"id": "route", "type": "switch", "cases": {"a": [{"id": "same", "type": "prompt"}]}}]
        with self.assertRaisesRegex(ValueError, "duplicate step id"):
            self.controller.validate_workflow_graph(graph)

    def test_validateGraph_rejectsConcreteModelDispatchSettings(self) -> None:
        for node in (
            {"id": "gate-model", "type": "gate", "model": "gpt-6-sol"},
            {"id": "switch-effort", "type": "switch", "reasoning_effort": "high", "cases": {}},
            {"id": "legacy-model", "type": "prompt", "model": "gpt-6-sol"},
        ):
            with self.subTest(node=node), self.assertRaisesRegex(ValueError, "concrete model"):
                self.controller.validate_workflow_graph([node])

    def test_resolveSkill_usesPinnedCommandNamingAndChecksDeclaredName(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill_dir = Path(temporary) / ".agents/skills/speckit-flow-wiki-ingest"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("---\nname: speckit-flow-wiki-ingest\n---\n", encoding="utf-8")
            result = self.controller.resolve_installed_skill(Path(temporary), "speckit.flow-wiki.ingest")
        self.assertEqual("speckit-flow-wiki-ingest", result["name"])

    def test_resolveSkill_failsClosedWhenMissingOrMismatched(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "not found"):
                self.controller.resolve_installed_skill(Path(temporary), "speckit.tasks")
            skill_dir = Path(temporary) / ".agents/skills/speckit-tasks"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("---\nname: unrelated\n---\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "different name"):
                self.controller.resolve_installed_skill(Path(temporary), "speckit.tasks")

    def test_agentMigration_rejectsOldNamesEvenInUntakenNestedBranches(self) -> None:
        for name in ("Roadmap Agent", "Specifier", "Planner", "Tasker", "Reviewer", "Coder", "Code Reviewer", "Wiki Curator"):
            graph = [{"id": "route", "type": "switch", "cases": {"taken": []}, "default": [
                {"id": "old-agent", "type": "prompt", "flow_kit": {"delegated": True, "agent": name}}
            ]}]
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "old-agent"):
                self.controller.collect_agent_assignments(graph)

    def test_validateDefinition_rejectsWorkflowLevelAgentDefaults(self) -> None:
        definition = {"workflow": {"id": "test", "version": "1.0", "agent": "FlowKit-Coder"}, "steps": []}
        with self.assertRaisesRegex(ValueError, "workflow-level"):
            self.controller.validate_workflow_definition(definition)

    def test_delegationBoundary_keepsMainTaskStepAndGateOutOfChildAssignments(self) -> None:
        graph = [
            {"id": "main-work", "type": "prompt", "prompt": "summarize"},
            {"id": "delegated-work", "type": "prompt", "flow_kit": {"delegated": True, "agent": "FlowKit-Coder"}},
            {"id": "human-review", "type": "gate", "options": ["continue"]},
        ]
        assignments = self.controller.collect_agent_assignments(graph)
        self.assertEqual([("delegated-work", "FlowKit-Coder")], [(item.step_id, item.agent_name) for item in assignments])

    def test_delegationBoundary_rejectsAgentOnNonDelegatedStepAndDelegatedGate(self) -> None:
        for graph in (
            [{"id": "main-work", "type": "prompt", "agent": "FlowKit-Coder"}],
            [{"id": "human-review", "type": "gate", "flow_kit": {"delegated": True, "agent": "FlowKit-Reviewer"}}],
            [{"id": "route", "type": "switch", "flow_kit": {"delegated": True, "agent": "FlowKit-Reviewer"}, "cases": {}}],
        ):
            with self.subTest(graph=graph), self.assertRaises(ValueError):
                self.controller.validate_workflow_graph(graph)

    def test_agentPreflight_rejectsMissingUnknownMalformedAndLegacyAssignmentsAcrossBranches(self) -> None:
        invalid_graphs = (
            ([{"id": "missing-agent", "type": "prompt", "flow_kit": {"delegated": True}}], "missing-agent"),
            ([{"id": "unknown-agent", "type": "prompt", "flow_kit": {"delegated": True, "agent": "Researcher"}}], "unknown-agent"),
            ([{"id": "case-mismatch", "type": "prompt", "flow_kit": {"delegated": True, "agent": "coder"}}], "case-mismatch"),
            ([{"id": "malformed", "type": "prompt", "flow_kit": "FlowKit-Coder"}], "malformed"),
            ([{"id": "null-metadata", "type": "prompt", "flow_kit": None}], "null-metadata"),
            ([{"id": "legacy-model", "type": "prompt", "model": "gpt-6-sol"}], "legacy-model"),
            ([{"id": "route", "type": "switch", "cases": {"taken": []}, "default": [
                {"id": "invalid-untaken", "type": "command", "command": "speckit.fixture",
                 "flow_kit": {"delegated": True, "agent": "coder"}}
            ]}], "invalid-untaken"),
        )
        for graph, expected_step_id in invalid_graphs:
            with self.subTest(step=expected_step_id), self.assertRaisesRegex(ValueError, expected_step_id):
                self.controller.collect_agent_assignments(graph)

    def test_agentPreflight_rejectsWorkflowLevelDefault(self) -> None:
        definition = {"workflow": {"id": "test", "version": "1.0", "agent": "FlowKit-Tasker"}, "steps": []}
        with self.assertRaisesRegex(ValueError, "workflow-level agent"):
            self.controller.validate_workflow_definition(definition)

    def test_doWhilePreflightAcceptsOneCompleteSupportedConditionAndPositiveCap(self) -> None:
        graph = [{
            "id": "corrective-loop",
            "type": "do-while",
            "condition": "{{ steps.assess.output.state == 'continue' }}",
            "max_iterations": 5,
            "steps": [
                {"id": "correct", "type": "command", "command": "speckit.tasks",
                 "flow_kit": {"delegated": True, "agent": "FlowKit-Tasker"}},
                {"id": "assess", "type": "prompt",
                 "flow_kit": {"delegated": True, "agent": "FlowKit-Reviewer"}},
            ],
        }]
        self.controller.validate_workflow_graph(graph)
        self.assertEqual(
            [("correct", "FlowKit-Tasker"), ("assess", "FlowKit-Reviewer")],
            [(item.step_id, item.agent_name) for item in self.controller.collect_agent_assignments(graph)],
        )

    def test_doWhilePreflightRejectsNestedLoopsAndDuplicateIDsAcrossBody(self) -> None:
        nested = [{"id": "outer", "type": "do-while", "condition": False, "max_iterations": 2,
                   "steps": [{"id": "inner", "type": "do-while", "condition": False,
                              "max_iterations": 2, "steps": [{"id": "inner-step", "type": "prompt"}]}]}]
        with self.assertRaisesRegex(ValueError, "nested do-while"):
            self.controller.validate_workflow_graph(nested)
        duplicate = [{"id": "loop", "type": "do-while", "condition": False, "max_iterations": 2,
                      "steps": [{"id": "same", "type": "prompt"}, {"id": "same", "type": "prompt"}]}]
        with self.assertRaisesRegex(ValueError, "duplicate step id"):
            self.controller.validate_workflow_graph(duplicate)
        outer_duplicate = [{"id": "loop", "type": "do-while", "condition": False, "max_iterations": 2,
                            "steps": [{"id": "loop", "type": "prompt"}]}]
        with self.assertRaisesRegex(ValueError, "duplicate step id"):
            self.controller.validate_workflow_graph(outer_duplicate)
        stale_assessment = [{"id": "loop", "type": "do-while",
                             "condition": "{{ steps.assess.output.state == 'continue' }}", "max_iterations": 2,
                             "steps": [{"id": "assess", "type": "prompt"}, {"id": "mutate-later", "type": "command"}]}]
        with self.assertRaisesRegex(ValueError, "final fresh assessment"):
            self.controller.validate_workflow_graph(stale_assessment)

    def test_doWhilePreflightRejectsUnsupportedConditionOrNonpositiveIterationCap(self) -> None:
        invalid_conditions = (
            "steps.assess.output.state == 'continue'",
            "{{ steps.assess.output.state }} == 'continue'",
            "{{ steps.assess.output.state == 'continue' }} trailing",
            "{{ steps.assess.output.state == 'continue' or true }}",
        )
        for condition in invalid_conditions:
            with self.subTest(condition=condition), self.assertRaisesRegex(ValueError, "condition"):
                self.controller.validate_workflow_graph([{
                    "id": "loop", "type": "do-while", "condition": condition,
                    "max_iterations": 5, "steps": [{"id": "assess", "type": "prompt"}],
                }])
        for limit in (0, -1, True, 1.5, "5", None):
            with self.subTest(limit=limit), self.assertRaisesRegex(ValueError, "max_iterations"):
                self.controller.validate_workflow_graph([{
                    "id": "loop", "type": "do-while", "condition": False,
                    "max_iterations": limit, "steps": [{"id": "assess", "type": "prompt"}],
                }])

    def test_assessmentRoutesCompleteNeedsHumanAndBlockedBeforeCorrectiveWork(self) -> None:
        cases = (
            ({"state": "complete", "reason_code": "analysis-clean"}, {"action": "complete"}),
            ({"state": "needs-human", "reason_code": "scope-decision", "gate_step_id": "scope-gate"},
             {"action": "needs-human", "gate_step_id": "scope-gate"}),
            ({"state": "blocked", "reason_code": "missing-prerequisite", "resume_action": "restore-plan"},
             {"action": "blocked", "resume_action": "restore-plan"}),
        )
        for assessment, expected in cases:
            with self.subTest(state=assessment["state"]):
                self.assertEqual(expected, self.controller.route_assessment(
                    assessment, loop_body_step_ids={"correct"}, human_gate_step_ids={"scope-gate"}
                ))

    def test_assessmentOutcomeRequiresValidEvidenceAndAnInBodyNextStepForContinue(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            evidence = project / "tasks.md"
            evidence.write_text("T001", encoding="utf-8")
            digest = __import__("hashlib").sha256(evidence.read_bytes()).hexdigest()
            valid = {
                "state": "continue", "reason_code": "routine-gap",
                "evidence": [{"path": "tasks.md", "sha256": digest}],
                "remaining_ids": ["T001"], "resolved_ids": [], "next_step_id": "correct",
            }
            self.assertEqual(valid, self.controller.validate_outcome_envelope(valid, project, {"correct", "assess"}))
            complete = {
                "state": "complete", "reason_code": "analysis-clean",
                "evidence": [{"path": "tasks.md", "sha256": digest}], "remaining_ids": [], "resolved_ids": ["T001"],
            }
            needs_human = {
                "state": "needs-human", "reason_code": "scope-decision",
                "evidence": [{"path": "tasks.md", "sha256": digest}], "remaining_ids": ["T002"],
                "resolved_ids": [], "gate_step_id": "review",
            }
            blocked = {
                "state": "blocked", "reason_code": "missing-prerequisite",
                "evidence": [{"path": "tasks.md", "sha256": digest}], "remaining_ids": ["T002"],
                "resolved_ids": [], "resume_action": "restore-plan",
            }
            self.assertEqual(complete, self.controller.validate_outcome_envelope(complete, project, {"correct", "assess"}))
            for field, value in (("next_step_id", "correct"), ("gate_step_id", "review"),
                                 ("resume_action", "restore-plan")):
                with self.subTest(terminal_route=field), self.assertRaisesRegex(ValueError, "route field required"):
                    self.controller.validate_outcome_envelope(
                        {**complete, field: value}, project, {"correct", "assess"}, {"review"}
                    )
            self.assertEqual(needs_human, self.controller.validate_outcome_envelope(
                needs_human, project, {"correct", "assess"}, {"review"}
            ))
            needs_human_stop = {**needs_human, "resume_action": "ask-operator"}
            del needs_human_stop["gate_step_id"]
            self.assertEqual(needs_human_stop, self.controller.validate_outcome_envelope(
                needs_human_stop, project, {"correct", "assess"}
            ))
            with self.assertRaisesRegex(ValueError, "route field required"):
                self.controller.validate_outcome_envelope(needs_human_stop, project, {"correct", "assess"}, {"review"})
            self.assertEqual(blocked, self.controller.validate_outcome_envelope(blocked, project, {"correct", "assess"}))
            invalid = (
                {**valid, "state": "unknown"},
                {**valid, "next_step_id": "outside"},
                {**valid, "remaining_ids": ["T001"], "resolved_ids": ["T001"]},
                {**valid, "evidence": [{"path": "../outside", "sha256": digest}]},
                {**valid, "evidence": [{"path": "tasks.md", "sha256": "0" * 64}]},
                {**valid, "reason_code": "free text with private details"},
                {**valid, "state": "blocked", "resume_action": "restore-plan", "next_step_id": "correct"},
            )
            for outcome in invalid:
                with self.subTest(outcome=outcome), self.assertRaises(ValueError):
                    self.controller.validate_outcome_envelope(outcome, project, {"correct", "assess"})
            complete_with_remaining = {key: value for key, value in valid.items() if key != "next_step_id"}
            complete_with_remaining.update({"state": "complete", "remaining_ids": ["T001"]})
            with self.assertRaisesRegex(ValueError, "unresolved"):
                self.controller.validate_outcome_envelope(complete_with_remaining, project, {"correct", "assess"})

    def test_assessmentIdentifiersRejectUnderscoresAndSpaces(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            evidence = project / "tasks.md"
            evidence.write_text("T001", encoding="utf-8")
            digest = __import__("hashlib").sha256(evidence.read_bytes()).hexdigest()
            valid = {
                "state": "blocked", "reason_code": "missing-prerequisite",
                "evidence": [{"path": "tasks.md", "sha256": digest}],
                "remaining_ids": ["T001"], "resolved_ids": [], "resume_action": "restore-plan",
            }
            self.assertEqual(valid, self.controller.validate_outcome_envelope(valid, project, {"correct"}))
            for field in ("reason_code", "resume_action"):
                for invalid in ("restore_plan", "restore plan"):
                    with self.subTest(field=field, value=invalid), self.assertRaisesRegex(ValueError, "reason_code" if field == "reason_code" else "stable resume action"):
                        self.controller.validate_outcome_envelope({**valid, field: invalid}, project, {"correct"})

    def test_assessmentProgressNeedsResolvedPriorWorkNotOnlyChangedDigest(self) -> None:
        previous = {"state": "continue", "remaining_ids": ["T001", "T002"], "resolved_ids": [],
                    "evidence": [{"path": "tasks.md", "sha256": "a" * 64}]}
        resolved = {"state": "continue", "remaining_ids": ["T002"], "resolved_ids": ["T001"],
                    "evidence": [{"path": "tasks.md", "sha256": "b" * 64}]}
        digest_only = {**previous, "evidence": [{"path": "tasks.md", "sha256": "b" * 64}]}
        self.assertTrue(self.controller.assessment_made_progress(previous, resolved))
        self.assertFalse(self.controller.assessment_made_progress(previous, digest_only))

    def test_loopConditionEvaluatesOnlyReviewedStateEquality(self) -> None:
        condition = "{{ steps.assess.output.state == 'continue' }}"
        self.assertTrue(self.controller.evaluate_loop_condition(condition, {"assess": {"state": "continue"}}))
        self.assertFalse(self.controller.evaluate_loop_condition(condition, {"assess": {"state": "complete"}}))
        with self.assertRaisesRegex(ValueError, "unresolved"):
            self.controller.evaluate_loop_condition(condition, {})

    def test_loopFixtureCoversCleanBeforeLoopPostPassGateRejectedLoopAndManualFallback(self) -> None:
        fixture = yaml.safe_load((ROOT / "tests/consumer-fixtures/controller-workflow.yml").read_text(encoding="utf-8"))
        self.controller.validate_workflow_definition(fixture)
        steps = fixture["steps"]
        self.assertEqual("assess-initial", steps[0]["id"])
        route = steps[1]
        self.assertEqual({"complete", "continue", "needs-human", "blocked", "manual-fallback"}, set(route["cases"]))
        continue_nodes = route["cases"]["continue"]
        self.assertEqual("do-while", continue_nodes[0]["type"])
        after_loop = continue_nodes[1]
        self.assertIn("needs-human", after_loop["cases"])
        manual = route["cases"]["manual-fallback"][0]
        self.assertNotIn("flow_kit", manual)
        rejected = [{"id": "outer", "type": "do-while", "condition": False, "max_iterations": 2,
                     "steps": [{"id": "inner", "type": "do-while", "condition": False,
                                "max_iterations": 2, "steps": [{"id": "inside", "type": "prompt"}]}]}]
        with self.assertRaisesRegex(ValueError, "nested do-while"):
            self.controller.validate_workflow_graph(rejected)

    def test_renderTemplate_resolvesInputsAndPriorOutputsAndRejectsUnknownForms(self) -> None:
        value = "Implement {{ inputs.feature }} after {{ steps.plan.output.summary }}"
        rendered = self.controller.render_template(value, {"feature": "013"}, {"plan": {"summary": "review"}})
        self.assertEqual("Implement 013 after review", rendered)
        with self.assertRaisesRegex(ValueError, "unresolved input"):
            self.controller.render_template("{{ inputs.absent }}", {}, {})
        with self.assertRaisesRegex(ValueError, "unsupported or unresolved"):
            self.controller.render_template("{{ unsupported.value }}", {}, {})


class HumanInteractionTests(unittest.TestCase):
    """Interactive answers stay explicit and bound to the original child."""

    def setUp(self) -> None:
        self.controller = load_module("flowkit_controller_interaction", CONTROLLER_DIR / "controller.py")
        self.question = {
            "kind": "question", "step_id": "clarify-specification",
            "question": "Which workflows should the dashboard show?",
            "options": ["A", "B"], "allow_custom": True,
        }

    def test_validateChildQuestion_normalizesCustomFlagAndRejectsInvalidRequests(self) -> None:
        validated = self.controller.validate_child_question(self.question, "clarify-specification")
        self.assertTrue(validated["allow_custom_answer"])
        with self.assertRaisesRegex(ValueError, "step_id"):
            self.controller.validate_child_question(self.question, "different-step")
        with self.assertRaisesRegex(ValueError, "options"):
            self.controller.validate_child_question({**self.question, "options": ["A", "A"]}, "clarify-specification")

    def test_resolveChildAnswer_requiresSameChildAndExplicitAllowedAnswer(self) -> None:
        resolved = self.controller.resolve_child_answer(self.question, "A", "child-1", "child-1")
        self.assertEqual({"step_id": "clarify-specification", "child_id": "child-1", "answer": "A"}, resolved)
        with self.assertRaisesRegex(ValueError, "same child"):
            self.controller.resolve_child_answer(self.question, "A", "child-1", "child-2")
        with self.assertRaisesRegex(ValueError, "explicit"):
            self.controller.resolve_child_answer(self.question, "", "child-1", "child-1")
        with self.assertRaisesRegex(ValueError, "allowed"):
            self.controller.resolve_child_answer({**self.question, "allow_custom": False}, "another answer", "child-1", "child-1")

    def test_childQuestion_acceptsDescribedChoicesAndResolvesTheirIds(self) -> None:
        request = {**self.question, "options": [
            {"id": "A", "description": "Select an active workflow."},
            {"id": "B", "description": "Display the designated current workflow."},
        ], "allow_custom": False}
        normalized = self.controller.validate_child_question(request, "clarify-specification")
        self.assertEqual(request["options"], normalized["options"])
        self.assertEqual("B", self.controller.resolve_child_answer(normalized, "2", "child-1", "child-1")["answer"])
        self.assertEqual("A", self.controller.resolve_child_answer(normalized, "a", "child-1", "child-1")["answer"])
        with self.assertRaisesRegex(ValueError, "distinct"):
            self.controller.validate_child_question({**request, "options": [request["options"][0]] * 2}, "clarify-specification")
        with self.assertRaisesRegex(ValueError, "options"):
            self.controller.validate_child_question({**request, "options": [{"id": "A", "description": ""}]}, "clarify-specification")

    def test_validateGateChoice_requiresHumanVerdictAndOnlySelectedBranch(self) -> None:
        gate = {"id": "review", "type": "gate", "options": ["analyze", "defer"]}
        self.assertEqual("analyze", self.controller.validate_gate_choice(gate, "1"))
        with self.assertRaisesRegex(ValueError, "explicit"):
            self.controller.validate_gate_choice(gate, "")
        with self.assertRaisesRegex(ValueError, "allowed"):
            self.controller.validate_gate_choice(gate, "implement")
        switch = {"id": "route", "type": "switch", "cases": {
            "analyze": [{"id": "stop", "type": "prompt", "prompt": "Start analysis separately."}],
            "defer": [{"id": "deferred", "type": "prompt", "prompt": "Stop."}],
        }}
        self.assertEqual(["stop"], [step["id"] for step in self.controller.select_switch_branch(switch, "analyze")])

    def test_interactionCli_validatesQuestionAnswerAndGateWithoutPersistingThem(self) -> None:
        output = io.StringIO()
        with patch.object(sys, "stdin", io.StringIO(json.dumps(self.question))), redirect_stdout(output):
            self.assertEqual(0, self.controller.main(["question", "--step-id", "clarify-specification"]))
        normalized = json.loads(output.getvalue())
        self.assertTrue(normalized["allow_custom_answer"])
        output = io.StringIO()
        payload = {"request": normalized, "answer": "1"}
        with patch.object(sys, "stdin", io.StringIO(json.dumps(payload))), redirect_stdout(output):
            self.assertEqual(0, self.controller.main(["answer", "--child-id", "child-1", "--target-child-id", "child-1"]))
        self.assertEqual("A", json.loads(output.getvalue())["answer"])
        output = io.StringIO()
        gate_payload = {"gate": {"id": "review", "type": "gate", "options": ["analyze", "defer"]}, "answer": "2"}
        with patch.object(sys, "stdin", io.StringIO(json.dumps(gate_payload))), redirect_stdout(output):
            self.assertEqual(0, self.controller.main(["gate"]))
        self.assertEqual({"choice": "defer"}, json.loads(output.getvalue()))

    def test_clarifyNeedsHumanStopsWithoutAStopOnlyGateOrPlanning(self) -> None:
        workflow = yaml.safe_load((ROOT / "workflows/speckit-flow-clarify/workflow.yml").read_text(encoding="utf-8"))
        self.assertNotIn("clarification_decision", workflow["inputs"])
        self.assertFalse(any("speckit-flow-plan" in str(step) for step in workflow["steps"]))
        self.assertFalse(any(step.get("type") == "gate" for step in workflow["steps"]))
        assessment = {"state": "needs-human", "reason_code": "product-decision", "resume_action": "ask-operator"}
        self.assertEqual({"action": "needs-human", "resume_action": "ask-operator"},
                         self.controller.route_assessment(assessment, loop_body_step_ids={"clarify-session"}))
        with self.assertRaisesRegex(ValueError, "declared main-task gate"):
            self.controller.route_assessment(assessment, loop_body_step_ids={"clarify-session"},
                                             human_gate_step_ids={"required-gate"})


class RecoveryTests(unittest.TestCase):
    """Stopped runs keep compact, portable evidence without reverting edits."""

    def setUp(self) -> None:
        self.recovery = load_module("flowkit_controller_recovery", CONTROLLER_DIR / "recovery.py")

    def test_createAndUpdateSummary_recordsBoundedStepEvidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            summary = self.recovery.create_summary(
                project,
                {"workflow": {"id": "speckit-flow-tasks", "version": "0.2.0"}, "sha256": "a" * 64},
                {"bundle_record": {"sha256": "b" * 64, "device": 1, "inode": 2}, "skill_record": {"sha256": "c" * 64, "device": 1, "inode": 3}},
                [{"step_id": "generate-tasks", "agent_name": "FlowKit-Tasker"}],
                preflight_passed=True,
            )
            path = project / ".specify/flow-controllers/runs" / summary["run_id"] / "summary.json"
            for status in ("pending", "waiting_for_human", "running", "completed"):
                self.recovery.update_step(path, f"status-{status}", status)
            self.recovery.update_step(path, "generate-tasks", "running")
            partial_edit = project / "created.md"
            partial_edit.write_text("preserve", encoding="utf-8")
            self.recovery.update_step(path, "generate-tasks", "completed", changed_files=["created.md"])
            saved = json.loads(path.read_text(encoding="utf-8"))
            preserved = partial_edit.read_text(encoding="utf-8")
        self.assertEqual("completed", saved["steps"]["generate-tasks"]["status"])
        self.assertEqual({"pending", "waiting_for_human", "running", "completed"}, {saved["steps"][f"status-{status}"]["status"] for status in ("pending", "waiting_for_human", "running", "completed")})
        self.assertEqual(["created.md"], saved["changed_files"])
        self.assertEqual("preserve", preserved)

    def test_createSummary_rejectsPreflightFailureAndSensitiveEvidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "successful preflight"):
                self.recovery.create_summary(Path(temporary), {}, {}, [], preflight_passed=False)
            with self.assertRaisesRegex(ValueError, "repository-relative"):
                self.recovery.validate_summary({"changed_files": ["/private/file"]})
            with self.assertRaisesRegex(ValueError, "escape the repository"):
                self.recovery.validate_summary({"changed_files": ["../outside"]})
            with self.assertRaisesRegex(ValueError, "transcript"):
                self.recovery.validate_summary({"child_transcript": "raw conversation"})

    def test_interruptionMarksRunningStepIncomplete_andRefreshStopsOnEitherRecord(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            summary = self.recovery.create_summary(project, {"workflow": {"id": "x", "version": "1"}, "sha256": "d" * 64}, {}, [], preflight_passed=True)
            path = project / ".specify/flow-controllers/runs" / summary["run_id"] / "summary.json"
            self.recovery.update_step(path, "step-one", "running")
            recovered = self.recovery.mark_interrupted_steps_incomplete(path)
        self.assertEqual("incomplete", recovered["steps"]["step-one"]["status"])
        initial = {"workflow_sha256": "a", "bundle_record": {"sha256": "b"}, "skill_record": {"sha256": "c"}}
        changed = {**initial, "skill_record": {"sha256": "new"}}
        self.assertTrue(self.recovery.installation_changed(initial, changed))

    def test_stopRun_marksWaitingStepIncomplete(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            summary = self.recovery.create_summary(project, {"workflow": {"id": "x", "version": "1"}, "sha256": "d" * 64}, {}, [], preflight_passed=True)
            path = project / ".specify/flow-controllers/runs" / summary["run_id"] / "summary.json"
            self.recovery.update_step(path, "review", "waiting_for_human")
            stopped = self.recovery.stop_run(path, "operator-deferred")
        self.assertEqual("stopped", stopped["status"])
        self.assertEqual("incomplete", stopped["steps"]["review"]["status"])
        self.assertEqual("operator-deferred", stopped["blocker"])

    def test_recoveryRejectsUnboundedBlockerText(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            summary = self.recovery.create_summary(project, {"workflow": {"id": "x", "version": "1"}, "sha256": "d" * 64}, {}, [], preflight_passed=True)
            path = project / ".specify/flow-controllers/runs" / summary["run_id"] / "summary.json"
            for blocker in ("Child transcript: private answer", "secret private-key-material"):
                with self.subTest(blocker=blocker), self.assertRaisesRegex(ValueError, "blocker"):
                    self.recovery.stop_run(path, blocker)
            self.assertIsNone(self.recovery.read_summary(path)["blocker"])

    def test_recoveryRead_sanitizesLegacyTextBlocker(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            summary = self.recovery.create_summary(project, {"workflow": {"id": "x", "version": "1"}, "sha256": "d" * 64}, {}, [], preflight_passed=True)
            path = project / ".specify/flow-controllers/runs" / summary["run_id"] / "summary.json"
            legacy = json.loads(path.read_text(encoding="utf-8"))
            legacy["blocker"] = "Legacy free-text stop reason"
            path.write_text(json.dumps(legacy), encoding="utf-8")
            self.assertEqual("unspecified-stop", self.recovery.read_summary(path)["blocker"])
            self.assertEqual("Legacy free-text stop reason", json.loads(path.read_text(encoding="utf-8"))["blocker"])

    def test_recoveryCli_createsSummaryFromSuccessfulPreflightInput(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            payload = {
                "workflow": {"workflow": {"id": "speckit-flow-tasks", "version": "0.2.0"}, "sha256": "a" * 64},
                "fingerprints": {}, "assignments": [], "preflight_passed": True,
            }
            output = io.StringIO()
            with patch.object(sys, "stdin", io.StringIO(json.dumps(payload))), redirect_stdout(output):
                self.assertEqual(0, self.recovery.main(["create", "--project", temporary]))
            result = json.loads(output.getvalue())
            summary_path = Path(result["summary_path"])
            self.assertTrue(summary_path.is_file())
            self.assertEqual("running", json.loads(summary_path.read_text(encoding="utf-8"))["status"])

    def test_recoveryCli_appendsLoopPassWithoutOverwritingPriorIteration(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            summary = self.recovery.create_summary(project, {"workflow": {"id": "x", "version": "1"}, "sha256": "d" * 64}, {}, [], preflight_passed=True)
            path = project / ".specify/flow-controllers/runs" / summary["run_id"] / "summary.json"
            payload = {"loop_id": "loop", "iteration": 1,
                       "steps": [{"step_id": "repeated", "status": "completed"}],
                       "outcome": {"state": "complete", "reason_code": "resolved"}, "evidence": []}
            output = io.StringIO()
            with patch.object(sys, "stdin", io.StringIO(json.dumps(payload))), redirect_stdout(output):
                self.assertEqual(0, self.recovery.main(["loop-pass", "--summary", str(path)]))
            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual([("loop", 1, "repeated")], [
                (item["loop_id"], item["iteration"], item["steps"][0]["step_id"]) for item in saved["loop_passes"]
            ])

    def test_recoveryLoopPassesAreAppendOnlyOrderedAndPreserveRepeatedStepIDs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            summary = self.recovery.create_summary(project, {"workflow": {"id": "x", "version": "1"}, "sha256": "d" * 64}, {}, [], preflight_passed=True)
            path = project / ".specify/flow-controllers/runs" / summary["run_id"] / "summary.json"
            task_file = project / "tasks.md"
            task_file.write_text("T001", encoding="utf-8")
            evidence = [{"path": "tasks.md", "sha256": __import__("hashlib").sha256(task_file.read_bytes()).hexdigest()}]
            for iteration in (1, 2):
                self.recovery.record_loop_pass(
                    path, loop_id="corrective-loop", iteration=iteration,
                    steps=[{"step_id": "correct", "status": "completed"}, {"step_id": "assess", "status": "completed"}],
                    outcome={"state": "continue", "reason_code": "routine-gap"}, evidence=evidence,
                )
            saved = self.recovery.read_summary(path)
            self.assertEqual([("corrective-loop", 1), ("corrective-loop", 2)],
                             [(item["loop_id"], item["iteration"]) for item in saved["loop_passes"]])
            self.assertEqual(["correct", "assess"], [item["step_id"] for item in saved["loop_passes"][0]["steps"]])
            with self.assertRaisesRegex(ValueError, "order"):
                self.recovery.record_loop_pass(path, loop_id="corrective-loop", iteration=2,
                                               steps=[], outcome={"state": "complete"}, evidence=evidence)
            with self.assertRaisesRegex(ValueError, "repository-relative"):
                self.recovery.record_loop_pass(path, loop_id="bad", iteration=1, steps=[],
                                               outcome={"state": "complete"},
                                               evidence=[{"path": "/private/t.md", "sha256": "0" * 64}])

    def test_recoveryInterruptionAndChangedInstallationProduceSafeResumeStops(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            workflow = {"workflow": {"id": "x", "version": "1"}, "sha256": "d" * 64}
            fingerprints = {"bundle_record": {"sha256": "b", "device": 1, "inode": 2},
                            "skill_record": {"sha256": "c", "device": 1, "inode": 3}}
            summary = self.recovery.create_summary(project, workflow, fingerprints, [], preflight_passed=True)
            path = project / ".specify/flow-controllers/runs" / summary["run_id"] / "summary.json"
            self.recovery.record_loop_pass(
                path, loop_id="corrective-loop", iteration=1,
                steps=[{"step_id": "correct", "status": "running"}],
                outcome={"state": "continue", "reason_code": "routine-gap"}, evidence=[],
            )
            interrupted = self.recovery.mark_interrupted_steps_incomplete(path)
            self.assertEqual("incomplete", interrupted["loop_passes"][0]["steps"][0]["status"])
            safe = self.recovery.resume_decision(interrupted, workflow["sha256"], fingerprints)
            self.assertEqual("resume", safe["action"])
            changed = {**fingerprints, "skill_record": {"sha256": "new", "device": 1, "inode": 4}}
            stopped = self.recovery.resume_decision(interrupted, workflow["sha256"], changed)
            self.assertEqual({"action": "stop", "blocker": "installation-changed"}, stopped)
            stopped_workflow = self.recovery.resume_decision(interrupted, "changed", fingerprints)
            self.assertEqual({"action": "stop", "blocker": "workflow-changed"}, stopped_workflow)


if __name__ == "__main__":
    unittest.main()
