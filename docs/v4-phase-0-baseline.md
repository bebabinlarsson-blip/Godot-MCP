# v4 Phase 0 Baseline

- Recorded: 2026-08-31
- Repository: `hi-godot/godot-ai`
- Rebuild branch: `v4/architecture-simplification`
- Rebuild worktree: local disposable worktree for
  `v4/architecture-simplification`
- Landing commit: `a468a7eedd7dcbbeb0221a297f7e7c50f5ab2b4e`
- Landing tree: `508149f3ca1f79fa1b60c23cc922e7ff7caa0c9b`
- Landing tag: `checkpoint/v4-rebuild-landing-2026-08-31` (local)
- Approved-plan commit: `c3c8ed338473398318127444a32b43f76b0ddc96`
- Approved-plan tag:
  `checkpoint/v4-architecture-plan-approved-2026-08-31` (local)

This file records what was genuinely executable before the first architecture
change. It is evidence, not permission to weaken a later qualification row.

## Landing decision

PR #940, `feat(project): add set_main_scene so a scaffolded project can boot`,
was accepted independently before pinning the rebuild:

- reviewed head: `d4f16f538710674e01136b1e0ba88bf458c120f4`;
- base before merge: `66ef3f5c60f0d6a7d0ec234453592f17c1d01cd1`;
- merge commit: `a468a7eedd7dcbbeb0221a297f7e7c50f5ab2b4e`;
- GitHub Actions run: `33358541452`;
- merge state before acceptance: clean and mergeable;
- all 23 Actions checks plus CodeRabbit: successful;
- local exact-head focused verification: 19 tests passed, lint and Godot import
  passed;
- local landing verification below includes the merged change.

The required PR-activity subscription capability was not exposed to this
session, so the repository instruction to call it could not be performed.

## Preserved oracle

- Oracle commit: `957add991347e94443014cf97079d72713fb05c2`
- Oracle tree: `978953001923f91cbbaf01495b4450602cb26d86`
- Oracle tag: `checkpoint/architecture-hardening-2026-08-30-draft1`
- Complete-history bundle SHA-256:
  `7ecd39304983a9be04b2ee683f6479c718fc2d2e692e0d3da1765f15e03e001a`
- Source tar SHA-256:
  `90bedf68606d28752b2d166befec743c3a9b4801202e725e86dbf3c6eb6e902d`

No oracle implementation commit was cherry-picked into the rebuild.

## Local toolchain

| Input | Exact value |
|---|---|
| Host | macOS 26.5.2 (25F84), arm64 |
| Python | 3.14.5, isolated `.venv` |
| pytest | 9.1.1 |
| ruff | 0.16.5 |
| uv | 0.11.7 (`9d177269e`) |
| OpenSSL | 3.6.2 |
| Godot archive | `Godot_v4.7-stable_macos.universal.zip` |
| Godot archive source | `https://github.com/godotengine/godot/releases/download/4.7-stable/Godot_v4.7-stable_macos.universal.zip` |
| Godot archive SHA-256 | `a6708c336f690e0dd8abd3d587d661707f4f33ed436946a3ec000d2fb497fd6c` |
| Godot version | `4.7.stable.official.5b4e0cb0f` |
| Godot binary SHA-256 | `445c6f95030e2ca767dd921be1e91bd99e50c3703f91d22a22cd31216c93a80f` |

Godot ran from an isolated, self-contained temporary installation with private
EditorSettings and ports `18127`/`19627`. Telemetry was disabled. It did not
reuse or modify the user's global Godot settings.

## Green baseline

| Gate | Result |
|---|---|
| `ruff check src tests` | pass |
| `pytest -q` | 1,857 passed; 6 skipped; 1 deprecation warning |
| Godot 4.7 `--import` plus `script/ci-check-gdscript` | pass; no parse/load errors |
| Live `script/ci-godot-tests` | 2,327 passed; 0 failed; 27 skipped; 70/70 suites |
| Worktree link verification | pass |

The six Python and 27 Godot skips are baseline facts, not qualification
waivers. The final v4 verification contract still requires zero skipped
mandatory rows.

## Known Phase 0/1 gaps

- Exact Windows and Linux machine/tool binary hashes are not yet captured.
- Python 3.11 and 3.13 were green in PR #940 CI, but their complete resolved
  environment reports are not yet frozen.
- CI runner labels float; qualification needs observed image identities.
- Historical release assets are not yet cached and hashed.
- Historical tags are lightweight; the checked-in inventory must bind every
  name to a full commit and remote release record.
- Numeric storm thresholds and effect-level failpoint IDs must be frozen in
  Phase 1 before their corresponding architecture changes.
- The standalone bootstrap verifier and independent fingerprint publication
  surface do not exist yet.
- `.github/workflows/verify-signing.yml` does not yet select the protected
  `release-signing` environment used by the release workflow.
- Successful CI runs do not yet retain the complete machine-readable evidence
  required by final qualification.

These gaps block candidate qualification, not the characterization-only Phase
1 work that resolves or freezes them.
