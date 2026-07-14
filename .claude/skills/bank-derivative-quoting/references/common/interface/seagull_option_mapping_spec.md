# 海鸥期权脚本调用映射（seagull_option）

> **本文件内容将注册到上下文中，供 skill 执行时引用。**
> 
> **使用方式：当用户调用 `seagull_option_XXX` 时，直接执行对应的脚本命令。**
>
> **脚本参数从上下文中获取（用户输入 + 对话历史 + 已加载的参考资料）。**

---

## 触发条件

当用户输入中**包含调用 seagull_option_XXX 的意图**时触发，例如：
- "调用 seagull_option_term_only"
- "使用 seagull_option_term_with_currency"
- "执行 seagull_option_term_with_desired_strikes"
- "帮我跑一下 seagull_option_term_with_two_desired_strikes"

---

## 执行方式

1. **识别类型**：从用户输入中识别 `seagull_option_XXX`（描述性名称）
2. **获取参数**：从当前上下文中获取该类型所需的参数
3. **执行脚本**：生成并执行对应的 Python 脚本命令
4. **返回结果**：直接返回脚本输出的字符串

## 1. 类型定义

| 类型 | 场景说明 |
|------|----------|
| seagull_option_term_only | 只有日期/期限，没有货币对 |
| seagull_option_term_with_currency | 指定了期限，指定了货币对 |
| seagull_option_term_with_desired_strikes | 指定了期限和期望执行价 |
| seagull_option_term_with_desired_strikes_and_currency | 指定了期限、期望执行价和货币对 |
| seagull_option_term_with_prem_pips | 指定了期限和期望收益点数 |
| seagull_option_term_with_prem_pips_and_currency | 指定了期限、期望收益点数和货币对 |
| seagull_option_term_with_strikes_and_pips | 同时指定执行价和期望收益点数 |
| seagull_option_term_with_two_desired_strikes | 两个期望执行价 |
| seagull_option_term_with_two_prem_pips | 两个期望收益点数 |
| seagull_option_term_with_delta | Delta反算（激进/保守） |
| seagull_option_term_with_direction | 指定期限和方向 |
| seagull_option_term_with_direction_and_currency | 指定期限、方向和货币对 |
| seagull_option_term_with_profit | 使用中收参数（profit） |
| seagull_option_term_with_profit_and_currency | 使用中收参数，指定货币对 |
| seagull_option_delivery_date_only | 使用具体交割日期 |
| seagull_option_delivery_date_with_currency | 使用具体交割日期和货币对 |
