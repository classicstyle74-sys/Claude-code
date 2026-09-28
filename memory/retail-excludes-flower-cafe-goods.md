---
name: retail-excludes-flower-cafe-goods
description: 「Retail」で集計する時は、Retail Concession と Retail Store のうち「Flower Café - Goods」を除く
type: user
---

本人が「Retail」と言った時の範囲は、Macro channel が Retail Concession と Retail Store の店舗から「Flower Café - Goods」を除いたもの。

**Why:** 2026-09-28、9月MTDの集計で Flower Café - Goods を含めて出したところ、本人から「Retailと言った時は除いて」と直された。この店は物販で客数・客単価の動きが他店と大きく違い（2026年9月は客数が前年の約10倍）、Retail全体のKPIをゆがめる。
**How to apply:** 売上データ（明細Excel：Calendar date, Macro channel, Store desc. (Parent) など）で Retail を集計する時は、最初から `Store desc. (Parent) != "Flower Café - Goods"` で除く。「MARNI CAFE」は除外を言われていないので含める。除外したことは結果に一言添える。
