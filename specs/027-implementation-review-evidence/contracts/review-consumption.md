# Review consumption behavior contract

This contract describes observable behavior of existing skill interfaces. It adds no command arguments, JSON packet, report format or native API.

## Inputs and responsibility

Ordinary delivery receives the selected feature/workspace and applicable explicit specification/full-plan approvals. Generic Farmboy delivery establishes applicability, reads committed evidence and assesses findings. Optional adapter locates authoritative Diagram references and supplies existing context; Diagram retains state/approval authority. Consumer verifies actual Git bytes/association separately from native consistency checks.

For example, approval may identify `specs/001-example/validation/plan-review.md` at a real commit with its supplied SHA-256; that existing report identifies its reviewed proposal and O1/O2. These are illustrative references, not actual authority or required fields. Later routine commits may preserve approved meaning with applicability evidence.

## Entry behavior

Before implementation/setup effects, resolve all reports supporting current approval, verify committed path/digest/feature/candidate, read full contents and assess status with resolution evidence. Required-but-unidentifiable, corrupt, wrong-feature/candidate, contradictory or ambiguous evidence stops precisely. Never choose by date/filename/location; modified working bytes cannot replace committed evidence. Consume multiple authoritative reports as needed to interpret approval and relevant resolution/supersession.

Non-Diagram applicability requires report-bearing approval or a governing report requirement. If neither exists, record not applicable and proceed under ordinary approvals. If required but unavailable, stop. This adds no Diagram lookup or bare-core-command authority.

## Findings and stops

Interpret existing report meaning without adding a parser or automatic classifier.

| Evidence example | Behavior |
|---|---|
| Current required R1 unresolved despite approval | Stop before implementation; identify inconsistent references. |
| Explicit high-priority blocker unresolved | Same stop. |
| Low-priority required correction unresolved | Same stop; severity cannot waive obligations. |
| Explicit high-priority non-blocking O1, no defect/unmet obligation | Consider voluntarily; priority alone cannot block/compel adoption. |
| Historical R1 with applicable explicit resolution/supersession evidence | Do not block solely on historical text; retain evidence relationship. |
| An unmet obligation is called optional, or resolution is merely asserted | Stop on unresolved contradiction/status; no implementer relabeling. |

A stop saves exact missing evidence/question and performed work in ordinary notes, preserves work and uses existing incomplete/release rules. It creates no approval/revocation, plan repair, return transition, automatic re-review or successful delivery.

## Optional decisions and resume

Consider every optional item before its related implementation decision. By closeout notes might say: “Review O1 adopted: approved T003 covers this bound, now implemented and checked. O2 declined: alternative storage is outside this approved delivery.” Both claims must describe actual evidence/work. Considered but unimplemented advice cannot be called adopted just to fill a note.

No suggestions needs only none. Resume reuses valid decisions without duplicate notes/work, reassesses relevant changes and preserves history. Adoption stays within authority and reconciles current artifacts; material changes retain affected human gates. Declining genuine advice requires no extra approval or polishing cycle and cannot waive an actual obligation.

## Outputs and exclusions

Existing delivery/closeout notes retain considered evidence, findings consistency, decisions and limitations. Adapter retains one body invocation and role-correct native recording/release. No core skill, report production, approval semantics, native schema, launcher/control or live consumer changes. Missing capability stops, never grants installation/external patch authority.
