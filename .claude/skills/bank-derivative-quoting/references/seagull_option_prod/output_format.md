# 海鸥期权追问与输出契约

## 0. 文档定位
本文件定义海鸥期权报价 agent 的 **追问条件、输出块与契约 checklist**。组合与预算见 `agent_output/quotation_format.md`。

## 1. 追问

仅在以下情形 `chat`: `term` 与 `delivery_date` 皆缺;方向无法判定且默认有歧义;一价多义(执行价 vs 结果目标);目标过泛;组合预计超 6 次。

模板:

```
<<<TYPE_START>>> chat <<<TYPE_END>>>
<<<CONTENT_START>>>
{追问内容}
<<<CONTENT_END>>>
```

## 2. 输出类型

- 报价:`<<<TYPE_START>>> price <<<TYPE_END>>>`
- 错误:`<<<TYPE_START>>> error <<<TYPE_END>>>`
- 补充/协商:`<<<TYPE_START>>> chat <<<TYPE_END>>>`

单次:脚本字符串 **透传**,不二次拼装。组合:并入单表,置于 `price` 块。

错误体:

```
<<<TYPE_START>>> error <<<TYPE_END>>>
<<<CONTENT_START>>>
**查询失败**:{错误信息}
<<<CONTENT_END>>>
```

未开市:

```
<<<TYPE_START>>> chat <<<TYPE_END>>>
<<<CONTENT_START>>>
当前未开市,工作日开市时间为:9:30-03:00,请您在工作时间内再来询价
<<<CONTENT_END>>>
```

节假日:

```
<<<TYPE_START>>> chat <<<TYPE_END>>>
<<<CONTENT_START>>>
当前日期为节假日,不支持报价,请输入非节假日进行询价
<<<CONTENT_END>>>
```

## 3. 契约 checklist

1. 每调一次须独立语义;禁试错式微调
2. 组合总调用 ≤6,超限先协商
3. 组合前先写调用计划再执行
4. 单次透传;组合单表汇总
5. 产品锚:「海鸥期权」「产品报价」
6. `term` 可自由期限
7. 日期:`term` 优先于 `delivery_date`
8. 默认:币种 `USDCNY`,方向 `settle`
9. `user_id` 仅 memory
10. 未开市/节假日用「2. 输出类型」所列原文
11. 六字段格式仅兼容,不推广
