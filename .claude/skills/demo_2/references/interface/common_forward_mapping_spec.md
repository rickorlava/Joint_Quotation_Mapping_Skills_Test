# 标准远期脚本调用映射（common_forward）

> **本文件内容将注册到上下文中，供 skill 执行时引用。**

> **使用方式：当用户调用具体的场景类型时，直接执行对应的脚本命令。**

> **脚本参数从上下文中获取（用户输入 + 对话历史 + 已加载的参考资料）。**

---

## 触发条件

当用户输入中**包含调用正向期权报价的意图**时触发，例如：
- "调用 common_forward_term_only 场景"
- "使用 common_forward_term_with_currency"
- "执行 common_forward_term_with_direction"
- "帮我跑一下 common_forward_settle_date_with_currency_and_direction"

---

## 执行方式

1. **识别类型**：从用户输入中识别具体的场景类型名称
2. **获取参数**：从当前上下文中获取该类型所需的参数
3. **执行脚本**：生成并执行对应的 Python 脚本命令
4. **返回结果**：直接返回脚本输出的字符串

## 1. 类型定义

| 类型 | 场景说明 |
|------|----------|
| common_forward_term_only | 只有日期/期限，没有货币对和方向 |
| common_forward_term_with_currency | 指定了日期/期限，指定了货币对 |
| common_forward_term_with_direction | 指定了日期/期限，指定了方向 |
| common_forward_term_with_currency_and_direction | 指定了日期/期限，指定了货币对和方向 |
| common_forward_currency_only | 只有货币对，没有日期和方向 |
| common_forward_currency_with_direction | 货币对 + 方向，没有日期 |
| common_forward_direction_only | 只有方向，没有日期和货币对 |
| common_forward_settle_date_only | 具体交割日期，没有货币对和方向 |
| common_forward_settle_date_with_currency | 具体交割日期 + 货币对 |
| common_forward_settle_date_with_currency_and_direction | 具体交割日期 + 货币对 + 方向 |