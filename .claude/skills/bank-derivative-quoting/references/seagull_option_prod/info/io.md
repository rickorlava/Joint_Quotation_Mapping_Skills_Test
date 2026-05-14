# 海鸥期权 Delta 与脚本契约

## 0. 文档定位
本文件定义海鸥期权报价 agent 的 **风格化 Delta 表、脚本路径与 CLI**。求解器选型见 `agent_output/quotation_format.md`。

## 1. Delta 表(契约)

| 方向 | Delta 符号约定 | 激进 | 保守 |
|---|---|---|---|
| 结汇 `settle` | 负值 | **-0.2** | **+0.15** |
| 购汇 `purchase` | 正值 | **+0.2** | **-0.15** |

风格化须 `--delta <值>` 且 `--inverse-type delta`(固定为 `delta`)。

## 2. 脚本路径

```
bank-derivative-quoting/scripts/seagull_option_query.py
```

## 3. 参数

| 参数 | 含义 |
|---|---|
| `--user-id` | 从 memory |
| `--currency-pair` | 货币对 |
| `--settle-purchase` | `settle` / `purchase` |
| `--term` | 期限 |
| `--delivery-date` | 交割日 |
| `--desired-strikes` | 执行价,一或两个值 |
| `--prem-pips` | 补贴点数,一或两个值 |
| `--delta` | 风格 Delta |
| `--inverse-type` | 与 `--delta` 同用,值 `delta` |
| `--profit` | 中收 |

## 4. 调用示例

```bash
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --term 3M
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --delivery-date 2026-04-20
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --term 3M --desired-strikes 7.0
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --term 3M --prem-pips 100
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --term 3M --desired-strikes 7.0 --prem-pips 100
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --term 3M --desired-strikes 7.0 7.5
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --term 3M --prem-pips 50 150
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --term 3M --delta 0.2 --inverse-type delta
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --delivery-date 2026-04-20 --term 3M
```

## 5. 脚本行为

双目标与区间扫描:脚本一次返回约 5 档梯度。单次输出可原样透传。组合多调时由 agent 汇总。
