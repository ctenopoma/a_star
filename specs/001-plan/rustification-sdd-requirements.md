# Rust化 SDD 要件まとめ

- `AStarPathfinder.find_path()` のコアループを Rust/PyO3 で再実装し、open set 管理や `came_from`/`g_score`/`f_score` の更新、経路復元の振る舞いを Python 実装と一致させる。プロファイリングで総時間の 31% を占める最優先ホットスポットのため、SDD ではループ構造と状態遷移を詳細化する。[specs/001-plan/runtime-profiling-report.md#L27-L39](specs/001-plan/runtime-profiling-report.md#L27-L39) / [a_star/pure_python.py#L47-L88](a_star/pure_python.py#L47-L88)
- Python 公開 API (`main.py` からの呼び出し) と互換性を維持し、`(path, duration, nodes_evaluated)` を返す挙動と 3000x3000/障害物 10%/seed 42 の代表入力を前提に設計する。[main.py#L6-L24](main.py#L6-L24)
- 優先度キュー操作 (`heapq.heappop/push`) を Rust 側 (例: `std::collections::BinaryHeap`) で完結させ、ヒープ要素構造体と PyO3 連携を定義する。ホットスポット上位にあり Rust 化候補として指名済み。[specs/001-plan/runtime-profiling-report.md#L29-L39](specs/001-plan/runtime-profiling-report.md#L29-L39)
- 近傍展開ロジック（上下左右探索＋障害物除外）も Rust に移し、高頻度呼び出しの Python オーバーヘッドを排除する。障害物集合の保持形式（ハッシュセットやビットセット）と PyO3 経由の初期化契約を明記する。[specs/001-plan/runtime-profiling-report.md#L28-L39](specs/001-plan/runtime-profiling-report.md#L28-L39) / [a_star/pure_python.py#L33-L45](a_star/pure_python.py#L33-L45)
- Rust 化後の再計測で viztracer のバッファ溢れを防ぐため、SDD に計測手順（`--tracer_entries` 拡大/フィルタ）と Rust 内部の観測ポイント（ノード展開数、ヒープ操作回数など）を盛り込み、改善評価が容易な観測性を確保する。[specs/001-plan/runtime-profiling-report.md#L6-L59](specs/001-plan/runtime-profiling-report.md#L6-L59)
