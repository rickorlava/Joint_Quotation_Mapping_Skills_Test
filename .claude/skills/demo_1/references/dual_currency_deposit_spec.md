# 双货币存款报价 Agent 规格说明书

## 快速判断流程（Agent 必须按此流程执行）

```
1. 用户提及"激进"、"保守"、"Delta" → 场景7
2. 用户提及两个执行价（如"7.1到7.3"）→ 场景5
3. 用户提及两个收益率（如"2%到5%"）→ 场景6
4. 用户同时提及执行价和收益率 → 场景4
5. 用户只提及执行价 → 场景2
6. 用户只提及收益率 → 场景3
7. 用户只提供日期 → 场景1
```

**重要提醒**：
- 只需要执行一次脚本，不要反复尝试
- 场景判断基于用户输入的**关键词**，不是基于报价结果
- 如果无法判断，就用场景1（最简单的参数组合）

---

## 1. 七种报价场景

脚本支持七种报价场景，Agent 需要根据用户输入判断使用哪种场景：

| 场景 | 用户输入 | 脚本参数 |
|------|----------|----------|
| 场景1 | 只有日期 | 无 strike/yield/delta |
| 场景2 | 只有期望执行价 | 1个 strike |
| 场景3 | 只有期望收益率 | 1个 yield |
| 场景4 | 执行价+收益率 | 1个 strike + 1个 yield |
| 场景5 | 两个期望执行价 | 2个 strike |
| 场景6 | 两个期望收益率 | 2个 yield |
| 场景7 | Delta（激进/保守） | 1个 delta |

> **通用参数**：如果用户提及"中收"或"pips"，需要同时传递 `--initial_profit` 参数。

### 场景判断规则

1. **场景1（只传日期）**：用户只提供交割日期或期限，无执行价、收益率、Delta 信息
2. **场景2（期望执行价）**：用户提及"执行价"、"行权价"、"K值"
3. **场景3（期望收益率）**：用户提及"收益率"、"补贴"、"年化收益"、"多少%"
4. **场景4（执行价+收益率）**：同时提供执行价和收益率 → **双边输入，脚本自动计算5个梯度报价**
5. **场景5（两个执行价）**：用户提供执行价范围，如"7.1到7.3" → **双边输入，脚本自动计算5个梯度报价**
6. **场景6（两个收益率）**：用户提供收益率范围，如"2%到5%" → **双边输入，脚本自动计算5个梯度报价**
7. **场景7（Delta）**：用户提及"激进"、"保守"、"Delta"，或者表达观点如"想要更高收益"、"想要风险小一点"等
    - **激进**：用户表示"想要更高收益"、"不怕风险"、"增加收益"等
    - **保守**：用户表示"想要风险小一点"、"降低风险"、"减少收益"等

> **场景4/5/6 说明**：这三个场景都是双边情形，只需要输入两个边界参数（如执行价7.1和7.3，或收益率2%和5%），脚本会自动在区间内计算5个梯度的报价供用户选择。

## 2. 参数提取规则

### 2.0 标准输入格式

用户输入可能采用标准格式：`产品 币种 期限 中收 方向 产品报价`

**输入示例**：
```
双货币存款 USDCNY 3M 100pips 结汇 产品报价
双货币存款 EURCNY 6M 50 购汇 产品报价
双货币存款 USDCNY 1M  结汇 产品报价
```

**字段映射规则**：

| 输入位置 | 字段名 | 脚本参数 | 说明 | 提取方式 |
|---------|--------|---------|------|---------|
| 第1个词 | 产品 | - | 固定为"双货币存款" | 固定值，用于区分产品类型 |
| 第2个词 | 币种 | `--currency_pair` | 货币对代码 | 直接取值，如 USDCNY, EURCNY；不指定时使用默认值 USDCNY |
| 第3个词 | 期限 | `--term` | 存款期限 | 支持：1W, 1M, 3M, 6M, 1Y 或具体日期 |
| 第4个词 | 中收 | `--initial_profit` | 中收点数(pips) | 可选，如"100pips"提取100，"50"提取50 |
| 第5个词 | 方向 | `--settle_purchase` | 结汇/购汇方向 | 结汇→settle，购汇→purchase |
| 第6个词 | 产品报价 | - | 固定标识 | 固定为"产品报价"，用于校验格式 |

**注意**：
- 中收和方向为可选字段，如不提供则使用默认值
- 如果用户未指定币种，默认使用 USDCNY，且会在输出中备注"因您未指定货币对，以上报价基于 USDCNY"
- 默认方向为结汇(settle)

### 2.1 userId（用户ID）

- **脚本参数**：`--user_id`
- **必须提取**：userId 是调用报价接口的必填参数
- **获取方式**：从记忆系统（memory）中获取用户ID

### 2.2 货币对

- **脚本参数**：`--currency_pair`
- **用户指定**：提取用户输入的货币对（如 EURCNY）
- **未指定**：**不需要**输出`--currency_pair`参数，脚本会自动使用默认值`USDCNY`进行请求，并在输出备注中说明"因您未指定货币对，以上报价基于 USDCNY"

### 2.3 方向

- **脚本参数**：`--settle_purchase`
- **结汇**：对应 `settle`
- **购汇**：对应 `purchase`
- **未指定**：默认 `settle`

### 2.3 日期/期限

- **脚本参数**：`--delivery_date` 或 `--term`
- **日期/期限参数**：必填参数，用户可提供具体日期或期限（1W/1M/3M/6M/1Y）
- **参数说明**：
    - 使用 `--delivery_date` 参数指定具体日期（如 `2026-04-20`）
    - 使用 `--term` 参数指定期限（如 `3M`），脚本会自动查询对应的交割日
    - **可以只填其中一个，也可以同时填写**
    - **如果同时填写，脚本会默认按照 term 的日期进行报价**（优先级：term > delivery_date）
    - 如果用户未传入日期，那么需要使用`chat` 类型返回以下信息：
       ```
      <<<TYPE_START>>> chat <<<TYPE_END>>>
      <<<CONTENT_START>>>
      请输入交割日期
      <<<CONTENT_END>>>
      ```

### 2.4 期望执行价

- **脚本参数**：`--desired_strikes`
- 期望执行价是指用户希望的行权价格。根据用户输入的汇率预期来提取。

**提取规则**：

| 用户输入 | 转换为 desired_strikes | 说明                    |
|---------|----------------------|-----------------------|
| "人民币不会贬值到7" | 7 | 直接提取数字 |
| "人民币不会升值到7" | 7 | 直接提取数字 |
| "执行价7.0" | 7.0 | 直接提取数字                |
| "行权价7.2" | 7.2 | 直接提取数字                |
| "K值7.5" | 7.5 | 直接提取数字                |
| "7到7.5" | 7 7.5 | 双边输入，表示执行价区间          |

**关键词识别**：
- "执行价" + 数字
- "行权价" + 数字
- "K值" + 数字

### 2.5 期望收益率

- **脚本参数**：`--desired_yields`
- **重要：需要将用户输入的收益率转换为百分比数字**

| 用户输入 | 转换为 desired_yields | 说明 |
|---------|---------------------|------|
| "5%"、"5个点" | 5 | 百分比形式直接取数字部分 |
| "0.05" | 5 | 小数形式乘以100 |
| "0.03"（3%） | 3 | 小数形式乘以100 |
| "年化收益5%" | 5 | 百分比形式直接取数字部分 |
| "想要3.5%的收益" | 3.5 | 百分比形式直接取数字部分 |
| "收益率达到3.4" | 3.4 | 直接提取数字 |
| "期望收益3到5" | 3 5 | 双边输入不带百分号 |

**转换规则**：
- 如果用户输入的是**百分比形式**（如 5%、3.5%），直接取数字部分
- 如果用户输入的是**小数形式**（如 0.05、0.03），乘以100转换为百分比数字
- "收益率达到"、"收益率可以"、"期望收益率"等 + 数字 → 直接提取数字

**关键词识别**：
- "收益率" + 数字
- "收益达到"、"收益可以"
- "年化收益" + 数字
- 数字 + "%"

### 2.6 Delta判断（场景7）

- **脚本参数**：`--delta`
- 用于激进/保守场景，根据用户表达的风险偏好来确定 Delta 值

| 方向 | Delta符号 | 激进 | 保守 |
|------|-----------|------|------|
| 结汇 | 正值 | delta +0.2 | delta -0.15 |
| 购汇 | 负值 | delta -0.2 | delta +0.15 |

### 2.7 中收参数

- **脚本参数**：`--initial_profit`
- 中收是所有场景都可以使用的通用参数。如果用户输入中提及"中收"或"pips"，需要提取数字部分并传递给 `--initial_profit` 参数。

**提取规则**：

| 用户输入 | 转换为 initial_profit | 说明 |
|---------|---------------------|------|
| "中收100pips" | 100 | 提取"中收"后面的数字 |
| "中收100" | 100 | 提取"中收"后面的数字 |
| "100pips" | 100 | 提取pips前面的数字 |
| "100 pips" | 100 | 提取pips前面的数字 |
| "中收50到100pips" | 50 100 | 双边输入，提取范围 |

**关键词识别**：
- "中收" + 数字 + "pips"
- 数字 + "pips" / "pips"
- "中收" + 数字

### 2.8 综合场景示例

用户输入可能包含多个参数，Agent 需要从用户输入中提取所有相关参数：

**示例**：用户输入
```
双货币存款 USDCNY 购汇方向 期限3M 我希望能够收益率可以达到3.4 同时我认为人民币不会贬值到7
```

**参数提取过程**：

| 用户输入关键词 | 对应参数 | 提取结果 |
|--------------|---------|---------|
| "USDCNY" | --currency_pair | USDCNY |
| "购汇方向" | --settle_purchase | purchase |
| "期限3M" | --term | 3M |
| "收益率可以达到3.4" | --desired_yields | 3.4 |
| "人民币不会贬值到7" | --desired_strikes | 7 |

**最终脚本调用**：
```bash
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --currency_pair USDCNY --settle_purchase purchase --term 3M --desired_yields 3.4 --desired_strikes 7
```

**说明**：
- 此场景属于**场景4**（执行价+收益率双边输入），脚本会自动计算5个梯度报价
- 用户同时提供了期望执行价和期望收益率，脚本会在区间内计算多个报价供选择


## 3. 脚本调用示例

```bash
# 场景1：只传日期（标准报价）
# 使用 --delivery_date 指定具体日期
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --delivery_date <日期> --currency_pair USDCNY --settle_purchase settle
# 使用 --term 指定期限（自动查询对应交割日）
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --term 3M --currency_pair USDCNY --settle_purchase settle
# 用户未指定货币对时（默认使用 USDCNY，输出会备注"因您未指定货币对，以上报价基于 USDCNY"）：
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --term 3M --settle_purchase settle

# 场景2：只传期望执行价
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --term 3M --currency_pair USDCNY --settle_purchase settle --desired_strikes 7.2
# 用户未指定货币对时：
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --term 3M --settle_purchase settle --desired_strikes 7.2

# 场景3：只传期望收益率（反算执行价）
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --term 3M --currency_pair USDCNY --settle_purchase settle --desired_yields 3.5
# 用户未指定货币对时：
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --term 3M --settle_purchase settle --desired_yields 3.5

# 场景4：执行价+收益率
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --term 3M --currency_pair USDCNY --desired_strikes 7.2 --desired_yields 3.5

# 场景5：两个期望执行价
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --term 3M --currency_pair USDCNY --desired_strikes 7.1 7.3

# 场景6：两个期望收益率
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --term 3M --currency_pair USDCNY --desired_yields 2 5

# 场景7：Delta（激进/保守）
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --term 3M --currency_pair USDCNY --delta 0.2

# 使用中收参数（initial_profit）
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --term 3M --currency_pair USDCNY --settle_purchase settle --initial_profit 100
# 用户未指定货币对时：
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --term 3M --settle_purchase settle --initial_profit 100

# 日期参数同时提供时，以 term 为准
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --delivery_date <日期> --term 3M  # 实际使用 term=3M 的日期
```

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

| 脚本输出字段      | 说明              |
|---------------|-----------------|
| 货币对           | 货币对代码（如 USDCNY） |
| 结汇/购汇方向       | 结汇或购汇           |
| 期限           | 交割日期            |
| 转换汇率          | 转换汇率            |
| 补贴参考收益率（年化：%） | 补贴参考收益率（年化：%）   |
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