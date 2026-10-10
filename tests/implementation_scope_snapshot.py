"""Installed-consumer execution of the deterministic SI001-SI015 route matrix."""
from __future__ import annotations

import hashlib
import json
import re
import shlex
import subprocess
from pathlib import Path
from typing import Any


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
                  outcome: str | None = None, same_child_resume: bool = False) -> dict[str, Any]:
    node = "prepare-scoped-prerequisites" if execution_kind == "preparation" else "implement-tasks"
    item: dict[str, Any] = {
        "event_id": f"{case_id}-{len(history['events']) + 1}",
        "predecessor_sha256": history["events"][-1]["sha256"] if history["events"] else "0" * 64,
        "scope_sha256": scope_payload["scope"]["scope_sha256"],
        "event_kind": event_kind, "declared_node_id": node,
        "occurred_at": f"2026-10-08T12:{session:02d}:{attempts:02d}Z",
        "evidence": _evidence(consumer, case_id, f"event-{len(history['events']) + 1}"),
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
                             capture_observation: dict[str, Any] | None = None) -> dict[str, Any]:
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
                               capture_output=True, check=False)
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
        previous_assessment_path = feature_dir / "validation/pre-source-assessment.json"
        previous_assessment_path.parent.mkdir(parents=True, exist_ok=True)
        previous_assessment_path.write_text(json.dumps({"baseline_sha256": baseline_capture["baseline_sha256"],
            "remaining_ids": baseline_capture["remaining_ids"], "source_preimage_sha256": source_preimage_sha256},
            sort_keys=True) + "\n", encoding="utf-8")
        revision_previous_assessment = {"state": "continue", "next_step_id": "implement-tasks",
            "reason_code": "pre-source-frozen-findings",
            "evidence": [{"path": f"{feature}/validation/pre-source-assessment.json",
                "sha256": sha(previous_assessment_path)}],
            "remaining_ids": baseline_capture["remaining_ids"], "resolved_ids": []}
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
        previous_assessment = {"state": "continue", "next_step_id": "implement-tasks",
            "reason_code": "pre-source-finding-open", "evidence": current_source_evidence,
            "remaining_ids": baseline_capture["remaining_ids"], "resolved_ids": []}
        scoped_progress = controller_module.validate_scoped_implementation_progress(consumer, {
            "controller_loop_mode": "implementation_scope", **history_payload,
            "retained_history_sha256": history["sha256"], "assessment": current_assessment,
            "eligible_task_ids": ["T002"],
            "declared_node_ids": ["prepare-scoped-prerequisites", "implement-tasks"],
            "previous_assessment": previous_assessment, "progress": progress_payload,
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
            "previous_assessment": previous_assessment, "progress": completion_progress_payload,
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
                    "frozen_baseline", "post_pass_state"}
        if set(bound) != expected or any(not isinstance(value, (dict, list)) for value in bound.values()):
            raise AssertionError(f"rendered scoped callback fields differ: {sorted(bound)}")
        return rendered, bound

    route_execution_prompt, _ = render_execution_bindings({"entry": {"scope": {}, "eligibility": {}, "history": {},
        "task_tracking_successors": [], "previous_assessment": {}, "baseline": {}},
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
                proof = {"task_id": task_id, "task_description_sha256": record["description_sha256"],
                         "completion_kind": kind, "scope_sha256": scope["scope_sha256"],
                         "requirements": [{"requirement_id": requirements[0], "satisfied": True, "evidence": ev}],
                         "proof_evidence": ev,
                         "review_evidence": {"reviewer": "FarmBoy Code Reviewer", "verdict": "complete",
                                             "reference": f"deterministic-review-{case_id}-{task_id}", "sha256": "c" * 64}}
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

        def run_scoped_progress(current_history: dict[str, Any], *, entry_history: dict[str, Any], case_name: str) -> dict[str, Any]:
            post_source_before = sha(source_effect_path)
            if case_name not in {"SI005", "SI011"}:
                source_effect_path.write_text(f"after correction {case_name}\n", encoding="utf-8")
            if case_name in {"SI002", "SI005"}:
                chronology_operations.append({"operation": "selected-source-effect",
                    "task_id": selected_source_task, "before_sha256": post_source_before,
                    "after_sha256": sha(source_effect_path), "history_sha256": current_history["sha256"]})
            current_source = [{"path": f"{feature}/{source_effect_path.name}", "sha256": sha(source_effect_path)}]
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
                    "previous_assessment": previous_assessment, "baseline": baseline_capture["baseline"]},
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
    task_revision_successor = _exercise_installed_task_revision_successor(
        controller_module, consumer, capture_command)
    post_pass_state = task_revision_successor["post_pass_state"]
    post_pass_assessment = {"state": "continue", "next_step_id": "implement-tasks",
        "reason_code": "reviewed-tasker-successor-ready", "evidence": task_revision_successor["progress"]["evidence"],
        "remaining_ids": list(dict.fromkeys([*task_revision_successor["progress"]["remaining_ids"],
            "task:T003", "finding:F020-R001"])),
        "resolved_ids": task_revision_successor["progress"]["resolved_ids"]}
    rendered_post_pass_prompt, rendered_post_pass = render_execution_bindings({
        "entry": {"scope": post_pass_state["scope"],
            "previous_assessment": {"state": "continue", "reason_code": "prior-assessment",
                "evidence": task_revision_successor["progress"]["evidence"],
                "remaining_ids": [f"finding:{item['id']}" for item in task_revision_successor["baseline"]["findings"]],
                "resolved_ids": []},
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
            "workflow_sha256": sha(workflow_path), "controller_package_version": "0.8.0",
            "cases": outcomes, "task_revision_successor": task_revision_successor}
