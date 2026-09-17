# Architecture Simplification Plan — Independent Review 3

- Date: 2026-08-30
- Reviewed plan: `docs/architecture-simplification-plan.md`, draft 2
- Frozen draft-2 commit: `ba31206`
- Implementation oracle: `957add991347e94443014cf97079d72713fb05c2`
- Method: three independent read-only reviews covering security, cognitive
  architecture, and execution/release proof
- Combined verdict: **needs major revision before implementation**

This file preserves review 3 as historical evidence. It should not be edited
to agree with later plan revisions. Draft 3 reconciles the accepted findings.

## Executive assessment

Draft 2 corrected the two most serious factual errors in draft 1: v3.2.4 does
not implement the checkpoint's secure protocol, and historical runners cannot
retroactively supply transactional update guarantees. Its v4 clean boundary is
sound.

It is still not implementation-ready. The proposed owner tree contains too
many new role names, the update proof is circular, normal startup is not
actually barred during activation, and a second editor can execute the shared
add-on tree while the first editor swaps it. The release gate cannot resolve an
unpublished matching Python server through the normal user path. The manual
v4 bootstrap also lacks a separately trusted verifier.

The right response is not more services. Reuse the existing published owners,
collapse duplicate maps, make one tagged episode replace flag combinations,
separate architecture from the exhaustive verification matrix, and defer
unrelated persistence/client feature restructuring.

## P0 findings

### R3-1. Replace the ownership tree with a collaboration/lifetime graph

Draft 2 showed parentage but not permitted dependency directions, startup
barriers, disposal order, or values crossing each edge. It also placed
`ClientWorkQuiescence` beneath the update owner, even though the client-work
domain owns those jobs.

The minimal target is:

- `plugin.gd` root-owns the existing update manager, lifecycle manager,
  client-work owner, and Dock;
- Dock emits user intents and renders immutable snapshots;
- the update manager depends on a narrow `quiesce()` port owned by client work
  and on an activation-runner factory;
- the update manager does not retain Dock or the plugin as a generic host;
- disposal reverses construction and never depends on Dock survival.

Do not add an `UpdateCoordinator` wrapper around `McpUpdateManager` merely to
give the existing owner a new name.

### R3-2. The phase and exact-candidate DAG is circular

Draft 2 qualified an exact v4.0 candidate before implementing its updater, then
changed client and persistence code afterward. A real self-update proof needs
two frozen sources, two plugin bundles, and two matching Python distributions.

The corrected order is:

1. characterize;
2. establish the minimal client-work/lifecycle ownership seams;
3. prototype the v4 migration asset contract;
4. implement transport and updater;
5. finish only required product/PR work;
6. freeze candidates;
7. build, sign, and qualify exact bytes.

Provisional fixtures are never called promotable candidates. Disposable and
eventual artifacts must not share one final version/tag identity.

### R3-3. Activation needs a startup barrier, not a watcher

New code currently could start lifecycle/server work before the old runner
writes and new code claims the terminal result. Activation mode must be
detected before normal startup. Only the minimum root/update UI initializes,
then new code writes readiness, awaits and atomically claims the terminal
result, and only then releases server, client, telemetry, repin, discovery, and
replacement side effects.

A timeout remains recovery mode. It cannot silently fall through into normal
startup or mint replacement authority.

### R3-4. Concurrent editors can execute the tree during replacement

Quiescing one Dock/plugin instance does not stop a second Godot process using
the same project. v4 needs a project/install-root interprocess activation lock
and live editor-instance leases. The simple policy is refusal: hot apply does
not begin while another live editor owns the install root. Startup observes an
activation lock and enters the barrier instead of loading normal services.

The proof must run two real editor processes through activation, not merely
race two consumers for one result file.

### R3-5. The manual v4 bootstrap lacks an authenticity root

Old runners select only the legacy asset name. They cannot authenticate a
renamed v4 asset, and pre-v3 runners do not contain the release public key.

The v4 archive must use the existing release key and ship a manifest/signature,
but that is not sufficient by itself. Migration documentation needs one exact
standalone verification procedure whose key or fingerprint is obtained from a
source independent of mutable release assets. The gate must replace archive,
manifest, signature, and release notes together and still observe failure.

A new release key would require an old-key-signed transition. Avoid that
unless rotation is independently necessary.

### R3-6. The update record protocol lacks editor identity and writer takeover

Project/root/transaction/version binding does not distinguish two editor
processes in the same project. Intent, readiness, result, and claim must bind
the initiating editor process instance and runner nonce. A non-initiating
editor may observe activation but cannot write readiness or claim success.

The plan also killed the old runner at every boundary while declaring it the
only result writer. Define one writer lease and an explicit user-invoked repair
takeover. Automatic startup may classify and wait; it may not seize authority
or write a recovered success without the takeover rule.

### R3-7. Session publication must occur after ACK is queued

Draft 2 registered a session before sending the terminal ACK. An authenticated
HTTP caller could find that session and race a command to a client that still
considers the server unauthenticated.

Reserve the session ID as pending, send/queue the simple ACK, then publish the
session and peer atomically. Ordered delivery after an authenticated challenge
is the property; plaintext `ws://` should not be described as providing
transport integrity.

## P1 architecture findings

### R3-8. Collapse session and peer state into one aggregate

`SessionRegistry` plus `ConnectionHub` retains two membership maps. Use one
aggregate map containing private session state, peer, and per-peer pending
futures, with one global pending counter. The existing asyncio loop serializes
mutations; do not add a lock/service layer. Readers get immutable snapshots and
all updates/routing go through the aggregate.

### R3-9. Reuse the lifecycle manager and define one tagged episode

The current lifecycle owner has 28 fields, 69 functions, and many generic host
dependencies. Renaming it `ServerSupervisor` and adding reducer/effects objects
would not simplify it.

Keep `McpServerLifecycleManager` as the serialized dispatcher. Replace
independent phase/retry/recovery flags with one tagged active episode:

```text
idle | starting | recovering | stopping
```

Each non-idle variant owns its generation, deadline, attempt, authority, and
expected effect. Startup and recovery cannot coexist. One narrow effect adapter
returns values; the generic `_host` reference and obsolete flag paths disappear
in the same tranche.

The acceptance metric is that invalid or ambiguous combinations become
unrepresentable, not that the raw number of declared variants must always
decline.

### R3-10. One LaunchPlan conflates managed and attach launches

Managed-server launch and client attach launch are different effects, including
client-specific Windows wrapping. Share a canonical endpoint/policy input, then
derive separate managed-server and attach plans. Runtime `TransportIdentity`
must not duplicate desired launch settings.

GDScript immutability needs a concrete rule: no retained mutable Dictionary
reference, deep-copy at boundaries, or a read-only value object with tests.

### R3-11. Remove ResourceIO and speculative services from the root graph

`McpResourceIO` has no mutable fields and is already a cohesive static helper.
Root ownership would add startup/lifetime coupling. Keep its centralized
response contract and do not restructure it unless #934/P6 establishes a
specific correctness need.

Every proposed role must identify the existing class it replaces and the old
owner/API deleted. Published `class_name` compatibility cannot become a second
permanent façade by default.

### R3-12. Narrow the measurement infrastructure

A general analyzer for dynamic GDScript dependencies, callbacks, mutable
facts, and state reachability would become its own tool project. Use small,
changed-owner checks:

- one backing store per changed fact;
- zero generic root/host access in a completed owner;
- zero owner cycles;
- zero public mutable session records;
- session/peer maps fall from two to one;
- one tagged lifecycle episode;
- update manager retains neither Dock nor plugin.

LOC and dependency/SCC reports remain informational.

## P1 security and migration findings

### R3-13. Manual backup must be outside the whole project

An old add-on backup elsewhere inside the project remains scan-visible and can
trigger duplicate/stale `class_name` cascades. Canonicalize a backup destination
outside the entire project root, reject symlink/junction/reparse traversal and
collisions, and test the exact documented path. Stage and authenticate v4
before moving the old tree.

Stop old clients/backend processes before replacement. After install,
repin/restart matching clients before declaring server-health success.

### R3-14. Every public installation surface must honor the clean boundary

Inspection of all 104 local `v*` tags found no updater in v0.2.0/v0.3.0 and an
exact `godot-ai-plugin.zip` equality match in all other 102 tags. A distinct v4
asset name therefore blocks those Dock updaters.

The classic Asset Library and Store/manual import are separate overlay paths.
Freeze/deprecate old listings or withhold an in-editor v4 overlay surface until
it can enforce clean replacement. The gate covers every published installation
surface, not only Dock release discovery.

### R3-15. Replacement authorization comes only from user intent

An update journal/result can gate an already-created replacement grant but can
never mint one. The grant originates from the initiating explicit user action,
is bound before activation to project/transaction/stale process identity, and
becomes spendable only in its named phase. Authority-bearing state is private
or authenticated; project/root binding alone is not trust.

### R3-16. Resolve Windows scope honestly

Current GDScript and Python do not verify Windows DACL ownership and skip some
reparse checks. If DACL enforcement is not implemented in both runtimes for
every path component and final handle, the documented guarantee must exclude
hostile other-local-account and same-account processes. It may claim only
remote-peer exclusion and accidental mixed-launch protection on Windows.

Windows represents most active installs, so the chosen claim and real Windows
tests are mandatory rather than an optional platform caveat.

### R3-17. Retaining the last backup simplifies terminal outcomes

Deleting the backup after readiness creates another cross-process effect and a
cleanup-failed terminal state. Prefer retaining exactly one quarantined backup
until an explicit later cleanup or the next update preflight. Cleanup then
occurs before a new mutation; failure aborts safely. This removes post-claim
cleanup ownership and preserves a human recovery artifact.

## P1 execution findings

### R3-18. Private self-update needs private release discovery and Python index

Plugin launch pins `godot-ai==<plugin version>`. An unpublished target cannot
exercise the real server/client path through public PyPI. Qualification needs:

- private GitHub-like release metadata/assets;
- a private PEP 503 index containing exact candidate wheel/sdist;
- production-safe, explicit test-channel overrides;
- immutable source/artifact/package digests;
- normal discovery, prewarm, launch, repin, and restart against those bytes.

PyPI remains first in final publication ordering. If a version already exists,
publication must compare expected digests and fail on mismatch; `skip-existing`
alone can hide different bytes.

### R3-19. Use unique candidate identities

A private smoke successor is either frozen for later byte-identical publication
or uses a unique signed test-channel/prerelease identity. Never sign two
different artifacts under one stable version/tag. Record source SHA, parent,
channel, plugin/Python digests, signer, evidence, and promotion policy for both
nodes.

### R3-20. Historical proof classifies every updater implementation

Group all released tags by updater patch/behavior, choose one exact tag per
class, and run the actual Update-button path through absent-legacy-asset
fallback. Source inspection alone supports classification; runtime rows prove
representatives. Missing assets are release-gate failures, not skips.

### R3-21. Fix mandatory matrices before harness work

Draft 2 left supported Godot versions and operating systems open while calling
their absence a gate failure. Resolve the v4 engine floor and require Windows,
macOS, and Linux before building the harness. Exact architecture and patch rows
are pinned in the verification plan at implementation start.

### R3-22. Failpoints require external barriers and unmodified bytes

Add externally observable before/after barriers for every reducer effect and
durable record operation, including readiness write/replace, result claim,
claim-before-fanout, client quiescence, and repair takeover. Fault controls must
be impossible to arm accidentally in production. The exact candidate bytes are
not patched to bypass discovery, signatures, or downloads.

### R3-23. Lock quantitative stress profiles before architecture changes

Fixed seeds, durations, calls/domain, topologies, allowed errors/windows,
latency/error ceilings, and leak bounds must be derived from Phase-1 baselines
and checked in before Phase 3. An alive editor is not a passing criterion.

### R3-24. Add PR #940 and keep feature work outside architecture tranches

PR #940 opened after review 2 at
`d4f16f538710674e01136b1e0ba88bf458c120f4`. It is clean and adds validated
`project_manage(set_main_scene)`, but overlaps shared registration and tests.
Give it a Phase-0 disposition. If accepted independently, merge it before
pinning the landing base; otherwise defer it. Do not absorb it silently into a
refactor.

## Review-3 conclusion

The v4 clean boundary is worth retaining. The next plan should be shorter and
more concrete:

- reuse existing owners;
- add one client-work owner, not an update wrapper;
- collapse two Python maps into one aggregate;
- use one tagged lifecycle episode;
- enforce a real activation barrier and interprocess lock;
- retain one backup rather than deleting it after success;
- separate the verification plan from architecture;
- move optional persistence, target-resolver, and feature work out of the v4
  architecture critical path.

Those changes make the plan both safer and more genuinely simplifying.
