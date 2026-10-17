# Prepare a specification draft

`$farmboy-prepare-specification` selects a named/next-eligible roadmap feature, queries relevant context and saves a specification draft, quality findings and roadmap brief. Automation ends with **Needs clarification** or **Awaiting spec review**. It does not stay active waiting for human answers.

## Use and prerequisites

Supply a supported Spec Kit project with its own rules, roadmap/wiki, effective spec template, feature setup/pointer helpers and installed roadmap-write/wiki-query/roadmap-brief capabilities. The only Farmboy runtime source is `.agents/skills/farmboy-prepare-specification/SKILL.md`; copy that directory into a supported project’s standard `.agents/skills/` location, preserving unrelated skills. There is no installer or additional configuration system.

Invoke ordinarily with “Use $farmboy-prepare-specification for feature 001.” To validate native Goals, the objective must end at drafting/handoff, for example:

```text
/goal Use $farmboy-prepare-specification for the selected test feature. Save a usable specification draft, actual quality/fit findings and an explicit Needs clarification or Awaiting spec review handoff. Finish this Goal at that handoff, before clarification answers or human approval. Do not plan, approve or implement.
```

This is an objective example, not proof that the installed host can complete it. Existing specify may ask questions before finishing, so this drafting skill uses resolved templates/setup rather than invoking the full interactive command and bypassing its requirements. Missing supported capability or a governing conflict is a blocker.

## Clarify, review and plan

At **Needs clarification**, separately invoke existing `$speckit-clarify` ordinarily after the preparation Goal is complete. It asks actual questions and genuinely waits; supported focused rounds preserve command/platform limits. No additional Farmboy clarification skill is needed. After clarification, reconcile affected findings/brief through existing capabilities and present **Awaiting spec review**. Review can return to clarification. The human chooses review depth; explicit approval is still prerequisite for **Ready for planning**. No planning follows by inference or from this preparation invocation.

Handoff labels use existing spec notes, not a new schema or Diagram state store. Resume revalidates target/current artifacts and the correct stage without duplicate activation or resurrecting a completed Goal to wait for input. Manual template-based drafting and ordinary core clarification remain available.

## Verification status

Independent disposable-project observations demonstrate the revised ambiguous and settled handoffs, native Goal completion observed by the operator and corroborated by session history, ordinary core clarification with a real question/answer/review stop, and explicit test-only approval recognition without planning. The settled revised case revalidates an existing draft; earlier recorded tests cover named/eligible creation, negative selection and changed-artifact/input resume. The API does not expose a native Goal-state receipt. The earlier combined Goal design stalled at unanswered input and remains a historical failure; automatic suspension/resumption across human waits is not supported by this delivery claim.

After ordinary clarification changes a draft, separately use `$speckit-flow-roadmap-brief` with its exact feature target to refresh any stale fit evidence before relying on it for current human review. Core clarify can disclose that manual next step; no additional hook or clarification skill is required.

See [actual evidence and limits](../specs/001-prepare-specification/validation/acceptance.md) for runtime versions, source hashes and final checks. This first workflow does not establish acceptance of the later planning/delivery workflows or the full three-segment Farmboy lifecycle.
