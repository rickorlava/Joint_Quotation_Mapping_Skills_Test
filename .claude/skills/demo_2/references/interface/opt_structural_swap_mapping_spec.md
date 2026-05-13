# 标准结构性掉期脚本调用映射（opt_structured_swap）

> **本文件内容将注册到上下文中，供 skill 执行时引用。**

> **使用方式：当用户调用具体的场景类型时，直接执行对应的脚本命令。**

> **脚本参数从上下文中获取（用户输入 + 对话历史 + 已加载的参考资料）。**

---

## 触发条件

当用户输入中**包含调用结构性掉期报价的意图**时触发，例如：
- "调用 opt_structured_swap_term_with_currency 场景"
- "使用 opt_structured_swap_far_settle_date_with_currency"
- "执行 opt_structured_swap_target_strike_only"
- "帮我跑一下 opt_structured_swap_term_with_profit"

---

## 执行方式

1. **识别类型**：从用户输入中识别具体的场景类型名称
2. **获取参数**：从当前上下文中获取该类型所需的参数
3. **执行脚本**：生成并执行对应的 Python 脚本命令
4. **返回结果**：直接返回脚本输出的字符串

## 1. 类型定义

| 类型 | 场景说明 |
|------|----------|
| opt_structured_swap_term_with_currency | 指定了期限，指定了货币对 |
| opt_structured_swap_term_only | 指定了期限 |
| opt_structured_swap_far_settle_date_with_currency | 指定了远期具体日期，指定了货币对 |
| opt_structured_swap_far_settle_date_only | 指定了远期具体日期 |
| opt_structured_swap_target_strike_with_currency | 指定了期望执行价，指定了货币对 |
| opt_structured_swap_target_strike_only | 指定了期望执行价 |
| opt_structured_swap_term_with_currency_and_profit | 使用中收参数（profit），指定了货币对 |
| opt_structured_swap_term_with_profit | 使用中收参数（profit） |
| opt_structured_swap_both_dates_with_term | 日期参数同时提供，实际使用 term的日期 |
