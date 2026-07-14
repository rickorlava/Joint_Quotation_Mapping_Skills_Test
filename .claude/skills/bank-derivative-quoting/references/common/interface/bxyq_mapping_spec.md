# 倍享远期脚本调用接口（bxyq_query.py — 标准脚本）

> **本文件内容将注册到上下文中，供 skill 执行时引用。**

> **使用方式：当用户调用具体的场景类型时，直接执行对应的脚本命令。**

> **脚本参数从上下文中获取（用户输入 + 对话历史 + 已加载的参考资料）。**

---

## 触发条件

当用户输入中**包含调用倍享远期报价的意图**时触发，例如：
- "调用 bxyq_term_only 场景"
- "使用 bxyq_term_with_currency"
- "执行 bxyq_term_with_leverage"
- "帮我跑一下 bxyq_term_with_currency_and_direction"
- "查询倍享远期报价"

---

## 执行方式

1. **识别类型**：从用户输入中识别具体的场景类型名称
2. **获取参数**：从当前上下文中获取该类型所需的参数
3. **执行脚本**：生成并执行对应的 Python 脚本命令
4. **返回结果**：直接返回脚本输出的字符串

---

## 1. 类型定义

| 类型 | 场景说明 |
|------|----------|
| bxyq_term_only | 只有期限，使用默认货币对和方向 |
| bxyq_term_with_currency | 指定期限 + 货币对 |
| bxyq_term_with_direction | 指定期限 + 方向（结汇/购汇） |
| bxyq_term_with_currency_and_direction | 指定期限 + 货币对 + 方向 |
| bxyq_term_with_leverage | 指定期限 + 杠杆倍数 |
| bxyq_term_with_leverage_and_profit | 指定期限 + 杠杆倍数 + 中收（反算） |
| bxyq_delivery_date_only | 具体交割日期，使用默认货币对和方向 |
| bxyq_delivery_date_with_currency | 具体交割日期 + 货币对 |
| bxyq_delivery_date_with_currency_and_direction | 具体交割日期 + 货币对 + 方向 |
| bxyq_delivery_date_with_leverage | 具体交割日期 + 杠杆倍数 |
| bxyq_delivery_date_with_leverage_and_profit | 具体交割日期 + 杠杆倍数 + 中收（反算） |
| bxyq_forward_calc | 正算场景：指定期限 + 杠杆倍数 + 约定汇率 |
| bxyq_multi_term | 多期限查询 |

---

## 2. 类型与脚本对应表

| 类型 | 调用脚本 | 场景说明 |
|------|----------|----------|
| bxyq_term_only | `python scripts/bxyq_query.py --user-id {userId} --term {term}` | 只有期限，使用默认货币对和方向 |
| bxyq_term_with_currency | `python scripts/bxyq_query.py --user-id {userId} --term {term} --currency-pair {currencyPair}` | 指定期限 + 货币对 |
| bxyq_term_with_direction | `python scripts/bxyq_query.py --user-id {userId} --term {term} --settle-purchase {settlePurchase}` | 指定期限 + 方向（结汇/购汇） |
| bxyq_term_with_currency_and_direction | `python scripts/bxyq_query.py --user-id {userId} --term {term} --currency-pair {currencyPair} --settle-purchase {settlePurchase}` | 指定期限 + 货币对 + 方向 |
| bxyq_term_with_leverage | `python scripts/bxyq_query.py --user-id {userId} --term {term} --leverage {leverage}` | 指定期限 + 杠杆倍数 |
| bxyq_term_with_leverage_and_profit | `python scripts/bxyq_query.py --user-id {userId} --term {term} --leverage {leverage} --profit {profit}` | 指定期限 + 杠杆倍数 + 中收（反算） |
| bxyq_delivery_date_only | `python scripts/bxyq_query.py --user-id {userId} --delivery-date {deliveryDate}` | 具体交割日期，使用默认货币对和方向 |
| bxyq_delivery_date_with_currency | `python scripts/bxyq_query.py --user-id {userId} --delivery-date {deliveryDate} --currency-pair {currencyPair}` | 具体交割日期 + 货币对 |
| bxyq_delivery_date_with_currency_and_direction | `python scripts/bxyq_query.py --user-id {userId} --delivery-date {deliveryDate} --currency-pair {currencyPair} --settle-purchase {settlePurchase}` | 具体交割日期 + 货币对 + 方向 |
| bxyq_delivery_date_with_leverage | `python scripts/bxyq_query.py --user-id {userId} --delivery-date {deliveryDate} --leverage {leverage}` | 具体交割日期 + 杠杆倍数 |
| bxyq_delivery_date_with_leverage_and_profit | `python scripts/bxyq_query.py --user-id {userId} --delivery-date {deliveryDate} --leverage {leverage} --profit {profit}` | 具体交割日期 + 杠杆倍数 + 中收（反算） |
| bxyq_forward_calc | `python scripts/bxyq_query.py --user-id {userId} --term {term} --leverage {leverage} --contract-strike {contractStrike} --reverse-calc false` | 正算场景：指定期限 + 杠杆倍数 + 约定汇率 |
| bxyq_multi_term | `python scripts/bxyq_query.py --user-id {userId} --terms {terms} --leverage {leverage}` | 多期限查询 |

---

## 3. 参数说明

### 3.1 必填参数

| 参数名 | 参数说明 | 有效值 |
|--------|----------|--------|
| userId | 用户 ID | 系统分配的用户标识 |
| term | 期限 | 1W, 1M, 2M, 3M, 6M, 9M, 1Y 等 |
| deliveryDate | 交割日期 | YYYY-MM-DD 格式 |

### 3.2 可选参数

| 参数名 | 参数说明 | 默认值 | 有效值 |
|--------|----------|--------|--------|
| currencyPair | 货币对 | USDCNY | USDCNY, USDCNH, EURCNY, EURCNH, JPYCNY, HKDCNY |
| settlePurchase | 结汇/购汇方向 | settle | settle(结汇), purchase(购汇) |
| leverage | 杠杆倍数 | 2 | 1-10，最多6位小数 |
| profit | 预期中收（pips） | 0 | 大于等于0的数字 |
| contractStrike | 约定汇率 | - | 大于0的数字（正算时必填） |
| reverseCalc | 计算模式 | true | true(反算), false(正算) |
| needRiskReserve | 风险准备金 | true(购汇)/false(结汇) | true, false |

### 3.3 多期限参数

| 参数名 | 参数说明 | 格式示例 |
|--------|----------|----------|
| terms | 多期限列表 | "1M,3M,6M" |
| deliveryDates | 多交割日期列表 | "2026-09-12,2026-12-12" |
| profits | 多中收列表 | "50,60,70" |

---

## 4. 输出字段含义

### 4.1 反算场景字段（reverseCalc=true）

| 字段 | 含义 | 说明 |
|------|------|------|
| currencyPair | 货币对 | -- |
| settlePurchase | 交易方向 | settle-结汇, purchase-购汇 |
| deliveryDate | 交割日 | -- |
| maturityDate | 到期日 | -- |
| leverage | 杠杆倍数 | -- |
| optimalForwardPrice | 优化汇率 | 反算得到的优化远期汇率 |
| profitLimit | 建议中收上限 | -- |
| profit | 中收 | 根据用户权限决定是否显示 |
| contractStrike | 约定汇率 | -- |
| riskReserve | 风险准备金 | -- |

### 4.2 正算场景字段（reverseCalc=false）

| 字段 | 含义 | 说明 |
|------|------|------|
| currencyPair | 货币对 | -- |
| settlePurchase | 交易方向 | settle-结汇, purchase-购汇 |
| deliveryDate | 交割日 | -- |
| maturityDate | 到期日 | -- |
| leverage | 杠杆倍数 | -- |
| contractStrike | 正算K | 约定的结汇/购汇价格 |
| directOptionPrice | 正算期权 | -- |
| directProfit | 正算中收 | 根据用户权限决定是否显示 |
| riskReserve | 风险准备金 | -- |

---

## 5. 场景示例

### 场景1 - 默认AIBP兜底对比
```bash
python scripts/bxyq_query.py --user-id 000000 --delivery-date 2026-12-12
```

### 场景2 - 单期限、杠杆倍数、中收（反算）
```bash
python ../../../scripts/bxyq_query.py --user-id 000000 --delivery-date 2026-12-11 --leverage 3 --profit 50
```

### 场景3 - 使用期限格式
```bash
python ../../../scripts/bxyq_query.py --user-id 000000 --term 3M --leverage 2
```

### 场景4 - 指定货币对
```bash
python ../../../scripts/bxyq_query.py --user-id 000000 --currency-pair EURCNY --delivery-date 2026-12-11
```

### 场景5 - 购汇方向
```bash
python ../../../scripts/bxyq_query.py --user-id 000000 --settle-purchase purchase --delivery-date 2026-12-12 --leverage 2
```

### 场景6 - 多期限查询
```bash
python ../../../scripts/bxyq_query.py --user-id 000000 --terms 1M,3M,6M --leverage 2
```

---

## 6. 注意事项

1. **货币对校验**：倍享远期仅支持 USDCNY, USDCNH, EURCNY, EURCNH, JPYCNY, HKDCNY
2. **杠杆倍数限制**：杠杆倍数范围为 1-10，最多支持6位小数
3. **正算模式要求**：正算模式（reverseCalc=false）时，必须提供约定汇率（contract-strike）
4. **中收显示**：中收字段的显示取决于用户的权限配置
5. **风险准备金**：购汇方向默认需要风险准备金，结汇方向默认不需要
6. **期限解析**：支持期限格式（如 1W, 1M, 3M）和具体日期格式（YYYY-MM-DD）