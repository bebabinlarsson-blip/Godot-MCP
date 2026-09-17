## Summary

Briefly describe the changes introduced by this pull request and the problem they solve.

## Type of Change

- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] New Godot operation / tool domain
- [ ] Documentation update

## Verification Checklist

- [ ] Ran `godot-omni tools stats` and verified tool counts (>= 1,500 operations).
- [ ] Ran `godot-omni self-test` and all 8 checks passed.
- [ ] Ran `pytest tests/unit/test_godot_omni.py` (all tests passed).
- [ ] Ran `ruff check src/ tests/` (no lint errors).
- [ ] Added unit or integration tests for new functionality.
- [ ] Tested with live Godot editor if applicable.
