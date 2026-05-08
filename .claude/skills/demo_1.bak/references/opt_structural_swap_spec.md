# 结构性掉期报价 Agent 规格说明书

## 快速判断流程（Agent 必须按此流程执行）

```
1. 用户提及"执行价"、"行权价"、"K值" → 使用场景2（期望执行价模式）
2. 用户提及具体日期或期限（如"1个月"、"3个月"）→ 使用场景1（传统模式）
3. 两者都没有提供 → 使用场景1（传统模式），脚本会自动使用默认参数
```

**重要提醒**：
- 只需要执行一次脚本，不要反复尝试
- 场景判断基于用户输入的**关键词**，不是基于报价结果
- 如果无法判断，就用传统模式（最简单的参数组合）

---

## 1. 两种报价场景

脚本支持两种报价场景，Agent 需要根据用户输入判断使用哪种场景：

### 场景 1：传统模式（指定交割日）

用户提供了**具体的交割日期或期限**，需要获取对应的执行价。

**判断条件**：用户提及具体的日期（如"2024-12-12"）或期限（如"1个月"、"3个月"）

**脚本参数**：
```bash
# 使用具体日期（近端默认T+0，只需要填写远端日期）
python bank-derivative-quoting/scripts/opt_structured_swap_query.py --far-settle-date <远端日期>

# 使用期限（自动解析为交割日）
python bank-derivative-quoting/scripts/opt_structured_swap_query.py --term 1M
```

### 场景 2：期望执行价模式

用户提供了**期望的执行价**，需要找到最接近该执行价的期权。

**判断条件**：用户提及"执行价"、"行权价"、"K值"等

**脚本参数**：
```bash
python bank-derivative-quoting/scripts/opt_structured_swap_query.py --target-strike 7.2
```

## 2. 参数提取规则

### 2.0 标准输入格式

用户输入可能采用标准格式：`产品 币种 期限 中收 方向 产品报价`

**输入示例**：
```
结构性掉期 USDCNY 3M 100pips 结汇 产品报价
结构性掉期 EURCNY 6M 50 结汇 产品报价
结构性掉期 USDCNY 1M  结汇 产品报价
```

**字段映射规则**：

| 输入位置 | 字段名 | 脚本参数 | 说明 | 提取方式 |
|---------|--------|---------|------|---------|
| 第1个词 | 产品 | - | 固定为"结构性掉期" | 固定值，用于区分产品类型 |
| 第2个词 | 币种 | `--currency-pair` | 货币对代码 | 直接取值，如 USDCNY, EURCNY |
| 第3个词 | 期限 | `--term` 或 `--far-settle-date` | 锁汇期限 | 支持：1W, 1M, 3M, 6M, 1Y 或具体日期 |
| 第4个词 | 中收 | `--profit` | 中收点数(pips) | 可选，如"100pips"提取100，"50"提取50 |
| 第5个词 | 方向 | `--settle-purchase` | 结汇/购汇方向 | 结汇→settle（仅支持结汇） |
| 第6个词 | 产品报价 | - | 固定标识 | 固定为"产品报价"，用于校验格式 |

**注意**：
- 中收和方向为可选字段，如不提供则使用默认值
- 如果用户未指定币种，默认使用 USDCNY
- 结构性掉期仅支持结汇方向

### 2.1 userId（用户ID）

- **脚本参数**：`--user-id`
- **必须提取**：userId 是调用报价接口的必填参数
- **获取方式**：从记忆系统（memory）中获取用户ID

### 2.2 货币对

- **脚本参数**：`--currency-pair`
- **用户指定**：提取用户输入的货币对（如 EURCNY）
- **未指定**：**不需要**输出`--currency_pair`参数，脚本会自动使用默认值`USDCNY`进行请求，并在输出备注中说明"因您未指定货币对，以上报价基于 USDCNY"

**判断逻辑**：
- 如果用户输入中指定了货币对 → 使用用户指定的货币对
- 如果用户未指定货币对 → 使用默认 `USDCNY`，报价会附带备注说明

### 2.3 方向

- **脚本参数**：`--settle-purchase`
- **仅支持结汇方向 (settle)**，默认按结汇处理

### 2.4 日期

- **脚本参数**：`--near-settle-date`、`--far-settle-date`、`--term`
- **日期/期限参数**：
  - **近端交割日**：**一般不需要输入**，脚本默认按照 T+0（即期）进行报价
  - **远端交割日**：用户指定具体日期或期限（1W/1M/3M/6M/1Y）
- **参数说明**：
  - 使用 `--near-settle-date` 指定近端交割日（通常不需要填写）
  - 使用 `--far-settle-date` 指定远端交割日
  - 使用 `--term` 参数指定期限（如 `3M`），脚本会自动查询对应的远端交割日
  - **可以只填期限，也可以同时指定具体日期和期限**
  - **如果同时填写，脚本会默认按照 term 的日期进行报价**（优先级：term > far-settle-date）
- **远端日期验证**：
  - **如果远端日期小于 1W（1周）**，脚本会返回错误提示
  - 此时需要使用 `chat` 类型返回以下信息：
    ```
    <<<TYPE_START>>> chat <<<TYPE_END>>>
    <<<CONTENT_START>>>
    结构性掉期，远端交割日不能小于1W
    <<<CONTENT_END>>>
    ```

### 2.5 执行价

- **脚本参数**：`--target-strike`（期望执行价模式）
- **传统模式**：从脚本返回结果中获取
- **期望执行价模式**：使用用户指定的期望执行价（`--target-strike`）

### 2.6 中收参数（通用参数）

- **脚本参数**：`--profit`
- 中收是所有场景都可以使用的通用参数。如果用户输入中提及"中收"或"pips"，需要提取数字部分并传递给 `--profit` 参数。

**提取规则**：

| 用户输入 | 转换为 profit | 说明 |
|---------|-------------|------|
| "中收100pips" | 100 | 提取"中收"后面的数字 |
| "中收100" | 100 | 提取"中收"后面的数字 |
| "100pips" | 100 | 提取pips前面的数字 |
| "100 pips" | 100 | 提取pips前面的数字 |
| "中收50到100pips" | 50 100 | 双边输入，提取范围 |

**关键词识别**：
- "中收" + 数字 + "pips"
- 数字 + "pips" / "pips"
- "中收" + 数字


## 3. 脚本调用示例

```bash
# 场景1：传统模式 - 指定期限
# 使用 --term 指定期限（自动查询对应交割日），指定货币对
python bank-derivative-quoting/scripts/opt_structured_swap_query.py --user-id {userId} --term 1M --currency-pair USDCNY
# 用户未指定货币对时（脚本自动使用 USDCNY，输出会备注）：
python bank-derivative-quoting/scripts/opt_structured_swap_query.py --user-id {userId} --term 1M

# 场景1：传统模式 - 指定具体日期
# 使用 --far-settle-date 指定远端日期（近端默认T+0，不需要填写）
python bank-derivative-quoting/scripts/opt_structured_swap_query.py --user-id {userId} --far-settle-date 2026-05-20 --currency-pair EURCNY
# 用户未指定货币对时：
python bank-derivative-quoting/scripts/opt_structured_swap_query.py --user-id {userId} --far-settle-date 2026-05-20

# 场景2：期望执行价模式
python bank-derivative-quoting/scripts/opt_structured_swap_query.py --user-id {userId} --target-strike 7.2 --currency-pair USDCNY
# 用户未指定货币对时：
python bank-derivative-quoting/scripts/opt_structured_swap_query.py --user-id {userId} --target-strike 7.2

# 使用中收参数（profit）
python bank-derivative-quoting/scripts/opt_structured_swap_query.py --user-id {userId} --term 1M --currency-pair USDCNY --profit 100
# 用户未指定货币对时：
python bank-derivative-quoting/scripts/opt_structured_swap_query.py --user-id {userId} --term 1M --profit 100

# 日期参数同时提供时，以 term 为准
python bank-derivative-quoting/scripts/opt_structured_swap_query.py --user-id {userId} --near-settle-date 2026-04-01 --far-settle-date 2026-05-20 --term 1M  # 实际使用 term=1M 的日期
```

**参数说明**：

| 参数 | 必填 | 说明 |
|-----|------|------|
| `--user-id` | 是 | 用户ID |
| `--currency-pair` | 否 | 货币对（如 USDCNY、EURCNY），未指定时默认 USDCNY |
| `--term` | 否 | 期限（1W、1M、3M、6M、1Y），与 `--far-settle-date` 二选一 |
| `--far-settle-date` | 否 | 远端交割日期，与 `--term` 二选一 |
| `--near-settle-date` | 否 | 近端交割日期，未指定时默认 T+0 |
| `--target-strike` | 否 | 期望执行价，使用此参数时为期望执行价模式 |
| `--profit` | 否 | 中收点数（pips） |
| `--settle-purchase` | 否 | 方向：settle（结汇）或 purchase（购汇），默认 settle |

## 4. 输出格式

> **⚠️ 重要说明**：
> - **脚本执行成功后，直接返回脚本输出信息，不需要额外进行组装**
> - 脚本已经按照规定格式组装好完整输出，直接返回即可

### 错误输出

```
<<<TYPE_START>>> error <<<TYPE_END>>>
<<<CONTENT_START>>>
**查询失败**：{错误信息}
<<<CONTENT_END>>>
```

### 节假日/未开市输出

当接口返回节假日或未开市错误时，使用 `chat` 类型返回业务提示信息：

**未开市（当前未开市）**：
```
<<<TYPE_START>>> chat <<<TYPE_END>>>
<<<CONTENT_START>>>
当前未开市，工作日开市时间为：9:30-03:00，请您在工作时间内再来询价
<<<CONTENT_END>>>
```

**节假日（当前日期为节假日）**：
```
<<<TYPE_START>>> chat <<<TYPE_END>>>
<<<CONTENT_START>>>
当前日期为节假日，不支持报价，请输入非节假日进行询价
<<<CONTENT_END>>>
```

### 报价表格字段（脚本输出字段映射）

| 脚本输出字段        | 说明                         |
|---------------|----------------------------|
| 货币对        | 货币对代码（如 USDCNY）            |
| 结汇/购汇方向    | 结汇或购汇                      |
| T+0结汇汇率    | 近端T+0结汇汇率                  |
| 较即期提升点数    | 较即期提升的点数                   |
| 远端交割日      | 远端交割日期                     |
| 远端或有汇率     | 远端或有汇率                     |
| 掉期年化收益率（%） | 掉期年化收益率（单位：%）              |
| 中收         | 如果脚本输出中包含中收字段就返回，否则不返回这个字段 |

## 5. 注意事项

> **关键提醒：只执行一次脚本，不要反复调用！**

1. **只执行一次脚本**：报价脚本只需要执行一次，脚本会自动根据输入参数判断使用哪种场景
2. **直接返回脚本输出**：脚本执行成功后，直接返回脚本输出的字符串，**不需要额外进行组装**
3. **批量报价**：如果脚本返回多行报价信息，全部在表格中返回
4. **常见错误**：
   - 反复用不同参数执行脚本 → 错误！应该回头检查参数提取是否正确
   - 执行脚本后查看输出再决定要不要再执行一次 → 错误！脚本已经返回了所有可用报价
   - 正确做法：仔细阅读用户输入，提取所有参数，一次性执行，直接返回脚本输出