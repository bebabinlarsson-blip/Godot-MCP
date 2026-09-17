# Pre-v4 updater one-time evidence

This file preserves the result of the one-time compatibility investigation used
to choose the v4 release boundary. It is evidence, not a supported compatibility
matrix and not a recurring CI obligation.

## Audit identity

- Executed: `2026-08-31T08:20:26-07:00`
- Repository: `https://github.com/hi-godot/godot-ai.git`
- Source checkout audited: `dc162f16dab5c095a05c283df28dba891b2e47d0`
- Tag universe: all 104 local `v*` tags from `v0.2.0`
  (`35c6986d8800d5602a19db578f466f5b462fdee9`) through `v3.2.4`
  (`b4bc574e7870de23adf280a32edff79f01727754`)
- Runtime: Godot `4.7.stable.official.5b4e0cb0f`, macOS 26.5.2
  build 25F84, arm64, Python 3.14.5
- Classifier SHA-256:
  `2708ff6e127fd0842683ec1d2ba758d2e4414a0eb696e96266e0f8257f64cfea`
- Release freezer SHA-256:
  `f3a5f6cd4ca44715628ef3a3d92880337607ca4e1efcd439054049d54f9924f1`
- Runtime harness SHA-256:
  `bffa9d6505f6e2885565ea47cb8f3839daa75c08cd920249998316c3eaa6e337`
- Frozen tag inventory SHA-256:
  `bd8ceee454568ae8a39b9f30c154743a9bbbddbee200017a1b57861fbf884b13`
- Frozen GitHub release inventory SHA-256:
  `8f4c1176afc9e35f1e45ca239c5d8e60ddadee4a0256540cbb9ea82b241dad39`
- Full runtime report SHA-256:
  `4cda7410e99133d530b6e8f808c071bd03f2c41b51c61aba917a44020e1f85d4`

The audit tools were uncommitted, purpose-built investigation code identified
by the hashes above; the full report lived at the temporary path below and is
not retained. This record is therefore a compact, non-reproducible attestation,
not independently replayable evidence. That is intentional: pre-v4 support was
dropped, and retaining the tool stack would add thousands of lines of permanent
maintenance surface. The exact per-row outcomes needed to review the conclusion
are preserved below.

For audit archaeology only, the now-deleted harness was invoked as follows.
This command is an archival transcript, not runnable from the current tree:

```bash
python3 script/historical-updater-runtime-smoke \
  --godot /private/tmp/godot-4.7-download/Godot.app/Contents/MacOS/Godot \
  --cache-dir /private/tmp/godot-ai-historical-assets \
  --report /private/tmp/godot-ai-historical-updater-runtime-macos-4.7-final.json
```

## Selection and result

The source classifier found 25 source behavior classes: one no-updater class
covering `v0.2.0` and `v0.3.0`, plus 24 updater classes covering the other 102
tags. Every updater selected the literal legacy payload name
`godot-ai-plugin.zip`. Runtime selection included one exact shipped ZIP per
updater class plus twelve mandatory release milestones; overlaps produced 29
unique rows. The no-updater class was proved from source and did not need a
runtime row.

The mandatory milestones were `v0.3.1`, `v1.0.0`, `v1.5.1`, `v2.1.1`,
`v2.2.0`, `v2.2.2`, `v2.3.1`, `v2.4.0`, `v2.7.6`, `v3.0.0`, `v3.1.5`, and
`v3.2.4`. The classifier normalized comments/layout, hashed the updater's asset
selector, update action, and installer call graph, and chose one tag per unique
digest; the milestone list added release-boundary coverage. Tags with no GitHub
release were excluded from runtime execution but remained represented by their
identical source class. The two no-updater tags were source-only by definition.

The pass predicate required bounded completion, no add-on/project filesystem
mutation, no update staging artifacts, and navigation to the release page
instead of selecting a v4 payload. All 29 runtime rows passed and all 29 had
identical before/after project-tree hashes. The v4 metadata presented to each
row contained exactly:

- `godot-ai-v4-plugin.zip`
- `godot-ai-v4-plugin.manifest.json`
- `godot-ai-v4-plugin.manifest.sig`

It contained no `godot-ai-plugin.zip` legacy alias.

The compact row record below is the retained reviewable outcome.
`class` is the complete normalized updater behavior-class digest; `asset` is
the GitHub asset ID and exact downloaded SHA-256. `retained`/`cleared` records
the legacy implementation's stale-URL behavior; neither state installed v4.

| tag | selection | class | asset | stale URL | result |
|---|---|---|---|---|---|
| v0.3.1 | class + milestone | ebac481237da0792f21820c5ea0d1eea31eafbaee0793189755666ea610f440c | 397432061 / 176ee733d7d5162beb22fd79154c03e4c53565f025f9c8d71b5a7d3624818908 | retained | pass/no mutation |
| v0.3.4 | class | 5960a35e997a37fa84f673899099deea99afdd3815b549a5a6bcc9d329d57ed2 | 397458330 / 4ce716fae225cdb30d8374b8f4ec503fbb6fbd52c7a74c0a10a0ad2d3f567baa | retained | pass/no mutation |
| v1.0.0 | milestone | 5960a35e997a37fa84f673899099deea99afdd3815b549a5a6bcc9d329d57ed2 | 399398817 / a636c68f6a4c1cf178872ed71eeae75842cabc3e8c3a9ebc019a189fd66c3016 | retained | pass/no mutation |
| v1.2.2 | class | ed2e89c4a0794e57070fb603bef6060d58724181c12054d3677c93b07f6ef163 | 400949344 / 75893aa116a68ca1008721e99fd3fd1e5cf627b1d390f25962338553b058167d | retained | pass/no mutation |
| v1.2.3 | class | 9f1b6df5eb07e4803bd648cd17d6b5c2e8bd30b27633427b65bfacf94d30ea40 | 401057316 / 891ab40cab3c58457df227315c6e49f16940d23cff2030264fb6f42865ca6899 | retained | pass/no mutation |
| v1.3.0 | class | 8ef4407750cfb886581b07bffadb59426ff86a1be703ba2544581b82ae72ebf8 | 402077745 / 173e811d60c2cf6368d1c52ba596b04592793a374206ebdd6698b502ea2cfd39 | retained | pass/no mutation |
| v1.3.3 | class | 870a0edc4a383bc5f6ca5d15b75afa82ebb0f5655988c967de080c624b304c92 | 402146886 / e436ae52e37d7cda3279fb20c9113f9249e9b82768cafaa912c95b499c2982e0 | retained | pass/no mutation |
| v1.5.1 | milestone | 8ef4407750cfb886581b07bffadb59426ff86a1be703ba2544581b82ae72ebf8 | 404929637 / 09b0f79525bcacb3896d5c363f6b579750dc2430ecff5b68f062aac645d2c5f5 | retained | pass/no mutation |
| v2.1.1 | milestone | 8ef4407750cfb886581b07bffadb59426ff86a1be703ba2544581b82ae72ebf8 | 406737626 / 7d7f0d77fbd887b6c7e35abc5f57ab0156189265368f09af444516361bf8a0f0 | retained | pass/no mutation |
| v2.1.2 | class | 8b44944ecba8627d5c067417688750b66c8fd60e38753587c5b2a771727eaed6 | 407121738 / 8466e6c1bb77e49bd4c0156b5cc0e4df1029a6992827bc4e0555e2d715a09d63 | retained | pass/no mutation |
| v2.2.0 | class + milestone | 461aa8c9ea3f2f69b62634b9cc246eac30e334a7929425c56cc166534a0d860d | 407607125 / af39cbe22c6fccb940408413f534b8a0c11f5f6a358e306ba824d9fd0f3882a1 | retained | pass/no mutation |
| v2.2.2 | class + milestone | e6ff24789ed99c1228449eba8124c914acbf17ec1c806ffc2bc4dc787b0a277a | 407917754 / eb09e79409bf77f168d840155f37850f67cd071b86749a30172db6d642983819 | retained | pass/no mutation |
| v2.3.0 | class | 759c41afb71bc445baa1f7ad7cc2cd2a57c44b4452d0eb93008100625102634f | 410150619 / fa4844c1583ded4e958c1f855b2af5b3f120e4d01422571f784d8d03742a946b | retained | pass/no mutation |
| v2.3.1 | class + milestone | 6f1880fa4e95aa4ec1023a05bb9b31c2f164e412a8839d17d06f785b772e654f | 410221993 / 6fb3e2bad7f5a7c48cb0ea5851325afe7461766d48654bf6399c3481b4c7aee6 | retained | pass/no mutation |
| v2.4.0 | class + milestone | 77424cf9d55c0dff569c772047c4d89999a9fcaa031bc879c0ea64fa476c9700 | 413830783 / fb9de1dce78f32b2360dd27f5b0b8cc5b673ffed0e10b3aa890fd7887c186fa6 | cleared | pass/no mutation |
| v2.4.4 | class | 5ec1c3473a55e27fccc46803c4276882271a01a496840b1b128fd1ab0572eff7 | 419577530 / f145dff10dbc41052cc183d7d582c4d86a36e17fdda2de94c419701af19c6a72 | cleared | pass/no mutation |
| v2.5.0 | class | 57e393e894f66ade0e369234ce0d9531b0d81dc8e7668dfc8ba87444adccec30 | 420477964 / 653f4cfadc917e7e436dc121660c0bcd381e30774d9626c614e71cbb82e87738 | cleared | pass/no mutation |
| v2.5.8 | class | ac15f218b3c17b43b2e3fe957de9d8d205d68c2708e04d18abba65de4202be76 | 432304699 / e5ac6274d625d75af0f3f1cf65de652a177ee2de18aa483fc0f2f9beb32038c6 | cleared | pass/no mutation |
| v2.7.6 | class + milestone | fd13b0254fe0ee56942d7bbcd0c841b79d2009070186fed14b377e47e6d5a948 | 453142278 / e048c199bf33f6f7222106ecca375a39d76fe552f8b069125d5e109ff282eff5 | cleared | pass/no mutation |
| v2.8.0 | class | 1954ee460ebccabba440c95e4acb73383362282dedaf5a2cca37a38cbb11bc48 | 458837381 / 205f8c70c5e0a544a2e51fdf6b3deda87b259cf3f92daabfc3ff000f9daffcd1 | cleared | pass/no mutation |
| v2.8.5 | class | a1a7bcc18319dcaeb48dbbca2718c53b971b9affdceaf28f557cb8c106689046 | 465862248 / 00f883f7b6988d04c967ab2da5e90a502be7577f7f5fec238663d228c0cd4e6e | cleared | pass/no mutation |
| v2.9.0 | class | 28ac2a5d1ee761f0327073062e3676080734a55eb74aa18d83dd0ec6d7dc24b6 | 466571477 / ac89224574e1b7c686b28e713b6780c9f5f026cf2abece7db94b6559ff02a82e | cleared | pass/no mutation |
| v2.9.2 | class | ba72882849c3a053014f855746f549b65373ad678582754129940a3ce6e46646 | 473675858 / cd1249e5e1c49258b183071ae20e6f504c8dd95a1874eedb99795078fb79347d | cleared | pass/no mutation |
| v3.0.0 | class + milestone | 6ce6e098b6e9d18aec5a2284a3580375d3817a4b746d106b18ac94b288a9c2bb | 475794214 / a5c4838308f49d2f0b81b1af41c56cc549b4914f2e4218aef55eace061fafb41 | cleared | pass/no mutation |
| v3.1.0 | class | 75fbb9ad219770e69274cfc7f04f30afc45ad1efa117e69432320878b7406650 | 500570809 / bb47c48fc5e52684a6872cf8e96dce1c8c41cbf066ee763054b268c2f0a27bc4 | cleared | pass/no mutation |
| v3.1.5 | milestone | 75fbb9ad219770e69274cfc7f04f30afc45ad1efa117e69432320878b7406650 | 510412444 / 20ab1053fb538b4adc00e9bfdb780d119014fd2a60c948f0c594341da1f1032b | cleared | pass/no mutation |
| v3.2.1 | class | de97d462732f8a51da012c3cca7254acb1275b8d1d3eac2d34733aca02f40b8c | 531605140 / ecf882058f5e5ab691cc5ad6f3c3853b8d57a88f6ed90c068c5e492fea5e3b2b | cleared | pass/no mutation |
| v3.2.3 | class | 6ff766e5f8ddc5a4512b5a418f99328f0581c918a53a8f7a2bf5f00055c8cb20 | 532828083 / 331b202de803cbcb974a8a15bd9b3c8902ec70e726ecae2c281b1e578a83947c | cleared | pass/no mutation |
| v3.2.4 | milestone | 6ff766e5f8ddc5a4512b5a418f99328f0581c918a53a8f7a2bf5f00055c8cb20 | 532921707 / 8275d98c66b9932feee2a2a5118768e6699a5827ca798fe6032978845ae16321 | cleared | pass/no mutation |

## Historical conclusion and superseding bridge decision

This audit proved the no-mutation boundary for the then-proposed release shape;
it did not prove a future transition capsule. Pre-v4 updater code remains
immutable and unsupported after the major-version cut. The later approved
design publishes one canonical signed v4 triple plus a separately signed,
legacy-named temporary capsule for the final v3 line. That capsule is not an
alias or final v4 tree: it delegates to the exact-tree v4 actor. Recurring CI
therefore executes the final-v3 bridge separately while this report remains the
non-recurring historical classification of older updater behavior.
