import heapq
import random
import time
from dataclasses import dataclass, field


@dataclass(frozen=True)
class GridConfig:
    size: int
    obstacle_ratio: float
    seed: int
    start: tuple[int, int] = field(init=False)
    goal: tuple[int, int] = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "start", (0, 0))
        object.__setattr__(self, "goal", (self.size - 1, self.size - 1))
        if self.size < 10 or self.size > 5000:
            raise ValueError("size must be between 10 and 5000")
        if not 0.0 <= self.obstacle_ratio < 0.5:
            raise ValueError("obstacle_ratio must be between 0.0 and 0.5")


@dataclass
class ObstacleStore:
    cells: set[tuple[int, int]]

    @classmethod
    def from_config(cls, config: GridConfig) -> "ObstacleStore":
        rng = random.Random(config.seed)
        num_obstacles = int(config.size * config.size * config.obstacle_ratio)
        obstacles: set[tuple[int, int]] = set()

        while len(obstacles) < num_obstacles:
            x = rng.randint(0, config.size - 1)
            y = rng.randint(0, config.size - 1)
            if (x, y) != config.start and (x, y) != config.goal:
                obstacles.add((x, y))

        return cls(obstacles)


def to_native_args(
    config: GridConfig, obstacles: ObstacleStore
) -> tuple[int, float, int, list[tuple[int, int]]]:
    return (
        config.size,
        config.obstacle_ratio,
        config.seed,
        list(obstacles.cells),
    )


class AStarPathfinder:
    def __init__(self, size, obstacle_ratio, seed):
        self.config = GridConfig(size=size, obstacle_ratio=obstacle_ratio, seed=seed)
        self.size = self.config.size
        self.seed = self.config.seed
        self.start = self.config.start
        self.goal = self.config.goal
        self.obstacles = ObstacleStore(set())
        self._generate_grid()

    def _generate_grid(self) -> None:
        """障害物をランダムに生成"""
        num_obstacles = int(
            self.size * self.size * self.config.obstacle_ratio
        )

        print(
            f"[*] グリッド生成中... ({self.size}x{self.size}, "
            f"障害物: {num_obstacles}個)"
        )

        self.obstacles = ObstacleStore.from_config(self.config)

    def heuristic(self, a, b):
        """マンハッタン距離"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_neighbors(self, node):
        """上下左右の移動（範囲内かつ障害物なし）"""
        x, y = node
        candidates = [
            (x + 1, y), (x - 1, y),
            (x, y + 1), (x, y - 1)
        ]
        results = []
        for nx, ny in candidates:
            if 0 <= nx < self.size and 0 <= ny < self.size:
                if (nx, ny) not in self.obstacles.cells:
                    results.append((nx, ny))
        return results

    def find_path(self):
        """A* アルゴリズムの実行"""
        start_time = time.time()
        
        open_set = []
        heapq.heappush(open_set, (0, self.start))
        
        came_from = {}
        g_score = {self.start: 0}
        f_score = {self.start: self.heuristic(self.start, self.goal)}
        
        nodes_evaluated = 0

        print("[*] 経路探索開始...")

        while open_set:
            _, current = heapq.heappop(open_set)
            nodes_evaluated += 1

            if current == self.goal:
                end_time = time.time()
                return self._reconstruct_path(came_from, current), end_time - start_time, nodes_evaluated

            for neighbor in self.get_neighbors(current):
                tentative_g_score = g_score[current] + 1

                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f = tentative_g_score + self.heuristic(neighbor, self.goal)
                    f_score[neighbor] = f
                    heapq.heappush(open_set, (f, neighbor))

        return None, time.time() - start_time, nodes_evaluated

    def _reconstruct_path(self, came_from, current):
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
        return total_path[::-1]

    def to_native_args(self) -> tuple[int, float, int, list[tuple[int, int]]]:
        return to_native_args(self.config, self.obstacles)

