# 毎朝の段取り

## 何をするか

今日のToDo（`goals/` の `today: true` と期限が今日以前のゴール）を読み、`days/YYYY-MM-DD.md` に「## 今日の段取り」を書く。中身は `/morning-plan` スキル（`.claude/skills/morning-plan/SKILL.md`）。

## やらないこと

- ゴールファイルの変更・完了
- メールなど外への送信
- `days/` 以外への書き込み

## 設定（2026-09-28 判断シートで決定）

- 時刻：毎日 7:00 ごろ（日本時間）。定期実行が混み合わないよう、実際の設定は 6:53
- 細かさ：最初の一手まで
- 動かし方：クラウドの定期実行
- 保存先：`.claude/skills/morning-plan` があるブランチ（マージ前は `claude/addness-template-integration-f3p5ed`、マージ後はマージ先のブランチ）に、`days/` だけをコミットして push する

## どこで動くか

- クラウドの定期実行（Routine）：毎朝決まった時刻に新しいクラウドのセッションが立ち上がり、このリポジトリで `/morning-plan` を実行し、`days/` をコミットして push する。
- 手で動かす：Claude Code でこのリポジトリを開き、`/morning-plan` と送る。

## 登録した定期実行

- 名前：毎朝の段取り
- ID：`trig_01RQ8ZqGVFDiXTnmMUJbHhNX`
- スケジュール：`CRON_TZ=Asia/Tokyo 53 6 * * *`（毎日 6:53 日本時間）
- 終わったらスマホに通知

## 止め方

- claude.ai/code の「Routines」（定期実行の一覧）から「毎朝の段取り」を止めるか消す。
- または Claude Code の会話で「毎朝の段取りの自動化を止めて」と頼む。
