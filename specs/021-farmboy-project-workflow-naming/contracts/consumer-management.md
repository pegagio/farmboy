# Contract: Existing Management Behavior After Cutover

The pure rename keeps existing management interfaces and semantics. This contract replaces the earlier consumer-migration design; it defines no new runtime operation.

## Existing Interfaces

`catalog:install`, `catalog:refresh`, `catalog:remove`, `catalog:agents` and native Specify commands keep their existing options and behavior. Applicable owned package IDs and paths change according to [naming.md](naming.md); the native bundle identity becomes `farmboy`. Owned feedback extension/command identities and the delegation metadata key follow the same pure-cutover mappings; capture/report/intake semantics remain unchanged. Maintainer intake remains a separate package outside generic bundle delivery.

Existing native component ownership, digest-owned controller files, consumer-owned agent copies and evidence-preservation rules remain unchanged. The rename does not redesign conflict handling, file writes, rollback or retry behavior already present in those interfaces.

## Cutover Boundary

The new source and fresh supported installation use FarmBoy names without old-name invocation aliases. This feature provides no upgrade of an old installation and no consumer-customization transfer. Operators handle replacement of personal installations outside this feature; actual consumer operations require their own instructions.

No migration command/flags, compatibility adapter, legacy conversion reader, migration journal, new status protocol, adoption detector or new recovery orchestration is added. No existing consumer is modified by merely reading or using the source checkout.

## Validation

Use existing install/refresh/remove and agent-delivery tests with renamed expectations, plus a fresh disposable consumer. Preserve existing ownership and protection assertions. No old-installation migration matrix, checkpoint compatibility or migration failure/retry tests are required.
