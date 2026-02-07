import heapq
import random
import time
import sys


class AStarPathfinder:
    def __init__(self, size, obstacle_ratio, seed):
        self.size = size
        self.seed = seed
        self.obstacles = set()
        self.start = (0, 0)
        self.goal = (size - 1, size - 1)
        self._generate_grid(obstacle_ratio)

    def _generate_grid(self, ratio):
        """障害物をランダムに生成"""
        random.seed(self.seed)
        num_obstacles = int(self.size * self.size * ratio)
        
        print(f"[*] グリッド生成中... ({self.size}x{self.size}, 障害物: {num_obstacles}個)")
        
        while len(self.obstacles) < num_obstacles:
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
            # スタートとゴールは埋めない
            if (x, y) != self.start and (x, y) != self.goal:
                self.obstacles.add((x, y))

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
                if (nx, ny) not in self.obstacles:
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

