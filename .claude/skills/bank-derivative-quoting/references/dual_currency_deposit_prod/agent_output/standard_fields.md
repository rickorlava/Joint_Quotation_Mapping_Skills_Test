# 双货币存款 Agent 标准输出字段

agent 报价结果包含以下字段:

| 字段 | 说明 | 取值来源 |
|---|---|---|
| 货币对 | 如 `USDCNY` | 取当次报价入参 `--currency_pair` |
| 结汇/购汇方向 | `结汇` 或 `购汇` | 取入参 `--settle_purchase` settle→结汇, purchase→购汇 |
| 期限 | 具体交割日期 | 报价结果 deliveryDate 格式化 `yyyy-MM-dd` |
| 转换汇率 | 行权价 K | 报价结果 strike |
| 补贴参考收益率(年化:%) | 补贴部分的年化收益率 | 报价结果 dcdDepoRate |
| 中收 | 可选 | 报价结果 profit |