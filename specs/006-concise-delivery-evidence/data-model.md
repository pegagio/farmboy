# Evidence content model

This describes ordinary document content and relationships; it introduces no runtime model, schema, validation service or persistent register.

| Existing content | Required meaning | Relationship and validation |
|---|---|---|
| Feature delivery summary | Tested revision or base plus working delta; performed checks/outcomes; repairs/rechecks; material limits; actual decisions/conditions or pending review | Required evidence references point here or to other retained required artifacts. No claim exceeds observed source/execution. |
| Reusable verification asset | Code, controlled inputs, expected outputs and repeat instructions | Together let a reviewer rerun the fixture without its old output. Portable, deterministic and free of private identities. |
| Disposable execution output | Raw logs/stdout, transcripts, runtime state and redundant intermediate reports | Optional diagnostic reference only. Normally outside Git; deletion cannot remove sole support for required claims. |
| Human decision in existing notes | Relevant role, actual approved content/checkpoint, conditions and limits, or pending status | Fixture decisions are TEST ONLY. Silence/checks/Goal completion cannot become approval. |

No new lifecycle transition is defined. Existing Awaiting result review and required-input stops retain their meaning. Material changes invalidate affected evidence/review; historical approval remains historical. Durable exceptions require a stated project rule or concrete essential need and minimal privacy-safe content; unresolved conflict stops dependent closeout.
