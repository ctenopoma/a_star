import sys

from a_star.pure_python import AStarPathfinder

# --- 設定 ---
GRID_SIZE = 3000      # グリッドのサイズ (3,000x3,000 = 900万ノード)
OBSTACLE_RATIO = 0.1  # 障害物の割合 (10%)
SEED = 42             # 毎回同じマップを生成するためのシード値

if __name__ == "__main__":
    # 再帰制限の緩和
    sys.setrecursionlimit(20000)

    # 初期化
    finder = AStarPathfinder(GRID_SIZE, OBSTACLE_RATIO, SEED)
    
    # 実行と計測
    path, duration, nodes = finder.find_path()

    # 結果出力
    print("-" * 30)
    if path:
        print(f"✅ 経路発見成功")
        print(f"   - 経路長: {len(path)} ステップ")
    else:
        print(f"❌ 経路なし（ブロックされています）")

    print(f"   - 探索ノード数: {nodes:,} 個")
    print(f"   - 実行時間: {duration:.4f} 秒")
    print("-" * 30)
