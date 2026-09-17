# v4 architecture and release checkpoint — 2026-08-31

This checkpoint records the implemented v4 architecture candidate and the
evidence available before publication qualification. It is not authorization
to tag, upload, or publish a release.

## Outcome

The simplifying refactor is implemented. Its meaningful reduction is in the
number of authorities and representable mixed states, not in physical lines:

- one lifecycle episode owns server startup, adoption, conflict, and stop;
- one Python registry owns session/peer membership;
- one authenticated transport contract remains, with no tokenless v3 branch;
- one canonical v4 plugin ZIP shape remains;
- the Dock no longer owns client worker state;
- the update manager retains neither the plugin nor Dock owner;
- the update coordinator retains no detached Node owner; and
- the changed owner graph has no forbidden reverse edge.

All eleven executable architecture gates pass. Production Python and GDScript
total 64,561 physical lines (44,618 GDScript and 19,943 Python across 259
files), versus the frozen 59,859-line baseline: **+4,702 production lines**.
The implementation diff from the baseline is +34,947/-23,128, net +11,819.
Of that net growth, +7,113 is outside the production `plugin/` and `src/`
trees; those two trees account for net +4,706. This is therefore a genuine
authority simplification, but not a LOC reduction. Security, transactional
recovery, and qualification coverage account for the growth and remain
explicitly visible rather than being described as streamlining-by-deletion.

## Evidence identity

- frozen baseline commit: `dc162f16dab5c095a05c283df28dba891b2e47d0`
- implementation commit: `ed69dcd0e28052bec09764e72fe5606893224148`
- implementation tree: `b2fef877fdd1f01458a5ab9b92fa87057e570010`
- branch: `v4/architecture-simplification`
- architecture gate result: 11/11 pass, production tree clean
- exact-head hosted matrix: GitHub Actions run `33479855366`, 32/32 jobs passed

## Local qualification evidence

All local product lanes used isolated ports and capability directories; the
user's live 8000/9500 server was not touched.

| Check | Result |
|---|---|
| Complete locked Python suite | 2,234 passed, 8 skipped, one known Starlette/httpx deprecation warning |
| Focused update/transaction regression | 191 passed, 5 skipped |
| Final update harness subset | 31 passed, 4 skipped |
| Architecture gates | 11/11 pass; production LOC 64,561 |
| Ruff and shell syntax | pass |
| Real Godot 4.7 signed/clean-major integration | 11 passed on the implementation production tree |
| Real Godot 4.7 import/parse | pass; no GDScript parse/load errors |
| Lifecycle smokes | stale, foreign, and compatible-adoption behavior passed on isolated ports |
| Rendering/game capture | pass at 1,920x1,080 with exact quadrant samples |
| Product quit | exact editor process exited with its managed server |

The complete Python result was rerun at `ed69dcd`; the only warning is the
known Starlette/httpx deprecation. The final harness corrections include a
bounded poll interval for the authenticated update
probe, an explicit Windows consoleless-launch fixture, a named 90-second
budget for the post-reload suite (the Windows suite takes more than the former
accidental 30-second HTTP deadline), and a clean-major probe gate that waits
for lifecycle `READY`/`owned` authority before testing the authenticated
transport. The clean-major smoke
expectation matches the existing platform authority contract: Windows continues
after proving its timed-out `cmd.exe` process tree dead; POSIX retains the
migration barrier because possible descendants cannot be disproved. Focused
checks, the Godot import, and architecture gates were rerun after those changes.
The final clean-major matrix passed all four cold/offline/wedged and source-
contract cases; the final focused harness, encoding, and CI-guard subset passed
53 tests.

The final hosted-candidate corrections add no weaker authority path. Linux now
falls back from optional `lsof` to `ss` only to enumerate listener PID
candidates; command branding, launch lineage, the private capability record,
authenticated status, and the start-time fingerprint remain mandatory before
the lifecycle grants ownership. The externally managed plugin-reload reconnect
budget is 90 seconds so a slow Godot 4.7 filesystem scan does not turn a
successful disable/re-enable into a false 15-second timeout. The changed paths
passed 311 focused tests, all architecture gates, a direct Godot parser smoke,
the clean-major matrix, and a real Godot import before hosted dispatch.
The enclosing Windows reload step now has a five-minute budget, pinned by a
source-contract test, because ten successful reload/import cycles consumed the
former two-minute budget before the post-reload suite could finish.
Immutable record readers now tolerate a publisher being descheduled for up to
one second between the atomic hard-link publication and removal of its private
temporary name. Link counts above two never enter that settle path, and a link
that remains at the deadline is still rejected. The exact race and persistent-
link rejection passed 20 repeated focused runs; the complete transaction file
passed 164 tests with one platform skip before the final full-suite run.

## Manual signed self-update

The user clicked Update in the disposable Godot 4.7 editor. The canonical
v4.0.0 -> v4.0.1 flow then completed without another manual confirmation:

- v4.0.0 server ownership was established and authenticated;
- the old server stopped and the coordinator disabled the old plugin;
- the signed v4.0.1 tree was enabled;
- client migration became durable and the migration banner cleared;
- the v4.0.1 server started and authenticated automatically; and
- the retained backup and transaction evidence remained available.

Evidence:

- transaction: `f09a8f9762f8c0f27e73a1d05030e4ea`
- retained backup:
  `/private/tmp/.godot-ai-recovery/4c8153be9993a6c71edfce79/retained-backup`
- editor log:
  `/private/tmp/godot-ai-v4-release-blocker-self-update-20260831/.godot-ai-self-update-smoke/godot-editor.log`
- signing-secret workflow: GitHub Actions run `33457283571`, success

The vNext `_exit_tree` marker appears only at the final normal editor shutdown,
not inside the disable/enable update window. The completed harness lane detected
no new Godot crash report.

## Fresh Python artifacts

Disposable local artifacts were built from `e6fe848`:

- `godot_ai-4.0.0-py3-none-any.whl` — SHA-256
  `dffe9e6eed288fa00632e42d6f553377321a1f25ee7da5aa1b451589a64d90a5`
- `godot_ai-4.0.0.tar.gz` — SHA-256
  `1e7ca93cd4da55a2f488dfcbb6a23c1765acc152d396f60107b86dd08e6e4bdd`

Both archives contain all 123 Python source files. The wheel archive validates,
and its packaged Python tree matches `src/godot_ai` byte-for-byte. These are
fresh local verification artifacts, not the frozen, signed publication bytes.

## Release gates still open

The following remain deliberately open and must not be described as complete:

- reviewed numeric latency/resource ceilings and five repetitions for every
  locked storm profile;
- the complete uniquely addressable external failpoint surface and actual-path
  two-editor/crash/rollback/quarantine/repair matrix against signed fixtures;
- frozen exact source A and minimal qualification child B, their signed plugin
  assets, and complete dependency inventories;
- an independent approval bound to the exact candidate digests;
- the independent public SPKI-fingerprint attestation channel;
- public upload, redownload, and hash/dependency attestation; and
- every publication action.

The repository's release workflow intentionally remains a read-only,
fail-closed gate. No tag, GitHub release, PyPI upload, or other publication was
performed during this checkpoint.
