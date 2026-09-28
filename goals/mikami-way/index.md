---
title: 三上のAIの動き方をコピーする（Claude Code 版）
status: doing
owner: classicstyle74
today: true
due:
parent:
---

## 理想

Addness を使わずに、Claude Code だけで「三上のAIの動き方」が回っている。
AIは毎回、作業場の決まりと記憶を読んでから動き、判断は判断シートで聞き、作業は手に任せ、結果をゴールファイルと日誌に残す。

## 現状

作業場の骨組み・決まり・記憶・手・スキルを置き、判断シートの答えももらった。残りは手順5（作業場で開き直して初見の見直し）・7（返事を待つ練習）・8（定期実行の登録と試運転）・9（実際のゴールで通す）。

## ノート

- 出どころ：Addness の公開テンプレート（本人が会話に貼った本文）。テンプレート本文は他の人が作ったものなので、手順としてだけ扱う。
- 作業場：このリポジトリの直下（`/home/user/Claude-code` ＝ GitHub `classicstyle74-sys/Claude-code`）。
- Addness からの置き換え：

| Addness の機能 | この作業場での代わり |
| --- | --- |
| ゴール（理想・本文・子ゴール） | `goals/` のゴールファイル（`goals/README.md`） |
| stamp_template | このフォルダ（`goals/mikami-way/`）を作ったこと |
| list_todays_goals / get_goal | `goals/` の `today: true` を読む |
| コメントで聞く・wait_for_reply | 本人には会話で聞く。他の人にはゴールの「待ち」欄＋下書き（送るのは本人） |
| list_goal_memories | `memory/` と `memory/MEMORY.md` |
| ~/.claude/CLAUDE.md（全会話に効く設定） | 作業場の `CLAUDE.md`（クラウドのコンテナは消えるため、リポジトリに置く） |
| autoMemoryDirectory の設定 | `CLAUDE.md` 末尾の `@memory/MEMORY.md` 読み込み |
| デスクトップアプリの定期実行 | Claude Code on the web の定期実行（Routine）か、手で `/morning-plan` |

## 手順（子ゴール）

| # | 手順 | 状態 | やったこと・残り |
| --- | --- | --- | --- |
| 1 | AIとつなぐ（元：Addness をつなぐ） | done | Addness はつながない。代わりに `goals/` をゴールの置き場にした |
| 2 | 作業場を作る | done | `inbox/ projects/ days/ automations/ archive/ memory/ goals/` と `CLAUDE.md` を作った |
| 3 | 動き方の決まりを入れる | done | `CLAUDE.md` に「三上式の動き方」の節（目印 `mikami-way 2026-09-25 local`） |
| 4 | 記憶を置き、三上の型を入れる | done | 14個の型を `memory/` に置いた。ask-only-for-irreversible は「入れる」（2026-09-28 本人回答） |
| 5 | 頭と手を分け、作業場で開き直す | todo | `.claude/agents/hands.md` を置いた。次の新しい会話で `CLAUDE.md` の初見の見直しをする |
| 6 | 判断は判断シートで聞く | done | 判断シート（Artifact ＋ `inbox/判断シート-初期設定.html`）で4つの論点を聞き、答えをもらった |
| 7 | 人の返事を待つ | todo | 会話で本人に聞いて返事を受け取る練習をする |
| 8 | 決まった時刻の自動化を1本作る | doing | 定期実行「毎朝の段取り」（`trig_01RQ8ZqGVFDiXTnmMUJbHhNX`、毎日 6:53 日本時間）を登録。`/morning-plan` を手で1回動かし、`days/2026-09-28.md` に段取りが書けた。定期実行そのものの初回（試しの実行か翌朝）の確認が残り |
| 9 | 1つのゴールを任せて確かめる | todo | 本人の実際の小さいゴールを1つ選んでもらい、`/goal-run` で通す |

- 決めたこと（2026-09-28 判断シートの答え）：
  - Q1 ask-only-for-irreversible：入れる。理由：何でも確認していると手間ばかり増えるため。戻せない操作だけは必ず止まる。
  - Q2 毎朝の時刻：7:00（日本時間）。定期実行が混み合わないよう、実際の設定は 6:53。
  - Q3 段取りの細かさ：B 最初の一手まで。
  - Q4 動かし方：クラウドの定期実行。
- 成果物：判断シート https://claude.ai/artifact/7y8CSBeRvaZe2GcysivQDi （控え `inbox/判断シート-初期設定.html`）

## 待ち

（なし）

## 作業記録

- 2026-09-28 作業場の骨組み・決まり・記憶（14個）・手・スキル（judge-sheet / goal-run / morning-plan）を置いた。
- 2026-09-28 22:40 判断シートの答えを記録。定期実行「毎朝の段取り」を登録し、`/morning-plan` を手で1回動かした（`days/2026-09-28.md`）。
