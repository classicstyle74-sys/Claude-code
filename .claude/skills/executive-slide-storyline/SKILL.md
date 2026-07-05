---
name: executive-slide-storyline
description: >-
  ラグジュアリーブランドのリテール実績・KPI分析・顧客分析・店舗課題・アクションプランなどの素材を、
  経営層・店長会・HQ・百貨店などのオーディエンスに合わせて「伝わるスライドストーリー」へ変換する会話型スキル。
  売上レビュー、月次/半期レビュー、店長会資料、HQ報告、社長向け報告、ハイスペンダー分析、
  New/Loyal/Lost顧客分析、外商強化、RTW比率改善、DSRベースの店舗アクション等の資料化に使用する。
  Use when the user wants to turn retail performance data, KPI analysis, customer insights,
  or store issues into a persuasive slide storyline tailored to a specific audience
  (executives, store manager meetings, HQ, department store partners, or store staff).
---

# Executive Slide Storyline Skill

ラグジュアリーリテールの分析素材・ラフメモを、オーディエンスに合わせた
「伝わるスライドストーリー」へ変換する会話型スキル。

いきなり完成版のスライド構成を出さず、必ず
**「受け取る → 整理する → オーディエンス確認 → 構成作成」** の順で進める。

## When to use

以下のような依頼を受けたときにこのスキルを使う。

- 売上レビュー / 月次レビュー / 半期レビューの資料化
- 店長会資料、HQ報告、社長・経営層向け報告
- ハイスペンダー分析、New / Loyal / Lost顧客分析の資料化
- 外商ビジネス強化、百貨店連携の提案資料
- RTW比率改善、UPT / ATV / AP改善のストーリー化
- DSRに基づく店舗アクション、店舗別課題整理、店長向けアクションプラン
- ミステリーショッピング結果の資料化

素材が箇条書き・未整理メモ・Excel分析結果の貼り付けなど粗い状態でもよい。
むしろ粗い素材を整理して資料化するのがこのスキルの役割。

## Workflow（必ずこの順番で進める）

```
1. ユーザーのラフな内容を受け取る（Step 1）
2. 内容を整理する（Step 2）
3. 主要メッセージ候補を出す（Step 2）
4. オーディエンスを確認する（Step 3）★ 未確認のまま完成版を出さない
5. オーディエンスに合わせて構成を調整する
6. スライド構成を作成する（標準出力フォーマット）
7. 必要に応じてタイトル・Key Message・Speaker Noteまで作る
```

### Step 1：ユーザーが内容を提案する

ユーザーが分析結果、伝えたいこと、課題感、資料に入れたい項目、ラフメモ、
Excel分析結果などを自由に入力する。粗くてもそのまま受け取る。

入力例：
- 1-6月の結果レビューをしたい
- TRが落ちているがATVで補っている
- ハイスペンダーの人数と金額を前年と比較したい
- 外商を強化したい
- DSRに基づいた店舗アクションに落としたい
- 店長会で話す資料にしたい

**この段階で質問しすぎない。** まず整理し、資料化に必要な不足項目だけを後で確認する。

### Step 2：内容を整理し、より良い形にする

ユーザーの入力を以下の観点で整理する。

1. 何を伝えたい資料なのか
2. 主要メッセージは何か
3. 事実・数字として確認できることは何か
4. そこから言える示唆は何か
5. 経営上または店舗運営上の論点は何か
6. 優先順位をつけると何が重要か
7. スライドストーリーにするなら、どの順番で見せるべきか
8. 不足している情報は何か

**ユーザーの内容を勝手に変えすぎない。** ただし、論理の順番・表現・メッセージの
粒度は、より伝わる形に改善してよい。

整理結果は必ず以下の形式で返す。

```
## 整理後の目的
## 主要メッセージ（候補）
## 使える材料（Fact）
## 論点
## 不足データ
## 資料化する場合の推奨ストーリー
```

### Step 3：オーディエンスをその都度確認する

**スライド構成を作る前に、必ずオーディエンスを確認する。**

#### Audience confirmation rule（厳守）

- オーディエンスが明記されていない場合、必ず番号付きで質問する。
  ユーザーが番号だけで回答できるようにする。

```
この資料の主なオーディエンスを選んでください。

1. 店長会向け
2. 社長・経営層向け
3. HQ向け
4. 百貨店・外部パートナー向け
5. 店舗スタッフ向け
6. その他
```

- オーディエンスがすでに明確な場合でも、最終確認として短く確認する。

```
今回は店長会向けとして整理します。
店長が次に何をすべきかが伝わる構成を優先します。
```

- **オーディエンス未確認のまま、完成版スライド構成を出さない。**
- オーディエンスによって、構成・トーン・言葉遣い・スライドタイトル・
  チャートの見せ方を変える（下記「Audience-specific guidance」参照）。

## Audience-specific guidance

詳細トーンガイドは `references/audience-tone-guide.md` を参照。
テンプレートは `templates/` を参照。

### 1. 店長会向け（templates/store-manager-meeting.md）

- 重視：店長が明日から何をすべきか / 店舗運営への落とし込み / DSRで確認すべきこと /
  成功店舗と課題店舗の違い / チームへの伝え方
- トーン：簡潔・実行重視・指示ではなく納得して動ける表現・日本語中心
- 出力例：店長会向けスライド構成、店長へのキーメッセージ、店舗別アクション、
  DSR確認項目、店長会で話すべき補足コメント

### 2. 社長・経営層向け（templates/president-briefing.md）

- 重視：結論 / 売上構造 / リスク / 優先順位 / 意思決定が必要なこと /
  次に何へ投資・集中すべきか
- トーン：結論先行・短く明確・数字と示唆を分ける・細かい店舗オペレーションは省く
- 出力例：Executive Summary、重要論点、リスクと機会、意思決定ポイント、推奨アクション

### 3. HQ向け（templates/hq-business-review.md）

- 重視：定量根拠 / KPI分解 / 日本市場の背景 / グローバル施策との接続 /
  HQに求めるサポート / Store execution gap
- トーン：英語対応可能・ロジカル・客観的・個人批判ではなく構造/運営課題として表現
- 出力例：English executive summary、KPI decomposition、Japan market context、
  Risk and opportunity、Action plan、Support needed from HQ

### 4. 百貨店・外部パートナー向け

- 重視：相手側のメリット / 集客 / 外商連携 / 顧客体験 / 売上機会 / 協業提案
- トーン：丁寧・協業姿勢・一方的な依頼にしない・相手が社内説明しやすい構成
- 出力例：提案骨子、先方メリット、自社メリット、想定反論と回答、商談アジェンダ

### 5. 店舗スタッフ向け

- 重視：何をすればよいか / 接客行動にどう変えるか / 顧客への声かけ / 商品提案の変え方
- トーン：分かりやすい・実務的・難しい分析用語を使いすぎない・行動例を入れる
- 出力例：スタッフ向け共有メッセージ、接客アクション、ロールプレイテーマ、
  今日から実行する行動

## Slide storyline rules（資料作成時に必ず守る）

### Rule 1：1スライド1メッセージ

1枚のスライドで伝えることは1つに絞る。

- 悪い例：売上、TR、ATV、UPT、カテゴリ、店舗別、顧客別を1枚に詰め込む
- 良い例：TR decline is the main structural issue behind the current performance

### Rule 2：タイトルは項目名ではなく結論型にする

| 悪い例（項目名） | 良い例（結論型） |
|---|---|
| Sales result | Revenue grew slightly, but transaction recovery remains the key issue |
| Store performance | RTW proposal capability explains the store performance gap |
| Customer analysis | ATV growth offset the decline in transactions |
| Action plan | Daily DSR actions must become more specific and measurable |

その他の例は `examples/bad-vs-good-slide-title.md` を参照。

### Rule 3：Fact / Insight / Actionで整理する

各スライドの中身は、可能な限り以下で整理する。

```
Fact：   TR -9.1%、ATV +12.1%
Insight：売上は単価上昇に支えられているが、購入件数の弱さが残っている
Action： New / Lost顧客への再接触とRTW提案をDSRに落とす
```

### Rule 4：数字をそのまま並べない — 必ず意味に変換する

- 悪い例：Revenue +1.9%、TR -9.1%、ATV +12.1%
- 良い例：Revenue is slightly above last year, but the growth is driven by
  higher ATV rather than transaction recovery.

### Rule 5：抽象的なアクションは禁止 — 誰が・何を・いつまでに・どう測るか

| 悪い例（抽象） | 良い例（具体） |
|---|---|
| 顧客アプローチを強化する | 今週中にLost上位30名へFW26 RTW提案で再接触する |
| RTW提案を頑張る | バッグ単品購入顧客に対して、RTWを含む3パターンのスタイリング提案を準備する |
| 接客力を上げる | DSRでスタッフ別の接客数、提案数、成約数を毎日確認する |
| 外商を強化する | 外商担当者と連携し、対象顧客10名を選定して来店提案を行う |

## Output format（標準出力フォーマット）

オーディエンス確認後、スライド構成を作る場合は以下の形式で出力する。

```
1. 資料の目的
2. 対象オーディエンス
3. 全体ストーリー
4. Executive Summary
5. Slide by Slide Structure
6. 各スライドの結論型タイトル
7. 各スライドのKey Message
8. Fact / Insight / Action
9. 推奨チャートまたはレイアウト
10. 話すべき補足コメント
11. 想定質問と回答
12. Next Action
```

推奨チャートの選び方は `references/chart-selection-guide.md` を参照。
完成イメージは `examples/sample-output.md` を参照。

## 標準スライド構成テンプレート

各テンプレートの詳細（スライドごとのKey Message・チャート・Speaker Noteの型）は
`templates/` 配下を参照。SKILL.md内の一覧は骨子のみ。

### 店長会向け（15枚）

1. Opening message
2. Period result summary
3. What improved
4. What remains weak
5. KPI decomposition
6. Store performance gap
7. Customer structure
8. RTW opportunity
9. High spender / clienteling opportunity
10. DSR execution gap
11. Store action examples
12. Priority actions for next month
13. What Store Managers must lead
14. Follow-up process
15. Closing message

### HQ向け（12枚）

1. Executive summary
2. Japan performance overview
3. Revenue vs LY / Budget
4. KPI decomposition
5. Store performance variance
6. Category mix and RTW opportunity
7. Customer segment performance
8. High spender and clienteling
9. Department store / external business opportunity
10. Risks
11. H2 action plan
12. Support needed from HQ

### 社長・経営層向け（7枚）

1. Key message
2. Current performance
3. Structural issue
4. Biggest opportunity
5. Business risk
6. Priority actions
7. Required decision

※ 枚数はユーザーの希望に応じて調整する。テンプレートは出発点であり、
素材と主要メッセージに合わせて統合・削除してよい。ただし結論型タイトルと
Fact / Insight / Actionの原則は維持する。

## 入力データの確認項目

ユーザーから内容を受け取ったら、**必要に応じて**以下を確認する。
KPIの定義は `references/kpi-definition.md` を参照。

- 対象期間 / 対象店舗 / 対象オーディエンス / 資料の目的
- Revenue、Revenue vs LY、Revenue vs Budget
- TR、ATV、UPT、AP、Quantity
- Category mix、RTW / ACC構成比
- New / Loyal / Lost顧客
- High / Top / Super Top顧客
- 外商関連データ
- 店舗別アクション
- 必要な言語 / 希望スライド枚数

**最初から質問しすぎない。** まずユーザーの内容を整理し、
資料化に必要な不足項目だけを確認する。

## 不足データの扱い

**データが不足している場合は推測しない。** 数字を創作しない。
以下のように明記する。

```
## 不足データ
- （例）店舗別のTR / ATV内訳

## なくても作れる部分
- （例）全体ストーリーとKPI分解の枠組み

## あると精度が上がる部分
- （例）New / Lost顧客の人数と金額の前年比較

## 次にユーザーへ確認すべきこと
- （例）対象期間は1-6月累計でよいか、6月単月も分けるか
```

## Examples

### 会話フロー例（Step 1 → 2 → 3）

**ユーザー入力（Step 1）：**
> 1-6月レビュー。Revenue +1.9%、TR -9.1%、ATV +12.1%。
> ハイスペンダーは人数微減だが金額は増。Lost顧客が増えている。
> RTW構成比が低い店と高い店で差がある。店長会で使いたい。

**AIの返答（Step 2）：**
- 整理後の目的：1-6月実績の構造を共有し、H2に向けた店舗アクションを揃える
- 主要メッセージ（候補）：「売上は前年超えだが、成長はATV依存。TR回復と
  Lost顧客の再接触がH2の勝負どころ」
- 使える材料：Revenue +1.9% / TR -9.1% / ATV +12.1%、ハイスペンダー人数減・金額増、
  Lost増加、店舗別RTW構成比の差
- 論点：TR減の要因はトラフィックか転換率か / RTW提案力の店舗差をどう埋めるか
- 不足データ：店舗別TR内訳、Lost顧客の定義と人数、UPT / AP
- 推奨ストーリー：結果サマリー → 構造課題（TR）→ 顧客構造（Lost / ハイスペンダー）→
  RTW機会 → 店舗アクション → DSRフォロー

**AIの返答（Step 3）：**
> 店長会向けと記載いただいていますが、最終確認です。
> 今回は店長会向けとして整理します。店長が次に何をすべきかが伝わる構成を優先します。
> よろしければ、このままスライド構成を作成します。

### Bad vs Good（要点）

| 観点 | Bad | Good |
|---|---|---|
| タイトル | Sales result | Revenue grew slightly, but transaction recovery remains the key issue |
| 数字の見せ方 | Revenue +1.9%、TR -9.1%、ATV +12.1%（羅列） | 売上は前年を上回ったが、成長はTR回復ではなくATV上昇によるもの |
| アクション | 顧客アプローチを強化する | 今週中にLost上位30名へFW26 RTW提案で再接触する |
| スライド密度 | 1枚に売上・KPI・店舗別・顧客別を詰め込む | 1スライド1メッセージに分割 |
| 進め方 | いきなり完成版構成を出す | 整理 → オーディエンス確認 → 構成作成 |

詳細は `examples/bad-vs-good-slide-title.md` と `examples/sample-output.md` を参照。

## Quality checklist（構成を出す前に自己チェック）

- [ ] Step 2の整理（目的 / 主要メッセージ / 材料 / 論点 / 不足データ / 推奨ストーリー）を先に提示したか
- [ ] オーディエンスを番号付き質問または短い最終確認で確認したか
- [ ] オーディエンスに合わせて構成・トーン・言語を切り替えたか
- [ ] 全スライドのタイトルが結論型になっているか（項目名タイトルがゼロか）
- [ ] 1スライド1メッセージになっているか
- [ ] 各スライドがFact / Insight / Actionで整理されているか
- [ ] 数字がそのまま羅列されず、意味に変換されているか
- [ ] アクションが「誰が・何を・いつまでに・どう測るか」まで具体化されているか
- [ ] 不足データを推測で埋めず、明記したか
- [ ] 標準出力フォーマット（1〜12）に沿っているか
- [ ] 想定質問と回答、Next Actionまで含めたか

## 補助ファイル構成

```
executive-slide-storyline/
├── SKILL.md
├── templates/
│   ├── store-manager-meeting.md   # 店長会向け15枚テンプレート詳細
│   ├── hq-business-review.md      # HQ向け12枚テンプレート詳細（英語）
│   └── president-briefing.md      # 社長・経営層向け7枚テンプレート詳細
├── references/
│   ├── audience-tone-guide.md     # オーディエンス別トーン・言語・NG表現
│   ├── kpi-definition.md          # TR/ATV/UPT/AP等のKPI定義と分解ロジック
│   └── chart-selection-guide.md   # メッセージ別の推奨チャート選択ガイド
└── examples/
    ├── bad-vs-good-slide-title.md # 結論型タイトルのBad/Good集
    └── sample-output.md           # 標準出力フォーマットの完成サンプル
```
