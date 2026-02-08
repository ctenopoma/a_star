import pytest

import a_star
from a_star import AStarPathfinder, native_available
from a_star.pure_python import AStarPathfinder as PurePythonAStarPathfinder


def test_native_missing_falls_back(monkeypatch) -> None:
    def _raise_import(_name: str):
        raise ImportError("native module not available")

    monkeypatch.setattr(a_star, "import_module", _raise_import)
    assert a_star._load_native() is None

    finder = PurePythonAStarPathfinder(10, 0.0, 1)
    path, duration, nodes = finder.find_path()

    assert path is not None
    assert duration >= 0.0
    assert nodes > 0


def test_native_parity_small_grid() -> None:
    if not native_available():
        pytest.skip("native module not available")

    size = 40
    ratio = 0.1
    seed = 42

    python_finder = PurePythonAStarPathfinder(size, ratio, seed)
    py_path, py_duration, py_nodes = python_finder.find_path()

    native_finder = AStarPathfinder(size, ratio, seed)
    native_path, native_duration, native_nodes = native_finder.find_path()

    assert native_path == py_path
    assert abs(native_nodes - py_nodes) <= max(1, int(py_nodes * 0.01))
    if py_duration > 0.1:
        duration_tolerance = py_duration * 0.2
        assert abs(native_duration - py_duration) <= duration_tolerance


def test_native_telemetry_resets_per_run() -> None:
    if not native_available():
        pytest.skip("native module not available")

    size = 30
    ratio = 0.1
    seed = 7

    finder = AStarPathfinder(size, ratio, seed)
    finder.find_path()
    telemetry_first = finder.telemetry

    assert telemetry_first is not None
    assert telemetry_first.nodes_evaluated > 0
    assert telemetry_first.heap_pushes >= telemetry_first.nodes_evaluated
    assert telemetry_first.heap_pops >= telemetry_first.nodes_evaluated

    finder.find_path()
    telemetry_second = finder.telemetry

    assert telemetry_second is not None
    assert telemetry_second.nodes_evaluated == telemetry_first.nodes_evaluated
