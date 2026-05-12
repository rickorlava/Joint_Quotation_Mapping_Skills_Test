# 海鸥期权报价 — 统一内部表示（分册）

## 0. 文档定位

本分册对应合订本 **§3**，定义海鸥期权 agent 的内部字段、层级与期限规则。产品背景见 [`spec.md`](spec.md)；风格对应的 Delta 数值见 [`script_contract.md`](script_contract.md)。

---

## 3. 统一内部表示

| 字段 | 含义 | 说明 |
|---|---|---|
| `product` | 产品类型 | 固定为 `seagull` |
| `user_id` | 用户ID | 必填,**从记忆系统(memory)获取** |
| `currency_pair` | 货币对 | 未指定默认 `USDCNY` |
| `direction` | 方向 | `settle` / `purchase`;未指定默认 `settle` |
| `term` | 期限 | 既支持预设档位,也支持自由期限 |
| `delivery_date` | 交割日 | 具体日期 |
| `desired_strikes` | 目标执行价 | 单点或两点 |
| `prem_pips` | 目标补贴/收益点数 | 单点或两点 |
| `target_all_in_rate` | 最终成交效果目标价 | 语义字段,需反推为 `prem_pips` |
| `delta_preference` | 风格偏好 | 激进 / 保守 |
| `delta_value` | 风格对应的 Delta 数值 | 见 [`script_contract.md`](script_contract.md) 中 Delta 数值表 |
| `profit` | 中收 / 附加点数 | 通用参数 |
| `quote_mode` | 求解模式 | 由 agent 推断 |

### 3.1 字段的层级分类
- **结构参数**:`desired_strikes`
- **收益参数**:`prem_pips`、`profit`
- **结果目标**:`target_all_in_rate`
- **风格偏好**:`delta_preference` / `delta_value`

不要把 `target_all_in_rate` 草率等同于 `desired_strikes`。

### 3.2 `term` 与 `delivery_date` 的优先级
- 若同时提供,以 `term` 为准
- 若两者都缺失,通过 `chat` 追问

### 3.3 `term` 字段的自由度
`term` 既支持预设档位(`1W` / `1M` / `3M` / `6M` / `1Y`),也支持自由期限(如 `2M`、`4M`、`9M`)。agent 不要把用户输入强行截断到预设档位。

### 3.4 `user_id` 获取
从记忆系统(memory)中获取,不要求用户在输入中提供。
