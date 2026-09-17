# v4 architecture checkpoints — 2026-09-01

This document records commit-specific checkpoints for PR #943. Documentation-
only commits may follow a checkpoint without changing its measured production
tree. It supplements the historical
[2026-08-31 implementation checkpoint](v4-local-implementation-checkpoint.md)
rather than rewriting that commit-specific evidence. It is not authorization
to tag, upload, or publish a release.

## Signing and attestation setup — owner-approved boundary

The owner approved the narrower repository/credential separation model on
2026-09-01. The public
[attestation repository](https://github.com/dsarno/godot-ai-release-attestations)
now exists; its bootstrap is commit `c39ec40245e83aa2143a0e4361a97eee48407563`.
API readback confirmed `dsarno` is the only collaborator, no deploy keys,
Actions disabled, and main-branch force-push/deletion blocked (including
administrators). This unsigned bootstrap is not a candidate approval or a
separate cryptographic identity; the GitHub owner/provider remain trusted.

`release-signing` now requires `dsarno` approval, disallows administrator
bypass, and permits only the `main` and `v4/architecture-simplification`
branches. Self-review is allowed because the owner may dispatch and approve.
The existing key was copied directly within Actions in
[run 33562599392](https://github.com/hi-godot/godot-ai/actions/runs/33562599392),
then the protected copy passed a fresh synthetic signing verification with
copying disabled in
[run 33562781557](https://github.com/hi-godot/godot-ai/actions/runs/33562781557).
Both ran source `18bcb11` after explicit `dsarno` approval. No private key was
rotated or retrieved into the workspace, chat, logs, or artifacts.

After that success, the repository-scoped `RELEASE_SIGNING_KEY_PEM` and the
environment's temporary `RELEASE_KEY_MIGRATION_TOKEN` secret were deleted.
Metadata readback confirmed neither exists at repository scope and the sole
remaining environment secret is `RELEASE_SIGNING_KEY_PEM`. The one-time transfer
input, shell step, and obsolete transfer tests are retired; the permanent
workflow remains a read-only, human-gated synthetic signing check. The owner
confirmed revocation of the temporary fine-grained GitHub token `godot-toke`
(ID `19038725`) after deleting its Actions secret. See the
[operator runbook](releasing.md#operator-setup-before-candidate-signing).

The prior occurrence-selector commit `531f1bf` passed **32/32 hosted CI jobs**
in [run 33556567537](https://github.com/hi-godot/godot-ai/actions/runs/33556567537).
Setup-batch local validation: Ruff clean; Python **2,266 passed, 9 skipped**;
Godot-backed updater **12 passed**; isolated live Godot **2,128 passed,
24 platform/environment skips, 0 failed**. The first Python run caught two
missing explicit UTF-8 encodings in the new test; both were fixed and the
complete suite rerun successfully. These are development checks, not immutable
release-candidate qualification. The live transfer and fresh signing check
subsequently passed as recorded above.
No final A/B candidates, release approval, or publication exist yet.

The setup commit's [CI run 33560671963](https://github.com/hi-godot/godot-ai/actions/runs/33560671963)
failed only Python 3.13/macOS: the CLI failpoint test parsed canonical filesystem
identity while the actor was renaming the live directory. Cleanup moves that
test's full intent/journal validation after the `stage_live` polling boundary;
production path checks are unchanged. The six retired tests belonged solely
to the deleted one-time transfer mechanism, not updater coverage.

Cleanup validation: Ruff clean; Python **2,260 passed, 9 skipped**; updater
integration **12 passed**; live Godot **2,128 passed, 24 skips, 0 failed**;
the three CLI failpoint cases passed ten consecutive runs (**30/30**).
The first live harness attempt could not connect because a separate client
occupied its inherited ports. The successful run used an intact self-contained
Godot 4.7.2 app copy with isolated settings and ports; no existing client was
stopped and no production source was patched for that run.

### Review follow-up in progress

The latest review was inspected during signing cleanup, not silently marked
addressed. This review tranche disables checkout credential
persistence, drives six-asset discovery through the production callback in the
manual smoke, states the Cherry Studio exception at the migration entry point,
and asserts the complete repin call. It also restricts non-loopback capability
targets to HTTPS and suppresses Retry, including across plugin reload, when
actor termination cannot be proved. Automated and actual-editor regression
checks passed as recorded below; the final manual-smoke gate remains open.

The [Windows qualification report](https://github.com/hi-godot/godot-ai/pull/943#issuecomment-5498715882)
also received direct dispositions in the current tranche: signing streams bytes
through OpenSSL rather than passing its nested output paths; the link fixture
uses a Git index entry and needs no Windows privilege; the supported v3 overlay
path explicitly proves the old autoload remains present; and bridge failures
are emitted to the editor log as well as the dock. The capsule remains a
temporary overlay, not a supported standalone add-on. These fixes do not
constitute exact-candidate qualification.

Review-tranche development validation: Ruff clean; Python **2,268 passed,
11 environment-gated skips**; isolated live Godot **2,128 passed, 24 skips,
0 failed**; actual-editor updater integration **12 passed**; and the changed
migration bridge passed its real-editor failure/reload cases. Godot 4.5 and 4.6
both refused the v4 runtime and migration bridge without mutating the add-on or
project configuration. The prior-head CI run failed only while its test poll
observed the journal's short-lived two-name atomic-publication interval; this
tranche lets that preliminary poll retry the transient identity while retaining
the subsequent full authenticated intent/journal validation. All three CLI
failpoint cases also passed ten consecutive runs (**30/30**). Hosted CI for
this tranche remains pending at commit time.

The operator clicked Update in the disposable manual fixture: the production
discovery/download path selected the canonical triple, the verified plugin
loaded, migration completed durably, and the replacement server authenticated.
The assistant then sent SIGTERM rather than waiting for normal editor Quit;
the wrapper correctly failed with exit `-15`. That is not recorded as a passed
manual smoke. A fresh fixture is awaiting its Update click and normal exit.
Pushing this tested tranche to obtain hosted CI does not close that remaining
merge gate or authorize merging or publishing.

## Qualification preparation — occurrence selector and operator preflight

The first qualification tranche after `666f3e5` adds explicit occurrence
selection to the existing activation/coordinator failpoint adapters. The
controller can now address the second journal commit rather than always
stopping at the first. Normal update behavior and publication remain unchanged.
Production delta for this tranche: **+41 / -7, net +34** Python/GDScript lines;
tests: **+72 / -4, net +68**. The production total is **64,687** lines.

Local development validation (not final candidate qualification):

- Python: **2,260 passed, 9 environment-gated skips**, one existing dependency
  deprecation warning;
- Godot 4.7.2: **2,128 passed, 24 platform/environment skips, zero failures**;
- actual-editor self-update integration: **12 passed**;
- user-performed Update click in the disposable macOS fixture: version and
  server advanced, migration completed durably, external backup retained,
  no new Godot crash report;
- Ruff, import/parse validation, diff hygiene, and all eleven architecture
  gates passed.

Operator preflight on 2026-09-01 found `RELEASE_SIGNING_KEY_PEM` present as a
repository secret, but no environment-scoped key, required reviewer, or
deployment branch policy on `release-signing`. The last synthetic signing
check passed, but that does not establish protected signing. Secure custody of
the original key, the approval identity, and the independent attestation
channel require operator input. Setup is described in
[the release runbook](releasing.md#operator-setup-before-candidate-signing).

The complete external failpoint/real-process matrix, measured storm ceilings,
immutable A/B candidates, qualification/promotion workflow, and both
attestations remain open. These development results do not satisfy the
zero-required-skip exact-candidate gate. No final candidate was signed, no key
was read or changed, and no public artifact was created by this tranche.

## One-click migration implementation

- implementation commits: `07416ef`, plus the narrow hosted-CI restart
  correction `7ba82b0`
- permanent production tree: `64,653` physical Python/GDScript lines
  (`44,650` GDScript and `20,003` Python across 259 files)
- permanent-production delta from the `59,859` baseline: **+4,794 lines**
- temporary signed migration bridge: `706` GDScript lines, packaged only in the
  v3 transition capsule and absent from the canonical/live v4 tree

This change deliberately adds a narrow compatibility capsule rather than
putting v3 branches back into the permanent v4 runtime. The final-v3 updater
authenticates the outer capsule; the bridge authenticates and stages the inner
canonical tree, replaces the complete add-on, gracefully restarts Godot, and
hands the transaction to the clean v4 process. The ordinary user flow is one
**Update** click.

Local exact-commit evidence includes 2,250 passing Python tests (9 environment-
gated skips), all 12 Godot self-update integration rows (including the exact
v3.2.4 button-click path), Godot 4.5/4.6 runtime-and-bridge refusal/no-mutation
smokes, GDScript import validation, Ruff, diff hygiene, and all architecture
simplification gates. The restart correction additionally passed the exact
button-click smoke, 4.5/4.6 refusal smokes, five focused transaction/release
tests, and 31 workflow-policy tests. Hosted exact-head CI at `b6d5655` passed
**32/32 jobs** in [run 33543192056](https://github.com/hi-godot/godot-ai/actions/runs/33543192056),
including the exact final-v3 one-click migration on Linux, macOS, and Windows.

## Prior reviewed head

- branch: `v4/architecture-simplification`
- reviewed PR head: `d6444e6`
- frozen production baseline: `59,859` physical Python/GDScript lines
- reviewed production tree: `64,581` physical lines (`44,632` GDScript and
  `19,949` Python across 259 files)
- reviewed production delta from baseline: **+4,722 lines**

The production tree is larger than the baseline. The simplification claim is
about fewer authorities, branches, legal mixed states, and reverse ownership
edges; it is not a claim that v4 reduced physical LOC. Security checks,
transactional update/recovery behavior, and qualification coverage account for
the retained growth.

## Final evidence

| Check | Result |
|---|---|
| Architecture simplification gates | 11/11 passed at `d6444e6`; production tree clean |
| Hosted exact-head matrix | [GitHub Actions run 33515469197](https://github.com/hi-godot/godot-ai/actions/runs/33515469197), 32/32 jobs passed |
| Automated review | CodeRabbit passed; no unresolved review threads |
| Older-PR disposition audit | All six PRs tracked in the architecture plan remain open at their recorded heads |

The hosted matrix and review establish the final PR-head evidence. The
remaining publication blockers are still the ones named by the architecture
and verification plans: complete external failpoint coverage, numeric storm
ceilings, the real-process recovery matrix, and exact-candidate Phase 7
qualification. Passing this checkpoint does not silently close those gates.
The authoritative
[qualification and publication checklist](architecture-simplification-verification-plan.md)
requires complete artifact/dependency inventories, digest-bound A/B approval,
independent verifier/SPKI attestation, and post-publication public-byte hashes;
this checkpoint does not replace any of those requirements.
