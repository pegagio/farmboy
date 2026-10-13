"""Tests for the FarmBoy Codex workflow controller helper."""

from __future__ import annotations

import importlib.util
import copy
import hashlib
import json
import os
import io
import subprocess
import sys
import tempfile
import unittest
import uuid
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import yaml


ROOT = Path(__file__).parents[1]
CONTROLLER_DIR = ROOT / "controllers/farmboy/scripts/python"


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
        self.controller = load_module("farmboy_controller_runtime", CONTROLLER_DIR / "controller.py")

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
        self.controller = load_module("farmboy_controller_definition", CONTROLLER_DIR / "controller.py")

    def test_loadDefinition_usesSelectedProjectAndReturnsProvenance(self) -> None:
        selected = Path("/consumer/project")
        definition = {"workflow": {"id": "farmboy-tasks", "version": "0.2.0"}, "steps": []}
        with patch.object(self.controller, "WorkflowEngine") as engine_class:
            engine_class.return_value.load_workflow.return_value = type(
                "Definition", (), {"data": definition, "source_path": Path("/consumer/project/.specify/workflows/tasks/workflow.yml"), "version": "0.2.0"}
            )()
            result = self.controller.load_installed_definition(selected, "farmboy-tasks")
        engine_class.assert_called_once_with(selected)
        engine_class.return_value.load_workflow.assert_called_once_with("farmboy-tasks")
        self.assertEqual("0.2.0", result["version"])
        self.assertEqual("farmboy-tasks", result["workflow"]["id"])
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
                ".agents/skills/farmboy-tasks/SKILL.md",
                ".agents/skills/farmboy-tasks/agents/openai.yaml",
                ".specify/farmboy/manifest.yml",
                ".specify/farmboy/controller-protocol.md",
                ".specify/farmboy/scripts/bootstrap.sh",
                ".specify/farmboy/scripts/python/controller.py",
                ".specify/farmboy/scripts/python/recovery.py",
            ]
            files = {}
            for relative in paths:
                target = project / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                content = f"name: farmboy-tasks\n" if relative.endswith("SKILL.md") else "fixture\n"
                if relative.endswith("manifest.yml"):
                    content = 'package:\n  version: "0.1.0"\n'
                target.write_text(content, encoding="utf-8")
                files[relative] = __import__("hashlib").sha256(content.encode()).hexdigest()
            record = {
                "package": "farmboy-controllers", "version": "0.1.0", "status": "installed", "files": files,
                "controllers": [{"skill_id": "farmboy-tasks", "workflow_id": "farmboy-tasks"}],
            }
            record_path = project / ".specify/farmboy/skills-install.json"
            record_path.write_text(json.dumps(record), encoding="utf-8")
            self.controller.verify_controller_install(project, "farmboy-tasks", "farmboy-tasks")
            (project / paths[0]).write_text("changed", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "was changed"):
                self.controller.verify_controller_install(project, "farmboy-tasks", "farmboy-tasks")


class NamedAgentAssignmentTests(unittest.TestCase):
    """Delegated steps resolve only to their reviewed native Codex agent names."""

    def setUp(self) -> None:
        self.controller = load_module("farmboy_controller_agents", CONTROLLER_DIR / "controller.py")

    def test_collectAgentAssignments_preservesDistinctNamesPerStep(self) -> None:
        steps = [
            {"id": "edit", "type": "prompt", "farmboy": {"delegated": True, "agent": "FarmBoy Coder"}},
            {"id": "review", "type": "command", "farmboy": {"delegated": True, "agent": "FarmBoy Reviewer"}},
            {"id": "summary", "type": "prompt", "prompt": "Summarize in the main task."},
        ]
        assignments = self.controller.collect_agent_assignments(steps)
        self.assertEqual(
            [
                self.controller.StepAssignmentIntent("edit", "FarmBoy Coder"),
                self.controller.StepAssignmentIntent("review", "FarmBoy Reviewer"),
            ],
            assignments,
        )

    def test_collectAgentAssignments_includesDelegatedStepsInEveryBranch(self) -> None:
        steps = [
            {
                "id": "route",
                "type": "switch",
                "cases": {"review": [{"id": "verify", "type": "prompt", "farmboy": {"delegated": True, "agent": "FarmBoy Reviewer"}}]},
                "default": [{"id": "build", "type": "prompt", "farmboy": {"delegated": True, "agent": "FarmBoy Code Reviewer"}}],
            }
        ]
        assignments = self.controller.collect_agent_assignments(steps)
        self.assertEqual(
            [("verify", "FarmBoy Reviewer"), ("build", "FarmBoy Code Reviewer")],
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
                    "--workflow-id", "farmboy-tasks",
                    "--specify", "/usr/bin/specify",
                    "--expected-version", "1.0.10.dev0+pegagio.2",
                    "--skill-id", "farmboy-tasks",
                    "--override", "agent=FarmBoy Coder",
                ]
            )
        self.assertEqual(2, error.exception.code)


class GraphPreflightTests(unittest.TestCase):
    """Graph validation covers nested branches before any execution starts."""

    def setUp(self) -> None:
        self.controller = load_module("farmboy_controller_graph", CONTROLLER_DIR / "controller.py")
        self.workflow = {
            "inputs": {"feature_context": {"required": True}},
            "steps": [
                {"id": "delegated-prompt", "type": "prompt", "farmboy": {"delegated": True, "agent": "FarmBoy Coder"}},
                {"id": "review-verdict", "type": "gate", "options": ["approve", "defer"]},
                {"id": "route-result", "type": "switch", "cases": {"primary": [
                    {"id": "nested-delegated-command", "command": "speckit.fixture", "farmboy": {"delegated": True, "agent": "FarmBoy Reviewer"}}
                ]}, "default": [
                    {"id": "alternate-agent", "type": "prompt", "farmboy": {"delegated": True, "agent": "FarmBoy Code Reviewer"}}
                ]},
            ],
        }

    def test_collectAgentAssignments_includesUntakenNestedBranches(self) -> None:
        assignments = self.controller.collect_agent_assignments(self.workflow["steps"])
        self.assertEqual(
            [("delegated-prompt", "FarmBoy Coder"), ("nested-delegated-command", "FarmBoy Reviewer"), ("alternate-agent", "FarmBoy Code Reviewer")],
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

    def test_agentPreflight_rejectsUnreviewedNamesEvenInUntakenNestedBranches(self) -> None:
        for name in ("Roadmap Agent", "Specifier", "Planner", "Tasker", "Reviewer", "Coder", "Code Reviewer", "Wiki Curator"):
            graph = [{"id": "route", "type": "switch", "cases": {"taken": []}, "default": [
                {"id": "old-agent", "type": "prompt", "farmboy": {"delegated": True, "agent": name}}
            ]}]
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "old-agent"):
                self.controller.collect_agent_assignments(graph)

    def test_validateDefinition_rejectsWorkflowLevelAgentDefaults(self) -> None:
        definition = {"workflow": {"id": "test", "version": "1.0", "agent": "FarmBoy Coder"}, "steps": []}
        with self.assertRaisesRegex(ValueError, "workflow-level"):
            self.controller.validate_workflow_definition(definition)

    def test_delegationBoundary_keepsMainTaskStepAndGateOutOfChildAssignments(self) -> None:
        graph = [
            {"id": "main-work", "type": "prompt", "prompt": "summarize"},
            {"id": "delegated-work", "type": "prompt", "farmboy": {"delegated": True, "agent": "FarmBoy Coder"}},
            {"id": "human-review", "type": "gate", "options": ["continue"]},
        ]
        assignments = self.controller.collect_agent_assignments(graph)
        self.assertEqual([("delegated-work", "FarmBoy Coder")], [(item.step_id, item.agent_name) for item in assignments])

    def test_delegationBoundary_ignoresOldFlowKitContainer(self) -> None:
        graph = [{"id": "old-key", "type": "prompt", "flow_kit": {"delegated": True, "agent": "FarmBoy Coder"}}]
        self.assertEqual([], self.controller.collect_agent_assignments(graph))

    def test_delegationBoundary_rejectsAgentOnNonDelegatedStepAndDelegatedGate(self) -> None:
        for graph in (
            [{"id": "main-work", "type": "prompt", "agent": "FarmBoy Coder"}],
            [{"id": "human-review", "type": "gate", "farmboy": {"delegated": True, "agent": "FarmBoy Reviewer"}}],
            [{"id": "route", "type": "switch", "farmboy": {"delegated": True, "agent": "FarmBoy Reviewer"}, "cases": {}}],
        ):
            with self.subTest(graph=graph), self.assertRaises(ValueError):
                self.controller.validate_workflow_graph(graph)

    def test_agentPreflight_rejectsMissingUnknownMalformedAndLegacyAssignmentsAcrossBranches(self) -> None:
        invalid_graphs = (
            ([{"id": "missing-agent", "type": "prompt", "farmboy": {"delegated": True}}], "missing-agent"),
            ([{"id": "unknown-agent", "type": "prompt", "farmboy": {"delegated": True, "agent": "Researcher"}}], "unknown-agent"),
            ([{"id": "case-mismatch", "type": "prompt", "farmboy": {"delegated": True, "agent": "coder"}}], "case-mismatch"),
            ([{"id": "malformed", "type": "prompt", "farmboy": "FarmBoy Coder"}], "malformed"),
            ([{"id": "null-metadata", "type": "prompt", "farmboy": None}], "null-metadata"),
            ([{"id": "legacy-model", "type": "prompt", "model": "gpt-6-sol"}], "legacy-model"),
            ([{"id": "route", "type": "switch", "cases": {"taken": []}, "default": [
                {"id": "invalid-untaken", "type": "command", "command": "speckit.fixture",
                 "farmboy": {"delegated": True, "agent": "coder"}}
            ]}], "invalid-untaken"),
        )
        for graph, expected_step_id in invalid_graphs:
            with self.subTest(step=expected_step_id), self.assertRaisesRegex(ValueError, expected_step_id):
                self.controller.collect_agent_assignments(graph)

    def test_agentPreflight_rejectsWorkflowLevelDefault(self) -> None:
        definition = {"workflow": {"id": "test", "version": "1.0", "agent": "FarmBoy Tasker"}, "steps": []}
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
                 "farmboy": {"delegated": True, "agent": "FarmBoy Tasker"}},
                {"id": "assess", "type": "prompt",
                 "farmboy": {"delegated": True, "agent": "FarmBoy Reviewer"}},
            ],
        }]
        self.controller.validate_workflow_graph(graph)
        self.assertEqual(
            [("correct", "FarmBoy Tasker"), ("assess", "FarmBoy Reviewer")],
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

    def test_loopConditionRequiresFreshReadinessOnlyAfterReviewerContinue(self) -> None:
        condition = ("{{ steps.assess.output.state == 'continue' && "
                     "steps.readiness-check.output.readiness_gate.state == 'ready' }}")
        self.assertTrue(self.controller.evaluate_loop_condition(condition, {
            "assess": {"state": "continue"},
            "readiness-check": {"readiness_gate": {"state": "ready"}},
        }))
        self.assertFalse(self.controller.evaluate_loop_condition(condition, {
            "assess": {"state": "continue"},
            "readiness-check": {"readiness_gate": {"state": "blocked"}},
        }))
        self.assertFalse(self.controller.evaluate_loop_condition(condition, {"assess": {"state": "complete"}}))
        with self.assertRaisesRegex(ValueError, "readiness gate output"):
            self.controller.evaluate_loop_condition(condition, {"assess": {"state": "continue"}})

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
        self.assertNotIn("farmboy", manual)
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

    def test_renderTemplate_serializesStructuredOutputsAsJson(self) -> None:
        rendered = self.controller.render_template(
            '{"proposal": {{ steps.prepare.output.proposal }}}', {},
            {"prepare": {"proposal": {"path": "specs/013\nplan.md", "ready": True,
                "label": "résumé 😀", "values": [None, False, 3]}}})
        self.assertEqual({"proposal": {"path": "specs/013\nplan.md", "ready": True,
            "label": "résumé 😀", "values": [None, False, 3]}}, json.loads(rendered))
        self.assertEqual(["A", None], self.controller.render_template(
            "{{ steps.prepare.output.choices }}", {}, {"prepare": {"choices": ["A", None]}}))
        self.assertEqual("review", self.controller.render_template(
            "{{ steps.prepare.output.summary }}", {}, {"prepare": {"summary": "review"}}))


class HumanInteractionTests(unittest.TestCase):
    """Interactive answers stay explicit and bound to the original child."""

    def setUp(self) -> None:
        self.controller = load_module("farmboy_controller_interaction", CONTROLLER_DIR / "controller.py")
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
        workflow = yaml.safe_load((ROOT / "workflows/farmboy-clarify/workflow.yml").read_text(encoding="utf-8"))
        self.assertNotIn("clarification_decision", workflow["inputs"])
        self.assertFalse(any("farmboy-plan" in str(step) for step in workflow["steps"]))
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
        self.recovery = load_module("farmboy_controller_recovery", CONTROLLER_DIR / "recovery.py")

    def test_createAndUpdateSummary_recordsBoundedStepEvidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            summary = self.recovery.create_summary(
                project,
                {"workflow": {"id": "farmboy-tasks", "version": "0.2.0"}, "sha256": "a" * 64},
                {"bundle_record": {"sha256": "b" * 64, "device": 1, "inode": 2}, "skill_record": {"sha256": "c" * 64, "device": 1, "inode": 3}},
                [{"step_id": "generate-tasks", "agent_name": "FarmBoy Tasker"}],
                preflight_passed=True,
            )
            path = project / ".specify/farmboy-controllers/runs" / summary["run_id"] / "summary.json"
            self.assertFalse((project / ".specify/flow-controllers").exists())
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
            path = project / ".specify/farmboy-controllers/runs" / summary["run_id"] / "summary.json"
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
            path = project / ".specify/farmboy-controllers/runs" / summary["run_id"] / "summary.json"
            self.recovery.update_step(path, "review", "waiting_for_human")
            stopped = self.recovery.stop_run(path, "operator-deferred")
        self.assertEqual("stopped", stopped["status"])
        self.assertEqual("incomplete", stopped["steps"]["review"]["status"])
        self.assertEqual("operator-deferred", stopped["blocker"])

    def test_recoveryRejectsUnboundedBlockerText(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            summary = self.recovery.create_summary(project, {"workflow": {"id": "x", "version": "1"}, "sha256": "d" * 64}, {}, [], preflight_passed=True)
            path = project / ".specify/farmboy-controllers/runs" / summary["run_id"] / "summary.json"
            for blocker in ("Child transcript: private answer", "secret private-key-material"):
                with self.subTest(blocker=blocker), self.assertRaisesRegex(ValueError, "blocker"):
                    self.recovery.stop_run(path, blocker)
            self.assertIsNone(self.recovery.read_summary(path)["blocker"])

    def test_recoveryRead_sanitizesLegacyTextBlocker(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            summary = self.recovery.create_summary(project, {"workflow": {"id": "x", "version": "1"}, "sha256": "d" * 64}, {}, [], preflight_passed=True)
            path = project / ".specify/farmboy-controllers/runs" / summary["run_id"] / "summary.json"
            legacy = json.loads(path.read_text(encoding="utf-8"))
            legacy["blocker"] = "Legacy free-text stop reason"
            path.write_text(json.dumps(legacy), encoding="utf-8")
            self.assertEqual("unspecified-stop", self.recovery.read_summary(path)["blocker"])
            self.assertEqual("Legacy free-text stop reason", json.loads(path.read_text(encoding="utf-8"))["blocker"])

    def test_recoveryCli_createsSummaryFromSuccessfulPreflightInput(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            payload = {
                "workflow": {"workflow": {"id": "farmboy-tasks", "version": "0.2.0"}, "sha256": "a" * 64},
                "fingerprints": {}, "assignments": [], "preflight_passed": True,
            }
            output = io.StringIO()
            with patch.object(sys, "stdin", io.StringIO(json.dumps(payload))), redirect_stdout(output):
                self.assertEqual(0, self.recovery.main(["create", "--project", temporary]))
            result = json.loads(output.getvalue())
            summary_path = Path(result["summary_path"])
            self.assertTrue(summary_path.is_file())
            self.assertEqual((".specify", "farmboy-controllers"),
                             summary_path.relative_to(Path(temporary)).parts[:2])
            self.assertFalse((Path(temporary) / ".specify/flow-controllers").exists())
            self.assertEqual(summary_path.relative_to(Path(temporary)).as_posix().split("/", 2)[:2],
                             [".specify", "farmboy-controllers"])
            self.assertFalse((Path(temporary) / ".specify/flow-controllers").exists())
            self.assertEqual("running", json.loads(summary_path.read_text(encoding="utf-8"))["status"])

    def test_recoveryCli_appendsLoopPassWithoutOverwritingPriorIteration(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            summary = self.recovery.create_summary(project, {"workflow": {"id": "x", "version": "1"}, "sha256": "d" * 64}, {}, [], preflight_passed=True)
            path = project / ".specify/farmboy-controllers/runs" / summary["run_id"] / "summary.json"
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
            path = project / ".specify/farmboy-controllers/runs" / summary["run_id"] / "summary.json"
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
            path = project / ".specify/farmboy-controllers/runs" / summary["run_id"] / "summary.json"
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

class ScopedImplementationControllerTests(unittest.TestCase):
    """The main controller binds scoped operations to current project files."""

    def setUp(self) -> None:
        sys.path.insert(0, str(CONTROLLER_DIR))
        self.addCleanup(sys.path.remove, str(CONTROLLER_DIR))
        load_module("implementation_scope", CONTROLLER_DIR / "implementation_scope.py")
        self.controller = load_module("farmboy_controller_scoped_implementation", CONTROLLER_DIR / "controller.py")
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.feature = "specs/901-scoped-implementation"
        (self.root / ".specify").mkdir()
        self.write(".specify/feature.json", {"feature_directory": self.feature})
        self.write(f"{self.feature}/spec.md", "# Current specification\n")
        self.write(f"{self.feature}/tasks.md", "- [ ] T001 Implement a scoped operation\n")

    def write(self, relative: str, value: dict | str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, sort_keys=True) if isinstance(value, dict) else value, encoding="utf-8")

    def current_scope_payload(self) -> dict:
        digest = lambda path: hashlib.sha256((self.root / path).read_bytes()).hexdigest()
        description = "Implement a scoped operation"
        scope = {
            "schema_version": "1.0", "run_id": "run-scoped-1", "feature_directory": self.feature,
            "request_reference": "trusted-main-request-1", "request_kind": "full-feature",
            "requested_task_ids": ["T001"],
            "task_records": [{"task_id": "T001", "marker": "unchecked", "description": description,
                              "description_sha256": hashlib.sha256(description.encode()).hexdigest()}],
            "input_digests": {path: digest(path) for path in (
                ".specify/feature.json", f"{self.feature}/spec.md", f"{self.feature}/tasks.md")},
        }
        scope["scope_sha256"] = hashlib.sha256(
            json.dumps(scope, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
        return {"scope": scope, "trusted_request_reference": "trusted-main-request-1",
                "retained_scope_sha256": scope["scope_sha256"]}

    def current_subset_scope_payload(self) -> dict:
        payload = self.current_scope_payload()
        payload["scope"]["request_kind"] = "explicit-subset"
        payload["scope"]["scope_sha256"] = hashlib.sha256(
            json.dumps({key: value for key, value in payload["scope"].items() if key != "scope_sha256"},
                       sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
        payload["retained_scope_sha256"] = payload["scope"]["scope_sha256"]
        payload["trusted_requested_task_ids"] = ["T001"]
        return payload

    def testScopeCommandBindsActivePointerSpecificationAndTaskBytes(self) -> None:
        payload = self.current_scope_payload()
        result = self.controller.validate_implementation_scope(self.root, payload)
        self.assertEqual("ready", result["state"])
        self.assertEqual(["T001"], result["requested_task_ids"])
        self.write(f"{self.feature}/spec.md", "# Changed specification\n")
        stale = self.controller.validate_implementation_scope(self.root, payload)
        self.assertEqual("blocked", stale["state"])
        self.assertEqual("implementation-scope-required-source-binding-missing", stale["reason_code"])

    def testTaskerMarkerSuccessorReentersOriginalScopeAndRejectsReplayOrRevert(self) -> None:
        payload = self.current_scope_payload()
        before_text = (self.root / f"{self.feature}/tasks.md").read_text(encoding="utf-8")
        after_text = before_text.replace("- [ ] T001", "- [x] T001")
        task_path = f"{self.feature}/tasks.md"
        self.write(task_path, after_text)
        tasker_path = f"{self.feature}/validation/tasker-tracking.json"
        reviewer_path = f"{self.feature}/validation/reviewer-completion.json"
        tasker_record = {"source": "exact FarmBoy Tasker marker-only tracking result", "task_ids": ["T001"]}
        reviewer_record = {"reviewer": "FarmBoy Code Reviewer", "completed_task_ids": ["T001"]}
        self.write(tasker_path, tasker_record)
        self.write(reviewer_path, reviewer_record)
        evidence = lambda path: [{"path": path, "sha256": hashlib.sha256((self.root / path).read_bytes()).hexdigest()}]
        event = {"predecessor_event_sha256": "0" * 64, "scope_sha256": payload["scope"]["scope_sha256"],
            "tasker_assignment": "FarmBoy Tasker", "tasks_before_text": before_text, "tasks_after_text": after_text,
            "tasker_result": {"state": "ready", "tasks_before_sha256": hashlib.sha256(before_text.encode()).hexdigest(),
                "tasks_after_sha256": hashlib.sha256(after_text.encode()).hexdigest(), "completed_task_ids": ["T001"],
                "evidence": evidence(tasker_path)},
            "reviewer_result": {"reviewer": "FarmBoy Code Reviewer", "completed_task_ids": ["T001"],
                "evidence": evidence(reviewer_path)}}
        event["sha256"] = hashlib.sha256(json.dumps(event, sort_keys=True, separators=(",", ":"),
                                                      ensure_ascii=False).encode()).hexdigest()
        tracking = [event]
        reentered = self.controller.validate_implementation_scope(
            self.root, {**payload, "task_tracking_successors": tracking})
        self.assertEqual("ready", reentered["state"], reentered)
        self.assertEqual(payload["scope"]["scope_sha256"], reentered["scope_sha256"])
        spec_path = self.root / f"{self.feature}/spec.md"
        current_spec = spec_path.read_text(encoding="utf-8")
        self.write(f"{self.feature}/spec.md", current_spec + "\nStale successor input.\n")
        stale_spec = self.controller.validate_implementation_scope(
            self.root, {**payload, "task_tracking_successors": tracking})
        self.assertEqual("blocked", stale_spec["state"])
        self.write(f"{self.feature}/spec.md", current_spec)
        pointer_path = self.root / ".specify/feature.json"
        current_pointer = pointer_path.read_text(encoding="utf-8")
        self.write(".specify/feature.json", current_pointer.replace(self.feature, "specs/999-other"))
        stale_pointer = self.controller.validate_implementation_scope(
            self.root, {**payload, "task_tracking_successors": tracking})
        self.assertEqual("blocked", stale_pointer["state"])
        self.write(".specify/feature.json", current_pointer)
        history = self.controller._empty_implementation_history(payload["scope"])
        current_evidence = evidence(reviewer_path)
        routed = self.controller.route_scoped_implementation(self.root, {
            **payload, "task_tracking_successors": tracking,
            "retained_history_sha256": history["sha256"],
            "assessment": {"state": "complete", "reason_code": "tracked-scope-complete",
                "evidence": current_evidence, "remaining_ids": [], "resolved_ids": ["task:T001"]},
            "eligible_task_ids": [],
            "declared_node_ids": ["prepare-scoped-prerequisites", "implement-tasks"],
        })
        self.assertEqual("blocked", routed["state"], routed)
        self.assertEqual("scoped-completion-proof-required", routed["reason_code"])
        self.assertEqual("blocked", self.controller.validate_implementation_scope(self.root, payload)["state"])
        replayed = self.controller.validate_implementation_scope(
            self.root, {**payload, "task_tracking_successors": tracking + tracking})
        self.assertEqual("blocked", replayed["state"])
        self.write(task_path, before_text)
        reverted = self.controller.validate_implementation_scope(
            self.root, {**payload, "task_tracking_successors": tracking})
        self.assertEqual("blocked", reverted["state"])

    def historical_progress_fixture(self, sessions: int = 1, attempts: int = 1) -> dict:
        """Retain a pre-effect assessment, then review and track one whole task."""
        digest = self.controller._progress_digest
        task_path = f"{self.feature}/tasks.md"
        self.write(task_path, "- [ ] T001 Implement a scoped operation\n- [ ] T002 Implement another operation\n")
        source_path = f"{self.feature}/operation.py"
        self.write(source_path, "result = 'before'\n")
        evidence = lambda path: [{"path": path, "sha256": hashlib.sha256((self.root / path).read_bytes()).hexdigest()}]
        binding = self.current_scope_payload()
        binding["scope"]["run_id"] = f"historical-{sessions}-{attempts}"
        # Full-feature scope includes both unfinished tasks.
        record = {"task_id": "T002", "marker": "unchecked", "description": "Implement another operation",
                  "description_sha256": hashlib.sha256(b"Implement another operation").hexdigest()}
        binding["scope"]["requested_task_ids"].append("T002")
        binding["scope"]["task_records"].append(record)
        binding["scope"]["scope_sha256"] = digest({k: v for k, v in binding["scope"].items() if k != "scope_sha256"})
        binding["retained_scope_sha256"] = binding["scope"]["scope_sha256"]
        baseline = self.controller.capture_implementation_baseline(self.root, {
            "feature_directory": self.feature, "selected_task_ids": ["T001", "T002"]})
        previous = {"state": "continue", "reason_code": "before-source-work",
                    "evidence": evidence(task_path) + evidence(source_path),
                    "remaining_ids": baseline["remaining_ids"], "resolved_ids": [], "next_step_id": "implement-tasks"}
        self.controller.validate_outcome_envelope(previous, self.root, {"implement-tasks"})
        retained = digest({"scope_sha256": binding["scope"]["scope_sha256"], "assessment": previous})
        history = self.controller._empty_implementation_history(binding["scope"])
        for index in range(sessions):
            prior_count = max(0, index - (sessions - attempts))
            kind = "preparation" if index < sessions - attempts else (
                "first-source-execution" if prior_count == 0 else "corrective-source-execution")
            node = "prepare-scoped-prerequisites" if kind == "preparation" else "implement-tasks"
            count = prior_count + (kind != "preparation")
            events = [("coder-session-start", {"execution_kind": kind}, prior_count)]
            if kind != "preparation":
                events.append(("source-attempt-start", {"execution_kind": kind}, count))
            events.append(("coder-session-outcome", {"outcome": "completed"}, count))
            for kind, fields, source_count in events:
                event = {"event_id": f"event-{len(history['events']) + 1}", "event_kind": kind,
                    "predecessor_sha256": history["events"][-1]["sha256"] if history["events"] else "0" * 64,
                    "scope_sha256": binding["scope"]["scope_sha256"], "declared_node_id": node,
                    "occurred_at": f"2026-10-12T12:00:{len(history['events']):02d}Z", "evidence": evidence(source_path),
                    "coder_session_id": f"session-{index}", "coder_sessions_started": index + 1,
                    "source_attempts_started": source_count, **fields}
                event["sha256"] = digest(event)
                result = self.controller.append_implementation_execution_event(self.root, {
                    **binding, "event": event, "retained_history_sha256": history["sha256"]})
                self.assertEqual("ready", result["state"], result)
                history = result["history"]
        self.write(source_path, "result = 'corrected'\n")
        review = {"reviewer": "FarmBoy Code Reviewer", "baseline_sha256": baseline["baseline_sha256"],
                  "findings": [], "completed_task_ids": ["T001"], "task_completion_evidence": evidence(source_path)}
        before = (self.root / task_path).read_text()
        after = before.replace("- [ ] T001", "- [x] T001")
        self.write(task_path, after)
        tasker_path = f"{self.feature}/validation/tasker.json"
        reviewer_path = f"{self.feature}/validation/reviewer.json"
        self.write(tasker_path, {"completed_task_ids": ["T001"]})
        self.write(reviewer_path, review)
        event = {"predecessor_event_sha256": "0" * 64, "scope_sha256": binding["scope"]["scope_sha256"],
                 "tasker_assignment": "FarmBoy Tasker", "tasks_before_text": before, "tasks_after_text": after,
                 "tasker_result": {"state": "ready", "tasks_before_sha256": hashlib.sha256(before.encode()).hexdigest(),
                     "tasks_after_sha256": hashlib.sha256(after.encode()).hexdigest(), "completed_task_ids": ["T001"],
                     "evidence": evidence(tasker_path)},
                 "reviewer_result": {"reviewer": "FarmBoy Code Reviewer", "completed_task_ids": ["T001"],
                     "evidence": evidence(reviewer_path)}}
        event["sha256"] = digest(event)
        return {**binding, "controller_loop_mode": "implementation_scope", "task_tracking_successors": [event],
                "retained_history_sha256": history["sha256"], "previous_assessment": previous,
                "retained_previous_assessment_sha256": retained,
                "assessment": {"state": "continue", "reason_code": "reviewed-partial-completion",
                    "evidence": evidence(task_path) + evidence(source_path), "remaining_ids": ["task:T002"],
                    "resolved_ids": ["task:T001"], "next_step_id": "implement-tasks"},
                "eligible_task_ids": ["T002"], "declared_node_ids": ["prepare-scoped-prerequisites", "implement-tasks"],
                "progress": {"baseline": baseline["baseline"], "baseline_sha256": baseline["baseline_sha256"], "review": review},
                "administrative_prerequisite_ids": []}

    def testRetainedHistoricalEvidencePermitsReviewedMarkerAndSourceChanges(self) -> None:
        request = self.historical_progress_fixture()
        original = json.dumps(request["previous_assessment"], sort_keys=True)
        result = self.controller.validate_scoped_implementation_progress(self.root, request)
        self.assertEqual("continue", result["state"], result)
        self.assertEqual(original, json.dumps(request["previous_assessment"], sort_keys=True))
        with self.assertRaisesRegex(ValueError, "digest does not match current bytes"):
            self.controller.validate_outcome_envelope(request["previous_assessment"], self.root, {"implement-tasks"})

    def testHistoricalAssessmentMustMatchIndependentlyRetainedScopeBinding(self) -> None:
        request = self.historical_progress_fixture()
        unbound = {key: value for key, value in request.items() if key != "retained_previous_assessment_sha256"}
        self.assertEqual("historical-assessment-binding-invalid",
                         self.controller.validate_scoped_implementation_progress(self.root, unbound)["reason_code"])
        foreign_scope = self.controller._progress_digest({"scope_sha256": "0" * 64,
                                                          "assessment": request["previous_assessment"]})
        for variant in (None, "0" * 64, foreign_scope, self.controller._progress_digest(request["previous_assessment"])):
            with self.subTest(binding=variant):
                changed = {**request, "retained_previous_assessment_sha256": variant}
                self.assertEqual("blocked", self.controller.validate_scoped_implementation_progress(self.root, changed)["state"])
        request["previous_assessment"]["remaining_ids"].append("finding:forged")
        result = self.controller.validate_scoped_implementation_progress(self.root, request)
        self.assertEqual("historical-assessment-binding-invalid", result["reason_code"])

    def testHistoricalBindingDoesNotRelaxCurrentEvidenceOrTaskScope(self) -> None:
        request = self.historical_progress_fixture()
        request["assessment"]["evidence"][0]["sha256"] = "0" * 64
        result = self.controller.validate_scoped_implementation_progress(self.root, request)
        self.assertEqual("assessment evidence digest does not match current bytes", result["reason_code"])
        self.write(f"{self.feature}/tasks.md", "- [x] T001 Unauthorized description change\n- [ ] T002 Implement another operation\n")
        request["assessment"]["evidence"][0]["sha256"] = hashlib.sha256(
            (self.root / f"{self.feature}/tasks.md").read_bytes()).hexdigest()
        result = self.controller.validate_scoped_implementation_progress(self.root, request)
        self.assertEqual("blocked", result["state"])
        self.assertNotEqual("assessment evidence digest does not match current bytes", result["reason_code"])

    def testBoundHistoricalEnvelopeStillRequiresValidStructure(self) -> None:
        request = self.historical_progress_fixture()
        variants = [
            {**request["previous_assessment"], "evidence": [{"path": "../outside", "sha256": "a" * 64}]},
            {**request["previous_assessment"], "evidence": [{"path": "relative", "sha256": "bad"}]},
            {**request["previous_assessment"], "evidence": request["previous_assessment"]["evidence"] * 2},
            {**request["previous_assessment"], "resolved_ids": ["task:T001"]},
            {**request["previous_assessment"], "next_step_id": "undeclared-node"},
        ]
        for previous in variants:
            with self.subTest(previous=previous):
                bound = {**request, "previous_assessment": previous,
                    "retained_previous_assessment_sha256": self.controller._progress_digest({
                        "scope_sha256": request["scope"]["scope_sha256"], "assessment": previous})}
                result = self.controller.validate_scoped_implementation_progress(self.root, bound)
                self.assertEqual("blocked", result["state"], result)
                self.assertNotEqual("historical-assessment-binding-invalid", result["reason_code"])

    def testHistoricalComparisonPreservesNoProgressAndBothBudgets(self) -> None:
        request = self.historical_progress_fixture()
        request["previous_assessment"]["remaining_ids"] = ["task:T002"]
        request["retained_previous_assessment_sha256"] = self.controller._progress_digest({
            "scope_sha256": request["scope"]["scope_sha256"], "assessment": request["previous_assessment"]})
        result = self.controller.validate_scoped_implementation_progress(self.root, request)
        self.assertEqual("no-progress", result["blocker"], result)
        for sessions, attempts in ((5, 1), (5, 5)):
            with self.subTest(sessions=sessions, attempts=attempts):
                request = self.historical_progress_fixture(sessions, attempts)
                result = self.controller.validate_scoped_implementation_progress(self.root, request)
                self.assertEqual("loop-cap-exhausted", result["blocker"], result)

    def testReviewedLoopCarrierIsRestrictedAndInspectable(self) -> None:
        body = [
            {"id": "route-scoped-entry", "type": "prompt", "prompt": "Route current scope."},
            {"id": "prepare-scoped-prerequisites", "type": "switch", "expression": "{{ steps.x.output.state }}", "cases": {"continue": []}},
            {"id": "implement-tasks", "type": "switch", "expression": "{{ steps.x.output.state }}", "cases": {"continue": []}},
            {"id": "assess-implementation-after-pass", "type": "prompt", "prompt": "Assess current substantive work."},
            {"id": "route-post-assessment", "type": "switch", "expression": "{{ steps.x.output.state }}", "cases": {"continue": []}},
            {"id": "capture-post-pass-state", "type": "prompt", "prompt": "Capture fresh validated state."},
            {"id": "route-scoped-execution", "type": "prompt", "prompt": "Apply guarded route."},
        ]
        loop = {"id": "implementation-loop", "type": "do-while", "max_iterations": 5,
                "condition": '{{ steps.route-scoped-execution.output.state == "continue" }}',
                "controller_loop_mode": "implementation_scope", "steps": body}
        self.controller.validate_workflow_graph([loop])
        self.assertEqual([{"step_id": loop["id"], "mode": "implementation_scope"}],
                         self.controller._controller_loop_modes([loop]))
        malformed = {**loop, "controller_loop_mode": "generic-but-scoped"}
        with self.assertRaisesRegex(ValueError, "unsupported controller_loop_mode"):
            self.controller.validate_workflow_graph([malformed])

    def testImplementationScopeCarrierRejectsBooleanConditionThroughInspect(self) -> None:
        definition = yaml.safe_load((ROOT / "workflows/farmboy-implement/workflow.yml").read_text(encoding="utf-8"))
        loop = find_workflow_step(definition["steps"], "implementation-loop")
        for condition in (True, False, None, 1, "{{ steps.route-scoped-execution.output.state }}"):
            with self.subTest(condition=condition):
                loop["condition"] = condition
                with self.assertRaisesRegex(ValueError, "exact route-scoped-execution condition"):
                    self.controller.validate_workflow_definition(definition)
                with patch.object(self.controller, "verify_controller_install", return_value={}), \
                        patch.object(self.controller, "load_installed_definition", return_value=definition), \
                        patch.object(self.controller.subprocess, "run", return_value=type("Process", (), {"stdout": "specify 1.0.10.dev0+pegagio.2"})()):
                    with self.assertRaisesRegex(ValueError, "exact route-scoped-execution condition"):
                        self.controller.main([
                            "inspect", "--project", str(self.root), "--workflow-id", "farmboy-implement",
                            "--specify", "/bin/true", "--expected-version", "1.0.10.dev0+pegagio.2",
                            "--skill-id", "farmboy-implement", "--input", "feature_context=specs/020-test",
                        ])
        definition = yaml.safe_load((ROOT / "workflows/farmboy-implement/workflow.yml").read_text(encoding="utf-8"))
        self.controller.validate_workflow_definition(definition)
        legacy_loop = {"id": "legacy-loop", "type": "do-while", "condition": True,
            "max_iterations": 2, "steps": [{"id": "legacy-body", "type": "prompt", "prompt": "Continue."}]}
        self.controller.validate_workflow_graph([legacy_loop])

    def testInspectSerializesReviewedLoopModeIntoDispatchDefinition(self) -> None:
        definition = yaml.safe_load((ROOT / "workflows/farmboy-implement/workflow.yml").read_text(encoding="utf-8"))
        output = io.StringIO()
        with patch.object(self.controller, "verify_controller_install", return_value={}), \
                patch.object(self.controller, "load_installed_definition", return_value=definition), \
                patch.object(self.controller, "installation_fingerprints", return_value={}), \
                patch.object(self.controller.subprocess, "run", return_value=type("Process", (), {"stdout": "specify 1.0.10.dev0+pegagio.2"})()), \
                redirect_stdout(output):
            status = self.controller.main([
                "inspect", "--project", str(self.root), "--workflow-id", "farmboy-implement",
                "--specify", "/bin/true", "--expected-version", "1.0.10.dev0+pegagio.2",
                "--skill-id", "farmboy-implement", "--input", "feature_context=specs/020-test",
            ])
        self.assertEqual(0, status)
        inspected = json.loads(output.getvalue())
        self.assertEqual([{"step_id": "implementation-loop", "mode": "implementation_scope"}],
                         inspected["controller_loop_modes"])
        loop = find_workflow_step(inspected["steps"], "implementation-loop")
        self.assertEqual("implementation_scope", loop["controller_loop_mode"])

    def testScopedHistoryCommandIsDispatchedAndReturnsBlockedStatus(self) -> None:
        with patch("sys.stdin", io.StringIO('{"unexpected":true}')), redirect_stdout(io.StringIO()) as output:
            status = self.controller.main(["implementation-history", "--project", str(self.root)])
        self.assertEqual(2, status)
        self.assertEqual("implementation-history-request-invalid", json.loads(output.getvalue())["reason_code"])

    def testScopedHistoryPersistsPreDispatchSessionAndRejectsStaleAppend(self) -> None:
        scope_payload = self.current_scope_payload()
        empty = {"schema_version": "1.0", "scope_sha256": scope_payload["scope"]["scope_sha256"],
                 "events": [], "coder_sessions_started": 0, "source_attempts_started": 0}
        empty["sha256"] = hashlib.sha256(
            json.dumps(empty, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
        evidence_path = f"{self.feature}/tasks.md"
        event = {
            "event_id": "session-1-start", "predecessor_sha256": "0" * 64,
            "scope_sha256": scope_payload["scope"]["scope_sha256"], "event_kind": "coder-session-start",
            "declared_node_id": "prepare-scoped-prerequisites", "occurred_at": "2026-10-08T12:00:00Z",
            "evidence": [{"path": evidence_path,
                          "sha256": hashlib.sha256((self.root / evidence_path).read_bytes()).hexdigest()}],
            "coder_session_id": "session-1", "coder_sessions_started": 1,
            "source_attempts_started": 0, "execution_kind": "preparation",
        }
        event["sha256"] = hashlib.sha256(
            json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
        payload = {**scope_payload, "event": event, "retained_history_sha256": empty["sha256"]}
        result = self.controller.append_implementation_execution_event(self.root, payload)
        self.assertEqual("ready", result["state"])
        self.assertEqual(1, result["coder_sessions_started"])
        retained_path = self.root / result["history_path"]
        self.assertTrue(result["history_path"].startswith(".specify/farmboy-controllers/implementation-history/"))
        self.assertTrue(result["history_path"].startswith(".specify/farmboy-controllers/implementation-history/"))
        self.assertTrue(retained_path.is_file())
        persisted = json.loads(retained_path.read_text(encoding="utf-8"))
        self.assertEqual(result["history_sha256"], persisted["sha256"])
        stale = self.controller.append_implementation_execution_event(self.root, payload)
        self.assertEqual("blocked", stale["state"])
        self.assertEqual("implementation-history-retained-state-stale", stale["reason_code"])

    def testScopedRouteUsesControllerOwnedZeroHistoryAndRejectsSuppliedCounters(self) -> None:
        scope_payload = self.current_scope_payload()
        empty = self.controller._empty_implementation_history(scope_payload["scope"])
        task_path = f"{self.feature}/tasks.md"
        assessment = {"state": "continue", "reason_code": "preparation-required",
                     "evidence": [{"path": task_path,
                                   "sha256": hashlib.sha256((self.root / task_path).read_bytes()).hexdigest()}],
                     "remaining_ids": ["task:T001"], "resolved_ids": [],
                     "next_step_id": "prepare-scoped-prerequisites"}
        request = {**scope_payload, "retained_history_sha256": empty["sha256"], "assessment": assessment,
                   "eligible_task_ids": ["T001"],
                   "declared_node_ids": ["prepare-scoped-prerequisites", "implement-tasks"]}
        routed = self.controller.route_scoped_implementation(self.root, request)
        self.assertEqual("continue", routed["state"])
        self.assertEqual("prepare-scoped-prerequisites", routed["next_step_id"])
        self.assertEqual(0, routed["history"]["source_attempts_started"])
        forged = self.controller.route_scoped_implementation(self.root, {**request, "history": {
            **empty, "coder_sessions_started": 5, "source_attempts_started": 5}})
        self.assertEqual("blocked", forged["state"])
        self.assertEqual("implementation-route-request-invalid", forged["reason_code"])

    def testExplicitSubsetSurvivesRouteAndAppendOnlyHistoryAdapters(self) -> None:
        subset = self.current_subset_scope_payload()
        empty = self.controller._empty_implementation_history(subset["scope"])
        task_path = f"{self.feature}/tasks.md"
        task_evidence = [{"path": task_path,
                          "sha256": hashlib.sha256((self.root / task_path).read_bytes()).hexdigest()}]
        event = {"event_id": "subset-session-1", "predecessor_sha256": "0" * 64,
                 "scope_sha256": subset["scope"]["scope_sha256"], "event_kind": "coder-session-start",
                 "declared_node_id": "prepare-scoped-prerequisites", "occurred_at": "2026-10-08T12:00:00Z",
                 "evidence": task_evidence, "coder_session_id": "subset-session-1",
                 "coder_sessions_started": 1, "source_attempts_started": 0, "execution_kind": "preparation"}
        event["sha256"] = hashlib.sha256(
            json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
        appended = self.controller.append_implementation_execution_event(self.root, {
            **subset, "event": event, "retained_history_sha256": empty["sha256"]})
        self.assertEqual("ready", appended["state"], appended)
        outcome = {"event_id": "subset-session-1-outcome",
                   "predecessor_sha256": appended["history"]["events"][-1]["sha256"],
                   "scope_sha256": subset["scope"]["scope_sha256"], "event_kind": "coder-session-outcome",
                   "declared_node_id": "prepare-scoped-prerequisites", "occurred_at": "2026-10-08T12:00:01Z",
                   "evidence": task_evidence, "coder_session_id": "subset-session-1",
                   "coder_sessions_started": 1, "source_attempts_started": 0, "outcome": "completed"}
        outcome["sha256"] = hashlib.sha256(
            json.dumps(outcome, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
        closed = self.controller.append_implementation_execution_event(self.root, {
            **subset, "event": outcome, "retained_history_sha256": appended["history_sha256"]})
        self.assertEqual("ready", closed["state"], closed)
        route = self.controller.route_scoped_implementation(self.root, {
            **subset, "retained_history_sha256": closed["history_sha256"],
            "assessment": {"state": "continue", "reason_code": "preparation-required", "evidence": task_evidence,
                           "remaining_ids": ["task:T001"], "resolved_ids": [],
                           "next_step_id": "prepare-scoped-prerequisites"},
            "eligible_task_ids": ["T001"],
            "declared_node_ids": ["prepare-scoped-prerequisites", "implement-tasks"]})
        self.assertEqual("continue", route["state"], route)
        self.assertEqual("prepare-scoped-prerequisites", route["next_step_id"])


class MetricsRunIdentityTests(unittest.TestCase):
    """Inspection allocates a separate correlation identity for each workflow invocation."""

    def setUp(self) -> None:
        self.controller = load_module("farmboy_controller_metrics_identity", CONTROLLER_DIR / "controller.py")
        self.metrics = load_module("farmboy_metrics_failure_isolation", CONTROLLER_DIR / "metrics.py")

    def testEmissionFailurePreservesObservedAgentOutcomeAssignmentAndHumanGate(self) -> None:
        outcome_evidence = [{
            "path": "specs/022-local-workflow-agent-timing-metrics/tasks.md",
            "sha256": hashlib.sha256((ROOT / "specs/022-local-workflow-agent-timing-metrics/tasks.md").read_bytes()).hexdigest(),
        }]
        observed_output = {
            "agent_name": "FarmBoy Reviewer",
            "outcome": {
                "state": "needs-human",
                "reason_code": "operator-review-required",
                "evidence": outcome_evidence,
                "remaining_ids": ["operator-review"],
                "resolved_ids": [],
                "gate_step_id": "review-gate",
            },
            "gate_options": ["approve", "defer"],
        }
        original_output = copy.deepcopy(observed_output)
        emit_record = getattr(self.metrics, "emit_record", None)
        self.assertTrue(callable(emit_record), "T010 record publication is not implemented yet")
        with tempfile.TemporaryDirectory() as temporary:
            blocked_parent = Path(temporary) / "not-a-directory"
            blocked_parent.write_text("occupied", encoding="utf-8")
            warning = emit_record({
                "schema_version": 1,
                "invocation_id": str(uuid.uuid4()),
                "run_id": str(uuid.uuid4()),
                "step_id": "review-artifacts",
                "invocation_kind": "execution",
                "agent_name": "FarmBoy Reviewer",
                "skill_id": "farmboy-analyze-remediate",
                "workflow_id": "farmboy-analyze-remediate",
                "project_label": "farmboy",
                "started_at": "2026-10-12T18:00:00.000Z",
                "finished_at": "2026-10-12T18:00:01.000Z",
                "duration_ms": 1000,
                "model": None,
                "effort": None,
            }, directory=blocked_parent / "metrics")

            self.assertFalse(warning.get("emitted"), warning)
            self.assertIn(warning.get("warning_code"), {"destination-unavailable", "storage-failed"})
            self.assertEqual(original_output, observed_output)

        validated_outcome = self.controller.validate_outcome_envelope(
            observed_output["outcome"], ROOT,
            loop_body_step_ids={"review-agent", "correct"},
            human_gate_step_ids={"review-gate"},
        )
        self.assertEqual({"action": "needs-human", "gate_step_id": "review-gate"},
                         self.controller.route_assessment(
                             validated_outcome,
                             loop_body_step_ids={"review-agent", "correct"},
                             human_gate_step_ids={"review-gate"},
                         ))
        gate = self.controller.render_template({
            "id": "review-gate", "type": "gate", "options": ["{{ steps.review-agent.output.gate_options }}"],
        }, {}, {"review-agent": observed_output})
        self.assertEqual("approve", self.controller.validate_gate_choice(gate, "1"))
        branch = self.controller.select_switch_branch({
            "id": "route-review", "type": "switch",
            "cases": {"approve": [{"id": "record-approval", "type": "prompt"}],
                      "defer": [{"id": "preserve-review", "type": "prompt"}]},
        }, "approve")
        self.assertEqual(["record-approval"], [step["id"] for step in branch])

    def test_inspectCreatesFreshMetricsRunIdWithoutChangingAgentAssignments(self) -> None:
        definition = yaml.safe_load((ROOT / "workflows/farmboy-analyze-remediate/workflow.yml").read_text(encoding="utf-8"))

        def inspect_once() -> dict:
            output = io.StringIO()
            with patch.object(self.controller, "verify_controller_install", return_value={}), \
                    patch.object(self.controller, "load_installed_definition", return_value=definition), \
                    patch.object(self.controller, "installation_fingerprints", return_value={}), \
                    patch.object(self.controller.subprocess, "run", return_value=type(
                        "Process", (), {"stdout": "specify 1.0.10.dev0+pegagio.2"}
                    )()), redirect_stdout(output):
                status = self.controller.main([
                    "inspect", "--project", str(ROOT), "--workflow-id", "farmboy-analyze-remediate",
                    "--specify", "/bin/true", "--expected-version", "1.0.10.dev0+pegagio.2",
                    "--skill-id", "farmboy-analyze-remediate", "--input",
                    "feature_context=specs/022-local-workflow-agent-timing-metrics",
                ])
            self.assertEqual(0, status)
            return json.loads(output.getvalue())

        first = inspect_once()
        second = inspect_once()
        first_id = uuid.UUID(first["metrics_run_id"])
        second_id = uuid.UUID(second["metrics_run_id"])

        self.assertNotEqual(first_id, second_id)
        self.assertEqual(
            [(item.step_id, item.agent_name) for item in self.controller.collect_agent_assignments(definition["steps"])],
            [(item["step_id"], item["agent_name"]) for item in first["agent_assignments"]],
        )
        self.assertNotIn("recovery_run_id", first)

    def test_inspectPreservesResolvedInputsAndWorkflowGraphAlongsideMetricsIdentity(self) -> None:
        definition = yaml.safe_load((ROOT / "workflows/farmboy-analyze-remediate/workflow.yml").read_text(encoding="utf-8"))
        output = io.StringIO()
        with patch.object(self.controller, "verify_controller_install", return_value={}), \
                patch.object(self.controller, "load_installed_definition", return_value=definition), \
                patch.object(self.controller, "installation_fingerprints", return_value={}), \
                patch.object(self.controller.subprocess, "run", return_value=type(
                    "Process", (), {"stdout": "specify 1.0.10.dev0+pegagio.2"}
                )()), redirect_stdout(output):
            status = self.controller.main([
                "inspect", "--project", str(ROOT), "--workflow-id", "farmboy-analyze-remediate",
                "--specify", "/bin/true", "--expected-version", "1.0.10.dev0+pegagio.2",
                "--skill-id", "farmboy-analyze-remediate", "--input",
                "feature_context=specs/022-local-workflow-agent-timing-metrics",
            ])

        inspected = json.loads(output.getvalue())
        self.assertEqual(0, status)
        self.assertEqual(definition["steps"], inspected["steps"])
        self.assertEqual(
            {"feature_context": "specs/022-local-workflow-agent-timing-metrics", "integration": "codex"},
            inspected["resolved_inputs"],
        )
        self.assertTrue(inspected["preflight_inputs_valid"])
        self.assertTrue(uuid.UUID(inspected["metrics_run_id"]))


if __name__ == "__main__":
    unittest.main()
