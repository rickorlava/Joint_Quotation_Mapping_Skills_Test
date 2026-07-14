# 结构性掉期 Agent 标准输出字段

agent 报价结果包含以下字段:

| 字段 | 说明 | 取值来源 |
|---|---|---|
| 货币对 | 如 `USDCNY` | 取当次报价入参 `--currency-pair` |
| 结汇/购汇方向 | `结汇` 或 `购汇` | 取入参 `--settle-purchase` settle→结汇, purchase→购汇 |
| 近端交割日 | 近端交割日期 | 报价结果 nearDate |
| 近端价格 | 近端成交价 | 报价结果 nearPrice |
| 掉期点 | 掉期点数 | 报价结果 swapPoint |
| 远端交割日 | 远端交割日期 | 报价结果 farDate |
| 远端价格 | 远端成交价 | 报价结果 farPrice |
| 行权价 K | 期权执行价 | 报价结果 strike |
| 补贴点数 | 期权费补贴 | 报价结果 premPips |
| 补贴后折年化 | 含补贴的折年化收益率 | 报价结果 annualizedRate |
| 中收 | 可选 | 报价结果 profit |
