"""Disposable generic-roadmap consumers for workflow-owned milestone policy."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest

import yaml
import test_phase_lifecycle as lifecycle_test_support
from test_phase_lifecycle import ROOT, load_module, sha


class WorkflowRoadmapBoundaryTests(unittest.TestCase):
    """Test delivered graphs and readback without extension lifecycle machinery."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.module = load_module()
        self.policy = self.module._workflow_module(self.root)
        self.feature = "specs/901-boundary"
        self.time = "2026-10-10T12:00:00Z"
        # A minimal generic configuration API fixture contains no workflow, phase,
        # role, model, milestone, receipt or consumer-package policy.
        self.write(".specify/extensions/flow-roadmap/scripts/python/load_config.py", '''
class ContractError(Exception):
    pass

def resolve_configuration(project, payload, yaml):
    return {"roadmap_path": ".specify/memory/roadmap.md"}
''')
        self.write(".specify/extensions/flow-roadmap/extension.yml", yaml.safe_dump({
            "extension": {"id": "flow-roadmap", "version": "0.4.0"}, "provides": {"commands": [
                {"name": "speckit.flow-roadmap.write"}, {"name": "speckit.flow-roadmap.brief"}]}}))
        self.write(".specify/extensions/flow-roadmap/scripts/python/review_contract.py", "# generic target resolution\n")
        self.write(".specify/extensions/flow-roadmap/scripts/python/roadmap_write.py", "# generic guarded amendment fixture\n")
        for name in ("phase_lifecycle.py", "milestone_policy.py"):
            self.write(f".specify/farmboy/scripts/python/{name}", (ROOT / "controllers/farmboy/scripts/python" / name).read_text())
        self.write(".specify/farmboy/manifest.yml", (ROOT / "controllers/farmboy/manifest.yml").read_text())
        self.write(".specify/farmboy/skills-install.json", "{}")
        self.write(".specify/bundle-records.json", "{}")
        self.write(".specify/feature.json", json.dumps({"feature_directory": self.feature}))
        self.write(".specify/memory/constitution.md", "# Approved governance\n")
        for name in ("spec.md", "plan.md", "tasks.md"):
            self.write(f"{self.feature}/{name}", f"# Reviewed {name}\n")
        self.write("src/feature.py", "# implementation evidence\n")
        self.write("tests/feature.py", "# validation evidence\n")

    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def refresh(self, request):
        request["snapshot"]["source_map"] = {
            p.relative_to(self.root).as_posix(): sha(p.read_bytes())
            for p in self.root.rglob("*") if p.is_file()}
        request["snapshot"] = self.policy.collect_snapshot(self.root, request, yaml)
        return request

    def request(self, phase="implement", current=None):
        target = self.policy.PHASES[phase]
        current = current or self.policy.STATUSES[self.policy.STATUSES.index(target) - 1]
        workflow = f"farmboy-{phase}"
        graph = (ROOT / f"workflows/{workflow}/workflow.yml").read_text()
        self.write(f".specify/workflows/{workflow}/workflow.yml", graph)
        self.roadmap = self.write(".specify/memory/roadmap.md", f'''# Roadmap

### 901 — Boundary [status: {current}]

- **Spec dir**: `{self.feature}/`
- **Depends on**: None
- **Outcome**: Preserve exact scope.

### 902 — Unrelated [status: planned]

- **Depends on**: None
- **Outcome**: Keep these bytes.

**Version**: 1.0.0 | **Ratified**: 2026-10-01 | **Last Amended**: 2026-10-01
''')
        scope = sha((self.root / self.feature / "spec.md").read_bytes())
        checks = sorted(self.policy.CHECKS[target])
        artifacts = {f"{self.feature}/{name}": sha((self.root / self.feature / name).read_bytes())
                     for name in ("spec.md", "plan.md", "tasks.md")}
        if phase == "closeout":
            artifacts.update({p: sha((self.root / p).read_bytes()) for p in ("src/feature.py", "tests/feature.py")})
        references = []
        for index, role in enumerate(sorted(self.policy.ROLES[target])):
            relative = f"{self.feature}/validation/review-{phase}-{index}.json"
            record = {"schema_version": "1.0", "kind": "independent-review", "reviewer": role,
                      "state": "ready", "feature_directory": self.feature, "scope_sha256": scope,
                      "artifact_digests": artifacts, "required_check_ids": checks,
                      "satisfied_check_ids": checks, "unresolved_ids": []}
            self.write(relative, json.dumps(record))
            references.append({"path": relative, "sha256": sha((self.root / relative).read_bytes()), "kind": record["kind"]})
        decision = f"{self.feature}/validation/operator-decision.json"
        self.write(decision, json.dumps({"schema_version": "1.0", "policy_sha256": self.module.POLICY_SHA256,
            "feature_directory": self.feature, "phase": phase, "scope_sha256": scope,
            "kind": "routine-invocation", "reference": "current-trusted-main-invocation"}))
        group = {"milestone": target, "owning_phase": phase, "assessments": references,
                 "required_check_ids": checks, "satisfied_check_ids": checks, "unresolved_ids": [],
                 "artifact_digests": artifacts, "historical_activity": [], "pending_future_ids": []}
        snapshot = {"schema_version": "1.0", "feature_directory": self.feature, "entry_id": "901",
                    "phase": phase, "workflow_id": workflow, "workflow_version": yaml.safe_load(graph)["workflow"]["version"],
                    "run_id": "current-run", "current_status": current, "source_map": {},
                    "scope_sha256": scope, "dependency_states": [], "pending_future_ids": []}
        request = {"schema_version": "1.0", "action": "prepare", "phase": phase, "feature_directory": self.feature,
                   "entry_id": "901", "run_id": snapshot["run_id"], "workflow_id": workflow,
                   "workflow_version": snapshot["workflow_version"], "mode": "normal", "decision_reference": decision,
                   "milestone_evidence": [group], "snapshot": snapshot}
        return self.refresh(request)

    def apply_generic_delta(self, proposal):
        # Simulate the public writer's exact amendment contract, preserving all
        # preexisting reports and entry bytes through each adjacent edge.
        text = self.roadmap.read_text().replace(f"[status: {proposal['from_status']}]", f"[status: {proposal['to_status']}]", 1)
        footer = self.policy.FOOTER.search(text)
        version = f"{footer[1]}.{footer[2]}.{int(footer[3])+1}"
        replacement = f"**Version**: {version} | **Ratified**: {footer[4]} | **Last Amended**: 2026-10-10"
        text = text[:footer.start()] + replacement + text[footer.end():]
        refs = sorted({ref["path"] for group in proposal["milestone_evidence"]
                       for ref in group["assessments"] + group["historical_activity"]})
        impact = ("<!--\nSYNC IMPACT REPORT\nAuthorization: " + proposal["decision"]["reference"]
                  + "\nEvidence paths: " + json.dumps(refs) + "\n-->\n")
        self.roadmap.write_text(impact + text)

    def verify(self, proposal, success=True):
        return self.module.workflow_check(self.root, {"action": "verify-effect", "proposal": proposal,
            "command_succeeded": success, "occurred_at": self.time})

    def test_allPhaseGraphsUseGenericDeltaAndOwnedReadback(self):
        for phase in self.policy.PHASES:
            with self.subTest(phase=phase):
                request = self.request(phase)
                before = self.roadmap.read_bytes()
                prepared = self.module.prepare(self.root, request)
                self.assertEqual("ready", prepared["state"], prepared)
                self.assertNotIn("PHASE_MILESTONE_REQUEST", prepared["roadmap_delta"])
                self.assertEqual(before, self.roadmap.read_bytes())
                retry = {**request, "action": "revalidate", "proposal": prepared["proposal"]}
                self.assertEqual("ready", self.module.revalidate(self.root, retry)["state"])
                self.apply_generic_delta(prepared["proposal"])
                result = self.verify(prepared["proposal"])
                self.assertEqual("verified", result["state"], result)
                self.assertEqual("applied", result["receipt"]["effect_state"])
                self.assertEqual("recorded", result["receipt"]["record_state"])
                self.assertFalse((self.root / ".specify/extensions/flow-roadmap/scripts/python/phase_lifecycle.py").exists())
                self.assertFalse((self.root / ".codex/agents").exists())

    def test_readbackPreservesAppliedAfterCommandFailure(self):
        proposal = self.module.prepare(self.root, self.request())["proposal"]
        self.apply_generic_delta(proposal)
        result = self.verify(proposal, False)
        self.assertEqual("blocked", result["state"])
        self.assertEqual("applied", result["receipt"]["effect_state"])

    def test_readbackPreservesAppliedAfterSourceDrift(self):
        proposal = self.module.prepare(self.root, self.request())["proposal"]
        self.apply_generic_delta(proposal)
        self.write(f"{self.feature}/spec.md", "changed after effect")
        result = self.verify(proposal)
        self.assertEqual("blocked", result["state"])
        self.assertEqual("applied", result["receipt"]["effect_state"])
        self.assertEqual("post-effect-source-changed", result["reason_code"])

    def test_readbackDistinguishesNoEffectFromPartialEffect(self):
        for partial in (False, True):
            with self.subTest(partial=partial):
                proposal = self.module.prepare(self.root, self.request())["proposal"]
                if partial:
                    self.roadmap.write_text(self.roadmap.read_text().replace("Keep these bytes.", "unrelated mutation"))
                result = self.verify(proposal)
                self.assertEqual("blocked", result["state"])
                self.assertEqual("indeterminate" if partial else "not-applied", result["receipt"]["effect_state"])

    def test_readbackRejectsUnrelatedEditsAndMissingMetadata(self):
        for edit in ("unrelated", "metadata", "provenance"):
            with self.subTest(edit=edit):
                proposal = self.module.prepare(self.root, self.request())["proposal"]
                self.apply_generic_delta(proposal)
                text = self.roadmap.read_text()
                text = text.replace("Keep these bytes.", "mutated") if edit == "unrelated" else text
                text = text.replace("**Version**: 1.0.1", "**Version**: 1.0.0") if edit == "metadata" else text
                text = text.replace(proposal["decision"]["reference"], "missing authorization") if edit == "provenance" else text
                self.roadmap.write_text(text)
                result = self.verify(proposal)
                self.assertEqual("blocked", result["state"])
                self.assertEqual("indeterminate", result["receipt"]["effect_state"])

    def test_recordFailureRetainsAppliedEffect(self):
        proposal = self.module.prepare(self.root, self.request())["proposal"]
        self.apply_generic_delta(proposal)
        destination = self.root / self.feature / "validation/phase-lifecycle"
        destination.symlink_to(self.root / "outside")
        result = self.verify(proposal)
        self.assertEqual("blocked", result["state"])
        self.assertEqual("applied", result["receipt"]["effect_state"])
        self.assertEqual("failed", result["receipt"]["record_state"])

    def test_revalidateRejectsDriftAndNoopNeverWrites(self):
        request = self.request()
        prepared = self.module.prepare(self.root, request)
        self.write(f"{self.feature}/tasks.md", "changed")
        retry = {**request, "action": "revalidate", "proposal": prepared["proposal"]}
        self.assertEqual("blocked", self.module.revalidate(self.root, retry)["state"])
        request = self.request(current="in-progress")
        before = self.roadmap.read_bytes()
        result = self.module.prepare(self.root, request)
        self.assertEqual("no-op", result["state"], result)
        self.assertNotIn("roadmap_delta", result)
        self.assertEqual(before, self.roadmap.read_bytes())

    def test_deferredStateRequiresOperatorResolution(self):
        result = self.module.prepare(self.root, self.request(current="deferred"))
        self.assertEqual("question", result["state"], result)
        self.assertNotIn("roadmap_delta", result)

    def test_dependencyAndReviewerFailuresPreventDelta(self):
        request = self.request()
        self.roadmap.write_text(self.roadmap.read_text().replace("**Depends on**: None", "**Depends on**: 902", 1))
        request = self.refresh(request)
        result = self.module.prepare(self.root, request)
        self.assertEqual("blocked", result["state"], result)
        request = self.request()
        ref = request["milestone_evidence"][0]["assessments"][0]
        record = json.loads((self.root / ref["path"]).read_text())
        record["reviewer"] = "Unexpected Reviewer"
        self.write(ref["path"], json.dumps(record))
        ref["sha256"] = sha((self.root / ref["path"]).read_bytes())
        request = self.refresh(request)
        self.assertEqual("blocked", self.module.prepare(self.root, request)["state"])

    def test_repeatedReadbackRetainsOriginalReceipt(self):
        proposal = self.module.prepare(self.root, self.request())["proposal"]
        self.apply_generic_delta(proposal)
        first = self.verify(proposal)
        second = self.verify(proposal)
        self.assertEqual(first, second)
        self.assertEqual(1, len(list((self.root / self.feature / "validation/phase-lifecycle").glob("*.json"))))

    def test_authoringProofRunsLocallyBeforeGenericBrief(self):
        request = self.request("specify")
        self.write(f"{self.feature}/checklists/requirements.md", "# Quality\n\n- [x] Reviewed\n")
        checks = ["authoring-quality", "clarification", "linkage", "independent-review"]
        artifacts = {path: sha((self.root / path).read_bytes()) for path in
                     (f"{self.feature}/spec.md", f"{self.feature}/checklists/requirements.md")}
        record = {"schema_version": "1.0", "kind": "independent-authoring-review", "reviewer": "FarmBoy Reviewer",
                  "state": "ready", "feature_directory": self.feature, "scope_sha256": request["snapshot"]["scope_sha256"],
                  "artifact_digests": artifacts, "required_check_ids": checks, "satisfied_check_ids": checks,
                  "unresolved_ids": []}
        review = f"{self.feature}/validation/authoring-review.json"
        self.write(review, json.dumps(record))
        packet_path = f"{self.feature}/validation/specification-ready.json"
        packet = {"schema_version": "1.0", "feature_directory": self.feature, "scope_sha256": record["scope_sha256"],
                  "assessments": [{"path": review, "sha256": sha((self.root / review).read_bytes()), "kind": record["kind"]}],
                  "required_check_ids": checks, "satisfied_check_ids": checks, "artifact_digests": artifacts,
                  "unresolved_ids": []}
        self.write(packet_path, json.dumps(packet))
        result = self.module.workflow_check(self.root, {"action": "validate-specification-ready", "packet_path": packet_path})
        self.assertEqual("ready", result["state"])
        self.write(f"{self.feature}/checklists/requirements.md", "- [ ] Missing quality\n")
        with self.assertRaises(self.module.LifecycleError):
            self.module.workflow_check(self.root, {"action": "validate-specification-ready", "packet_path": packet_path})

    def test_deliveredGenericConfigurationWithoutExtensionLifecycleHelper(self):
        source = os.environ.get("FARMBOY_TEST_ROADMAP_SOURCE")
        if not source:
            self.skipTest("supply FARMBOY_TEST_ROADMAP_SOURCE for delivered generic loader validation")
        request = self.request()
        loader = Path(source) / "scripts/python/load_config.py"
        self.write(".specify/extensions/flow-roadmap/scripts/python/load_config.py", loader.read_text())
        self.refresh(request)
        result = self.module.prepare(self.root, request)
        self.assertEqual("ready", result["state"], result)
        self.assertFalse((self.root / ".specify/extensions/flow-roadmap/scripts/python/phase_lifecycle.py").exists())

    def test_yamlPolicyRejectsDuplicateKeysAndAliases(self):
        for text in ("workflow: {}\nworkflow: {}", "workflow: &x {}\nsteps: *x"):
            with self.subTest(text=text), self.assertRaises(self.policy.ContractError):
                self.policy.load_yaml(text, "workflow", yaml)

    def test_controllerCliPreparesAndVerifiesGenericAmendment(self):
        request = self.request()
        command = [sys.executable, str(ROOT / "controllers/farmboy/scripts/python/controller.py"),
                   "phase-lifecycle", "--project", str(self.root)]
        prepared_process = subprocess.run(command, input=json.dumps(request), text=True, capture_output=True)
        self.assertEqual(0, prepared_process.returncode, prepared_process.stderr)
        prepared = json.loads(prepared_process.stdout)
        self.assertEqual("ready", prepared["state"])
        self.apply_generic_delta(prepared["proposal"])
        result = subprocess.run(command, input=json.dumps({"action": "verify-effect", "proposal": prepared["proposal"],
            "command_succeeded": True, "occurred_at": self.time}), text=True, capture_output=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("verified", json.loads(result.stdout)["state"])

    def test_recoveryPolicyValidatesRetainedHistoricalOccurrence(self):
        request = self.request()
        group = request["milestone_evidence"][0]
        path = f"{self.feature}/validation/historical-start.json"
        for occurrence, valid in (("2026-10-01T12:00:00Z", True), ("2026-10-01T12:00:00", False)):
            with self.subTest(occurrence=occurrence):
                self.write(path, json.dumps({"kind": "authorized-implementation-start",
                    "scope_sha256": request["snapshot"]["scope_sha256"], "occurred_at": occurrence}))
                group["historical_activity"] = [{"path": path, "sha256": sha((self.root / path).read_bytes()),
                    "kind": "authorized-implementation-start"}]
                if valid:
                    self.assertEqual(group, self.policy.validate_milestone(
                        self.root, [group], "in-progress", request["snapshot"], recovery=True))
                else:
                    with self.assertRaisesRegex(self.policy.ContractError, "occurrence-time-invalid"):
                        self.policy.validate_milestone(self.root, [group], "in-progress", request["snapshot"], recovery=True)

    def test_legacyRoadmapCannotPrepareGenericMilestone(self):
        request = self.request()
        path = ".specify/extensions/flow-roadmap/extension.yml"
        manifest = yaml.safe_load((self.root / path).read_text())
        manifest["extension"]["version"] = "0.3.0"
        self.write(path, yaml.safe_dump(manifest))
        request["snapshot"]["source_map"][path] = sha((self.root / path).read_bytes())
        result = self.module.prepare(self.root, request)
        self.assertEqual("blocked", result["state"])
        self.assertEqual("generic-roadmap-contract-unavailable", result["reason_code"])
        self.assertNotIn("roadmap_delta", result)

    def test_genericWriterDriftBlocksRevalidation(self):
        request = self.request()
        prepared = self.module.prepare(self.root, request)
        self.write(".specify/extensions/flow-roadmap/scripts/python/roadmap_write.py", "# changed writer\n")
        result = self.module.revalidate(self.root, {**request, "action": "revalidate", "proposal": prepared["proposal"]})
        self.assertEqual("blocked", result["state"])
        self.assertNotIn("roadmap_delta", result)

    def add_recovery_attestation(self, request, packet):
        history = self.module.validate_recovery_start_history(self.root, packet)
        history_path = f"{self.feature}/validation/phase-lifecycle/start-history-validation.json"
        self.write(history_path, json.dumps(history))
        identity = {key: request[key] for key in ("workflow_id", "workflow_version", "run_id")}
        run_prefix = f".specify/flow-controllers/runs/{request['run_id']}"
        dispatch = {**identity,
                    "child_tasks": [{"agent": "FarmBoy Reviewer", "step_id": "attest-recovery-start", "child_id": "reviewer-child"}],
                    "effective_assignments": [{"agent_name": "FarmBoy Reviewer", "step_id": "attest-recovery-start"}]}
        self.write(f"{run_prefix}/summary.json", json.dumps(dispatch))
        captured = f"{run_prefix}/dispatch-summary-at-capture.json"
        self.write(captured, json.dumps(dispatch))
        witness_path = f"{run_prefix}/recovery-start-dispatch-witness.json"
        witness = {"schema_version": "1.0", "kind": "main-retained-native-dispatch-witness",
                   "feature_directory": self.feature, "scope_sha256": history["scope_sha256"], **identity,
                   "step_id": "attest-recovery-start", "agent": "FarmBoy Reviewer", "child_id": "reviewer-child",
                   "source_summary": {"path": captured, "sha256": sha((self.root / captured).read_bytes())}}
        self.write(witness_path, json.dumps(witness))
        artifacts = {f"{self.feature}/{name}": sha((self.root / self.feature / name).read_bytes())
                     for name in ("spec.md", "plan.md", "tasks.md")}
        attestation = {"schema_version": "1.0", "kind": "authorized-implementation-start", "reviewer": "FarmBoy Reviewer",
                       "state": "ready", "feature_directory": self.feature, "scope_sha256": history["scope_sha256"],
                       **identity, "step_id": "attest-recovery-start", "child_id": "reviewer-child",
                       "source_run_id": history["source_run_id"], "original_scope_sha256": history["original_scope_sha256"],
                       "occurred_at": history["occurred_at"],
                       "history_validation": {"path": history_path, "sha256": sha((self.root / history_path).read_bytes())},
                       "dispatch_witness": {"path": witness_path, "sha256": sha((self.root / witness_path).read_bytes())},
                       "recorded_dispatch": {"agent": "FarmBoy Reviewer", "step_id": "attest-recovery-start",
                                             **identity, "child_id": "reviewer-child"},
                       "required_check_ids": sorted(self.module.START_CHECKS), "satisfied_check_ids": sorted(self.module.START_CHECKS),
                       "unresolved_ids": [], "artifact_digests": artifacts}
        path = f"{self.feature}/validation/phase-lifecycle/authorized-implementation-start.json"
        self.write(path, json.dumps(attestation))
        return {"path": path, "sha256": sha((self.root / path).read_bytes()), "kind": attestation["kind"]}

    def recovery_request(self):
        helper = lifecycle_test_support.RecoveryStartHistoryTests()
        helper.feature = self.feature
        packet = helper._materialize(self.root)
        groups = [self.request(phase)["milestone_evidence"][0] for phase in self.policy.PHASES]
        request = self.request("closeout", current="planned")
        request["mode"] = "recovery"
        request["milestone_evidence"] = groups
        groups[1]["historical_activity"] = [self.add_recovery_attestation(request, packet)]
        return self.refresh(request)

    def test_readbackPreservesEveryHistoricalImpactReport(self):
        for tamper in ("delete", "modify"):
            with self.subTest(tamper=tamper):
                request = self.request()
                historical = "<!--\nSYNC IMPACT REPORT\nEarlier authority and evidence.\n-->\n"
                self.roadmap.write_text(historical + self.roadmap.read_text())
                request = self.refresh(request)
                proposal = self.module.prepare(self.root, request)["proposal"]
                self.apply_generic_delta(proposal)
                text = self.roadmap.read_text()
                text = text.replace(historical, "") if tamper == "delete" else text.replace("Earlier authority", "Tampered authority")
                self.roadmap.write_text(text)
                result = self.verify(proposal)
                self.assertEqual("blocked", result["state"])
                self.assertEqual("indeterminate", result["receipt"]["effect_state"])

    def test_readbackUsesUTCDateForOffsetTimestamp(self):
        proposal = self.module.prepare(self.root, self.request())["proposal"]
        self.apply_generic_delta(proposal)
        self.time = "2026-10-09T20:00:00-07:00"
        self.assertEqual("verified", self.verify(proposal)["state"])

    def test_allPhasesRetainEqualAndAdvancedStatesWithoutMutation(self):
        for phase, ceiling in self.policy.PHASES.items():
            for current in self.policy.STATUSES[self.policy.STATUSES.index(ceiling):]:
                with self.subTest(phase=phase, current=current):
                    groups = [self.request(p)["milestone_evidence"][0] for p in self.policy.PHASES]
                    request = self.request(phase, current=current)
                    request["milestone_evidence"] = groups
                    request = self.refresh(request)
                    before = {p: (self.root/p).read_bytes() for p in request["snapshot"]["source_map"]}
                    result = self.module.prepare(self.root, request)
                    self.assertEqual("no-op", result["state"], result)
                    self.assertEqual(current, result["retained_status"])
                    self.assertNotIn("roadmap_delta", result)
                    self.assertEqual(before, {p: (self.root/p).read_bytes() for p in before})

    def test_closeoutRecoveryExecutesThreeAdjacentEdgesAndPreservesReceipts(self):
        request = self.recovery_request()
        receipts = {}
        for target in ("specced", "in-progress", "implemented"):
            request = self.refresh(request)
            prepared = self.module.prepare(self.root, request)
            self.assertEqual("ready", prepared["state"], prepared)
            proposal = prepared["proposal"]
            self.assertEqual(target, proposal["to_status"])
            self.assertEqual("ready", self.module.revalidate(self.root, {**request, "action": "revalidate", "proposal": proposal})["state"])
            self.apply_generic_delta(proposal)
            result = self.verify(proposal)
            self.assertEqual("verified", result["state"], result)
            receipt_path = self.root / self.feature / "validation/phase-lifecycle" / (proposal["effect_id"] + ".json")
            receipts[receipt_path] = receipt_path.read_bytes()
            for retained, raw in receipts.items():
                self.assertEqual(raw, retained.read_bytes())
            self.assertEqual(len(receipts), self.roadmap.read_text().count("SYNC IMPACT REPORT"))
        request = self.refresh(request)
        self.assertEqual("no-op", self.module.prepare(self.root, request)["state"])

    def test_recoveryMissingOrStaleIntermediateProofPreventsNextEffect(self):
        for bad_proof in ("missing", "stale"):
            with self.subTest(bad_proof=bad_proof):
                request = self.recovery_request()
                prepared = self.module.prepare(self.root, request)
                self.assertEqual("ready", prepared["state"], prepared)
                self.apply_generic_delta(prepared["proposal"])
                self.assertEqual("verified", self.verify(prepared["proposal"])["state"])
                request = self.refresh(request)
                if bad_proof == "missing":
                    request["milestone_evidence"] = [g for g in request["milestone_evidence"] if g["milestone"] != "in-progress"]
                else:
                    reference = request["milestone_evidence"][1]["historical_activity"][0]
                    self.write(reference["path"], "{}")
                before = self.roadmap.read_bytes()
                result = self.module.prepare(self.root, request)
                self.assertEqual("blocked", result["state"], result)
                self.assertNotIn("roadmap_delta", result)
                self.assertEqual(before, self.roadmap.read_bytes())

    def test_newReportRequiresCompleteExactProvenance(self):
        request = self.recovery_request()
        proposal = self.module.prepare(self.root, request)["proposal"]
        self.apply_generic_delta(proposal)
        text = self.roadmap.read_text()
        line = next(line for line in text.splitlines() if line.startswith("Evidence paths: "))
        paths = json.loads(line.removeprefix("Evidence paths: "))
        history = request["milestone_evidence"][1]["historical_activity"][0]["path"]
        self.assertIn(history, paths)
        self.roadmap.write_text(text.replace(line, "Evidence paths: " + json.dumps([path for path in paths if path != history]), 1))
        result = self.verify(proposal)
        self.assertEqual("blocked", result["state"])
        self.assertEqual("roadmap-delta-provenance-missing", result["reason_code"])
        self.assertEqual("indeterminate", result["receipt"]["effect_state"])


if __name__ == "__main__":
    unittest.main()
