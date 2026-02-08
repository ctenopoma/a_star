use std::cmp::Reverse;
use std::collections::{BinaryHeap, HashMap, HashSet};
use std::time::Instant;

use pyo3::{exceptions::PyValueError, prelude::*, wrap_pyfunction};

#[derive(Clone)]
struct GridConfig {
    size: i32,
    obstacle_ratio: f64,
    seed: i64,
    start: (i32, i32),
    goal: (i32, i32),
}

impl GridConfig {
    fn new(size: i32, obstacle_ratio: f64, seed: i64) -> PyResult<Self> {
        if size < 10 || size > 5000 {
            return Err(PyValueError::new_err("size must be between 10 and 5000"));
        }
        if !(0.0..0.5).contains(&obstacle_ratio) {
            return Err(PyValueError::new_err(
                "obstacle_ratio must be between 0.0 and 0.5",
            ));
        }

        Ok(Self {
            size,
            obstacle_ratio,
            seed,
            start: (0, 0),
            goal: (size - 1, size - 1),
        })
    }

    fn expected_obstacle_count(&self) -> usize {
        let area = (self.size as i64 * self.size as i64) as f64;
        (area * self.obstacle_ratio).floor() as usize
    }
}

struct ObstacleStore {
    cells: HashSet<(i32, i32)>,
}

impl ObstacleStore {
    fn from_obstacles(config: &GridConfig, obstacles: Vec<(i32, i32)>) -> PyResult<Self> {
        let expected = config.expected_obstacle_count();
        if obstacles.len() != expected {
            return Err(PyValueError::new_err(format!(
                "obstacles length {len} does not match expected {expected}",
                len = obstacles.len()
            )));
        }

        let mut cells = HashSet::with_capacity(obstacles.len());
        for (x, y) in obstacles {
            if x < 0 || x >= config.size || y < 0 || y >= config.size {
                return Err(PyValueError::new_err("obstacle coordinate out of bounds"));
            }
            if (x, y) == config.start || (x, y) == config.goal {
                return Err(PyValueError::new_err("obstacles cannot include start/goal"));
            }
            if !cells.insert((x, y)) {
                return Err(PyValueError::new_err("duplicate obstacle coordinate"));
            }
        }

        Ok(Self { cells })
    }
}

fn heuristic(a: (i32, i32), b: (i32, i32)) -> i32 {
    (a.0 - b.0).abs() + (a.1 - b.1).abs()
}

fn reconstruct_path(
    came_from: &HashMap<(i32, i32), (i32, i32)>,
    mut current: (i32, i32),
) -> Vec<(i32, i32)> {
    let mut total_path = vec![current];
    while let Some(prev) = came_from.get(&current) {
        current = *prev;
        total_path.push(current);
    }
    total_path.reverse();
    total_path
}

fn find_path_core(
    config: &GridConfig,
    obstacles: &ObstacleStore,
) -> (Option<Vec<(i32, i32)>>, f64, u64, SearchTelemetry) {
    let start_time = Instant::now();
    let mut open_set: BinaryHeap<Reverse<(i32, i32, i32)>> = BinaryHeap::new();
    let mut came_from: HashMap<(i32, i32), (i32, i32)> = HashMap::new();
    let mut g_score: HashMap<(i32, i32), i32> = HashMap::new();
    let mut nodes_evaluated: u64 = 0;
    let mut heap_pushes: u64 = 0;
    let mut heap_pops: u64 = 0;
    let mut neighbors_checked: u64 = 0;

    open_set.push(Reverse((0, config.start.0, config.start.1)));
    heap_pushes += 1;
    g_score.insert(config.start, 0);

    while let Some(Reverse((_f, x, y))) = open_set.pop() {
        let current = (x, y);
        heap_pops += 1;
        nodes_evaluated += 1;

        if current == config.goal {
            let path = reconstruct_path(&came_from, current);
            let duration = start_time.elapsed().as_secs_f64();
            let telemetry = SearchTelemetry {
                duration,
                nodes_evaluated,
                heap_pushes,
                heap_pops,
                neighbors_checked,
            };
            return (Some(path), duration, nodes_evaluated, telemetry);
        }

        let current_g = *g_score.get(&current).unwrap_or(&i32::MAX);
        for (dx, dy) in [(1, 0), (-1, 0), (0, 1), (0, -1)] {
            let nx = current.0 + dx;
            let ny = current.1 + dy;
            if nx < 0 || ny < 0 || nx >= config.size || ny >= config.size {
                continue;
            }
            neighbors_checked += 1;
            if obstacles.cells.contains(&(nx, ny)) {
                continue;
            }

            let neighbor = (nx, ny);
            let tentative_g = current_g + 1;
            if tentative_g < *g_score.get(&neighbor).unwrap_or(&i32::MAX) {
                came_from.insert(neighbor, current);
                g_score.insert(neighbor, tentative_g);
                let f = tentative_g + heuristic(neighbor, config.goal);
                open_set.push(Reverse((f, neighbor.0, neighbor.1)));
                heap_pushes += 1;
            }
        }
    }

    let duration = start_time.elapsed().as_secs_f64();
    let telemetry = SearchTelemetry {
        duration,
        nodes_evaluated,
        heap_pushes,
        heap_pops,
        neighbors_checked,
    };
    (
        None,
        duration,
        nodes_evaluated,
        telemetry,
    )
}

#[pyclass]
#[derive(Clone)]
struct SearchTelemetry {
    #[pyo3(get)]
    duration: f64,
    #[pyo3(get)]
    nodes_evaluated: u64,
    #[pyo3(get)]
    heap_pushes: u64,
    #[pyo3(get)]
    heap_pops: u64,
    #[pyo3(get)]
    neighbors_checked: u64,
}

#[pymethods]
impl SearchTelemetry {
    #[new]
    fn new() -> Self {
        Self {
            duration: 0.0,
            nodes_evaluated: 0,
            heap_pushes: 0,
            heap_pops: 0,
            neighbors_checked: 0,
        }
    }
}

#[pyclass]
struct RustPathfinder {
    config: GridConfig,
    obstacles: ObstacleStore,
}

#[pymethods]
impl RustPathfinder {
    #[new]
    fn new(
        size: i32,
        obstacle_ratio: f64,
        seed: i64,
        obstacles: Option<Vec<(i32, i32)>>,
    ) -> PyResult<Self> {
        let config = GridConfig::new(size, obstacle_ratio, seed)?;
        let store = ObstacleStore::from_obstacles(&config, obstacles.unwrap_or_default())?;
        Ok(Self {
            config,
            obstacles: store,
        })
    }

    fn find_path(
        &self,
        py: Python<'_>,
    ) -> PyResult<(Option<Vec<(i32, i32)>>, f64, u64, SearchTelemetry)> {
        let result = py.allow_threads(|| find_path_core(&self.config, &self.obstacles));
        Ok(result)
    }
}

#[pyfunction]
fn validate_name(name: String) -> PyResult<String> {
    if name.trim().is_empty() {
        Err(PyValueError::new_err("name must not be empty"))
    } else {
        Ok(name)
    }
}

#[pyfunction]
fn native_find_path(
    py: Python<'_>,
    size: i32,
    obstacle_ratio: f64,
    seed: i64,
    obstacles: Option<Vec<(i32, i32)>>,
) -> PyResult<(Option<Vec<(i32, i32)>>, f64, u64, SearchTelemetry)> {
    let config = GridConfig::new(size, obstacle_ratio, seed)?;
    let store = ObstacleStore::from_obstacles(&config, obstacles.unwrap_or_default())?;
    let result = py.allow_threads(|| find_path_core(&config, &store));
    Ok(result)
}

#[pymodule]
fn _native(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<RustPathfinder>()?;
    m.add_class::<SearchTelemetry>()?;
    m.add_function(wrap_pyfunction!(native_find_path, m)?)?;
    m.add_function(wrap_pyfunction!(validate_name, m)?)?;
    Ok(())
}
