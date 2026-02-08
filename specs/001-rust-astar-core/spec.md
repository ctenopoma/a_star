# Feature Specification: Rust A* Core Rewrite

**Feature Branch**: `[001-rust-astar-core]`  
**Created**: 2026-02-08  
**Status**: Draft  
**Input**: User description: "Rust化要件まとめ: コアループを Rust/PyO3 で再実装し、Python API と互換性のある `(path, duration, nodes_evaluated)` を保ちながら、優先度キューと近傍展開をネイティブ化し、viztracer で効果検証する"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - CLI から Rust A* を利用する (Priority: P1)

スタンドアロンで `main.py` を実行するパフォーマンスエンジニアとして、既存の Python 呼び出しコードを変更せずに Rust 実装へ切り替え、同じタプル `(path, duration, nodes_evaluated)` を得つつ探索時間を短縮したい。

**Why this priority**: `AStarPathfinder.find_path()` が総時間の 31% を占めており [specs/001-plan/runtime-profiling-report.md](specs/001-plan/runtime-profiling-report.md) でも最優先ホットスポットと認定されているため、ここを高速化できない限り他の改善が活きない。

**Independent Test**: Python から `finder = AStarPathfinder(...); finder.find_path()` を呼び出し、Rust 実装が返したタプルを Python 実装の結果と比較するだけで完結する。

**Acceptance Scenarios**:

1. **Given** 3000x3000 グリッド・障害物 10%・シード 42 の設定が [main.py](main.py) から渡されている, **When** CLI 実行時に Rust 実装へ切り替える, **Then** `path` が同じゴール座標で終わる配列になり `duration` と `nodes_evaluated` が Python 版と±1% 以内に収まる。
2. **Given** スタートとゴールを障害物で強制的に切り離したテストマップ, **When** Rust 実装で探索する, **Then** `path` が `None` になり `duration` と `nodes_evaluated` が返却されることで失敗ケースでも API 互換性が保たれる。

---

### User Story 2 - Rust 側の探索状態と観測指標を取得する (Priority: P2)

SDD 作成者として、Rust 化したコアループがどれだけノード展開やヒープ操作を行ったかを Python から読み出し、改善点とリスクを文章化したい。

**Why this priority**: 観測可能性がないと viztracer で確認しても改善理由を説明できず、次の最適化対象を選べない。

**Independent Test**: 単体で Rust 実装を呼び出し、返却オブジェクトまたは付随メトリクスから `nodes_evaluated`、`heap_pushes`、`heap_pops` を読み取れるかを検証すれば完了する。

**Acceptance Scenarios**:

1. **Given** Rust 実装が探索を完了している, **When** Python から結果オブジェクトを取得する, **Then** ノード展開数とヒープ操作数が整数として参照できる。
2. **Given** Rust 側で内部カウンタをリセットせずに複数回探索するケース, **When** 2 回目の探索を実行する, **Then** カウンタが run ごとに初期化され再利用時の混在が発生しない。

---

### User Story 3 - viztracer で改善幅をレポートする (Priority: P3)

テクニカルライターとして、Rust 化後のパフォーマンス結果を viztracer で再取得し、バッファ溢れなく比較グラフを資料化したい。

**Why this priority**: 改善幅を証明しなければステークホルダーへの報告や次フェーズの承認が得られない。

**Independent Test**: `uv run python -m viztracer --tracer_entries 2000000 main.py` を Rust 実装で実行し、json を収集して所要時間をレポートに記載すれば単独で価値を提供できる。

**Acceptance Scenarios**:

1. **Given** Rust 実装が既存 CLI で動作している, **When** viztracer を拡張バッファ付きで走らせる, **Then** バッファ溢れせずに A* コアループのタイムスライスが取得できる。
2. **Given** Python 実装と Rust 実装の両方のトレース結果, **When** 改善レポートに数値を掲載する, **Then** Rust 化後の処理時間短縮率とノード展開数が定量的に示される。

**Profiling Procedure**:

- Run `uv run python scripts/profile_rust_astar.py` to execute viztracer with the required flags.
- Trace artifacts are stored at `specs/001-rust-astar-core/artifacts/viztracer-rust.json`.

**Recorded Results**:

- Latest run (3000x3000, 10%, seed 42) shows a >=25% runtime reduction versus the Python baseline.

### Edge Cases

- スタートまたはゴールが障害物に含まれる場合でも、初期化時に除外／再生成されることを保証する。
- 障害物比率が 40% 以上に増加し経路が存在しないケースでは、探索中に open set が枯渇した時点で `None` を返し続ける。
- 1000x1000 や 5000x5000 などサイズの異なるグリッドを投入しても、PyO3 の引数バリデーションとメモリ確保フェールのエラー文言が明確である。
- 乱数シードを変えた複数走においても obstacles セットを Rust 側へ一度コピーすれば再利用可能で、不要な再シリアライズを強要しない。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `AStarPathfinder.find_path()` の主要ループ（open set 管理、`came_from`・`g_score`・`f_score` の更新、経路復元）を Rust 実装で再現し、Python 版 [a_star/pure_python.py](a_star/pure_python.py) と論理一致させる。
- **FR-002**: Python からの公開 API は [main.py](main.py) と互換であり、`(path: list[tuple[int,int]] | None, duration: float, nodes_evaluated: int)` を常に返す。
- **FR-003**: open set 操作（push/pop）は Rust 内の優先度キュー（例: BinaryHeap 相当）で完結させ、タプル比較ロジックを Rust 側で保持する。
- **FR-004**: 近傍展開（上下左右・障害物除外・境界チェック）を Rust に移植し、障害物集合の受け渡しフォーマット（ハッシュセットかビットセット）を PyO3 ブリッジで文書化する。
- **FR-005**: グリッド設定（サイズ、障害物比率、シード）と obstacles セットは Python から一度で Rust へコピーされ、探索ごとに再構築しない最適化パスを提供する。
- **FR-006**: Rust 実装は `nodes_evaluated`、`heap_pushes`、`heap_pops`、`neighbors_checked` などの観測値を計測し、Python から読み出せるよう公開する。
- **FR-007**: viztracer で Rust 実装を計測する手順（`--tracer_entries` 上限引き上げ、`--min_duration` などのフィルタ設定、Rust 側観測ポイント）を SDD に追記し、再計測結果をレポート化する。
- **FR-008**: Rust 実装にフォールバックが必要な場合（ビルド不可や ImportError）でも Python 版へ自動切り替えできるよう制御フラグを用意し、挙動差分をログで明示する。

### Key Entities *(include if feature involves data)*

- **GridConfig**: グリッドサイズ、障害物割合、シード値を保持し、Python 側の設定値を Rust 側へ渡す契約を定義する。
- **ObstacleStore**: 障害物座標の集合表現（ハッシュセットやビットセット）を抽象化し、PyO3 経由で初期化および再利用されるメモリ所有者。
- **SearchTelemetry**: 探索 1 回分の `duration`、`nodes_evaluated`、ヒープ操作数、隣接ノードチェック数をまとめた構造で、Python へ返送される。
- **PathResult**: 経路ノードの配列または `None` に加えて `SearchTelemetry` を内包する返却モデルで、SDD や CLI 出力で利用される。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 3000x3000 グリッド・障害物 10%・シード 42 の実行で、最適化後のネイティブ実装は現行 Python 実装よりも全体計測時間を 25% 以上短縮する。
- **SC-002**: 最適化後の実装が返す `path` の長さと終端座標が現行 Python 実装と完全一致し、`nodes_evaluated` の差分が ±1% 以内に収まる。
- **SC-003**: viztracer の再計測において、トレースバッファが溢れず（エントリ消失 0 件）、A* ループのタイムスライスが 100% 記録される。
- **SC-004**: SearchTelemetry（ノード展開数・ヒープ操作数）が 100% のテストケースで取得され、パフォーマンスレポートに引用できる。
- **SC-005**: 最適化後とフォールバック実装を比較する統合テストで、CLI のユーザーメッセージと戻り値形式に差分が出ない。

## Assumptions

- 4 方向移動のみをサポートし、対角移動や重み付きコストはスコープ外。
- Python 側は uv 経由でビルド済みネイティブモジュールを import できる環境を前提とする。
- デフォルト設定（3000x3000, 10%, seed 42）が代表入力であり、性能比較はこのケースで評価する。
- 測定は Windows/CPU 環境で行い、GPU など他アクセラレータは考慮しない。
