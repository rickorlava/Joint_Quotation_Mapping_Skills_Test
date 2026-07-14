# 实时期权脚本调用映射（vanilla_option）

> **本文件内容将注册到上下文中，供 skill 执行时引用。**

> **使用方式：当用户调用具体的场景类型时，直接执行对应的脚本命令。**

> **脚本参数从上下文中获取（用户输入 + 对话历史 + 已加载的参考资料）。**

---

## 触发条件

当用户输入中**包含调用普通期权报价的意图**时触发，例如：
- "调用 common_vanilla_option_term_only 场景"
- "使用 common_vanilla_option_term_with_strike_and_currency"
- "执行 common_vanilla_option_delta_reverse"
- "帮我跑一下 common_vanilla_option_profit_with_direction_and_call_put"

---

## 执行方式

1. **识别类型**：从用户输入中识别具体的场景类型名称
2. **获取参数**：从当前上下文中获取该类型所需的参数
3. **执行脚本**：生成并执行对应的 Python 脚本命令
4. **返回结果**：直接返回脚本输出的字符串

## 1. 类型定义

| 类型 | 场景说明 |
|------|----------|
| common_vanilla_option_term_only | 只有日期/期限，没有货币对 |
| common_vanilla_option_term_with_currency | 指定了期限，指定了货币对 |
| common_vanilla_option_term_with_currency_and_direction | 指定了期限、货币对和买卖方向 |
| common_vanilla_option_term_with_currency_direction_call_put | 指定了期限、货币对、买卖方向和看涨看跌 |
| common_vanilla_option_term_with_strike | 只有期望执行价，没有货币对 |
| common_vanilla_option_term_with_strike_and_currency | 指定了期限和期望执行价，有货币对 |
| common_vanilla_option_term_with_strike_currency_direction | 指定了期限、执行价和买卖方向 |
| common_vanilla_option_term_with_strike_currency_direction_call_put | 指定了期限、执行价、买卖方向和看涨看跌 |
| common_vanilla_option_term_with_yield | 只有期望收益率，没有货币对 |
| common_vanilla_option_term_with_yield_and_currency | 指定了期限和期望收益率，有货币对 |
| common_vanilla_option_term_with_yield_and_direction | 指定了期限、收益率和买卖方向 |
| common_vanilla_option_term_with_yield_direction_call_put | 指定了期限、收益率、买卖方向和看涨看跌 |
| common_vanilla_option_delta_reverse | Delta反算（激进/保守） |
| common_vanilla_option_profit_only | 使用中收参数（profit） |
| common_vanilla_option_profit_with_direction | 使用中收参数，指定买卖方向 |
| common_vanilla_option_profit_with_direction_and_call_put | 使用中收参数，指定买卖方向和看涨看跌 |

---
