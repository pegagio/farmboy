"""Installed-consumer execution of the deterministic SI001-SI015 route matrix."""
from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
import os
import re
import shlex
import shutil
import subprocess
import tempfile
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import patch


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _evidence(consumer: Path, case_id: str, name: str) -> list[dict[str, str]]:
    relative = f".specify/si-evidence/{case_id}/{name}.json"
    path = consumer / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"case": case_id, "kind": name, "fixture": True}, sort_keys=True) + "\n")
    return [{"path": relative, "sha256": sha(path)}]


def _append_event(controller_module: Any, consumer: Path, scope_payload: dict[str, Any], history: dict[str, Any],
                  case_id: str, event_kind: str, *, session: int, attempts: int, execution_kind: str,
                  outcome: str | None = None, same_child_resume: bool = False,
                  current_source_evidence: list[dict[str, str]] | None = None) -> dict[str, Any]:
    node = "prepare-scoped-prerequisites" if execution_kind == "preparation" else "implement-tasks"
    item: dict[str, Any] = {
        "event_id": f"{case_id}-{len(history['events']) + 1}",
        "predecessor_sha256": history["events"][-1]["sha256"] if history["events"] else "0" * 64,
        "scope_sha256": scope_payload["scope"]["scope_sha256"],
        "event_kind": event_kind, "declared_node_id": node,
        "occurred_at": f"2026-10-08T12:{session:02d}:{attempts:02d}Z",
        "evidence": [*_evidence(consumer, case_id, f"event-{len(history['events']) + 1}"),
                     *(current_source_evidence or [])],
        "coder_session_id": f"{case_id}-session-{session}",
        "coder_sessions_started": session, "source_attempts_started": attempts,
    }
    if event_kind in {"coder-session-start", "source-attempt-start"}:
        item["execution_kind"] = execution_kind
    elif event_kind == "coder-session-outcome":
        item["outcome"] = outcome or "completed"
    else:
        item["same_child_resume"] = same_child_resume
    item["sha256"] = digest(item)
    result = controller_module.append_implementation_execution_event(consumer, {
        **scope_payload, "event": item, "retained_history_sha256": history["sha256"]})
    if result.get("state") != "ready":
        raise AssertionError(f"{case_id}: installed history append blocked: {result}")
    return result["history"]


def _record_sessions(controller_module: Any, consumer: Path, scope_payload: dict[str, Any], history: dict[str, Any],
                     case_id: str, sessions: int, attempts: int, *, outcomes: list[str] | None = None,
                     question: bool = False) -> dict[str, Any]:
    outcomes = outcomes or []
    preparation_count = sessions - attempts
    for number in range(history["coder_sessions_started"] + 1, sessions + 1):
        is_source = number > preparation_count
        execution_kind = "first-source-execution" if is_source and number == preparation_count + 1 else (
            "corrective-source-execution" if is_source else "preparation")
        attempts_before = number - preparation_count - 1 if is_source else 0
        history = _append_event(controller_module, consumer, scope_payload, history, case_id,
            "coder-session-start", session=number, attempts=attempts_before, execution_kind=execution_kind)
        if question and number == 1:
            history = _append_event(controller_module, consumer, scope_payload, history, case_id,
                "operator-input", session=number, attempts=attempts_before, execution_kind=execution_kind,
                same_child_resume=True)
        if is_source:
            history = _append_event(controller_module, consumer, scope_payload, history, case_id,
                "source-attempt-start", session=number, attempts=attempts_before + 1, execution_kind=execution_kind)
        event_attempts = attempts_before + 1 if is_source else attempts_before
        result = outcomes[number - 1] if number <= len(outcomes) else "completed"
        if result == "question-stopped":
            history = _append_event(controller_module, consumer, scope_payload, history, case_id,
                "coder-session-outcome", session=number, attempts=event_attempts, execution_kind=execution_kind,
                outcome="question-stopped")
            history = _append_event(controller_module, consumer, scope_payload, history, case_id,
                "operator-input", session=number, attempts=event_attempts, execution_kind=execution_kind,
                same_child_resume=True)
            history = _append_event(controller_module, consumer, scope_payload, history, case_id,
                "coder-session-outcome", session=number, attempts=event_attempts, execution_kind=execution_kind,
                outcome="completed")
        else:
            history = _append_event(controller_module, consumer, scope_payload, history, case_id,
                "coder-session-outcome", session=number, attempts=event_attempts, execution_kind=execution_kind,
                outcome=result)
    return history


POST_PASS_CAPTURE_FIELDS = ("scope", "trusted_request_reference", "retained_scope_sha256",
                           "entry_history_sha256", "task_tracking_successors", "producer_pairs",
                           "eligibility_request", "completion_branch")


def _capture_post_pass_command(prompt: str) -> list[str]:
    """Read the complete supported production invocation from the installed prompt."""
    fields_match = re.search(r"Serialize exactly these fields:\s*([^.]*)\.", prompt)
    command_match = re.search(r"Invoke `([^`]+)` with that JSON on stdin", prompt)
    if fields_match is None or command_match is None:
        raise AssertionError("installed production capture prompt omits its field list or executable command")
    fields = tuple(item.strip().removeprefix("and ").strip("`")
                   for item in fields_match.group(1).split(","))
    if fields != POST_PASS_CAPTURE_FIELDS:
        raise AssertionError(f"installed production capture request fields changed: {fields}")
    try:
        command = shlex.split(command_match.group(1), posix=True)
    except ValueError as error:
        raise AssertionError(f"installed production capture command is malformed: {error}") from error
    if (len(command) != 5 or command[0] != "python3"
            or command[1] != ".specify/farmboy/scripts/python/controller.py"
            or command[2] != "post-pass-capture" or command[3] != "--project"):
        raise AssertionError(f"installed production capture command is unsupported: {command}")
    project = command[4]
    if project != "$PWD" and (
            not Path(project).is_absolute() or any(character in project for character in "$`~*?[];|&<>()")):
        raise AssertionError("installed production capture project argument uses unsupported shell syntax")
    return command


def _capture_post_pass_state(controller_module: Any, consumer: Path, *, scope: dict[str, Any],
                             trusted_request_reference: str, retained_scope_sha256: str,
                             retained_history_sha256: str, incoming_successors: list[dict[str, Any]],
                             producer_records: list[dict[str, Any]], eligibility: dict[str, Any],
                             eligibility_request: dict[str, Any], completion: bool = False,
                             entry_history_sha256: str | None = None,
                             capture_command: list[str],
                             capture_observation: dict[str, Any] | None = None,
                             capture_environment: dict[str, str] | None = None) -> dict[str, Any]:
    """Exercise the installed production capture operation with actual fixture producers."""
    pairs = [{key: record[key] for key in (
        "tasker_step_id", "validator_step_id", "tasker_result", "validator_result")}
        for record in producer_records]
    request = {
        "scope": scope, "trusted_request_reference": trusted_request_reference,
        "retained_scope_sha256": retained_scope_sha256,
        "entry_history_sha256": entry_history_sha256 or retained_history_sha256,
        "task_tracking_successors": incoming_successors, "producer_pairs": pairs,
        "eligibility_request": eligibility_request, "completion_branch": completion}
    if (scope.get("request_reference") != trusted_request_reference
            or scope.get("scope_sha256") != retained_scope_sha256
            or eligibility_request.get("scope") != scope
            or eligibility_request.get("trusted_request_reference") != trusted_request_reference
            or eligibility_request.get("retained_scope_sha256") != retained_scope_sha256):
        raise AssertionError("post-pass capture request fields are detached from current scope bindings")
    command_template = list(capture_command)
    command = list(command_template)
    if command[4] == "$PWD":
        command[4] = str(consumer.resolve())
    completed = subprocess.run(command, cwd=consumer, input=json.dumps(request), text=True,
                               capture_output=True, check=False,
                               env={**os.environ, **(capture_environment or {})})
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise ValueError("post-pass-capture-command-output-invalid") from error
    if capture_observation is not None:
        capture_observation.update({
            "command_template": command_template,
            "project_argument_bound_to_consumer": command[4] == str(consumer.resolve()),
            "request": request,
            "request_fields": list(request),
            "request_sha256": digest(request),
            "scope_sha256": request["scope"]["scope_sha256"],
            "trusted_request_reference": request["trusted_request_reference"],
            "retained_scope_sha256": request["retained_scope_sha256"],
            "entry_history_sha256": request["entry_history_sha256"],
            "task_tracking_successors_sha256": digest(request["task_tracking_successors"]),
            "producer_pairs_sha256": digest(request["producer_pairs"]),
            "eligibility_request_sha256": digest(request["eligibility_request"]),
            "eligibility_scope_sha256": request["eligibility_request"]["scope"]["scope_sha256"],
            "eligibility_trusted_request_reference": request["eligibility_request"]["trusted_request_reference"],
            "eligibility_retained_scope_sha256": request["eligibility_request"]["retained_scope_sha256"],
            "completion_branch": request["completion_branch"],
            "return_code": completed.returncode,
            "result_state": result.get("state"),
        })
        audit_path = (capture_environment or {}).get("FARMBOY_SUBPROCESS_AUDIT_PATH")
        if audit_path:
            capture_observation["child_process_dispatches"] = [
                json.loads(line) for line in Path(audit_path).read_text(encoding="utf-8").splitlines()
                if line.strip()]
    if completed.returncode != 0 or result.get("state") != "ready":
        raise ValueError(result.get("reason_code", "post-pass-capture-invalid"))
    return result["post_pass_state"]


def _exercise_installed_task_revision_successor(controller_module: Any, consumer: Path,
                                                capture_command: list[str]) -> dict[str, Any]:
    """Exercise Tasker-approved append lineage through the installed adapters."""
    feature = "specs/998-tasker-revision-successor-fixture"
    feature_dir = consumer / feature
    feature_dir.mkdir(parents=True)
    spec_path = feature_dir / "spec.md"
    spec_path.write_text("# Approved task-revision fixture\n", encoding="utf-8")
    tasks_path = feature_dir / "tasks.md"
    source_path = feature_dir / "implementation.py"
    source_path.write_text("def result(): return 'before'\n", encoding="utf-8")
    before = "- [X] T001 Preserve completed history\n- [ ] T002 Existing selected work\n"
    tasks_path.write_text(before, encoding="utf-8")
    pointer = consumer / ".specify/feature.json"
    prior_pointer = pointer.read_bytes()
    pointer.write_text(json.dumps({"feature_directory": feature}) + "\n", encoding="utf-8")
    try:
        before_sha = sha(tasks_path)
        pointer_sha = sha(pointer)
        spec_sha = sha(spec_path)
        scope = {"schema_version": "1.0", "run_id": "installed-revision-successor",
            "feature_directory": feature, "request_reference": "installed-fixture-request",
            "request_kind": "full-feature", "requested_task_ids": ["T002"],
            "task_records": [{"task_id": "T002", "marker": "unchecked", "description": "Existing selected work",
                "description_sha256": hashlib.sha256(b"Existing selected work").hexdigest()}],
            "input_digests": {".specify/feature.json": pointer_sha, f"{feature}/spec.md": spec_sha,
                f"{feature}/tasks.md": before_sha}}
        scope["scope_sha256"] = digest(scope)
        progress_finding = {"id": "F020-LIFECYCLE-REENTRY-001", "task_id": "T002",
            "artifact_location": f"{feature}/implementation.py:1", "violated_requirement": "Correct the selected behavior.",
            "observed_deficiency": "The selected behavior is still incorrect.",
            "exact_correction": "Correct the selected behavior and retain its regression.",
            "evidence": [{"path": f"{feature}/implementation.py", "sha256": sha(source_path)}]}
        baseline_capture = controller_module.capture_implementation_baseline(consumer, {
            "feature_directory": feature, "selected_task_ids": ["T002"], "findings": [progress_finding]})
        if baseline_capture.get("state") != "ready":
            raise AssertionError(f"installed pre-effect baseline did not validate: {baseline_capture}")
        source_preimage_sha256 = sha(source_path)
        revision_previous_assessment = {"state": "continue", "next_step_id": "implement-tasks",
            "reason_code": "pre-source-frozen-findings",
            "evidence": [{"path": f"{feature}/tasks.md", "sha256": sha(tasks_path)},
                         {"path": f"{feature}/implementation.py", "sha256": sha(source_path)}],
            "remaining_ids": baseline_capture["remaining_ids"], "resolved_ids": []}
        controller_module.validate_outcome_envelope(revision_previous_assessment, consumer, {"implement-tasks"})
        retained_revision_assessment = digest({"scope_sha256": scope["scope_sha256"],
                                               "assessment": revision_previous_assessment})
        source_scope_payload = {"scope": scope, "trusted_request_reference": scope["request_reference"],
            "retained_scope_sha256": scope["scope_sha256"]}
        history = controller_module._empty_implementation_history(scope)
        history = _append_event(controller_module, consumer, source_scope_payload, history,
            "post-review-successor", "coder-session-start", session=1, attempts=0,
            execution_kind="first-source-execution")
        history = _append_event(controller_module, consumer, source_scope_payload, history,
            "post-review-successor", "source-attempt-start", session=1, attempts=1,
            execution_kind="first-source-execution")
        source_path.write_text("def result(): return 'after'\n", encoding="utf-8")
        source_effect = {"path": f"{feature}/implementation.py", "before_sha256": source_preimage_sha256,
            "after_sha256": sha(source_path)}
        history = _append_event(controller_module, consumer, source_scope_payload, history,
            "post-review-successor", "coder-session-outcome", session=1, attempts=1,
            execution_kind="first-source-execution", outcome="completed")
        current_evidence = [{"path": source_effect["path"], "sha256": source_effect["after_sha256"]}]
        task_revision_finding = {"id": "F020-R001", "task_id": "T002",
            "artifact_location": f"{feature}/implementation.py:1",
            "violated_requirement": "The selected feature retains a concrete implementation correction.",
            "observed_deficiency": "A follow-up implementation task is needed to finish the reviewed route.",
            "exact_correction": "Add the reviewed follow-up implementation task and preserve its selected identity.",
            "evidence": current_evidence}
        reviewer_review = {"reviewer": "FarmBoy Code Reviewer",
            "baseline_sha256": baseline_capture["baseline_sha256"],
            "findings": [{"id": progress_finding["id"], "task_id": "T002", "status": "resolved",
                "evidence": current_evidence,
                "resolution_summary": "The reviewed correction changes the captured source behavior."}],
            "new_findings": [task_revision_finding], "completed_task_ids": []}
        progress = controller_module.validate_implementation_progress(consumer, {
            "baseline": baseline_capture["baseline"],
            "baseline_sha256": baseline_capture["baseline_sha256"], "review": reviewer_review})
        if progress.get("state") != "ready" or progress.get("resolved_ids") != [f"finding:{progress_finding['id']}"]:
            raise AssertionError(f"post-review source correction lacks independent progress evidence: {progress}")
        after = before + "- [ ] T003 [US1] Correct F020-R001 in the implemented workflow\n"
        tasker_result = {"revision_state": "updated", "feature_directory": feature, "tasks_path": f"{feature}/tasks.md",
            "tasks_before_sha256": before_sha, "tasks_after_sha256": hashlib.sha256(after.encode()).hexdigest(),
            "finding_ids": ["F020-R001"],
            "task_mappings": [{"finding_id": "F020-R001", "task_ids": ["T003"], "owner": "FarmBoy Tasker"}],
            "reopened_task_ids": [], "added_task_ids": ["T003"], "preserved_completed_task_ids": ["T001"]}
        frozen_scope = {"findings": [{"id": task_revision_finding["id"],
            "exact_correction": task_revision_finding["exact_correction"]}],
            "eligible_task_owners": {}, "approved_specification_sha256": spec_sha,
            "permitted_added_task_owner": "FarmBoy Tasker", "tasker_owner": "FarmBoy Tasker"}
        revision_scope_sha = controller_module.task_revision_scope_digest(feature, f"{feature}/tasks.md", frozen_scope)
        semantic_review = {"reviewer": "main-controller", "state": "approved", "finding_ids": ["F020-R001"],
            "task_ids": ["T003"], "scope_sha256": revision_scope_sha,
            "rationale": "The Tasker addition is the exact eligible correction for the reviewed finding."}
        tasks_path.write_text(after, encoding="utf-8")
        revision = controller_module.validate_task_revision(consumer, {
            "feature_directory": feature, "tasks_path": f"{feature}/tasks.md", "tasks_before_text": before,
            "frozen_scope": frozen_scope, "semantic_review": semantic_review, "tasker_result": tasker_result,
            "requested_scope": scope, "retained_scope_sha256": scope["scope_sha256"],
            "trusted_request_reference": "installed-fixture-request", "task_tracking_successors": []})
        if revision.get("state") != "ready":
            raise AssertionError(f"installed Tasker revision was not validated: {revision}")
        successor = revision["task_tracking_successor"]
        scope_result = controller_module.validate_implementation_scope(consumer, {
            "scope": scope, "trusted_request_reference": "installed-fixture-request",
            "retained_scope_sha256": scope["scope_sha256"], "task_tracking_successors": [successor]})
        if scope_result.get("state") != "ready" or scope_result.get("tasker_derived_task_ids") != ["T003"]:
            raise AssertionError(f"installed Tasker successor did not preserve scope and expose only its derivative: {scope_result}")
        tasker_result_output = {"revision_state": tasker_result["revision_state"],
            "tasks_before_sha256": tasker_result["tasks_before_sha256"],
            "tasks_after_sha256": tasker_result["tasks_after_sha256"],
            "finding_ids": tasker_result["finding_ids"], "task_mappings": tasker_result["task_mappings"]}
        validator_result_output = {"state": revision["state"], "task_tracking_successor": successor}
        producer_record = {"tasker_step_id": "revise-task-plan", "tasker_result": tasker_result_output,
            "tasker_result_sha256": digest(tasker_result_output), "validator_step_id": "validate-task-revision",
            "validator_result": validator_result_output,
            "validator_result_sha256": digest(validator_result_output), "task_tracking_successor": successor}
        post_pass_inputs = {"scope": scope, "history": history, "task_tracking_successors": [successor],
            "eligibility": {"state": "ready", "tasker_derived_task_ids": ["T003"]},
            "producer_records": [producer_record], "ordered_operations": [
                "session-start", "source-attempt-start", "source-effect", "session-outcome",
                "independent-review", "Tasker-result",
                "Tasker-validation", "post-pass-capture"]}
        stale_successor = json.loads(json.dumps(successor))
        stale_successor["predecessor_event_sha256"] = "7" * 64
        stale_successor["sha256"] = digest({key: value for key, value in stale_successor.items() if key != "sha256"})
        stale_result = controller_module.validate_implementation_scope(consumer, {
            "scope": scope, "trusted_request_reference": scope["request_reference"],
            "retained_scope_sha256": scope["scope_sha256"], "task_tracking_successors": [stale_successor]})
        if stale_result.get("state") != "blocked":
            raise AssertionError(f"post-review callback accepted a stale Tasker predecessor: {stale_result}")
        forged_scope = json.loads(json.dumps(successor))
        forged_scope["frozen_scope"]["approved_specification_sha256"] = "9" * 64
        self_consistent_digest = controller_module.task_revision_scope_digest(
            feature, f"{feature}/tasks.md", forged_scope["frozen_scope"])
        forged_scope["semantic_review"]["scope_sha256"] = self_consistent_digest
        forged_scope["validation_result"]["scope_sha256"] = self_consistent_digest
        forged_scope["sha256"] = digest({key: value for key, value in forged_scope.items() if key != "sha256"})
        forged_spec = controller_module.validate_implementation_scope(consumer, {
            "scope": scope, "trusted_request_reference": "installed-fixture-request",
            "retained_scope_sha256": scope["scope_sha256"], "task_tracking_successors": [forged_scope]})
        if forged_spec.get("state") != "blocked":
            raise AssertionError(f"self-consistent Tasker revision detached from the approved specification was accepted: {forged_spec}")
        forged_semantic = json.loads(json.dumps(successor))
        forged_semantic["semantic_review"]["scope_sha256"] = "8" * 64
        forged_semantic["validation_result"]["scope_sha256"] = "8" * 64
        forged_semantic["sha256"] = digest({key: value for key, value in forged_semantic.items() if key != "sha256"})
        detached_semantic = controller_module.validate_implementation_scope(consumer, {
            "scope": scope, "trusted_request_reference": "installed-fixture-request",
            "retained_scope_sha256": scope["scope_sha256"], "task_tracking_successors": [forged_semantic]})
        if detached_semantic.get("state") != "blocked":
            raise AssertionError(f"self-consistent stored semantic/validation scope digests were trusted: {detached_semantic}")
        route_evidence_path = f"{feature}/validation/activation-route.json"
        readiness_evidence_path = f"{feature}/validation/activation-readiness.json"
        (consumer / route_evidence_path).parent.mkdir(parents=True, exist_ok=True)
        (consumer / route_evidence_path).write_text("{\"route\":\"declared source owner\"}\n", encoding="utf-8")
        (consumer / readiness_evidence_path).write_text("{\"state\":\"ready\"}\n", encoding="utf-8")
        t003_source = feature_dir / "tasker-successor.py"
        t003_source.write_text("def successor(): return 'before'\n", encoding="utf-8")
        activation_evidence = [{"path": route_evidence_path, "sha256": sha(consumer / route_evidence_path)}]
        readiness_evidence = [{"path": readiness_evidence_path, "sha256": sha(consumer / readiness_evidence_path)}]
        eligible_task_records = {"T002": ("unchecked", "Existing selected work"),
                                 "T003": ("unchecked", "[US1] Correct F020-R001 in the implemented workflow")}
        initial_task_evidence = [{"path": f"{feature}/tasks.md", "sha256": sha(tasks_path)}]
        revision_scope_payload = {"scope": scope, "trusted_request_reference": "installed-fixture-request",
            "retained_scope_sha256": scope["scope_sha256"], "task_tracking_successors": [successor]}
        initial_requirements = {task_id: ["behavior"] for task_id in eligible_task_records}
        initial_classifications = {}
        for task_id, (_, description) in eligible_task_records.items():
            initial_classifications[task_id] = {"task_id": task_id,
                "task_description_sha256": hashlib.sha256(description.encode()).hexdigest(),
                "completion_kind": "substantive-implementation", "requirement_ids": ["behavior"],
                "source_requirement_ids": ["behavior"], "scope_sha256": scope["scope_sha256"],
                "classification_evidence": initial_task_evidence}
        initial_assessment = {"assessment_id": "installed-revision-source-eligibility",
            "scope_sha256": scope["scope_sha256"], "predecessor_sha256": "a" * 64,
            "input_digests": {f"{feature}/spec.md": sha(spec_path), f"{feature}/tasks.md": sha(tasks_path)},
            "task_states": [{"task_id": task_id, "state": "eligible", "dependency_ids": [],
                "evidence": initial_task_evidence, "blocker": None, "resume_action": None, "proof_sha256": None}
                for task_id in eligible_task_records],
            "eligible_task_ids": list(eligible_task_records), "pending_task_ids": [], "global_blockers": [],
            "iteration": 1, "evidence": initial_task_evidence}
        initial_eligibility_payload = {**revision_scope_payload, "assessment": initial_assessment, "proofs": {},
            "proof_requirements": initial_requirements, "completion_classifications": initial_classifications,
            "source_requirement_ids": initial_requirements, "retained_predecessor_sha256": "a" * 64}
        initial_eligibility = controller_module.validate_implementation_eligibility(consumer, initial_eligibility_payload)
        if initial_eligibility.get("state") != "ready" or initial_eligibility["eligibility"].get("eligible_task_ids") != ["T002", "T003"]:
            raise AssertionError(f"installed revised scope did not pass current source eligibility: {initial_eligibility}")
        post_pass_inputs["eligibility"] = initial_eligibility
        capture_observation: dict[str, Any] = {}
        post_pass_state = _capture_post_pass_state(controller_module, consumer, scope=scope,
            trusted_request_reference="installed-fixture-request", retained_scope_sha256=scope["scope_sha256"],
            retained_history_sha256=post_pass_inputs["history"]["sha256"],
            incoming_successors=[], producer_records=post_pass_inputs["producer_records"],
            eligibility=post_pass_inputs["eligibility"], eligibility_request=initial_eligibility_payload,
            entry_history_sha256=post_pass_inputs["history"]["sha256"],
            capture_command=capture_command, capture_observation=capture_observation)
        try:
            invalid_project_command = [*capture_command[:-1], "/nonexistent-capture-target"]
            _capture_post_pass_state(controller_module, consumer, scope=scope,
                trusted_request_reference="installed-fixture-request", retained_scope_sha256=scope["scope_sha256"],
                retained_history_sha256=post_pass_inputs["history"]["sha256"], incoming_successors=[],
                producer_records=post_pass_inputs["producer_records"], eligibility=post_pass_inputs["eligibility"],
                eligibility_request=initial_eligibility_payload,
                entry_history_sha256=post_pass_inputs["history"]["sha256"],
                capture_command=invalid_project_command)
        except ValueError:
            invalid_project_state = "blocked"
        else:
            raise AssertionError("capture harness ignored a mutated production --project argument")
        try:
            _capture_post_pass_state(controller_module, consumer, scope=scope,
                trusted_request_reference="installed-fixture-request", retained_scope_sha256=scope["scope_sha256"],
                retained_history_sha256=post_pass_inputs["history"]["sha256"], incoming_successors=[],
                producer_records=post_pass_inputs["producer_records"], eligibility=post_pass_inputs["eligibility"],
                eligibility_request=initial_eligibility_payload, entry_history_sha256="f" * 64,
                capture_command=capture_command)
        except ValueError as error:
            if str(error) != "post-pass-entry-history-not-ancestor":
                raise AssertionError(f"capture accepted the wrong stale-history outcome: {error}") from error
            stale_entry_history_state = "blocked"
        else:
            raise AssertionError("capture accepted stale route-entry history")
        post_pass_state["ordered_operations"] = post_pass_inputs["ordered_operations"]
        revision_assessment = {"state": "continue", "next_step_id": "implement-tasks",
            "reason_code": "reviewed-task-revision-ready", "evidence": progress["evidence"],
            "remaining_ids": list(dict.fromkeys([*progress["remaining_ids"], "task:T002", "task:T003"])),
            "resolved_ids": progress["resolved_ids"]}
        captured_revision_route = controller_module.validate_scoped_implementation_progress(consumer, {
            "controller_loop_mode": "implementation_scope", "scope": post_pass_state["scope"],
            "trusted_request_reference": "installed-fixture-request",
            "retained_scope_sha256": post_pass_state["scope"]["scope_sha256"],
            "retained_history_sha256": post_pass_state["history"]["sha256"],
            "task_tracking_successors": post_pass_state["task_tracking_successors"],
            "assessment": revision_assessment,
            "eligible_task_ids": post_pass_state["eligibility"]["eligibility"]["eligible_task_ids"],
            "declared_node_ids": ["prepare-scoped-prerequisites", "implement-tasks"],
            "previous_assessment": revision_previous_assessment,
            "retained_previous_assessment_sha256": retained_revision_assessment,
            "progress": {"baseline": baseline_capture["baseline"],
                "baseline_sha256": baseline_capture["baseline_sha256"], "review": reviewer_review},
            "administrative_prerequisite_ids": []})
        if captured_revision_route.get("state") != "continue":
            raise AssertionError(f"the captured Tasker revision packet failed the installed final route: {captured_revision_route}")
        activation_packets: dict[str, dict[str, Any]] = {}
        for task_id, source in (("T002", source_path), ("T003", t003_source)):
            activation = {"activation_id": f"installed-revision-activation-{task_id}", "task_id": task_id,
                "scope_sha256": scope["scope_sha256"], "eligibility_sha256": initial_eligibility["eligibility_sha256"],
                "predecessor_baseline_sha256": baseline_capture["baseline_sha256"],
                "occurred_at": "2026-10-08T12:00:00Z", "requirements": ["behavior"],
                "source_preimages": [{"path": source.relative_to(consumer).as_posix(), "state": "present", "sha256": sha(source)}],
                "route_evidence": activation_evidence, "readiness_evidence": readiness_evidence, "iteration": 1}
            activation_result = controller_module.validate_implementation_activation(consumer, {
                **revision_scope_payload, "activation": activation,
                "eligibility_sha256": initial_eligibility["eligibility_sha256"],
                "predecessor_baseline_sha256": baseline_capture["baseline_sha256"],
                "task_id": task_id, "required_paths": [source.relative_to(consumer).as_posix()]})
            if activation_result.get("state") != "ready":
                raise AssertionError(f"installed task activation failed for {task_id}: {activation_result}")
            activation_packets[task_id] = activation
        task_evidence = [{"path": f"{feature}/tasks.md", "sha256": sha(tasks_path)}]
        derived_classification = {"task_id": "T003",
            "task_description_sha256": hashlib.sha256(b"[US1] Correct F020-R001 in the implemented workflow").hexdigest(),
            "completion_kind": "substantive-implementation", "requirement_ids": ["code"],
            "source_requirement_ids": ["code"], "scope_sha256": scope["scope_sha256"],
            "classification_evidence": task_evidence}
        eligibility = controller_module.validate_implementation_eligibility(consumer, {
            "scope": scope, "trusted_request_reference": "installed-fixture-request",
            "retained_scope_sha256": scope["scope_sha256"], "task_tracking_successors": [successor],
            "assessment": {"assessment_id": "installed-derived-eligibility", "scope_sha256": scope["scope_sha256"],
                "predecessor_sha256": "f" * 64,
                "input_digests": {f"{feature}/tasks.md": sha(tasks_path)},
                "task_states": [
                    {"task_id": "T002", "state": "pending", "dependency_ids": [], "evidence": task_evidence,
                     "blocker": "selected-work-pending", "resume_action": "resume-implementation", "proof_sha256": None},
                    {"task_id": "T003", "state": "eligible", "dependency_ids": [], "evidence": task_evidence,
                     "blocker": None, "resume_action": None, "proof_sha256": None}],
                "eligible_task_ids": ["T003"], "pending_task_ids": ["T002"], "global_blockers": [],
                "iteration": 1, "evidence": task_evidence}, "proofs": {},
            "proof_requirements": {"T003": ["code"]}, "completion_classifications": {"T003": derived_classification},
            "source_requirement_ids": {"T003": ["code"]}, "retained_predecessor_sha256": "f" * 64})
        if eligibility.get("state") != "ready" or eligibility["eligibility"].get("eligible_task_ids") != ["T003"]:
            raise AssertionError(f"installed eligibility rejected the authorized derived task: {eligibility}")
        checked_after = after.replace("- [ ] T003", "- [x] T003")
        tasker_evidence_path = f".specify/si-evidence/task-revision/tasker.json"
        reviewer_evidence_path = f".specify/si-evidence/task-revision/reviewer.json"
        tasker_evidence_file = consumer / tasker_evidence_path
        reviewer_evidence_file = consumer / reviewer_evidence_path
        tasker_evidence_file.parent.mkdir(parents=True, exist_ok=True)
        tasker_evidence_file.write_text(json.dumps({"kind": "tasker-marker-tracking", "task_ids": ["T003"]}) + "\n")
        reviewer_evidence_file.write_text(json.dumps({"kind": "independent-marker-review", "task_ids": ["T003"]}) + "\n")
        marker_event = {"predecessor_event_sha256": successor["sha256"], "scope_sha256": scope["scope_sha256"],
            "tasker_assignment": "FarmBoy Tasker", "tasks_before_text": after, "tasks_after_text": checked_after,
            "tasker_result": {"state": "ready", "tasks_before_sha256": hashlib.sha256(after.encode()).hexdigest(),
                "tasks_after_sha256": hashlib.sha256(checked_after.encode()).hexdigest(), "completed_task_ids": ["T003"],
                "evidence": [{"path": tasker_evidence_path, "sha256": sha(tasker_evidence_file)}]},
            "reviewer_result": {"reviewer": "FarmBoy Code Reviewer", "completed_task_ids": ["T003"],
                "evidence": [{"path": reviewer_evidence_path, "sha256": sha(reviewer_evidence_file)}]}}
        marker_event["sha256"] = digest(marker_event)
        tasks_path.write_text(checked_after, encoding="utf-8")
        tasker_chain = [successor, marker_event]
        tracked_scope = controller_module.validate_implementation_scope(consumer, {
            "scope": scope, "trusted_request_reference": "installed-fixture-request",
            "retained_scope_sha256": scope["scope_sha256"], "task_tracking_successors": tasker_chain})
        if tracked_scope.get("state") != "ready" or tracked_scope.get("tasker_tracked_task_ids") != ["T003"]:
            raise AssertionError(f"installed marker successor did not follow the revision chain: {tracked_scope}")
        source_path.write_text("def result(): return 'corrected'\n", encoding="utf-8")
        current_source_evidence = [{"path": f"{feature}/implementation.py", "sha256": sha(source_path)}]
        progress_review = {"reviewer": "FarmBoy Code Reviewer",
            "baseline_sha256": baseline_capture["baseline_sha256"],
            "findings": [{"id": progress_finding["id"], "task_id": "T002", "status": "resolved",
                "resolution_summary": "The original reproduction now passes against the corrected source.",
                "evidence": current_source_evidence}],
            "new_findings": [], "completed_task_ids": []}
        progress_payload = {"baseline": baseline_capture["baseline"],
            "baseline_sha256": baseline_capture["baseline_sha256"], "review": progress_review}
        progress = controller_module.validate_implementation_progress(consumer, progress_payload)
        if progress.get("state") != "ready" or progress.get("resolved_ids") != [f"finding:{progress_finding['id']}"]:
            raise AssertionError(f"installed source progress did not validate against its frozen finding: {progress}")
        history_payload = {"scope": scope, "trusted_request_reference": "installed-fixture-request",
            "retained_scope_sha256": scope["scope_sha256"], "task_tracking_successors": tasker_chain}
        current_assessment = {"state": "continue", "next_step_id": "implement-tasks",
            "reason_code": "recorded-defect-resolved", "evidence": progress["evidence"],
            "remaining_ids": progress["remaining_ids"], "resolved_ids": progress["resolved_ids"]}
        previous_assessment = revision_previous_assessment
        scoped_progress = controller_module.validate_scoped_implementation_progress(consumer, {
            "controller_loop_mode": "implementation_scope", **history_payload,
            "retained_history_sha256": history["sha256"], "assessment": current_assessment,
            "eligible_task_ids": ["T002"],
            "declared_node_ids": ["prepare-scoped-prerequisites", "implement-tasks"],
            "previous_assessment": previous_assessment,
            "retained_previous_assessment_sha256": retained_revision_assessment, "progress": progress_payload,
            "administrative_prerequisite_ids": []})
        if scoped_progress.get("state") != "continue":
            raise AssertionError(f"installed scoped progress did not re-enter after legitimate Tasker successors: {scoped_progress}")
        unsubstantiated = controller_module.validate_implementation_eligibility(consumer, {
            "scope": scope, "trusted_request_reference": "installed-fixture-request",
            "retained_scope_sha256": scope["scope_sha256"], "task_tracking_successors": tasker_chain,
            "assessment": {"assessment_id": "installed-unsubstantiated-completion", "scope_sha256": scope["scope_sha256"],
                "predecessor_sha256": "a" * 64, "input_digests": {f"{feature}/tasks.md": sha(tasks_path)},
                "task_states": [
                    {"task_id": "T002", "state": "pending", "dependency_ids": [], "evidence": task_evidence,
                     "blocker": "selected-work-pending", "resume_action": "resume-implementation", "proof_sha256": None},
                    {"task_id": "T003", "state": "completed-with-proof", "dependency_ids": [], "evidence": task_evidence,
                     "blocker": None, "resume_action": None, "proof_sha256": "b" * 64}],
                "eligible_task_ids": [], "pending_task_ids": ["T002"], "global_blockers": [], "iteration": 2,
                "evidence": task_evidence}, "proofs": {}, "proof_requirements": {},
            "completion_classifications": {}, "source_requirement_ids": {}, "retained_predecessor_sha256": "a" * 64})
        if unsubstantiated.get("state") != "blocked":
            raise AssertionError(f"installed Tasker checkbox was treated as completion proof: {unsubstantiated}")
        (consumer / f"{feature}/validation/completion-review.json").write_text(
            json.dumps({"reviewer": "FarmBoy Code Reviewer", "task_ids": ["T002", "T003"],
                        "finding_ids": [progress_finding["id"]]}, sort_keys=True) + "\n", encoding="utf-8")
        completion_review_evidence = [{"path": f"{feature}/validation/completion-review.json",
                                       "sha256": sha(consumer / f"{feature}/validation/completion-review.json")}]
        (consumer / f"{feature}/validation/tasker-final-tracking.json").write_text(
            json.dumps({"owner": "FarmBoy Tasker", "completed_task_ids": ["T002"]}, sort_keys=True) + "\n",
            encoding="utf-8")
        (consumer / f"{feature}/validation/reviewer-final-tracking.json").write_text(
            json.dumps({"reviewer": "FarmBoy Code Reviewer", "completed_task_ids": ["T002"]}, sort_keys=True) + "\n",
            encoding="utf-8")
        final_tasks = checked_after.replace("- [ ] T002", "- [x] T002")
        final_tasker_event = {"predecessor_event_sha256": marker_event["sha256"],
            "scope_sha256": scope["scope_sha256"], "tasker_assignment": "FarmBoy Tasker",
            "tasks_before_text": checked_after, "tasks_after_text": final_tasks,
            "tasker_result": {"state": "ready", "tasks_before_sha256": hashlib.sha256(checked_after.encode()).hexdigest(),
                "tasks_after_sha256": hashlib.sha256(final_tasks.encode()).hexdigest(), "completed_task_ids": ["T002"],
                "evidence": [{"path": f"{feature}/validation/tasker-final-tracking.json",
                              "sha256": sha(consumer / f"{feature}/validation/tasker-final-tracking.json")}]},
            "reviewer_result": {"reviewer": "FarmBoy Code Reviewer", "completed_task_ids": ["T002"],
                "evidence": [{"path": f"{feature}/validation/reviewer-final-tracking.json",
                              "sha256": sha(consumer / f"{feature}/validation/reviewer-final-tracking.json")}]}}
        final_tasker_event["sha256"] = digest(final_tasker_event)
        final_tasker_chain = [*tasker_chain, final_tasker_event]
        tasks_path.write_text(final_tasks, encoding="utf-8")
        t003_source.write_text("def successor(): return 'corrected'\n", encoding="utf-8")
        final_source_evidence = [{"path": f"{feature}/implementation.py", "sha256": sha(source_path)},
                                 {"path": f"{feature}/tasker-successor.py", "sha256": sha(t003_source)}]
        completion_review = {"reviewer": "FarmBoy Code Reviewer",
            "baseline_sha256": baseline_capture["baseline_sha256"],
            "findings": [{"id": progress_finding["id"], "task_id": "T002", "status": "resolved",
                "resolution_summary": "The original finding is fixed and its behavior regression passed.",
                "evidence": [{"path": f"{feature}/implementation.py", "sha256": sha(source_path)}]}],
            "new_findings": [], "completed_task_ids": ["T002"],
            "task_completion_evidence": [{"path": f"{feature}/implementation.py", "sha256": sha(source_path)}]}
        completion_progress_payload = {"baseline": baseline_capture["baseline"],
            "baseline_sha256": baseline_capture["baseline_sha256"], "review": completion_review}
        completion_progress = controller_module.validate_implementation_progress(consumer, completion_progress_payload)
        if (completion_progress.get("state") != "ready" or completion_progress.get("remaining_ids")
                or f"task:T002" not in completion_progress.get("resolved_ids", [])):
            raise AssertionError(f"installed whole-task progress did not validate: {completion_progress}")
        stale_prior_pass = controller_module.validate_scoped_implementation_progress(consumer, {
            "controller_loop_mode": "implementation_scope", "scope": post_pass_state["scope"],
            "trusted_request_reference": "installed-fixture-request",
            "retained_scope_sha256": post_pass_state["scope"]["scope_sha256"],
            "retained_history_sha256": post_pass_state["history"]["sha256"],
            "task_tracking_successors": post_pass_state["task_tracking_successors"],
            "assessment": revision_assessment,
            "eligible_task_ids": post_pass_state["eligibility"]["eligibility"]["eligible_task_ids"],
            "declared_node_ids": ["prepare-scoped-prerequisites", "implement-tasks"],
            "previous_assessment": revision_previous_assessment,
            "retained_previous_assessment_sha256": retained_revision_assessment,
            "progress": {"baseline": baseline_capture["baseline"],
                "baseline_sha256": baseline_capture["baseline_sha256"], "review": reviewer_review},
            "administrative_prerequisite_ids": []})
        if stale_prior_pass.get("state") != "blocked":
            raise AssertionError("a prior-pass capture was reused after later Tasker tracking changed current task bytes")
        final_task_evidence = [{"path": f"{feature}/tasks.md", "sha256": sha(tasks_path)}]
        final_descriptions = {"T002": "Existing selected work",
                              "T003": "[US1] Correct F020-R001 in the implemented workflow"}
        final_classifications = {task_id: {"task_id": task_id,
            "task_description_sha256": hashlib.sha256(description.encode()).hexdigest(),
            "completion_kind": "substantive-implementation", "requirement_ids": ["behavior"],
            "source_requirement_ids": ["behavior"], "scope_sha256": scope["scope_sha256"],
            "classification_evidence": final_task_evidence}
            for task_id, description in final_descriptions.items()}
        final_proofs = {}
        for task_id in final_descriptions:
            source_item = next(item for item in final_source_evidence
                               if (task_id == "T002") == item["path"].endswith("implementation.py"))
            final_proofs[task_id] = {"task_id": task_id,
                "task_description_sha256": hashlib.sha256(final_descriptions[task_id].encode()).hexdigest(),
                "completion_kind": "substantive-implementation", "scope_sha256": scope["scope_sha256"],
                "requirements": [{"requirement_id": "behavior", "satisfied": True, "evidence": [source_item]}],
                "proof_evidence": [source_item],
                "review_evidence": {"reviewer": "FarmBoy Code Reviewer", "verdict": "complete",
                    "reference": f"{feature}/validation/completion-review.json",
                    "sha256": sha(consumer / f"{feature}/validation/completion-review.json")},
                "activation_sha256": digest(activation_packets[task_id]),
                "source_delta_evidence": [source_item], "validation_evidence": completion_review_evidence}
        final_assessment = {"assessment_id": "installed-revision-final-completion",
            "scope_sha256": scope["scope_sha256"], "predecessor_sha256": "b" * 64,
            "input_digests": {".specify/feature.json": sha(pointer), f"{feature}/spec.md": sha(spec_path),
                              f"{feature}/tasks.md": sha(tasks_path)},
            "task_states": [{"task_id": task_id, "state": "completed-with-proof", "dependency_ids": [],
                "evidence": final_task_evidence, "blocker": None, "resume_action": None,
                "proof_sha256": digest(final_proofs[task_id])} for task_id in final_descriptions],
            "eligible_task_ids": [], "pending_task_ids": [], "global_blockers": [], "iteration": 2,
            "evidence": final_task_evidence}
        final_eligibility_payload = {"scope": scope, "trusted_request_reference": "installed-fixture-request",
            "retained_scope_sha256": scope["scope_sha256"], "task_tracking_successors": final_tasker_chain,
            "assessment": final_assessment, "proofs": final_proofs,
            "proof_requirements": {task_id: ["behavior"] for task_id in final_descriptions},
            "completion_classifications": final_classifications,
            "source_requirement_ids": {task_id: ["behavior"] for task_id in final_descriptions},
            "retained_predecessor_sha256": "b" * 64}
        final_eligibility = controller_module.validate_implementation_eligibility(consumer, final_eligibility_payload)
        if final_eligibility.get("state") != "ready" or final_eligibility["eligibility"].get("eligible_task_ids") or final_eligibility["eligibility"].get("pending_task_ids"):
            raise AssertionError(f"installed final current eligibility did not prove every requested/derived task: {final_eligibility}")
        final_assessment_envelope = {"state": "complete", "reason_code": "all-requested-work-substantiated",
            "evidence": completion_progress["evidence"], "remaining_ids": [],
            "resolved_ids": completion_progress["resolved_ids"]}
        completion_tasker_output = final_tasker_event["tasker_result"]
        completion_validator_output = {"state": "complete", "task_tracking_successor": final_tasker_event,
            "completion_progress": completion_progress, "eligibility_sha256": final_eligibility["eligibility_sha256"]}
        completion_producer = {"tasker_step_id": "track-reviewed-completion",
            "tasker_result": completion_tasker_output, "tasker_result_sha256": digest(completion_tasker_output),
            "validator_step_id": "validate-reviewed-completion-tracking",
            "validator_result": completion_validator_output,
            "validator_result_sha256": digest(completion_validator_output)}
        final_post_pass_state = _capture_post_pass_state(controller_module, consumer, scope=scope,
            trusted_request_reference="installed-fixture-request", retained_scope_sha256=scope["scope_sha256"],
            retained_history_sha256=history["sha256"], incoming_successors=tasker_chain,
            producer_records=[completion_producer], eligibility=final_eligibility,
            eligibility_request=final_eligibility_payload, completion=True,
            entry_history_sha256=history["sha256"], capture_command=capture_command)
        if final_post_pass_state["task_tracking_successors"] != final_tasker_chain:
            raise AssertionError("completion capture did not append the actual completion Tasker successor")
        completion_capture_negative_states: dict[str, str] = {}
        for invalid_producer, expected_reason in (
            ({**completion_producer, "tasker_step_id": "revise-task-plan",
              "validator_step_id": "validate-task-revision"}, "post-pass-producer-branch-invalid"),
            ({**completion_producer, "validator_result": {**completion_validator_output, "state": "blocked"}},
             "post-pass-validator-state-invalid"),
            ({**completion_producer, "validator_result": {key: value for key, value in completion_validator_output.items()
                if key != "task_tracking_successor"}}, "post-pass-successor-output-missing"),
        ):
            invalid_producer["validator_result_sha256"] = digest(invalid_producer["validator_result"])
            try:
                _capture_post_pass_state(controller_module, consumer, scope=scope,
                    trusted_request_reference="installed-fixture-request", retained_scope_sha256=scope["scope_sha256"],
                    retained_history_sha256=history["sha256"], incoming_successors=tasker_chain,
                    producer_records=[invalid_producer], eligibility=final_eligibility,
                    eligibility_request=final_eligibility_payload, completion=True,
                    entry_history_sha256=history["sha256"], capture_command=capture_command)
            except ValueError as error:
                if str(error) != expected_reason:
                    raise AssertionError(f"completion capture returned the wrong blocker: {error}") from error
                completion_capture_negative_states[expected_reason] = "blocked"
            else:
                raise AssertionError(f"completion capture accepted invalid producer state: {expected_reason}")
        stale_completion = json.loads(json.dumps(final_tasker_event))
        stale_completion["predecessor_event_sha256"] = "7" * 64
        stale_completion["sha256"] = digest({key: value for key, value in stale_completion.items() if key != "sha256"})
        stale_completion_producer = {**completion_producer,
            "validator_result": {**completion_validator_output, "task_tracking_successor": stale_completion}}
        stale_completion_producer["validator_result_sha256"] = digest(stale_completion_producer["validator_result"])
        try:
            _capture_post_pass_state(controller_module, consumer, scope=scope,
                trusted_request_reference="installed-fixture-request", retained_scope_sha256=scope["scope_sha256"],
                retained_history_sha256=history["sha256"], incoming_successors=tasker_chain,
                producer_records=[stale_completion_producer], eligibility=final_eligibility,
                eligibility_request=final_eligibility_payload, completion=True,
                entry_history_sha256=history["sha256"], capture_command=capture_command)
        except ValueError:
            completion_capture_negative_states["stale-successor"] = "blocked"
        else:
            raise AssertionError("completion capture accepted a stale Tasker successor")
        final_scoped_progress = controller_module.validate_scoped_implementation_progress(consumer, {
            "controller_loop_mode": "implementation_scope", "scope": scope,
            "trusted_request_reference": "installed-fixture-request",
            "retained_scope_sha256": final_post_pass_state["scope"]["scope_sha256"],
            "task_tracking_successors": final_post_pass_state["task_tracking_successors"],
            "retained_history_sha256": final_post_pass_state["history"]["sha256"],
            "assessment": final_assessment_envelope,
            "eligible_task_ids": final_post_pass_state["eligibility"]["eligibility"]["eligible_task_ids"],
            "declared_node_ids": ["prepare-scoped-prerequisites", "implement-tasks"],
            "previous_assessment": previous_assessment,
            "retained_previous_assessment_sha256": retained_revision_assessment, "progress": completion_progress_payload,
            "administrative_prerequisite_ids": [], "eligibility_request": final_eligibility_payload})
        if final_scoped_progress.get("state") != "complete":
            raise AssertionError(f"installed final scoped route did not complete with current whole-scope proof: {final_scoped_progress}")
        replayed = controller_module.validate_implementation_scope(consumer, {
            "scope": scope, "trusted_request_reference": "installed-fixture-request",
            "retained_scope_sha256": scope["scope_sha256"], "task_tracking_successors": [*final_tasker_chain, final_tasker_event]})
        stale_spec = spec_path.read_text(encoding="utf-8")
        spec_path.write_text(stale_spec + "Changed after the Tasker review.\n", encoding="utf-8")
        stale = controller_module.validate_implementation_scope(consumer, {
            "scope": scope, "trusted_request_reference": "installed-fixture-request",
            "retained_scope_sha256": scope["scope_sha256"], "task_tracking_successors": final_tasker_chain})
        spec_path.write_text(stale_spec, encoding="utf-8")
        pointer.write_text(json.dumps({"feature_directory": "specs/997-stale-pointer"}) + "\n", encoding="utf-8")
        stale_pointer = controller_module.validate_implementation_scope(consumer, {
            "scope": scope, "trusted_request_reference": "installed-fixture-request",
            "retained_scope_sha256": scope["scope_sha256"], "task_tracking_successors": final_tasker_chain})
        pointer.write_text(json.dumps({"feature_directory": feature}) + "\n", encoding="utf-8")
        if (replayed.get("state") != "blocked" or stale.get("state") != "blocked"
                or stale_pointer.get("state") != "blocked"):
            raise AssertionError(f"installed successor replay/stale-input guard failed: {replayed}, {stale}, {stale_pointer}")
        return {"scope_state": scope_result["state"], "eligible_derived_task_ids": eligibility["eligibility"]["eligible_task_ids"],
            "scope_sha256_preserved": scope["scope_sha256"], "original_task_sha256_preserved": before_sha,
            "revision_successor_sha256": successor["sha256"], "replay_state": replayed["state"],
            "stale_spec_state": stale["state"], "stale_pointer_state": stale_pointer["state"],
            "forged_approved_spec_state": forged_spec["state"],
            "forged_semantic_scope_state": detached_semantic["state"],
            "post_pass_state": post_pass_state,
            "capture_project_argument_mutation_state": invalid_project_state,
            "capture_dispatch": capture_observation,
            "stale_entry_history_state": stale_entry_history_state,
            "captured_revision_route_state": captured_revision_route["state"],
            "stale_prior_pass_after_later_tracking_state": stale_prior_pass["state"],
            "captured_revision_history_sha256": post_pass_state["history"]["sha256"],
            "captured_revision_producer_step_ids": [
                post_pass_state["producer_records"][0]["tasker_step_id"],
                post_pass_state["producer_records"][0]["validator_step_id"]],
            "baseline": baseline_capture["baseline"],
            "baseline_sha256": baseline_capture["baseline_sha256"],
            "previous_assessment": revision_previous_assessment,
            "retained_previous_assessment_sha256": retained_revision_assessment,
            "review": reviewer_review,
            "progress": progress,
            "post_pass_ordered_operations": post_pass_state["ordered_operations"],
            "stale_post_review_successor_state": stale_result["state"],
            "post_review_source_effect": source_effect,
            "post_review_progress_state": progress["state"],
            "scoped_progress_after_tasker_successors": scoped_progress["state"],
            "initial_eligibility_state": initial_eligibility["state"],
            "activation_task_ids": sorted(activation_packets),
            "final_eligibility_state": final_eligibility["state"],
            "final_scoped_progress_state": final_scoped_progress["state"],
            "final_post_pass_completion_validator_state": final_post_pass_state["completion_validator_state"],
            "final_post_pass_successor_count": len(final_post_pass_state["task_tracking_successors"]),
            "completion_capture_negative_states": completion_capture_negative_states,
            "final_tasker_tracked_ids": ["T002", "T003"],
            "tracked_task_ids": tracked_scope["tasker_tracked_task_ids"],
            "unsubstantiated_completion_state": unsubstantiated["state"],
            "result": "installed-tasker-revision-successor-passed"}
    finally:
        pointer.write_bytes(prior_pointer)


class _SubprocessDispatchObserver:
    """Record child-process dispatches across one complete connected trace."""

    def __init__(self) -> None:
        self.commands: list[list[str]] = []
        self._run_depth = 0
        self._patches: list[Any] = []
        self._real_run: Any = None
        self._real_popen: Any = None

    @staticmethod
    def _command(command: Any) -> list[str]:
        if isinstance(command, (list, tuple)):
            return [str(part) for part in command]
        return [str(command)]

    def _record(self, command: Any) -> None:
        self.commands.append(self._command(command))

    def __enter__(self) -> _SubprocessDispatchObserver:
        self._real_run = subprocess.run
        self._real_popen = subprocess.Popen

        def observe_run(command: Any, *args: Any, **kwargs: Any) -> Any:
            self._record(command)
            self._run_depth += 1
            try:
                return self._real_run(command, *args, **kwargs)
            finally:
                self._run_depth -= 1

        def observe_popen(command: Any, *args: Any, **kwargs: Any) -> Any:
            # subprocess.run delegates to Popen; count that dispatch once at
            # the public run boundary while still observing direct Popen use.
            if self._run_depth == 0:
                self._record(command)
            return self._real_popen(command, *args, **kwargs)

        self._patches = [patch.object(subprocess, "run", side_effect=observe_run),
                         patch.object(subprocess, "Popen", side_effect=observe_popen)]
        for active_patch in self._patches:
            active_patch.start()
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        for active_patch in reversed(self._patches):
            active_patch.stop()
        self._patches = []


def _exercise_connected_positive_traces(controller_module: Any, consumer: Path, fixture_path: Path,
                                        capture_command: list[str]) -> list[dict[str, Any]]:
    """Run each connected positive control through installed production helpers."""
    def authority_artifacts() -> dict[str, str]:
        result: dict[str, str] = {}
        for path in consumer.rglob("*"):
            relative = path.relative_to(consumer).as_posix()
            parts = {part.lower() for part in path.relative_to(consumer).parts}
            name = path.name.lower()
            if (".git" in parts or "phase-lifecycle" in parts or "acceptance" in name
                    or "roadmap" in name):
                if path.is_file() and not path.is_symlink():
                    result[relative] = sha(path)
        return result

    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    traces = fixture.get("connected_positive_traces")
    if not isinstance(traces, list) or len(traces) != 2:
        raise AssertionError("connected positive trace fixture must contain exactly two scenarios")
    pointer = consumer / ".specify/feature.json"
    pointer.parent.mkdir(parents=True, exist_ok=True)
    prior_pointer = pointer.read_bytes() if pointer.exists() else None
    roadmap_path = consumer / ".specify/memory/roadmap.md"
    prior_roadmap_sha256 = sha(roadmap_path) if roadmap_path.is_file() else None
    observed: dict[str, dict[str, Any]] = {}
    dispatch_observer = _SubprocessDispatchObserver()
    try:
        dispatch_observer.__enter__()
        for trace in traces:
            dispatch_observer.commands.clear()
            trace_id = trace["id"]
            feature = f"specs/connected-{trace_id.lower()}"
            feature_root = consumer / feature
            feature_root.mkdir(parents=True, exist_ok=False)
            observed_sequence: list[str] = []
            pointer.write_text(json.dumps({"feature_directory": feature}, sort_keys=True) + "\n", encoding="utf-8")
            spec = feature_root / "spec.md"
            spec.write_text(f"# {trace_id}\n", encoding="utf-8")
            tasks = feature_root / "tasks.md"
            before_tasks = "- [ ] T001 Reviewed source correction\n- [ ] T002 Pending follow-up\n"
            tasks.write_text(before_tasks, encoding="utf-8")
            source_relative = f"{feature}/implementation.py"
            source = consumer / source_relative
            source.write_text("result = 'before'\n", encoding="utf-8")
            route_relative = f"{feature}/validation/route.json"
            readiness_relative = f"{feature}/validation/readiness.json"
            for relative, content in ((route_relative, {"route": "selected-source"}),
                                     (readiness_relative, {"state": "ready"})):
                destination = consumer / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(json.dumps(content, sort_keys=True) + "\n", encoding="utf-8")
            record_text = "Reviewed source correction"
            scope = {"schema_version": "1.0", "run_id": f"connected-{trace_id}",
                "feature_directory": feature, "request_reference": f"fixture-request-{trace_id}",
                "request_kind": "full-feature", "requested_task_ids": ["T001", "T002"],
                "task_records": [
                    {"task_id": "T001", "marker": "unchecked", "description": record_text,
                     "description_sha256": hashlib.sha256(record_text.encode()).hexdigest()},
                    {"task_id": "T002", "marker": "unchecked", "description": "Pending follow-up",
                     "description_sha256": hashlib.sha256(b"Pending follow-up").hexdigest()}],
                "input_digests": {".specify/feature.json": sha(pointer), f"{feature}/spec.md": sha(spec),
                                  f"{feature}/tasks.md": sha(tasks)}}
            scope["scope_sha256"] = digest(scope)
            binding = {"scope": scope, "trusted_request_reference": scope["request_reference"],
                       "retained_scope_sha256": scope["scope_sha256"]}
            scope_check = controller_module.validate_implementation_scope(consumer, binding)
            if scope_check.get("state") != "ready":
                raise AssertionError(f"{trace_id}: production scope validation failed: {scope_check}")

            evidence_relative = f"{feature}/validation/assessment.json"
            evidence_file = consumer / evidence_relative
            evidence_file.write_text(json.dumps({"scenario_id": trace_id}, sort_keys=True) + "\n", encoding="utf-8")
            evidence = [{"path": evidence_relative, "sha256": sha(evidence_file)}]
            predecessor = "a" * 64
            input_digests = {".specify/feature.json": sha(pointer), f"{feature}/spec.md": sha(spec),
                             f"{feature}/tasks.md": sha(tasks)}
            assessment = {"assessment_id": f"assessment-{trace_id}", "scope_sha256": scope["scope_sha256"],
                "predecessor_sha256": predecessor, "input_digests": input_digests,
                "task_states": [
                    {"task_id": "T001", "state": "eligible", "dependency_ids": [], "evidence": evidence,
                     "blocker": None, "resume_action": None, "proof_sha256": None},
                    {"task_id": "T002", "state": "pending", "dependency_ids": ["T001"], "evidence": evidence,
                     "blocker": "fixture-follow-up-pending", "resume_action": "resume-follow-up", "proof_sha256": None}],
                "eligible_task_ids": ["T001"], "pending_task_ids": ["T002"], "global_blockers": [],
                "iteration": 1, "evidence": evidence}
            classification = {"task_id": "T001", "task_description_sha256": scope["task_records"][0]["description_sha256"],
                "completion_kind": "substantive-implementation", "requirement_ids": ["FR-007"],
                "source_requirement_ids": ["FR-007"], "scope_sha256": scope["scope_sha256"],
                "classification_evidence": evidence}
            eligibility_request = {**binding, "assessment": assessment, "proofs": {},
                "proof_requirements": {"T001": ["FR-007"]}, "completion_classifications": {"T001": classification},
                "source_requirement_ids": {"T001": ["FR-007"]},
                "retained_predecessor_sha256": predecessor}
            eligibility = controller_module.validate_implementation_eligibility(consumer, eligibility_request)
            if eligibility.get("state") != "ready" or eligibility["eligibility"].get("eligible_task_ids") != ["T001"]:
                raise AssertionError(f"{trace_id}: initial production eligibility failed: {eligibility}")

            previous_assessment = {"state": "continue", "next_step_id": "implement-tasks",
                "reason_code": "connected-positive-control", "evidence": evidence,
                "remaining_ids": ["task:T001", "task:T002"], "resolved_ids": []}
            retained_assessment_sha256 = digest(previous_assessment)
            controller_module.validate_outcome_envelope(previous_assessment, consumer, {"implement-tasks"})
            retained_previous = digest({"scope_sha256": scope["scope_sha256"], "assessment": previous_assessment})
            history = controller_module._empty_implementation_history(scope)
            entry_history = json.loads(json.dumps(history))
            entry_history_sha256 = entry_history["sha256"]
            entry_history_bytes_sha256 = hashlib.sha256(
                json.dumps(entry_history, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
            ).hexdigest()
            initial_route = controller_module.route_scoped_implementation(consumer, {
                **binding, "retained_history_sha256": history["sha256"],
                "assessment": previous_assessment, "eligible_task_ids": ["T001"],
                "declared_node_ids": ["prepare-scoped-prerequisites", "implement-tasks"]})
            if initial_route.get("state") != "continue":
                raise AssertionError(f"{trace_id}: production route did not continue: {initial_route}")
            switch = {"id": f"route-{trace_id}", "type": "switch",
                "expression": "{{ steps.assessment.output.next_step_id }}",
                "cases": {"implement-tasks": [{"id": "implement-tasks", "type": "command",
                    "command": "speckit.implement"}], "prepare-scoped-prerequisites": []},
                "default": [{"id": "blocked-route", "type": "command", "command": "blocked"}]}
            rendered_switch, selected_steps = controller_module.render_selected_switch(
                switch, {}, {"assessment": initial_route})
            selected_ids = [step["id"] for step in selected_steps]
            prevented_ids = [step["id"] for branch in [*switch["cases"].values(), switch["default"]]
                             for step in branch if step["id"] not in selected_ids]
            if (initial_route.get("next_step_id") != "implement-tasks"
                    or selected_ids != [initial_route.get("next_step_id")]
                    or rendered_switch.get("expression") != initial_route.get("next_step_id")):
                if "implement-tasks" not in selected_ids:
                    raise AssertionError(f"{trace_id}: source effects were prevented for the production-selected route: "
                                         f"{selected_ids}; no source effect was started")
                raise AssertionError(f"{trace_id}: production switch selected an unexpected route: "
                                     f"{rendered_switch}, {selected_steps}")

            baseline_finding = {"id": f"F023-{trace_id}-SOURCE", "task_id": "T001",
                "artifact_location": f"{feature}/implementation.py:1", "violated_requirement": "The selected behavior works.",
                "observed_deficiency": "The disposable implementation still has its pre-correction value.",
                "exact_correction": "Correct the selected source and retain reviewed evidence.",
                "evidence": [{"path": source_relative, "sha256": sha(source)}]}
            baseline = controller_module.capture_implementation_baseline(consumer, {
                "feature_directory": feature, "selected_task_ids": ["T001"], "findings": [baseline_finding]})
            if baseline.get("state") != "ready":
                raise AssertionError(f"{trace_id}: frozen source baseline failed: {baseline}")
            if trace["sequence"][0] == "retained-source-preimage":
                observed_sequence.append("retained-source-preimage")
            activation = {"activation_id": f"activation-{trace_id}", "task_id": "T001",
                "scope_sha256": scope["scope_sha256"], "eligibility_sha256": eligibility["eligibility_sha256"],
                "predecessor_baseline_sha256": baseline["baseline_sha256"],
                "occurred_at": "2026-10-13T20:00:00Z", "requirements": ["FR-007"],
                "source_preimages": [{"path": source_relative, "state": "present", "sha256": sha(source)}],
                "route_evidence": [{"path": route_relative, "sha256": sha(consumer / route_relative)}],
                "readiness_evidence": [{"path": readiness_relative, "sha256": sha(consumer / readiness_relative)}],
                "iteration": 1}
            activation_result = controller_module.validate_implementation_activation(consumer, {
                **binding, "activation": activation, "eligibility_sha256": eligibility["eligibility_sha256"],
                "predecessor_baseline_sha256": baseline["baseline_sha256"], "task_id": "T001",
                "required_paths": [source_relative]})
            if activation_result.get("state") != "ready":
                raise AssertionError(f"{trace_id}: production task activation failed: {activation_result}")
            observed_sequence.append("eligible-source-dispatch")
            authority_artifacts_before = authority_artifacts()
            activation_file = feature_root / "validation/activation.json"
            activation_file.write_text(json.dumps(activation, sort_keys=True) + "\n", encoding="utf-8")
            history = _record_sessions(controller_module, consumer, binding, history, trace_id, 1, 1,
                                       outcomes=["completed"])
            marker_trace = trace_id == "F023-POSITIVE-TASK-RESOLUTION-MARKER-ONLY"
            if not marker_trace:
                pre_effect_review = feature_root / "validation/pre-effect-review.json"
                pre_effect_review.write_text(json.dumps({"scenario_id": trace_id,
                    "reviewer_kind": "deterministic-fixture", "source_preimage_sha256": sha(source),
                    "reviewed_action": "apply-the-selected-source-correction"}, sort_keys=True) + "\n", encoding="utf-8")
                observed_sequence.append("independent-review")
            source.write_text("result = 'corrected'\n", encoding="utf-8")
            after_source = sha(source)
            if after_source == baseline_finding["evidence"][0]["sha256"]:
                raise AssertionError(f"{trace_id}: source effect did not change its retained preimage")

            review_relative = f"{feature}/validation/deterministic-review.json"
            review_file = consumer / review_relative
            review_file.write_text(json.dumps({"scenario_id": trace_id, "reviewer_kind": "deterministic-fixture",
                "verdict": "complete", "task_id": "T001"}, sort_keys=True) + "\n", encoding="utf-8")
            review_evidence = [{"path": review_relative, "sha256": sha(review_file)}]
            current_source = [{"path": source_relative, "sha256": after_source}]
            progress_review = {"reviewer": "FarmBoy Code Reviewer", "baseline_sha256": baseline["baseline_sha256"],
                "findings": [{"id": baseline_finding["id"], "task_id": "T001", "status": "resolved",
                    "resolution_summary": "The selected disposable behavior was corrected.",
                    "evidence": current_source + review_evidence}], "new_findings": [],
                "completed_task_ids": ["T001"], "task_completion_evidence": current_source + review_evidence}
            progress_request = {"baseline": baseline["baseline"], "baseline_sha256": baseline["baseline_sha256"],
                                "review": progress_review}
            progress = controller_module.validate_implementation_progress(consumer, progress_request)
            if progress.get("state") != "ready" or "task:T001" not in progress.get("resolved_ids", []):
                raise AssertionError(f"{trace_id}: production progress validation failed: {progress}")
            if marker_trace:
                observed_sequence.append("independent-review")
                observed_sequence.append("task-resolution")
            else:
                observed_sequence.append("reviewed-source-correction")

            task_tracking_successors: list[dict[str, Any]] = []
            producer_records: list[dict[str, Any]] = []
            if marker_trace:
                after_tasks = before_tasks.replace("- [ ] T001", "- [x] T001")
                tasker_relative = f"{feature}/validation/tasker.json"
                reviewer_relative = f"{feature}/validation/tracking-review.json"
                for relative, content in ((tasker_relative, {"scenario_id": trace_id, "completed_task_ids": ["T001"]}),
                                          (reviewer_relative, {"scenario_id": trace_id, "completed_task_ids": ["T001"]})):
                    target = consumer / relative
                    target.write_text(json.dumps(content, sort_keys=True) + "\n", encoding="utf-8")
                successor = {"predecessor_event_sha256": "0" * 64, "scope_sha256": scope["scope_sha256"],
                    "tasker_assignment": "FarmBoy Tasker", "tasks_before_text": before_tasks,
                    "tasks_after_text": after_tasks,
                    "tasker_result": {"state": "ready", "tasks_before_sha256": hashlib.sha256(before_tasks.encode()).hexdigest(),
                        "tasks_after_sha256": hashlib.sha256(after_tasks.encode()).hexdigest(),
                        "completed_task_ids": ["T001"], "evidence": [{"path": tasker_relative,
                            "sha256": sha(consumer / tasker_relative)}]},
                    "reviewer_result": {"reviewer": "FarmBoy Code Reviewer", "completed_task_ids": ["T001"],
                        "evidence": [{"path": reviewer_relative, "sha256": sha(consumer / reviewer_relative)}]}}
                successor["sha256"] = digest(successor)
                tasks.write_text(after_tasks, encoding="utf-8")
                tracked = controller_module.validate_implementation_scope(consumer, {
                    **binding, "task_tracking_successors": [successor]})
                if tracked.get("state") != "ready" or tracked.get("tasker_tracked_task_ids") != ["T001"]:
                    raise AssertionError(f"{trace_id}: production marker tracking failed: {tracked}")
                task_tracking_successors = [successor]
                observed_sequence.append("marker-only-tracking")

            current_task_evidence = [{"path": f"{feature}/tasks.md", "sha256": sha(tasks)}]
            final_proof = {"task_id": "T001", "task_description_sha256": scope["task_records"][0]["description_sha256"],
                "completion_kind": "substantive-implementation", "scope_sha256": scope["scope_sha256"],
                "requirements": [{"requirement_id": "FR-007", "satisfied": True, "evidence": current_source}],
                "proof_evidence": current_source, "review_evidence": {"reviewer": "FarmBoy Code Reviewer",
                    "verdict": "complete", "reference": review_relative, "sha256": sha(review_file)},
                "activation_sha256": digest(activation), "source_delta_evidence": current_source,
                "validation_evidence": review_evidence}
            final_assessment = {"assessment_id": f"current-{trace_id}", "scope_sha256": scope["scope_sha256"],
                "predecessor_sha256": predecessor, "input_digests": {".specify/feature.json": sha(pointer),
                    f"{feature}/spec.md": sha(spec), f"{feature}/tasks.md": sha(tasks)},
                "task_states": [
                    {"task_id": "T001", "state": "completed-with-proof", "dependency_ids": [],
                     "evidence": current_task_evidence, "blocker": None, "resume_action": None,
                     "proof_sha256": digest(final_proof)},
                    {"task_id": "T002", "state": "eligible", "dependency_ids": ["T001"],
                     "evidence": current_task_evidence, "blocker": None,
                     "resume_action": None, "proof_sha256": None}],
                "eligible_task_ids": ["T002"], "pending_task_ids": [], "global_blockers": [],
                "iteration": 2, "evidence": current_task_evidence}
            final_eligibility_request = {**binding, "task_tracking_successors": task_tracking_successors,
                "assessment": final_assessment, "proofs": {"T001": final_proof},
                "proof_requirements": {"T001": ["FR-007"], "T002": ["FR-008"]}, "completion_classifications": {
                    "T001": {**classification, "classification_evidence": current_task_evidence},
                    "T002": {"task_id": "T002", "task_description_sha256": scope["task_records"][1]["description_sha256"],
                        "completion_kind": "substantive-implementation", "requirement_ids": ["FR-008"],
                        "source_requirement_ids": ["FR-008"], "scope_sha256": scope["scope_sha256"],
                        "classification_evidence": current_task_evidence}},
                "source_requirement_ids": {"T001": ["FR-007"], "T002": ["FR-008"]},
                "retained_predecessor_sha256": predecessor}
            final_eligibility = controller_module.validate_implementation_eligibility(consumer, final_eligibility_request)
            if final_eligibility.get("state") != "ready":
                raise AssertionError(f"{trace_id}: current proof was not rechecked: {final_eligibility}")
            if task_tracking_successors:
                producer_validator = {"state": "ready", "task_tracking_successor": task_tracking_successors[0],
                    "eligibility_sha256": final_eligibility["eligibility_sha256"]}
                producer_records = [{"tasker_step_id": "track-reviewed-task-outcomes",
                    "validator_step_id": "validate-reviewed-task-tracking",
                    "tasker_result": task_tracking_successors[0]["tasker_result"], "validator_result": producer_validator}]
            child_observer_dir = feature_root / "validation/python-observer"
            child_observer_dir.mkdir(parents=True, exist_ok=True)
            (child_observer_dir / "sitecustomize.py").write_text(
                "import json, os, sys\n"
                "_audit_path = os.environ.get('FARMBOY_SUBPROCESS_AUDIT_PATH')\n"
                "def _record_process_dispatch(event, arguments):\n"
                "    if event not in {'subprocess.Popen', 'os.system', 'os.posix_spawn'} or not _audit_path:\n"
                "        return\n"
                "    command = arguments[1] if event == 'subprocess.Popen' and len(arguments) > 1 else arguments[0]\n"
                "    command = [str(part) for part in command] if isinstance(command, (list, tuple)) else [str(command)]\n"
                "    with open(_audit_path, 'a', encoding='utf-8') as audit_file:\n"
                "        audit_file.write(json.dumps({'event': event, 'command': command}) + '\\n')\n"
                "sys.addaudithook(_record_process_dispatch)\n"
                "if os.environ.get('FARMBOY_TEST_INJECT_CHILD_PROCESS') == '1':\n"
                "    import subprocess\n"
                "    subprocess.run(['true'], check=True)\n",
                encoding="utf-8")
            child_audit_path = child_observer_dir / "child-process-dispatches.jsonl"
            child_audit_path.write_text("", encoding="utf-8")
            capture_environment = {"PYTHONPATH": os.pathsep.join(filter(None, (
                str(child_observer_dir), os.environ.get("PYTHONPATH", "")))),
                "FARMBOY_SUBPROCESS_AUDIT_PATH": str(child_audit_path)}
            post_pass = _capture_post_pass_state(controller_module, consumer, scope=scope,
                trusted_request_reference=scope["request_reference"], retained_scope_sha256=scope["scope_sha256"],
                retained_history_sha256=history["sha256"], incoming_successors=[], producer_records=producer_records,
                eligibility=final_eligibility, eligibility_request=final_eligibility_request,
                entry_history_sha256=entry_history_sha256, capture_command=capture_command,
                capture_observation=(capture_observation := {}), capture_environment=capture_environment)
            if post_pass["task_tracking_successors"] != task_tracking_successors:
                raise AssertionError(f"{trace_id}: production capture omitted the actual marker event")
            observed_sequence.append("post-pass-capture")
            current_assessment = {"state": "continue", "next_step_id": "implement-tasks",
                "reason_code": "connected-positive-control", "evidence": progress["evidence"],
                "remaining_ids": ["task:T002"], "resolved_ids": progress["resolved_ids"]}
            scoped_request = {
                "controller_loop_mode": "implementation_scope", "scope": post_pass["scope"],
                "trusted_request_reference": scope["request_reference"],
                "retained_scope_sha256": post_pass["scope"]["scope_sha256"],
                "retained_history_sha256": post_pass["history"]["sha256"],
                "task_tracking_successors": post_pass["task_tracking_successors"],
                "assessment": current_assessment, "eligible_task_ids": ["T002"],
                "declared_node_ids": ["prepare-scoped-prerequisites", "implement-tasks"],
                "previous_assessment": previous_assessment,
                "retained_previous_assessment_sha256": retained_previous,
                "progress": progress_request, "administrative_prerequisite_ids": []}
            scoped = controller_module.validate_scoped_implementation_progress(consumer, scoped_request)
            if scoped.get("state") != "continue":
                raise AssertionError(f"{trace_id}: guarded production re-entry failed: {scoped}")
            observed_sequence.append("guarded-reentry")
            if observed_sequence != trace["sequence"]:
                raise AssertionError(f"{trace_id}: production operation order differs from fixture: {observed_sequence}")
            negative_dispatch_before = list(dispatch_observer.commands)
            negative_authority_before = authority_artifacts()
            negative_traces = _exercise_connected_negative_traces(
                controller_module, consumer, trace_id, scoped_request, post_pass["history"], progress_request,
                fixture["feature_023"]["scenarios"])
            if dispatch_observer.commands != negative_dispatch_before:
                raise AssertionError(f"{trace_id}: negative guard produced a later subprocess dispatch")
            negative_authority_after = authority_artifacts()
            if negative_authority_after != negative_authority_before:
                raise AssertionError(f"{trace_id}: negative guard changed an authority artifact")
            for negative_trace in negative_traces:
                negative_trace["prohibited_effect_counts"] = {
                    "workflow_or_phase_dispatch": 0, "git_integration": 0,
                    "real_roadmap_verification": 0, "feature_or_consumer_acceptance": 0}
            command_observations = list(dispatch_observer.commands)
            expected_capture_command = ["python3", ".specify/farmboy/scripts/python/controller.py",
                                        "post-pass-capture", "--project", "$PWD"]
            expected_observed_capture_command = [*expected_capture_command[:-1], str(consumer.resolve())]
            portable_dispatches = [
                [*command[:-1], "$CONSUMER_ROOT"]
                if command == expected_observed_capture_command else command
                for command in command_observations]
            authority_artifacts_after = authority_artifacts()
            changed_authority_artifacts = sorted(
                path for path in authority_artifacts_before.keys() | authority_artifacts_after.keys()
                if authority_artifacts_before.get(path) != authority_artifacts_after.get(path))
            roadmap_verification_records = [path for path in changed_authority_artifacts
                                            if "roadmap" in path.lower() or "phase-lifecycle" in path.lower()]
            acceptance_records = [path for path in changed_authority_artifacts if "acceptance" in path.lower()]
            git_artifacts = [path for path in changed_authority_artifacts
                             if ".git/" in path or path.startswith(".git")]
            child_process_dispatches = capture_observation.get("child_process_dispatches", [])
            workflow_or_phase_commands = [command for command in command_observations
                                          if command != expected_observed_capture_command] + child_process_dispatches
            git_commands = [command for command in command_observations if command and command[0] == "git"]
            git_commands.extend(record for record in child_process_dispatches
                                if record.get("command", [None])[0] == "git")
            details = {"id": trace_id, "valid_control_id": trace["valid_control_id"],
                "requirements": trace["requirements"], "execution_mode": trace["execution_mode"],
                "sequence": list(trace["sequence"]), "observed_sequence": observed_sequence,
                "scope_sha256": scope["scope_sha256"], "scope_sha256_preserved":
                    final_eligibility.get("scope_sha256") == scope["scope_sha256"],
                "assessment_sha256": retained_assessment_sha256,
                "assessment_sha256_preserved": digest(previous_assessment) == retained_assessment_sha256,
                "source_preimage_sha256": baseline_finding["evidence"][0]["sha256"],
                "source_after_sha256": after_source,
                "baseline_sha256": baseline["baseline_sha256"],
                "current_evidence": final_eligibility.get("evidence", []),
                "entry_history_sha256": entry_history_sha256,
                "execution_history_sha256": post_pass["history"]["sha256"],
                "source_preimage_sha256_preserved": baseline["baseline"]["findings"][0]["evidence"][0]["sha256"]
                    == baseline_finding["evidence"][0]["sha256"],
                "current_review_evidence_rechecked": final_eligibility.get("state") == "ready",
                "selected_steps": selected_ids, "prevented_steps": prevented_ids,
                "activation_state": activation_result["state"], "history_sha256": post_pass["history"]["sha256"],
                "history_counters": {"coder_sessions_started": post_pass["history"]["coder_sessions_started"],
                                     "source_attempts_started": post_pass["history"]["source_attempts_started"]},
                "entry_history_counters": {"coder_sessions_started": entry_history["coder_sessions_started"],
                                           "source_attempts_started": entry_history["source_attempts_started"]},
                "entry_history_sha256": entry_history_sha256,
                "entry_history_sha256_preserved": entry_history["sha256"] == entry_history_sha256,
                "entry_history_bytes_sha256": entry_history_bytes_sha256,
                "entry_history_bytes_sha256_preserved": hashlib.sha256(
                    json.dumps(entry_history, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
                ).hexdigest() == entry_history_bytes_sha256,
                "post_pass_history_advanced": post_pass["history"]["sha256"] != entry_history_sha256,
                "task_tracking_successor_sha256": task_tracking_successors[0]["sha256"] if task_tracking_successors else None,
                "post_pass_capture": "ready",
                "guarded_reentry": scoped["state"],
                "declared_disposable_effects": ["scenario source correction", "append-only fixture history",
                    *( ["Tasker marker transition"] if marker_trace else [])],
                "roadmap_sha256_before_after": [prior_roadmap_sha256,
                    sha(roadmap_path) if roadmap_path.is_file() else None],
                "external_dispatches": portable_dispatches,
                "child_process_dispatches": child_process_dispatches,
                "production_outputs": {"initial_scope": scope_check, "initial_eligibility": eligibility,
                    "route": initial_route, "rendered_switch": rendered_switch,
                    "selected_step_ids": selected_ids, "activation": activation_result,
                    "history": post_pass["history"], "task_tracking": tracked if marker_trace else None,
                    "post_pass_capture": capture_observation,
                    "current_eligibility": final_eligibility, "progress": progress,
                    "guarded_route": scoped},
                "negative_traces": negative_traces,
                "observed_effects": [
                    {"operation": "source-correction", "path": source_relative,
                     "before_sha256": baseline_finding["evidence"][0]["sha256"], "after_sha256": after_source},
                    {"operation": "implementation-history", "event_count": len(post_pass["history"]["events"]),
                     "history_sha256": post_pass["history"]["sha256"]},
                    *([{"operation": "task-marker-tracking", "path": f"{feature}/tasks.md",
                        "after_sha256": sha(tasks)}] if marker_trace else []),
                    {"operation": "post-pass-capture", "command": portable_dispatches[0] if portable_dispatches else None,
                     "state": capture_observation["result_state"]}],
                "prohibited_effect_counts": {
                    "workflow_or_phase_dispatch": len(workflow_or_phase_commands),
                    "git_integration": len(git_commands) + len(git_artifacts),
                    "real_roadmap_verification": len(roadmap_verification_records),
                    "feature_or_consumer_acceptance": len(acceptance_records),
                },
                "authority_artifact_changes": changed_authority_artifacts,
                "result": "connected-positive-production-trace"}
            if details["roadmap_sha256_before_after"][0] != details["roadmap_sha256_before_after"][1]:
                raise AssertionError(f"{trace_id}: disposable trace changed its roadmap fixture")
            if (details["scope_sha256_preserved"] is not trace["expected"]["scope_sha256_preserved"]
                    or details["assessment_sha256_preserved"] is not trace["expected"]["assessment_sha256_preserved"]
                    or details["source_preimage_sha256_preserved"] is not trace["expected"]["source_preimage_sha256_preserved"]
                    or details["current_review_evidence_rechecked"] is not trace["expected"]["current_review_evidence_rechecked"]
                    or scoped["state"] != trace["expected"]["result"]):
                raise AssertionError(f"{trace_id}: observed positive trace differs from its fixture contract: {details}")
            undeclared_effects = [effect for effect in details["observed_effects"]
                                  if effect["operation"] not in {
                                      "source-correction", "implementation-history",
                                      "task-marker-tracking", "post-pass-capture"}]
            undeclared_dispatches = [command for command in command_observations
                                     if command != expected_observed_capture_command]
            undeclared_dispatches.extend(child_process_dispatches)
            details["undeclared_effects"] = undeclared_effects + [
                {"operation": "external-dispatch", "command": command} for command in undeclared_dispatches]
            if (details["history_counters"] != {"coder_sessions_started": 1, "source_attempts_started": 1}
                    or selected_ids != ["implement-tasks"] or prevented_ids != ["blocked-route"]
                    or capture_observation.get("request_fields") != list(POST_PASS_CAPTURE_FIELDS)
                    or capture_observation.get("return_code") != 0
                    or capture_observation.get("result_state") != "ready"
                    or capture_observation.get("command_template") != expected_capture_command
                    or capture_observation.get("project_argument_bound_to_consumer") is not True
                    or child_process_dispatches
                    or command_observations != [expected_observed_capture_command]
                    or details["undeclared_effects"]
                    or details["entry_history_sha256_preserved"] is not True
                    or details["entry_history_bytes_sha256_preserved"] is not True
                    or details["post_pass_history_advanced"] is not True
                    or details["prohibited_effect_counts"] != {
                        "workflow_or_phase_dispatch": 0, "git_integration": 0,
                        "real_roadmap_verification": 0, "feature_or_consumer_acceptance": 0}):
                raise AssertionError(f"{trace_id}: dispatch, counter, or exact capture contract differs: "
                                     f"capture={capture_observation}, counters={details['history_counters']}, "
                                     f"selected={selected_ids}, prevented={prevented_ids}")
            observed[trace_id] = {"adapter_result_path": trace["adapter_result_path"],
                "sequence": list(trace["sequence"]), "expected": trace["expected"],
                "observed": {**{key: details[key] for key in trace["expected"]}, "result": scoped["state"]},
                "details": details}
    finally:
        dispatch_observer.__exit__(None, None, None)
        if prior_pointer is None:
            pointer.unlink(missing_ok=True)
        else:
            pointer.write_bytes(prior_pointer)
    if ((sha(roadmap_path) if roadmap_path.is_file() else None) != prior_roadmap_sha256):
        raise AssertionError("connected positive or negative traces changed the disposable roadmap")
    sensitivity_path = child_observer_dir / "child-process-dispatch-sensitivity.jsonl"
    sensitivity_path.write_text("", encoding="utf-8")
    sensitivity_environment = {**os.environ,
        "PYTHONPATH": os.pathsep.join(filter(None, (str(child_observer_dir), os.environ.get("PYTHONPATH", "")))),
        "FARMBOY_SUBPROCESS_AUDIT_PATH": str(sensitivity_path),
        "FARMBOY_TEST_INJECT_CHILD_PROCESS": "1"}
    subprocess.run([sys.executable, "-c", "pass"], cwd=consumer, env=sensitivity_environment,
                   text=True, capture_output=True, check=True)
    sensitivity_records = [json.loads(line) for line in sensitivity_path.read_text(encoding="utf-8").splitlines()]
    if not any(record.get("command", [None])[0] == "true" for record in sensitivity_records):
        raise AssertionError("capture-child audit sensitivity did not observe an injected child process")
    for trace_result in observed.values():
        trace_result["details"]["capture_child_audit_sensitivity"] = {
            "injected_dispatch_count": len(sensitivity_records),
            "injected_child_observed": True,
            "mode": "deterministic-sensitivity-check"}
    return observed


def _exercise_connected_negative_traces(controller_module: Any, consumer: Path, trace_id: str,
                                        valid_request: dict[str, Any], valid_history: dict[str, Any],
                                        valid_progress: dict[str, Any],
                                        fixture_scenarios: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Mutate connected controls in memory and capture production stop decisions."""
    scenarios = {item["id"]: item for item in fixture_scenarios}
    feature = valid_request["scope"]["feature_directory"]
    scope_binding = {key: valid_request[key] for key in (
        "scope", "trusted_request_reference", "retained_scope_sha256")}
    if "task_tracking_successors" in valid_request:
        scope_binding["task_tracking_successors"] = valid_request["task_tracking_successors"]
    history_path = controller_module._implementation_history_path(consumer, valid_request["scope"])[0]
    retained_before = history_path.read_bytes()
    retained_sha256 = hashlib.sha256(retained_before).hexdigest()
    observed_history, _ = controller_module._read_implementation_history(
        consumer, valid_request["scope"], valid_history["sha256"])
    counters = {"coder_sessions_started": observed_history["coder_sessions_started"],
                "source_attempts_started": observed_history["source_attempts_started"]}
    observed: list[dict[str, Any]] = []

    corrective_control = controller_module.validate_scoped_implementation_progress(consumer, valid_request)
    if (corrective_control.get("state") != "continue"
            or valid_progress.get("review", {}).get("completed_task_ids") != ["T001"]
            or counters["source_attempts_started"] < 1):
        raise AssertionError(f"{trace_id}: connected fresh corrective source control is not valid: "
                             f"route={corrective_control}, counters={counters}")

    # Start a genuine second source attempt from the exact retained history
    # prefix. Both events go through the production history adapter, and the
    # disposable consumer is restored to its original bytes after the check.
    corrective_before = history_path.read_bytes()
    corrective_before_sha256 = hashlib.sha256(corrective_before).hexdigest()
    corrective_before_history, _ = controller_module._read_implementation_history(
        consumer, valid_request["scope"], observed_history["sha256"])
    corrective_before_counters = {
        "coder_sessions_started": corrective_before_history["coder_sessions_started"],
        "source_attempts_started": corrective_before_history["source_attempts_started"]}
    corrective_observation = None
    try:
        corrective_history = _append_event(controller_module, consumer, scope_binding,
            corrective_before_history, "F023-REENTRY-FRESH-CORRECTIVE-SESSION-CONTROL",
            "coder-session-start", session=2, attempts=1, execution_kind="corrective-source-execution",
            current_source_evidence=valid_request["assessment"]["evidence"])
        corrective_history = _append_event(controller_module, consumer, scope_binding,
            corrective_history, "F023-REENTRY-FRESH-CORRECTIVE-SESSION-CONTROL",
            "source-attempt-start", session=2, attempts=2, execution_kind="corrective-source-execution",
            current_source_evidence=valid_request["assessment"]["evidence"])
        corrective_history = _append_event(controller_module, consumer, scope_binding,
            corrective_history, "F023-REENTRY-FRESH-CORRECTIVE-SESSION-CONTROL",
            "coder-session-outcome", session=2, attempts=2, execution_kind="corrective-source-execution",
            outcome="completed", current_source_evidence=valid_request["assessment"]["evidence"])
        corrective_history, _ = controller_module._read_implementation_history(
            consumer, valid_request["scope"], corrective_history["sha256"])
        fresh_request = json.loads(json.dumps(valid_request))
        fresh_request["retained_history_sha256"] = corrective_history["sha256"]
        fresh_control = controller_module.validate_scoped_implementation_progress(consumer, fresh_request)
        if (fresh_control.get("state") != "continue"
                or corrective_history["coder_sessions_started"] != 2
                or corrective_history["source_attempts_started"] != 2):
            raise AssertionError(f"{trace_id}: production fresh corrective session did not advance to 2/2: "
                                 f"history={corrective_history}, route={fresh_control}")
        if corrective_history["events"][:len(corrective_before_history["events"])] != corrective_before_history["events"]:
            raise AssertionError(f"{trace_id}: fresh corrective session changed the retained history prefix")
        corrective_after_sha256 = hashlib.sha256(history_path.read_bytes()).hexdigest()
        corrective_observation = {"id": "F023-REENTRY-FRESH-CORRECTIVE-SESSION-CONTROL",
            "valid_control_id": "F023-POSITIVE-REVIEWED-SOURCE-CORRECTION",
            "production_state": fresh_control["state"], "selected_steps": ["implement-tasks"],
            "prevented_steps": ["prepare-scoped-prerequisites"],
            "counters_before": corrective_before_counters,
            "counters_after": {"coder_sessions_started": corrective_history["coder_sessions_started"],
                               "source_attempts_started": corrective_history["source_attempts_started"]},
            "later_source_dispatches": 0, "fallback": False,
            "retained_history_prefix_sha256": observed_history["sha256"],
            "retained_history_prefix_preserved": corrective_history["events"][:len(corrective_before_history["events"])]
                == corrective_before_history["events"],
            "retained_history_bytes_sha256_before": corrective_before_sha256,
            "retained_history_bytes_sha256_after_append": corrective_after_sha256,
            "source_attempt_events_appended": 1,
            "scope_sha256_preserved": fresh_request["scope"]["scope_sha256"]
                == valid_request["scope"]["scope_sha256"]}
    finally:
        history_path.write_bytes(corrective_before)
    restored_bytes = history_path.read_bytes()
    restored_bytes_sha256 = hashlib.sha256(restored_bytes).hexdigest()
    if restored_bytes != corrective_before or restored_bytes_sha256 != corrective_before_sha256:
        raise AssertionError(f"{trace_id}: fresh corrective trace did not restore the retained history bytes")
    restored_history, _ = controller_module._read_implementation_history(
        consumer, valid_request["scope"], observed_history["sha256"])
    if (restored_history["sha256"] != observed_history["sha256"]
            or restored_history["coder_sessions_started"] != corrective_before_counters["coder_sessions_started"]
            or restored_history["source_attempts_started"] != corrective_before_counters["source_attempts_started"]):
        raise AssertionError(f"{trace_id}: production retained history readback differs after restoration: "
                             f"history={restored_history}, counters={corrective_before_counters}")
    if corrective_observation is None:
        raise AssertionError(f"{trace_id}: fresh corrective source control did not produce an observation")
    corrective_observation["retained_history_bytes_sha256_after_restore"] = restored_bytes_sha256
    if (corrective_observation["retained_history_bytes_sha256_after_restore"]
            != corrective_observation["retained_history_bytes_sha256_before"]
            or corrective_observation["retained_history_bytes_sha256_after_restore"]
            == corrective_observation["retained_history_bytes_sha256_after_append"]):
        raise AssertionError(f"{trace_id}: retained history observation does not distinguish restored bytes "
                             "from the appended history")
    observed.append(corrective_observation)

    def expected(case_id: str) -> tuple[str, str]:
        record = scenarios.get(case_id)
        if record is None:
            raise AssertionError(f"{case_id}: declared Feature 023 scenario is missing")
        outcome = record["expected_production_outcome"]
        if outcome.get("result") != "block":
            raise AssertionError(f"{case_id}: negative scenario must declare a blocking result")
        blocker = outcome.get("blocker")
        if blocker is None and case_id in {
                "F023-REENTRY-NO-SUBSTANTIVE-PROGRESS",
                "F023-REENTRY-ADMIN-ONLY-NONCREDIT",
                "F023-REENTRY-ANSWER-ONLY-NONCREDIT",
                "F023-REENTRY-MARKER-ONLY-NONCREDIT"}:
            blocker = "no-progress"
        if not isinstance(blocker, str):
            raise AssertionError(f"{case_id}: scenario lacks a stable expected production blocker")
        return blocker, outcome["safe_action"]

    def assert_expected(case_id: str, result: dict[str, Any]) -> tuple[str, str]:
        expected_blocker, safe_action = expected(case_id)
        actual_blocker = result.get("blocker", result.get("reason_code"))
        actual_action = result.get("resume_action")
        if result.get("state") != "blocked" or actual_blocker != expected_blocker:
            raise AssertionError(f"{case_id}: production blocker differs from fixture: {result}")
        if actual_action is not None and actual_action != safe_action:
            raise AssertionError(f"{case_id}: production resume action differs from fixture: {result}")
        return expected_blocker, safe_action

    # Each non-credit case starts with the independently reviewed positive control,
    # then removes only substantive resolution while retaining the same child history.
    no_credit_progress = json.loads(json.dumps(valid_progress))
    for finding in no_credit_progress["review"]["findings"]:
        finding["status"] = "unresolved"
        finding.pop("resolution_summary", None)
    no_credit_progress["review"]["completed_task_ids"] = []
    no_credit_progress["review"].pop("task_completion_evidence", None)
    no_credit_result = controller_module.validate_implementation_progress(consumer, no_credit_progress)
    if no_credit_result.get("state") != "ready" or no_credit_result.get("substantive_progress") is not False:
        raise AssertionError(f"{trace_id}: non-credit mutation did not reach production progress validation: {no_credit_result}")
    current_evidence = valid_request["assessment"]["evidence"]
    blocked_request = json.loads(json.dumps(valid_request))
    blocked_request["assessment"] = {**valid_request["assessment"],
        "reason_code": "no-new-source-progress",
        "remaining_ids": sorted(set(valid_request["assessment"]["remaining_ids"])
                                | set(no_credit_result["remaining_ids"])),
        "resolved_ids": no_credit_result["resolved_ids"]}
    blocked_request["progress"] = no_credit_progress
    variants = [("F023-REENTRY-NO-SUBSTANTIVE-PROGRESS", "substantive source resolution")]
    if not blocked_request.get("task_tracking_successors"):
        variants.append(("F023-REENTRY-ADMIN-ONLY-NONCREDIT", "administrative-only update"))
        variants.append(("F023-REENTRY-ANSWER-ONLY-NONCREDIT", "same-child answer only"))
    else:
        variants.append(("F023-REENTRY-MARKER-ONLY-NONCREDIT", "validated marker-only tracking"))

    def prepare_noncredit_history(case_id: str) -> tuple[dict[str, Any], Path]:
        scope = json.loads(json.dumps(valid_request["scope"]))
        suffix = case_id.lower().removeprefix("f023-reentry-")
        scope["run_id"] = f"{scope['run_id']}-{suffix}"
        scope["scope_sha256"] = digest({key: value for key, value in scope.items() if key != "scope_sha256"})
        binding = {"scope": scope, "trusted_request_reference": scope["request_reference"],
                   "retained_scope_sha256": scope["scope_sha256"]}
        history = controller_module._empty_implementation_history(scope)
        history = _append_event(controller_module, consumer, binding, history, case_id,
            "coder-session-start", session=1, attempts=0, execution_kind="preparation")
        history = _append_event(controller_module, consumer, binding, history, case_id,
            "coder-session-outcome", session=1, attempts=0, execution_kind="preparation", outcome="completed")
        history = _append_event(controller_module, consumer, binding, history, case_id,
            "coder-session-start", session=2, attempts=0, execution_kind="first-source-execution")
        history = _append_event(controller_module, consumer, binding, history, case_id,
            "source-attempt-start", session=2, attempts=1, execution_kind="first-source-execution")
        if case_id == "F023-REENTRY-ANSWER-ONLY-NONCREDIT":
            history = _append_event(controller_module, consumer, binding, history, case_id,
                "coder-session-outcome", session=2, attempts=1,
                execution_kind="first-source-execution", outcome="question-stopped")
            history = _append_event(controller_module, consumer, binding, history, case_id,
                "operator-input", session=2, attempts=1,
                execution_kind="first-source-execution", same_child_resume=True)
            history = _append_event(controller_module, consumer, binding, history, case_id,
                "coder-session-outcome", session=2, attempts=1,
                execution_kind="first-source-execution", outcome="completed")
        else:
            history = _append_event(controller_module, consumer, binding, history, case_id,
                "coder-session-outcome", session=2, attempts=1,
                execution_kind="first-source-execution", outcome="completed")
        path, _ = controller_module._implementation_history_path(consumer, scope)
        return {**binding, "history": history}, path

    for case_id, mutation_label in variants:
        candidate = json.loads(json.dumps(blocked_request))
        variant_history = valid_history
        variant_history_path = history_path
        if case_id == "F023-REENTRY-ADMIN-ONLY-NONCREDIT":
            scenario, variant_history_path = prepare_noncredit_history(case_id)
            variant_history = scenario["history"]
            candidate.update({key: scenario[key] for key in (
                "scope", "trusted_request_reference", "retained_scope_sha256")})
            candidate["retained_previous_assessment_sha256"] = digest({
                "scope_sha256": scenario["retained_scope_sha256"],
                "assessment": candidate["previous_assessment"]})
        if case_id == "F023-REENTRY-ANSWER-ONLY-NONCREDIT":
            answer = controller_module.resolve_child_answer(
                {"kind": "question", "step_id": "implement-tasks", "question": "Continue?",
                 "options": ["continue"], "allow_custom_answer": False},
                "continue", "retained-child", "retained-child")
            if answer["child_id"] != "retained-child":
                raise AssertionError(f"{case_id}: same-child answer was not relayed to its original child")
            scenario, variant_history_path = prepare_noncredit_history(case_id)
            variant_history = scenario["history"]
            candidate.update({key: scenario[key] for key in (
                "scope", "trusted_request_reference", "retained_scope_sha256")})
            candidate["retained_previous_assessment_sha256"] = digest({
                "scope_sha256": scenario["retained_scope_sha256"],
                "assessment": candidate["previous_assessment"]})
        if case_id == "F023-REENTRY-MARKER-ONLY-NONCREDIT":
            tracking = controller_module.validate_implementation_scope(consumer, {
                "scope": valid_request["scope"],
                "trusted_request_reference": valid_request["trusted_request_reference"],
                "retained_scope_sha256": valid_request["retained_scope_sha256"],
                "task_tracking_successors": valid_request["task_tracking_successors"]})
            if tracking.get("state") != "ready":
                raise AssertionError(f"{case_id}: actual marker-only tracking control was rejected: {tracking}")
        candidate["retained_history_sha256"] = variant_history["sha256"]
        before_call = variant_history_path.read_bytes()
        before_call_sha256 = hashlib.sha256(before_call).hexdigest()
        current_history, _ = controller_module._read_implementation_history(
            consumer, candidate["scope"], variant_history["sha256"])
        counters_before = {"coder_sessions_started": current_history["coder_sessions_started"],
                           "source_attempts_started": current_history["source_attempts_started"]}
        if case_id in {"F023-REENTRY-ADMIN-ONLY-NONCREDIT", "F023-REENTRY-ANSWER-ONLY-NONCREDIT"}:
            control = json.loads(json.dumps(candidate))
            control["assessment"]["resolved_ids"] = valid_request["assessment"]["resolved_ids"]
            control["assessment"]["remaining_ids"] = valid_request["assessment"]["remaining_ids"]
            control["progress"] = valid_progress
            control_result = controller_module.validate_scoped_implementation_progress(consumer, control)
            if control_result.get("state") != "continue":
                raise AssertionError(f"{case_id}: fresh history did not pass its production control: {control_result}")
        result = controller_module.validate_scoped_implementation_progress(consumer, candidate)
        blocker, safe_action = assert_expected(case_id, result)
        retained_after_call = variant_history_path.read_bytes()
        current_history, _ = controller_module._read_implementation_history(
            consumer, candidate["scope"], candidate["retained_history_sha256"])
        counters_after = {"coder_sessions_started": current_history["coder_sessions_started"],
                          "source_attempts_started": current_history["source_attempts_started"]}
        if retained_after_call != before_call or counters_after != counters_before:
            raise AssertionError(f"{case_id}: guard changed retained history or counters")
        observed.append({"id": case_id, "valid_control_id": "F023-REENTRY-TASK-TRACKING-CONTROL",
            "mutation": mutation_label, "production_state": result["state"], "blocker": blocker,
            "resume_action": result.get("resume_action"), "fixture_safe_action": safe_action,
            "later_source_dispatches": 0,
            "selected_steps": [], "prevented_steps": ["implement-tasks"],
            "retained_history_sha256_before": before_call_sha256,
            "retained_history_sha256_after": hashlib.sha256(retained_after_call).hexdigest(), "counters_before": counters_before,
            "counters_after": counters_after, "variant_history_sha256": variant_history["sha256"],
            "fallback": False, "history_reconstructed": False,
            "budget_reset": False})

    # Re-enter each remaining historical/current/output guard from the exact
    # passing production route control. Each mutation is confined to a fresh
    # request copy; mutable on-disk evidence is restored byte-for-byte.
    route_fields = ("scope", "trusted_request_reference", "retained_scope_sha256",
                    "retained_history_sha256", "previous_assessment",
                    "retained_previous_assessment_sha256", "task_tracking_successors")
    def route_request(source: dict[str, Any]) -> dict[str, Any]:
        return {**{key: json.loads(json.dumps(source[key])) for key in route_fields if key in source},
            "assessment": json.loads(json.dumps(source["assessment"])),
            "eligible_task_ids": list(source["eligible_task_ids"]),
            "declared_node_ids": list(source["declared_node_ids"])}

    if valid_request.get("task_tracking_successors"):
        r001_specs = {
            "F023-REENTRY-FORGED-HISTORY": ("historical-assessment-binding-invalid", "retained_previous_assessment_sha256"),
            "F023-REENTRY-ALTERED-HISTORY": ("historical-assessment-binding-invalid", "previous_assessment"),
            "F023-REENTRY-MISSING-HISTORY": ("historical-assessment-binding-invalid", "retained_previous_assessment_sha256"),
            "F023-REENTRY-UNBOUND-HISTORY": ("requested-scope-digest-mismatch", "retained_scope_sha256"),
            "F023-REENTRY-STALE-REVIEW": ("task-tracking-evidence-stale", "reviewer evidence bytes"),
            "F023-REENTRY-UNAUTHORIZED-TASK-EDIT": ("task-tracking-current-preimage-mismatch", "tasks.md description"),
            "F023-REENTRY-WRONG-BRANCH-OUTPUT": ("unresolved step output reference: assess.reason_code", "required_output.branch"),
            "F023-REENTRY-EXHAUSTED-LIMIT": ("loop-cap-exhausted", "retained source-attempt history"),
            "F023-REENTRY-EXHAUSTED-CODER-SESSIONS": ("loop-cap-exhausted", "retained coder-session history"),
        }
        for case_id, (expected_reason, mutation_label) in r001_specs.items():
            scenario = scenarios.get(case_id)
            if scenario is None:
                raise AssertionError(f"{case_id}: missing declared re-entry fixture")
            expected_action = scenario["expected_production_outcome"]["safe_action"]
            control_payload = route_request(valid_request)
            control_result = controller_module.route_scoped_implementation(consumer, control_payload)
            if control_result.get("state") != "continue" or control_result.get("next_step_id") != "implement-tasks":
                raise AssertionError(f"{case_id}: fresh production route control did not pass: {control_result}")
            candidate = route_request(valid_request)
            restore: tuple[Path, bytes] | None = None
            restore_history: tuple[Path, bytes] | None = None
            if case_id == "F023-REENTRY-FORGED-HISTORY":
                candidate["retained_previous_assessment_sha256"] = "forged"
            elif case_id == "F023-REENTRY-ALTERED-HISTORY":
                candidate["previous_assessment"]["remaining_ids"].append("finding:invented")
            elif case_id == "F023-REENTRY-MISSING-HISTORY":
                candidate.pop("retained_previous_assessment_sha256", None)
            elif case_id == "F023-REENTRY-UNBOUND-HISTORY":
                candidate["retained_scope_sha256"] = "different-scope"
            elif case_id == "F023-REENTRY-STALE-REVIEW":
                successor = candidate.get("task_tracking_successors", [None])[0]
                if successor is None:
                    if trace_id != "F023-POSITIVE-TASK-RESOLUTION-MARKER-ONLY":
                        raise AssertionError(f"{case_id}: selected control has no actual review-tracking record")
                    raise AssertionError(f"{case_id}: marker-only successor is missing")
                review_evidence = successor["reviewer_result"]["evidence"][0]
                review_path = consumer / review_evidence["path"]
                restore = (review_path, review_path.read_bytes())
                review_path.write_text("stale review evidence\n", encoding="utf-8")
            elif case_id == "F023-REENTRY-UNAUTHORIZED-TASK-EDIT":
                task_path = consumer / valid_request["scope"]["feature_directory"] / "tasks.md"
                restore = (task_path, task_path.read_bytes())
                task_text = restore[1].decode("utf-8")
                changed = task_text.replace("Reviewed source correction", "Unauthorized description edit")
                if changed == task_text:
                    raise AssertionError(f"{case_id}: valid control task text has no selected description to mutate")
                task_path.write_text(changed, encoding="utf-8")
                candidate["assessment"]["evidence"] = [{"path": task_path.relative_to(consumer).as_posix(),
                    "sha256": sha(task_path)}]
            elif case_id == "F023-REENTRY-EXHAUSTED-LIMIT":
                # Append genuine source events to the exact bound positive history,
                # then restore its original bytes after the route guard is observed.
                binding = {key: candidate[key] for key in (
                    "scope", "trusted_request_reference", "retained_scope_sha256", "task_tracking_successors")
                    if key in candidate}
                history_to_extend, _ = controller_module._implementation_history_path(consumer, candidate["scope"])
                restore_history = (history_to_extend, history_to_extend.read_bytes())
                current_history, _ = controller_module._read_implementation_history(
                    consumer, candidate["scope"], candidate["retained_history_sha256"])
                exhausted_history = _record_sessions(controller_module, consumer, binding, current_history,
                    case_id, 5, 5)
                candidate["retained_history_sha256"] = exhausted_history["sha256"]
            elif case_id == "F023-REENTRY-EXHAUSTED-CODER-SESSIONS":
                # A valid history cannot return to preparation after its first source
                # attempt. Build this independent same-scope invocation in a disposable
                # consumer copy so its five-session/one-attempt history stays valid.
                with tempfile.TemporaryDirectory(prefix="farmboy-r001-session-cap-") as temp_root:
                    isolated_consumer = Path(temp_root) / "consumer"
                    shutil.copytree(consumer, isolated_consumer, symlinks=True)
                    binding = {key: candidate[key] for key in (
                        "scope", "trusted_request_reference", "retained_scope_sha256", "task_tracking_successors")
                        if key in candidate}
                    isolated_history_path, _ = controller_module._implementation_history_path(
                        isolated_consumer, candidate["scope"])
                    isolated_history_path.unlink(missing_ok=True)
                    isolated_history = controller_module._empty_implementation_history(candidate["scope"])
                    fresh_route = controller_module.route_scoped_implementation(
                        isolated_consumer, {**route_request(valid_request),
                            "retained_history_sha256": isolated_history["sha256"]})
                    if fresh_route.get("state") != "continue":
                        raise AssertionError(f"{case_id}: fresh isolated route control did not pass: {fresh_route}")
                    exhausted_history = _record_sessions(controller_module, isolated_consumer, binding,
                        isolated_history, case_id, 5, 1)
                    candidate["retained_history_sha256"] = exhausted_history["sha256"]
                    history_path_current, _ = controller_module._implementation_history_path(
                        isolated_consumer, candidate["scope"])
                    history_before = history_path_current.read_bytes()
                    before_sha = hashlib.sha256(history_before).hexdigest()
                    history_current, _ = controller_module._read_implementation_history(
                        isolated_consumer, candidate["scope"], candidate["retained_history_sha256"])
                    before_counts = {"coder_sessions_started": history_current["coder_sessions_started"],
                                     "source_attempts_started": history_current["source_attempts_started"]}
                    result = controller_module.route_scoped_implementation(isolated_consumer, candidate)
                    history_after = history_path_current.read_bytes()
                    history_after_record, _ = controller_module._read_implementation_history(
                        isolated_consumer, candidate["scope"], candidate["retained_history_sha256"])
                    after_counts = {"coder_sessions_started": history_after_record["coder_sessions_started"],
                                    "source_attempts_started": history_after_record["source_attempts_started"]}
                    if history_after != history_before or before_counts != after_counts:
                        raise AssertionError(f"{case_id}: production guard changed isolated history or counters")
                actual_reason = result.get("reason_code", result.get("blocker"))
                actual_action = result.get("resume_action")
                if result.get("state") != "blocked" or actual_reason != expected_reason:
                    raise AssertionError(f"{case_id}: production result differs from exact expected guard: {result}")
                observed.append({"id": case_id, "valid_control_id": scenario["valid_control_id"],
                    "mutation": mutation_label, "production_state": result["state"],
                    "blocker": actual_reason, "production_resume_action": actual_action,
                    "fixture_safe_action": expected_action, "later_source_dispatches": 0,
                    "selected_steps": [], "prevented_steps": ["implement-tasks"],
                    "retained_history_sha256_before": before_sha,
                    "retained_history_sha256_after": hashlib.sha256(history_after).hexdigest(),
                    "counters_before": before_counts, "counters_after": after_counts,
                    "fallback": False, "history_reconstructed": False, "budget_reset": False})
                continue
            history_path_current, _ = controller_module._implementation_history_path(consumer, candidate["scope"])
            history_before = history_path_current.read_bytes()
            before_sha = hashlib.sha256(history_before).hexdigest()
            history_current, _ = controller_module._read_implementation_history(
                consumer, candidate["scope"], candidate["retained_history_sha256"])
            before_counts = {"coder_sessions_started": history_current["coder_sessions_started"],
                             "source_attempts_started": history_current["source_attempts_started"]}
            try:
                if case_id == "F023-REENTRY-WRONG-BRANCH-OUTPUT":
                    switch = {"id": "route", "type": "switch",
                        "expression": "{{ steps.route-choice.output.state }}",
                        "cases": {
                            "continue": [{"id": "assess", "type": "prompt"},
                                {"id": "continue-consumer", "type": "prompt",
                                 "prompt": "Continue with {{ steps.assess.output.reason_code }}"}],
                            "blocked": [{"id": "stop", "type": "prompt"},
                                {"id": "blocked-consumer", "type": "prompt",
                                 "prompt": "Stop with {{ steps.stop.output.reason_code }}"}]}}
                    selected_switch, selected_steps = controller_module.render_selected_switch(
                        switch, {}, {"route-choice": control_result})
                    if selected_switch["expression"] != "continue" or [step["id"] for step in selected_steps] != [
                            "assess", "continue-consumer"]:
                        raise AssertionError(f"{case_id}: unchanged selected-output control differs: "
                                             f"{selected_switch}, {selected_steps}")
                    valid_output = controller_module.render_template(selected_steps[1]["prompt"], {}, {
                        "assess": {"state": "continue", "reason_code": "reviewed-progress"}})
                    if valid_output != "Continue with reviewed-progress":
                        raise AssertionError(f"{case_id}: selected producer control failed: {valid_output}")
                    # The fixture's one-field mutation supplies the output from the
                    # untaken branch to the selected consumer. It must fail before effect.
                    try:
                        controller_module.render_template(selected_steps[1]["prompt"], {}, {
                            "stop": {"state": "blocked", "reason_code": "untaken-branch"}})
                    except ValueError as error:
                        actual_reason = str(error)
                    else:
                        raise AssertionError(f"{case_id}: untaken-branch output reached selected consumer")
                    result = {"state": "blocked", "reason_code": actual_reason,
                              "resume_action": "restore-required-output-from-selected-branch"}
                else:
                    result = controller_module.route_scoped_implementation(consumer, candidate)
            finally:
                if restore is not None:
                    restore[0].write_bytes(restore[1])
            actual_reason = result.get("reason_code", result.get("blocker"))
            actual_action = result.get("resume_action")
            if result.get("state") != "blocked" or actual_reason != expected_reason:
                raise AssertionError(f"{case_id}: production result differs from exact expected guard: {result}")
            expected_production_actions = {
                "historical-assessment-binding-invalid": "reassess-current-scoped-implementation-route",
                "implementation-scope-request-invalid": "reestablish-the-trusted-current-implementation-scope",
                "requested-scope-digest-mismatch": "reassess-current-scoped-implementation-route",
                "task-tracking-evidence-stale": "reassess-current-scoped-implementation-route",
                "task-tracking-current-preimage-mismatch": "reassess-current-scoped-implementation-route",
                "scoped-route-node-undeclared": "reassess-current-scoped-implementation-route",
            }
            expected_production_action = expected_production_actions.get(expected_reason)
            if expected_production_action is not None and actual_action != expected_production_action:
                raise AssertionError(f"{case_id}: production resume action differs from its stable controller contract: {result}")
            history_after = history_path_current.read_bytes()
            history_after_record, _ = controller_module._read_implementation_history(
                consumer, candidate["scope"], candidate["retained_history_sha256"])
            after_counts = {"coder_sessions_started": history_after_record["coder_sessions_started"],
                            "source_attempts_started": history_after_record["source_attempts_started"]}
            if history_after != history_before or before_counts != after_counts:
                raise AssertionError(f"{case_id}: production guard changed history bytes or counters")
            if restore_history is not None:
                restore_history[0].write_bytes(restore_history[1])
            observed.append({"id": case_id, "valid_control_id": scenario["valid_control_id"],
                "mutation": mutation_label, "production_state": result["state"],
                "blocker": actual_reason, "production_resume_action": actual_action,
                "fixture_safe_action": expected_action, "later_source_dispatches": 0,
                "selected_steps": [], "prevented_steps": ["implement-tasks"],
                "retained_history_sha256_before": before_sha,
                "retained_history_sha256_after": hashlib.sha256(history_after).hexdigest(),
                "counters_before": before_counts, "counters_after": after_counts,
                "fallback": False, "history_reconstructed": False, "budget_reset": False})

    # The assertion itself must reject both an unrelated blocker and an
    # incorrect recovery action; this is a focused sensitivity check.
    sensitivity_id = "F023-REENTRY-NO-SUBSTANTIVE-PROGRESS"
    expected_blocker, expected_action = expected(sensitivity_id)
    for injected in (
        {"state": "blocked", "blocker": "unrelated-injected-blocker"},
        {"state": "blocked", "blocker": expected_blocker, "resume_action": "wrong-injected-action"},
    ):
        try:
            assert_expected(sensitivity_id, injected)
        except AssertionError:
            continue
        raise AssertionError(f"{sensitivity_id}: wrong-blocker/action sensitivity was accepted")

    # Exercise the controller's actual same-child relay validator, first with a
    # valid relay and then with a one-field wrong-child mutation.
    question = {"kind": "question", "step_id": "implement-tasks", "question": "Continue?",
        "options": ["continue"], "allow_custom_answer": False}
    accepted_answer = controller_module.resolve_child_answer(question, "continue", "retained-child", "retained-child")
    try:
        controller_module.resolve_child_answer(question, "continue", "retained-child", "replacement-child")
    except ValueError as error:
        answer_blocker = str(error)
    else:
        raise AssertionError(f"{trace_id}: wrong-child answer passed the production relay guard")
    observed.append({"id": "F023-REENTRY-PENDING-ANSWER-RELAY-CONTROL",
        "production_state": "accepted", "action": "continue-same-child-answer-relay",
        "child_id": accepted_answer["child_id"], "counters_before": counters, "counters_after": counters,
        "later_source_dispatches": 0, "fallback": False})
    observed.append({"id": "F023-REENTRY-WRONG-CHILD-ANSWER",
        "valid_control_id": "F023-REENTRY-PENDING-ANSWER-RELAY-CONTROL",
        "production_state": "blocked", "blocker": answer_blocker,
        "resume_action": "resume-same-child-after-operator-answer", "counters_before": counters,
        "counters_after": counters, "later_source_dispatches": 0, "selected_steps": [],
        "prevented_steps": ["implement-tasks"], "fallback": False})

    scope_module = controller_module.implementation_scope_module
    child_history = controller_module._empty_implementation_history(valid_request["scope"])
    child_id = "retained-child"
    child_evidence = [{"path": f"{feature}/tasks.md", "sha256": sha(consumer / feature / "tasks.md")}]
    child_events = [
        ("coder-session-start", {"coder_session_id": child_id, "coder_sessions_started": 1,
            "source_attempts_started": 0, "execution_kind": "first-source-execution"}),
        ("source-attempt-start", {"coder_session_id": child_id, "coder_sessions_started": 1,
            "source_attempts_started": 1, "execution_kind": "first-source-execution"}),
        ("coder-session-outcome", {"coder_session_id": child_id, "coder_sessions_started": 1,
            "source_attempts_started": 1, "outcome": "question-stopped"}),
        ("operator-input", {"coder_session_id": child_id, "coder_sessions_started": 1,
            "source_attempts_started": 1, "same_child_resume": True}),
    ]
    for number, (kind, extra) in enumerate(child_events, start=1):
        event = {"event_id": f"{trace_id}-answer-{number}",
            "predecessor_sha256": child_history["events"][-1]["sha256"] if child_history["events"] else "0" * 64,
            "scope_sha256": valid_request["scope"]["scope_sha256"], "event_kind": kind,
            "declared_node_id": "implement-tasks", "occurred_at": f"2026-10-13T21:00:{number:02d}Z",
            "evidence": child_evidence, **extra}
        event["sha256"] = digest(event)
        child_history = scope_module.append_execution_event(child_history, event,
            scope_sha256=valid_request["scope"]["scope_sha256"],
            retained_history_sha256=child_history["sha256"])
    same_child_history = scope_module.validate_execution_history(child_history,
        scope_sha256=valid_request["scope"]["scope_sha256"], retained_history_sha256=child_history["sha256"])
    fresh_child_history = json.loads(json.dumps(same_child_history))
    fresh_child_history["events"][-1]["coder_session_id"] = "fresh-child"
    fresh_child_history["events"][-1]["sha256"] = digest({key: value for key, value in
        fresh_child_history["events"][-1].items() if key != "sha256"})
    fresh_child_history["sha256"] = digest({key: value for key, value in fresh_child_history.items()
        if key != "sha256"})
    try:
        scope_module.validate_execution_history(fresh_child_history,
            scope_sha256=valid_request["scope"]["scope_sha256"],
            retained_history_sha256=fresh_child_history["sha256"])
    except ValueError as error:
        fresh_child_blocker = str(error)
    else:
        raise AssertionError(f"{trace_id}: fresh child session received same-child answer credit")
    observed.append({"id": "F023-REENTRY-FRESH-CHILD-NONCREDIT",
        "valid_control_id": "F023-REENTRY-PENDING-ANSWER-RELAY-CONTROL",
        "valid_control_state": "accepted", "production_state": "blocked",
        "blocker": fresh_child_blocker, "resume_action": "resume-same-child-after-operator-answer",
        "later_source_dispatches": 0, "selected_steps": [], "prevented_steps": ["implement-tasks"],
        "counters_before": counters, "counters_after": counters, "fallback": False,
        "history_reconstructed": False, "budget_reset": False})

    # Route unresolved consequential decisions to the declared human boundary.
    gate_id = "resolve-consequential-human-decision"
    needs_human = {"state": "needs-human", "reason_code": "operator-decision-required",
        "evidence": current_evidence, "remaining_ids": ["task:T002"], "resolved_ids": [],
        "gate_step_id": gate_id}
    gate_route = controller_module.route_assessment(needs_human,
        loop_body_step_ids={"prepare-scoped-prerequisites", "implement-tasks"},
        human_gate_step_ids={gate_id})
    if gate_route != {"action": "needs-human", "gate_step_id": gate_id}:
        raise AssertionError(f"{trace_id}: production router bypassed unresolved human gate: {gate_route}")
    observed.append({"id": "F023-REENTRY-CONSEQUENTIAL-GATE-UNRESOLVED",
        "valid_control_id": "F023-REENTRY-TASK-TRACKING-CONTROL", "production_state": "needs-human",
        "blocker": "human-decision-required", "resume_action": "resolve-consequential-human-decision",
        "selected_step": gate_route["gate_step_id"], "prevented_steps": ["implement-tasks"],
        "later_source_dispatches": 0, "counters_before": counters, "counters_after": counters,
        "fallback": False})

    # Validate the installed assignment graph before exercising a single
    # malformed-assignment mutation through the production definition guard.
    definition = __import__("yaml").safe_load(
        (consumer / ".specify/workflows/farmboy-implement/workflow.yml").read_text(encoding="utf-8"))
    controller_module.validate_workflow_definition(definition)
    source_assignments = [item for item in controller_module.collect_agent_assignments(definition["steps"])
                          if item.step_id == "run-scoped-source-implementation"]
    if len(source_assignments) != 1 or source_assignments[0].agent_name != "FarmBoy Coder":
        raise AssertionError(f"{trace_id}: installed source assignment control is invalid: {source_assignments}")
    assignment_mutation = json.loads(json.dumps(definition))
    def mutate_assignment(nodes: list[dict[str, Any]]) -> bool:
        for node in nodes:
            if node.get("id") == "run-scoped-source-implementation":
                node["farmboy"]["agent"] = "Unavailable Fixture Agent"
                return True
            for branch in node.get("cases", {}).values() if isinstance(node.get("cases"), dict) else []:
                if mutate_assignment(branch):
                    return True
            if mutate_assignment(node.get("default", [])) or mutate_assignment(node.get("steps", [])):
                return True
        return False
    if not mutate_assignment(assignment_mutation["steps"]):
        raise AssertionError(f"{trace_id}: installed workflow omitted the selected source assignment")
    try:
        controller_module.validate_workflow_definition(assignment_mutation)
    except ValueError as error:
        assignment_blocker = str(error)
    else:
        raise AssertionError(f"{trace_id}: production definition guard accepted an invalid source assignment")
    bootstrap_path = consumer / ".specify/farmboy/scripts/bootstrap.sh"
    bootstrap_source = bootstrap_path.read_text(encoding="utf-8")
    if ("exec \"$python_bin\" \"$controller\" inspect" not in bootstrap_source
            or "workflow_id=\"$2\"" not in bootstrap_source
            or "skill_id=\"$3\"" not in bootstrap_source):
        raise AssertionError(f"{trace_id}: installed bootstrap command ownership contract changed")
    observed.append({"id": "F023-REENTRY-ASSIGNMENT-STATIC-BOUNDARY",
        "valid_control_id": "F023-REENTRY-ASSIGNMENT-STATIC-BOUNDARY",
        "production_state": "accepted", "assignment": {"step_id": source_assignments[0].step_id,
            "agent_name": source_assignments[0].agent_name}, "mutation_state": "blocked",
        "mutation_blocker": assignment_blocker, "bootstrap_owner": ".specify/farmboy/scripts/bootstrap.sh",
        "bootstrap_command_owner": ".specify/farmboy/scripts/python/controller.py inspect",
        "later_source_dispatches": 0, "counters_before": counters, "counters_after": counters,
        "fallback": False, "native_availability_claim": False})

    # Verify the installed bootstrap ownership record as the passing control,
    # then change only its retained digest in the disposable consumer record.
    install_record = controller_module.verify_controller_install(
        consumer, "farmboy-implement", "farmboy-implement")
    install_record_path = consumer / ".specify/farmboy/skills-install.json"
    install_record_before = install_record_path.read_bytes()
    mutated_record = json.loads(install_record_before)
    mutated_record["files"][".specify/farmboy/scripts/bootstrap.sh"] = "0" * 64
    install_record_path.write_text(json.dumps(mutated_record, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    try:
        try:
            controller_module.verify_controller_install(consumer, "farmboy-implement", "farmboy-implement")
        except ValueError as error:
            bootstrap_blocker = str(error)
        else:
            raise AssertionError(f"{trace_id}: bootstrap ownership mutation passed installed verification")
    finally:
        install_record_path.write_bytes(install_record_before)
    if (install_record_path.read_bytes() != install_record_before
            or bootstrap_blocker != "FarmBoy owned controller file was changed: .specify/farmboy/scripts/bootstrap.sh"):
        raise AssertionError(f"{trace_id}: bootstrap ownership control/mutation was not exact: {bootstrap_blocker}")
    observed.append({"id": "F023-REENTRY-BOOTSTRAP-OWNERSHIP",
        "valid_control_id": "F023-REENTRY-BOOTSTRAP-OWNERSHIP",
        "production_state": "accepted", "mutation_state": "blocked",
        "mutation_blocker": bootstrap_blocker,
        "bootstrap_sha256": install_record["files"][".specify/farmboy/scripts/bootstrap.sh"],
        "retained_record_bytes_restored": install_record_path.read_bytes() == install_record_before,
        "later_source_dispatches": 0, "counters_before": counters, "counters_after": counters,
        "fallback": False})

    # The installed Close Out workflow declares a real gate menu. Validate its
    # explicit deterministic answer, then mutate only the answer value.
    gate_definition = __import__("yaml").safe_load(
        (consumer / ".specify/workflows/farmboy-closeout/workflow.yml").read_text(encoding="utf-8"))
    controller_module.validate_workflow_definition(gate_definition)
    def find_gate(nodes: list[dict[str, Any]]) -> dict[str, Any] | None:
        for node in nodes:
            if node.get("type") == "gate":
                return node
            for branch in node.get("cases", {}).values() if isinstance(node.get("cases"), dict) else []:
                found = find_gate(branch)
                if found is not None:
                    return found
            found = find_gate(node.get("default", [])) or find_gate(node.get("steps", []))
            if found is not None:
                return found
        return None
    gate = find_gate(gate_definition["steps"])
    if gate is None or not gate.get("options"):
        raise AssertionError(f"{trace_id}: installed workflow has no declared gate/menu control")
    allowed_gate_answer = gate["options"][0]
    gate_choice = controller_module.validate_gate_choice(gate, allowed_gate_answer)
    def find_answer_switch(nodes: list[dict[str, Any]]) -> dict[str, Any] | None:
        for node in nodes:
            if (node.get("type") == "switch"
                    and f"steps.{gate['id']}.output.choice" in node.get("expression", "")):
                return node
            for branch in node.get("cases", {}).values() if isinstance(node.get("cases"), dict) else []:
                found = find_answer_switch(branch)
                if found is not None:
                    return found
            found = find_answer_switch(node.get("default", [])) or find_answer_switch(node.get("steps", []))
            if found is not None:
                return found
        return None
    answer_switch = find_answer_switch(gate_definition["steps"])
    if answer_switch is None:
        raise AssertionError(f"{trace_id}: installed gate answer has no actual downstream branch switch")
    selected_switch, selected_gate_branch = controller_module.render_selected_switch(
        answer_switch, {}, {gate["id"]: {"choice": gate_choice}})
    if selected_switch.get("expression") != gate_choice:
        raise AssertionError(f"{trace_id}: validated gate did not select its matching branch: {selected_switch}")
    selected_gate_steps = [step["id"] for step in selected_gate_branch]
    try:
        controller_module.validate_gate_choice(gate, "invalid-unlisted-gate-answer")
    except ValueError as error:
        gate_blocker = str(error)
    else:
        raise AssertionError(f"{trace_id}: production gate accepted an unlisted answer")
    observed.append({"id": "F023-REENTRY-GATE-ANSWER-BOUNDARY",
        "valid_control_id": "F023-REENTRY-GATE-ANSWER-BOUNDARY",
        "production_state": "accepted", "mutation_state": "blocked",
        "gate_step_id": gate["id"], "downstream_switch_id": answer_switch["id"],
        "frozen_options_sha256": digest(gate["options"]),
        "accepted_answer": gate_choice, "selected_branch_steps": selected_gate_steps,
        "invalid_answer_blocker": gate_blocker,
        "invalid_answer_branch_dispatches": 0, "later_branch_dispatches": 0,
        "later_source_dispatches": 0, "counters_before": counters, "counters_after": counters,
        "fallback": False, "gate_definition_unchanged": True})

    # Compare retained installation evidence through the installed recovery helper.
    recovery_path = consumer / ".specify/farmboy/scripts/python/recovery.py"
    recovery_spec = importlib.util.spec_from_file_location("farmboy_snapshot_recovery", recovery_path)
    if recovery_spec is None or recovery_spec.loader is None:
        raise AssertionError("installed recovery module cannot be loaded for installation-drift coverage")
    recovery_module = importlib.util.module_from_spec(recovery_spec)
    recovery_spec.loader.exec_module(recovery_module)
    initial_fingerprints = {"bundle_record": {"sha256": "b" * 64}, "skill_record": {"sha256": "c" * 64}}
    recovery_summary = {"status": "incomplete", "workflow_sha256": "a" * 64,
        "bundle_record": initial_fingerprints["bundle_record"],
        "skill_record": initial_fingerprints["skill_record"]}
    unchanged_resume = recovery_module.resume_decision(recovery_summary, "a" * 64, initial_fingerprints)
    if unchanged_resume != {"action": "resume"}:
        raise AssertionError(f"{trace_id}: unchanged installation recovery control failed: {unchanged_resume}")
    drifted_fingerprints = {**initial_fingerprints, "skill_record": {"sha256": "d" * 64}}
    resume = recovery_module.resume_decision(recovery_summary, "a" * 64, drifted_fingerprints)
    if resume != {"action": "stop", "blocker": "installation-changed"}:
        raise AssertionError(f"{trace_id}: installation drift did not stop through production recovery: {resume}")
    observed.append({"id": "F023-REENTRY-INSTALLATION-DRIFT", "valid_control_id": "F023-REENTRY-INSTALLATION-RECOVERY-CONTROL",
        "production_state": resume["action"], "blocker": resume["blocker"],
        "resume_action": "revalidate-installed-workflow-and-records", "later_source_dispatches": 0,
        "matching_control": unchanged_resume, "counters_before": counters, "counters_after": counters,
        "fallback": False})

    # Exercise the installed main recovery boundary with deterministic stimuli.
    # These observations model main-controller reports only; they make no claim
    # that a native Coder is or is not currently available.
    installed_workflow_path = consumer / ".specify/workflows/farmboy-implement/workflow.yml"
    installed_workflow = __import__("yaml").safe_load(installed_workflow_path.read_text(encoding="utf-8"))
    controller_module.validate_workflow_definition(installed_workflow)
    installed_assignments = [item for item in controller_module.collect_agent_assignments(installed_workflow["steps"])
                             if item.step_id == "run-scoped-source-implementation"]
    if (len(installed_assignments) != 1 or installed_assignments[0].agent_name != "FarmBoy Coder"
            or installed_workflow["workflow"]["id"] != "farmboy-implement"):
        raise AssertionError(f"{trace_id}: exact installed source assignment is unavailable: {installed_assignments}")
    recovery_fingerprints = controller_module.installation_fingerprints(consumer)
    if not recovery_fingerprints or any(recovery_fingerprints.get(key) is None
                                        for key in ("bundle_record", "skill_record")):
        raise AssertionError(f"{trace_id}: installed recovery fingerprints are incomplete: {recovery_fingerprints}")
    workflow_sha256 = sha(installed_workflow_path)
    assignment_payload = [{"step_id": item.step_id, "agent_name": item.agent_name}
                          for item in installed_assignments]
    source_route_control = controller_module.validate_scoped_implementation_progress(consumer, valid_request)
    if source_route_control.get("state") != "continue":
        raise AssertionError(f"{trace_id}: available source control did not reach guarded source consumption: "
                             f"{source_route_control}")
    history_before_stops = history_path.read_bytes()
    history_before_stops_sha256 = hashlib.sha256(history_before_stops).hexdigest()
    history_before_stops_record, _ = controller_module._read_implementation_history(
        consumer, valid_request["scope"], valid_history["sha256"])
    stop_counters_before = {"coder_sessions_started": history_before_stops_record["coder_sessions_started"],
                            "source_attempts_started": history_before_stops_record["source_attempts_started"]}

    recovery_observations: list[dict[str, Any]] = []
    stop_cases = (
        ("F023-REENTRY-ASSIGNMENT-UNAVAILABLE", "child-unavailable"),
        ("F023-REENTRY-CONSEQUENTIAL-GATE-UNRESOLVED", "human-input-missing"),
    )
    for fixture_case_id, blocker in stop_cases:
        scenario = scenarios.get(fixture_case_id)
        if scenario is None:
            raise AssertionError(f"{fixture_case_id}: declared recovery stop fixture is missing")
        summary = recovery_module.create_summary(consumer,
            {"workflow": installed_workflow["workflow"], "sha256": workflow_sha256},
            recovery_fingerprints, assignment_payload, preflight_passed=True)
        summary_path = consumer / ".specify/farmboy-controllers/runs" / summary["run_id"] / "summary.json"
        recovery_module.update_step(summary_path, "run-scoped-source-implementation", "running")
        interrupted = recovery_module.mark_interrupted_steps_incomplete(summary_path)
        resumable_control = recovery_module.resume_decision(interrupted, workflow_sha256, recovery_fingerprints)
        if resumable_control != {"action": "resume"}:
            raise AssertionError(f"{trace_id}: unchanged installed recovery control failed: {resumable_control}")
        before_summary_sha256 = sha(summary_path)

        # Prove that a no-op stop would leave the run resumable, so this fixture
        # detects a lost persistence effect. The actual stop below still uses
        # the production helper and must block re-entry.
        with patch.object(recovery_module, "stop_run", side_effect=lambda path, stop_blocker, changed_files=None:
                          recovery_module.read_summary(path)):
            no_op_summary = recovery_module.stop_run(summary_path, blocker, [])
        no_op_resume = recovery_module.resume_decision(no_op_summary, workflow_sha256, recovery_fingerprints)
        if no_op_resume != {"action": "resume"}:
            raise AssertionError(f"{trace_id}: stop-persistence sensitivity did not expose no-op stop: {no_op_resume}")

        stopped_summary = recovery_module.stop_run(summary_path, blocker, [])
        readback = recovery_module.read_summary(summary_path)
        stopped_decision = recovery_module.resume_decision(readback, workflow_sha256, recovery_fingerprints)
        if (stopped_summary.get("status") != "stopped" or readback.get("blocker") != blocker
                or readback.get("effective_assignments") != assignment_payload
                or readback.get("workflow_sha256") != workflow_sha256
                or {key: readback.get(key) for key in recovery_fingerprints} != recovery_fingerprints
                or readback.get("steps", {}).get("run-scoped-source-implementation", {}).get("status") != "incomplete"
                or stopped_decision != {"action": "stop", "blocker": blocker}):
            raise AssertionError(f"{trace_id}: production recovery failed to persist exact stop: "
                                 f"readback={readback}, decision={stopped_decision}")
        history_after = history_path.read_bytes()
        history_after_record, _ = controller_module._read_implementation_history(
            consumer, valid_request["scope"], valid_history["sha256"])
        counters_after = {"coder_sessions_started": history_after_record["coder_sessions_started"],
                          "source_attempts_started": history_after_record["source_attempts_started"]}
        if history_after != history_before_stops or counters_after != stop_counters_before:
            raise AssertionError(f"{trace_id}: production stop changed retained scope history or counters")
        recovery_observations.append({
            "id": fixture_case_id,
            "valid_control_id": scenario["valid_control_id"],
            "mutation": scenario["mutation"],
            "execution_mode": "deterministic-main-stop-observation",
            "simulated_main_observation": blocker,
            "live_identity_claim": False,
            "assignment": assignment_payload,
            "workflow_sha256": workflow_sha256,
            "installation_fingerprints": recovery_fingerprints,
            "valid_recovery_control": resumable_control,
            "valid_scope_progress_control": source_route_control["state"],
            "production_state": "blocked",
            "observed_recovery_decision": stopped_decision,
            "fallback": False,
            "prevented_steps": ["run-scoped-source-implementation"],
            "later_source_dispatches": 0,
            "source_consumption_after_stop": False,
            "scope_sha256_preserved": valid_request["scope"]["scope_sha256"]
                == valid_request["retained_scope_sha256"],
            "retained_history_sha256_before": valid_history["sha256"],
            "retained_history_sha256_after": history_after_record["sha256"],
            "retained_history_bytes_sha256_before": history_before_stops_sha256,
            "retained_history_bytes_sha256_after": hashlib.sha256(history_after).hexdigest(),
            "counters_before": stop_counters_before,
            "counters_after": counters_after,
            "summary_sha256_before": before_summary_sha256,
            "summary_sha256_after": sha(summary_path),
            "stop_persistence_sensitivity": {"detected": True, "injections": 1,
                "unpersisted_stop_decision": no_op_resume}})
    if history_path.read_bytes() != history_before_stops:
        raise AssertionError(f"{trace_id}: recovery stop observations changed retained history bytes")
    observed.extend(recovery_observations)

    retained_after = history_path.read_bytes()
    if len(retained_after) < len(retained_before):
        raise AssertionError(f"{trace_id}: retained history was shortened during negative controls")
    for result in observed:
        if result.get("later_source_dispatches") != 0 or result.get("fallback") is not False:
            raise AssertionError(f"{trace_id}: negative control allowed a later dispatch or fallback: {result}")
        result["retained_records_unchanged"] = hashlib.sha256(retained_after).hexdigest() == retained_sha256
        result["retained_history_sha256"] = valid_history["sha256"]
        result["counters"] = counters
        result.setdefault("history_reconstructed", False)
        result.setdefault("budget_reset", False)
    return observed
    if ((sha(roadmap_path) if roadmap_path.is_file() else None) != prior_roadmap_sha256
            or (pointer.read_bytes() if pointer.is_file() else None) != prior_pointer):
        raise AssertionError("connected positive traces did not restore the consumer pointer or preserve its roadmap")
    if list(observed) != [item["id"] for item in traces]:
        raise AssertionError("connected positive traces were aliased or reordered")
    report_path = os.environ.get("FARMBOY_CONNECTED_TRACE_REPORT")
    if report_path:
        Path(report_path).write_text(json.dumps(observed, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return observed


def _load_public_extension_module(path: Path, name: str) -> Any:
    """Load a module from the initialized consumer's installed extension payload."""
    if not path.is_file():
        raise AssertionError(f"required installed roadmap API is missing: {path.name}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"installed roadmap API cannot be loaded: {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _exercise_lifecycle_receipt_readback(controller_module: Any, consumer: Path) -> dict[str, Any]:
    """Apply one disposable roadmap delta, then read its receipt through production APIs."""
    lifecycle_check = getattr(controller_module, "workflow_lifecycle_check", None)
    receipt_validator = getattr(controller_module, "validate_lifecycle_receipt", None)
    lifecycle_module = getattr(lifecycle_check, "__globals__", None)
    if (not callable(lifecycle_check) or not callable(receipt_validator)
            or not isinstance(lifecycle_module, dict)):
        raise AssertionError("required production lifecycle APIs are unavailable")
    controller_runtime_path = Path(getattr(controller_module, "__file__", "")).resolve()
    lifecycle_runtime_path = Path(str(lifecycle_module.get("__file__", ""))).resolve()
    if (not controller_runtime_path.is_file() or not lifecycle_runtime_path.is_file()
            or lifecycle_runtime_path.parent != controller_runtime_path.parent):
        raise AssertionError(
            "production lifecycle API must come from the same intended source or installed runtime directory")

    with tempfile.TemporaryDirectory(prefix="farmboy-lifecycle-readback-") as temporary:
        project = Path(temporary).resolve() / "consumer"
        shutil.copytree(consumer, project)
        extension_root = project / ".specify/extensions/flow-roadmap"
        scripts = extension_root / "scripts/python"
        yaml_module = __import__("yaml")
        config_module = _load_public_extension_module(scripts / "load_config.py", "snapshot_roadmap_config")
        writer_module = _load_public_extension_module(scripts / "roadmap_write.py", "snapshot_roadmap_writer")
        config = config_module.resolve_configuration(project, extension_root, yaml_module)
        roadmap_relative = config["roadmap_path"]
        roadmap = project / roadmap_relative
        roadmap.parent.mkdir(parents=True, exist_ok=True)

        feature = "specs/998-lifecycle-readback"
        spec_relative = f"{feature}/spec.md"
        spec_bytes = b"# Disposable lifecycle readback fixture\n"
        spec_path = project / spec_relative
        spec_path.parent.mkdir(parents=True, exist_ok=True)
        spec_path.write_bytes(spec_bytes)
        decision_relative = f"{feature}/validation/operator-decision.json"
        decision = {"schema_version": "1.0", "kind": "disposable-lifecycle-test",
                    "reference": "disposable-lifecycle-test"}
        decision_bytes = (json.dumps(decision, sort_keys=True, separators=(",", ":")) + "\n").encode()
        decision_path = project / decision_relative
        decision_path.parent.mkdir(parents=True, exist_ok=True)
        decision_path.write_bytes(decision_bytes)

        original_roadmap = (
            "<!--\nSYNC IMPACT REPORT\n==================\nDisposable lifecycle readback fixture.\n-->\n"
            "# Roadmap\n\n### 998 — Lifecycle Readback [status: specced]\n\n"
            "- **Description**: Disposable lifecycle readback.\n"
            "- **Outcome**: Verify applied receipt readback.\n"
            "- **Scope (in)**: One disposable fixture.\n"
            "- **Scope (out)**: Real roadmap state.\n"
            "- **Depends on**: None.\n"
            f"- **Spec dir**: {feature}/\n\n"
            "**Version**: 1.2.3 | **Ratified**: 2026-01-01 | **Last Amended**: 2026-01-02\n"
        ).encode()
        roadmap.write_bytes(original_roadmap)
        scope_sha = hashlib.sha256(spec_bytes).hexdigest()
        decision_sha = hashlib.sha256(decision_bytes).hexdigest()
        check_ids = sorted(lifecycle_module["CHECKS"]["in-progress"])
        assessment_refs: list[dict[str, str]] = []
        for reviewer, kind, filename in (
                ("FarmBoy Reviewer", "independent-review", "reviewer.json"),
                ("FarmBoy Readiness Checker", "readiness", "readiness.json")):
            relative = f"{feature}/validation/{filename}"
            assessment = {"schema_version": "1.0", "kind": kind, "reviewer": reviewer,
                "state": "ready", "feature_directory": feature, "scope_sha256": scope_sha,
                "artifact_digests": {spec_relative: scope_sha}, "required_check_ids": check_ids,
                "satisfied_check_ids": check_ids, "unresolved_ids": []}
            raw = (json.dumps(assessment, sort_keys=True, separators=(",", ":")) + "\n").encode()
            path = project / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            assessment_refs.append({"path": relative, "sha256": hashlib.sha256(raw).hexdigest(), "kind": kind})

        snapshot = {"schema_version": "1.0", "feature_directory": feature, "entry_id": "998",
            "phase": "implement", "workflow_id": "farmboy-implement", "workflow_version": "0.8.0",
            "run_id": "lifecycle-readback", "current_status": "specced", "scope_sha256": scope_sha,
            "source_map": {spec_relative: scope_sha, decision_relative: decision_sha,
                           **{item["path"]: item["sha256"] for item in assessment_refs}},
            "dependency_states": [], "pending_future_ids": []}
        group = {"milestone": "in-progress", "owning_phase": "implement", "assessments": assessment_refs,
            "required_check_ids": check_ids, "satisfied_check_ids": check_ids, "unresolved_ids": [],
            "artifact_digests": {spec_relative: scope_sha}, "historical_activity": [], "pending_future_ids": []}
        effect_id = "lifecycle-readback-effect"
        authorization = decision_relative
        delta = {"roadmap_path": roadmap_relative, "entry_id": "998", "feature_directory": feature,
            "from_status": "specced", "to_status": "in-progress",
            "expected_roadmap_sha256": hashlib.sha256(original_roadmap).hexdigest(),
            "authorization_reference": authorization,
            "evidence_paths": sorted(item["path"] for item in assessment_refs)}
        actual_writer_apply = writer_module.apply
        writer_invocations = 0

        def counted_writer_apply(*args: Any, **kwargs: Any) -> dict[str, Any]:
            nonlocal writer_invocations
            writer_invocations += 1
            return actual_writer_apply(*args, **kwargs)

        writer_module.apply = counted_writer_apply
        writer_result = writer_module.apply(project, delta, yaml_module)
        if writer_result.get("state") != "applied":
            raise AssertionError(f"disposable roadmap writer did not apply its one authorized delta: {writer_result}")
        if writer_invocations != 1:
            raise AssertionError(f"disposable setup expected one writer application, observed {writer_invocations}")

        proposal: dict[str, Any] = {"schema_version": "1.0", "snapshot": snapshot,
            "milestone_evidence": [group],
            "decision": {"reference": decision_relative, "sha256": decision_sha,
                         "contract_sha256": lifecycle_module["POLICY_SHA256"]},
            "from_status": "specced", "to_status": "in-progress",
            "expected_roadmap_sha256": delta["expected_roadmap_sha256"], "patch_sha256": "0" * 64,
            "effect_id": effect_id,
            "recovery": {"mode": "normal", "ceiling": "in-progress", "roadmap_path": roadmap_relative,
                         "source_preimage": original_roadmap.decode(), "verification": []}}
        operations = {key: value for key, value in proposal.items() if key != "patch_sha256"}
        operations["recovery"] = {key: value for key, value in proposal["recovery"].items()
                                  if key != "verification"}
        proposal["patch_sha256"] = digest(operations)
        occurred_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        payload = {"action": "verify-effect", "proposal": proposal,
                   "command_succeeded": True, "occurred_at": occurred_at}
        applied_bytes = roadmap.read_bytes()
        mutation_count = applied_bytes.count(b"Version**: 1.2.4")
        if mutation_count != 1:
            raise AssertionError("disposable roadmap writer did not produce exactly one version mutation")
        first = lifecycle_check(project, payload)
        receipt_relative = f"{feature}/validation/phase-lifecycle/{effect_id}.json"
        receipt_path = project / receipt_relative
        if first.get("state") != "verified" or not receipt_path.is_file():
            raise AssertionError(f"production lifecycle readback did not verify the applied effect: {first}")
        receipt_before = receipt_path.read_bytes()
        receipt = receipt_validator(json.loads(receipt_before))
        second = lifecycle_check(project, payload)
        controller_path = Path(inspect.getsourcefile(controller_module) or "").resolve()
        subprocess_result = subprocess.run(
            [sys.executable, str(controller_path), "phase-lifecycle", "--project", str(project)],
            input=json.dumps(payload), text=True, capture_output=True, check=False)
        try:
            subprocess_observation = json.loads(subprocess_result.stdout)
        except json.JSONDecodeError as error:
            raise AssertionError("production lifecycle subprocess returned invalid JSON") from error
        receipt_after = receipt_path.read_bytes()
        if second.get("state") != "verified":
            raise AssertionError(f"production lifecycle reassessment did not verify the retained receipt: {second}")
        if (subprocess_result.returncode != 0 or subprocess_observation.get("state") != "verified"
                or subprocess_observation.get("receipt") != second.get("receipt")):
            raise AssertionError(f"production lifecycle subprocess disagreed with direct API readback: {subprocess_observation}")
        if writer_invocations != 1:
            raise AssertionError("lifecycle readback invoked the roadmap writer a second time")
        if receipt_before != receipt_after or roadmap.read_bytes() != applied_bytes:
            raise AssertionError("lifecycle reassessment changed retained receipt or applied roadmap bytes")
        source_mutation = project / assessment_refs[0]["path"]
        non_roadmap_sha_before = sha(source_mutation)
        source_mutation.write_bytes(source_mutation.read_bytes() + b"separate non-roadmap mutation\n")
        non_roadmap_sha_after = sha(source_mutation)
        if non_roadmap_sha_before == non_roadmap_sha_after:
            raise AssertionError("separate non-roadmap artifact mutation did not change its current digest")
        blocked = lifecycle_check(project, payload)
        if blocked.get("state") != "blocked" or blocked.get("reason_code") != "post-effect-source-changed":
            raise AssertionError(f"changed non-roadmap artifact was not rejected by production lifecycle: {blocked}")
        if receipt_path.read_bytes() != receipt_before or roadmap.read_bytes() != applied_bytes:
            raise AssertionError("non-roadmap rejection changed retained receipt or applied roadmap bytes")

        lifecycle_path = Path(inspect.getsourcefile(lifecycle_check) or "").resolve()
        if lifecycle_path != lifecycle_runtime_path:
            raise AssertionError("lifecycle API source path changed during disposable readback")
        try:
            module_origin = lifecycle_path.relative_to(project.resolve()).as_posix()
        except ValueError:
            try:
                module_origin = lifecycle_path.relative_to(consumer.resolve()).as_posix()
            except ValueError:
                module_origin = lifecycle_path.relative_to(Path(__file__).parents[1].resolve()).as_posix()
        try:
            controller_origin = controller_path.relative_to(consumer.resolve()).as_posix()
        except ValueError:
            controller_origin = controller_path.relative_to(Path(__file__).parents[1].resolve()).as_posix()
        return {"scenario_id": "F023-LIFECYCLE-APPLIED-ROADMAP-READBACK",
            "module_origin": module_origin, "module_sha256": sha(lifecycle_path),
            "controller_runtime_origin": controller_origin,
            "controller_runtime_sha256": sha(controller_path),
            "subprocess_runtime_state": subprocess_observation["state"],
            "effect_identity_before": receipt["effect_id"], "effect_identity_after": second["receipt"]["effect_id"],
            "receipt_identity_before": receipt_relative, "receipt_identity_after": receipt_relative,
            "receipt_timestamp_before": receipt["occurred_at"],
            "receipt_timestamp_after": second["receipt"]["occurred_at"],
            "receipt_sha256_before": hashlib.sha256(receipt_before).hexdigest(),
            "receipt_sha256_after": hashlib.sha256(receipt_after).hexdigest(),
            "roadmap_preimage_sha256": hashlib.sha256(original_roadmap).hexdigest(),
            "retained_roadmap_sha256": hashlib.sha256(applied_bytes).hexdigest(),
            "roadmap_mutation_count_before_reassessment": mutation_count,
            "roadmap_mutation_count_after_reassessment": roadmap.read_bytes().count(b"Version**: 1.2.4"),
            "writer_invocations_before_readback": writer_invocations,
            "writer_invocations_after_readback": writer_invocations,
            "reassessment_state": second["state"], "non_roadmap_artifact_mutation_state": blocked["state"],
            "non_roadmap_artifact_reason_code": blocked["reason_code"],
            "non_roadmap_artifact_path": assessment_refs[0]["path"],
            "non_roadmap_sha256_before": non_roadmap_sha_before,
            "non_roadmap_sha256_after": non_roadmap_sha_after}


def _observed_specify_version() -> str:
    """Read the version from the configured Specify executable."""
    executable = shutil.which(os.environ.get("SPECIFY_BIN", "specify"))
    if not executable:
        raise AssertionError("Specify CLI is required to validate portable runtime provenance")
    result = subprocess.run([executable, "--version"], text=True, capture_output=True, check=False)
    if result.returncode != 0 or not result.stdout.strip():
        raise AssertionError("Specify CLI did not report its runtime version")
    return result.stdout.strip()


def _portable_matrix_provenance(consumer: Path, controller_module: Any, workflow_path: Path,
                                fixture_path: Path) -> dict[str, Any]:
    """Collect observed, portable provenance for one source or installed matrix run."""
    root = Path(__file__).parents[1].resolve()
    controller_path = Path(getattr(controller_module, "__file__", "")).resolve()
    installed_root = consumer.resolve()
    installed = controller_path.is_relative_to(installed_root)
    source_manifest = root / "controllers/farmboy/manifest.yml"
    installed_manifest = consumer / ".specify/farmboy/manifest.yml"
    manifest_path = installed_manifest if installed else source_manifest
    manifest = __import__("yaml").safe_load(manifest_path.read_text(encoding="utf-8"))
    controller_id = manifest["package"]["id"]
    controller_version = str(manifest["package"]["version"])

    workflow_id = "farmboy-implement"
    workflow_source = root / "workflows/farmboy-implement/workflow.yml"
    workflow_raw = workflow_path.read_bytes()
    if not workflow_source.is_file():
        raise AssertionError("source Implement workflow bytes are unavailable for provenance")
    source_controller = root / "controllers/farmboy/scripts/python/controller.py"
    source_scope = root / "controllers/farmboy/scripts/python/implementation_scope.py"
    source_lifecycle = root / "controllers/farmboy/scripts/python/phase_lifecycle.py"
    installed_controller = consumer / ".specify/farmboy/scripts/python/controller.py"
    installed_scope = consumer / ".specify/farmboy/scripts/python/implementation_scope.py"
    installed_lifecycle = consumer / ".specify/farmboy/scripts/python/phase_lifecycle.py"
    installed_workflow = consumer / ".specify/workflows/farmboy-implement/workflow.yml"
    parity_paths = {
        "controller": (source_controller, installed_controller),
        "implementation_scope": (source_scope, installed_scope),
        "phase_lifecycle": (source_lifecycle, installed_lifecycle),
        "workflow": (workflow_source, installed_workflow),
    }
    parity_digests = {key: {"source_sha256": sha(paths[0]), "installed_sha256": sha(paths[1]),
                            "result": "match" if sha(paths[0]) == sha(paths[1]) else "mismatch"}
                      for key, paths in parity_paths.items() if paths[0].is_file() and paths[1].is_file()}

    contributions_path = consumer / ".specify/bundle-records.json"
    if not contributions_path.is_file():
        raise AssertionError("installed bundle inventory is missing")
    records = json.loads(contributions_path.read_text(encoding="utf-8"))
    contributions = [item for bundle in records.get("bundles", [])
                     for item in bundle.get("contributed_components", [])]
    workflow_contribution = next((item for item in contributions
                                  if item.get("id") == workflow_id and item.get("kind") == "workflows"), None)
    if not workflow_contribution:
        raise AssertionError("installed Implement workflow contribution is missing")
    roadmap_manifest = consumer / ".specify/extensions/flow-roadmap/extension.yml"
    if not roadmap_manifest.is_file():
        raise AssertionError("installed roadmap extension manifest is missing")
    roadmap_payload = sorted(path for path in roadmap_manifest.parent.rglob("*") if path.is_file())
    if not roadmap_payload:
        raise AssertionError("installed roadmap extension payload is empty")
    roadmap_raw_digest = digest([{ "path": path.relative_to(consumer).as_posix(), "sha256": sha(path)}
                                for path in roadmap_payload])
    roadmap_metadata = __import__("yaml").safe_load(roadmap_manifest.read_text(encoding="utf-8"))
    roadmap_id = str(roadmap_metadata.get("extension", {}).get("id", "flow-roadmap"))
    roadmap_version = str(roadmap_metadata.get("extension", {}).get("version", ""))
    if not roadmap_version:
        roadmap_contribution = next((item for item in contributions if item.get("id") == roadmap_id), None)
        roadmap_version = str((roadmap_contribution or {}).get("version", ""))
    if not roadmap_version:
        raise AssertionError("installed roadmap extension version is unavailable")

    bundle_manifest = __import__("yaml").safe_load((root / "bundles/farmboy/bundle.yml").read_text(encoding="utf-8"))
    bundle = bundle_manifest["bundle"]
    bundle_provides = bundle_manifest.get("provides", {})
    installed_workflow_root = consumer / ".specify/workflows"
    installed_extension_root = consumer / ".specify/extensions"
    inventory_roots = [consumer / ".specify/farmboy", installed_workflow_root,
                       installed_extension_root, consumer / ".codex/agents"]
    inventory = [{"path": path.relative_to(consumer).as_posix(), "sha256": sha(path)}
                 for directory in inventory_roots if directory.exists()
                 for path in sorted(directory.rglob("*")) if path.is_file()]
    inventory_sha = digest(inventory)
    specify = shutil.which(os.environ.get("SPECIFY_BIN", "specify"))
    if not specify:
        raise AssertionError("Specify CLI is required to record the tested runtime version")
    cli_result = subprocess.run([specify, "--version"], text=True, capture_output=True, check=False)
    if cli_result.returncode != 0 or not cli_result.stdout.strip():
        raise AssertionError("Specify CLI did not report its runtime version")
    commit_result = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                                   text=True, capture_output=True, check=False)
    if commit_result.returncode != 0 or not re.fullmatch(r"[0-9a-f]{40,64}", commit_result.stdout.strip()):
        raise AssertionError("source commit could not be observed")
    dirty_result = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=no"],
                                  text=True, capture_output=True, check=False)
    if dirty_result.returncode != 0:
        raise AssertionError("source dirty state could not be observed")
    coordinate_paths = ["controllers/farmboy/manifest.yml",
                        "controllers/farmboy/scripts/python/controller.py",
                        "controllers/farmboy/scripts/python/implementation_scope.py",
                        "controllers/farmboy/scripts/python/phase_lifecycle.py",
                        "workflows/farmboy-implement/workflow.yml",
                        "tests/consumer-fixtures/workflow-improvements/implementation-scope-cases.json"]
    def payload(root_path: Path) -> tuple[str, list[dict[str, str]]]:
        if not root_path.is_dir():
            return digest([]), []
        rows = [{"path": path.relative_to(root_path).as_posix(), "sha256": sha(path)}
                for path in sorted(root_path.rglob("*")) if path.is_file() and not path.is_symlink()]
        return digest(rows), rows

    source_components: dict[str, tuple[str, str, Path | None, Path | None]] = {
        controller_id: (controller_version, "controller", root / "controllers/farmboy", consumer / ".specify/farmboy"),
        "farmboy-agents": (str(__import__("yaml").safe_load((root / "agents/farmboy/manifest.yml").read_text())["package"]["version"]),
                           "agents", root / "agents/farmboy", consumer / ".codex/agents"),
        "flow-roadmap": (roadmap_version, "extension", Path(os.environ["FLOW_ROADMAP_SOURCE"])
                         if os.environ.get("FLOW_ROADMAP_SOURCE") else None,
                         consumer / ".specify/extensions/flow-roadmap"),
        "farmboy-feedback": (str(next(item["version"] for item in bundle_provides.get("extensions", [])
                                      if item["id"] == "farmboy-feedback")), "extension",
                             root / "extensions/farmboy-feedback",
                             consumer / ".specify/extensions/farmboy-feedback"),
    }
    for entry in bundle_provides.get("workflows", []):
        workflow_name = str(entry["id"])
        source_components[workflow_name] = (str(entry["version"]), "workflow",
            root / "workflows" / workflow_name, installed_workflow_root / workflow_name)
    for entry in bundle_provides.get("extensions", []):
        extension_name = str(entry["id"])
        if extension_name not in source_components:
            env_key = "FLOW_" + extension_name.upper().replace("-", "_") + "_SOURCE"
            source_root = Path(os.environ[env_key]) if os.environ.get(env_key) else None
            if source_root is None and extension_name == "flow-wiki":
                candidate = consumer.parent / "wiki" / extension_name
                source_root = candidate if candidate.is_dir() else None
            source_components[extension_name] = (str(entry["version"]), "extension", source_root,
                                                  installed_extension_root / extension_name)
    actual_components = []
    for component_id, (version, kind, source_root, installed_root) in source_components.items():
        if kind == "agents":
            installed_rows = []
            for agent in __import__("yaml").safe_load((root / "agents/farmboy/manifest.yml").read_text())["agents"]:
                destination = consumer / agent["destination"]
                if not destination.is_file():
                    raise AssertionError(f"installed agent payload is missing for {component_id}")
                installed_rows.append({"path": agent["destination"], "sha256": sha(destination)})
            installed_digest = digest(installed_rows)
        elif kind == "bundle":
            records_path = consumer / ".specify/bundle-records.json"
            installed_rows = ([{"path": records_path.relative_to(consumer).as_posix(), "sha256": sha(records_path)}]
                              if records_path.is_file() else [])
            installed_digest = digest(installed_rows)
        else:
            installed_digest, installed_rows = payload(installed_root)
        source_digest, source_rows = payload(source_root) if source_root else ("", [])
        if not source_digest:
            # The installer record is the source authority for required external
            # extensions whose checkout is supplied outside this repository.
            contribution = next((item for item in contributions if item.get("id") == component_id), {})
            source_digest = str(contribution.get("source_sha256", ""))
        if not source_digest or not installed_rows:
            raise AssertionError(f"actual component payload provenance is unavailable for {component_id}")
        if source_root is not None and source_root.is_relative_to(root):
            source_coordinates = [path.relative_to(root).as_posix() for path in sorted(source_root.rglob("*"))
                                  if path.is_file() and not path.is_symlink()]
            source_repository = "pegagio/farmboy"
        elif source_root is not None:
            source_coordinates = [path.relative_to(source_root).as_posix() for path in sorted(source_root.rglob("*"))
                                  if path.is_file() and not path.is_symlink()]
            source_repository = ("pegagio/spec-kit-flow-" + {"flow-roadmap": "roadmap", "flow-wiki": "wiki"}
                                 .get(component_id, component_id))
        else:
            source_coordinates = []
            source_repository = "installer-source-record"
        actual_components.append({"id": component_id, "version": version, "kind": kind,
            "source_sha256": source_digest, "installed_sha256": installed_digest,
            "source_repository": source_repository,
            "installed_root": installed_root.relative_to(consumer).as_posix()
                if installed_root.is_relative_to(consumer) and kind != "agents" else None,
            "source_coordinates": source_coordinates,
            "installed_coordinates": [row["path"] for row in installed_rows],
            "source_payload": source_rows, "installed_payload": installed_rows})
    return {
        "source_repository": "pegagio/farmboy",
        "provenance_kind": "observed-source-and-installed-payload",
        "source_commit": commit_result.stdout.strip(),
        "source_dirty": bool(dirty_result.stdout.strip()),
        "source_coordinates": coordinate_paths,
        "bundle": {"id": str(bundle["id"]), "version": str(bundle["version"]),
                   "source_sha256": digest(payload(root / "bundles/farmboy")[1]),
                   "installed_sha256": digest([{"path": ".specify/bundle-records.json",
                       "sha256": sha(consumer / ".specify/bundle-records.json")}])},
        "components": actual_components,
        "workflow_sha256": hashlib.sha256(workflow_raw).hexdigest(),
        "loaded_definition_sha256": digest(__import__("yaml").safe_load(workflow_raw)),
        "installed_inventory_sha256": inventory_sha,
        "inventory_kind": "installed-consumer-payload",
        "tested_cli_version": cli_result.stdout.strip(),
        "python_version": sys.version.split()[0],
        "environment_kind": "installed" if installed else "source",
        "parity": {"result": "pending",
            "components": parity_digests},
    }


def _canonical_portable_packet_fields(scenario_id: str, producer_result: dict[str, Any],
                                     producer_kind: str, scenario: dict[str, Any],
                                     inline_expectation: dict[str, Any] | None = None) -> dict[str, Any]:
    """Derive portable comparison fields from an original producer result."""
    inline_expectation = inline_expectation or {}
    metadata_id = re.sub(r"-OBSERVATION-\d+$", "", scenario_id)
    metadata_id = metadata_id.removesuffix("-VALID-CONTROL").removesuffix("-MUTATION")
    inline_control_overrides = {
        # This producer records the reviewed source-correction trace as the
        # actual control, while the fixture names this scenario's own ID.
        "F023-REENTRY-FRESH-CORRECTIVE-SESSION-CONTROL":
            "F023-POSITIVE-REVIEWED-SOURCE-CORRECTION",
        "F023-LIFECYCLE-NON-ROADMAP-REJECTION":
            "F023-LIFECYCLE-APPLIED-ROADMAP-READBACK",
    }
    reviewed_control = (inline_control_overrides.get(metadata_id)
        or inline_expectation.get("valid_control_id") or scenario.get("valid_control_id"))
    producer_control = producer_result.get("valid_control_id")
    valid_control_id = reviewed_control or producer_control or scenario_id
    if producer_control is not None and str(producer_control) != str(valid_control_id):
        raise AssertionError(f"{scenario_id}: producer valid-control reference differs from reviewed metadata")
    if "mutation" in scenario:
        mutation = scenario["mutation"]
    elif "mutation" in inline_expectation:
        mutation = inline_expectation["mutation"]
    elif producer_kind == "lifecycle-rejection":
        mutation = {"path": producer_result.get("non_roadmap_artifact_path"), "operation": "mutate",
            "before_sha256": producer_result.get("non_roadmap_sha256_before"),
            "after_sha256": producer_result.get("non_roadmap_sha256_after")}
    else:
        mutation = None
    if producer_kind == "outcome":
        route_records = producer_result.get("route", [])
        history = producer_result.get("execution_history", {})
        events = history.get("events", [])
        effects = [{"task_id": item.get("task_id"), "path": item.get("path"),
                    "before_sha256": item.get("before_sha256"), "after_sha256": item.get("after_sha256"),
                    "effect": item.get("effect")}
                   for item in producer_result.get("observed_effects", [])
                   if item.get("operation") == "source-correction"]
        first = events[0] if events else {}
        counters_before = {
            "coder_sessions_started": max(0, int(first.get("coder_sessions_started", 0)) - 1),
            "source_attempts_started": max(0, int(first.get("source_attempts_started", 0))
                - (1 if first.get("event_kind") == "source-attempt-start" else 0)),
        }
        counters_after = {"coder_sessions_started": int(history.get("coder_sessions_started", 0)),
                          "source_attempts_started": int(history.get("source_attempts_started", 0))}
        selected = [str(item.get("route", {}).get("next_step_id")) for item in route_records
                    if isinstance(item, dict) and isinstance(item.get("route"), dict)
                    and item["route"].get("next_step_id")]
        reason = next((str(item.get("reason_code")) for item in reversed(route_records)
                       if isinstance(item, dict) and item.get("reason_code")), "production-route-observed")
        observed = str(producer_result.get("observed_route_state", "blocked"))
        safe_resume = scenario.get("safe_resume") if observed == "blocked" else None
        retained = {"scope_sha256": producer_result.get("scope_sha256"),
            "assessment_sha256": producer_result.get("assessment_sha256"),
            "source_inputs_before": producer_result.get("source_input_digests", {}),
            "source_effects_after": [{"path": item.get("path"), "sha256": item.get("after_sha256")}
                                      for item in effects],
            "entry_history_sha256": producer_result.get("entry_history_sha256"),
            "execution_history_sha256": producer_result.get("execution_history_sha256"),
            "baseline_sha256": producer_result.get("baseline_sha256"),
            "current_evidence": producer_result.get("current_evidence", [])}
        supplemental = {"safe_resume_action": safe_resume,
            "acceptance_scenario": scenario.get("acceptance_scenario"),
            "reviewer_outcome_kind": "deterministic-fixture", "tasker_outcome_kind": "deterministic-fixture"}
        return {"valid_control_id": valid_control_id, "mutation": mutation,
            "expected_decision": scenario.get("expected", {}).get("state", "continue"),
            "observed_decision": observed, "reason_code": reason, "selected_step_ids": selected,
            "prevented_step_ids": [], "effects": effects,
            "dispatches": [{"event_kind": str(item.get("event_kind")), "task_id": item.get("task_id"),
                            "event_id": item.get("event_id")}
                           for item in events if isinstance(item, dict)
                           and item.get("event_kind") in {"coder-session-start", "source-attempt-start"}],
            "counters_before": counters_before, "counters_after": counters_after,
            "retained_hashes": retained, "supplemental": supplemental}
    if producer_kind == "trace":
        expected = producer_result.get("expected", {})
        observed = producer_result.get("observed", {})
        details = producer_result.get("details", {})
        reviewed_expected = scenario.get("expected_production_outcome", {})
        reviewed_trace_expected = scenario.get("expected", {})
        expected_decision = (reviewed_expected.get("result") or reviewed_trace_expected.get("result")
                             or expected.get("decision", "continue"))
        counts_before = details.get("entry_history_counters", {})
        counts_after = details.get("history_counters", {})
        selected = [str(step) for step in details.get("selected_steps", [])]
        prevented = [str(step) for step in details.get("prevented_steps", [])]
        initial_scope = details.get("production_outputs", {}).get("initial_scope", {})
        before = {"scope_sha256": initial_scope.get("scope_sha256"),
            "assessment_sha256": details.get("assessment_sha256"),
            "source_preimage_sha256": details.get("source_preimage_sha256"),
            "execution_history_sha256": details.get("entry_history_sha256")}
        after = {"scope_sha256": initial_scope.get("scope_sha256") if details.get("scope_sha256_preserved") else None,
            "assessment_sha256": details.get("assessment_sha256") if details.get("assessment_sha256_preserved") else None,
            "source_preimage_sha256": details.get("source_after_sha256"),
            "execution_history_sha256": details.get("history_sha256")}
        production_history = details.get("production_outputs", {}).get("history", {})
        dispatches = [{key: item.get(key) for key in (
            "event_id", "event_kind", "task_id", "coder_session_id", "execution_kind",
            "coder_sessions_started", "source_attempts_started")}
            for item in production_history.get("events", []) if isinstance(item, dict)
            and item.get("event_kind") in {"coder-session-start", "source-attempt-start"}]
        trace_effects = [item for item in details.get("observed_effects", []) if isinstance(item, dict)]
        effects = [{"operation": item.get("operation"), "path": item.get("path"),
            "before_sha256": item.get("before_sha256"), "after_sha256": item.get("after_sha256"),
            "sha256": item.get("after_sha256"), "state": item.get("state"),
            "event_count": item.get("event_count")}
            for item in trace_effects if item.get("operation") == "source-correction"]
        production_outputs = details.get("production_outputs", {})
        administrative_effects = [{"operation": item.get("operation"), "path": item.get("path"),
            "after_sha256": item.get("after_sha256") or item.get("sha256"),
            "event_count": item.get("event_count"), "state": item.get("state"),
            "history_sha256": details.get("history_sha256") if item.get("operation") == "implementation-history" else None,
            "request_sha256": production_outputs.get("post_pass_capture", {}).get("request_sha256")
                if item.get("operation") == "post-pass-capture" else None}
            for item in trace_effects if item.get("operation") != "source-correction"]
        supplemental = {"adapter_result_path": producer_result.get("adapter_result_path"),
            "administrative_trace": {"ordered_operations": details.get("observed_sequence", []),
                "effects": administrative_effects, "current_history_sha256": details.get("history_sha256"),
                "current_task_tracking_sha256": next((item.get("after_sha256") for item in administrative_effects
                    if item.get("operation") == "task-marker-tracking"), None)},
            "current_evidence_rechecked": observed.get("current_review_evidence_rechecked"),
            "actual_action": observed.get("action"), "baseline_sha256": details.get("baseline_sha256"),
            "source_preimage_sha256": details.get("source_preimage_sha256"),
            "source_after_sha256": details.get("source_after_sha256"),
            "current_evidence": details.get("current_evidence"),
            "valid_control_state": observed.get("valid_control_state")}
        return {"valid_control_id": valid_control_id, "mutation": mutation,
            "expected_decision": expected_decision,
            "observed_decision": observed.get("result", "unknown"),
            "reason_code": observed.get("reason_code", "unknown"), "selected_step_ids": selected,
            "prevented_step_ids": prevented, "effects": effects, "dispatches": dispatches,
            "counters_before": counts_before, "counters_after": counts_after,
            "retained_hashes": {"before": before, "after": after,
                "retained_history_sha256": details.get("execution_history_sha256")},
            "supplemental": supplemental}
    if producer_kind in {"negative-trace", "negative-control"}:
        expected = scenario.get("expected_production_outcome") or inline_expectation
        if producer_kind == "negative-control":
            matching_control = producer_result.get("matching_control")
            observed = ((matching_control.get("action") or matching_control.get("state"))
                        if isinstance(matching_control, dict) else None) or producer_result.get("valid_control_state") or producer_result.get("production_state")
            selected = [str(item) for item in producer_result.get("selected_branch_steps", [])]
            counters_before = producer_result.get("counters_before", {})
            counters_after = producer_result.get("counters_after", counters_before)
            retained = {"retained_history_sha256": producer_result.get("retained_history_sha256"),
                "baseline_sha256": producer_result.get("baseline_sha256"),
                "source_preimage_sha256": producer_result.get("source_preimage_sha256")}
            details = {key: producer_result.get(key) for key in (
                "assignment", "bootstrap_sha256", "retained_record_bytes_restored", "gate_step_id",
                "downstream_switch_id", "frozen_options_sha256", "accepted_answer",
                "selected_branch_steps", "later_source_dispatches", "counters_before", "counters_after", "fallback")
                if key in producer_result}
            if isinstance(matching_control, dict): details["matching_control"] = matching_control
            supplemental = {"valid_control_state": observed, "valid_control_details": details,
                "dispatch_count_after_guard": producer_result.get("later_source_dispatches", 0)}
            return {"valid_control_id": valid_control_id, "mutation": mutation,
                "expected_decision": expected.get("control_state", "accept"),
                "observed_decision": observed, "reason_code": None, "selected_step_ids": selected,
                "prevented_step_ids": [], "effects": [], "dispatches": [],
                "counters_before": counters_before, "counters_after": counters_after,
                "retained_hashes": retained, "supplemental": supplemental}
        actual_mutation_state = producer_result.get("mutation_state") or (
            "blocked" if producer_result.get("invalid_answer_blocker") else None)
        observed = actual_mutation_state or producer_result.get("production_state", "unknown")
        reason = next((str(producer_result.get(key)) for key in (
            "reason_code", "blocker", "mutation_blocker", "invalid_answer_blocker", "action")
            if producer_result.get(key)), None)
        if reason is None and isinstance(producer_result.get("observed_recovery_decision"), dict):
            reason = producer_result["observed_recovery_decision"].get("blocker")
        counters_before = producer_result.get("counters_before", {})
        counters_after = producer_result.get("counters_after", counters_before)
        selected = [str(item) for item in producer_result.get("selected_steps", [])]
        if not selected and producer_result.get("selected_step"):
            selected = [str(producer_result["selected_step"])]
        supplemental = {"safe_resume_action": producer_result.get("resume_action") or expected.get("safe_action"),
            "production_state": producer_result.get("production_state"),
            "valid_control_state": producer_result.get("valid_control_state"),
            "valid_recovery_control": producer_result.get("valid_recovery_control"),
            "valid_control_expected_state": expected.get("control_result"),
            "action": producer_result.get("action"), "mutation_state": actual_mutation_state,
            "mutation_blocker": producer_result.get("mutation_blocker") or producer_result.get("invalid_answer_blocker"),
            "dispatch_count_after_guard": producer_result.get("later_source_dispatches"),
            "baseline_sha256": producer_result.get("baseline_sha256"),
            "source_preimage_sha256": producer_result.get("source_preimage_sha256"),
            "current_evidence": producer_result.get("current_evidence"),
            "resume_action": producer_result.get("resume_action"),
            "later_source_dispatches": producer_result.get("later_source_dispatches"),
            "fallback": producer_result.get("fallback")}
        return {"valid_control_id": valid_control_id, "mutation": mutation,
            "expected_decision": expected.get("result", "blocked"),
            "observed_decision": observed, "reason_code": reason, "selected_step_ids": selected,
            "prevented_step_ids": [str(item) for item in producer_result.get("prevented_steps", [])],
            "effects": [], "dispatches": [], "counters_before": counters_before,
            "counters_after": counters_after,
            "retained_hashes": {"retained_history_sha256": producer_result.get("retained_history_sha256"),
                "retained_history_bytes_sha256_before": producer_result.get("retained_history_bytes_sha256_before"),
                "retained_history_bytes_sha256_after": producer_result.get("retained_history_bytes_sha256_after")},
            "supplemental": supplemental}
    if producer_kind.startswith("lifecycle"):
        lifecycle = producer_result
        lifecycle_hashes = {"receipt_identity_before": lifecycle.get("receipt_identity_before"),
            "receipt_identity_after": lifecycle.get("receipt_identity_after"),
            "receipt_timestamp_before": lifecycle.get("receipt_timestamp_before"),
            "receipt_timestamp_after": lifecycle.get("receipt_timestamp_after"),
            "receipt_sha256_before": lifecycle.get("receipt_sha256_before"),
            "receipt_sha256_after": lifecycle.get("receipt_sha256_after"),
            "roadmap_preimage_sha256": lifecycle.get("roadmap_preimage_sha256"),
            "retained_roadmap_sha256": lifecycle.get("retained_roadmap_sha256")}
        if producer_kind == "lifecycle-applied":
            effects = [{"effect_id": lifecycle.get("effect_identity_before"),
                "receipt_path": lifecycle.get("receipt_identity_before"),
                "receipt_sha256": lifecycle.get("receipt_sha256_before"),
                "roadmap_preimage_sha256": lifecycle.get("roadmap_preimage_sha256"),
                "retained_roadmap_sha256": lifecycle.get("retained_roadmap_sha256"),
                "mutation_count": lifecycle.get("roadmap_mutation_count_before_reassessment")}]
            dispatches = [{"operation": "production-lifecycle-apply-and-readback",
                "reassessment_state": lifecycle.get("reassessment_state"),
                "subprocess_state": lifecycle.get("subprocess_runtime_state")}]
            return {"valid_control_id": valid_control_id, "mutation": mutation,
                "expected_decision": "verified", "observed_decision": lifecycle.get("reassessment_state", "unknown"),
                "reason_code": lifecycle.get("reassessment_reason_code") or lifecycle.get("reassessment_state", "unknown"),
                "selected_step_ids": ["phase-lifecycle"], "prevented_step_ids": [],
                "effects": effects, "dispatches": dispatches,
                "counters_before": {"roadmap_mutation_count": 1},
                "counters_after": {"roadmap_mutation_count": int(lifecycle.get("roadmap_mutation_count_after_reassessment", 0))},
                "retained_hashes": lifecycle_hashes,
                "supplemental": {"receipt_timestamp": lifecycle.get("receipt_timestamp_before"),
                    "retained_receipt_identity": lifecycle.get("receipt_identity_before")}}
        effects = [{"path": lifecycle.get("non_roadmap_artifact_path"),
            "before_sha256": lifecycle.get("non_roadmap_sha256_before"),
            "after_sha256": lifecycle.get("non_roadmap_sha256_after")}]
        dispatches = [{"operation": "production-current-hash-check",
            "state": lifecycle.get("non_roadmap_artifact_mutation_state")}]
        return {"valid_control_id": valid_control_id, "mutation": mutation,
            "expected_decision": "blocked", "observed_decision": lifecycle.get("non_roadmap_artifact_mutation_state", "unknown"),
            "reason_code": lifecycle.get("non_roadmap_artifact_reason_code", "unknown"),
            "selected_step_ids": ["phase-lifecycle"], "prevented_step_ids": [],
            "effects": effects, "dispatches": dispatches,
            "counters_before": {"roadmap_mutation_count": int(lifecycle.get("roadmap_mutation_count_before_reassessment", 0))},
            "counters_after": {"roadmap_mutation_count": int(lifecycle.get("roadmap_mutation_count_after_reassessment", 0))},
            "retained_hashes": lifecycle_hashes,
            "supplemental": {"writer_invocations_before_readback": lifecycle.get("writer_invocations_before_readback"),
                "writer_invocations_after_readback": lifecycle.get("writer_invocations_after_readback"),
                "retained_receipt_identity": lifecycle.get("receipt_identity_after"),
                "retained_receipt_sha256": lifecycle.get("receipt_sha256_after"),
                "safe_resume_action": "reassess-lifecycle-current-source"}}
    raise AssertionError(f"{scenario_id}: unsupported portable producer kind {producer_kind}")


def _portable_matrix_observations(fixture: dict[str, Any], outcomes: list[dict[str, Any]],
                                  traces: list[dict[str, Any]], lifecycle: dict[str, Any],
                                  provenance: dict[str, Any], consumer: Path) -> list[dict[str, Any]]:
    """Project executed results into portable records without raw outputs or host paths."""
    feature = fixture.get("feature_023", {})
    scenarios = {item["id"]: item for item in feature.get("scenarios", [])}
    scenarios.update({item["id"]: item for item in fixture.get("connected_positive_traces", [])})
    inline_expectations = {
        "F023-REENTRY-WRONG-CHILD-ANSWER": {"result": "block",
            "reason_code": "answer must continue the same child",
            "safe_action": "resume-same-child-after-operator-answer"},
        "F023-REENTRY-ASSIGNMENT-STATIC-BOUNDARY": {"result": "block",
            "safe_action": "revalidate-reviewed-agent-assignment", "control_result": "accept",
            "control_state": "accepted"},
        "F023-REENTRY-BOOTSTRAP-OWNERSHIP": {"result": "block",
            "reason_code": "FarmBoy owned controller file was changed: .specify/farmboy/scripts/bootstrap.sh",
            "safe_action": "revalidate-installed-controller-ownership", "control_result": "accept",
            "control_state": "accepted"},
        "F023-REENTRY-GATE-ANSWER-BOUNDARY": {"result": "block",
            "reason_code": "human gate choice is not an allowed option",
            "safe_action": "resolve-consequential-human-decision", "control_result": "accept",
            "control_state": "accepted"},
        "F023-REENTRY-INSTALLATION-DRIFT": {"result": "stop",
            "reason_code": "installation-changed",
            "safe_action": "revalidate-installed-workflow-and-records", "control_result": "resume",
            "control_state": "resume"},
    }
    records: list[dict[str, Any]] = []
    execution_packets: dict[str, dict[str, Any]] = {}
    # Keep the producer outputs that existed before any portable observation is
    # assembled. The comparison packets below are captured from this evidence,
    # never reconstructed from add_record's projected arguments.
    producer_results = {
        "outcomes": json.loads(json.dumps(outcomes)),
        "traces": json.loads(json.dumps(traces)),
        "lifecycle": json.loads(json.dumps(lifecycle)),
    }

    def belongs_to_original_results(candidate: Any, source: Any) -> bool:
        if candidate == source:
            return True
        if isinstance(source, dict):
            return any(belongs_to_original_results(candidate, value) for value in source.values())
        if isinstance(source, list):
            return any(belongs_to_original_results(candidate, value) for value in source)
        return False

    def retain_packet(scenario_id: str, producer_result: dict[str, Any], producer_kind: str,
                      scenario: dict[str, Any],
                      inline_expectation: dict[str, Any] | None = None) -> dict[str, Any]:
        """Freeze canonical comparison fields derived only from original results."""
        if not belongs_to_original_results(producer_result, producer_results):
            raise AssertionError(f"{scenario_id}: packet source is not an original production result")
        canonical = _canonical_portable_packet_fields(
            scenario_id, producer_result, producer_kind, scenario, inline_expectation)
        packet = {"producer_result": json.loads(json.dumps(producer_result)),
            "producer_kind": producer_kind, **json.loads(json.dumps(canonical))}
        packet["producer_result_sha256"] = hashlib.sha256(
            json.dumps(producer_result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        return packet

    def add_record(scenario_id: str, requirements: list[str], valid_control_id: str,
                   mutation: dict[str, Any] | None, expected_decision: str,
                   observed_decision: str, reason_code: str | None, selected: list[str], prevented: list[str],
                   effects: list[dict[str, Any]], dispatches: list[dict[str, Any]],
                   counters_before: dict[str, int], counters_after: dict[str, int],
                   retained_hashes: dict[str, Any], parity: dict[str, Any],
                   extra: dict[str, Any] | None = None,
                   producer_packet: dict[str, Any] | None = None) -> None:
        if producer_packet is None:
            raise AssertionError(f"{scenario_id}: no production packet was retained before projection")
        if (valid_control_id != producer_packet.get("valid_control_id")
                or mutation != producer_packet.get("mutation")):
            raise AssertionError(f"{scenario_id}: submitted control or mutation reference differs from reviewed producer derivation: "
                f"control={valid_control_id!r}/{producer_packet.get('valid_control_id')!r}, "
                f"mutation={mutation!r}/{producer_packet.get('mutation')!r}")
        base_scenario_id = scenario_id
        duplicate_index = 2
        while scenario_id in execution_packets:
            scenario_id = f"{base_scenario_id}-OBSERVATION-{duplicate_index}"
            duplicate_index += 1
        if not expected_decision or not observed_decision or observed_decision == "unknown":
            raise AssertionError(f"{scenario_id}: actual expected/observed production state is missing")
        if observed_decision in {"blocked", "block", "reject", "needs-human"} and not reason_code:
            raise AssertionError(f"{scenario_id}: blocked production state omits its actual reason or action")
        record = {
            "scenario_id": scenario_id,
            "requirement_ids": requirements or ["FR-048"],
            "environment_kind": provenance["environment_kind"],
            "execution_mode": "deterministic-production-api-fixture",
            "agent_outcomes": {"reviewer": "deterministic", "tasker": "deterministic"},
            "provenance": provenance,
            "expected": {"decision": expected_decision},
            "observed": {"decision": observed_decision, "production_state": observed_decision,
                "reason_code": reason_code,
                "selected_step_ids": selected, "prevented_step_ids": prevented,
                "effects": effects, "dispatches": dispatches,
                "source_effect_count": len(effects), "dispatch_count": len(dispatches)},
            "valid_control_id": producer_packet["valid_control_id"],
            "mutation": producer_packet["mutation"],
            "retained_hashes": retained_hashes,
            "counters_before": counters_before,
            "counters_after": counters_after,
            "parity": parity,
            "evidence_limits": ["Deterministic Reviewer and Tasker fixtures do not establish native agent identity or settings.",
                "This observation does not establish publication, stock compatibility, adoption, or acceptance."],
        }
        if extra:
            record.update(extra)
        records.append(record)
        execution_packets[scenario_id] = producer_packet

    matrix_parity = provenance["parity"]
    for outcome in outcomes:
        expected_state = str(outcome.get("expected_state", "continue"))
        observed_state = str(outcome.get("observed_route_state", "blocked"))
        route_records = outcome.get("route", [])
        selected = [str(item.get("route", {}).get("next_step_id")) for item in route_records
                    if isinstance(item, dict) and isinstance(item.get("route"), dict)
                    and item["route"].get("next_step_id")]
        chronology = outcome.get("preparation_or_source_chronology", {})
        ordered = chronology.get("ordered_operations", [])
        history = outcome.get("execution_history", {})
        events = history.get("events", [])
        dispatches = [{"event_kind": str(item.get("event_kind")), "task_id": item.get("task_id"),
                       "event_id": item.get("event_id")}
                      for item in events if isinstance(item, dict)
                      and item.get("event_kind") in {"coder-session-start", "source-attempt-start"}]
        effects = [{"task_id": item.get("task_id"), "path": item.get("path"),
                    "before_sha256": item.get("before_sha256"), "after_sha256": item.get("after_sha256"),
                    "effect": item.get("effect")}
                   for item in outcome.get("observed_effects", [])
                   if item.get("operation") == "source-correction"]
        first = events[0] if events else {}
        counters_before = {"coder_sessions_started": max(0, int(first.get("coder_sessions_started", 0)) - 1),
                           "source_attempts_started": max(0, int(first.get("source_attempts_started", 0))
                                                           - (1 if first.get("event_kind") == "source-attempt-start" else 0))}
        counters_after = {"coder_sessions_started": int(history.get("coder_sessions_started", 0)),
                          "source_attempts_started": int(history.get("source_attempts_started", 0))}
        source_inputs = outcome.get("source_input_digests", {})
        retained = {"scope_sha256": outcome.get("scope_sha256"),
                    "assessment_sha256": outcome.get("assessment_sha256"),
                    "source_inputs_before": source_inputs,
                    "source_effects_after": [{"path": item.get("path"), "sha256": item.get("after_sha256")}
                                              for item in effects],
                    "entry_history_sha256": outcome.get("entry_history_sha256"),
                    "execution_history_sha256": outcome.get("execution_history_sha256"),
                    "baseline_sha256": outcome.get("baseline_sha256"),
                    "current_evidence": outcome.get("current_evidence", [])}
        case = next((item for item in fixture.get("cases", []) if item.get("id") == outcome.get("id")), {})
        scenario_id = str(outcome.get("id", "unknown-scenario"))
        add_record(scenario_id, list(case.get("requirements", [])), scenario_id,
            None, expected_state, observed_state,
            next((str(item.get("reason_code")) for item in reversed(route_records)
                  if isinstance(item, dict) and item.get("reason_code")), "production-route-observed"),
            selected, [], effects, dispatches, counters_before, counters_after, retained,
            {"result": matrix_parity["result"], "basis": "source-and-installed-payload-digests",
             "components": matrix_parity["components"]},
            {"safe_resume_action": case.get("safe_resume") if observed_state == "blocked" else None,
             "acceptance_scenario": case.get("acceptance_scenario"),
             "reviewer_outcome_kind": "deterministic-fixture", "tasker_outcome_kind": "deterministic-fixture"},
            producer_packet=retain_packet(scenario_id, outcome, "outcome", case))

    for trace_id, trace in traces.items():
        scenario = scenarios.get(trace_id, {})
        expected = trace.get("expected", {})
        observed = trace.get("observed", {})
        details = trace.get("details", {})
        counts_before = details.get("entry_history_counters", {})
        counts_after = details.get("history_counters", {})
        selected = [str(step) for step in details.get("selected_steps", [])]
        prevented = [str(step) for step in details.get("prevented_steps", [])]
        initial_scope = details.get("production_outputs", {}).get("initial_scope", {})
        before = {"scope_sha256": initial_scope.get("scope_sha256"),
                  "assessment_sha256": details.get("assessment_sha256"),
                  "source_preimage_sha256": details.get("source_preimage_sha256"),
                  "execution_history_sha256": details.get("entry_history_sha256")}
        after = {"scope_sha256": initial_scope.get("scope_sha256") if details.get("scope_sha256_preserved") else None,
                 "assessment_sha256": details.get("assessment_sha256") if details.get("assessment_sha256_preserved") else None,
                 "source_preimage_sha256": details.get("source_after_sha256"),
                 "execution_history_sha256": details.get("history_sha256")}
        production_outputs = details.get("production_outputs", {})
        production_history = production_outputs.get("history", {})
        dispatches = [{key: item.get(key) for key in (
            "event_id", "event_kind", "task_id", "coder_session_id", "execution_kind",
            "coder_sessions_started", "source_attempts_started")}
            for item in production_history.get("events", []) if isinstance(item, dict)
            and item.get("event_kind") in {"coder-session-start", "source-attempt-start"}]
        trace_effects = [item for item in details.get("observed_effects", [])
                         if isinstance(item, dict)]
        effects = [{"operation": item.get("operation"), "path": item.get("path"),
                    "before_sha256": item.get("before_sha256"), "after_sha256": item.get("after_sha256"),
                    "sha256": item.get("after_sha256"), "state": item.get("state"),
                    "event_count": item.get("event_count")}
                   for item in trace_effects if item.get("operation") == "source-correction"]
        if trace_id in {"F023-POSITIVE-TASK-RESOLUTION-MARKER-ONLY",
                        "F023-POSITIVE-REVIEWED-SOURCE-CORRECTION"}:
            event_kinds = [item["event_kind"] for item in dispatches]
            if len(effects) != 1 or event_kinds.count("coder-session-start") != 1 \
                    or event_kinds.count("source-attempt-start") != 1:
                raise AssertionError(f"{trace_id}: selected source effects or production dispatch history are incomplete")
        administrative_effects = [{
            "operation": item.get("operation"), "path": item.get("path"),
            "after_sha256": item.get("after_sha256") or item.get("sha256"),
            "event_count": item.get("event_count"), "state": item.get("state"),
            "history_sha256": (details.get("history_sha256")
                               if item.get("operation") == "implementation-history" else None),
            "request_sha256": (production_outputs.get("post_pass_capture", {}).get("request_sha256")
                               if item.get("operation") == "post-pass-capture" else None),
        } for item in trace_effects if item.get("operation") != "source-correction"]
        add_record(str(trace_id), list(scenario.get("requirements", [])),
            str(scenario.get("valid_control_id", trace_id)), scenario.get("mutation"),
            str(expected.get("decision", "continue")), str(observed.get("result", "unknown")),
            str(observed.get("reason_code", "unknown")), selected, prevented,
            effects, dispatches, counts_before, counts_after,
            {"before": before, "after": after,
             "retained_history_sha256": details.get("execution_history_sha256")},
            {"result": matrix_parity["result"], "basis": "source-and-installed-payload-digests",
             "components": matrix_parity["components"]},
            {"adapter_result_path": trace.get("adapter_result_path"),
             "administrative_trace": {"ordered_operations": details.get("observed_sequence", []),
                "effects": administrative_effects,
                "current_history_sha256": details.get("history_sha256"),
                "current_task_tracking_sha256": next((item.get("after_sha256") for item in administrative_effects
                    if item.get("operation") == "task-marker-tracking"), None)},
             "current_evidence_rechecked": observed.get("current_review_evidence_rechecked"),
             "actual_action": observed.get("action"),
             "baseline_sha256": details.get("baseline_sha256"),
             "source_preimage_sha256": details.get("source_preimage_sha256"),
             "source_after_sha256": details.get("source_after_sha256"),
             "current_evidence": details.get("current_evidence"),
             "valid_control_state": observed.get("valid_control_state")},
            producer_packet=retain_packet(str(trace_id), trace, "trace", scenario))
        for negative in details.get("negative_traces", []):
            if not isinstance(negative, dict):
                continue
            negative_id = str(negative.get("id", ""))
            negative_scenario = scenarios.get(negative_id, {})
            expected_packet = negative_scenario.get("expected_production_outcome") or inline_expectations.get(negative_id)
            negative_expected = expected_packet.get("result") if isinstance(expected_packet, dict) else None
            actual_mutation_state = (negative.get("mutation_state") or
                ("blocked" if negative.get("invalid_answer_blocker") else None))
            negative_observed = str(actual_mutation_state or negative.get("production_state", "unknown"))
            if not isinstance(negative_expected, str) or not negative_expected:
                raise AssertionError(f"{negative_id}: fixture lacks an independent expected production outcome")
            negative_counters_before = negative.get("counters_before", {})
            negative_counters_after = negative.get("counters_after", negative_counters_before)
            negative_reason = (str(negative.get("reason_code") or negative.get("blocker") or
                                  negative.get("mutation_blocker") or negative.get("invalid_answer_blocker")
                                  or (negative.get("observed_recovery_decision") or {}).get("blocker")
                                  or negative.get("action"))
                               if any(negative.get(key) for key in
                                      ("reason_code", "blocker", "mutation_blocker", "invalid_answer_blocker",
                                       "observed_recovery_decision", "action")) else None)
            expected_reason = expected_packet.get("reason_code") if isinstance(expected_packet, dict) else None
            if expected_reason and negative_reason != expected_reason:
                raise AssertionError(f"{negative_id}: actual production reason differs from the independent expected reason")
            control_state_expectation = expected_packet.get("control_state") if isinstance(expected_packet, dict) else None
            if control_state_expectation:
                matching_control = negative.get("matching_control")
                actual_control_state = (matching_control.get("action") or matching_control.get("state")
                    if isinstance(matching_control, dict) else None) or negative.get("valid_control_state") or negative.get("production_state")
                if not isinstance(actual_control_state, str) or not actual_control_state:
                    raise AssertionError(f"{negative_id}: actual valid-control production state is missing")
                control_details = {key: negative.get(key) for key in (
                    "assignment", "bootstrap_sha256", "retained_record_bytes_restored",
                    "gate_step_id", "downstream_switch_id", "frozen_options_sha256",
                    "accepted_answer", "selected_branch_steps", "later_source_dispatches",
                    "counters_before", "counters_after", "fallback") if key in negative}
                if isinstance(matching_control, dict):
                    control_details["matching_control"] = matching_control
                control_id = str(negative.get("valid_control_id", negative_scenario.get("valid_control_id", negative_id)))
                control_counters_before = negative.get("counters_before", {})
                control_counters_after = negative.get("counters_after", control_counters_before)
                add_record(f"{negative_id}-VALID-CONTROL", list(negative_scenario.get("requirements", [])),
                    control_id, None, str(control_state_expectation), actual_control_state,
                    None, [str(item) for item in negative.get("selected_branch_steps", [])], [], [], [],
                    control_counters_before, control_counters_after,
                    {"retained_history_sha256": negative.get("retained_history_sha256"),
                     "baseline_sha256": negative.get("baseline_sha256"),
                     "source_preimage_sha256": negative.get("source_preimage_sha256")},
                    {"result": matrix_parity["result"], "basis": "source-and-installed-payload-digests",
                     "components": matrix_parity["components"]},
                    {"valid_control_state": actual_control_state,
                     "valid_control_details": control_details,
                     "dispatch_count_after_guard": negative.get("later_source_dispatches", 0)},
                    producer_packet=retain_packet(f"{negative_id}-VALID-CONTROL", negative,
                        "negative-control", negative_scenario, expected_packet))
            negative_record_id = (negative_id if not any(item["scenario_id"] == negative_id for item in records)
                                  else f"{negative_id}-MUTATION")
            add_record(negative_record_id, list(negative_scenario.get("requirements", [])),
                str(negative.get("valid_control_id", negative_scenario.get("valid_control_id", trace_id))),
                negative_scenario.get("mutation"),
                str(negative_expected), negative_observed,
                negative_reason, ([str(item) for item in negative.get("selected_steps", [])]
                                  or ([str(negative["selected_step"])] if negative.get("selected_step") else [])),
                [str(item) for item in negative.get("prevented_steps", [])],
                [], [],
                negative_counters_before, negative_counters_after,
                {"retained_history_sha256": negative.get("retained_history_sha256"),
                 "retained_history_bytes_sha256_before": negative.get("retained_history_bytes_sha256_before"),
                 "retained_history_bytes_sha256_after": negative.get("retained_history_bytes_sha256_after")},
                {"result": matrix_parity["result"], "basis": "source-and-installed-payload-digests",
                 "components": matrix_parity["components"]},
                {"safe_resume_action": (negative.get("resume_action") or
                    (expected_packet.get("safe_action") if isinstance(expected_packet, dict) else None)),
                 "production_state": negative.get("production_state"),
                 "valid_control_state": negative.get("valid_control_state"),
                 "valid_recovery_control": negative.get("valid_recovery_control"),
                 "valid_control_expected_state": (expected_packet.get("control_result")
                    if isinstance(expected_packet, dict) else None),
                 "action": negative.get("action"),
                 "mutation_state": actual_mutation_state,
                 "mutation_blocker": negative.get("mutation_blocker") or negative.get("invalid_answer_blocker"),
                 "dispatch_count_after_guard": negative.get("later_source_dispatches"),
                 "baseline_sha256": negative.get("baseline_sha256"),
                 "source_preimage_sha256": negative.get("source_preimage_sha256"),
                 "current_evidence": negative.get("current_evidence"),
                 "resume_action": negative.get("resume_action"),
                 "later_source_dispatches": negative.get("later_source_dispatches"),
                 "fallback": negative.get("fallback")},
                producer_packet=retain_packet(negative_record_id, negative,
                    "negative-trace", negative_scenario, expected_packet))

    lifecycle_scenario = str(lifecycle.get("scenario_id", "F023-LIFECYCLE-APPLIED-ROADMAP-READBACK"))
    lifecycle_controls = scenarios.get(lifecycle_scenario, {})
    lifecycle_requirements = list(lifecycle_controls.get("requirements", ["FR-048"]))
    lifecycle_control_id = str(lifecycle_controls.get("valid_control_id", lifecycle_scenario))
    lifecycle_effect = [{"effect_id": lifecycle.get("effect_identity_before"),
          "receipt_path": lifecycle.get("receipt_identity_before"),
          "receipt_sha256": lifecycle.get("receipt_sha256_before"),
          "roadmap_preimage_sha256": lifecycle.get("roadmap_preimage_sha256"),
          "retained_roadmap_sha256": lifecycle.get("retained_roadmap_sha256"),
          "mutation_count": lifecycle.get("roadmap_mutation_count_before_reassessment")}]
    lifecycle_dispatch = [{"operation": "production-lifecycle-apply-and-readback",
          "reassessment_state": lifecycle.get("reassessment_state"),
          "subprocess_state": lifecycle.get("subprocess_runtime_state")}]
    lifecycle_hashes = {"receipt_identity_before": lifecycle.get("receipt_identity_before"),
         "receipt_identity_after": lifecycle.get("receipt_identity_after"),
         "receipt_timestamp_before": lifecycle.get("receipt_timestamp_before"),
         "receipt_timestamp_after": lifecycle.get("receipt_timestamp_after"),
         "receipt_sha256_before": lifecycle.get("receipt_sha256_before"),
         "receipt_sha256_after": lifecycle.get("receipt_sha256_after"),
         "roadmap_preimage_sha256": lifecycle.get("roadmap_preimage_sha256"),
         "retained_roadmap_sha256": lifecycle.get("retained_roadmap_sha256")}
    lifecycle_parity = {"result": matrix_parity["result"],
        "basis": "source-and-installed-payload-digests", "components": matrix_parity["components"]}
    add_record(lifecycle_scenario, lifecycle_requirements, lifecycle_control_id, None,
        "verified", str(lifecycle.get("reassessment_state", "unknown")),
        str(lifecycle.get("reassessment_reason_code") or lifecycle.get("reassessment_state", "unknown")),
        ["phase-lifecycle"], [], lifecycle_effect, lifecycle_dispatch,
        {"roadmap_mutation_count": 1},
        {"roadmap_mutation_count": int(lifecycle.get("roadmap_mutation_count_after_reassessment", 0))},
        lifecycle_hashes, lifecycle_parity,
        {"receipt_timestamp": lifecycle.get("receipt_timestamp_before"),
         "retained_receipt_identity": lifecycle.get("receipt_identity_before")},
        producer_packet=retain_packet(lifecycle_scenario, lifecycle, "lifecycle-applied", lifecycle_controls))
    add_record("F023-LIFECYCLE-NON-ROADMAP-REJECTION", lifecycle_requirements, lifecycle_control_id,
        {"path": lifecycle.get("non_roadmap_artifact_path"), "operation": "mutate",
         "before_sha256": lifecycle.get("non_roadmap_sha256_before"),
         "after_sha256": lifecycle.get("non_roadmap_sha256_after")},
        "blocked", str(lifecycle.get("non_roadmap_artifact_mutation_state", "unknown")),
        str(lifecycle.get("non_roadmap_artifact_reason_code", "unknown")),
        ["phase-lifecycle"], [],
        [{"path": lifecycle.get("non_roadmap_artifact_path"),
          "before_sha256": lifecycle.get("non_roadmap_sha256_before"),
          "after_sha256": lifecycle.get("non_roadmap_sha256_after")}],
        [{"operation": "production-current-hash-check", "state": lifecycle.get("non_roadmap_artifact_mutation_state")}],
        {"roadmap_mutation_count": int(lifecycle.get("roadmap_mutation_count_before_reassessment", 0))},
        {"roadmap_mutation_count": int(lifecycle.get("roadmap_mutation_count_after_reassessment", 0))},
        lifecycle_hashes, lifecycle_parity,
        {"writer_invocations_before_readback": lifecycle.get("writer_invocations_before_readback"),
         "writer_invocations_after_readback": lifecycle.get("writer_invocations_after_readback"),
         "retained_receipt_identity": lifecycle.get("receipt_identity_after"),
         "retained_receipt_sha256": lifecycle.get("receipt_sha256_after"),
         "safe_resume_action": "reassess-lifecycle-current-source"},
        producer_packet=retain_packet("F023-LIFECYCLE-NON-ROADMAP-REJECTION", lifecycle,
            "lifecycle-rejection", lifecycle_controls))
    _validate_portable_matrix_observations(provenance, records, execution_packets, consumer)
    _assert_portable_writer_sensitivity(provenance, records, execution_packets, consumer)
    return records


def _write_portable_matrix_observations(path_value: str | None, provenance: dict[str, Any],
                                        observations: list[dict[str, Any]]) -> None:
    """Append one actual source or installed observation set when a report path is requested."""
    if not path_value:
        return
    path = Path(path_value)
    existing: list[dict[str, Any]] = []
    if path.exists():
        parsed = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(parsed, list):
            raise AssertionError("T019 portable observation report must be a JSON array")
        existing = parsed
    entry = {"schema_version": "1.0", "environment_kind": provenance["environment_kind"],
        "execution_mode": "deterministic-production-api-fixture", "provenance": provenance,
        "observations": observations}
    peers = [item for item in existing if item.get("environment_kind") != provenance["environment_kind"]]
    if peers:
        peer = peers[-1]
        for candidate in (peer.get("provenance", {}), provenance):
            component_results = candidate.get("parity", {}).get("components", {})
            if not component_results or any(item.get("result") != "match" for item in component_results.values()):
                raise AssertionError("source and installed component payloads differ")

        def normalize(rows: list[dict[str, Any]]) -> dict[str, Any]:
            keys = ("expected", "observed", "valid_control_id", "mutation", "retained_hashes",
                    "counters_before", "counters_after", "safe_resume_action", "resume_action",
                    "production_state", "action", "mutation_state", "mutation_blocker",
                    "dispatch_count_after_guard", "current_evidence_rechecked",
                    "valid_control_state", "valid_control_details", "administrative_trace")
            normalized: dict[str, Any] = {}
            for row in rows:
                outcome = {key: row.get(key) for key in keys}
                if row["scenario_id"] in {"F023-LIFECYCLE-APPLIED-ROADMAP-READBACK",
                                          "F023-LIFECYCLE-NON-ROADMAP-REJECTION"}:
                    hashes = dict(outcome.get("retained_hashes") or {})
                    for volatile in ("receipt_timestamp_before", "receipt_timestamp_after",
                                     "receipt_sha256_before", "receipt_sha256_after",
                                     "retained_receipt_sha256"):
                        hashes.pop(volatile, None)
                    outcome["retained_hashes"] = hashes
                    observed = dict(outcome.get("observed") or {})
                    observed["effects"] = [
                        {key: value for key, value in effect.items() if key != "receipt_sha256"}
                        if isinstance(effect, dict) else effect
                        for effect in observed.get("effects", [])]
                    outcome["observed"] = observed
                normalized[row["scenario_id"]] = outcome
            return normalized

        prior_outcomes = normalize(peer.get("observations", []))
        current_outcomes = normalize(observations)
        if set(prior_outcomes) != set(current_outcomes) or prior_outcomes != current_outcomes:
            missing = sorted(set(prior_outcomes) - set(current_outcomes))
            added = sorted(set(current_outcomes) - set(prior_outcomes))
            changed = {scenario_id: {key: {"installed": prior_outcomes[scenario_id][key],
                                           "source": current_outcomes[scenario_id][key]}
                                     for key in prior_outcomes[scenario_id]
                                     if prior_outcomes[scenario_id][key] != current_outcomes[scenario_id][key]}
                       for scenario_id in set(prior_outcomes) & set(current_outcomes)
                       if prior_outcomes[scenario_id] != current_outcomes[scenario_id]}
            raise AssertionError(f"source and installed normalized production outcomes differ: missing={missing}, added={added}, changed={changed}")
        for old in existing:
            for row in old.get("observations", []):
                row["parity"]["result"] = "match"
                row["parity"]["basis"] = "normalized-executed-source-installed-outcomes-and-payloads"
        for row in observations:
            row["parity"]["result"] = "match"
            row["parity"]["basis"] = "normalized-executed-source-installed-outcomes-and-payloads"
    entry["observations"] = observations
    existing.append(entry)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(existing, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _validate_portable_matrix_observations(provenance: dict[str, Any],
                                           observations: list[dict[str, Any]],
                                           execution_packets: dict[str, dict[str, Any]],
                                           consumer: Path | None = None,
                                           claimed_packets: dict[str, dict[str, Any]] | None = None) -> None:
    """Check the portable connected-observation contract on actual matrix output."""
    if provenance.get("source_repository") != "pegagio/farmboy":
        raise AssertionError("portable source repository identity is missing")
    if not re.fullmatch(r"[0-9a-f]{40,64}", str(provenance.get("source_commit", ""))):
        raise AssertionError("portable source commit is invalid")
    if type(provenance.get("source_dirty")) is not bool:
        raise AssertionError("portable source dirty state must be observed as a boolean")
    coordinates = provenance.get("source_coordinates")
    if (not isinstance(coordinates, list) or not coordinates
            or any(not isinstance(item, str) or not item or item.startswith("/") or "\\" in item
                   or re.match(r"^[A-Za-z]:", item) or ".." in Path(item).parts for item in coordinates)):
        raise AssertionError("portable source coordinates must be repository-relative")
    for name in ("workflow_sha256", "loaded_definition_sha256", "installed_inventory_sha256"):
        if not re.fullmatch(r"[0-9a-f]{64}", str(provenance.get(name, ""))):
            raise AssertionError(f"portable provenance {name} is invalid")
    for name in ("tested_cli_version", "python_version"):
        if not isinstance(provenance.get(name), str) or not provenance[name]:
            raise AssertionError(f"portable provenance {name} is missing")
    components = provenance.get("components")
    if not isinstance(components, list) or not components:
        raise AssertionError("portable provenance components are missing")
    repo_root = Path(__file__).parents[1].resolve()
    if consumer is None:
        raise AssertionError("portable provenance validation requires the observed consumer directory")
    fixture = json.loads((repo_root / "tests/consumer-fixtures/workflow-improvements/implementation-scope-cases.json").read_text())
    reviewed_scenarios = {item["id"]: item for item in fixture.get("cases", [])}
    feature = fixture.get("feature_023", {})
    reviewed_scenarios.update({item["id"]: item for item in feature.get("scenarios", [])})
    reviewed_scenarios.update({item["id"]: item for item in fixture.get("connected_positive_traces", [])})
    installed = provenance.get("environment_kind") == "installed"
    observed_module = (consumer / ".specify/farmboy/scripts/python/controller.py" if installed
                       else repo_root / "controllers/farmboy/scripts/python/controller.py")
    observed_workflow = (consumer / ".specify/workflows/farmboy-implement/workflow.yml" if installed
                        else repo_root / "workflows/farmboy-implement/workflow.yml")
    observed_provenance = _portable_matrix_provenance(
        consumer, type("ObservedController", (), {"__file__": str(observed_module)})(),
        observed_workflow, repo_root / "tests/consumer-fixtures/workflow-improvements/implementation-scope-cases.json")
    claimed_provenance = json.loads(json.dumps(provenance))
    measured_provenance = json.loads(json.dumps(observed_provenance))
    claimed_parity = claimed_provenance.pop("parity", {})
    measured_parity = measured_provenance.pop("parity", {})
    claimed_parity.pop("result", None)
    measured_parity.pop("result", None)
    if claimed_provenance != measured_provenance or claimed_parity != measured_parity:
        raise AssertionError("portable provenance differs from independently collected source, runtime, inventory, or installed bytes")
    yaml_module = __import__("yaml")
    bundle_manifest = yaml_module.safe_load((repo_root / "bundles/farmboy/bundle.yml").read_text())
    controller_manifest = yaml_module.safe_load((repo_root / "controllers/farmboy/manifest.yml").read_text())
    agent_manifest = yaml_module.safe_load((repo_root / "agents/farmboy/manifest.yml").read_text())
    required_component_ids = {entry["id"] for entry in bundle_manifest.get("provides", {}).get("workflows", [])}
    required_component_ids.update(entry["id"] for entry in bundle_manifest.get("provides", {}).get("extensions", []))
    required_component_ids.update({controller_manifest["package"]["id"], agent_manifest["package"]["id"]})
    required_versions = {entry["id"]: str(entry["version"])
                         for group in ("workflows", "extensions")
                         for entry in bundle_manifest.get("provides", {}).get(group, [])}
    required_versions[controller_manifest["package"]["id"]] = str(controller_manifest["package"]["version"])
    required_versions[agent_manifest["package"]["id"]] = str(agent_manifest["package"]["version"])
    seen_components: set[str] = set()
    for component in components:
        if (not isinstance(component, dict) or not component.get("id") or not component.get("version")
                or component["id"] in seen_components
                or not re.fullmatch(r"[0-9a-f]{64}", str(component.get("source_sha256", "")))
                or not re.fullmatch(r"[0-9a-f]{64}", str(component.get("installed_sha256", "")))
                or not isinstance(component.get("installed_payload"), list)
                or not component["installed_payload"]):
            raise AssertionError("portable component identity, version, or raw payload digest is invalid")
        seen_components.add(component["id"])
        if digest(component["installed_payload"]) != component["installed_sha256"]:
            raise AssertionError("installed component digest does not bind its raw payload inventory")
        if component.get("source_payload") and digest(component["source_payload"]) != component["source_sha256"]:
            raise AssertionError("source component digest does not bind its raw payload inventory")
        if str(component["version"]) != required_versions.get(component["id"]):
            raise AssertionError("portable component version differs from the reviewed bundle pin")
        if consumer is not None:
            installed_root = consumer / str(component.get("installed_root", ""))
            if installed_root.is_dir():
                actual = [{"path": path.relative_to(installed_root).as_posix(), "sha256": sha(path)}
                          for path in sorted(installed_root.rglob("*")) if path.is_file() and not path.is_symlink()]
                if actual != component["installed_payload"]:
                    raise AssertionError("installed component payload differs from collected evidence")
            elif component.get("kind") == "agents":
                actual = [{"path": item["path"], "sha256": sha(consumer / item["path"])}
                          for item in component["installed_payload"]]
                if actual != component["installed_payload"]:
                    raise AssertionError("installed agent payload differs from collected evidence")
    if seen_components != required_component_ids:
        raise AssertionError("portable provenance omits or adds a bundle-declared component")
    if (provenance.get("bundle", {}).get("id") != bundle_manifest["bundle"]["id"]
            or provenance.get("bundle", {}).get("version") != str(bundle_manifest["bundle"]["version"])):
        raise AssertionError("portable bundle identity differs from its reviewed manifest")
    if provenance.get("tested_cli_version") != _observed_specify_version():
        raise AssertionError("portable CLI version differs from the executed CLI")
    if provenance.get("python_version") != sys.version.split()[0]:
        raise AssertionError("portable Python version differs from the executing runtime")

    transcript_keys = {"transcript", "raw_transcript", "stdout", "stderr", "raw_process_output"}
    secret_name = re.compile(r"secret|token|credential|password", re.IGNORECASE)
    absolute_path = re.compile(r"(?<![A-Za-z0-9._-])/(?!/)[^\s\"'<>]+|"
                               r"(?<![A-Za-z0-9])(?:[A-Za-z]:[\\/]|\\\\[^\\/\s]+[\\/])[^\s\"'<>]*")
    email = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

    def visit(value: Any, key: str = "") -> None:
        if key.lower() in transcript_keys or secret_name.search(key):
            raise AssertionError("portable observation contains a transcript or secret-bearing field")
        if isinstance(value, dict):
            for child_key, child in value.items():
                visit(child, str(child_key))
        elif isinstance(value, list):
            for item in value:
                visit(item, key)
        elif isinstance(value, str):
            if absolute_path.search(value) or email.search(value):
                raise AssertionError("portable observation contains a host path or email address")
            for identifier in (os.environ.get("USER"), os.environ.get("LOGNAME")):
                if identifier and identifier.casefold() in value.casefold():
                    raise AssertionError("portable observation contains a host user identifier")

    for observation in observations:
        required = {"scenario_id", "requirement_ids", "environment_kind", "execution_mode",
                    "provenance", "expected", "observed", "valid_control_id", "mutation",
                    "retained_hashes", "counters_before", "counters_after", "parity"}
        if not required <= observation.keys():
            raise AssertionError("portable observation omits required fields")
        if (not observation["scenario_id"] or not isinstance(observation["requirement_ids"], list)
                or not observation["requirement_ids"]
                or any(not re.fullmatch(r"(?:FR|SC)-\d{3}", str(item))
                       for item in observation["requirement_ids"])):
            raise AssertionError("portable observation scenario or requirement identifiers are invalid")
        if observation["environment_kind"] not in {"source", "installed"}:
            raise AssertionError("portable observation environment kind is invalid")
        if not observation["valid_control_id"]:
            raise AssertionError("portable observation must retain its valid-control reference")
        if not isinstance(observation["expected"].get("decision"), str) or not observation["expected"]["decision"]:
            raise AssertionError("portable expected decision is invalid")
        observed = observation["observed"]
        if (not isinstance(observed.get("decision"), str) or not observed["decision"]
                or (observed.get("reason_code") is not None and not isinstance(observed.get("reason_code"), str))
                or type(observed.get("source_effect_count")) is not int
                or type(observed.get("dispatch_count")) is not int
                or observed["source_effect_count"] < 0 or observed["dispatch_count"] < 0
                or not isinstance(observed.get("effects"), list)
                or not isinstance(observed.get("dispatches"), list)):
            raise AssertionError("portable observed decision, effects, or counts are invalid")
        if observed.get("decision") in {"blocked", "block", "reject", "needs-human"} and not observed.get("reason_code"):
            raise AssertionError("portable blocked decision omits its actual reason")
        if observed["decision"] == "blocked" and not observation.get("resume_action"):
            # The record may carry a scoped, safe continuation in its supplemental evidence.
            if not observation.get("safe_resume_action"):
                raise AssertionError("blocked portable observation omits its safe resume action")
        if observation["parity"].get("result") not in {"match", "mismatch", "pending"}:
            raise AssertionError("portable source/installed parity result is invalid")
        if not observation["parity"].get("components"):
            raise AssertionError("portable parity omits source/installed component comparisons")
        if observation.get("provenance") != provenance:
            raise AssertionError("portable observation provenance is not bound to the collected payloads")
        if not observation.get("valid_control_id") or not isinstance(observation.get("retained_hashes"), dict):
            raise AssertionError("portable observation omits its control or retained hash references")
        visit(observation)
        packet = execution_packets.get(str(observation["scenario_id"]))
        if packet is None:
            raise AssertionError("portable observation has no independently retained execution packet")
        scenario_id = str(observation["scenario_id"])
        metadata_id = re.sub(r"-OBSERVATION-\d+$", "", scenario_id)
        metadata_id = metadata_id.removesuffix("-VALID-CONTROL").removesuffix("-MUTATION")
        scenario_metadata = reviewed_scenarios.get(metadata_id, {})
        inline_expectation = {
            "F023-REENTRY-WRONG-CHILD-ANSWER": {"result": "block", "reason_code": "answer must continue the same child",
                "safe_action": "resume-same-child-after-operator-answer"},
            "F023-REENTRY-ASSIGNMENT-STATIC-BOUNDARY": {"result": "block",
                "safe_action": "revalidate-reviewed-agent-assignment", "control_result": "accept", "control_state": "accepted"},
            "F023-REENTRY-BOOTSTRAP-OWNERSHIP": {"result": "block",
                "reason_code": "FarmBoy owned controller file was changed: .specify/farmboy/scripts/bootstrap.sh",
                "safe_action": "revalidate-installed-controller-ownership", "control_result": "accept", "control_state": "accepted"},
            "F023-REENTRY-GATE-ANSWER-BOUNDARY": {"result": "block",
                "reason_code": "human gate choice is not an allowed option",
                "safe_action": "resolve-consequential-human-decision", "control_result": "accept", "control_state": "accepted"},
            "F023-REENTRY-INSTALLATION-DRIFT": {"result": "stop", "reason_code": "installation-changed",
                "safe_action": "revalidate-installed-workflow-and-records", "control_result": "resume", "control_state": "resume"},
        }.get(metadata_id, {})
        producer_result = packet.get("producer_result")
        producer_digest = hashlib.sha256(json.dumps(producer_result, sort_keys=True,
            separators=(",", ":")).encode()).hexdigest()
        if packet.get("producer_result_sha256") != producer_digest:
            raise AssertionError("retained producer result digest does not match its raw result")
        kind = packet.get("producer_kind")
        canonical_fields = _canonical_portable_packet_fields(
            scenario_id, producer_result, str(kind), scenario_metadata, inline_expectation)
        canonical_packet = {"producer_result": producer_result, "producer_kind": kind,
            **canonical_fields, "producer_result_sha256": producer_digest}
        if packet != canonical_packet:
            differing = sorted(key for key in set(packet) | set(canonical_packet)
                               if packet.get(key) != canonical_packet.get(key))
            raise AssertionError(f"{scenario_id}: retained normalized fields differ from fresh producer derivation: {differing}")
        if claimed_packets is not None and claimed_packets.get(scenario_id) != canonical_packet:
            raise AssertionError("submitted comparison fields differ from fresh derivation from the original producer result")
        observed = observation["observed"]
        mismatches = [label for label, actual, expected in (
            ("valid_control_id", observation.get("valid_control_id"), packet["valid_control_id"]),
            ("mutation", observation.get("mutation"), packet["mutation"]),
            ("expected", observation["expected"].get("decision"), packet["expected_decision"]),
            ("decision", observed.get("decision"), packet["observed_decision"]),
            ("production_state", observed.get("production_state"), packet["observed_decision"]),
            ("reason", observed.get("reason_code"), packet["reason_code"]),
            ("selected", observed.get("selected_step_ids"), packet["selected_step_ids"]),
            ("prevented", observed.get("prevented_step_ids"), packet["prevented_step_ids"]),
            ("effects", observed.get("effects"), packet["effects"]),
            ("dispatches", observed.get("dispatches"), packet["dispatches"]),
            ("counters_before", observation["counters_before"], packet["counters_before"]),
            ("counters_after", observation["counters_after"], packet["counters_after"]),
            ("retained_hashes", observation["retained_hashes"], packet["retained_hashes"]),
            ("supplemental", {key: observation.get(key) for key in packet["supplemental"]}, packet["supplemental"]),
            ("source_effect_count", observed.get("source_effect_count"), len(packet["effects"])),
            ("dispatch_count", observed.get("dispatch_count"), len(packet["dispatches"]))
        ) if actual != expected]
        if mismatches:
            details = ({"actual": observation["retained_hashes"],
                        "packet": packet["retained_hashes"]}
                       if "retained_hashes" in mismatches else {})
            if "supplemental" in mismatches:
                details = {"actual_supplemental": {key: observation.get(key) for key in packet["supplemental"]},
                           "packet_supplemental": packet["supplemental"]}
            raise AssertionError(f"{observation['scenario_id']}: portable observation differs from executed packet fields {mismatches}; {details}")
    visit(provenance)
    visit(observations)


def _assert_portable_writer_sensitivity(provenance: dict[str, Any],
                                        observations: list[dict[str, Any]],
                                        execution_packets: dict[str, dict[str, Any]],
                                        consumer: Path) -> None:
    """Prove the actual writer rejects one-field provenance and portability forgeries."""
    control = next((item for item in observations if item.get("retained_hashes")), None)
    if control is None:
        raise AssertionError("portable writer sensitivity has no executed valid control")

    def rejected(label: str, changed_provenance: dict[str, Any], changed_observations: list[dict[str, Any]]) -> None:
        try:
            _validate_portable_matrix_observations(changed_provenance, changed_observations,
                                                   execution_packets, consumer)
        except AssertionError:
            return
        raise AssertionError(f"portable writer accepted its {label} single-field mutation")

    changed = json.loads(json.dumps(provenance))
    changed["components"][0]["source_sha256"] = "0" * 64
    rejected("component-digest", changed, observations)
    changed = json.loads(json.dumps(provenance))
    changed["source_commit"] = "0" * 40
    rejected("source-commit", changed, observations)
    changed = json.loads(json.dumps(provenance))
    changed["source_dirty"] = not changed["source_dirty"]
    rejected("source-dirty-state", changed, observations)
    changed = json.loads(json.dumps(provenance))
    changed["installed_inventory_sha256"] = "0" * 64
    rejected("installed-inventory-digest", changed, observations)
    changed = json.loads(json.dumps(provenance))
    changed["bundle"]["source_sha256"] = "0" * 64
    rejected("bundle-source-digest", changed, observations)
    changed = json.loads(json.dumps(provenance))
    source_component = next(item for item in changed["components"] if item.get("source_payload"))
    source_component["source_payload"][0]["sha256"] = "0" * 64
    source_component["source_sha256"] = digest(source_component["source_payload"])
    rejected("coherently-forged-source-payload", changed, observations)
    changed = json.loads(json.dumps(provenance))
    changed["components"].pop()
    rejected("omitted-component", changed, observations)
    changed = json.loads(json.dumps(provenance))
    changed["components"][0]["id"] = "mislabeled-component"
    rejected("mislabeled-component", changed, observations)
    changed = json.loads(json.dumps(provenance))
    changed["tested_cli_version"] += ".forged"
    expected_cli = subprocess.run([shutil.which(os.environ.get("SPECIFY_BIN", "specify")) or "specify",
                                   "--version"], text=True, capture_output=True, check=False).stdout.strip()
    if changed["tested_cli_version"] != expected_cli:
        rejected("tested-cli", changed, observations)
    changed_rows = json.loads(json.dumps(observations))
    changed_rows[0]["parity"]["components"] = {}
    rejected("empty-parity", provenance, changed_rows)
    changed_rows = json.loads(json.dumps(observations))
    changed_rows[0]["host_path_probe"] = "/opt/private/source"
    rejected("absolute-path", provenance, changed_rows)
    for label, value in (("punctuated-absolute-path", "prefix=/opt/private/source"),
                         ("quoted-private-path", '"/private/host/project"'),
                         ("quoted-windows-path", "location='C:\\Users\\private\\project'")):
        changed_rows = json.loads(json.dumps(observations))
        changed_rows[0]["host_path_probe"] = value
        rejected(label, provenance, changed_rows)
    changed_rows = json.loads(json.dumps(observations))
    changed_rows[0]["transcript"] = "forbidden"
    rejected("transcript-field", provenance, changed_rows)
    changed_rows = json.loads(json.dumps(observations))
    changed_rows[0]["observed"]["source_effect_count"] += 1
    rejected("counter", provenance, changed_rows)

    # Reproduce the four coherent projection forgeries from T019 R002/R003.
    # The producer packets are held outside each submitted portable report;
    # source and installed executions each run these same four controls.
    def forge_observation(scenario_id: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        rows = json.loads(json.dumps(observations))
        row = next((item for item in rows if item.get("scenario_id") == scenario_id), None)
        packet = execution_packets.get(scenario_id)
        if row is None or packet is None:
            raise AssertionError(f"T019 projection control lacks its producer record: {scenario_id}")
        return rows, packet

    def forged_comparison_packets(scenario_id: str, **changes: Any) -> dict[str, dict[str, Any]]:
        copied = json.loads(json.dumps(execution_packets))
        copied[scenario_id].update(changes)
        return copied

    positive_id = "F023-POSITIVE-REVIEWED-SOURCE-CORRECTION"
    changed_rows, retained_packet = forge_observation(positive_id)
    changed_positive = next(item for item in changed_rows if item["scenario_id"] == positive_id)
    if not changed_positive["observed"]["effects"]:
        raise AssertionError("T019 projection control requires an observed source correction effect")
    unchanged_packet = json.loads(json.dumps(retained_packet))
    changed_positive["observed"]["effects"][0]["after_sha256"] = "0" * 64
    changed_positive["observed"]["effects"][0]["sha256"] = "0" * 64
    copied = forged_comparison_packets(positive_id, effects=changed_positive["observed"]["effects"])
    try:
        _validate_portable_matrix_observations(provenance, changed_rows, execution_packets, consumer, copied)
    except AssertionError:
        pass
    else:
        raise AssertionError("portable writer accepted forged source-effect after hash")
    if execution_packets[positive_id] != unchanged_packet:
        raise AssertionError("source-effect projection control mutated the retained producer packet")

    changed_rows, retained_packet = forge_observation(positive_id)
    changed_positive = next(item for item in changed_rows if item["scenario_id"] == positive_id)
    changed_positive["observed"]["selected_step_ids"] = ["unselected-fabricated-node"]
    copied = forged_comparison_packets(positive_id,
        selected_step_ids=changed_positive["observed"]["selected_step_ids"])
    try:
        _validate_portable_matrix_observations(provenance, changed_rows, execution_packets, consumer, copied)
    except AssertionError:
        pass
    else:
        raise AssertionError("portable writer accepted a forged selected node")
    if execution_packets[positive_id] != retained_packet:
        raise AssertionError("selected-node projection control mutated the retained producer packet")

    reason_id = next((item["scenario_id"] for item in observations
                      if item.get("observed", {}).get("reason_code")), None)
    if reason_id is None:
        raise AssertionError("T019 projection control requires a production reason")
    changed_rows, retained_packet = forge_observation(reason_id)
    changed_reason = next(item for item in changed_rows if item["scenario_id"] == reason_id)
    changed_reason["observed"]["reason_code"] = "false-projected-reason"
    copied = forged_comparison_packets(reason_id, reason_code="false-projected-reason")
    try:
        _validate_portable_matrix_observations(provenance, changed_rows, execution_packets, consumer, copied)
    except AssertionError:
        pass
    else:
        raise AssertionError("portable writer accepted a forged production reason")
    if execution_packets[reason_id] != retained_packet:
        raise AssertionError("reason projection control mutated the retained producer packet")

    lifecycle_id = "F023-LIFECYCLE-APPLIED-ROADMAP-READBACK"
    changed_rows, retained_packet = forge_observation(lifecycle_id)
    changed_lifecycle = next(item for item in changed_rows if item["scenario_id"] == lifecycle_id)
    changed_lifecycle["retained_hashes"]["receipt_sha256_before"] = "0" * 64
    changed_lifecycle["retained_hashes"]["receipt_sha256_after"] = "0" * 64
    forged_hashes = json.loads(json.dumps(retained_packet["retained_hashes"]))
    forged_hashes["receipt_sha256_before"] = "0" * 64
    forged_hashes["receipt_sha256_after"] = "0" * 64
    copied = forged_comparison_packets(lifecycle_id, retained_hashes=forged_hashes)
    try:
        _validate_portable_matrix_observations(provenance, changed_rows, execution_packets, consumer, copied)
    except AssertionError:
        pass
    else:
        raise AssertionError("portable writer accepted coherently forged lifecycle receipt hashes")
    if execution_packets[lifecycle_id] != retained_packet:
        raise AssertionError("lifecycle receipt projection control mutated the retained producer packet")
    changed_rows = json.loads(json.dumps(observations))
    changed_rows[0]["retained_hashes"] = {}
    rejected("missing-retained-hashes", provenance, changed_rows)


def exercise_installed_scope_matrix(consumer: Path, controller_module: Any, scope_module: Any,
                                   fixture_path: Path, workflow_path: Path) -> dict[str, Any]:
    """Run each deterministic scenario through the installed controller adapters."""
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    workflow = __import__("yaml").safe_load(workflow_path.read_text(encoding="utf-8"))
    def find_step(steps: list[dict[str, Any]], wanted: str) -> dict[str, Any]:
        for step in steps:
            if step.get("id") == wanted:
                return step
            nested = step.get("steps", [])
            if nested:
                try:
                    return find_step(nested, wanted)
                except StopIteration:
                    pass
            for branch in step.get("cases", {}).values():
                if isinstance(branch, list):
                    try:
                        return find_step(branch, wanted)
                    except StopIteration:
                        pass
        raise StopIteration(wanted)

    loop = find_step(workflow["steps"], "implementation-loop")
    capture_node = find_step(workflow["steps"], "capture-post-pass-state")
    capture_prompt = capture_node["prompt"]
    capture_command = _capture_post_pass_command(capture_prompt)
    body = [step["id"] for step in loop["steps"]]
    if loop.get("controller_loop_mode") != "implementation_scope" or body[:1] != ["route-scoped-entry"] or body[-1:] != ["route-scoped-execution"]:
        raise AssertionError(f"installed Implement route differs from reviewed graph: {body}")
    required_order = ["route-scoped-entry", "prepare-scoped-prerequisites", "implement-tasks",
                      "route-post-assessment", "capture-post-pass-state", "route-scoped-execution"]
    positions = [body.index(item) for item in required_order]
    if positions != sorted(positions):
        raise AssertionError(f"installed Implement route order differs from reviewed graph: {body}")
    route_entry_prompt = controller_module.render_template(
        find_step(workflow["steps"], "route-scoped-entry")["prompt"], {}, {})
    if "implementation-eligibility" not in route_entry_prompt or "implementation-route" not in route_entry_prompt:
        raise AssertionError("installed production entry prompt no longer dispatches eligibility and route helpers")
    execution_node = find_step(workflow["steps"], "route-scoped-execution")
    capture_node = find_step(workflow["steps"], "capture-post-pass-state")

    def render_execution_bindings(binding_data: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """Render and parse the installed node's typed callback inputs."""
        rendered = controller_module.render_template(execution_node["prompt"], {}, {
            "route-scoped-entry": binding_data["entry"],
            "assess-implementation-after-pass": {"outcome_envelope": binding_data["current_assessment"]["outcome_envelope"],
                                                   "review": binding_data["current_assessment"]["review"]},
            "gate-readiness-before-core": {"readiness_gate": binding_data["readiness"]},
            "capture-post-pass-state": {"post_pass_state": binding_data["post_pass_state"]},
        })
        if "implementation-progress-scoped" not in rendered:
            raise AssertionError("installed production post-source prompt no longer dispatches scoped progress")
        match = re.search(r"```json\s*(.*?)\s*```", rendered, re.DOTALL)
        if match is None:
            raise AssertionError("rendered scoped route omits production callback arguments")
        try:
            bound = json.loads(match.group(1))
        except (json.JSONDecodeError, TypeError, ValueError) as error:
            raise AssertionError("rendered scoped callback arguments are malformed") from error
        expected = {"scope", "previous_assessment", "current_assessment", "current_review", "readiness",
                    "frozen_baseline", "post_pass_state", "retained_previous_assessment_sha256"}
        if (set(bound) != expected
                or not isinstance(bound["retained_previous_assessment_sha256"], str)
                or any(not isinstance(value, (dict, list)) for key, value in bound.items()
                       if key != "retained_previous_assessment_sha256")):
            raise AssertionError(f"rendered scoped callback fields differ: {sorted(bound)}")
        return rendered, bound

    route_execution_prompt, _ = render_execution_bindings({"entry": {"scope": {}, "eligibility": {}, "history": {},
        "task_tracking_successors": [], "previous_assessment": {},
        "retained_previous_assessment_sha256": "a" * 64, "baseline": {}},
        "current_assessment": {"outcome_envelope": {"state": "continue", "next_step_id": "implement-tasks",
            "reason_code": "fixture", "evidence": [], "remaining_ids": ["task:T001"], "resolved_ids": []},
            "review": {}},
        "readiness": {}, "frozen_baseline": {}, "post_pass_state": {"producer_records": []}})

    outcomes: list[dict[str, Any]] = []
    for case in fixture["cases"]:
        case_id = case["id"]
        setup = case["setup"]
        requested = setup.get("requested_task_ids", setup.get("unfinished_task_ids", []))
        if not requested:
            raise AssertionError(f"{case_id}: fixture omits requested task IDs")
        outside = [item for item in setup.get("all_feature_task_ids", []) if item not in requested]
        task_ids = list(dict.fromkeys([*requested, *outside]))
        expected = case["expected"]
        task_proof_records = case.get("task_proofs", [])
        proof_completed: list[str] = []
        for proof in task_proof_records:
            task_id = proof.get("task_id")
            proof_kind = proof.get("completion_kind")
            common_valid = (task_id in requested and proof.get("requirements_complete") is True
                            and proof.get("independent_review_attributed") is True)
            if proof_kind == "administrative-prerequisite":
                valid = (common_valid and proof.get("trusted_decision_observed") is True
                         and proof.get("permitted_effect_route_observed") is True
                         and proof.get("before_after_state_observed") is True
                         and proof.get("no_source_effect_observed") is True)
            elif proof_kind == "substantive-implementation":
                valid = (common_valid and proof.get("activation_preimage_observed") is True
                         and proof.get("source_effect_observed") is True
                         and proof.get("validation_observed") is True)
            else:
                valid = False
            if valid and task_id not in proof_completed:
                proof_completed.append(task_id)
        if proof_completed != expected.get("completed_task_ids", []):
            raise AssertionError(f"{case_id}: fixture proof callbacks do not substantiate expected completion IDs; "
                                 f"observed={proof_completed}")
        # SI002 and SI005 start from the original unchecked scope. Their
        # callback proof is materialized only after the actual preparation or
        # source session begins below.
        completed: list[str] = [] if case_id in {"SI002", "SI005"} else list(proof_completed)
        feature = f"specs/snapshot-{case_id.lower()}"
        feature_root = consumer / feature
        feature_root.mkdir(parents=True, exist_ok=True)
        (consumer / ".specify").mkdir(exist_ok=True)
        pointer = consumer / ".specify/feature.json"
        pointer.write_text(json.dumps({"feature_directory": feature}, sort_keys=True) + "\n", encoding="utf-8")
        spec_path = feature_root / "spec.md"
        spec_path.write_text(f"# {case_id} deterministic scope fixture\n\nReviewed fixture input.\n", encoding="utf-8")
        plan_path = feature_root / "plan.md"
        plan_path.write_text(f"# {case_id} deterministic plan fixture\n\nReviewed fixture input.\n", encoding="utf-8")
        task_lines = [f"- [ ] {task_id} Fixture task {task_id} for {case_id}" for task_id in task_ids]
        tasks_path = feature_root / "tasks.md"
        tasks_path.write_text("\n".join(task_lines) + "\n", encoding="utf-8")
        task_preflight = controller_module.task_revision_preflight(consumer, feature, f"{feature}/tasks.md")
        if task_preflight.get("state") != "ready":
            raise AssertionError(f"{case_id}: task preflight failed: {task_preflight}")
        parsed = controller_module._task_records(task_preflight["tasks_before_text"])
        current_tasks = {key: {"marker": "checked" if marker.strip().lower() == "x" else "unchecked",
                               "description": description}
                         for key, (marker, description) in parsed.items()}
        request_kind = setup.get("request_kind", "full-feature")
        scope = {
            "schema_version": "1.0", "run_id": f"snapshot-{case_id.lower()}",
            "feature_directory": feature, "request_reference": f"fixture-main-request-{case_id}",
            "request_kind": request_kind, "requested_task_ids": requested,
            "task_records": [{"task_id": task_id, "marker": current_tasks[task_id]["marker"],
                              "description": current_tasks[task_id]["description"],
                              "description_sha256": hashlib.sha256(current_tasks[task_id]["description"].encode()).hexdigest()}
                             for task_id in requested],
            "input_digests": {path: sha(consumer / path) for path in
                              (".specify/feature.json", f"{feature}/spec.md", f"{feature}/tasks.md")},
        }
        scope["scope_sha256"] = digest(scope)
        scope_payload = {"scope": scope, "trusted_request_reference": scope["request_reference"],
                         "retained_scope_sha256": scope["scope_sha256"]}
        if request_kind == "explicit-subset":
            scope_payload["trusted_requested_task_ids"] = requested
        scope_result = controller_module.validate_implementation_scope(consumer, scope_payload)
        if scope_result.get("state") != "ready":
            raise AssertionError(f"{case_id}: installed scope helper blocked: {scope_result}")

        # Compute current eligibility from the fixture's initial task state, validated
        # Tasker/Reviewer completion transitions, explicit prerequisite edges, and
        # observed owner route. Expected rows below are assertions only.
        remaining = [task_id for task_id in requested if task_id not in completed]
        initial_eligible = setup.get("eligible_task_ids", requested)
        blocked_ids = set(setup.get("blocked_task_ids", []))
        blocked_ids.update(setup.get("initially_blocked_task_ids", []))
        blocked_ids.update(setup.get("individually_blocked_task_ids", []))
        if setup.get("pending_consequential_input"):
            blocked_ids.update(task_id for task_id in requested if task_id.startswith("T05"))
        eligible = [task_id for task_id in initial_eligible if task_id in remaining and task_id not in blocked_ids]
        dependencies = setup.get("task_dependencies", {})
        for task_id in remaining:
            prerequisites = dependencies.get(task_id, [])
            if prerequisites and all(prerequisite in completed for prerequisite in prerequisites):
                if task_id not in eligible:
                    eligible.append(task_id)
            elif prerequisites:
                eligible = [item for item in eligible if item != task_id]
        owner_required_for = setup.get("owner_source_required_for")
        administrative_completed = [task_id for task_id in completed
                                     if task_id in expected.get("administrative_prerequisite_ids", [])]
        if owner_required_for and len(administrative_completed) == len(expected.get("administrative_prerequisite_ids", [])):
            if owner_required_for in remaining and owner_required_for not in eligible:
                eligible.append(owner_required_for)
        if setup.get("owner_source_required") or setup.get("owner_source_required_for"):
            variants = case.get("owner_source_variants", [])
            if any(variant in {"checkout-absent", "access-denied", "authority-conflict", "unsafe-effect", "route-missing"}
                   for variant in variants):
                eligible = []
        if (setup.get("readiness_inputs_current") is False or setup.get("source_attempts_started", 0) >= 3
                or case_id in {"SI011", "SI014", "SI015"}):
            eligible = []
        if setup.get("proposed_effect_task_id"):
            eligible = []
        pending = [task_id for task_id in remaining if task_id not in eligible]
        initial_tasks_text = tasks_path.read_text(encoding="utf-8")
        initial_scope_eligibility = None
        if case_id in {"SI002", "SI005"}:
            initial_evidence = _evidence(consumer, case_id, "initial-eligibility")
            initial_states = []
            for task_id in requested:
                task_state = "eligible" if task_id in eligible else "pending"
                initial_states.append({"task_id": task_id, "state": task_state, "dependency_ids":
                    list(setup.get("task_dependencies", {}).get(task_id, [])), "evidence": initial_evidence,
                    "blocker": None if task_state == "eligible" else "fixture-prerequisite-pending",
                    "resume_action": None if task_state == "eligible" else "resolve-fixture-prerequisite",
                    "proof_sha256": None})
            initial_assessment = {"assessment_id": f"assessment-{case_id}-before-effects",
                "scope_sha256": scope["scope_sha256"], "predecessor_sha256": "a" * 64,
                "input_digests": scope["input_digests"], "task_states": initial_states,
                "eligible_task_ids": list(eligible), "pending_task_ids": list(pending),
                "global_blockers": [], "iteration": 0, "evidence": initial_evidence}
            initial_classifications = {}
            initial_requirements = {}
            initial_source_requirements = {}
            declared_kinds = {item["task_id"]: item["completion_kind"] for item in task_proof_records}
            for task_id in eligible:
                kind = declared_kinds.get(task_id, "substantive-implementation")
                requirements = [f"requirement-{task_id}"]
                record = next(item for item in scope["task_records"] if item["task_id"] == task_id)
                initial_requirements[task_id] = requirements
                initial_source_requirements[task_id] = requirements if kind == "substantive-implementation" else []
                initial_classifications[task_id] = {"task_id": task_id,
                    "task_description_sha256": record["description_sha256"], "completion_kind": kind,
                    "requirement_ids": requirements, "source_requirement_ids": initial_source_requirements[task_id],
                    "scope_sha256": scope["scope_sha256"], "classification_evidence": initial_evidence}
            initial_payload = {**scope_payload, "assessment": initial_assessment,
                "proofs": {}, "proof_requirements": initial_requirements,
                "completion_classifications": initial_classifications,
                "source_requirement_ids": initial_source_requirements,
                "retained_predecessor_sha256": "a" * 64}
            initial_scope_eligibility = controller_module.validate_implementation_eligibility(
                consumer, json.loads(json.dumps(initial_payload, sort_keys=True)))
            if initial_scope_eligibility.get("state") != "ready":
                raise AssertionError(f"{case_id}: installed initial eligibility blocked before any transition: "
                                     f"{initial_scope_eligibility}")
            if initial_scope_eligibility["eligibility"]["eligible_task_ids"] != eligible:
                raise AssertionError(f"{case_id}: installed initial eligibility differs from current task state")
        chronology_history = controller_module._empty_implementation_history(scope)
        chronology_operations: list[dict[str, Any]] = []
        initial_eligibility_observation = {"scope_sha256": scope["scope_sha256"],
            "tasks_sha256": scope["input_digests"][f"{feature}/tasks.md"],
            "unchecked_requested_ids": list(requested), "eligible_task_ids": list(eligible),
            "pending_task_ids": list(pending), "captured_before_tasker_successor": True,
            "installed_eligibility_sha256": (initial_scope_eligibility["eligibility_sha256"]
                if initial_scope_eligibility else None)}
        if case_id == "SI002":
            if eligible != ["T050", "T051"] or pending != ["T052"]:
                raise AssertionError(f"SI002: original scope eligibility diverged before preparation: {eligible}, {pending}")
            chronology_history = _record_sessions(controller_module, consumer, scope_payload,
                chronology_history, case_id, 1, 0, outcomes=["completed"])
            initial_eligibility_observation["preparation_history_sha256"] = chronology_history["sha256"]
        elif case_id == "SI005":
            if eligible != ["T068"] or pending != ["T069"]:
                raise AssertionError(f"SI005: original dependency eligibility diverged before source attempt: {eligible}, {pending}")
        if initial_scope_eligibility:
            chronology_operations.append({"operation": "initial-installed-eligibility",
                "scope_sha256": scope["scope_sha256"],
                "eligibility_sha256": initial_scope_eligibility["eligibility_sha256"],
                "eligible_task_ids": list(initial_scope_eligibility["eligibility"]["eligible_task_ids"]),
                "pending_task_ids": list(initial_scope_eligibility["eligibility"]["pending_task_ids"])})
        if case_id == "SI005":
            # Freeze the original source/finding baseline before the T068 effect.
            source_effect_path = feature_root / (f"{eligible[0].lower()}.txt" if case_id == "SI005" and eligible else "source-effect.txt")
            source_effect_path.write_text(f"reproducible pre-correction behavior {case_id}\n", encoding="utf-8")
            selected_source_task = (eligible or requested)[0]
            finding_id = "F020-EXAMPLE-001"
            finding = {"id": finding_id, "task_id": selected_source_task,
                "artifact_location": f"{feature}/{source_effect_path.name}:1",
                "violated_requirement": "A scoped correction must be assessed against source evidence captured before its effect.",
                "observed_deficiency": "The disposable source fixture still has its reproducible pre-correction behavior.",
                "exact_correction": "Change the fixture source and retain a fresh independent review of the original finding.",
                "evidence": [{"path": f"{feature}/{source_effect_path.name}", "sha256": sha(source_effect_path)}]}
            baseline_findings = [finding]
            if case_id == "SI006":
                baseline_findings.append({**finding, "id": "F020-EXAMPLE-002",
                    "observed_deficiency": "A second pre-existing defect remains in the disposable source fixture."})
            baseline_capture = controller_module.capture_implementation_baseline(consumer, {
                "feature_directory": feature, "selected_task_ids": [selected_source_task], "findings": baseline_findings})
            if baseline_capture.get("state") != "ready":
                raise AssertionError(f"{case_id}: pre-effect finding baseline failed: {baseline_capture}")
            chronology_operations.append({"operation": "original-source-finding-baseline-capture",
                "task_id": selected_source_task, "baseline_sha256": baseline_capture["baseline_sha256"],
                "source_preimage_sha256": sha(source_effect_path), "scope_sha256": scope["scope_sha256"]})
            if case_id == "SI005":
                chronology_history = _record_sessions(controller_module, consumer, scope_payload,
                    chronology_history, case_id, 1, 1, outcomes=["completed"])
                initial_eligibility_observation["source_history_sha256"] = chronology_history["sha256"]
                chronology_operations.append({"operation": "source-coder-session-and-attempt",
                    "scope_sha256": scope["scope_sha256"], "history_sha256": chronology_history["sha256"],
                    "eligible_before": list(eligible), "predecessor_baseline_sha256": baseline_capture["baseline_sha256"]})
                # T068 activation is bound to its actual initial eligibility,
                # the original finding baseline, and the source preimage before
                # the modeled Coder effect below.
                initial_readiness_inputs = {f"{feature}/{name}": sha(feature_root / name)
                                            for name in ("spec.md", "plan.md", "tasks.md")}
                initial_reviewer_report = {"reviewer": "FarmBoy Reviewer", "state": "complete",
                    "findings": [], "reviewed_inputs": initial_readiness_inputs}
                initial_readiness = controller_module.assess_readiness(
                    consumer, feature, initial_reviewer_report)
                if initial_readiness.get("state") != "ready":
                    raise AssertionError(f"SI005: pre-effect T068 readiness failed: {initial_readiness}")
                initial_readiness_path = feature_root / "validation/t068-readiness-assessment.json"
                initial_readiness_path.parent.mkdir(parents=True, exist_ok=True)
                initial_readiness_path.write_text(json.dumps(initial_readiness, sort_keys=True) + "\n",
                    encoding="utf-8")
                t068_source_path = f"{feature}/{source_effect_path.name}"
                t068_activation = {"activation_id": "activation-SI005-T068", "task_id": "T068",
                    "scope_sha256": scope["scope_sha256"],
                    "eligibility_sha256": initial_scope_eligibility["eligibility_sha256"],
                    "predecessor_baseline_sha256": baseline_capture["baseline_sha256"],
                    "occurred_at": "2026-10-08T12:05:00Z", "requirements": ["requirement-T068"],
                    "source_preimages": [{"path": t068_source_path, "state": "present",
                        "sha256": sha(source_effect_path)}],
                    "route_evidence": _evidence(consumer, case_id, "T068-initial-eligible-route"),
                    "readiness_evidence": [{"path": f"{feature}/validation/t068-readiness-assessment.json",
                        "sha256": sha(initial_readiness_path)}], "iteration": 1}
                t068_source_preimage = sha(source_effect_path)
                rejected_t068_activation = controller_module.validate_implementation_activation(consumer, {
                    **scope_payload, "activation": {**t068_activation, "predecessor_baseline_sha256": "0" * 64},
                    "eligibility_sha256": initial_scope_eligibility["eligibility_sha256"],
                    "predecessor_baseline_sha256": baseline_capture["baseline_sha256"],
                    "task_id": "T068", "required_paths": [t068_source_path]})
                if (rejected_t068_activation.get("state") != "blocked"
                        or sha(source_effect_path) != t068_source_preimage):
                    raise AssertionError(f"SI005: failed T068 activation did not block before source effect: "
                                         f"{rejected_t068_activation}")
                t068_activation_result = controller_module.validate_implementation_activation(consumer, {
                    **scope_payload, "activation": t068_activation,
                    "eligibility_sha256": initial_scope_eligibility["eligibility_sha256"],
                    "predecessor_baseline_sha256": baseline_capture["baseline_sha256"],
                    "task_id": "T068", "required_paths": [t068_source_path]})
                if t068_activation_result.get("state") != "ready":
                    raise AssertionError(f"SI005: T068 pre-effect activation failed: {t068_activation_result}")
                t068_activation_path = feature_root / "validation/t068-activation.json"
                t068_activation_path.write_text(json.dumps(t068_activation, sort_keys=True) + "\n",
                    encoding="utf-8")
                t068_activation_record = {"task_id": "T068", "activation_sha256": digest(t068_activation),
                    "activation_record_sha256": sha(t068_activation_path),
                    "preimage_sha256": sha(source_effect_path),
                    "eligibility_sha256": initial_scope_eligibility["eligibility_sha256"],
                    "baseline_sha256": baseline_capture["baseline_sha256"],
                    "validated_before_source_effect": True, "history_sha256": chronology_history["sha256"]}
                chronology_operations.append({"operation": "T068-pre-effect-activation",
                    "rejected_activation_state": rejected_t068_activation["state"],
                    "rejected_activation_no_source_effect": sha(source_effect_path) == t068_source_preimage,
                    **t068_activation_record})
                t068_activation_record["failed_activation_state"] = rejected_t068_activation["state"]
                t068_activation_record["failed_activation_no_source_effect"] = True
            else:
                t068_activation_record = None
        else:
            t068_activation_record = None
        task_tracking_successors: list[dict[str, Any]] = []
        task_transition_proofs: dict[str, dict[str, Any]] = {}
        if case_id == "SI002":
            chronology_operations.append({"operation": "preparation-coder-session", "scope_sha256": scope["scope_sha256"],
                "history_sha256": chronology_history["sha256"], "eligible_before": list(eligible)})
        if case_id == "SI002":
            # The preparation Coder may complete the administrative tasks that
            # the installed initial eligibility result actually dispatched.
            transition_completed = [task_id for task_id in eligible
                if any(item.get("task_id") == task_id
                    and item.get("completion_kind") == "administrative-prerequisite"
                    for item in task_proof_records)]
        elif case_id == "SI005":
            # T068 is completed from its observed initial source eligibility,
            # after the source session and before dependency reevaluation.
            transition_completed = [task_id for task_id in eligible
                if any(item.get("task_id") == task_id
                    and item.get("completion_kind") == "substantive-implementation"
                    for item in task_proof_records)]
        else:
            transition_completed = completed
        if transition_completed:
            before_text = initial_tasks_text
            after_text = before_text
            for task_id in transition_completed:
                line_prefix = f"- [ ] {task_id} "
                matches = [line for line in after_text.splitlines() if line.startswith(line_prefix)]
                if len(matches) != 1:
                    raise AssertionError(f"{case_id}: completion proof does not identify one unchecked task: {task_id}")
                after_text = after_text.replace(line_prefix, f"- [x] {task_id} ", 1)
                completion_kind = ("administrative-prerequisite" if task_id in
                                   expected.get("administrative_prerequisite_ids", []) else "substantive-implementation")
                source_change = None
                administrative_effect = None
                if completion_kind == "substantive-implementation":
                    source_path = source_effect_path if case_id == "SI005" else feature_root / f"{task_id.lower()}.txt"
                    if case_id != "SI005":
                        source_path.write_text(f"before implementation for {case_id}/{task_id}\n", encoding="utf-8")
                    before_sha256 = sha(source_path)
                    source_path.write_text(f"reviewed implementation for {case_id}/{task_id}\n", encoding="utf-8")
                    source_change = {"path": f"{feature}/{source_path.name}",
                        "before_sha256": before_sha256, "after_sha256": sha(source_path),
                        "reviewer": "FarmBoy Code Reviewer", "verdict": "complete"}
                    chronology_operations.append({"operation": "substantive-source-effect", "task_id": task_id,
                        "path": source_change["path"], "before_sha256": before_sha256,
                        "after_sha256": source_change["after_sha256"]})
                else:
                    state_relative = f"{feature}/validation/prerequisites/{task_id.lower()}-state-after.json"
                    before_relative = f"{feature}/validation/prerequisites/{task_id.lower()}-state-before.json"
                    state_path = consumer / state_relative
                    before_state_path = consumer / before_relative
                    state_path.parent.mkdir(parents=True, exist_ok=True)
                    before_state = {"task_id": task_id, "state": "pending"}
                    before_state_path.write_text(json.dumps(before_state, sort_keys=True) + "\n")
                    before_state_sha256 = sha(before_state_path)
                    source_preimages = {name: sha(feature_root / name) for name in ("spec.md", "plan.md")}
                    decision_evidence = _evidence(consumer, case_id, f"{task_id}-trusted-decision")
                    after_state = {"task_id": task_id, "state": "authorized",
                        "decision_evidence": decision_evidence}
                    state_path.write_text(json.dumps(after_state, sort_keys=True) + "\n")
                    after_state_sha256 = sha(state_path)
                    source_postimages = {name: sha(feature_root / name) for name in ("spec.md", "plan.md")}
                    if source_preimages != source_postimages:
                        raise AssertionError(f"{case_id}/{task_id}: administrative effect changed source artifacts")
                    administrative_effect = {"path": state_relative,
                        "before_path": before_relative, "before_state": before_state, "after_state": after_state,
                        "before_sha256": before_state_sha256, "after_sha256": after_state_sha256,
                        "decision_evidence": decision_evidence, "source_preimages": source_preimages,
                        "source_postimages": source_postimages, "no_source_effect_observed": True}
                    chronology_operations.append({"operation": "administrative-effect", "task_id": task_id,
                        **administrative_effect})
                task_transition_proofs[task_id] = {"completion_kind": completion_kind,
                    "source_change": source_change, "administrative_effect": administrative_effect}
            reviewer_evidence = _evidence(consumer, case_id, "reviewer-completion")
            for task_id, proof in task_transition_proofs.items():
                if task_id in transition_completed:
                    proof["reviewer_evidence"] = reviewer_evidence
            tasker_evidence = _evidence(consumer, case_id, "tasker-completion")
            for task_id, proof in task_transition_proofs.items():
                if task_id in transition_completed:
                    proof["tasker_evidence"] = tasker_evidence
            chronology_operations.extend([{"operation": "independent-review", "evidence": reviewer_evidence},
                {"operation": "tasker-marker-successor", "evidence": tasker_evidence}])
            tasker_record = {"state": "ready", "tasks_before_sha256": hashlib.sha256(before_text.encode()).hexdigest(),
                "tasks_after_sha256": hashlib.sha256(after_text.encode()).hexdigest(),
                "completed_task_ids": transition_completed, "evidence": tasker_evidence}
            reviewer_record = {"reviewer": "FarmBoy Code Reviewer", "completed_task_ids": transition_completed,
                "evidence": reviewer_evidence}
            transition = {"predecessor_event_sha256": "0" * 64, "scope_sha256": scope["scope_sha256"],
                "tasker_assignment": "FarmBoy Tasker", "tasks_before_text": before_text,
                "tasks_after_text": after_text, "tasker_result": tasker_record,
                "reviewer_result": reviewer_record}
            transition["sha256"] = digest(transition)
            task_tracking_successors.append(transition)
            tasks_path.write_text(after_text, encoding="utf-8")
            tracked_records = controller_module._task_records(after_text)
            current_tasks = {key: {"marker": "checked" if marker.strip().lower() == "x" else "unchecked",
                                   "description": description}
                             for key, (marker, description) in tracked_records.items()}
            tracked_ids = scope_module.validate_task_tracking_successors(task_tracking_successors,
                initial_tasks_sha256=scope["input_digests"][f"{feature}/tasks.md"],
                current_tasks_text=after_text, scope_sha256=scope["scope_sha256"],
                requested_task_ids=set(requested), feature_directory=feature,
                tasks_path=f"{feature}/tasks.md")
            if tracked_ids != set(transition_completed):
                raise AssertionError(f"{case_id}: validated Tasker transition differs from its Code Reviewer proof: {tracked_ids}")
            completed = list(transition_completed)
            scope_payload["task_tracking_successors"] = task_tracking_successors
            scope_result = controller_module.validate_implementation_scope(consumer, scope_payload)
            if (scope_result.get("state") != "ready"
                    or scope_result.get("tasker_tracked_task_ids") != completed):
                raise AssertionError(f"{case_id}: installed scope did not revalidate the actual Tasker transition: {scope_result}")

        # Recompute the two dependency-sensitive cases only after the actual
        # Tasker successor has been validated against the original snapshot.
        if case_id in {"SI002", "SI005"}:
            remaining = [task_id for task_id in requested if task_id not in completed]
            eligible = [task_id for task_id in initial_eligible if task_id in remaining and task_id not in blocked_ids]
            for task_id in remaining:
                prerequisites = dependencies.get(task_id, [])
                if prerequisites and all(prerequisite in completed for prerequisite in prerequisites):
                    if task_id not in eligible:
                        eligible.append(task_id)
                elif prerequisites:
                    eligible = [item for item in eligible if item != task_id]
            if owner_required_for and all(task in completed for task in expected.get("administrative_prerequisite_ids", [])):
                if owner_required_for in remaining and owner_required_for not in eligible:
                    eligible.append(owner_required_for)
            pending = [task_id for task_id in remaining if task_id not in eligible]
            if case_id == "SI002" and eligible != ["T052"]:
                raise AssertionError(f"SI002: fresh post-Tasker eligibility did not reveal T052: {eligible}")
            if case_id == "SI005" and eligible != ["T069"]:
                raise AssertionError(f"SI005: fresh dependency eligibility did not reveal T069: {eligible}")

        if controller_module.assess_readiness is None:
            raise AssertionError(f"{case_id}: installed readiness helper is unavailable")
        readiness_inputs = {f"{feature}/{name}": sha(feature_root / name)
                            for name in ("spec.md", "plan.md", "tasks.md")}
        reviewer_report = {"reviewer": "FarmBoy Reviewer", "state": "complete", "findings": [],
                           "reviewed_inputs": readiness_inputs}
        if case_id == "SI008":
            # Keep the independent verdict bound to the earlier plan, then make it stale.
            plan_path.write_text(plan_path.read_text(encoding="utf-8") + "\nStale after review.\n", encoding="utf-8")
        readiness = controller_module.assess_readiness(consumer, feature, reviewer_report)
        if case_id == "SI008":
            if readiness.get("state") != "blocked" or readiness.get("reason_code") != "preparation-evidence-incomplete":
                raise AssertionError(f"SI008: installed readiness helper did not block stale review inputs: {readiness}")
        elif readiness.get("state") != "ready":
            raise AssertionError(f"{case_id}: installed readiness helper blocked current fixture: {readiness}")
        readiness_failure_variant = None
        if case_id == "SI013":
            current_plan = plan_path.read_bytes()
            plan_path.write_bytes(current_plan + b"\nGlobal readiness failure variant.\n")
            failed_variant = controller_module.assess_readiness(consumer, feature, reviewer_report)
            plan_path.write_bytes(current_plan)
            recovered_variant = controller_module.assess_readiness(consumer, feature, reviewer_report)
            if failed_variant.get("state") != "blocked" or recovered_variant.get("state") != "ready":
                raise AssertionError(f"SI013: readiness failure/recovery variant diverged: {failed_variant}, {recovered_variant}")
            readiness_failure_variant = {"failed_state": failed_variant["state"],
                "failed_reason_code": failed_variant["reason_code"],
                "failed_blocking_ids": failed_variant.get("blocking_ids", []),
                "recovered_state": recovered_variant["state"],
                "failed_assessment_sha256": digest(failed_variant),
                "recovered_assessment_sha256": digest(recovered_variant)}
        readiness_evidence_path = feature_root / "validation/readiness-assessment.json"
        readiness_evidence_path.parent.mkdir(parents=True, exist_ok=True)
        readiness_evidence_path.write_text(json.dumps(readiness, sort_keys=True) + "\n", encoding="utf-8")

        proof_requirements: dict[str, list[str]] = {}
        source_requirements: dict[str, list[str]] = {}
        classifications: dict[str, dict[str, Any]] = {}
        proofs: dict[str, dict[str, Any]] = {}
        state_rows: list[dict[str, Any]] = []
        evidence_path = f"{feature}/evidence.json"
        evidence_file = consumer / evidence_path
        evidence_file.write_text(json.dumps({"case": case_id, "evidence": "deterministic disposable fixture"}, sort_keys=True) + "\n")
        ev = [{"path": evidence_path, "sha256": sha(evidence_file)}]
        for task_id in requested:
            if task_id in completed:
                state = "completed-with-proof"
                kind = "administrative-prerequisite" if task_id in expected.get("administrative_prerequisite_ids", []) else "substantive-implementation"
            elif task_id in eligible:
                state = "eligible"
                kind = "substantive-implementation"
            else:
                state = "pending"
                kind = None
            row = {"task_id": task_id, "state": state, "dependency_ids": [], "evidence": ev,
                   "blocker": "fixture-prerequisite-pending" if state == "pending" else None,
                   "resume_action": "resolve-fixture-prerequisite" if state == "pending" else None,
                   "proof_sha256": None}
            if kind:
                record = next(item for item in scope["task_records"] if item["task_id"] == task_id)
                requirements = [f"requirement-{task_id}"]
                proof_requirements[task_id] = requirements
                source_requirements[task_id] = requirements if kind == "substantive-implementation" else []
                classification = {"task_id": task_id,
                    "task_description_sha256": record["description_sha256"], "completion_kind": kind,
                    "requirement_ids": requirements, "source_requirement_ids": source_requirements[task_id],
                    "scope_sha256": scope["scope_sha256"], "classification_evidence": ev}
                classifications[task_id] = classification
                review_reference = f"{feature}/validation/deterministic-review-{case_id}-{task_id}.json"
                review_file = consumer / review_reference
                review_file.parent.mkdir(parents=True, exist_ok=True)
                review_file.write_text(json.dumps({"scenario_id": case_id, "task_id": task_id,
                    "reviewer_kind": "deterministic-fixture", "verdict": "complete"},
                    sort_keys=True) + "\n", encoding="utf-8")
                proof = {"task_id": task_id, "task_description_sha256": record["description_sha256"],
                         "completion_kind": kind, "scope_sha256": scope["scope_sha256"],
                         "requirements": [{"requirement_id": requirements[0], "satisfied": True, "evidence": ev}],
                         "proof_evidence": ev,
                         "review_evidence": {"reviewer": "FarmBoy Code Reviewer", "verdict": "complete",
                                             "reference": review_reference, "sha256": sha(review_file)}}
                if kind == "administrative-prerequisite":
                    administrative_effect = task_transition_proofs[task_id]["administrative_effect"]
                    proof.update({"trusted_decision_references": [f"fixture-answer-{case_id}"],
                                  "permitted_effect_route": "disposable-fixture-only",
                                  "administrative_state_before": {"state": administrative_effect["before_state"],
                                      "sha256": administrative_effect["before_sha256"],
                                      "evidence": [{"path": administrative_effect["before_path"],
                                                    "sha256": administrative_effect["before_sha256"]}]},
                                  "administrative_state_after": {"state": administrative_effect["after_state"],
                                      "sha256": administrative_effect["after_sha256"],
                                      "evidence": [{"path": administrative_effect["path"],
                                                    "sha256": administrative_effect["after_sha256"]}]},
                                  "no_source_effect_evidence": True})
                else:
                    source_path = f"{feature}/{task_id.lower()}.txt"
                    source_file = consumer / source_path
                    if state != "completed-with-proof":
                        source_file.write_text("before\n", encoding="utf-8")
                    source_ev = [{"path": source_path, "sha256": sha(source_file)}]
                    proof.update({"activation_sha256": "f" * 64, "source_delta_evidence": source_ev,
                                  "validation_evidence": ev})
                proofs[task_id] = proof
                row["proof_sha256"] = digest(proof) if state == "completed-with-proof" else None
            state_rows.append(row)
        predecessor = "a" * 64
        input_digests = {path: sha(consumer / path) for path in
                         (".specify/feature.json", f"{feature}/spec.md", f"{feature}/tasks.md")}
        blockers = []
        if expected.get("state") == "blocked" and not eligible:
            blockers = [{"reason_code": expected.get("reason_code", "fixture-blocked"),
                         "resume_action": expected.get("resume_action", "reassess-fixture"), "evidence": ev}]
        assessment = {"assessment_id": f"assessment-{case_id}", "scope_sha256": scope["scope_sha256"],
                      "predecessor_sha256": predecessor, "input_digests": input_digests,
                      "task_states": state_rows, "eligible_task_ids": eligible, "pending_task_ids": pending,
                      "global_blockers": blockers, "iteration": 1, "evidence": ev}
        # When a global guard blocks, no per-task item is executable; retain all unfinished requests as pending.
        if blockers:
            assessment["eligible_task_ids"] = []
            assessment["pending_task_ids"] = [task for task in requested if task not in completed]
            for row in state_rows:
                if row["state"] == "eligible":
                    row.update(state="pending", blocker=blockers[0]["reason_code"],
                               resume_action=blockers[0]["resume_action"])
                    row["proof_sha256"] = None
            proofs = {key: value for key, value in proofs.items() if key in completed}
            proof_requirements = {key: value for key, value in proof_requirements.items() if key in completed}
            source_requirements = {key: value for key, value in source_requirements.items() if key in completed}
            classifications = {key: value for key, value in classifications.items() if key in completed}
        eligibility_payload = {**scope_payload, "assessment": assessment, "proofs": proofs,
            "proof_requirements": proof_requirements, "completion_classifications": classifications,
            "source_requirement_ids": source_requirements, "retained_predecessor_sha256": predecessor}
        eligibility_wire = json.dumps(eligibility_payload, sort_keys=True, separators=(",", ":"))
        forwarded_eligibility_payload = json.loads(eligibility_wire)
        eligibility = controller_module.validate_implementation_eligibility(consumer, forwarded_eligibility_payload)
        if eligibility.get("state") != "ready":
            raise AssertionError(f"{case_id}: installed eligibility helper blocked: {eligibility}; payload_keys={sorted(eligibility_payload)}")
        if case_id in {"SI002", "SI005"}:
            chronology_operations.append({"operation": "fresh-installed-eligibility-after-tasker",
                "scope_sha256": scope["scope_sha256"],
                "task_tracking_successor_sha256": task_tracking_successors[0]["sha256"],
                "eligibility_sha256": eligibility["eligibility_sha256"],
                "eligible_task_ids": list(eligibility["eligibility"]["eligible_task_ids"]),
                "pending_task_ids": list(eligibility["eligibility"]["pending_task_ids"])})
        route_wire_packets: list[dict[str, str]] = []

        def dispatch_production_route(route_request: dict[str, Any]) -> dict[str, Any]:
            wire = json.dumps(route_request, sort_keys=True, separators=(",", ":"))
            forwarded = json.loads(wire)
            result = controller_module.route_scoped_implementation(consumer, forwarded)
            route_wire_packets.append({"request_sha256": hashlib.sha256(wire.encode()).hexdigest(),
                                       "result_sha256": digest(result)})
            return result
        observed_task_states = {item["task_id"]: item["state"]
                                for item in eligibility["eligibility"]["task_states"]}
        observed_completed = [task_id for task_id in requested
                              if observed_task_states.get(task_id) == "completed-with-proof"]
        if observed_completed != completed:
            raise AssertionError(f"{case_id}: completed IDs differ from installed task states: {observed_task_states}")
        observed_outside = [task_id for task_id in task_ids if task_id not in requested]

        if case_id != "SI005":
            source_effect_path = feature_root / "source-effect.txt"
            source_effect_path.write_text(f"reproducible pre-correction behavior {case_id}\n", encoding="utf-8")
            selected_source_task = (eligible or requested)[0]
            finding = {"id": "F020-EXAMPLE-001", "task_id": selected_source_task,
                "artifact_location": f"{feature}/{source_effect_path.name}:1",
                "violated_requirement": "A scoped correction must be assessed against source evidence captured before its effect.",
                "observed_deficiency": "The disposable source fixture still has its reproducible pre-correction behavior.",
                "exact_correction": "Change the fixture source and retain a fresh independent review of the original finding.",
                "evidence": [{"path": f"{feature}/{source_effect_path.name}", "sha256": sha(source_effect_path)}]}
            baseline_findings = [finding]
            if case_id == "SI006":
                baseline_findings.append({**finding, "id": "F020-EXAMPLE-002",
                    "observed_deficiency": "A second pre-existing defect remains in the disposable source fixture."})
            baseline_capture = controller_module.capture_implementation_baseline(consumer, {
                "feature_directory": feature, "selected_task_ids": [selected_source_task], "findings": baseline_findings})
            if baseline_capture.get("state") != "ready":
                raise AssertionError(f"{case_id}: pre-effect finding baseline failed: {baseline_capture}")
            chronology_operations.append({"operation": "original-source-finding-baseline-capture",
                "task_id": selected_source_task, "baseline_sha256": baseline_capture["baseline_sha256"],
                "source_preimage_sha256": sha(source_effect_path), "scope_sha256": scope["scope_sha256"]})
        activation_baseline = baseline_capture
        t069_source_path = None
        if case_id == "SI005":
            # T069 is a distinct successor task with its own activation baseline
            # after T068's source effect and Tasker proof have closed.
            t069_source_file = feature_root / "t069.txt"
            t069_source_file.write_text("fresh successor task preimage after T068 closure\n", encoding="utf-8")
            t069_source_path = f"{feature}/t069.txt"
            t069_finding = {"id": "F020-EXAMPLE-T069", "task_id": "T069",
                "artifact_location": f"{t069_source_path}:1",
                "violated_requirement": "A successor task receives a fresh task-specific activation baseline.",
                "observed_deficiency": "The T069 fixture source retains its pre-effect behavior.",
                "exact_correction": "Use the current T069 source preimage and current eligibility for activation.",
                "evidence": [{"path": t069_source_path, "sha256": sha(t069_source_file)}]}
            activation_baseline = controller_module.capture_implementation_baseline(consumer, {
                "feature_directory": feature, "selected_task_ids": ["T069"], "findings": [t069_finding]})
            if activation_baseline.get("state") != "ready":
                raise AssertionError(f"SI005: separate T069 activation baseline failed: {activation_baseline}")
            chronology_operations.append({"operation": "T069-successor-activation-baseline-after-T068-closure",
                "task_id": "T069", "baseline_sha256": activation_baseline["baseline_sha256"],
                "source_preimage_sha256": sha(t069_source_file),
                "t068_progress_baseline_sha256": baseline_capture["baseline_sha256"]})
        activation_results = ([t068_activation_record] if case_id == "SI005" else [])
        deferred_activation_inputs: dict[str, dict[str, Any]] = {}
        for task_id in eligible:
            source_path = t069_source_path if case_id == "SI005" else f"{feature}/{task_id.lower()}-activation.txt"
            source_file = consumer / source_path
            if case_id != "SI005":
                source_file.write_text(f"observed source before activation for {case_id}/{task_id}\n", encoding="utf-8")
            activation_evidence = _evidence(consumer, case_id, f"activation-{task_id}")
            if case_id == "SI002":
                deferred_activation_inputs[task_id] = {"source_path": source_path,
                    "source_sha256": sha(source_file), "route_evidence": activation_evidence}
                continue
            activation = {"activation_id": f"activation-{case_id}-{task_id}", "task_id": task_id,
                "scope_sha256": scope["scope_sha256"], "eligibility_sha256": eligibility["eligibility_sha256"],
                "predecessor_baseline_sha256": activation_baseline["baseline_sha256"], "occurred_at": "2026-10-08T12:10:00Z",
                "requirements": [f"requirement-{task_id}"],
                "source_preimages": [{"path": source_path, "state": "present", "sha256": sha(source_file)}],
                "route_evidence": activation_evidence,
                "readiness_evidence": [{"path": f"{feature}/validation/readiness-assessment.json",
                                        "sha256": sha(readiness_evidence_path)}], "iteration": 1}
            activation_result = controller_module.validate_implementation_activation(consumer, {
                **scope_payload, "activation": activation, "eligibility_sha256": eligibility["eligibility_sha256"],
                "predecessor_baseline_sha256": activation_baseline["baseline_sha256"], "task_id": task_id, "required_paths": [source_path]})
            if activation_result.get("state") != "ready":
                raise AssertionError(f"{case_id}: activation failed: {activation_result}")
            activation_record_path = feature_root / f"validation/{task_id.lower()}-activation.json"
            activation_record_path.parent.mkdir(parents=True, exist_ok=True)
            activation_record_path.write_text(json.dumps(activation, sort_keys=True) + "\n", encoding="utf-8")
            activation_results.append({"task_id": task_id, "activation_sha256": digest(activation),
                "activation_record_sha256": sha(activation_record_path), "preimage_sha256": sha(source_file),
                "predecessor_baseline_sha256": activation_baseline["baseline_sha256"],
                "validated_before_source_effect": True})

        administrative_progress_check = None

        def check_no_progress_before_selected_source() -> None:
            nonlocal administrative_progress_check
            baseline_finding = baseline_capture["baseline"]["findings"][0]
            current_evidence = [{"path": baseline_finding["evidence"][0]["path"],
                                 "sha256": sha(consumer / baseline_finding["evidence"][0]["path"])}]
            review = {"reviewer": "FarmBoy Code Reviewer",
                "baseline_sha256": baseline_capture["baseline_sha256"],
                "findings": [{"id": baseline_finding["id"], "task_id": baseline_finding["task_id"],
                    "status": "unresolved", "evidence": current_evidence}],
                "new_findings": [], "completed_task_ids": []}
            payload = {"baseline": baseline_capture["baseline"],
                "baseline_sha256": baseline_capture["baseline_sha256"], "review": review}
            observed = controller_module.validate_implementation_progress(consumer, payload)
            if observed.get("state") != "ready" or observed.get("substantive_progress") is not False:
                raise AssertionError(f"{case_id}: admin-only work must produce zero source progress: {observed}")
            administrative_progress_check = {"state": observed["state"],
                "substantive_progress": observed["substantive_progress"],
                "baseline_sha256": baseline_capture["baseline_sha256"],
                "source_preimage_sha256": current_evidence[0]["sha256"],
                "review_sha256": digest(review)}

        def collect_stale_evidence(value: Any) -> list[dict[str, str]]:
            stale: list[dict[str, str]] = []
            if isinstance(value, dict):
                if set(value) == {"path", "sha256"} and isinstance(value["path"], str):
                    path = consumer / value["path"]
                    if not path.is_file() or sha(path) != value["sha256"]:
                        stale.append({"path": value["path"], "expected_sha256": str(value["sha256"]),
                                      "observed_sha256": sha(path) if path.is_file() else "missing"})
                else:
                    for child in value.values():
                        stale.extend(collect_stale_evidence(child))
            elif isinstance(value, list):
                for child in value:
                    stale.extend(collect_stale_evidence(child))
            return stale

        def run_scoped_progress(current_history: dict[str, Any], *, entry_history: dict[str, Any], case_name: str) -> dict[str, Any]:
            nonlocal eligibility
            post_source_before = sha(source_effect_path)
            if case_name not in {"SI005", "SI011"}:
                source_effect_path.write_text(f"after correction {case_name}\n", encoding="utf-8")
            if case_name in {"SI002", "SI005"}:
                chronology_operations.append({"operation": "selected-source-effect",
                    "task_id": selected_source_task, "before_sha256": post_source_before,
                    "after_sha256": sha(source_effect_path), "history_sha256": current_history["sha256"]})
            current_source = [{"path": f"{feature}/{source_effect_path.name}", "sha256": sha(source_effect_path)}]
            stale_source_paths = {item["path"] for item in collect_stale_evidence(eligibility_payload)}
            if stale_source_paths:
                # A source correction invalidates the prior proof. Refresh the
                # deterministic current review artifact and every proof digest
                # that names the changed source before asking production to
                # revalidate current eligibility.
                for task_id, proof in eligibility_payload.get("proofs", {}).items():
                    source_refs = [item for item in proof.get("source_delta_evidence", [])
                                   if item.get("path") in stale_source_paths]
                    if not source_refs:
                        continue
                    reviewed_paths = {item["path"] for item in source_refs}
                    review = proof.get("review_evidence", {})
                    reference = review.get("reference")
                    if isinstance(reference, str) and reference.startswith(f"{feature}/"):
                        review_file = consumer / reference
                        review_file.write_text(json.dumps({"scenario_id": case_name, "task_id": task_id,
                            "reviewer_kind": "deterministic-fixture", "verdict": "complete",
                            "reviewed_source": [{"path": path, "sha256": sha(consumer / path)}
                                                for path in sorted(reviewed_paths)]},
                            sort_keys=True) + "\n", encoding="utf-8")
                        review["sha256"] = sha(review_file)
                    def refresh_source_refs(value: Any) -> None:
                        if isinstance(value, dict):
                            if set(value) == {"path", "sha256"} and value["path"] in reviewed_paths:
                                value["sha256"] = sha(consumer / value["path"])
                            else:
                                for child in value.values():
                                    refresh_source_refs(child)
                        elif isinstance(value, list):
                            for child in value:
                                refresh_source_refs(child)
                    refresh_source_refs(proof)
                    task_state = next((row for row in eligibility_payload["assessment"]["task_states"]
                                       if row["task_id"] == task_id), None)
                    if task_state is not None and task_state.get("state") == "completed-with-proof":
                        task_state["proof_sha256"] = digest(proof)
                eligibility = controller_module.validate_implementation_eligibility(consumer, eligibility_payload)
                if eligibility.get("state") != "ready":
                    raise AssertionError(f"{case_name}: fresh current proof failed eligibility recheck: {eligibility}")
            review_findings = []
            for prior in baseline_capture["baseline"]["findings"]:
                status = "unresolved" if case_name == "SI011" or (case_name == "SI006" and prior["id"] == "F020-EXAMPLE-002") else "resolved"
                item = {"id": prior["id"], "task_id": selected_source_task, "status": status,
                    "evidence": current_source}
                if status == "resolved":
                    item["resolution_summary"] = "The original pre-effect defect was reviewed against the corrected source."
                review_findings.append(item)
            new_findings = []
            if case_name == "SI006":
                new_findings.append({"id": "F020-EXAMPLE-003", "task_id": selected_source_task,
                    "artifact_location": f"{feature}/source-effect.txt:1",
                    "violated_requirement": "New findings retain their own identity.",
                    "observed_deficiency": "A new issue was discovered after the source correction.",
                    "exact_correction": "Record and resolve the newly observed issue in a later pass.",
                    "evidence": current_source})
            completed_source_tasks = (list(transition_completed) if case_name == "SI005" else [])
            task_completion_evidence = []
            for task_id in completed_source_tasks:
                proof = task_transition_proofs[task_id]
                source_change = proof["source_change"]
                task_completion_evidence.append({"path": source_change["path"],
                    "sha256": sha(consumer / source_change["path"])})
                task_completion_evidence.extend(proof["reviewer_evidence"])
                task_completion_evidence.extend(proof["tasker_evidence"])
            review = {"reviewer": "FarmBoy Code Reviewer",
                "baseline_sha256": baseline_capture["baseline_sha256"], "findings": review_findings,
                "new_findings": new_findings, "completed_task_ids": completed_source_tasks}
            if task_completion_evidence:
                review["task_completion_evidence"] = task_completion_evidence
            progress_payload = {"baseline": baseline_capture["baseline"],
                "baseline_sha256": baseline_capture["baseline_sha256"], "review": review}
            progress = controller_module.validate_implementation_progress(consumer, progress_payload)
            if progress.get("state") != "ready":
                raise AssertionError(f"{case_name}: real frozen-baseline progress validation failed: {progress}")
            producer_records = []
            if task_tracking_successors:
                pairs = re.findall(r"`([a-z-]+)`/`([a-z-]+)`", capture_prompt)
                producer_pair = next((pair for pair in pairs
                    if "task-outcomes" in pair[0]), None)
                if producer_pair is None:
                    raise AssertionError("production capture node no longer declares the executed task-outcome producer pair")
                validator_output = {**scope_result, "task_tracking_successor": task_tracking_successors[-1]}
                producer_records = [{"tasker_step_id": producer_pair[0], "validator_step_id": producer_pair[1],
                    "tasker_result": tasker_record, "validator_result": validator_output}]
            stale_eligibility_evidence = collect_stale_evidence(eligibility_payload)
            if stale_eligibility_evidence:
                raise AssertionError(f"{case_name}: current eligibility contains stale evidence before capture: {stale_eligibility_evidence}")
            post_pass_state = _capture_post_pass_state(controller_module, consumer, scope=scope,
                trusted_request_reference=scope["request_reference"],
                retained_scope_sha256=scope["scope_sha256"],
                retained_history_sha256=current_history["sha256"],
                incoming_successors=[], producer_records=producer_records,
                eligibility=eligibility, eligibility_request=eligibility_payload,
                entry_history_sha256=entry_history["sha256"], capture_command=capture_command)
            predecessor_path = feature_root / "validation/pre-source-assessment.json"
            predecessor_path.parent.mkdir(parents=True, exist_ok=True)
            predecessor_path.write_text(json.dumps({"baseline_sha256": baseline_capture["baseline_sha256"],
                "remaining_ids": baseline_capture["remaining_ids"],
                "source_preimage_sha256": baseline_capture["baseline"]["findings"][0]["evidence"][0]["sha256"]},
                sort_keys=True) + "\n", encoding="utf-8")
            predecessor_evidence = [{"path": f"{feature}/validation/pre-source-assessment.json",
                                     "sha256": sha(predecessor_path)}]
            previous_assessment = {"state": "continue", "next_step_id": "implement-tasks",
                "reason_code": "pre-source-frozen-findings", "evidence": predecessor_evidence,
                "remaining_ids": baseline_capture["remaining_ids"], "resolved_ids": []}
            outcome_envelope = {"state": "continue", "next_step_id": "implement-tasks",
                "reason_code": "independently-assessed-post-source-state", "evidence": progress["evidence"],
                "remaining_ids": list(dict.fromkeys([*progress["remaining_ids"],
                    *(f"task:{task_id}" for task_id in requested if task_id not in completed)])),
                "resolved_ids": progress["resolved_ids"]}
            current_assessment = {"outcome_envelope": outcome_envelope, "review": review}
            expected_progress_payload = progress_payload
            rendered_prompt, bound = render_execution_bindings({
                "entry": {"scope": scope, "eligibility": eligibility, "history": entry_history,
                    "task_tracking_successors": task_tracking_successors,
                    "previous_assessment": previous_assessment,
                    "retained_previous_assessment_sha256": digest({"scope_sha256": scope["scope_sha256"],
                        "assessment": previous_assessment}), "baseline": baseline_capture["baseline"]},
                "current_assessment": {**current_assessment, "review": review},
                "readiness": readiness, "post_pass_state": post_pass_state})
            if ("route-scoped-entry.output.history" in execution_node["prompt"]
                    or "route-scoped-entry.output.task_tracking_successors" in execution_node["prompt"]):
                raise AssertionError(f"{case_name}: post-pass callback regressed to stale route entry state")
            if "steps.assess-implementation-after-pass.output.outcome_envelope" not in execution_node["prompt"]:
                raise AssertionError(f"{case_name}: callback does not forward the exact validated Reviewer envelope")
            bound_scope = bound["scope"]
            bound["retained_history"] = bound["post_pass_state"]["history"]
            bound["task_tracking_successors"] = bound["post_pass_state"]["task_tracking_successors"]
            bound["eligibility"] = bound["post_pass_state"]["eligibility"]
            progress_payload = {"baseline": bound["frozen_baseline"],
                "baseline_sha256": digest(bound["frozen_baseline"]), "review": bound["current_review"]}
            scoped_request = {
                "controller_loop_mode": "implementation_scope", "scope": bound_scope,
                "trusted_request_reference": bound_scope["request_reference"],
                "retained_scope_sha256": bound_scope["scope_sha256"],
                "retained_history_sha256": bound["retained_history"]["sha256"],
                "assessment": bound["current_assessment"],
                "eligible_task_ids": bound["eligibility"]["eligibility"]["eligible_task_ids"],
                "declared_node_ids": ["prepare-scoped-prerequisites", "implement-tasks"],
                "previous_assessment": bound["previous_assessment"],
                "retained_previous_assessment_sha256": bound["retained_previous_assessment_sha256"],
                "progress": progress_payload,
                "administrative_prerequisite_ids": [],
                "task_tracking_successors": bound["task_tracking_successors"]}
            if (bound["readiness"] != readiness or bound["frozen_baseline"] != baseline_capture["baseline"]
                    or bound["current_review"] != review):
                raise AssertionError(f"{case_name}: rendered readiness or frozen-baseline binding changed")
            if (scoped_request["assessment"] != outcome_envelope
                    or scoped_request["previous_assessment"] != previous_assessment
                    or scoped_request["progress"] != expected_progress_payload):
                raise AssertionError(f"{case_name}: scoped callback packet differs from rendered assessments "
                    f"(current={scoped_request['assessment'] == current_assessment}, "
                    f"previous={scoped_request['previous_assessment'] == previous_assessment}, "
                    f"progress={scoped_request['progress'] == expected_progress_payload})")
            scoped_wire = json.dumps(scoped_request, sort_keys=True, separators=(",", ":"))
            forwarded_scoped_request = json.loads(scoped_wire)
            scoped = controller_module.validate_scoped_implementation_progress(consumer, forwarded_scoped_request)
            if entry_history["sha256"] != current_history["sha256"]:
                stale_history_request = json.loads(json.dumps(forwarded_scoped_request))
                stale_history_request["retained_history_sha256"] = entry_history["sha256"]
                stale_history_result = controller_module.validate_scoped_implementation_progress(
                    consumer, stale_history_request)
                if stale_history_result.get("state") != "blocked":
                    raise AssertionError(f"{case_name}: stale route-entry history was accepted after a pass: {stale_history_result}")
            else:
                stale_history_result = None
            corrupted = json.loads(json.dumps(forwarded_scoped_request))
            corrupted["progress"]["baseline_sha256"] = "0" * 64
            corruption_result = controller_module.validate_scoped_implementation_progress(consumer, corrupted)
            if corruption_result.get("state") != "blocked":
                raise AssertionError(f"{case_name}: corrupted rendered progress binding reached routing: {corruption_result}")
            corrupted_assessment = json.loads(json.dumps(forwarded_scoped_request))
            corrupted_assessment["assessment"]["resolved_ids"].append("task:T999")
            assessment_mutation_result = controller_module.validate_scoped_implementation_progress(
                consumer, corrupted_assessment)
            if assessment_mutation_result.get("state") != "blocked":
                raise AssertionError(f"{case_name}: corrupted rendered assessment reached routing: {assessment_mutation_result}")
            return {"previous_assessment": previous_assessment, "current_assessment": current_assessment,
                "review": review, "progress": progress, "progress_payload": progress_payload,
                "route_result": scoped, "corrupted_binding_result": corruption_result,
                "entry_history_sha256": entry_history["sha256"], "post_pass_history_sha256": current_history["sha256"],
                "stale_entry_history_result": stale_history_result,
                "assessment_mutation_result": assessment_mutation_result,
                "production_progress_dispatch": {"rendered_prompt_sha256": hashlib.sha256(rendered_prompt.encode()).hexdigest(),
                    "request_sha256": hashlib.sha256(scoped_wire.encode()).hexdigest(),
                    "forwarded_payload_sha256": digest(forwarded_scoped_request),
                    "result_sha256": digest(scoped),
                    "previous_assessment_sha256": digest(previous_assessment),
                    "current_assessment_sha256": digest(current_assessment),
                    "baseline_sha256": baseline_capture["baseline_sha256"]}}

        owner_checks = []
        owner_effects = []
        owner_variants = case.get("owner_source_variants", [])
        owner_required = case.get("owner_source") is not None or bool(owner_variants)
        if owner_required:
            variants = owner_variants or ["permitted"]
            for variant in variants:
                owner_root = consumer / ".specify" / "si-owner" / case_id / variant
                owner_root.mkdir(parents=True, exist_ok=True)
                for name in ("AGENTS.md", "owner-contract.md", "source.py", "authority.md"):
                    (owner_root / name).write_text(f"{case_id} {variant} {name}\n", encoding="utf-8")
                route_state = "permitted"
                access = "read-write"
                state = "ready"
                reason = None
                resume = None
                if variant == "checkout-absent":
                    route_state, state, reason, resume = "missing", "blocked", "owner-source-unavailable", "restore-owner-checkout"
                elif variant == "access-denied":
                    access, state, reason, resume = "denied", "blocked", "owner-source-access-denied", "restore-owner-access"
                elif variant in {"authority-conflict", "unsafe-effect"}:
                    route_state, state, reason, resume = "conflicted", "blocked", "owner-source-authority-conflict", "resolve-owner-authority"
                elif variant == "route-missing":
                    route_state, state, reason, resume = "missing", "blocked", "owner-source-route-unverified", "establish-owner-source-route"
                paths = ["AGENTS.md", "owner-contract.md", "source.py", "authority.md"]
                base = {"task_id": "T052", "component_id": "flow-roadmap", "source_identity": "fixture-owner-checkout",
                    "source_coordinates": {"repository": "fixture/spec-kit-flow-roadmap", "revision": "fixture-revision",
                        "dirty_state": "clean", "relative_paths": paths}, "access_state": access,
                    "guidance_evidence": [{"path": f".specify/si-owner/{case_id}/{variant}/AGENTS.md",
                        "sha256": sha(owner_root / "AGENTS.md")}],
                    "source_route": {"state": route_state, "description": f"deterministic {variant} route",
                        "evidence": [{"path": f".specify/si-owner/{case_id}/{variant}/owner-contract.md",
                                      "sha256": sha(owner_root / "owner-contract.md")}]},
                    "authority_evidence": [{"path": f".specify/si-owner/{case_id}/{variant}/authority.md",
                                            "sha256": sha(owner_root / "authority.md")}], "state": state}
                if state == "blocked":
                    base.update(reason_code=reason, resume_action=resume)
                checked_owner = scope_module.validate_owner_source_assessment(base)
                if case_id in {"SI002", "SI009"} and variant == "permitted":
                    owner_source = owner_root / "source.py"
                    before_bytes = owner_source.read_bytes()
                    before_hash = sha(owner_source)
                    owner_source.write_text(owner_source.read_text(encoding="utf-8") + "# fixture correction\n", encoding="utf-8")
                    after_hash = sha(owner_source)
                    if before_bytes == owner_source.read_bytes() or before_hash == after_hash:
                        raise AssertionError(f"{case_id}: permitted disposable owner effect did not change bytes")
                    owner_effects.append({"task_id": "T052", "path": f".specify/si-owner/{case_id}/{variant}/source.py",
                                          "before_sha256": before_hash, "after_sha256": after_hash,
                                          "effect": "disposable fixture source correction"})
                owner_checks.append({"variant": variant, "state": checked_owner["state"],
                                     "source_coordinates": checked_owner["source_coordinates"],
                                     "route_state": checked_owner["source_route"]["state"]})

        operator_question = None
        if case_id == "SI004":
            request = {"kind": "question", "step_id": "prepare-scoped-prerequisites",
                "question": "The proposed task/effect is outside this request. Keep the current scope or request a separate scope revision?",
                "options": ["keep-requested-scope", "request-scope-revision"], "allow_custom_answer": False}
            validated = controller_module.validate_child_question(request, "prepare-scoped-prerequisites")
            answer = controller_module.resolve_child_answer(validated, "keep-requested-scope",
                "si004-coder-child", "si004-coder-child")
            needs_human = controller_module.route_assessment(
                {"state": "needs-human", "resume_action": "resume-same-child-after-operator-answer"},
                loop_body_step_ids={"prepare-scoped-prerequisites", "implement-tasks"})
            if needs_human.get("action") != "needs-human" or answer.get("child_id") != "si004-coder-child":
                raise AssertionError("SI004: explicit question/gate did not preserve same-child answer")
            scope_after_answer = controller_module.validate_implementation_scope(consumer, scope_payload)
            eligibility_after_answer = controller_module.validate_implementation_eligibility(consumer, eligibility_payload)
            if scope_after_answer.get("state") != "ready" or eligibility_after_answer.get("state") != "ready":
                raise AssertionError("SI004: unchanged trusted scope did not revalidate after same-child answer")
            operator_question = {"question": validated, "main_route": needs_human, "simulated_fixture_answer": answer,
                                 "scope_revalidation": {"scope_state": scope_after_answer["state"],
                                     "eligibility_state": eligibility_after_answer["state"]},
                                 "scope_expanded": False}

        results = []
        route_input = expected.get("expected_route", case.get("expected_route", []))
        if case_id == "SI002":
            # Preparation has already happened before administrative proof and
            # Tasker tracking; the fresh eligibility dispatch starts at source.
            route_input = ["implement-tasks"]
        route_state = ("blocked" if blockers else "complete" if not eligible and not pending else "continue")
        assessment_state = "complete" if route_state == "complete" else "blocked" if route_state == "blocked" else "continue"
        if route_state == "blocked":
            route_assessment = {"state": "blocked", "reason_code": expected.get("reason_code", "fixture-blocked"),
                "evidence": ev, "remaining_ids": [f"task:{task}" for task in pending], "resolved_ids": [],
                "resume_action": expected.get("resume_action", "reassess-fixture")}
        elif route_state == "complete":
            route_assessment = {"state": "complete", "reason_code": "scope-complete", "evidence": ev,
                                "remaining_ids": [], "resolved_ids": [f"task:{task}" for task in completed]}
        else:
            selected = route_input[0] if route_input else "implement-tasks"
            remaining = [f"task:{task}" for task in requested if task not in completed]
            route_assessment = {"state": "continue", "next_step_id": selected,
                "reason_code": expected.get("reason_code") or "fixture-pending-work", "evidence": ev,
                "remaining_ids": remaining or ["task:T068"], "resolved_ids": [f"task:{task}" for task in completed]}
        retained_history = chronology_history
        preexisting_attempts = 1 if case_id == "SI005" else setup.get("source_attempts_started", 0)
        preexisting_sessions = case["history"].get("coder_sessions_started", 0) if preexisting_attempts else 0
        if preexisting_sessions and not retained_history.get("events"):
            raw_outcomes = [event.get("outcome") for event in case["history"].get("events", [])
                            if event.get("kind") in {"session-outcome", "session-start"} and event.get("outcome")]
            retained_history = _record_sessions(controller_module, consumer, scope_payload, retained_history,
                case_id, preexisting_sessions, preexisting_attempts, outcomes=raw_outcomes,
                question=any(event.get("kind") in {"question", "operator-input"} for event in case["history"].get("events", [])))
        route_payload = {**scope_payload, "retained_history_sha256": retained_history["sha256"],
                         "assessment": route_assessment,
                         "eligible_task_ids": eligible if not blockers else [],
                         "declared_node_ids": ["prepare-scoped-prerequisites", "implement-tasks"]}
        if assessment_state == "complete":
            route_payload["eligibility_request"] = eligibility_payload
        generic_post_source_calls = []
        if preexisting_attempts:
            post_source = run_scoped_progress(retained_history, entry_history=retained_history, case_name=case_id)
            route = post_source["route_result"]
            generic_post_source_calls.append({key: value for key, value in post_source.items()
                                              if key != "progress_payload"})
            if route.get("state") == "blocked" and assessment_state != "blocked":
                raise AssertionError(f"{case_id}: scoped post-source route details: eligible={eligible}, "
                    f"previous={post_source['previous_assessment']}, current={post_source['current_assessment']}, "
                    f"progress={post_source['progress']}, route={route}")
        else:
            route = dispatch_production_route(route_payload)
        if route.get("state") == "blocked" and assessment_state != "blocked":
            raise AssertionError(f"{case_id}: installed route blocked unexpectedly: {route}")
        routed_node = route.get("route", {}).get("next_step_id") or route.get("scoped_route", {}).get("next_step_id")
        if route.get("state") == "continue" and routed_node not in {None, "prepare-scoped-prerequisites", "implement-tasks"}:
            raise AssertionError(f"{case_id}: installed route escaped declared nodes: {route}")
        results.append(route)
        if route.get("state") == "continue" and not preexisting_attempts:
            nodes_to_execute = route_input or [route.get("route", {}).get("next_step_id", "implement-tasks")]
            for index, node in enumerate(nodes_to_execute):
                entry_history_for_pass = retained_history
                execution_kind = "preparation" if node == "prepare-scoped-prerequisites" else (
                    "first-source-execution" if retained_history["source_attempts_started"] == 0 else "corrective-source-execution")
                next_session = retained_history["coder_sessions_started"] + 1
                retained_history = _record_sessions(controller_module, consumer, scope_payload, retained_history,
                    case_id, next_session, retained_history["source_attempts_started"] + (1 if node == "implement-tasks" else 0),
                    outcomes=["completed"], question=(case_id == "SI004"))
                if node == "implement-tasks" and case_id == "SI002":
                    chronology_operations.append({"operation": "source-coder-session-and-attempt",
                        "scope_sha256": scope["scope_sha256"], "history_sha256": retained_history["sha256"],
                        "source_attempts_started": retained_history["source_attempts_started"]})
                    for task_id, activation_input in deferred_activation_inputs.items():
                        activation = {"activation_id": f"activation-{case_id}-{task_id}", "task_id": task_id,
                            "scope_sha256": scope["scope_sha256"], "eligibility_sha256": eligibility["eligibility_sha256"],
                            "predecessor_baseline_sha256": baseline_capture["baseline_sha256"], "occurred_at": "2026-10-08T12:10:00Z",
                            "requirements": [f"requirement-{task_id}"],
                            "source_preimages": [{"path": activation_input["source_path"], "state": "present",
                                                  "sha256": activation_input["source_sha256"]}],
                            "route_evidence": activation_input["route_evidence"],
                            "readiness_evidence": [{"path": f"{feature}/validation/readiness-assessment.json",
                                "sha256": sha(readiness_evidence_path)}], "iteration": 1}
                        activation_result = controller_module.validate_implementation_activation(consumer, {
                            **scope_payload, "activation": activation,
                            "eligibility_sha256": eligibility["eligibility_sha256"],
                            "predecessor_baseline_sha256": baseline_capture["baseline_sha256"], "task_id": task_id,
                            "required_paths": [activation_input["source_path"]]})
                        if activation_result.get("state") != "ready":
                            raise AssertionError(f"SI002: post-history activation failed: {activation_result}")
                        activation_results.append({"task_id": task_id, "activation_sha256": digest(activation),
                            "preimage_sha256": activation_input["source_sha256"],
                            "history_sha256_before_activation": retained_history["sha256"]})
                        chronology_operations.append({"operation": "source-activation-validation",
                            "task_id": task_id, "activation_sha256": digest(activation),
                            "history_sha256": retained_history["sha256"]})
                    check_no_progress_before_selected_source()
                    chronology_operations.append({"operation": "administrative-no-source-progress-assessment",
                        **administrative_progress_check, "history_sha256": retained_history["sha256"]})
                if node == "implement-tasks":
                    before_hash = sha(source_effect_path)
                    source_effect_path.write_text(f"after correction {case_id}\n", encoding="utf-8")
                    after_hash = sha(source_effect_path)
                    if before_hash == after_hash:
                        raise AssertionError(f"{case_id}: disposable source effect did not change bytes")
                    owner_effects.append({"task_id": (eligible or requested)[0],
                        "path": f"{feature}/source-effect.txt", "before_sha256": before_hash,
                        "after_sha256": after_hash, "effect": "disposable source correction"})
                    if case_id in {"SI002", "SI005"}:
                        chronology_operations.append({"operation": "selected-source-effect",
                            "task_id": (eligible or requested)[0], "before_sha256": before_hash,
                            "after_sha256": after_hash})
                if index + 1 < len(nodes_to_execute):
                    next_assessment = dict(route_assessment)
                    next_assessment["next_step_id"] = nodes_to_execute[index + 1]
                    route_payload.update(assessment=next_assessment, retained_history_sha256=retained_history["sha256"])
                    route = dispatch_production_route(route_payload)
                    if route.get("state") != "continue" or route.get("route", {}).get("next_step_id") != nodes_to_execute[index + 1]:
                        raise AssertionError(f"{case_id}: installed route sequence failed at {nodes_to_execute[index + 1]}: {route}")
                    results.append(route)
                if node == "implement-tasks":
                    post_source = run_scoped_progress(retained_history, entry_history=entry_history_for_pass, case_name=case_id)
                    route = post_source["route_result"]
                    if route.get("state") != expected.get("state", "continue"):
                        raise AssertionError(f"{case_id}: actual scoped progress route differs from fixture: {route}")
                    results.append(route)
                    generic_post_source_calls.append({key: value for key, value in post_source.items()
                                                      if key != "progress_payload"})
        observed = {"id": case_id, "requested_task_ids": requested,
                    "eligible_task_ids": eligibility["eligibility"]["eligible_task_ids"],
                    "pending_task_ids": eligibility["eligibility"]["pending_task_ids"],
                    "completed_task_ids": observed_completed, "outside_task_ids": observed_outside,
                    "scope_sha256": scope["scope_sha256"], "eligibility_sha256": eligibility["eligibility_sha256"],
                    "fulfillment_proof_digests": {key: digest(value) for key, value in proofs.items()},
                    "task_tracking_successors": task_tracking_successors,
                    "preparation_or_source_chronology": {
                        "ordered_operations": chronology_operations,
                        "initial_eligibility": initial_eligibility_observation,
                        "initial_task_markers": {task_id: "unchecked" for task_id in requested},
                        "history_before_tasker_successor": (chronology_history["sha256"]
                            if case_id in {"SI002", "SI005"} else None),
                        "tasker_successor_predecessor_scope_sha256": (task_tracking_successors[0]["scope_sha256"]
                            if case_id in {"SI002", "SI005"} and task_tracking_successors else None),
                        "fresh_eligibility_after_tasker": (eligibility["eligibility"]["eligible_task_ids"]
                            if case_id in {"SI002", "SI005"} else None),
                        "fresh_eligibility_sha256": (eligibility["eligibility_sha256"]
                            if case_id in {"SI002", "SI005"} else None),
                        "administrative_zero_progress": administrative_progress_check,
                        "source_attempts_before_fresh_eligibility": (case_id == "SI005"),
                        "same_scope_sha256": (scope["scope_sha256"] if case_id in {"SI002", "SI005"} else None),
                        "history_event_ids": ([event["event_id"] for event in retained_history["events"]]
                            if case_id in {"SI002", "SI005"} else []),
                        "history_counters": {"coder_sessions_started": retained_history["coder_sessions_started"],
                            "source_attempts_started": retained_history["source_attempts_started"]}},
                    "task_transition_proofs": task_transition_proofs,
                    "task_markers_after_tracking": {task_id: current_tasks[task_id]["marker"]
                        for task_id in requested},
                    "completion_kinds": {key: value["completion_kind"] for key, value in classifications.items()},
                    "source_input_digests": input_digests,
                    "production_dispatch": {
                        "rendered_route_scoped_entry_prompt_sha256": hashlib.sha256(route_entry_prompt.encode()).hexdigest(),
                        "rendered_route_scoped_execution_prompt_sha256": (
                            generic_post_source_calls[-1]["production_progress_dispatch"]["rendered_prompt_sha256"]
                            if generic_post_source_calls else hashlib.sha256(route_execution_prompt.encode()).hexdigest()),
                        "eligibility_request_sha256": hashlib.sha256(eligibility_wire.encode()).hexdigest(),
                        "eligibility_forwarded_payload_sha256": digest(forwarded_eligibility_payload),
                        "eligibility_result_sha256": digest(eligibility),
                        "route_request_and_result_digests": route_wire_packets,
                    },
                    "readiness": {"state": readiness.get("state"), "reason_code": readiness.get("reason_code"),
                        "blocking_ids": readiness.get("blocking_ids", []),
                        "source_evidence": readiness.get("source_evidence", []),
                        "assessment_sha256": sha(readiness_evidence_path),
                        "global_failure_variant": readiness_failure_variant},
                    "generic_post_source_calls": generic_post_source_calls,
                    "execution_history_sha256": retained_history["sha256"],
                    "execution_history": retained_history,
                    "coder_sessions_started": retained_history["coder_sessions_started"],
                    "source_attempts_started": retained_history["source_attempts_started"],
                    "activation_results": activation_results, "owner_checks": owner_checks,
                    "observed_effects": owner_effects,
                    "operator_question": operator_question,
                    "generic_route_inputs": {"previous_assessment": route_payload.get("previous_assessment"),
                                             "current_assessment": route_payload.get("assessment")},
                    "route": results, "expected_state": expected.get("state"),
                    "observed_gate_state": (operator_question["main_route"]["action"]
                                            if operator_question else
                                            (results[-1].get("state") if results else route.get("state"))),
                    "observed_route_state": results[-1].get("state") if results else route.get("state"),
                    "result": "helper-executed; source baseline and scoped-progress adapter used before and after disposable effects",
                    "limitations": ["Reviewer payload is a deterministic contract fixture; native independent-agent launches and manual-prompt comparison remain separate cases.",
                                    "Owner-source checks use deterministic disposable fixtures; no external owner write was performed."]}
        outcomes.append(observed)
    connected_positive_traces = _exercise_connected_positive_traces(
        controller_module, consumer, fixture_path, capture_command)
    lifecycle_receipt_readback = _exercise_lifecycle_receipt_readback(controller_module, consumer)
    task_revision_successor = _exercise_installed_task_revision_successor(
        controller_module, consumer, capture_command)
    provenance = _portable_matrix_provenance(consumer, controller_module, workflow_path, fixture_path)
    portable_observations = _portable_matrix_observations(
        fixture, outcomes, connected_positive_traces, lifecycle_receipt_readback, provenance, consumer)
    _write_portable_matrix_observations(os.environ.get("FARMBOY_T019_EVIDENCE_PATH"), provenance,
                                        portable_observations)
    post_pass_state = task_revision_successor["post_pass_state"]
    post_pass_assessment = {"state": "continue", "next_step_id": "implement-tasks",
        "reason_code": "reviewed-tasker-successor-ready", "evidence": task_revision_successor["progress"]["evidence"],
        "remaining_ids": list(dict.fromkeys([*task_revision_successor["progress"]["remaining_ids"],
            "task:T003", "finding:F020-R001"])),
        "resolved_ids": task_revision_successor["progress"]["resolved_ids"]}
    rendered_post_pass_prompt, rendered_post_pass = render_execution_bindings({
        "entry": {"scope": post_pass_state["scope"],
            "retained_previous_assessment_sha256": task_revision_successor["retained_previous_assessment_sha256"],
            "previous_assessment": task_revision_successor["previous_assessment"],
            "baseline": task_revision_successor["baseline"]},
        "current_assessment": {"outcome_envelope": post_pass_assessment,
            "review": task_revision_successor["review"]},
        "readiness": {"state": "ready"}, "post_pass_state": post_pass_state})
    if rendered_post_pass["post_pass_state"] != post_pass_state:
        raise AssertionError("final rendered callback did not consume the capture node's current producer packet")
    if post_pass_state["ordered_operations"] != ["session-start", "source-attempt-start", "source-effect",
            "session-outcome", "independent-review", "Tasker-result", "Tasker-validation", "post-pass-capture"]:
        raise AssertionError("post-review producer chronology differs from the current rendered callback")
    task_revision_successor["post_pass_rendered_prompt_sha256"] = hashlib.sha256(
        rendered_post_pass_prompt.encode()).hexdigest()
    return {"schema_version": "1.0", "contract": "implementation-scope-installed-matrix",
            "workflow_sha256": sha(workflow_path),
            "controller_package_version": provenance["components"][0]["version"],
            "cases": outcomes, "connected_positive_traces": connected_positive_traces,
            "lifecycle_receipt_readback": lifecycle_receipt_readback,
            "task_revision_successor": task_revision_successor,
            "provenance": provenance, "portable_observations": portable_observations}
