"""Increment-A tests for the Phase-5 streaming score reducer.

Subject under review: ``scripts/p2a/p2a_phase5_score_stream.py``.

Reviewer-runnable proof rule (charter s5). Nothing under review is replaced:

  * the parameter map is the committed one;
  * the loader is ``dclaborsupply.data.loader.load_singles``;
  * the likelihood is ``engine_jax.build_jax_singles_ll(..., per_group=True)``;
  * the reducer is ``ScoreStreamReducer``;
  * the ONLY thing patched is the household subset size
    (``build_production_binding(household_limit=...)``).

Test families
-------------
  A  parameter-map authentication + T-17 fingerprints
  B  canonical household order (design v4 s6.3 order (b))
  C  deterministic synthetic reducer fixtures (exact aggregates + exact digest)
  D  no row-level persistence (static, behavioural, failure-path)
  E  REAL production-path integration on a bounded subset, cross-checked
     against a direct ``jax.jacrev`` computation on the same subset

Family E is slow (JAX traces + compiles per batch). Run it with
``-m production`` or skip it with ``-m "not production"``.

No test writes, prints, or otherwise emits a household score value.
"""
from __future__ import annotations

import ast
import gc
import hashlib
import json
import struct
import sys
import weakref
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

MNL_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(MNL_ROOT / "scripts" / "p2a"))

import p2a_phase5_score_stream as sst  # noqa: E402

MODULE_PATH = MNL_ROOT / "scripts" / "p2a" / "p2a_phase5_score_stream.py"

# bounded production subset: the ONLY patched quantity (charter s5)
SUBSET_HOUSEHOLDS = 24
# Fix A-3: design v4 T-16 freezes the cross-mode check at the FIRST 64
# canonical households. T-11's chunk comparison is run on the same slice.
T16_HOUSEHOLDS = 64

# design v4 s14 / s16 tolerances exercised here
T11_CHUNK_INVARIANCE_REL = 1e-12      # <= 1e-12 * max|S|
T16_MODE_AGREEMENT_REL = 1e-10        # <= 1e-10 * max|S|


# --------------------------------------------------------------------------- #
# deterministic synthetic fixture
#   s[i, j] = (i + 1) * c_j            c_j = (j mod 5) - 2,  i = 0..5
# every entry is a small integer, hence exact in float64. Therefore
#   sum_i s[i, :]      = (1+2+3+4+5+6) * c      = 21 * c
#   (S^T S)[j, k]      = (1+4+9+16+25+36) c_j c_k = 91 * c_j c_k
#   (S_I^T S_I)[j, k]  = 91 * c_I[j] c_I[k]
# and every accumulation is exact regardless of summation order, so the
# aggregates are bitwise batch-size invariant.
# --------------------------------------------------------------------------- #
SYNTH_IDS = np.array([10, 20, 30, 40, 50, 60], dtype=np.int64)
SYNTH_C = np.array([(j % 5) - 2 for j in range(sst.N_FREE)], dtype=np.float64)
SYNTH_SCORES = np.outer(np.arange(1, 7, dtype=np.float64), SYNTH_C)
SYNTH_SUM_COEF = 21.0     # sum_{i=1..6} i
SYNTH_SQ_COEF = 91.0      # sum_{i=1..6} i^2

# The documented digest convention, pinned as a constant so it cannot drift
# silently: sha256 over  struct.pack("<q", idhh) || s_g.astype("<f8").tobytes()
# for the six fixture households in ascending id order.
SYNTH_DIGEST = "a077a2ab7b5e8141247dd6bdd3591669b795511ad6881409988353ed3327175c"


@pytest.fixture(scope="module")
def pmap():
    return sst.load_parameter_map(MNL_ROOT)


@pytest.fixture()
def synth_order():
    return sst.build_canonical_order(SYNTH_IDS[[0, 2, 4]], SYNTH_IDS[[1, 3, 5]])


def _expected_digest(ids, scores):
    """Independent re-implementation of the addendum s2 byte convention."""
    h = hashlib.sha256()
    for k in range(len(ids)):
        h.update(struct.pack("<q", int(ids[k])))
        h.update(np.asarray(scores[k], dtype="<f8").tobytes())
    return h.hexdigest()


def _feed(order, pmap_, scores, batch_size):
    """Drive the reducer with caller-supplied score rows (synthetic path)."""
    reducer = sst.ScoreStreamReducer(pmap_, order, batch_size=batch_size)
    for batch in order.batches(batch_size):
        block = np.ascontiguousarray(scores[batch.position:batch.position + batch.size])
        reducer.update(batch, block)
        del block
    return reducer.result()


# =========================================================================== #
# A. parameter-map authentication
# =========================================================================== #
def test_A1_parameter_map_dimensions_and_active_set(pmap):
    assert len(pmap.all_names) == 47
    assert len(pmap.free_names) == sst.N_FREE == 37
    assert len(pmap.interior_names) == sst.N_INTERIOR == 35
    assert len(pmap.pin_names) == 10
    # design v4 s7.2: interior = free minus free positions {2, 6}, BY NAME
    assert pmap.active_positions_in_free == (2, 6)
    assert tuple(pmap.free_names[p] for p in pmap.active_positions_in_free) \
        == sst.ACTIVE_BOUND_NAMES
    assert len(pmap.interior_positions_in_free) == 35
    assert set(pmap.interior_positions_in_free) | {2, 6} == set(range(37))


def test_A2_t17_fingerprints_match_phase4_manifest(pmap):
    """T-17: fingerprints recomputed from phase4_manifest.json must agree."""
    manifest = json.loads((MNL_ROOT / sst.PHASE4_MANIFEST).read_text(encoding="utf-8"))
    free_names = list(manifest["contract"]["parameter_map"]["free_names"])
    assert free_names == list(pmap.free_names)
    recomputed = hashlib.sha256("\n".join(free_names).encode("utf-8")).hexdigest()
    assert recomputed == pmap.free_names_sha256
    interior = [n for n in free_names if n not in sst.ACTIVE_BOUND_NAMES]
    assert hashlib.sha256("\n".join(interior).encode("utf-8")).hexdigest() \
        == pmap.interior_names_sha256


def test_A3_parameter_map_rejects_a_tampered_manifest(tmp_path):
    """FAILURE DEMONSTRATION: a manifest whose free_names order is permuted."""
    manifest = json.loads((MNL_ROOT / sst.PHASE4_MANIFEST).read_text(encoding="utf-8"))
    names = manifest["contract"]["parameter_map"]["free_names"]
    names[0], names[1] = names[1], names[0]
    fake_root = tmp_path / "fake"
    (fake_root / Path(sst.PHASE4_MANIFEST).parent).mkdir(parents=True)
    (fake_root / sst.PHASE4_MANIFEST).write_text(json.dumps(manifest), encoding="utf-8")
    (fake_root / Path(sst.PARAMETER_MAP_CSV).parent).mkdir(parents=True)
    (fake_root / sst.PARAMETER_MAP_CSV).write_bytes(
        (MNL_ROOT / sst.PARAMETER_MAP_CSV).read_bytes())
    with pytest.raises(sst.ScoreStreamError, match="free-name sequence"):
        sst.load_parameter_map(fake_root)


# =========================================================================== #
# B. canonical household order
# =========================================================================== #
def test_B1_order_is_idhh_ascending_across_genders():
    order = sst.build_canonical_order(np.array([30, 10, 50]), np.array([20, 60, 40]))
    assert order.idhh.tolist() == [10, 20, 30, 40, 50, 60]
    assert order.is_male.tolist() == [True, False, True, False, True, False]
    assert np.all(np.diff(order.idhh) > 0)
    assert order.order_sha256 == hashlib.sha256(
        "10\n20\n30\n40\n50\n60".encode("utf-8")).hexdigest()


def test_B2_batches_partition_the_order_exactly():
    order = sst.build_canonical_order(np.arange(0, 10, 2), np.arange(1, 10, 2))
    for bs in (1, 2, 3, 4, 7, 10, 25):
        seen, pos = [], 0
        for batch in order.batches(bs):
            assert batch.position == pos
            assert batch.size <= bs
            seen.append(batch.idhh)
            pos += batch.size
        assert pos == order.n_households
        assert np.concatenate(seen).tolist() == order.idhh.tolist()


def test_B3_order_rejects_overlapping_gender_id_sets():
    """FAILURE DEMONSTRATION: a household appearing in both builders."""
    with pytest.raises(sst.ScoreStreamError, match="strictly increasing"):
        sst.build_canonical_order(np.array([10, 20]), np.array([20, 30]))


def test_B4_order_rejects_non_integral_identifiers():
    with pytest.raises(sst.ScoreStreamError, match="not integral"):
        sst.build_canonical_order(np.array([10.5, 20.0]), np.array([30.0]))


# =========================================================================== #
# C. deterministic synthetic reducer fixtures
# =========================================================================== #
def test_C1_exact_aggregate_vector(pmap, synth_order):
    res = _feed(synth_order, pmap, SYNTH_SCORES, 2)
    expected = SYNTH_SUM_COEF * SYNTH_C
    assert res.score_sum_free37.shape == (37,)
    assert np.array_equal(res.score_sum_free37, expected)      # bitwise
    assert res.n_households == 6
    assert res.dim_free == 37 and res.dim_interior == 35


def test_C2_exact_meat_blocks(pmap, synth_order):
    res = _feed(synth_order, pmap, SYNTH_SCORES, 2)
    m37_expected = SYNTH_SQ_COEF * np.outer(SYNTH_C, SYNTH_C)
    assert res.meat_free37.shape == (37, 37)
    assert np.array_equal(res.meat_free37, m37_expected)       # bitwise
    c_i = SYNTH_C[np.asarray(pmap.interior_positions_in_free)]
    m35_expected = SYNTH_SQ_COEF * np.outer(c_i, c_i)
    assert res.meat_interior35.shape == (35, 35)
    assert np.array_equal(res.meat_interior35, m35_expected)   # bitwise
    # the 35x35 block IS the by-name interior selection of the 37x37 block
    sel = np.asarray(pmap.interior_positions_in_free)
    assert np.array_equal(res.meat_interior35, res.meat_free37[np.ix_(sel, sel)])


def test_C3_exact_digest_matches_the_documented_convention(pmap, synth_order):
    res = _feed(synth_order, pmap, SYNTH_SCORES, 2)
    assert res.score_stream_sha256 == _expected_digest(SYNTH_IDS, SYNTH_SCORES)
    assert res.score_stream_sha256 == SYNTH_DIGEST
    assert res.idhh_encoding == "int64_le"
    assert res.dtype == "float64" and res.byte_order == "little"
    assert res.bytes_per_household == 8 + 37 * 8 == 304


def test_C4_batch_size_invariance_is_bitwise(pmap, synth_order):
    """Reducer-level chunking invariance: identical results at every chunking."""
    ref = _feed(synth_order, pmap, SYNTH_SCORES, 1)
    for bs in (2, 3, 4, 5, 6, 11):
        res = _feed(synth_order, pmap, SYNTH_SCORES, bs)
        assert res.score_stream_sha256 == ref.score_stream_sha256
        assert np.array_equal(res.score_sum_free37, ref.score_sum_free37)
        assert np.array_equal(res.meat_free37, ref.meat_free37)
        assert np.array_equal(res.meat_interior35, ref.meat_interior35)
        assert res.n_batches == -(-6 // bs)


def test_C5_failure_wrong_order(pmap, synth_order):
    """FAILURE DEMONSTRATION: batches fed out of canonical order."""
    batches = list(synth_order.batches(2))
    reducer = sst.ScoreStreamReducer(pmap, synth_order, batch_size=2)
    with pytest.raises(sst.ScoreStreamError, match="out-of-order batch"):
        reducer.update(batches[1], SYNTH_SCORES[2:4])


def test_C6_failure_permuted_identifiers_within_a_batch(pmap, synth_order):
    """FAILURE DEMONSTRATION: right households, wrong internal order."""
    batch = next(iter(synth_order.batches(3)))
    bad = sst.HouseholdBatch(position=0,
                             idhh=batch.idhh[::-1].copy(),
                             is_male=batch.is_male[::-1].copy())
    reducer = sst.ScoreStreamReducer(pmap, synth_order, batch_size=3)
    with pytest.raises(sst.ScoreStreamError, match="do not match the canonical order"):
        reducer.update(bad, SYNTH_SCORES[:3])


@pytest.mark.parametrize("corrupt,pattern", [
    ("rows", "score shape"),
    ("cols", "score shape"),
    ("dtype", "score dtype"),
    ("type", "must be a numpy array"),
])
def test_C7_failure_corrupted_batch(pmap, synth_order, corrupt, pattern):
    """FAILURE DEMONSTRATION: shape / dtype / type corruption of S_b."""
    batch = next(iter(synth_order.batches(3)))
    good = SYNTH_SCORES[:3]
    bad = {"rows": good[:2],
           "cols": good[:, :36],
           "dtype": good.astype(np.float32),
           "type": good.tolist()}[corrupt]
    reducer = sst.ScoreStreamReducer(pmap, synth_order, batch_size=3)
    with pytest.raises(sst.ScoreStreamError, match=pattern):
        reducer.update(batch, bad)


@pytest.mark.parametrize("bad_value", [np.nan, np.inf, -np.inf])
def test_C8_failure_non_finite_scores(pmap, synth_order, bad_value):
    """FAILURE DEMONSTRATION: NaN / +-Inf anywhere in the batch."""
    batch = next(iter(synth_order.batches(3)))
    block = SYNTH_SCORES[:3].copy()
    block[1, 17] = bad_value
    reducer = sst.ScoreStreamReducer(pmap, synth_order, batch_size=3)
    with pytest.raises(sst.ScoreStreamError, match="non-finite score entries"):
        reducer.update(batch, block)


def test_C9_failure_incomplete_stream(pmap, synth_order):
    """FAILURE DEMONSTRATION: result() before the order is exhausted."""
    batch = next(iter(synth_order.batches(3)))
    reducer = sst.ScoreStreamReducer(pmap, synth_order, batch_size=3)
    reducer.update(batch, SYNTH_SCORES[:3])
    with pytest.raises(sst.ScoreStreamError, match="incomplete stream"):
        reducer.result()


# =========================================================================== #
# D. no row-level persistence  (addendum s6 / T-23S)
# =========================================================================== #
_FORBIDDEN_WRITE_CALLS = {
    "save", "savez", "savez_compressed", "savetxt", "tofile",
    "to_csv", "to_parquet", "to_pickle", "to_json", "to_feather", "to_hdf",
    "write", "writelines", "write_text", "write_bytes",
    "dump",                       # json.dump / pickle.dump / np lib dump
    "print",
}
_FORBIDDEN_IMPORTS = {"pickle", "shelve", "csv", "sqlite3", "logging", "shutil", "tempfile"}


def test_D1_static_no_write_path_in_the_module():
    """STATIC: the module contains no persistence call and no write-mode open()."""
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            name = fn.attr if isinstance(fn, ast.Attribute) else \
                (fn.id if isinstance(fn, ast.Name) else None)
            if name in _FORBIDDEN_WRITE_CALLS:
                offenders.append((name, node.lineno))
            if name == "open":
                mode = None
                if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                    mode = node.args[1].value
                for kw in node.keywords:
                    if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                        mode = kw.value.value
                if not (isinstance(mode, str) and mode.startswith("r")):
                    offenders.append((f"open(mode={mode!r})", node.lineno))
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            mods = ([a.name.split(".")[0] for a in node.names]
                    if isinstance(node, ast.Import)
                    else [(node.module or "").split(".")[0]])
            for m in mods:
                if m in _FORBIDDEN_IMPORTS:
                    offenders.append((f"import {m}", node.lineno))
    assert offenders == [], f"write-capable constructs found: {offenders}"


def test_D2_static_scanner_actually_catches_a_write(tmp_path):
    """FAILURE DEMONSTRATION: the D1 scanner is not vacuous."""
    probe = tmp_path / "probe.py"
    probe.write_text("import numpy as np\n"
                     "def f(S, p):\n"
                     "    np.save(p, S)\n"
                     "    open(p, 'w').write('x')\n", encoding="utf-8")
    tree = ast.parse(probe.read_text(encoding="utf-8"))
    found = [n.func.attr if isinstance(n.func, ast.Attribute) else n.func.id
             for n in ast.walk(tree) if isinstance(n, ast.Call)
             and (getattr(n.func, "attr", None) in _FORBIDDEN_WRITE_CALLS
                  or getattr(n.func, "id", None) in _FORBIDDEN_WRITE_CALLS
                  or getattr(n.func, "id", None) == "open")]
    assert "save" in found and "write" in found and "open" in found


def test_D3_result_object_exposes_no_row_level_score(pmap, synth_order):
    """The aggregate result carries nothing of shape (G, 37) or (G,)."""
    res = _feed(synth_order, pmap, SYNTH_SCORES, 2)
    shapes = []
    for value in vars(res).values():
        if isinstance(value, np.ndarray):
            shapes.append(value.shape)
    assert shapes == [(37,), (37, 37), (35, 35)]
    for shape in shapes:
        assert res.n_households not in shape


def test_D4_reducer_retains_no_reference_to_the_batch(pmap, synth_order):
    """BEHAVIOURAL: after update(), the batch array is unreachable from the reducer."""
    reducer = sst.ScoreStreamReducer(pmap, synth_order, batch_size=6)
    batch = next(iter(synth_order.batches(6)))
    block = SYNTH_SCORES.copy()
    ref = weakref.ref(block)
    reducer.update(batch, block)
    del block
    gc.collect()
    assert ref() is None, "the reducer is holding the transient batch alive"
    res = reducer.result()
    assert res.n_households == 6


def test_D5_no_file_is_created_anywhere(tmp_path, monkeypatch, pmap, synth_order):
    """BEHAVIOURAL: a full synthetic stream creates no filesystem member."""
    monkeypatch.chdir(tmp_path)
    before = _snapshot(MNL_ROOT / "outputs" / "p2a_singles2016" / "region_live_v1")
    _feed(synth_order, pmap, SYNTH_SCORES, 2)
    assert list(tmp_path.rglob("*")) == []
    assert _snapshot(MNL_ROOT / "outputs" / "p2a_singles2016" / "region_live_v1") == before


def test_D6_failure_path_leaks_no_score_bytes(tmp_path, monkeypatch, pmap, synth_order):
    """The non-finite failure raises WITHOUT any score value in the message,
    and without leaving a temporary batch on disk."""
    monkeypatch.chdir(tmp_path)
    batch = next(iter(synth_order.batches(3)))
    block = SYNTH_SCORES[:3].copy()
    block[2, 4] = np.nan
    reducer = sst.ScoreStreamReducer(pmap, synth_order, batch_size=3)
    with pytest.raises(sst.ScoreStreamError) as exc:
        reducer.update(batch, block)
    message = str(exc.value)
    assert "nan" not in message.lower()
    for value in np.unique(np.abs(SYNTH_SCORES[np.isfinite(SYNTH_SCORES)])):
        if value == 0:
            continue
        assert repr(float(value)) not in message
    assert list(tmp_path.rglob("*")) == []


# --- Fix A-1: failure-path transient-score release (review finding NP-1) ---- #
@pytest.mark.parametrize("bad_value", [np.nan, np.inf, -np.inf])
def test_D9_failure_exception_graph_holds_no_score(pmap, synth_order, bad_value):
    """Fix A-1: the caller-visible exception retains NO row-level score.

    Traverses the complete final exception object graph -- traceback frames and
    their locals, ``__context__``, ``__cause__``, args and attribute payloads,
    and containers reachable from them -- and fails on any retained score block.
    This is the check the shipped v1 test lacked; the reviewer's probe found the
    ``(3, 37)`` array in three module frames through ``__traceback__``.
    """
    reducer = sst.ScoreStreamReducer(pmap, synth_order, batch_size=3)
    batch = next(iter(synth_order.batches(3)))
    block = SYNTH_SCORES[:3].copy()
    block[1, 17] = bad_value

    exc = _capture_update_failure(reducer, batch, block)

    assert exc.code == "SS-NONFINITE"
    assert exc.__cause__ is None
    assert exc.__context__ is None
    assert exc.__suppress_context__ is True
    permitted = (reducer._m37, reducer._m35, reducer._g37)
    leaks = _score_leaks(exc, block, permitted_aggregates=permitted)
    assert leaks == [], f"score data reachable from the raised exception: {leaks}"


def test_D10_graph_walker_and_leak_detector_are_not_vacuous():
    """FAILURE DEMONSTRATION: the D9 machinery detects a leak when one exists.

    Builds an exception that deliberately retains the score block the way the
    pre-fix code did -- through a traceback frame local, through ``__context__``
    and through an attribute payload -- and asserts every route is reported."""
    block = SYNTH_SCORES[:3].copy()

    def leaky_frame_local(scores):
        raise sst.ScoreStreamError("leak via frame local", code="SS-PROBE")

    # (a) traceback frame local
    try:
        leaky_frame_local(block)
    except sst.ScoreStreamError as exc:
        via_frame = exc
    assert any("f_locals" in p for p, _ in _score_leaks(via_frame, block))

    # (b) __context__ chain
    inner = sst.ScoreStreamError("inner", code="SS-PROBE")
    inner.payload = block
    outer = sst.ScoreStreamError("outer", code="SS-PROBE")
    outer.__context__ = inner
    assert any("__context__" in p for p, _ in _score_leaks(outer, block))

    # (c) attribute payload / __cause__
    caused = sst.ScoreStreamError("caused", code="SS-PROBE")
    caused.__cause__ = inner
    assert any("__cause__" in p for p, _ in _score_leaks(caused, block))

    # (d) raw bytes payload
    byteful = sst.ScoreStreamError("bytes", code="SS-PROBE")
    byteful.blob = block.tobytes()
    assert any(kind == "raw score bytes" for _, kind in _score_leaks(byteful, block))

    # (e) rule 4 flags any OTHER 2-D 37-column array, and the explicit
    # permitted_aggregates exemption is identity-scoped
    rows = np.zeros((5, sst.N_FREE))
    holder = sst.ScoreStreamError("rows", code="SS-PROBE")
    holder.m = rows
    assert _score_leaks(holder, block, permitted_aggregates=()) != []
    assert _score_leaks(holder, block, permitted_aggregates=(rows,)) == []
    # the two addendum s2 aggregate shapes are exempt from rule 4 by shape
    for shape in ((sst.N_FREE, sst.N_FREE), (sst.N_INTERIOR, sst.N_INTERIOR)):
        agg = sst.ScoreStreamError("agg", code="SS-PROBE")
        agg.m = np.zeros(shape)
        assert _score_leaks(agg, block) == []


def test_D20_traversal_is_deterministic_and_the_shape_exemption_is_not_a_hole(
        pmap, synth_order):
    """Fix A-1 soundness: the detector must not go green by accident.

    (a) Repeated traversals of the same exception must return the identical node
        set. An id()-keyed visited set that does not pin its objects can skip a
        node whose id was recycled from a freed temporary -- a false green. The
        walker keeps every visited object alive; this asserts the consequence.

    (b) The rule-4 exemption is by aggregate shape, so a retained score block
        that happens to be 37x37 would slip past rule 4. Assert that rules 1-3
        catch it anyway.
    """
    reducer = sst.ScoreStreamReducer(pmap, synth_order, batch_size=3)
    batch = next(iter(synth_order.batches(3)))
    block = SYNTH_SCORES[:3].copy()
    block[0, 5] = np.inf
    exc = _capture_update_failure(reducer, batch, block)

    runs = [[p for p, _ in _walk_exception_graph(exc)] for _ in range(6)]
    assert all(r == runs[0] for r in runs), "traversal is not deterministic"
    assert any(p.endswith("['_m37']") for p in runs[0]), \
        "traversal never reached the reducer's own aggregates - it is too shallow"
    verdicts = [_score_leaks(exc, block, (reducer._m37,)) for _ in range(6)]
    assert all(v == [] for v in verdicts), verdicts

    # (b) a 37x37 score block is shape-exempt from rule 4 but caught by rules 1-3
    square = np.zeros((sst.N_FREE, sst.N_FREE), dtype=np.float64)
    holder = sst.ScoreStreamError("probe", code="SS-PROBE")
    holder.retained = square
    assert _score_leaks(holder, square) != []
    view = sst.ScoreStreamError("probe", code="SS-PROBE")
    view.retained = square[:2]
    assert _score_leaks(view, square) != []


def test_D11_failed_reducer_is_poisoned(pmap, synth_order):
    """Fix A-1: a reducer that recorded a failed batch can never yield a result."""
    reducer = sst.ScoreStreamReducer(pmap, synth_order, batch_size=3)
    batch = next(iter(synth_order.batches(3)))
    block = SYNTH_SCORES[:3].copy()
    block[0, 0] = np.nan
    _capture_update_failure(reducer, batch, block)

    with pytest.raises(sst.ScoreStreamError, match="SS-POISONED"):
        reducer.result()
    good = next(iter(synth_order.batches(3)))
    with pytest.raises(sst.ScoreStreamError, match="SS-POISONED"):
        reducer.update(good, SYNTH_SCORES[:3])


def test_D12_foreign_exception_message_is_suppressed():
    """Fix A-1: a foreign exception's message never reaches the caller, because
    a third-party message may embed array values."""
    foreign = ValueError("operands could not be broadcast: [1.234567, 8.9]")
    clean = sst._sanitize(foreign, "SS-EVAL")
    assert isinstance(clean, sst.ScoreStreamError)
    assert clean.code == "SS-EVAL"
    assert "1.234567" not in str(clean)
    assert "broadcast" not in str(clean)
    assert "ValueError" in str(clean)
    assert clean.__traceback__ is None
    assert clean.__cause__ is None and clean.__context__ is None
    # our own errors keep their (value-free) message and code verbatim
    mine = sst.ScoreStreamError("[SS-SHAPE] score shape (2, 37) != (3, 37)",
                                code="SS-SHAPE")
    kept = sst._sanitize(mine, "SS-EVAL")
    assert str(kept) == str(mine) and kept.code == "SS-SHAPE"


# --- Fix A-2: strict canonical household-ID validation (finding DG-1) ------- #
def _forged_batch(values, dtype, reference):
    """A batch whose ids are a forged representation of ``reference``."""
    return sst.HouseholdBatch(position=0,
                              idhh=np.array(values, dtype=dtype),
                              is_male=np.asarray(reference.is_male[:len(values)]))


@pytest.mark.parametrize("values,dtype,label", [
    ([10.5, 20.5, 30.5], np.float64, "fractional floats (the reviewer's forgery)"),
    ([10.0, 20.0, 30.0], np.float64, "numerically integral floats"),
    ([10.0, np.nan, 30.0], np.float64, "NaN"),
    ([10.0, np.inf, 30.0], np.float64, "+Inf"),
    ([10.0, -np.inf, 30.0], np.float64, "-Inf"),
    ([1e300, 2e300, 3e300], np.float64, "out of int64 range"),
    ([10, 20, 30], np.float32, "float32"),
    ([10, 20, 30], np.int32, "int32 (narrower)"),
    ([10, 20, 30], np.uint64, "unsigned"),
    ([10, 20, 30], ">i8", "non-native byte order"),
    ([10, 20, 30], object, "object"),
    (["10", "20", "30"], None, "strings"),
    ([True, False, True], np.bool_, "bool"),
])
def test_D13_reducer_rejects_non_canonical_ids(pmap, synth_order, values, dtype, label):
    """Fix A-2: every non-canonical ID representation is refused BEFORE hashing.

    The reducer must reject, not coerce: a forged ``.5`` identifier previously
    reached the digest as its truncated integer."""
    reducer = sst.ScoreStreamReducer(pmap, synth_order, batch_size=3)
    batch = _forged_batch(values, dtype, synth_order)
    with pytest.raises(sst.ScoreStreamError, match="SS-IDDTYPE|SS-IDTYPE") as err:
        reducer.update(batch, SYNTH_SCORES[:3])
    assert err.value.code in {"SS-IDDTYPE", "SS-IDTYPE"}, label
    # nothing was folded and nothing was hashed
    assert reducer._cursor == 0


def test_D14_forged_floats_cannot_reproduce_the_integer_digest(pmap, synth_order):
    """Fix A-2 / R-32a freeze condition: `.5` identifiers can no longer hash as
    their truncated integers, because they cannot be hashed at all."""
    honest = sst.ScoreStreamReducer(pmap, synth_order, batch_size=6)
    honest.update(next(iter(synth_order.batches(6))), SYNTH_SCORES)
    reference = honest.result().score_stream_sha256
    assert reference == SYNTH_DIGEST

    forged_ids = np.asarray(synth_order.idhh, dtype=np.float64) + 0.5
    forged = sst.HouseholdBatch(position=0, idhh=forged_ids,
                                is_male=np.asarray(synth_order.is_male))
    reducer = sst.ScoreStreamReducer(pmap, synth_order, batch_size=6)
    with pytest.raises(sst.ScoreStreamError, match="SS-IDDTYPE"):
        reducer.update(forged, SYNTH_SCORES)
    # the digest of an empty stream is not the honest digest, and the reducer is
    # poisoned so it can never be coaxed into emitting one
    with pytest.raises(sst.ScoreStreamError, match="SS-POISONED"):
        reducer.result()


def test_D15_canonical_int64_ids_pass(pmap, synth_order):
    """Fix A-2: the production representation is accepted unchanged."""
    assert synth_order.idhh.dtype == np.dtype(np.int64)
    batch = next(iter(synth_order.batches(6)))
    assert batch.idhh.dtype == np.dtype(np.int64)
    assert batch.idhh.flags["C_CONTIGUOUS"]
    reducer = sst.ScoreStreamReducer(pmap, synth_order, batch_size=6)
    reducer.update(batch, SYNTH_SCORES)
    assert reducer.result().score_stream_sha256 == SYNTH_DIGEST


@pytest.mark.parametrize("values,dtype,pattern", [
    ([10.5, 20.0], np.float64, "SS-IDFRACTIONAL"),
    ([10.0, np.nan], np.float64, "SS-IDNONFINITE"),
    ([1e300, 2.0], np.float64, "SS-IDRANGE"),
    ([2 ** 63, 2], np.uint64, "SS-IDRANGE"),
    (["10", "20"], None, "SS-IDDTYPE"),
    ([True, False], np.bool_, "SS-IDDTYPE"),
])
def test_D16_loader_id_conversion_validates_before_casting(values, dtype, pattern):
    """Fix A-2: the one permitted conversion checks the ORIGINAL dtype first.

    The previous `_as_int64_ids` cast to int64 and only then compared, so an
    out-of-range or non-integral value was truncated before it was inspected."""
    arr = np.array(values, dtype=dtype)
    with pytest.raises(sst.ScoreStreamError, match=pattern):
        sst._loader_ids_to_canonical(arr, "probe")


def test_D17_loader_id_conversion_accepts_the_real_loader_dtypes():
    """Integral floats and narrower ints from the loader convert exactly."""
    for arr in (np.array([3, 1, 2], dtype=np.int64),
                np.array([3, 1, 2], dtype=np.int32),
                np.array([3, 1, 2], dtype=np.uint32),
                np.array([3.0, 1.0, 2.0], dtype=np.float64)):
        out = sst._loader_ids_to_canonical(arr, "probe")
        assert out.dtype == np.dtype(np.int64)
        assert out.flags["C_CONTIGUOUS"]
        assert out.tolist() == [3, 1, 2]


# --- Fix A-5: test-29 state guard (review finding ST-1) --------------------- #
def test_D18_test29_guard_is_installed_and_blocks_by_default(monkeypatch):
    """Fix A-5: the guard fails test 29 in SETUP, before it can write.

    Verified against the real ``conftest.pytest_runtest_setup`` hook with a
    stand-in item, so no Phase-3 subprocess is spawned and no ``attempts/``
    directory is created by this test."""
    import conftest as p2a_conftest

    class _Item:
        def __init__(self, name):
            self.name = name

    monkeypatch.delenv(p2a_conftest.TEST29_OPT_IN_ENV, raising=False)
    assert p2a_conftest.test29_is_allowed() is False
    # pytest.fail raises Failed, which derives from BaseException, not Exception
    with pytest.raises(pytest.fail.Exception) as err:
        p2a_conftest.pytest_runtest_setup(_Item(p2a_conftest.TEST29_NAME))
    assert "attempts/" in str(err.value)
    assert p2a_conftest.TEST29_DESELECT in str(err.value)

    # unrelated tests are untouched
    p2a_conftest.pytest_runtest_setup(_Item("test_A1_parameter_map_dimensions"))

    # deliberate opt-in releases the guard
    monkeypatch.setenv(p2a_conftest.TEST29_OPT_IN_ENV, "1")
    assert p2a_conftest.test29_is_allowed() is True
    p2a_conftest.pytest_runtest_setup(_Item(p2a_conftest.TEST29_NAME))


def test_D19_test29_writes_into_the_accepted_attempts_root():
    """Fix A-5: documents WHY the guard exists -- test 29 targets the canonical
    accepted output root, not a temporary one. Read-only: imports the runner
    module and inspects its constant."""
    sys.path.insert(0, str(MNL_ROOT / "scripts" / "p2a"))
    import run_p2a_regionlive_rebuild as runner

    attempts = runner.CANONICAL_PHASE3_ROOT / "attempts"
    assert attempts.is_dir()
    assert "outputs" in str(attempts) and "phase3_estimation_v1" in str(attempts)
    # and the accepted immutable bundle lives beside it, which is what an
    # accidental run puts at risk
    assert (runner.CANONICAL_PHASE3_ROOT / "complete" / "phase3_manifest.json").is_file()


def test_D7_digest_convention_is_load_bearing(pmap, synth_order):
    """FAILURE DEMONSTRATION: the pinned digest constant genuinely pins the
    documented convention. Encoding idhh or the score row big-endian, or
    omitting idhh, yields a different digest -- so a silent drift in the byte
    contract cannot pass test_C3."""
    res = _feed(synth_order, pmap, SYNTH_SCORES, 2)
    assert res.score_stream_sha256 == SYNTH_DIGEST

    def variant(id_fmt, row_dtype, include_id=True):
        h = hashlib.sha256()
        for k in range(6):
            if include_id:
                h.update(struct.pack(id_fmt, int(SYNTH_IDS[k])))
            h.update(np.asarray(SYNTH_SCORES[k], dtype=row_dtype).tobytes())
        return h.hexdigest()

    assert variant(">q", "<f8") != SYNTH_DIGEST          # big-endian idhh
    assert variant("<q", ">f8") != SYNTH_DIGEST          # big-endian scores
    assert variant("<q", "<f8", include_id=False) != SYNTH_DIGEST   # ids dropped
    assert variant("<i", "<f8") != SYNTH_DIGEST          # int32 idhh


def test_D8_stream_emits_nothing_on_stdout_or_stderr(capsys, pmap, synth_order):
    """No score byte reaches a log or a captured stream."""
    _feed(synth_order, pmap, SYNTH_SCORES, 2)
    captured = capsys.readouterr()
    assert captured.out == "" and captured.err == ""


# --------------------------------------------------------------------------- #
# Fix A-1 — recursive exception-object-graph traversal
# --------------------------------------------------------------------------- #
_GRAPH_MAX_NODES = 50_000
_GRAPH_MAX_DEPTH = 12


def _walk_exception_graph(exc, max_nodes=_GRAPH_MAX_NODES, max_depth=_GRAPH_MAX_DEPTH):
    """Yield ``(path, obj)`` for everything reachable from a raised exception.

    Bounded safe traversal, covering exactly the surfaces the review named:

      * the exception object itself and its ``args`` payload;
      * its instance ``__dict__`` (any attribute payload);
      * ``__cause__`` and ``__context__``, recursively as exceptions;
      * every ``__traceback__`` frame and that frame's ``f_locals``;
      * containers (list/tuple/set/dict/ndarray-of-object) and plain-object
        ``__dict__``\\s reachable from any of the above.

    ``frame.f_globals`` and ``frame.f_builtins`` are deliberately NOT traversed.
    They are the module and builtin namespaces, shared by every frame and alive
    regardless of the exception; walking them would report this test module's own
    ``SYNTH_SCORES`` constant as "retained by the exception", which it is not.
    Everything the exception itself keeps alive is covered above.
    """
    seen = set()
    # CRITICAL: hold a strong reference to every visited object. The visited set
    # is keyed by id(), and CPython reuses the id of a freed object. Traversal
    # creates short-lived temporaries (``dict(f_locals)``, ``vars(obj)``); if
    # those were released, a later DISTINCT object could inherit an id already in
    # ``seen`` and be skipped -- silently producing a false green. Keeping every
    # visited object alive makes ids unique for the whole walk, which makes the
    # traversal deterministic and complete.
    keepalive = []
    stack = [("exc", exc, 0)]
    nodes = 0
    while stack and nodes < max_nodes:
        path, obj, depth = stack.pop()
        if obj is None or depth > max_depth:
            continue
        key = id(obj)
        if key in seen:
            continue
        seen.add(key)
        keepalive.append(obj)
        nodes += 1
        yield path, obj

        if isinstance(obj, BaseException):
            stack.append((f"{path}.args", obj.args, depth + 1))
            stack.append((f"{path}.__dict__", vars(obj), depth + 1))
            stack.append((f"{path}.__cause__", obj.__cause__, depth + 1))
            stack.append((f"{path}.__context__", obj.__context__, depth + 1))
            tb, i = obj.__traceback__, 0
            while tb is not None:
                name = tb.tb_frame.f_code.co_name
                stack.append((f"{path}.tb[{i}:{name}].f_locals",
                              dict(tb.tb_frame.f_locals), depth + 1))
                tb = tb.tb_next
                i += 1
            continue
        if isinstance(obj, np.ndarray):
            continue                       # leaf: never recursed into
        if isinstance(obj, dict):
            for k, v in list(obj.items())[:512]:
                stack.append((f"{path}[{k!r}]", v, depth + 1))
            continue
        if isinstance(obj, (list, tuple, set, frozenset)):
            for i, v in enumerate(list(obj)[:512]):
                stack.append((f"{path}[{i}]", v, depth + 1))
            continue
        if isinstance(obj, (str, bytes, bytearray, memoryview, int, float, bool)):
            continue
        payload = getattr(obj, "__dict__", None)
        if isinstance(payload, dict):
            stack.append((f"{path}.__dict__", payload, depth + 1))


def _score_leaks(exc, block, permitted_aggregates=()):
    """Return every path in ``exc``'s object graph that leaks row-level scores.

    A finding is any of:

      1. the supplied ``block`` itself, by identity;
      2. an ndarray sharing memory with ``block``;
      3. an ndarray equal to ``block`` in shape and value;
      4. any 2-D ndarray with ``N_FREE`` columns that is not an addendum s2
         aggregate. The ONLY 37-column 2-D matrix a reducer may legitimately
         hold is the meat ``M_37`` (37x37); ``M_35`` is (35x35) and so never
         matches. The exemption is therefore by exact aggregate shape, plus any
         array the caller names explicitly in ``permitted_aggregates``. It is not
         a hole: a score block that happened to be 37 rows tall is still caught
         by rules 1-3 (identity, shared memory, equality), which test_D20 proves;
      5. raw score bytes carried as ``bytes``/``bytearray``/``memoryview``.
    """
    raw = block.tobytes()
    permitted = {id(a) for a in permitted_aggregates}
    aggregate_shapes = {(sst.N_FREE, sst.N_FREE), (sst.N_INTERIOR, sst.N_INTERIOR)}
    findings = []
    for path, obj in _walk_exception_graph(exc):
        if obj is block:
            findings.append((path, "identity with the supplied score block"))
            continue
        if isinstance(obj, np.ndarray):
            if obj.size and np.shares_memory(obj, block):
                findings.append((path, f"shares memory with the score block {obj.shape}"))
            elif obj.shape == block.shape and obj.dtype == block.dtype \
                    and np.array_equal(obj, block):
                findings.append((path, f"equals the score block {obj.shape}"))
            elif (obj.ndim == 2 and obj.shape[1] == sst.N_FREE
                    and obj.shape not in aggregate_shapes
                    and id(obj) not in permitted):
                findings.append((path, f"unpermitted 2-D {sst.N_FREE}-column array {obj.shape}"))
            continue
        if isinstance(obj, (bytes, bytearray)) and raw in bytes(obj):
            findings.append((path, "raw score bytes"))
        elif isinstance(obj, memoryview) and raw in obj.tobytes():
            findings.append((path, "raw score bytes in a memoryview"))
    return findings


def _capture_update_failure(reducer, batch, block):
    """Call the real reducer, return the caller-visible exception.

    This helper drops its OWN reference to ``block`` before returning, so the
    only thing under test is what the module's failure boundary retains.
    """
    try:
        reducer.update(batch, block)
    except sst.ScoreStreamError as exc:
        del block
        return exc
    raise AssertionError("reducer.update did not raise")


def _capture_stream_failure(binding, batch_size):
    """Run the real stream, return the caller-visible exception.

    Exists so the calling test's frame -- which holds the comparison copy of the
    score block -- is NOT part of the traceback being inspected. This helper
    holds no score reference of its own.
    """
    try:
        sst.run_score_stream(binding, batch_size=batch_size)
    except sst.ScoreStreamError as exc:
        return exc
    raise AssertionError("run_score_stream did not raise")


def _snapshot(root: Path):
    return sorted((str(p.relative_to(root)), p.stat().st_size)
                  for p in root.rglob("*") if p.is_file())


# =========================================================================== #
# E. REAL production-path integration on a bounded household subset
# =========================================================================== #
@pytest.fixture(scope="module")
def binding():
    return sst.build_production_binding(household_limit=SUBSET_HOUSEHOLDS)


@pytest.fixture(scope="module")
def binding64():
    """The frozen design v4 T-11/T-16 slice: the first 64 canonical households."""
    return sst.build_production_binding(household_limit=T16_HOUSEHOLDS)


def _direct_jacrev_reference(binding, mode="jacrev"):
    """Independent reference: ONE ``jax.jac{rev,fwd}`` call per gender over the
    whole subset, assembled with plain numpy. It reuses the same accepted loader
    and the same accepted likelihood -- what it does NOT use is the streaming
    reducer, the canonical iterator, or any batching."""
    import jax
    import jax.numpy as jnp

    from dclaborsupply.data.loader import load_singles
    from dclaborsupply.likelihood.engine_jax import build_jax_singles_ll

    # float64 must already be active before ANY jnp array is created, or this
    # reference silently degrades to float32 (design v4 s3.3). The binding
    # fixture guarantees it eagerly; assert rather than rely on call ordering.
    assert jax.config.read("jax_enable_x64") is True

    ids = np.asarray(binding.order.idhh)
    is_male = np.asarray(binding.order.is_male)
    free_idx = jnp.asarray(binding.pmap.free_index_array)
    base_full = jnp.asarray(binding.base_full)
    assert base_full.dtype == np.float64
    out = np.empty((ids.size, sst.N_FREE), dtype=np.float64)

    for male in (True, False):
        sel = ids[is_male] if male else ids[~is_male]
        frame = binding.male_frame if male else binding.female_frame
        sub = frame[pd.to_numeric(frame["idhh"]).isin({int(v) for v in sel})]
        sub = sub.copy().reset_index(drop=True)
        data = load_singles(sub, binding.spec, is_male=male, metadata=binding.metadata)
        ll_vec, _ = build_jax_singles_ll(data, binding.spec, is_male=male, per_group=True)

        def per_group_free(x, _ll=ll_vec):
            return _ll(base_full.at[free_idx].set(x))

        jac = jax.jacrev(per_group_free) if mode == "jacrev" else jax.jacfwd(per_group_free)
        block = np.asarray(jac(jnp.asarray(binding.x_hat_free)), dtype=np.float64)
        assert np.array_equal(np.asarray(data.group_ids).astype(np.int64), np.sort(sel))
        out[np.flatnonzero(is_male if male else ~is_male)] = block
    return ids, out


@pytest.mark.production
def test_E1_binding_uses_the_accepted_authenticated_sources(binding):
    import jax

    # the binding activates the accepted float64 initialiser EAGERLY, so no
    # downstream consumer can create a float32 array by calling things in the
    # wrong order (design v4 s3.3)
    assert jax.config.read("jax_enable_x64") is True
    assert binding.spec_sha256 == sst.CERTIFIED_SPEC_SHA256
    assert binding.theta_hat_sha256 == sst.ACCEPTED_THETA_SHA256
    assert binding.full_order.n_households == sst.N_HOUSEHOLDS == 1555
    assert binding.order.n_households == SUBSET_HOUSEHOLDS
    assert np.array_equal(binding.order.idhh,
                          binding.full_order.idhh[:SUBSET_HOUSEHOLDS])
    # pins are injected, never differentiated (design v4 s5.1)
    pin_idx = np.asarray(binding.pmap.pin_indices)
    assert np.array_equal(binding.base_full[pin_idx],
                          np.asarray(binding.pmap.pin_values))
    assert np.array_equal(binding.base_full[binding.pmap.free_index_array],
                          np.zeros(sst.N_FREE))


@pytest.mark.production
def test_E2_streamed_aggregates_match_a_direct_jacrev_reference(binding):
    """The headline Increment-A claim, on the REAL production path."""
    res = sst.run_score_stream(binding, batch_size=8)
    ids, ref = _direct_jacrev_reference(binding)
    assert np.array_equal(ids, np.asarray(binding.order.idhh))

    scale = float(np.max(np.abs(ref)))
    assert res.n_households == SUBSET_HOUSEHOLDS
    assert np.max(np.abs(res.score_sum_free37 - ref.sum(axis=0))) \
        <= T16_MODE_AGREEMENT_REL * scale
    assert np.max(np.abs(res.meat_free37 - ref.T @ ref)) \
        <= T16_MODE_AGREEMENT_REL * scale * scale * SUBSET_HOUSEHOLDS
    sel = np.asarray(binding.pmap.interior_positions_in_free)
    ref_i = ref[:, sel]
    assert np.max(np.abs(res.meat_interior35 - ref_i.T @ ref_i)) \
        <= T16_MODE_AGREEMENT_REL * scale * scale * SUBSET_HOUSEHOLDS
    # meat blocks are Gram matrices: symmetric and consistent with one another
    assert res.diagnostics["meat_free37_max_asymmetry"] == 0.0
    assert res.diagnostics["meat_interior35_max_asymmetry"] == 0.0
    assert np.array_equal(res.meat_interior35, res.meat_free37[np.ix_(sel, sel)])


@pytest.mark.production
def test_E3_digest_reproduces_the_direct_reference_bitwise(binding):
    """Same AD mode, same shapes: the streamed digest must equal, BITWISE, a
    digest computed row-by-row from the direct reference matrix."""
    res = sst.run_score_stream(binding, batch_size=SUBSET_HOUSEHOLDS, mode="jacrev")
    ids, ref = _direct_jacrev_reference(binding, mode="jacrev")
    assert res.score_stream_sha256 == _expected_digest(ids, ref)
    assert res.order_sha256 == binding.order.order_sha256
    res_fwd = sst.run_score_stream(binding, batch_size=SUBSET_HOUSEHOLDS)
    ids_f, ref_f = _direct_jacrev_reference(binding, mode="jacfwd")
    assert res_fwd.score_stream_sha256 == _expected_digest(ids_f, ref_f)


@pytest.mark.production
def test_E3b_digest_is_deterministic_at_a_fixed_batch_size(binding):
    """The digest is a function of (subset, mode, batch size). Repeating the
    stream at the same batch size reproduces it bitwise -- the in-process
    precursor of the addendum s4 fresh-process comparison, which likewise pins
    the actual batch size. Across batch sizes only the T-11 bound is claimed
    (test_E4); no batch-size-independent digest claim is made anywhere."""
    a = sst.run_score_stream(binding, batch_size=8)
    b = sst.run_score_stream(binding, batch_size=8)
    assert a.score_stream_sha256 == b.score_stream_sha256
    assert np.array_equal(a.score_sum_free37, b.score_sum_free37)
    assert np.array_equal(a.meat_free37, b.meat_free37)
    assert np.array_equal(a.meat_interior35, b.meat_interior35)
    assert a.batch_size == 8 and a.n_batches == 3


@pytest.mark.production
def test_E4_t11_chunk_route_invariance_first64(binding64):
    """T-11 on the FROZEN design slice: the first 64 canonical households.

    Fix A-3 / review finding T16-1. Design v4 T-11 bounds the chunked-versus-
    reference score deviation by ``1e-12 * max|S|``; the batch tuple compared
    here is (16, 64) over the first 64 canonical households, i.e. four batches
    against one. Mode: ``jacfwd`` (design v4 s5.4 baseline) on both legs.
    """
    blocks = {}
    for bs in (16, 64):
        blocks[bs] = np.vstack([sst.compute_batch_scores(binding64, b)
                                for b in binding64.order.batches(bs)])
    assert blocks[16].shape == (T16_HOUSEHOLDS, sst.N_FREE)
    scale = float(np.max(np.abs(blocks[64])))
    deviation = float(np.max(np.abs(blocks[16] - blocks[64])))
    assert deviation <= T11_CHUNK_INVARIANCE_REL * scale, (
        f"T-11 first-64 batch(16 vs 64) deviation {deviation!r} exceeds bar "
        f"{T11_CHUNK_INVARIANCE_REL * scale!r}")


@pytest.mark.production
def test_E5_t16_forward_reverse_mode_agreement_first64(binding64):
    """T-16 on the FROZEN design slice: the first 64 canonical households.

    Fix A-3 / review finding T16-1. Design v4 T-16: ``on the first 64 households
    in canonical order, max|S_jacfwd - S_jacrev| <= 1e-10 * max|S|``. Forward
    mode is ``jax.jacfwd``, reverse is ``jax.jacrev``, both over the accepted
    per-group likelihood; batch tuple (64, 64), i.e. one batch on each leg so
    the two modes see identical shapes.
    """
    fwd = np.vstack([sst.compute_batch_scores(binding64, b)
                     for b in binding64.order.batches(T16_HOUSEHOLDS)])
    rev = np.vstack([sst.compute_batch_scores(binding64, b, mode="jacrev")
                     for b in binding64.order.batches(T16_HOUSEHOLDS)])
    assert fwd.shape == rev.shape == (T16_HOUSEHOLDS, sst.N_FREE)
    scale = float(np.max(np.abs(fwd)))
    deviation = float(np.max(np.abs(fwd - rev)))
    assert deviation <= T16_MODE_AGREEMENT_REL * scale, (
        f"T-16 first-64 jacfwd-vs-jacrev deviation {deviation!r} exceeds bar "
        f"{T16_MODE_AGREEMENT_REL * scale!r}")


@pytest.mark.production
def test_E4s_smoke_chunk_invariance_24(binding):
    """SMOKE ONLY -- additional chunkings on the 24-household subset.

    Fix A-3: this is NOT T-16 or T-11 evidence. The frozen design slice is the
    first 64 households (test_E4/test_E5); this case exists only because odd
    batch sizes (3, 8, 24) exercise ragged final batches that the 16/64 split
    does not."""
    blocks = {}
    for bs in (3, 8, 24):
        blocks[bs] = np.vstack([sst.compute_batch_scores(binding, b)
                                for b in binding.order.batches(bs)])
    scale = float(np.max(np.abs(blocks[8])))
    for bs in (3, 24):
        assert np.max(np.abs(blocks[bs] - blocks[8])) <= T11_CHUNK_INVARIANCE_REL * scale


@pytest.mark.production
def test_E5s_smoke_mode_agreement_24(binding):
    """SMOKE ONLY -- forward/reverse on the 24-household subset at batch 8.

    Fix A-3: not T-16 evidence; see test_E5 for the frozen first-64 check."""
    fwd = np.vstack([sst.compute_batch_scores(binding, b)
                     for b in binding.order.batches(8)])
    rev = np.vstack([sst.compute_batch_scores(binding, b, mode="jacrev")
                     for b in binding.order.batches(8)])
    scale = float(np.max(np.abs(fwd)))
    assert np.max(np.abs(fwd - rev)) <= T16_MODE_AGREEMENT_REL * scale


@pytest.mark.production
def test_E6_aggregates_are_chunking_stable_within_tolerance(binding):
    ref = sst.run_score_stream(binding, batch_size=24)
    scale = ref.diagnostics["max_abs_score_entry"]
    for bs in (3, 5, 8):
        res = sst.run_score_stream(binding, batch_size=bs)
        assert res.n_households == ref.n_households
        assert res.order_sha256 == ref.order_sha256
        assert np.max(np.abs(res.score_sum_free37 - ref.score_sum_free37)) \
            <= T11_CHUNK_INVARIANCE_REL * scale
        assert np.max(np.abs(res.meat_free37 - ref.meat_free37)) \
            <= T11_CHUNK_INVARIANCE_REL * scale * scale * SUBSET_HOUSEHOLDS
        assert np.max(np.abs(res.meat_interior35 - ref.meat_interior35)) \
            <= T11_CHUNK_INVARIANCE_REL * scale * scale * SUBSET_HOUSEHOLDS


@pytest.mark.production
def test_E7_production_stream_writes_nothing(binding, tmp_path, monkeypatch):
    """T-23S on the REAL path: a production-route stream creates no file."""
    monkeypatch.chdir(tmp_path)
    root = MNL_ROOT / "outputs" / "p2a_singles2016" / "region_live_v1"
    before = _snapshot(root)
    docs = MNL_ROOT / "docs" / "France_case" / "P2a"
    docs_before = _snapshot(docs)
    res = sst.run_score_stream(binding, batch_size=12)
    assert res.n_households == SUBSET_HOUSEHOLDS
    assert list(tmp_path.rglob("*")) == []
    assert _snapshot(root) == before
    assert _snapshot(docs) == docs_before


@pytest.mark.production
def test_E8_subset_size_is_the_only_patched_quantity(binding):
    """A second, differently sized subset must reproduce the first as a prefix."""
    smaller = sst.build_production_binding(household_limit=6)
    assert np.array_equal(smaller.order.idhh, binding.order.idhh[:6])
    assert smaller.spec_sha256 == binding.spec_sha256
    assert smaller.theta_hat_sha256 == binding.theta_hat_sha256
    assert smaller.pmap.free_names_sha256 == binding.pmap.free_names_sha256
    res_small = sst.run_score_stream(smaller, batch_size=6)
    _, ref = _direct_jacrev_reference(binding, mode="jacfwd")
    prefix = ref[:6]
    scale = float(np.max(np.abs(ref)))
    sel = np.asarray(binding.pmap.interior_positions_in_free)
    assert np.max(np.abs(res_small.score_sum_free37 - prefix.sum(axis=0))) \
        <= T11_CHUNK_INVARIANCE_REL * scale
    assert np.max(np.abs(res_small.meat_free37 - prefix.T @ prefix)) \
        <= T11_CHUNK_INVARIANCE_REL * scale * scale * SUBSET_HOUSEHOLDS
    assert np.max(np.abs(res_small.meat_interior35
                         - prefix[:, sel].T @ prefix[:, sel])) \
        <= T11_CHUNK_INVARIANCE_REL * scale * scale * SUBSET_HOUSEHOLDS


@pytest.mark.production
def test_E9_household_limit_is_validated():
    with pytest.raises(sst.ScoreStreamError, match="household_limit"):
        sst.build_production_binding(household_limit=0)
    with pytest.raises(sst.ScoreStreamError, match="household_limit"):
        sst.build_production_binding(household_limit=sst.N_HOUSEHOLDS + 1)


@pytest.mark.production
def test_E11_a_mutated_evaluator_would_be_caught(binding, monkeypatch):
    """FAILURE DEMONSTRATION: test_E2 is not vacuous.

    Perturb the batch evaluator by a single ULP-scale constant and show that the
    E2 comparison against the direct reference then EXCEEDS its tolerance. The
    shipped module is untouched: the perturbation lives only in this test's
    monkeypatch scope."""
    _, ref = _direct_jacrev_reference(binding)
    scale = float(np.max(np.abs(ref)))
    clean = sst.run_score_stream(binding, batch_size=8)
    assert np.max(np.abs(clean.score_sum_free37 - ref.sum(axis=0))) \
        <= T16_MODE_AGREEMENT_REL * scale

    original = sst._gender_score_block

    def perturbed(*args, **kwargs):
        block = original(*args, **kwargs)
        if block.size:
            block = block.copy()
            block[0, 0] += 1e-6
        return block

    monkeypatch.setattr(sst, "_gender_score_block", perturbed)
    mutated = sst.run_score_stream(binding, batch_size=8)
    assert np.max(np.abs(mutated.score_sum_free37 - ref.sum(axis=0))) \
        > T16_MODE_AGREEMENT_REL * scale
    assert mutated.score_stream_sha256 != clean.score_stream_sha256


@pytest.mark.production
def test_E12_float64_is_active_and_enforced_on_the_route(binding, monkeypatch):
    """The accepted route runs in float64 (design v4 s3.3, T-15 precursor), and
    the module REJECTS a non-float64 derivative rather than upcasting it.

    FAILURE DEMONSTRATION: patching jax.jacfwd to return a float32 jacobian must
    raise, not silently produce a float64-looking block."""
    import jax

    batch = next(iter(binding.order.batches(4)))
    block = sst.compute_batch_scores(binding, batch)
    assert jax.config.read("jax_enable_x64") is True
    assert block.dtype == np.float64

    real_jacfwd = jax.jacfwd

    def downcasting_jacfwd(fun):
        inner = real_jacfwd(fun)
        return lambda x: inner(x).astype("float32")

    monkeypatch.setattr(jax, "jacfwd", downcasting_jacfwd)
    with pytest.raises(sst.ScoreStreamError, match="!= float64"):
        sst.compute_batch_scores(binding, batch)


@pytest.mark.production
def test_E13_stream_failure_graph_holds_no_score(binding, monkeypatch):
    """Fix A-1 on the REAL path: `run_score_stream` holds the live ``block``.

    Fault injection only -- the real loader, the real likelihood and the real
    `ScoreStreamReducer` all run; a single NaN is written into one genuinely
    computed score block so the reducer rejects it. This is the scenario where
    `run_score_stream`'s own frame is holding a real ``(batch, 37)`` array at the
    moment the exception is raised."""
    real = sst._compute_batch_scores
    captured = {}

    def nan_injecting(binding_, batch_, mode_):
        block = real(binding_, batch_, mode_)
        captured["block"] = block.copy()
        block[0, 0] = np.nan
        return block

    monkeypatch.setattr(sst, "_compute_batch_scores", nan_injecting)
    # captured in a helper so THIS frame -- which holds the comparison copy in
    # `captured` -- is not itself part of the traceback under inspection
    exc = _capture_stream_failure(binding, 8)

    assert exc.code == "SS-NONFINITE"
    assert exc.__cause__ is None and exc.__context__ is None
    probe = captured["block"]
    assert probe.shape == (8, sst.N_FREE)
    leaks = _score_leaks(exc, probe)
    assert leaks == [], f"score data reachable from the stream exception: {leaks}"
    assert "nan" not in str(exc).lower()


@pytest.mark.production
def test_E10_corrupted_production_slice_is_detected(binding):
    """FAILURE DEMONSTRATION on the real path: a batch naming a household that
    is not in this gender's frame cannot silently produce a short block."""
    batch = next(iter(binding.order.batches(4)))
    bogus = sst.HouseholdBatch(
        position=0,
        idhh=np.array([-1, -2, -3, -4], dtype=np.int64),
        is_male=batch.is_male.copy())
    with pytest.raises(sst.ScoreStreamError, match="household slice has"):
        sst.compute_batch_scores(binding, bogus)
