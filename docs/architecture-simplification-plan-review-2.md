# Architecture Simplification Plan — Independent Review 2

- Date: 2026-08-30
- Reviewed plan: `docs/architecture-simplification-plan.md`, draft 1
- Frozen implementation checkpoint:
  `957add991347e94443014cf97079d72713fb05c2`
- Canonical tree: `978953001923f91cbbaf01495b4450602cb26d86`
- Review method: three independent read-only reviews covering security,
  cognitive architecture, and execution/release readiness
- Combined verdict: **needs major revision**

This file preserves review 2 as historical evidence. It should not be edited to
match later plan revisions. Accepted findings are reconciled in draft 2 of
`architecture-simplification-plan.md`.

## Executive assessment

The simplifying direction remains worthwhile. The strongest parts of draft 1
are:

- distinct HTTP and editor capabilities;
- one coherent transport snapshot;
- per-peer futures with one global pending budget;
- structural update staging before disable;
- producer-first archive validation;
- refusing file splits that remove no owner;
- conditional JSONC and command-catalog work;
- rebuild-up rather than treating the maximal tree as required architecture.

Draft 1 is not implementation-ready. Its central compatibility model confuses
the unreleased checkpoint protocol with v3.2.4, applies new updater guarantees
to historical runners that cannot provide them, and names several owners
without defining a collaboration graph that actually reduces mutable state.
Its final release and smoke gates are also not executable against the exact
signed candidate before publication.

## P0 findings — must change before implementation planning

### R2-1. The released transport premise is false

Draft 1 said every released plugin through v3.2.4 requires the checkpoint's
five-field proof ACK. Exact tag history proves otherwise.

At tag v3.2.4:

- `plugin/addons/godot_ai/connection.gd` sends one metadata-bearing
  `handshake` first, with an optional plaintext auth token;
- after repeated 4003 closes, that client can retry without the token;
- it accepts a two-field ACK containing only `type` and `server_version`;
- `src/godot_ai/transport/websocket.py` accepts the old handshake shape and
  emits that two-field ACK.

The challenge, server-possession proof, client proof, and five-field final ACK
exist only in the unreleased frozen checkpoint. Both the v3.2.4 tag and the
checkpoint still report plugin version 3.2.4, which caused the mistaken
compatibility claim.

Consequences:

- v3.2.4 plugin → first secure server fails because the old client sends a
  handshake while the new server waits for `auth_hello`;
- first secure plugin → v3.2.4 server fails because the new client waits for a
  challenge the old server never emits;
- making either cross-pair interoperate in normal mode would weaken T3;
- no released client creates a five-field-ACK compatibility floor;
- the final ACK proof can be retained or removed before the first secure
  release on its actual security merits.

The compatibility matrix must state expected outcomes. Bounded fail-closed plus
actionable matching-version replacement is safer than dual-protocol normal
mode. The explicit legacy bypass remains an operator decision, never an
automatic fallback.

### R2-2. Historical updater generations cannot satisfy unqualified U1/U2/U3

An already-released runner cannot acquire future authentication or transaction
semantics.

Verified history:

- v2.7.6 verifies a checksum only when the same-channel sidecar is present;
  that is integrity checking, not embedded-key authentication;
- signature enforcement first appears in v3.0.0, with `2.9.3` used as a target
  version threshold rather than a release tag;
- v3.2.4 installs only ZIP-listed new/existing paths, so old-only files remain;
- v3.2.4 deletes per-file backups and writes `success` before filesystem scan
  and plugin enable;
- historical clients query the latest release and may skip any intended bridge
  version.

Therefore:

- U1 embedded-key authentication can only be guaranteed for sufficiently new
  initiating runners;
- U2 exact-tree deletion can only be guaranteed for a hardened runner;
- U3 readiness-gated backup retention can only be guaranteed for a hardened
  runner;
- every public candidate must still be directly overlay-safe when installed by
  every historical runner the project continues to support;
- a two-release transition alone is insufficient because a dormant install can
  skip the first transition release.

The ledger must split hardened-runner guarantees from legacy-base
compatibility. Legacy support means asset and direct-install safety, not
retroactive authentication or transactionality.

### R2-3. P11 needs an explicit multi-record, cross-release protocol

Draft 1's event order was impossible. New-plugin startup writes a readiness
receipt before the old detached runner can validate it and write the terminal
result. A one-shot startup result drain has already run by then.

The minimum coherent protocol is:

```text
activation intent/journal
    -> new-code main-thread readiness receipt
    -> old-runner activation result
    -> bounded post-start claim/consumption
```

The new plugin must enter a bounded post-activation startup barrier, emit a
receipt independent of server recovery, await/claim the result, then start
normal lifecycle work. A missing receipt causes rollback; it does not produce
`success` or arm stale-server replacement.

This protocol only becomes enforceable when the initiating runner already
implements it. A legacy-initiated install follows the documented weaker path.

### R2-4. U4's current marker is global and non-atomic

The checkpoint uses a global EditorSettings key. The plugin peeks it before
server start, then telemetry later drains it with separate read and clear
operations. It has no project/install identity and no interprocess claim.

Two editors can observe or consume the same marker, and the wrong project can
inherit a user-authorized replacement budget.

The target needs:

- a canonical project/install-root identity;
- a project-local sibling result or journal;
- atomic rename-to-claim or an interprocess lock;
- schema, transaction, target-version, and terminal-status validation;
- one immutable `PostUpdateOutcome` fanned to lifecycle, telemetry, and repin;
- a bounded post-start consumer rather than a one-shot startup drain.

Legacy global markers may remain telemetry evidence. They must not arm U4.

### R2-5. Exact signed-candidate verification cannot currently precede publish

The desired release gate is not wired into the current workflow:

- `script/local-self-update-smoke` bypasses release discovery and real
  signature verification;
- signing tests use a throwaway private key;
- historical integration coverage is opt-in, incomplete, and does not prove a
  successful modern transition;
- `release.yml` signs on a version tag and then automatically publishes to
  PyPI and GitHub;
- no historical/live/manual gate runs against the exact private signed bytes
  between signing and publication;
- `verify-signing.yml` reads an environment-scoped secret without declaring
  the `release-signing` environment;
- `bump-and-release.yml` pushes the version commit/tag before the full final
  evidence is bound to that exact SHA.

Prepare/sign must be separated from publication. The exact private artifact
digests must pass historical/current consumers and the manual smoke matrix,
then those identical bytes may be published without rebuilding or repacking.

### R2-6. Preservation is complete; draft 1's blocker text is stale

The complete dirty tree is now frozen at commit `957add9`, with:

- annotated local tag
  `checkpoint/architecture-hardening-2026-08-30-draft1`;
- canonical 743-file tree manifest;
- verified complete Git bundle;
- content-only source archive;
- SHA-256 hashes and recovery commands in
  `/Users/davidsarno/Documents/godot-ai/checkpoints/architecture-hardening-2026-08-30-957add9.md`.

No baseline gauntlet is yet attributed to the checkpoint; that remains a
separate validation phase.

## P1 findings — architecture or execution must become concrete

### R2-7. Model three independent authorities

Transport capability, process ownership, and user-authorized replacement are
not interchangeable.

The target needs explicit values:

- `TransportAuthority`: proves the endpoint speaks for the launch identity;
- `OwnedProcessGrant`: proves which process this owner may stop/reap;
- `ReplacementAuthorization`: one bounded, user-derived grant to replace a
  brand/version-proved stale server after update.

Server-published PID is diagnostic and never creates ownership. External
adoption can preserve transport authority while surrendering process ownership.
Python's `BackendEnsurer` and lease-aware self-reapers remain independent
process owners and must appear in the ownership map.

### R2-8. Windows does not yet prove the broad other-local-user claim

POSIX code enforces owner/mode/link checks. Windows currently relies on
inherited ACLs and skips equivalent directory/record privacy checks; GDScript
accepts any openable non-link path, and relevant tests are skipped.

The plan must either:

- implement and integration-test DACL and reparse-point policy;
- reject unverifiable Windows directory overrides and retain a narrower
  documented default-path guarantee; or
- explicitly narrow the threat claim on Windows.

### R2-9. `UpdateCoordinator` ownership is missing from the phase map

The Dock currently creates the update manager. The manager stores both Dock
and plugin references, drains Dock-owned worker state, and calls back into the
plugin. The plugin then passes a detached Dock into the runner.

Phase 5 changes activation, while Phase 7 later moves client workers, which
would rewire this seam twice.

An early owner tranche must:

- root-own `UpdateCoordinator` outside the Dock;
- define a reload-stable client-work quiescence interface;
- assign detach/reattach responsibility;
- hand only value data and explicit effect ports to activation;
- sequence before updater and client-workflow refactors.

### R2-10. `ServerSupervisor` risks becoming a larger god object

The existing lifecycle manager is already roughly 2,227 lines with 69
functions, 28 instance fields, and multiple orthogonal retry, recovery,
generation, watcher, and worker states.

Absorbing another 25–30 responsibilities is not simplification by itself. The
target needs a smaller explicit episode/reducer model and narrow effect ports.
Admission must require fewer mutable fields, writer sites, reachable state
combinations, and host callbacks—not merely a new class name.

### R2-11. Client workflow and launch-policy ownership are conflated

`client_configurator.gd` also owns server ports/settings, attach command
resolution, server-command selection, prewarm, and toolchain caches. These are
shared with lifecycle, not merely client-file mutation.

Extract an immutable `LaunchPlan`/policy builder shared by supervisor and
client entry construction. Pass immutable server-health and update-phase
snapshots into client workflows. Assign reload-surviving worker, orphan, and
cancellation state currently held statically by Dock.

### R2-12. Registry-only session writes need an enforceable API

`SessionRegistry.get`, `get_active`, and `list_all` expose mutable `Session`
objects. WebSocket handling, readiness handlers, and `GodotClient` mutate
session fields or counters directly.

Phase 4 must require:

- frozen/private session state;
- immutable session snapshots for readers;
- registry methods for all mutations and diagnostic consumption;
- atomic peer/session registration and removal;
- an explicit owner of the `session_id -> EditorPeer` collection.

### R2-13. Rebuild-up needs a proof and branch DAG

The checkpoint is one 171-file preservation commit. Most work cannot be
cherry-picked by provenance. “Latest main” is also not a reproducible base.

Before rebuild-up:

- pin a landing-base SHA;
- create a hunk/dependency/tranche manifest for shared files;
- maintain a dedicated oracle-proof branch;
- pair tests with each implementation tranche;
- record expected-red/current-green/expected-difference evidence;
- sync main only between immutable green tranche checkpoints;
- use range-diff after each sync;
- define explicit pass and intentional-difference lists per tranche.

### R2-14. LOC ranges are gross opportunities, not credible net promises

Draft 1 did not subtract required journal, receipt, result-claim, repair,
snapshot, peer, budget, supervisor, resolver, policy, and harness code. Some
updater work may be net-positive while still reducing dangerous states.

The plan needs a checked-in measurement method and must report, per tranche:

- production additions, deletions, and net;
- mutable fields and writer sites;
- reachable transition states;
- dependency edges/cycles and component fan-in/fan-out;
- callbacks/host members and private dependency seams;
- test additions/deletions separately.

Do not publish a total net-reduction promise until skeleton prototypes and the
required safety additions are measured.

### R2-15. `save_to_disk` response shaping may be useful centralization

Its arguments currently centralize non-undoable reasons, overwrite results,
cleanup hints, path keys, and partial-commit semantics across nine callers.
Moving all shaping into handlers may distribute D2 honesty.

Narrow this only if a prototype demonstrates net deletion while retaining one
standard response-contract helper.

### R2-16. Phase 2 and final harness gates are not executable yet

Draft 1 asks Phase 2 to execute producer, receipt, journal, and orphan contracts
before their pure seams exist. The manual smoke has no deterministic failpoints
for disable refusal, rename boundaries, readiness timeout, rollback failure, or
process kill. Stress passes when the editor remains reachable even if errors or
latency are excessive.

Build the harness/proof substrate first. Define:

- named failpoints and log barriers;
- expected tree/marker/journal hashes;
- retained artifacts and restart actions;
- no skip on missing release-gate assets;
- fixed stress seeds/topologies/workloads/durations;
- allowed error codes and windows;
- error-rate/latency ceilings;
- pending/session/process/capability leak checks;
- report retention.

## Outstanding PR ledger at review time

All six PRs were open and non-draft on 2026-08-30:

| PR | Head SHA | Merge state | Draft-1 lane issue |
|---|---|---|---|
| #936 | `537a490c865837bedb96042d10ee0fc74673cd99` | UNSTABLE | Explicit Phase 3 lane exists |
| #927 | `1a95bcca51d81d29de925c2f636814eaa037c1c2` | UNSTABLE | Explicit Phase 3 lane exists |
| #930 | `ea79e5a3735198d3be9d562871fddcb0a699bf0a` | UNSTABLE | P5 must precede port/disposition |
| #892 | `d16770c017f106d7035d9a1d59479bb0e3693668` | CLEAN | No explicit landing lane |
| #934 | `5880005515e5fc234ed75f36c1b1cdd3f4595d0d` | UNSTABLE | Explicit persistence lane exists |
| #931 | `418fb5e2eec516f2b34251f0034dc37fe26e680c` | UNSTABLE | No explicit landing lane |

#936/#927 have exact stable-patch equivalents in the checkpoint. The other
four are reworked inside the maximal integration. #892 and #934 overlap seven
files; #931 overlaps server/plugin work with both. Phase 0 must record canonical
head, supersede/port/exclude decision, dependency order, and destination lane.

## Historical updater facts to correct

- v2.2.0–v2.2.1 reserve none of the future updater names.
- `.godot_ai_update_tmp` begins in v2.2.2.
- The directory-entry-sensitive range is v2.2.2–v2.3.0; v2.3.1 fixes it.
- `.update_backup` begins in v2.4.0.
- v3.2.4 does not reserve `.gdignore`; that updater-root guard is checkpoint-only.
- v2.7.6–v2.9.2 checksum verification is verify-if-present, although continuing
  to publish the sidecar remains prudent compatibility policy.

## Accepted directions

- Keep T1/T2/T5 and the no-automatic-legacy-fallback rule.
- Keep separate HTTP/WS capabilities and server proof before project metadata
  for the first secure protocol.
- Keep explicit-input capability pinning and coherent snapshot rotation.
- Keep per-peer futures with a global 128-entry budget.
- Keep structural staging before disable for hardened runners.
- Keep manifest retention for the first hardened release.
- Keep producer-first archive preflight and exact digest handoff to signing.
- Keep a project-scoped journal/result and out-of-tree recovery path.
- Keep `plugin.gd` as a narrow composition root.
- Keep rebuild-up, conditional on a pinned base and proof DAG.
- Keep the shared-listener proposal late and expected-fail.
- Keep cohesive `McpResourceIO`, conditional JSONC restructuring, and a
  conditional authoritative command catalog.

## Required draft-2 disposition

Draft 2 should:

1. mark checkpoint preservation complete;
2. replace the ACK migration narrative with an accurate first-secure-protocol
   decision and fail-closed version matrix;
3. split updater invariants by initiating runner generation;
4. require direct legacy-overlay safety for every supported candidate;
5. define the three-record readiness/result protocol and project-scoped claim;
6. model transport, process ownership, and replacement grants separately;
7. narrow or harden the Windows threat claim;
8. establish root-owned update/quiescence and immutable launch-policy owners;
9. constrain supervisor/registry APIs by measurable state reduction;
10. replace net LOC promises with a checked-in per-tranche measurement method;
11. add exact signed-candidate, deterministic failure, and stress harness
    work before those become release gates;
12. pin the rebuild base/proof DAG and give every outstanding PR an explicit
    disposition lane.

## Verdict

**Needs major revision.** The three decisive reasons are:

1. released transport and updater compatibility were modeled from unreleased
   code;
2. several named owner moves do not yet reduce mutable state or define a
   coherent collaboration graph;
3. the exact signed-artifact and hellacious smoke gates cannot currently run
   before irreversible publication.

The direction remains suitable for another planning iteration. It is not safe
to begin implementation from draft 1.
