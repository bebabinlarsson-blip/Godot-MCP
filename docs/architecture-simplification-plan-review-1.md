# Independent review 1 — architecture-simplification-plan.md, draft 0

Reviewer: Claude (independent session; did not participate in the hardening
implementation or the plan's authorship)
Date: 2026-08-30
Version reviewed: the 781-line post-proofread draft 0 (md5
`2e19e5bb147728be52f0626df37a0237`), i.e. including the 2026-08-30
internal-consistency proofread noted in the decision log.
Method: four parallel read-only area reviews (transport/authority; self-update;
plugin/persistence/clients; tests/measurements) over the worktree at
`audit/architecture-hardening-2026-08-30`, each verifying the plan's factual
claims against code with file:line evidence, plus a direct pass on sequencing,
product decisions, and repository history. No files were modified, no tests
run, no editors launched. This document satisfies the first Phase 0 checkbox
("at least one independent architecture/security review using the reviewer
brief"); it intentionally follows the brief's eight requested outputs.

## Verdict (brief item 8, stated up front)

**Approve for another planning iteration.** All four area reviews reached this
verdict independently. The three most important reasons:

1. **The plan's factual claims are accurate or conservative in every case
   checked, and its measurements reproduce exactly.** The boolean auth state,
   global pending tuples, three dependency-private seams, ~20 legacy branch
   sites, string-named runner steps, two-caller `persist_mutation`, JSONC
   repeated scans, and inert descriptor fields all verified. The LOC table
   recomputed to the line for production and tests. The open questions are the
   right ones — two are answered below in the plan's favor.
2. **Two incident-derived invariants are missing from the ledger and sit
   directly in the refactor's path.** The pin-only client-config rewrite gate
   (`client_configurator.gd:468–515`, incident recorded at `mcp_dock.gd:3611`)
   and the post-update arm/spend stale-recovery chain (`plugin.gd:331–333`,
   `server_lifecycle.gd:96–114`) were each bought with a production incident;
   Phase 4 and Phase 5 as written would refactor all of their implementing
   components blind. Proposed ledger rows C2 and U4 below.
3. **The quantitative expectations and two proposals need re-scoping.** At
   constant product surface the realistic total is ~900–1,500 lines, not
   1,500–2,500 (the stated ranges silently assume OPEN product decisions);
   the McpResourceIO three-way split fails the plan's own rule 8 (the class is
   stateless — there is no owner to separate); and P7's payoff is illusory as
   specified (uvicorn's WS support *is* the `websockets` package, so no
   dependency is removed, and all five HTTP middleware no-op on WS scopes).

Two operational items precede everything else and belong in Phase 0, not
Phase 1:

- **Freeze the reference now.** The "maximal hardening reference" currently
  exists as ~12,200 added / 4,760 deleted lines of *uncommitted* working-tree
  state across 157 files, plus ~3,600 lines in 13 untracked files, on a branch
  with only three commits past `66ef3f5`. One errant git command destroys the
  behavioral oracle the entire plan measures against. Committing the snapshot
  (or an equivalent immutable capture) should happen before any further review
  iteration, not after Phase 0 exits. Phase 1's new manifest requirement is
  right; its timing is not.
- **The compatibility baseline is v3.2.4, not v3.2.2.** Tags v3.2.3 and
  v3.2.4 (2026-08-27) are on `origin/main` and precede the comparison base
  `66ef3f5`. Releases shipped mid-audit; every compatibility matrix and the
  P3 deadline below must be written against v3.2.4.

## 0. Fact corrections and disclosure gaps

- Latest released version: **v3.2.4** (see above).
- The LOC table is honest: production 6,606/2,748 and tests 7,109/1,760
  reproduce **exactly**. Two undisclosed choices should be written down so
  Phase 1's re-measurement reconciles: `pyproject.toml` (+12/−4) was bucketed
  as CI/tooling, and the docs bucket excludes the plan document itself (the
  worktree's actual docs delta today is ~+1,370 net, not +582).
- The plan document and this review are themselves untracked files in the
  worktree — they are part of what an accidental clean would destroy.

## 1. Security regressions the target architecture would introduce

Ordered by severity; each is fixable in draft 1 with a sentence or a ledger
annotation, which is exactly why they matter now.

1. **A3 silently rewrites T5's pending-command bound.** The cap is global
   today: 128 across *all* editors (`websocket.py:807`). Per-peer futures make
   it per-peer (128 × 64 connections = 8,192 potential futures). EditorPeer
   needs either a shared counter (reintroducing one piece of cross-peer state)
   or an explicit, ledger-approved semantic change. The plan must name the
   chosen semantics; a faithful implementer would weaken T5 here without
   noticing.
2. **Final-ACK removal without version gating bricks released plugins.**
   Current plugins hard-require the 5-field proofful ack
   (`connection.gd:797–803`; `parsed.size() != 5` ⇒ close). A server that
   stops sending `server_proof` strands every released plugin immediately
   after self-update — the exact path the v3.2.x fixes hardened. The server
   sees `plugin_version` in the handshake *before* building the ack
   (`websocket.py:516–539`), so gating is cheap. See §Answers for the full
   ACK analysis.
3. **P3 (sign the exact ZIP) degrades a property the threat table must own:
   authenticated version before side effects.** Today the server package
   pre-warm is keyed by the *signed* version before the archive downloads
   (`update_manager.gd:693–694`, locked by
   `tests/unit/test_post_update_stale_server.py:39`). With no manifest there
   is no signed version pre-download: pre-warm either runs on the unsigned
   API tag (a tampered API response can steer a `uvx` install of an
   attacker-chosen *genuine* PyPI version — an integrity non-event but a
   cache/DoS lever) or serializes after a ~60 MB download, re-opening the
   #896 cold-spawn window. Resolve this inside the P3 decision, not during
   Phase 4.
4. **P4's retained-check list is internally inconsistent.** B3 says to retain
   "expanded-write bounds" after removing the central-directory parser — but
   the parser is the *only* pre-allocation bound (`ZIPReader` exposes no
   uncompressed-size API; `read_file()` materializes the whole entry — the
   parser's own header says so, `update_reload_runner.gd:403–405`). Honest
   formulation: remove the parser *and* accept that expansion bounds become
   producer-side + signature-inherited, with consumer checks reduced to path
   confinement, required files, entry count via `reader.get_files().size()`,
   and post-write read-back. Two corollaries: the case-fold-collision and
   file/ancestor checks (`:486–518`) die with the parser, and the producer
   preflight currently has **no case-collision logic**
   (`release.yml:271–296`) — it must gain those checks, as a tested script,
   *before* the consumer parser is deleted.
5. **B2's outcome refactor can break a cross-release wire contract.** The
   runner's success-marker statuses (`"success"/"failed_clean"/"failed_mixed"`,
   `update_reload_runner.gd:973–977`) are read by the **next** plugin
   version's `_pending_self_update_succeeded` (`plugin.gd:564`) and by
   telemetry. They are not internal strings; renaming them is a
   compatibility change.
6. **Section C's event-emitting ServerSupervisor contradicts two recorded
   hot-reload policies.** `plugin.gd:1146–1152` documents *rejecting* a signal
   in favor of polling because "a signal added in the same release as a new
   consumer would be another shape-coupled update," and the `_host` reference
   is deliberately untyped for self-update shape tolerance
   (`server_lifecycle.gd:17–18`, same convention `update_manager.gd:23–27`).
   The supervisor design must either honor these (events only across
   release-stable shapes, introduced one release before their consumers) or
   explicitly retire the policy with a P-row decision. P9 applies here and
   the plan doesn't connect them.
7. **Inlining `persist_mutation` multiplies D1/D2 honesty semantics.** The
   codebase already demonstrates the failure mode: `set_resource_property`
   (`resource_handler.gd:455–607`) implements its own explicit
   snapshot/apply/restore flow that — unlike `persist_mutation` — performs
   **no uncached disk read-back**. After inlining, "partial commits are
   reported honestly" would have three or four subtly different
   implementations instead of one. Prefer the inverse: keep one shared
   persistence transaction and migrate `set_resource_property` *onto* it.
8. **One retained seam fails open.** A renamed/moved FastMCP
   `session_manager` attribute silently returns the app to unbounded sessions
   (`security.py:282–285` — `_find_session_manager` → None → pass-through),
   while the analogous websockets registry seam fails closed with
   `transport.abort()` (`websocket.py:78–83`). Whatever P8 decides about
   retention, the A4 admission decision should require converting this seam
   to fail-closed (or a startup assertion).
9. **P7's spike, if run naively, weakens two invariants at once.** All five
   HTTP middleware no-op on `websocket` ASGI scopes
   (`origin_guard.py:343–345`, `security.py:81, :135, :231, :277`), so a
   consolidated editor route arrives with no guards from either plane; and
   the per-phase frame budget (16 KiB pre-auth → 4 MiB post-auth,
   `websocket.py:469–471`) has no supported uvicorn equivalent — the spike's
   likely endpoint is a weakened pre-auth bound or a *new* private seam,
   contradicting P8. Under `--allow-host` it also converts T2's bind-level
   loopback guarantee into a route-level policy check. Keep the spike (the
   "failed spike is a valid outcome" framing is right) but run it expecting
   failure, after P2 and a plugin-floor decision — and note the motivating
   payoff is smaller than stated: **no dependency is removed either way**,
   because uvicorn's WS support is the `websockets` package
   (`asgi.py:387`, `ws="websockets-sansio"`).

## 2. False simplifications

1. **A1's Python half is largely already true.** `TransportCapabilities` is a
   frozen dataclass, the record write is atomic, validation is centralized.
   The substance is the *deletions* A1 implies but doesn't enumerate: the
   per-field default generation in `create_server` (`server.py:480–483` can
   pair one supplied key with one generated key — a real mixed-identity
   path), the duplicated generation across three launch paths
   (`__init__.py:324–336`, `attach/ensure.py:541–545`, `:635–639`), and the
   import-time identity (`protocol/attach.py:24`,
   `SERVER_INSTANCE_ID = … or uuid.uuid4().hex`). Name these as the
   acceptance criteria; the wrapper object alone is packaging.
2. **A2's enum is client-side only.** The Python server has no auth-state
   booleans to delete — `_serve_connection` (`websocket.py:396–539`) is
   already structurally sequential, i.e. the plan's ideal. The real client
   gains are the single failure event (collapsing ~10 `close()` sites) and
   the already-true property that the socket never reads capability files.
   Keep the two rotation-diagnostic booleans out of the phase enum — they are
   diagnostics, not phases.
3. **The McpResourceIO three-way split fails the plan's own rule 8.**
   `resource_io.gd` (525 lines) is 100% `static` with zero mutable state —
   there is no state owner to separate; state lives in callers (undo manager,
   connection pause target, disk). The split is file-boundary bucketing of a
   stateless namespace, which the executive section (lines 40–44) explicitly
   disqualifies. The defensible kernel inside D: extract response-shaping
   (`label`/`extra_fields`/`path_field`/`cleanup_hint` parameters) out of
   `save_to_disk`, and fix the validation asymmetry where
   `read_text_from_disk` validates paths but `write_text_to_disk` relies on
   callers (a latent D1 hole with or without any split). Also note churn: the
   class is +258/−10 in this branch's own uncommitted work (the #934 rework);
   reorganizing it again before that contract ships maximizes Phase 6 restack
   noise.
4. **B1 is predominantly a move, not a delete.** Download and *all*
   cryptographic verification already happen pre-disable
   (`update_manager.gd:159–781`); what relocates is staging-dir prep, ZIP
   structural validation, extraction, and read-back (~450 lines of
   `update_reload_runner.gd:283–305` and callees). Genuine deletions are the
   duplicated re-validation rounds (`:289`/`:297`) and post-handoff identity
   re-derivation, ~100–150 lines. B1's real (and understated) benefit is that
   post-disable *validation* failures stop invoking the full
   rollback/rescan/re-enable machinery and become plain aborts — whole
   failure classes leave the dangerous window.
5. **B2's terminal outcomes already exist.** `InstallStatus { OK,
   FAILED_CLEAN, FAILED_MIXED }` (`update_reload_runner.gd:54`) is the
   enumerated outcome model B2 proposes, almost verbatim. What is stringly is
   the *transition sequencing* (`_next_step` strings dispatched via
   `call(step)`, `:238–248`, plus `_waiting_for_scan`/`_scan_timed_out`/
   `_frames_remaining`). Scope B2 to sequencing, and add one implementation
   rule: **enum dispatched by value, never stored `Callable`s** — a Callable
   captured pre-swap pins the old script version, recreating the #245/#247
   crash class the string dispatch exists to avoid. (The frame-driven
   machine itself is required mechanism, not style debt; the plan's framing
   is correct and consistent with this repo's prior rejections of
   frame-yielding elsewhere.)
6. **The 144-command explicit catalog is +50–150 LOC.** Three registration
   conventions (17 same-name groups → 76 commands, 12 prefix groups → 42,
   26 aliases; `plugin.gd:232–248`) cost 17 lines. A one-mental-rule table
   pays rent **only if** it simultaneously becomes the machine-readable
   namespace source that kills `test_command_name_parity.py`'s six
   convention-specific regexes and feeds docs. State that as the payoff or
   drop the item.
7. **Half of Section E's diagram already exists.** `_atomic_write.gd:17–170`
   already does permissions preservation, 0600 floor, backup,
   symlink-preserving replace, and size read-back; descriptors are already
   data-only (enforced by test). The genuine extractions are TargetResolver —
   merge-tier logic today split-brained between `_base.gd:266+` and
   `_json_strategy.gd:633–726` — and EntryPolicy — build/verify/launch-error
   logic triplicated across the four strategies (~100–150 line dedup).
8. **B4's "move out of YAML" slightly misstates the debt.**
   `test_release_signing_contract.py` already *executes* the literal `run:`
   bodies under bash (`:68–82`) — the plan-endorsed direction. The actual
   debt is the ~90 lines of pinned YAML text and `.index()` step-ordering in
   the same file, plus a preflight "contract" test (`:199–214`) that asserts
   the preflight's *source text* names the four limits instead of executing
   it — while the very next test does execute it, making the pin redundant.

## 3. Missing ownership

State with multiple writers or no terminal owner that the plan does not
currently address:

1. **The capability record has two in-process publishers with two nonce
   derivations**: the lifespan publish (`server.py:558–563`) and the H11
   `connection_made` republish (`asgi.py:55–91`, called at `:129`;
   module-global `_PUBLISHED_BOUND_HTTP_PORTS` at `:52`) — consistent only
   when the env triplet is present. A1's "one capability store publishes"
   must consolidate both under one owner or delete the republish and
   re-solve the stale-record race it heals. Sequencing: consolidate the
   store *before* removing the seam, or the race reopens.
2. **Stale capability records are healed, never reaped** — nothing unlinks
   `http-<port>.json` on shutdown; staleness is absorbed by the GDScript
   401-retry (`plugin.gd:1056–1076`). Fine as a policy, but the store should
   own the statement.
3. **`ws_port` is outside the identity entirely** — seeded and republished
   independently of any capability triplet
   (`plugin.gd:347, :1273–1277`; `server_lifecycle.gd:870, :974`), with
   ws↔http pairing only advisory via the status probe. A1 should add it to
   the snapshot or state why pairing stays advisory.
4. **Where does the reload-surviving identity live?** Today the four
   credential fields survive plugin hot-reload by being `static`
   (`plugin.gd:189–204`). A per-instance ServerSupervisor that owns the
   snapshot loses authority on every reload and enters the 4003 loop. The
   plan must name the reload-surviving home. (Related: A1's new "McpConnection
   receives one snapshot for an attempt and never refreshes it" is a
   *behavior change* — today `_refresh_rejected_capability`
   (`connection.gd:505–512`) swaps credentials on a live connection. The
   target is cleaner, but the rotation retry loop and its bound must be
   re-expressed as close-and-reconnect, and the plan should say so.)
5. **`Session` objects have two writers** — WS event handlers
   (`websocket.py:724–790`) and per-response envelope healing (`:611–621`,
   `:875–953`) — while `SessionRegistry` owns lifecycle, promotion, and
   waiters. A3 should name the Session's single writer; the registry must
   stay authoritative for active-session policy, and the coalesced
   custom-tool broadcast (`:327–332, :694–722`) is server-global by design
   and stays outside any peer.
6. **The post-update arm/spend chain has no owner and no ledger row** — see
   proposed row U4 below. The plan's only mention is a manual smoke item
   (line 697); that is a test, not an owner. A P1 restart-to-apply variant
   must still deliver an equivalent one-shot arming signal across the
   restart, or post-update updates dead-end at INCOMPATIBLE against
   attach-bridge-respawned old servers — the exact bug the invariant fixed.
7. **Legacy release-asset retirement has no owner or evidence bar.** Every
   release must keep emitting the dir-entry-free zip (v2.2.x rescue
   contract), `.sha256`, and `.sha256.sig` (v2.9.3–v3.2.4 updaters) —
   "temporarily" (`docs/releasing.md:35`) has no criterion. The natural bar
   exists in this project: telemetry's active-install version distribution.
   Assign it.
8. **Orphaned-backup crash recovery is manual and undiscovered.** Crash
   between the two renames (`update_reload_runner.gd:854/:865`) or
   mid-rollback leaves the canonical path empty with both trees as hidden
   siblings; nothing outside the runner references the backup dir, there is
   no startup orphan detection, and the next update fails closed with only a
   log line (`:687–689`). U3's letter holds; its spirit doesn't. A startup
   orphan check is cheap and the plan should claim it. Two ledger
   annotations for U3: the disable proof is taken **once** (`:271`) and
   nothing re-checks before the swap at `:846` (a user re-enabling mid-
   extract defeats it); and "proved enabled" (`:1019`) is Godot's flag, not
   functional liveness — an enabled-but-broken plugin still gets its backup
   deleted.
9. **`mcp_dock.gd` — 3,774 lines, 137 functions — appears zero times in the
   plan**, and `client_configurator.gd` (1,879 lines) is never named. The
   dock owns client-status refresh worker threads with generation counters,
   per-client Configure/Remove workers, the post-update repin arming and
   sweep, banners, the crash panel, and the port picker. Section C's
   `ClientConfigService` overlaps the dock's threading and repin sweep
   without saying which side owns workflow state — recreating the
   multi-writer defect the plan exists to fix. Needed: an ownership row —
   "dock = rendering + click forwarding; workflow state owner =
   ClientConfigService" — and an explicit owner for the repin gate.
10. **The `_host` surface, quantified** (supporting Section C, which is
    directionally right): `server_lifecycle.gd` calls **42 distinct members**
    on `_host` across ~180 sites, and `plugin.gd` calls 30 members back on
    `_lifecycle`, including private-field reach-ins. ServerSupervisor is a
    real reduction **only if** it absorbs the record I/O, pid/port probes,
    and capability apply (~25–30 of the 42) rather than wrapping them; an
    irreducible residue of ~8–10 host-side members remains structural (the
    watch `Timer` and `McpConnection` node must live on the plugin — the
    manager is RefCounted and cannot host children; dock refresh and
    `set_process` arming are main-thread UI). Two more constraints the
    supervisor design must state: **thread affinity** (the startup walk runs
    host callbacks on worker threads per #678, `server_lifecycle.gd:147–222`,
    and Godot signals emit on the calling thread — a naive events conversion
    moves dock/UI work off-main-thread), and the hot-reload signal policy
    from finding 1.6.

## 4. Product decisions

- **General: use telemetry as the evidence base.** The plan asks "which
  P1–P8 decisions can be made from current product evidence" — this project
  *has* current product evidence: the live telemetry pipeline (ledger row
  D3) with an active-install version distribution. P1 (one-click update
  usage), P2 (does anyone run `--insecure-legacy-transport`?), P5 (which
  client families actually get configured), and the legacy-asset retirement
  bar (finding 3.7) are all measurable queries, not opinions. Draft 1 should
  add "query telemetry" as the first evidence step for each.
- **P1**: the recommendation (preserve one-click, stage completely, spike
  restart-to-apply) is sound. Add the arm/spend constraint (finding 3.6) as
  a design requirement for the restart-to-apply spike, and note the
  updater LOC range depends on this decision (§7).
- **P2**: correct direction; two additions. `--insecure-legacy-transport` is
  a *documented operator contract* (`AGENTS.md:21–24`), so removal needs a
  deprecation window, and the ordering must be strict: legacy removal
  **before** any origin-policy narrowing — several Host/Origin/Sec-Fetch
  checks are the only control in legacy mode. The residual unique value of
  the origin guard in secure mode is small (401-vs-403 liveness oracle
  shaping, pre-auth WS handshake spam) — that answers the open question at
  line 764 in the plan's favor, but only post-P2.
- **P3**: the recommendation survives, with a **forcing deadline the plan
  must state**: the manifest is unshipped, but the worktree updater
  *hard-requires* the manifest assets (`update_manager.gd:256–260, :398`).
  P3 must be decided **before the first release cut from this branch**, or
  the manifest becomes a consumed contract and the simplification turns into
  a three-generation asset migration. The written threat table (brief form):
  asset substitution, replay-under-newer-tag, and tag/version confusion are
  equivalent under both contracts (the version lives inside the signed bytes
  either way); the manifest is strictly better only in denial-class ways
  (exact-size body cap vs static 64 MB, fail-before-fetch on a ~2 KB
  manifest vs post-download) plus the pre-warm property in finding 1.3,
  which must be resolved inside the decision.
- **P4**: adoptable under rule 7, but rewrite the retained-check list
  (finding 1.4) and fix the sequencing: script-ify and extend the producer
  preflight first, delete the consumer parser second — the plan currently
  lists them as siblings.
- **P5**: correctly gated before the JSONC work. Two conditions: the
  Phase 2 corpus must be input-file → output-**bytes** black-box pairs
  (today's strong fixtures call private strategy methods like
  `_strip_jsonc` directly and die in the rewrite), and the single-index
  admission bar should be explicit — the span index is, functionally, a
  JSONC CST (the warned-against "parser framework" with a different name),
  so it must delete at least the ~750 lines of scanning it replaces.
- **P6**: the consequence text overstates by one leg — a non-undoable
  contract deletes the UndoRedo pipeline-per-history-step callables and the
  `_last_persistence_error` side-channel (~80–120 lines plus a nasty
  silent-redo-failure class), but **not** the save/verify/rollback
  transaction, which D1 requires regardless. The stronger argument the plan
  misses: `set_resource_property` is already non-undoable by design
  (`resource_handler.gd:536`), so P6=non-undoable makes the persistence
  surface *consistent*. Decide P6 before any `persist_mutation` surgery.
- **P7**: see finding 1.9 — keep the spike, expect failure, re-state the
  payoff honestly (no dependency removed), sequence after P2.
- **P8**: the proofread's rewrite (T5 bounds fixed; retain a private adapter
  only when no supported public control proves the same bound) is the right
  frame. Add: any retained seam must fail closed (finding 1.8), and the
  dependency-floor "contracts" need upgrading from string pins to executed
  adapter contracts (§6.6).
- **Proposed P10 — implementation substrate.** The plan is ambiguous about
  whether implementation *edits the maximal branch down* or *rebuilds up
  from main using the branch as an oracle* ("reference, not an
  implementation that must be preserved line for line" vs Phase 6
  "restack the work"). These have very different risk profiles against a
  main that ships weekly (v3.2.3/v3.2.4 landed mid-audit; #922–#936 merged
  in the same window). The proofread's new Phase 0 items (diff inventory by
  destination, early patch boundaries) help either way, but the choice
  itself is a decision, not an emergent property — make it a P-row and
  resolve it in Phase 0. Related: consider landing the separable
  correctness/pure-simplification tranches on main *early* rather than
  holding everything for one big-bang Phase 6 integration; long-lived
  divergence is the historically observed killer of maximal branches.

## 5. Sequencing hazards

1. **Freeze before review, not after** (see Verdict). Move Phase 1's
   checkpoint+manifest items to the front of Phase 0.
2. **The P3 clock**: decide before any release from this branch
   (finding 4.P3). The plan orders the checkbox correctly (line 604) but
   never states the deadline or that releases already shipped mid-audit.
3. **Phase 2 must convert the arm/spend and U3-ordering pins before Phase 4
   touches the runner.** `test_post_update_stale_server.py:138–200, :248–277`
   (arm/spend) and `test_editor_focus_refocus.py:359` (disable-before-mutate)
   are literal source pins; Phase 4's refactor deletes their anchors and the
   invariants' only proof in the same motion.
4. **Store consolidation before H11-republish removal** (finding 3.1), else
   the stale-record race reopens mid-refactor.
5. **ACK removal last and version-gated** (finding 1.2); legacy removal
   strictly before origin narrowing (finding 4.P2); the client enum rewrite
   and server peer rewrite must not share commits with any wire-visible
   change — the cross-language proof vectors are the contract that keeps
   them honest, and they must be unified first (§6.1).
6. **P4 after B4's producer script, not alongside it** (finding 4.P4).
7. **The supervisor spans Phases 3 and 5** — both reshape `plugin.gd` and
   `server_lifecycle.gd`, which will defeat Phase 6's attribution goal.
   Either do the supervisor once in Phase 5 with a narrowly-scoped Phase 3
   transport-identity carve-out, or accept the attribution loss explicitly.
8. **P6 before `persist_mutation` surgery** — otherwise Phase 5 hand-writes
   undo flows that P6 then deletes.
9. **Phase 5 bundles ~8 workstreams** against the plan's own
   one-active-workstream risk control (line 718). Split it or stage it.
10. **Phase 2 needs an explicit scope cut to avoid being open-ended.**
    8 of 13 ledger rows already have solid behavioral proof (§6). Of the
    ~3,800 LOC of source-text-coupled tests, the largest family
    (~2,000 LOC: `test_editor_focus_refocus.py`, the timeout/race/reload
    contracts) pins behavior whose *triggers* — hung CLI, frozen game
    subprocess, reload-mid-await, editor scan races — the harness cannot
    produce; their own docstrings say so. They convert only after
    Phases 3/5 extract pure seams. Realistic Phase 2 exit criterion:
    "every ledger row has implementation-independent proof; trigger-
    unreachable regression pins are inventoried and convert during
    Phases 3–5." The convertible-now set (~800 LOC with declared behavioral
    twins: `test_audit_data_loss_safeguards.py`,
    `test_persistent_resource_save_contract.py`, parts of the updater pins)
    is a bounded work item. Also schedule the **re-seaming of the ~186
    host-stub lifecycle tests** (`_ManagerHostStub`/`_ProofPlugin`, two
    near-identical ~90-line stub hierarchies) — they are behavior tests, but
    their seam is the `_host` surface Phase 5 deletes, and Phase 2 currently
    has no line item for them.
11. **One consistency note**: the branch is *adding* new source-pin tests
    (`test_persistent_resource_save_contract.py`,
    `test_release_signing_contract.py`'s text half,
    `test_audit_data_loss_safeguards.py`) in the same change-set whose plan
    deprecates the pattern. Fine as scaffolding, but Phase 2 should
    enumerate these files by name so they are converted, not grandfathered.

## 6. Test gaps (proof cannot distinguish secure from broken)

1. **Cross-language protocol drift (T3).** Python pins the transcript
   encoding against the test's own reimplementation
   (`test_transport_security.py:95–103, :721`); GDScript pins
   once-generated hex digests (`test_connection.gd:178–214`) that appear
   nowhere in Python or src. Both suites stay green if the two sides are
   changed "consistently" but incompatibly — or if a weakened GD encoding
   regenerates its digests. Only a single literal-vector corpus consumed by
   both suites closes this; it is roughly a day of work and ~70% of the
   Phase 2 item is already in place.
2. **T2 cross-credential acceptance is untested.** The ledger's own proof
   sentence — "An HTTP credential cannot register an editor; a WS credential
   cannot invoke HTTP" — has no direct test: independence is only checked at
   construction, and WS rejection tests use arbitrary wrong keys, never the
   other plane's real credential.
3. **T4 constructor mixing needs a characterization test before A1 deletes
   it**: `create_server(transport_capability=X, ws_capability=None)`
   silently generates the other half (`server.py:481–483`); no test pins
   what happens to that pair.
4. **U3's central sequencing claim has only a source pin.** Behavioral
   suites prove stage/swap/rollback mechanics, but disable-before-mutate
   ordering lives in `test_editor_focus_refocus.py:359` alone. Phase 4 needs
   an observable ordering proof — e.g., an injected disable-refusal must
   leave the live tree byte-identical (extending
   `test_update_manager.gd:836`, which today checks worker-gate release,
   not tree integrity). Also missing: a runner-level refused-disable test,
   an end-to-end enable-failure → rollback → re-enable test, any
   crash/orphan-restart test (no production code exists to test —
   finding 3.8), and a test driving a *released* updater (v3.2.4's) against
   the next release's asset set (the rescue-contract test does exactly this
   for v2.2.x via a Python re-implementation; the same pattern is needed for
   the v3.x sidecar consumers before P3 changes anything).
5. **C1 credential-absence is unasserted.** No test greps produced client
   configs for bearer/capability material; a regression embedding the HTTP
   capability in a generated entry passes the entire 250-test suite. One
   differential assertion over every strategy's output closes it cheaply.
6. **Dependency-floor "contracts" are string pins** on `pyproject.toml`;
   executed adapter contracts exist for the H11 seam only
   (`test_transport_security.py:386–437`), not for the FastMCP traversal or
   the websockets registry inspection. A4's "one contract test per retained
   adapter" should mean executed contracts.
7. **GDScript sync-rule fragility.** The runner never awaits tests and the
   zero-assertion detector only catches the all-assertions-detached case; a
   test that asserts once before suspending passes with silently amputated
   coverage. Existing top-level `await`s are safe only because
   `_run_blocking` inline mode never suspends. Phase 2's transition tests
   are safe if written frame-free (drive `_handle_message` /
   `_handle_handshake_ack` with crafted frames, as `test_connection.gd`
   does); the plan should state the sync constraint in Section F and add the
   cheap guard — a meta-lint flagging top-level `await` in GD test functions
   (the pattern already exists in
   `test_no_direct_undo_redo_in_gdscript_tests.py`).
8. **Loopback WS bind is unpinned** — no test asserts the `"127.0.0.1"`
   bind argument or rejects a non-loopback WS peer at the socket. If P7 ever
   runs, this is the invariant most at risk with the least proof.
9. **Post-B4, semantic workflow parsing does not exist yet even in embryo**
   — nothing parses the workflows as YAML; permissions/ordering are
   substring pins that die when the YAML moves. The proofread's rule-10
   carve-out ("semantic workflow parsing remains appropriate") names the
   right destination; the migration itself belongs in Phase 2's enumeration.

## 7. Complexity estimate

The plan's own framing — LOC secondary to owners/states/edges — is right,
and the honest tone ("plausible, not the definition of success") is
appreciated. The ranges still need conditioning, because as stated they
silently assume OPEN product decisions:

| Area | Plan | Review estimate at constant product surface | To reach the plan's upper range requires |
|---|---|---|---|
| Transport | 350–650 / 700–1,200 | ~250–450 | P2 landed *and* origin narrowing; 1,200 additionally needs P7 to succeed (unlikely per finding 1.9) |
| Updater | 700–1,000 | ~350–450 (P3 ≈ −180, P4 ≈ −150, B1 dedup ≈ −80, B2 ≈ neutral) | P1 = restart-to-apply (deletes ~300–400 of scan/enable/verify/rollback machinery) |
| Domains | 500–900 | ~300–600 (descriptors −40, EntryPolicy −100…−150, JSONC −150…−250, supervisor absorption −150…−350, catalog **+50…+150**, ResourceIO split ≈ 0) | P5 = manual (−~500 more) or P6 = non-undoable (−~100–150) |
| **Total** | **1,500–2,500** | **~900–1,500** | explicit product narrowing, as the plan itself warns |

Recommendation: restate each range as *conditional* ("X at constant surface;
+Y under decision Pn"), which also makes the Change Admission Checklist's
question 4 self-enforcing.

## Proposed amendments for draft 1

**New invariant-ledger rows:**

- **C2 (pin-only auto-rewrite):** "Automatic client-config rewrites occur
  only for entries proven to differ solely by version pin; all other drift —
  including entries pointing at another editor's ports, hand-edits, and
  changed settings — requires an explicit human action." Owner: client-config
  service (gate predicate currently `client_configurator.gd:468–515`,
  consumed by the dock's one-shot sweep `mcp_dock.gd:3600–3655`). Proof:
  existing dock/post-update tests, mapped in Phase 2. Rationale: incident
  recorded in-source ("18000 repinned 21 real client configs",
  `mcp_dock.gd:3611`).
- **U4 (post-update recovery arming):** "A completed self-update arms
  bounded stale-server recovery exactly once, from user consent; automatic
  triggers spend the budget and never arm it; the success marker that
  conveys arming is a cross-release wire contract." Owner: activation
  transaction + lifecycle manager jointly. Proof: the
  `test_post_update_stale_server.py` suite, converted to behavioral form in
  Phase 2 before Phase 4 runs.

**Ledger annotations:** T5 — name the pending-command bound's global
semantics as part of A3; T2 — note bind-level vs route-level loopback as a
P7 admission criterion; U3 — record the one-shot disable proof and
flag-not-liveness "proved enabled" caveats (finding 3.8).

**Phase edits:** move freeze/manifest to the top of Phase 0; add the P3
deadline sentence to Phase 4; add the Phase 2 scope cut, the named pin-file
enumeration, the shared-vector corpus, the GD top-level-await lint, and the
host-stub re-seaming item; split or stage Phase 5; add P10
(edit-down vs rebuild-up) to the decision table; add "query telemetry" as
the first evidence step for P1/P2/P5 and the legacy-asset retirement bar.

**Answers to the plan's open questions, where the evidence permits:**

- *Final ACK*: denial-only; within the stated threat model (port-race
  impostor, same-user out of scope) it binds nothing the hello proof and
  client proof don't already bind — no downgrade resistance is added
  (downgrade is prevented by client policy, `connection.gd:482–502,
  :793–794`). Removable, **only** behind plugin-version gating; LOC payoff
  ~60–90 lines.
- *One-listener*: technically plausible (uvicorn already runs
  `ws="websockets-sansio"`), but it removes no dependency, strips every
  existing guard from the consolidated route by default, and loses the
  supported per-phase frame budget — expect the spike to fail its own
  admission criteria (finding 1.9).
- *Smallest consumer ZIP validation set*: path confinement, required files,
  entry count via `reader.get_files().size()`, post-write read-back —
  valid only after the producer preflight is a tested script extended with
  case-collision and ancestor checks; expansion bounds necessarily migrate
  producer-side (finding 1.4).
- *Which resource edits need UndoRedo*: the shipped precedent
  (`set_resource_property`, non-undoable by design) argues for consistency
  via P6 = non-undoable; the deletion is legs 2–3 only (finding 4.P6).
- *JSONC index without a parser framework*: feasible, but be honest that
  the index is a CST; admission = it deletes at least the ~750 lines of
  scanning it replaces, and the byte-level black-box corpus exists first.
- *Origin checks post-P2*: residual unique value in secure mode is small —
  liveness-oracle shaping on `/godot-ai/status` and pre-auth WS handshake
  spam; evaluate for removal only strictly after P2.
- *Released updater/plugin compatibility*: v2.2.x–v2.3.0 require the
  dir-entry-free zip (`zip -D`, rescue-contract test); v2.9.3–v3.2.4 require
  zip + `.sha256` + `.sha256.sig` with the exact `sha256sum` sidecar format;
  all shipped runners reserve `.godot_ai_update_tmp` / `.update_backup` /
  `.gdignore` entry names. The manifest is consumed by no released version
  — see the P3 deadline.

**What the plan gets right (kept short, but it matters):** the invariant
ledger as the review currency; the complexity taxonomy; rule 8 and the
admission checklist (this review used them against the plan's own proposals,
and they held up); honest LOC accounting that reproduces exactly; gating P5
before the JSONC work; the B4 trust-boundary preservation; the frame-driven
activation stance, which matches this repo's hard-won hot-reload history;
and the proofread's A1/P8 tightenings, which resolved two findings before
this review landed. Draft 0 is an unusually reviewable plan — these findings
are refinements to a sound direction, which is what "approve for another
planning iteration" means.
