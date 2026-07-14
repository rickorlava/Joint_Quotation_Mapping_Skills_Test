# 海鸥期权 Agent 标准输出字段

agent 报价结果包含以下字段:

| 字段      | 说明 | 取值来源 |
|---------|---|---|
| 货币对     | 如 `USDCNY` | 取当次报价入参 `--currency-pair` |
| 结汇/购汇方向 | `结汇` 或 `购汇` | 取入参 `--settle-purchase` settle→结汇, purchase→购汇 |
| 期限      | 具体交割日期 | 报价结果 deliveryDate |
| 执行价 K   | 行权价 | 报价结果 strike |
| 补贴点数    | 期权费补贴 | 报价结果 premPips |
| 中收      | 可选 | 报价结果 profit |
| 优化价     | 最终海鸥期权报价|报价结果| target_all_in_rate|