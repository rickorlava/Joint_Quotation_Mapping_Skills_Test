# 倍享远期（BXYQ）产品报价范式

## 0. 文档定位

本文件定义 倍享远期（BXYQ）产品报价 agent 合法报价范式

- 单次求解模式
- 组合求解模式

由 倍享远期的**意图识别**指定到此 区分范式 调用脚本报价

## 1. 标准入参字段

| 字段 | 标签 | 来源 | 说明 |
|------|------|------|------|
| direction | 方向 | 用户输入,默认settle | 结汇(settle) / 购汇(purchase) |
| leverage | 杠杆倍数 | 用户输入 | n，期权本金=(n-1)×远期本金 |
| quoted_rate | 约定汇率 | 反算输出 | 符号 K，即报价结果 |
| profit | 中收 | 用户输入（反算）或正算输出 | 内含于 K 的收益 |
| risk_reserve | 风险准备金 | 计算 | 杠杆倍数 × 基础准备金 |
| currency_pair | 货币对 | 用户输入 | 如 USDCNY 、 USD/CNY |
| delivery_date | 交割日 | 用户输入 | 如 20231212、2026-12-12 |

## 2. 报价范式映射总表

### 2.1 单次求解模式

**场景**: 用户给定期限+方向+币种(+中收/杠杆)，需要输出优化汇率

**输入参数组合**:
| 组合 | 期限 | 方向 | 币种 | 杠杆 | 中收 | 处理逻辑 |
|------|------|------|------|------|------|---------|
| 组合1 | ✓ | ✓ | ✓ | - | - | 基准报价，默认2倍杠杆 |
| 组合2 | ✓ | ✓ | ✓ | ✓ | - | 调整杠杆报价 |
| 组合3 | ✓ | ✓ | ✓ | - | ✓ | 中收反算汇率 |
| 组合4 | ✓ | ✓ | ✓ | ✓ | ✓ | 调整杠杆+中收反算 |

**调用示例**:
```python
# 基准报价
quotation(direction="settle", currency_pair="USDCNY", delivery_date="3M")

# 调整杠杆
quotation(direction="settle", currency_pair="USDCNY", delivery_date="3M", leverage=3)

# 中收反算
quotation(direction="settle", currency_pair="USDCNY", delivery_date="3M", profit=50)
```

### 2.2 组合求解模式

**场景**: 用户已知方向+期限+约定汇率，需要计算中收

**输入参数组合**:
| 组合 | 期限 | 方向 | 币种 | 约定汇率 | 处理逻辑 |
|------|------|------|------|---------|---------|
| 组合1 | ✓ | ✓ | ✓ | ✓ | 组合求解中收 |

**调用示例**:
```python
# 组合求解
profit = calculate_profit(direction="settle", currency_pair="USDCNY", 
                          delivery_date="3M", quoted_rate=6.78)
```

## 3. 标准输出字段

| 输出字段 | 来源字段 | 映射关系 | 说明 |
|---------|---------|---------|------|
| currency_pair | currency_pair | 默认格式为：USDCNY | 请求的货币对 |
| delivery_date | delivery_date | 交割日 | 用户指定的交割日 |
| maturity_date | maturity_date | 期权到期日 | 报价返回的期权到期日 |
| direction | direction | 用户输入：默认结汇 | 交易方向 |
| leverage | leverage | 杠杆倍数 | 用户输入，n，期权本金=(n-1)×远期本金 |
| optimalForwardPrice | optimalForwardPrice | 倍享远期优化结果 | 报价结果 |
| profitLimit | profitLimit | 计算结果，中收上限 | 建议中收上限 |

## 4. 报价格式示例

### 4.1 单次求解输出示例

```json
{
  "currency_pair": "USDCNY",
  "delivery_date": "3M",
  "maturity_date": "2026-10-08",
  "direction": "settle",
  "leverage": 2,
  "optimalForwardPrice": 6.8520,
  "profitLimit": 80
}
```

### 4.2 组合求解输出示例

```json
{
  "currency_pair": "USDCNY",
  "delivery_date": "3M",
  "direction": "settle",
  "quoted_rate": 6.78,
  "profit": 65,
  "profitUnit": "pips"
}
```

## 5. Few-shot 样例集

### A. 基础干净表达

#### 示例 A1: 明确中收的基准报价
用户: "倍享远期,3M结汇USDCNY中收50pips"
处理: 期限 + 方向 + 币种 + 中收 → 走基准报价反算

#### 示例 A2: 基准报价缺失中收
用户: "倍享远期,3M结汇USDCNY"
处理: 只有期限 + 方向 + 币种 → 走基准报价

#### 示例 A3: 调整杠杆
用户: "3M倍享远期,3倍杠杆"
处理: 给定期限 + 方向 + 币种 → 3倍的sell call

#### 示例 A4: 调整期限
用户: "多给几组期限的报价" 或 "我需要6个月的报价"
处理: 只有期限 + 方向 + 币种 → 走基准报价

#### 示例 A5: 调整方向
用户: "倍享远期,3M购汇USDCNY"
处理: 只有期限 + 方向 + 币种 → 走基准报价

#### 示例 A6: 调整币种
用户: "倍享远期,3M购汇EURCNY" 或 "再报一组欧元的价格"
处理: 只有期限 + 方向 + 币种 → 走基准报价

#### 示例 A7: 最终报价
用户: "倍享远期,3M已6.78结汇报价"
处理: 方向、期限、最终报价 → 组合求解

### B. 市场观点表达

（暂无）

## 6. 边界情况处理

| 场景 | 处理方式 |
|------|---------|
| 未指定方向 | 默认结汇(settle) |
| 未指定杠杆 | 默认2倍(n=2) |
| 未指定期限 | 默认3M |
| 中收为负 | 提示输入无效 |
| 约定汇率不合理 | 提示超出合理范围 |