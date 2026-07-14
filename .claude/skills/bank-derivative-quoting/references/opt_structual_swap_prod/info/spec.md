# 结构性掉期产品知识说明

## 0. 文档定位
本文件定义结构性掉期报价 agent 的 **产品元知识**

## 1.1 结构性掉期的定义

结构性掉期 = **一个掉期 + 卖出一个期权**。通过卖出期权，获取期权费，将期权费补贴到掉期近端或远端，使得原掉期的一端有更好的价格。
掉期要素：近端交割日（近端期限）、近端汇率、 掉期点、远端汇率、远端交割日（远端期限)

对客户的直观价值:

- 掉期近端或者远端实际成交价比标准掉期更优
- 代价是承担期权被行权的风险

产品设计要求：
> 卖出期权交割日 = 掉期远端交割日
> 期权费默认补贴掉期近端。
> 当前仅支持结汇方向，购汇方向进行错误信息提示（“当前结构性掉期仅支持结汇方向”）。

## 1.2 方向与期权结构的映射关系

| 用户表达 | 内部方向 | 期权结构 |
|---|---|---|
| 结汇 | `settle` | Sell Put |
| 购汇 | `purchase` | Sell Call |

> 此映射为产品层面的业务约定,不可由模型自行更改。

## 1.3 脚本选型与参数识别（核心规则，务必遵守）

结构性掉期存在**两个报价脚本**，必须根据用户约束条件选择正确的脚本。

### 关键词映射 — 期权费 vs 中收（最容易混淆，必须区分）

| 用户表述 | 含义 | 脚本参数 | 使用脚本 |
|---------|------|---------|---------|
| **期权费**、**补贴**、**补贴点数**、**prem** | 卖出期权获得的费用，补贴到掉期端 | `--prem-pips {值}` | `structured_swap_query.py` |
| **中收**、**profit**、**预期中收** | 银行中间业务收入 | `--profit {值}` | `opt_structured_swap_query.py` 或 `structured_swap_query.py` |
| **执行价**、**K**、**行权价**、**strike** | 期权执行价格 | `--target-strikes {值}` | `structured_swap_query.py` |
| **delta**、**激进**、**保守** | 期权风险指标 | `--delta {值}` | `structured_swap_query.py` |

> **关键区别**：
> - **"补贴100点" / "期权费100pips" / "补贴点数=100"** → `--prem-pips 100` → `structured_swap_query.py`
> - **"中收100pips" / "中收100点"** → `--profit 100` → `opt_structured_swap_query.py`（若仅此项）或 `structured_swap_query.py`（若同时有 K/prem/delta）
> - **只说"100pips"等模糊表述**：结合上下文判断；若无法判断，通过 `chat` 进行追问是中收 还是 期权费

### 脚本选型判据

**核心判据**：
- 用户**未给 K / prem / delta** → `opt_structured_swap_query.py`（基准报价）
- 用户**给出 K / prem / delta 任一** → `structured_swap_query.py`（独立求解）

| 用户约束                              | 使用脚本 | 报价范式           | 关键区别                               |
|-----------------------------------|---------|----------------|------------------------------------|
| 仅 近、远端期限（无 K / prem / delta）      | `opt_structured_swap_query.py` | 1.1 基准报价 K=FAR | 默认 K=远端价格                          |
| 仅 近、远端交割日（无 K / prem / delta）     | `opt_structured_swap_query.py` | 1.2 基准报价 K=FAR | 默认 K=远端价格                          |
| 仅 近远端期限或交割日组合（无 K / prem / delta） | `opt_structured_swap_query.py` | 1.3 双term基准报价  | 默认 K=远端价格                          |
| far-term + K（执行价）                 | **`structured_swap_query.py`** | 1.4 K确定求prem   | `--target-strikes` + `--far-term`  |
| far-term + prem（期权费）              | **`structured_swap_query.py`** | 1.5 Prem反求K    | `--prem-pips` + `--far-term`       |
| far-term + K + prem               | **`structured_swap_query.py`** | 1.6 双目标探索      | `--target-strikes` + `--prem-pips` |
| far-term + [K₁, K₂] 区间            | **`structured_swap_query.py`** | 1.7 K区间扫描      | `--target-strikes K1 K2`           |
| far-term + [p₁, p₂] 区间            | **`structured_swap_query.py`** | 1.8 Prem区间扫描   | `--prem-pips p1 p2`                |
| far-term + delta（风格）              | **`structured_swap_query.py`** | 1.9 风格化报价      | `--delta` + `--far-term`           |
| 仅 K（无 term）                       | **`structured_swap_query.py`** | 追问 term 后走 1.4 | 可默认 6M                             |

### 参数命名区别（不可混用）

| 参数 | opt 脚本                | 标准脚本 |
|------|-----------------------|---------|
| 执行价 | `--target-strike`（单值） | `--target-strikes`（1-2值） |
| 期限 | `--far-term`（远端）      | `--far-term`（远端）+ `--near-term`（近端） |
| 近端日期 | `--near-delivery-date`  | `--near-delivery-date` |
| 远端日期 | `--far-delivery-date`   | `--far-delivery-date` |
| 期权费 | ❌ 不支持                 | `--prem-pips` |
| delta | ❌ 不支持                 | `--delta` |


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
  结构性掉期 远端价格 farPrice = farBasePrice + premPips
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

| 参数                     | 含义 | 互斥关系             |
|------------------------|---|------------------|
| `--user-id`            | 用户ID,从 memory 获取 | -                |
| `--currency-pair`      | 货币对 | -                |
| `--settle-purchase`    | 方向,`settle` / `purchase` | -                |
| `--far-term`           | 远端期限 | 默认远端             |
| `--far-delivery-date`  | 交割日 | 默认远端             |
| `--desired-strike`     | 目标执行价 K(单值) | -                |
| `--profit`             | 中收点数 | -                |
| `--near-delivery-date` |近端交割日| 等价 `--near-term` |
| `--near-term`          | 近端期限| 与近端交割日等价         |

### 3.2 典型调用示例

```bash
# 给 term 求 K
python bank-derivative-quoting/scripts/opt_structured_swap_query.py --user-id {userId} --currency-pair USDCNY --settle-purchase settle --far-term 3M

# 给 K 求 term
python bank-derivative-quoting/scripts/structured_swap_query.py --user-id {userId} --currency-pair USDCNY --settle-purchase settle --desired-strike 7.10

# 指定交割日求 K
python bank-derivative-quoting/scripts/opt_structured_swap_query.py --user-id {userId} --settle-purchase settle --far-delivery-date 2026-09-01

# 带中收
python bank-derivative-quoting/scripts/opt_structured_swap_query.py --user-id {userId} --far-term 3M --profit 100

# 带近端term或交割日
python bank-derivative-quoting/scripts/opt_structured_swap_query.py --user-id {userId} --currency-pair USDCNY --settle-purchase settle --far-term 3M --near-term {near-term}

python bank-derivative-quoting/scripts/opt_structured_swap_query.py --user-id {userId} --currency-pair USDCNY --settle-purchase settle --far-term 3M --near-delivery-date {near-delivery-date}
```


### 3.3 脚本行为承诺

- 单次调用返回字符串已按规范组装,**直接透传**
- 组合调用由 agent 负责汇总与筛选
- **可以传入 K 和 term/delivery-date

## 4. 风格化求解器:Delta 数值表(契约层)

风格偏好必须按下列业务约定映射为 Delta 数值:

### 4.1 Delta 数值表

| 方向 | 风格 | Delta 值 | 符号说明 |
|---|---|---|---|
| **结汇(settle)** | 激进 | **delta = +0.2** | 正值 |
| **结汇(settle)** | 保守 | **delta = -0.15** | 负值 |
| **购汇(purchase)** | 激进 | **delta = -0.2** | 负值 |
| **购汇(purchase)** | 保守 | **delta = +0.15** | 正值 |

### 4.2 记忆口诀

> **"结汇激进正值，购汇激进负值"**
> - 结汇方向：激进 = 正值(+0.2)，保守 = 负值(-0.15)
> - 购汇方向：激进 = 负值(-0.2)，保守 = 正值(+0.15)

### 4.3 快速查表

```
用户说"激进" → 先判断方向 → 再确定 delta 符号
  - 结汇 + 激进 → delta = +0.2
  - 购汇 + 激进 → delta = -0.2

用户说"保守" → 先判断方向 → 再确定 delta 符号
  - 结汇 + 保守 → delta = -0.15
  - 购汇 + 保守 → delta = +0.15
```

### 4.4 常见错误警示

❌ **错误理解**：激进就是负值，保守就是正值
✅ **正确理解**：delta 的符号由**方向**决定，不是由风格决定

| 错误示例 | 正确做法 |
|---|---|
| "结汇激进" → delta = -0.2 ❌ | "结汇激进" → delta = +0.2 ✅ |
| "购汇保守" → delta = -0.15 ❌ | "购汇保守" → delta = +0.15 ✅ |

### 4.5 风格化调用示例

```bash
# 结汇激进风格
python bank-derivative-quoting/scripts/opt_structured_swap_query.py --user-id {userId} --currency-pair USDCNY --settle-purchase settle --term 3M --delta 0.2 --inverse-type delta

# 结汇保守风格
python bank-derivative-quoting/scripts/opt_structured_swap_query.py --user-id {userId} --currency-pair USDCNY --settle-purchase settle --term 3M --delta -0.15 --inverse-type delta
```

---

## 5. 注意事项

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
16. **交割日或term**正确识别对应近端、对应远端
17. ** 当前仅支持结汇方向，购汇方向提示错误信息：“当前结构性掉期仅支持结汇方向”
