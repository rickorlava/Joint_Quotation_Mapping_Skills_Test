# 结构性掉期产品知识说明

## 0. 文档定位
本文件定义结构性掉期报价 agent 的 **产品元知识**

## 1.1 结构性掉期的定义

结构性掉期 = **一个掉期 + 卖出一个期权**。通过卖出期权，获取期权费，将期权费补贴到掉期近端或远端，使得原掉期的一端有更好的价格。

对客户的直观价值:

- 掉期近端或者远端实际成交价比标准掉期更优
- 代价是承担期权被行权的风险

产品设计要求：
> 卖出期权交割日 = 掉期远端交割日
> 期权费默认补贴掉期近端。

## 1.2 方向与期权结构的映射关系

| 用户表达 | 内部方向 | 期权结构 |
|---|---|---|
| 结汇 | `settle` | Sell Put |
| 购汇 | `purchase` | Sell Call |

> 此映射为产品层面的业务约定,不可由模型自行更改。

## 2. 报价
### 2.1 正算报价

- 输入货币对、方向、近远端交割日、中收
- 2.1.1 获取 原始掉期:（nearBasePrice + swapBasePoint = farBasePrice）
- 2.1.2 获取 期权: 默认strike -> premPips（期权费）

### 2.2 反算报价 (strike)

- 输入货币对、方向、近远端交割日、中收 + 反算类型（delta、pips）
- 2.2.1 获取原始掉期
- 2.2.2 通过 delta或者 premPips(期权费) 反算 获取strike。
- 2.2.3 获取 strike -> premPips

### 2.3 公共计算逻辑

- 若补贴近端
  结构性掉期 近端价格 nearPrice = nearBasePrice + premPips 
  结构性掉期 掉期点 swapPoint = farBasePrice - nearPrice - profit
  结构性掉期 远端价格 farPrice = nearPrice + swapPoint

- 若补贴远端
  结构性掉期 远端价格 farPrice = farBasePric + premPips
  结构性掉期 掉期点 swapPoint = farPrice - nearPrice - profit
  结构性掉期 近端价格 nearPrice = farPrice - swapPoint

### 2.4 最终报价结果：

+ 掉期格式（nearPrice 近端, swapPoint 掉期点, farPrice 远端）
+ strike（行权价）、premPips（期权费）、补贴前折年化、补贴后折年化、补贴点数等 
+ profit 为产品的利润，假设它是已知的，报价接口会根据其余输入参数指定

## 3. 报价接口 IO 格式

脚本路径:

```
bank-derivative-quoting/scripts/opt_structured_swap_query.py
```

### 3.1 完整参数清单

| 参数 | 含义 | 互斥关系 |
|---|---|---|
| `--user-id` | 用户ID,从 memory 获取 | - |
| `--currency-pair` | 货币对 | - |
| `--settle-purchase` | 方向,`settle` / `purchase` | - |
| `--term` | 远端期限 | 默认远端 |
| `--delivery-date` | 交割日 | 默认远端 |
| `--desired-strike` | 目标执行价 K(单值) | - |
| `--profit` | 中收点数 | - |
|`--near-term`| 近端期限| 近端 |
|`--near-delivery-date`|近端交割日|-|

### 3.2 典型调用示例

```bash
# 给 term 求 K
python bank-derivative-quoting/scripts/opt_structured_swap_query.py --user-id {userId} --currency-pair USDCNY --settle-purchase settle --term 3M

# 给 K 求 term
python bank-derivative-quoting/scripts/structured_swap_query.py --user-id {userId} --currency-pair USDCNY --settle-purchase settle --desired-strike 7.10

# 指定交割日求 K
python bank-derivative-quoting/scripts/opt_structured_swap_query.py --user-id {userId} --settle-purchase settle --delivery-date 2026-09-01

# 带中收
python bank-derivative-quoting/scripts/opt_structured_swap_query.py --user-id {userId} --term 3M --profit 100
```

### 3.3 脚本行为承诺

- 单次调用返回字符串已按规范组装,**直接透传**
- 组合调用由 agent 负责汇总与筛选
- **可以传入 K 和 term/delivery-date

## 4. 注意事项

1. **K 与 term 可以同时**,调用标准结构性掉期接口
2. **补贴点数是目标不是输入**:用户给出补贴目标时,走扫描反查组合,不作为参数直接传入
3. **不存在双目标探索**:解空间是一维曲线,没有二维折中
4. **区间扫描走组合**:K 区间或 term 区间通过多次单点调用实现
5. **调用纪律**:每次调用必须有独立语义目的
6. **组合调用预算**:上限 6 次
7. **先规划后执行**:组合前必须列出调用计划清单
8. **直接透传单次输出**;组合输出汇总为单表,补贴反查只输出筛选后方案
9. **产品识别锚**:"结构性掉期""产品报价"
10. **`term` 自由**:支持预设档位和自由期限
11. **日期优先级**:`term` > `delivery_date`
12. **默认值**:币种 `USDCNY`;方向 `settle`
13. **`user_id` 来源**:memory
14. **固定文案**:未开市 / 节假日使用报价范式所规定输出格式对应的 `2.5/2.6` 固定文案
15. **历史六字段格式**仅作兼容识别,不作为推荐形态
