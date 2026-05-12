# 海鸥期权报价 — Delta 与脚本调用契约（分册）

## 0. 文档定位

本分册对应合订本 **§8–§9**：风格化 Delta 硬表、脚本路径、CLI 参数与行为承诺。求解器选型见 [`quotation_format.md`](quotation_format.md)。

---

## 8. 风格化求解器:Delta 数值表(契约层)

| 方向 | Delta 符号 | 激进 | 保守 |
|---|---|---|---|
| 结汇(settle) | 负值 | **delta = -0.2** | **delta = +0.15** |
| 购汇(purchase) | 正值 | **delta = +0.2** | **delta = -0.15** |

调用时使用 `--delta <value>` 并配合 `--inverse-type delta`。

---

## 9. 脚本调用契约

脚本路径:

```
bank-derivative-quoting/scripts/seagull_option_query.py
```

### 9.1 完整参数清单

| 参数 | 含义 |
|---|---|
| `--user-id` | 用户ID,从 memory 获取 |
| `--currency-pair` | 货币对 |
| `--settle-purchase` | 方向,`settle` / `purchase` |
| `--term` | 期限,支持预设档位与自由期限 |
| `--delivery-date` | 交割日 |
| `--desired-strikes` | 目标执行价,单值或两值 |
| `--prem-pips` | 目标补贴点数,单值或两值 |
| `--delta` | 风格化 Delta 数值 |
| `--inverse-type` | 与 `--delta` 搭配,固定为 `delta` |
| `--profit` | 中收点数 |

### 9.2 典型调用示例

```bash
# 基准报价
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --term 3M

# 指定交割日
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --delivery-date 2026-04-20

# 只给执行价
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --term 3M --desired-strikes 7.0

# 只给补贴点数
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --term 3M --prem-pips 100

# 双目标探索(给定 term,strike 和 prem_pips 都以目标值给出,脚本在该 term 切片内返回接近两目标的几组折中解)
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --term 3M --desired-strikes 7.0 --prem-pips 100

# 执行价区间扫描
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --term 3M --desired-strikes 7.0 7.5

# 补贴区间扫描
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --term 3M --prem-pips 50 150

# 风格化
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --term 3M --delta 0.2 --inverse-type delta

# term 与 delivery-date 同时传入,以 term 为准
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --delivery-date 2026-04-20 --term 3M
```

### 9.3 脚本行为承诺
- 双目标探索、区间扫描时,脚本自动返回 5 个梯度报价
- 单次调用结果可直接透传
- 组合调用由 agent 负责汇总
