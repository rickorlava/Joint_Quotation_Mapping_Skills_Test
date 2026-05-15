# 标准掉期脚本调用映射（common_swap）

> **本文件内容将注册到上下文中，供 skill 执行时引用。**
>
> **使用方式：当用户调用具体的场景类型时，直接执行对应的脚本命令。**
>
> **脚本参数从上下文中获取（用户输入 + 对话历史 + 已加载的参考资料）。**

---

## 触发条件

当用户输入中**包含调用掉期报价的意图**时触发，例如：
- "调用 common_swap_near_date_only 场景"
- "使用 common_swap_near_date_with_currency"
- "执行 common_swap_direction_with_near_date"
- "帮我跑一下 common_swap_full_params"

---

## 执行方式

1. **识别类型**：从用户输入中识别具体的场景类型名称
2. **获取参数**：从当前上下文中获取该类型所需的参数
3. **执行脚本**：生成并执行对应的 Python 脚本命令
4. **返回结果**：直接返回脚本输出的字符串

## 1. 类型定义

| 类型 | 场景说明 |
|------|----------|
| common_swap_near_date_only | 只有近端交割日，没有远端交割日，没有货币对 |
| common_swap_near_and_far_date | 同时有近端和远端交割日，没有货币对 |
| common_swap_near_date_with_currency | 有近端交割日，指定货币对 |
| common_swap_near_and_far_date_with_currency | 同时有近端和远端交割日，指定货币对 |
| common_swap_near_date_with_amount | 有近端交割日，指定名义本金 |
| common_swap_near_and_far_date_with_amount | 同时有近端和远端交割日，指定名义本金 |
| common_swap_near_date_with_amount_and_currency | 有近端交割日，指定名义本金和货币对 |
| common_swap_near_and_far_date_with_amount_and_currency | 同时有近端和远端交割日，指定名义本金和货币对 |
| common_swap_direction_only | 只有买卖方向，没有交割日 |
| common_swap_direction_with_near_date | 有买卖方向和近端交割日 |
| common_swap_direction_with_near_and_far_date | 有买卖方向、近端和远端交割日 |
| common_swap_full_params | 完整参数：买卖方向、近端/远端交割日、名义本金、货币对 |