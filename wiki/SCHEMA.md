# Wiki Schema

This file defines how this wiki is structured and maintained. Edit it to
change the rules; `/speckit.flow-wiki.*` commands read it before writing anything.

## Scope
1. Farmboy’s development decisions, governing constraints and agreed delivery direction, with intended outcomes kept distinct from demonstrated capabilities.

## Page types
| Type | Holds | Example title |
|------|-------|---------------|
| concept | domain ideas and definitions that outlive any feature | "Idempotency keys" |
| decision | choices made, alternatives rejected, and why | "Why SQLite over Postgres" |
| component | how a part of the system actually works | "Auth middleware" |
| reference | distilled external facts (APIs, papers, vendor limits) | "Stripe rate limits" |
| howto | procedures that took effort to figure out | "Local TLS setup" |

## Rules
- Pages live in `pages/`, one topic per page, kebab-case filenames.
- Every synthesized claim cites a source ID from `sources.md` (e.g. `(S003)`).
- Pages cross-reference with relative links: `[title](./other-page.md)`.
- A page that outgrows 600 words is split, and both halves link to each other.
- Conflicting claims are kept side by side under a `> ⚠ conflict:` marker
  until resolved — never silently overwritten.
- Frontmatter per page: `title`, `type`, `sources`, `updated` (ISO date).

## Maintenance workflows
- Grow: `/speckit.flow-wiki.ingest <source>` — the only way knowledge enters.
- Use: `/speckit.flow-wiki.query <question>` — answers come from pages, cited.
- Check: `/speckit.flow-wiki.lint` — drift, orphans, contradictions, staleness.
- Resume: `/speckit.flow-wiki.status` — the session-resume entry point.
