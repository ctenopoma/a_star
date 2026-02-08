# Feature Specification: 実行時間調査レポート

**Feature Branch**: `1-runtime-profiling-report`  
**Created**: 2026-02-08  
**Status**: Draft  
**Input**: User description: "viztracerでmain.pyの実行時間調査。Pythonが原因で処理に時間がかかっている部分を抽出し、処理高速化のためにRust化する部分を考察してレポートを保存する。今回は実装作業は発生させない。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 実行時間の可視化とボトルネック抽出 (Priority: P1)

開発者として、main.pyの実行時間を可視化し、Python由来のボトルネックを特定して、Rust化候補を整理したレポートを保存したい。

**Why this priority**: 性能改善の次の意思決定に必要な一次情報を得るため。

**Independent Test**: 代表的な実行を計測し、レポートに主要ホットスポットとRust化候補が含まれることを確認できる。

**Acceptance Scenarios**:

1. **Given** main.pyが代表的な入力で実行可能、**When** 実行時間の計測を行う、**Then** 実行時間の内訳と主要ホットスポットがレポートに記載される
2. **Given** 計測結果が得られている、**When** Python由来の高負荷箇所を分析する、**Then** Rust化候補が理由付きでレポートに整理される

---

### User Story 2 - レポートのレビューによる意思決定 (Priority: P2)

ステークホルダーとして、レポートを読んでどこをRust化すべきかの方針を決めたい。

**Why this priority**: 調査結果が意思決定に直結するため。

**Independent Test**: レポートのみを読んで、優先順位付けと次のアクションが決められる。

**Acceptance Scenarios**:

1. **Given** レポートが保存されている、**When** ステークホルダーがレビューする、**Then** 主要ボトルネックと推奨アクションが明確に把握できる

---

### Edge Cases

- main.pyが例外終了する場合でも、原因と再実行条件がレポートに明記される
- 計測対象が想定より長時間の場合でも、部分結果の有無と欠落範囲がレポートに明記される
- 計測結果がばらつく場合、再計測の有無と平均/代表値の扱いがレポートに記載される

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 計測はmain.pyの代表的な実行全体を対象とし、関数単位の実行時間と呼び出し関係を取得できること
- **FR-002**: Python由来のボトルネックを特定し、各項目の実行時間と割合がレポートに含まれること
- **FR-003**: Rust化候補を複数列挙し、各候補の理由と期待される効果がレポートに含まれること
- **FR-004**: レポートはリポジトリ内に保存され、再確認できる形式であること
- **FR-005**: 計測時の前提（入力条件、実行環境の前提、再現手順）がレポートに記載されること
- **FR-006**: 本タスクは分析のみとし、性能改善の実装変更は行わないこと

### Key Entities *(include if feature involves data)*

- **Profiling Run**: 計測対象、入力条件、実行日時、前提条件の集合
- **Hotspot**: 高負荷な関数/処理単位と、その実行時間・割合
- **Recommendation**: Rust化候補、理由、期待される影響の記述

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: レポートがリポジトリ内の合意された場所に1件以上保存されている
- **SC-002**: レポートに上位5件以上のホットスポットが時間割合付きで記載されている
- **SC-003**: Rust化候補が3件以上、理由とともに記載されている
- **SC-004**: ホットスポットの合計時間割合が全体の90%以上をカバーしている

## Assumptions

- main.pyは代表的な入力で再現可能に実行できる
- 実行時間の可視化には、関数単位の時間を取得できるトレース手段を用いる
- 既定の計測ツールが利用不可の場合は、代替手段と影響をレポートに記載する

## Out of Scope

- Rust実装や最適化コードの作成
- 本番データ全量での再計測や長期的なベンチマーク
