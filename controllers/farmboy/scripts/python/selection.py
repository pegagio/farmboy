"""Pure feature-reference resolution for selection workflows."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Literal


ReferenceKind = Literal["auto", "stable-id", "exact-title", "menu-position", "canonical-answer"]
_STABLE_REFERENCE = re.compile(r"^(?:feature\s*|f)?\s*0*(\d+)$", re.IGNORECASE)
_MENU_REFERENCE = re.compile(r"^(?:(?:option|menu)\s+)?(\d+)$", re.IGNORECASE)


@dataclass(frozen=True)
class SelectionResult:
    """Describe a unique feature match or a safe reason to stop."""

    state: Literal["selected", "ambiguous", "missing", "blocked"]
    selected_entry_id: str | None
    match_method: str | None
    candidate_ids: tuple[str, ...]
    reason_code: str

    def to_dict(self) -> dict[str, Any]:
        """Return a stable, JSON-compatible result envelope."""
        result = asdict(self)
        result["candidate_ids"] = list(self.candidate_ids)
        return result


def _inventory(entries: Any, menu_order: Any) -> tuple[list[dict[str, str]], list[str]] | SelectionResult:
    if not isinstance(entries, list) or not entries:
        return _blocked("feature-inventory-invalid")
    normalized: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            return _blocked("feature-inventory-invalid")
        entry_id = entry.get("id", entry.get("entry_id"))
        title = entry.get("title")
        if not isinstance(entry_id, str) or not entry_id.isdigit() or not isinstance(title, str) or not title.strip():
            return _blocked("feature-inventory-invalid")
        entry_id = str(int(entry_id)).zfill(max(3, len(entry_id)))
        if entry_id in seen_ids:
            return _blocked("feature-inventory-duplicate-id", [entry_id])
        seen_ids.add(entry_id)
        normalized.append({"id": entry_id, "title": title.strip()})

    if not isinstance(menu_order, list) or any(not isinstance(item, str) for item in menu_order):
        return _blocked("feature-menu-order-invalid")
    menu_ids = [str(int(item)).zfill(max(3, len(item))) if item.isdigit() else item for item in menu_order]
    if len(menu_ids) != len(set(menu_ids)) or any(item not in seen_ids for item in menu_ids):
        return _blocked("feature-menu-order-invalid")
    return normalized, menu_ids


def _blocked(reason_code: str, candidate_ids: list[str] | None = None) -> SelectionResult:
    return SelectionResult("blocked", None, None, tuple(candidate_ids or ()), reason_code)


def _stable_matches(reference: str, entries: list[dict[str, str]]) -> list[str]:
    match = _STABLE_REFERENCE.fullmatch(reference.strip())
    if match is None:
        return []
    number = int(match.group(1))
    return [entry["id"] for entry in entries if int(entry["id"]) == number]


def _title_matches(reference: str, entries: list[dict[str, str]]) -> list[str]:
    folded = reference.strip().casefold()
    return [entry["id"] for entry in entries if entry["title"].casefold() == folded]


def _menu_match(reference: str, menu_order: list[str]) -> list[str]:
    match = _MENU_REFERENCE.fullmatch(reference.strip())
    if match is None:
        return []
    position = int(match.group(1))
    return [menu_order[position - 1]] if 1 <= position <= len(menu_order) else []


def _ordered_candidates(candidates: set[str], entries: list[dict[str, str]]) -> tuple[str, ...]:
    order = {entry["id"]: index for index, entry in enumerate(entries)}
    return tuple(sorted(candidates, key=lambda item: (int(item), order[item])))


def resolve_feature_reference(
    reference: str,
    reference_kind: ReferenceKind,
    entries: list[dict[str, Any]],
    menu_order: list[str],
) -> SelectionResult:
    """Resolve a stable ID, exact title, explicit menu position, or canonical answer.

    The resolver has no filesystem or mutation side effects. `menu_order` contains
    feature IDs in the order shown to the operator; it never changes stable-ID
    interpretation for generic approval menus.
    """
    if not isinstance(reference, str):
        return _blocked("feature-reference-invalid")
    if reference_kind not in {"auto", "stable-id", "exact-title", "menu-position", "canonical-answer"}:
        return _blocked("feature-reference-kind-invalid")
    if not reference.strip():
        return SelectionResult("missing", None, None, (), "feature-reference-missing")

    inventory = _inventory(entries, menu_order)
    if isinstance(inventory, SelectionResult):
        return inventory
    normalized_entries, normalized_menu = inventory
    value = reference.strip()
    if value.casefold() == "defer":
        return _blocked("feature-selection-deferred")

    if reference_kind == "stable-id":
        matches = _stable_matches(value, normalized_entries)
        return _selected_or_missing(matches, "stable-id")
    if reference_kind == "exact-title":
        matches = _title_matches(value, normalized_entries)
        return _selected_or_missing(matches, "exact-title")
    if reference_kind == "menu-position":
        matches = _menu_match(value, normalized_menu)
        return _selected_or_missing(matches, "menu-position")
    if reference_kind == "canonical-answer":
        stable_matches = _stable_matches(value, normalized_entries)
        title_matches = _title_matches(value, normalized_entries)
        return _resolve_candidates(stable_matches + title_matches, "canonical-answer")

    stable_matches = _stable_matches(value, normalized_entries)
    title_matches = _title_matches(value, normalized_entries)
    menu_matches = _menu_match(value, normalized_menu) if value.isdigit() else []
    combined = set(stable_matches + title_matches + menu_matches)
    if len(combined) > 1:
        return SelectionResult(
            "ambiguous", None, None, _ordered_candidates(combined, normalized_entries), "feature-reference-conflict"
        )
    if not combined:
        return SelectionResult("missing", None, None, (), "feature-reference-not-found")
    methods = []
    selected_id = next(iter(combined))
    if selected_id in stable_matches:
        methods.append("stable-id")
    if selected_id in title_matches:
        methods.append("exact-title")
    if selected_id in menu_matches:
        methods.append("menu-position")
    method = methods[0] if len(methods) == 1 else "stable-id-and-menu-position" if set(methods) == {"stable-id", "menu-position"} else "+".join(methods)
    return SelectionResult("selected", selected_id, method, (selected_id,), "feature-reference-selected")


def _selected_or_missing(matches: list[str], method: str) -> SelectionResult:
    if not matches:
        return SelectionResult("missing", None, None, (), "feature-reference-not-found")
    return _resolve_candidates(matches, method)


def _resolve_candidates(matches: list[str], method: str) -> SelectionResult:
    unique = tuple(dict.fromkeys(matches))
    if not unique:
        return SelectionResult("missing", None, None, (), "feature-reference-not-found")
    if len(unique) > 1:
        return SelectionResult("ambiguous", None, None, unique, "feature-reference-ambiguous")
    return SelectionResult("selected", unique[0], method, unique, "feature-reference-selected")
