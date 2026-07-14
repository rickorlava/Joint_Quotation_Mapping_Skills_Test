# 海鸥期权 Delta 与脚本契约

## 0. 文档定位
本文件定义海鸥期权报价 agent 的 **风格化 Delta 表、脚本路径与 CLI**。求解器选型见 `agent_output/quotation_format.md`。

## 1. Delta 表(契约)

### 1.1 Delta 数值表

| 方向 | 风格 | Delta 值           | 符号说明 |
|---|---|-------------------|------|
| **结汇(settle)** | 激进 | **delta = -0.3**  | 负值   |
| **结汇(settle)** | 保守 | **delta = -0.20** | 负值   |
| **购汇(purchase)** | 激进 | **delta = +0.3**  | 正值   |
| **购汇(purchase)** | 保守 | **delta = +0.20** | 正值   |

### 1.2 记忆口诀

> **"海鸥期权结汇负值，购汇正值"**
> - 购汇方向：激进 = 正值(+0.3)，更激进 = 正值(+0.35), 绝对值增大
> - 购汇方向：保守 = 正值(+0.20), 更保守 = 正值(+0.15), 绝对值减小
> - 结汇方向：激进 = 负值(-0.3)，更激进 = 负值(-0.35), 绝对值增大
> - 结汇方向：保守 = 负值(-0.20), 更保守 = 负值(-0.15), 绝对值减小

### 1.3 快速查表

```
用户说"激进" → 先判断方向 → 再确定 delta 符号 -> 再确定delta值
  - 结汇 + 激进 → delta = -0.30
  - 购汇 + 激进 → delta = +0.30

用户说"更激进" → 在激进基础上 +0.05 步长 -> 再确定delta值
  - 结汇 + 更激进 → delta = -0.35（-0.30 - 0.05）
  - 购汇 + 更激进 → delta = +0.35（+0.30 + 0.05）

用户说"保守" → 先判断方向 → 确定 delta 符号 -> 再确定delta值
  - 结汇 + 保守 → delta = -0.20
  - 购汇 + 保守 → delta = +0.20

用户说"更保守" → 在保守基础上 +、- 0.05 步长 
  - 结汇 + 更保守 → delta = -0.15（-0.20 + 0.05）
  - 购汇 + 更保守 → delta = +0.15（+0.20 - 0.05）
```

### 1.4 常见错误警示

❌ **错误理解**：激进就是正值，保守就是负值
✅ **正确理解**：delta 的符号由**方向**决定，不同产品符号规则不同

| 错误示例                     | 正确做法                     |
|--------------------------|--------------------------|
| "结汇激进" → delta = +0.2 ❌  | "结汇激进" → delta = -0.3 ✅  |
| "购汇保守" → delta = -0.15 ❌ | "购汇保守" → delta = +0.20 ✅ |

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
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --term 3M --delta -0.2 --inverse-type delta
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --delivery-date 2026-04-20 --term 3M
```

## 5. 脚本行为

双目标与区间扫描:脚本一次返回约 5 档梯度。单次输出可原样透传。组合多调时由 agent 汇总。
