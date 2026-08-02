"""Local pytest configuration for the P2a test package.

Two responsibilities, both test-infrastructure only. Nothing here defines,
wraps, replaces or fixtures any evaluator, loader, reducer or parameter map.

1. Registers the ``production`` marker used by the Phase-5 Increment-A
   integration tests, so no unknown-marker warning is emitted and reviewers can
   select or deselect the slow real-data family with ``-m production`` /
   ``-m "not production"``.

2. **Fix A-5 / review finding ST-1 — test-29 state guard.**
   ``test_p2a_regionlive_phase3_safety.py::test_29_subprocess_dry_run_never_optimizes``
   invokes the Phase-3 runner as a subprocess against the CANONICAL output root
   and therefore appends a dry-run directory to the accepted, never-deleted
   ``outputs/.../phase3_estimation_v1/attempts/`` history on every execution.
   Two accidental full-suite runs did exactly that during Increment A and were
   recorded as an exact-state violation.

   The guard makes that accident LOUD instead of silent: the test now fails in
   *setup*, before its body runs and therefore before the subprocess can write
   anything, unless the operator has explicitly opted in with

       MNL_ALLOW_TEST29=1

   Mission rule (deputy decision §2 A-5): every full-suite command deselects the
   test by name, which keeps the suite green and writes nothing:

       -k "not test_29_subprocess_dry_run_never_optimizes"

   To run test 29 deliberately, set the environment variable for that invocation
   only, and own the resulting ``attempts/`` entry.
"""
import os

import pytest

TEST29_NAME = "test_29_subprocess_dry_run_never_optimizes"
TEST29_OPT_IN_ENV = "MNL_ALLOW_TEST29"

TEST29_DESELECT = f'-k "not {TEST29_NAME}"'


def test29_is_allowed() -> bool:
    """True when the operator has explicitly opted in to writing an attempt."""
    return os.environ.get(TEST29_OPT_IN_ENV, "") == "1"


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "production: exercises the REAL accepted loader/likelihood on a bounded "
        "household subset (slow: JAX traces and compiles per batch)")


def pytest_runtest_setup(item):
    """Fail test 29 in setup -- before its body, and so before it can write.

    Setup runs prior to the test function, so the Phase-3 runner subprocess is
    never spawned and no ``attempts/`` directory is created.
    """
    if item.name.startswith(TEST29_NAME) and not test29_is_allowed():
        pytest.fail(
            f"{TEST29_NAME} writes a new dry-run attempt directory into the "
            f"accepted canonical output root and must never run as part of a "
            f"full-suite invocation (JMP-M05C deputy decision s2 A-5). "
            f"Deselect it with {TEST29_DESELECT}, or opt in deliberately with "
            f"{TEST29_OPT_IN_ENV}=1 and own the resulting attempts/ entry.",
            pytrace=False)
