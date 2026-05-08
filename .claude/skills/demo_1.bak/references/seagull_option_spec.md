# 海鸥期权报价 Agent 规格说明书

## 快速判断流程（Agent 必须按此流程执行）

```
1. 用户提及"激进"、"保守"、"Delta" → 场景7
2. 用户提及两个执行价（如"7.0到7.5"）→ 场景5
3. 用户提及两个期望收益点数（如"50点到150点"）→ 场景6
4. 用户同时提及执行价和期望收益点数 → 场景4
5. 用户只提及执行价 → 场景2
6. 用户只提及收益/期权费 → 场景3
7. 用户只提供日期 → 场景1
```

**重要提醒**：
- 只需要执行一次脚本，不要反复尝试
- 场景判断基于用户输入的**关键词**，不是基于报价结果
- 如果无法判断，就用场景1（最简单的参数组合）

---

## 1. 七种报价场景

脚本支持七种报价场景，Agent 需要根据用户输入判断使用哪种场景：

| 场景 | 用户输入         | 脚本参数 |
|------|--------------|----------|
| 场景1 | 只有日期         | 无 strike/prem_pips/delta |
| 场景2 | 只有期望执行价      | 1个 strike |
| 场景3 | 只有期望收益点数     | 1个 prem_pips |
| 场景4 | 执行价+期望收益点数      | 1个 strike + 1个 prem_pips |
| 场景5 | 两个期望执行价      | 2个 strike |
| 场景6 | 两个期望收益点数      | 2个 prem_pips |
| 场景7 | Delta（激进/保守） | 1个 delta |

### 场景判断规则

1. **场景1（只传日期）**：用户只提供交割日期，无执行价、期望收益点数、Delta 信息
2. **场景2（期望执行价）**：用户提及"执行价"、"行权价"、"K值"
3. **场景3（期望收益点数）**：用户提及"期望收益点数"、"补贴"、"期权费"、"多少点"
4. **场景4（执行价+期望收益点数）**：同时提供执行价和期望收益点数 → **双边输入，脚本自动计算5个梯度报价**
5. **场景5（两个执行价）**：用户提供执行价范围，如"7.0到7.5" → **双边输入，脚本自动计算5个梯度报价**
6. **场景6（两个期望收益点数）**：用户提供期望收益点数范围，如"50点到150点" → **双边输入，脚本自动计算5个梯度报价**
7. **场景7（Delta）**：用户提及"激进"、"保守"、"Delta"，或者表达观点如"想要更高收益"、"想要风险小一点"等
   - **激进**：用户表示"想要更高收益"、"不怕风险"、"增加收益"等
   - **保守**：用户表示"想要风险小一点"、"降低风险"、"减少收益"等

> **场景4/5/6 说明**：这三个场景都是双边情形，只需要输入两个边界参数（如执行价7.0和7.5，或期望收益点数50点和150点），脚本会自动在区间内计算5个梯度的报价供用户选择。

## 2. 参数提取规则

### 2.0 标准输入格式

用户输入可能采用标准格式：`产品 币种 期限 中收 方向 产品报价`

**输入示例**：
```
海鸥期权 USDCNY 3M 100pips 结汇 产品报价
海鸥期权 EURCNY 6M 50 购汇 产品报价
海鸥期权 USDCNY 1M  结汇 产品报价
```

**字段映射规则**：

| 输入位置 | 字段名 | 脚本参数 | 说明 | 提取方式 |
|---------|--------|---------|------|---------|
| 第1个词 | 产品 | - | 固定为"海鸥期权" | 固定值，用于区分产品类型 |
| 第2个词 | 币种 | `--currency-pair` / `-c` | 货币对代码 | 直接取值，如 USDCNY, EURCNY |
| 第3个词 | 期限 | `--term` 或 `--delivery-date` | 锁汇期限 | 支持：1W, 1M, 3M, 6M, 1Y 或具体日期 |
| 第4个词 | 中收 | `--profit` | 中收点数(pips) | 可选，如"100pips"提取100，"50"提取50 |
| 第5个词 | 方向 | `--settle-purchase` / `-s` | 结汇/购汇方向 | 结汇→settle(Sell Put)，购汇→purchase(Sell Call) |
| 第6个词 | 产品报价 | - | 固定标识 | 固定为"产品报价"，用于校验格式 |

**注意**：
- 中收和方向为可选字段，如不提供则使用默认值
- 如果用户未指定币种，默认使用 USDCNY
- 默认方向为结汇(settle)

### 2.1 userId（用户ID）

- **脚本参数**：`--user-id` 或 `-u`（必填参数）
- **必须提取**：userId 是调用报价接口的必填参数
- **获取方式**：从记忆系统（memory）中获取用户ID

### 2.2 货币对

- **脚本参数**：`--currency-pair` 或 `-c`
- **用户指定**：提取用户输入的货币对（如 EURCNY、USDCNY）
- **未指定**：默认 `USDCNY`，系统会自动使用该默认货币对进行报价

**判断逻辑**：
- 如果用户显式传入 `--currency-pair` 参数 → 使用用户指定的货币对，输出不备注
- **未指定**：**不需要**输出`--currency_pair`参数，脚本会自动使用默认值`USDCNY`进行请求，并在输出备注中说明"因您未指定货币对，以上报价基于 USDCNY"

### 2.3 方向

- **脚本参数**：`--settle-purchase` 或 `-s`
- **结汇**：对应 `settle`，自动映射为 Sell Put
- **购汇**：对应 `purchase`，自动映射为 Sell Call
- **未指定**：默认 `settle`

### 2.4 日期

- **脚本参数**：`--delivery-date` / `-d`（具体日期）或 `--term` / `-t`（期限）
- **日期/期限参数**：必填参数，用户可提供具体日期或期限（1W/1M/3M/6M/1Y）
- **参数说明**：
  - 使用 `--delivery-date` 参数指定具体日期（如 `2026-04-20`）
  - 使用 `--term` 参数指定期限（如 `3M`），脚本会自动查询对应的交割日
  - **可以只填其中一个，也可以同时填写**
  - **如果同时填写，脚本会默认按照 term 的日期进行报价**（优先级：term > delivery-date）
  - 如果用户未传入日期，那么需要使用`chat` 类型返回以下信息：
     ```
    <<<TYPE_START>>> chat <<<TYPE_END>>>
    <<<CONTENT_START>>>
    请输入交割日期
    <<<CONTENT_END>>>
    ```

### 2.5 期望执行价（desired_strikes）

- **脚本参数**：`--desired-strikes` 或 `-k`
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

### 2.6 期望期望收益点数/期权费（prem_pips）

- **脚本参数**：`--prem-pips` 或 `-p`
- 期望期望收益点数是指用户期望获得的期权费补贴（以 pips 为单位）。

**提取规则**：

| 用户输入 | 转换为 prem_pips | 说明 |
|---------|-----------------|------|
| "补贴超过100点" | 100 | 提取"点"前面的数字 |
| "期权费100点" | 100 | 提取"点"前面的数字 |
| "100点" | 100 | 直接提取pips数字 |
| "100pips" | 100 | 提取pips前面的数字 |
| "期望收益点数50到150点" | 50 150 | 双边输入，表示期望收益点数区间 |

**关键词识别**：
- "补贴" + 数字 + "点"
- "期权费" + 数字 + "点"
- 数字 + "点" / "pips"
- "期望收益点数" + 数字

### 2.7 Delta判断（场景7）

- **脚本参数**：`--delta` 和 `--inverse-type`（设为 `delta`）
- Delta反算场景使用的参数，用于激进/保守策略报价

| 方向 | Delta符号 | 激进         | 保守          |
|------|-----------|------------|-------------|
| 结汇 | 负值 | delta -0.2 | delta +0.15 |
| 购汇 | 正值 | delta +0.2 | delta -0.15 |

### 2.8 中收参数（通用参数）

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

### 2.9 综合场景示例

用户输入可能包含多个参数，Agent 需要从用户输入中提取所有相关参数：

**示例**：用户输入
```
海鸥期权 USDCNY 购汇方向 期限3M 我希望能够补贴我超过100点 同时我认为人民币不会贬值到7
```

**参数提取过程**：

| 用户输入关键词 | 对应参数 | 提取结果 |
|--------------|---------|---------|
| "USDCNY" | --currency-pair | USDCNY |
| "购汇方向" | --settle-purchase | purchase |
| "期限3M" | --term | 3M |
| "补贴我超过100点" | --prem-pips | 100 |
| "人民币不会贬值到7" | --desired-strikes | 7 |

**最终脚本调用**：
```bash
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --currency-pair USDCNY --settle-purchase purchase --term 3M --prem-pips 100 --desired-strikes 7
```

**说明**：
- 此场景属于**场景4**（执行价+期望收益点数双边输入），脚本会自动计算5个梯度报价
- 用户同时提供了期望执行价和期望期望收益点数，脚本会在区间内计算多个报价供选择


## 3. 脚本调用示例

### 3.1 货币对参数使用

```bash
# 指定货币对（输出不备注默认货币对）
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --term 3M --currency-pair EURCNY
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --term 3M -c EURCNY

# 不指定货币对（使用默认 USDCNY，输出会备注）
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --term 3M
# 输出备注：因您未指定货币对，以上报价基于 USDCNY
```

### 3.2 各场景调用示例

```bash
# 场景1：只有日期（基础查询）
# 使用 --delivery-date 指定具体日期
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --delivery-date 2026-04-20
# 使用 --term 指定期限（自动查询对应交割日）
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --term 3M

# 场景2：只传期望执行价
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --term 3M --desired-strikes 7.0

# 场景3：只传期望期望收益点数（pips反算）
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --term 3M --prem-pips 100

# 场景4：同时有期望执行价和期望期望收益点数
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --term 3M --desired-strikes 7.0 --prem-pips 100

# 场景5：两个期望执行价
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --term 3M --desired-strikes 7.0 7.5

# 场景6：两个期望期望收益点数
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --term 3M --prem-pips 50 150

# 场景7：Delta反算
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --term 3M --delta 0.2 --inverse-type delta

# 使用中收参数（profit）
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --term 3M --profit 100

# 日期参数同时提供时，以 term 为准
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --delivery-date 2026-04-20 --term 3M  # 实际使用 term=3M 的日期
```

### 3.3 完整参数组合示例

```bash
# 完整参数：指定货币对、方向、期限、执行价、期望收益点数
python bank-derivative-quoting/scripts/seagull_option_query.py \
  --user-id {userId} \
  --currency-pair EURCNY \
  --settle-purchase settle \
  --term 3M \
  --desired-strikes 7.5 \
  --prem-pips 100

# 不指定货币对，使用默认 USDCNY（输出会备注）
python bank-derivative-quoting/scripts/seagull_option_query.py \
  --user-id {userId} \
  --settle-purchase purchase \
  --term 1M \
  --desired-strikes 7.2
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

## 5. 注意事项

> **关键提醒：只执行一次脚本，不要反复调用！**

1. **只执行一次脚本**：报价脚本只需要执行一次，脚本会自动根据输入参数判断使用哪种场景
2. **直接返回脚本输出**：脚本执行成功后，直接返回脚本输出的字符串，**不需要额外进行组装**
3. **批量报价**：如果脚本返回多行报价信息，全部在表格中返回
4. **常见错误**：
   - 反复用不同参数执行脚本 → 错误！应该回头检查参数提取是否正确
   - 执行脚本后查看输出再决定要不要再执行一次 → 错误！脚本已经返回了所有可用报价
   - 正确做法：仔细阅读用户输入，提取所有参数，一次性执行，直接返回脚本输出