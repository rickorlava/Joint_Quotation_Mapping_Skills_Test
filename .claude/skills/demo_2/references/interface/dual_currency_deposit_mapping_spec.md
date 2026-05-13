# 双货币存款脚本调用映射（dual_currency_deposit）

> **本文件内容将注册到上下文中，供 skill 执行时引用。**

> **使用方式：当用户调用具体的场景类型时，直接执行对应的脚本命令。**

> **脚本参数从上下文中获取（用户输入 + 对话历史 + 已加载的参考资料）。**

---

## 触发条件

当用户输入中**包含调用双货币存款报价的意图**时触发，例如：
- "调用 dcd_term_only"
- "使用 dcd_term_with_currency"
- "执行 dcd_term_with_strike"
- "帮我跑一下 dcd_term_with_strike_yield_and_currency"

---

## 执行方式

1. **识别类型**：从用户输入中识别具体的场景类型名称
2. **获取参数**：从当前上下文中获取该类型所需的参数
3. **执行脚本**：生成并执行对应的 Python 脚本命令
4. **返回结果**：直接返回脚本输出的字符串

## 1. 类型定义

| 类型 | 场景说明 |
|------|----------|
| dcd_term_only | 只有日期/期限，没有货币对 |
| dcd_term_with_currency | 指定了期限，指定了货币对 |
| dcd_term_with_strike | 只有期望执行价，没有货币对 |
| dcd_term_with_strike_and_currency | 指定了期限和期望执行价 |
| dcd_term_with_yield | 只有期望收益率，没有货币对 |
| dcd_term_with_yield_and_currency | 指定了期限和期望收益率 |
| dcd_term_with_strike_and_yield | 同时有执行价和收益率，没有货币对 |
| dcd_term_with_strike_yield_and_currency | 同时有执行价和收益率，有货币对 |
| dcd_term_with_two_strikes | 两个期望执行价 |
| dcd_term_with_two_yields | 两个期望收益率 |
| dcd_term_with_delta | Delta反算（激进/保守） |
| dcd_term_with_direction | 指定期限和方向 |
| dcd_term_with_direction_and_currency | 指定期限、方向和货币对 |
| dcd_term_with_profit | 使用中收参数（profit） |
| dcd_term_with_profit_and_currency | 使用中收参数，指定货币对 |
| dcd_settle_date_only | 使用具体交割日期 |
| dcd_settle_date_with_currency | 使用具体交割日期和货币对 |