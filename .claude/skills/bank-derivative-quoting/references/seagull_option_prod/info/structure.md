# 海鸥期权统一内部表示

## 0. 文档定位
本文件定义海鸥期权报价 agent 的 **内部字段与层级**。Delta 数值见 `info/io.md`。

## 1. 字段表

| 字段 | 含义 | 说明 |
|---|---|---|
| `product` | 产品类型 | 固定 `seagull` |
| `user_id` | 用户ID | 必填,从 **memory** 取 |
| `currency_pair` | 货币对 | 默认 `USDCNY` |
| `direction` | 方向 | `settle` / `purchase`,默认 `settle` |
| `term` | 期限 | 预设档或自由期限 |
| `delivery_date` | 交割日 | 具体日期 |
| `desired_strikes` | 执行价目标 | 单点或两点 |
| `prem_pips` | 补贴/收益点数 | 单点或两点 |
| `target_all_in_rate` | 最终成交价目标 | 语义字段,须反推为 `prem_pips` |
| `delta_preference` | 风格 | 激进 / 保守 |
| `delta_value` | Delta 数值 | 见 `info/io.md` |
| `profit` | 中收 | 通用 |
| `quote_mode` | 求解模式 | agent 推断 |

## 2. 层级

- **结构**: `desired_strikes`
- **收益**: `prem_pips`、`profit`
- **结果目标**: `target_all_in_rate`
- **风格**: `delta_preference`、`delta_value`

勿将 `target_all_in_rate` 与 `desired_strikes` 混为一谈。

## 3. 规则

**term / delivery_date**: 同时给则以 `term` 为准;皆缺则 `chat` 追问。

**term**: 支持 `1W`/`1M`/`3M`/`6M`/`1Y` 及 `2M` 等自由期限;勿强行归到预设档。

**user_id**: 仅从 memory 取,不要求用户输入。
