# 双货币存款 样例

## 11. Few-shot 样例集

> **说明**:以下样例覆盖常见场景与边缘场景。学习重点不是样例本身,而是每条样例后的**处理理由**——它体现了从自然语言到内部约束的推理路径。

---

### A. 基础干净表达

#### 示例 A1:基准报价
用户:
> DCD,3M 结汇 USDCNY

处理:只有期限 + 方向 + 币种,没有结构或收益目标。走基准报价。

调用:
```bash
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --currency_pair USDCNY --settle_purchase settle --term 3M
```

---

#### 示例 A2:指定行权价
用户:
> 3M 结汇双货币存款,K 定在 7.20

处理:给定 term + K,单目标求 yield。

调用:
```bash
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --term 3M --currency_pair USDCNY --settle_purchase settle --desired_strikes 7.2
```

---

#### 示例 A3:指定目标收益率
用户:
> 3M 结汇 DCD,希望补贴收益率 3.5%

处理:给定 term + yield,单目标反求 K。

调用:
```bash
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --term 3M --currency_pair USDCNY --settle_purchase settle --desired_yields 3.5
```

---

#### 示例 A4:历史格式兼容
用户:
> 双货币存款 USDCNY 3M 100pips 结汇 产品报价

处理:按位置解析。归一化后走基准报价 + 中收参数。

调用:
```bash
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --currency_pair USDCNY --settle_purchase settle --term 3M --initial_profit 100
```

---

### B. 市场观点表达(关键场景)

#### 示例 B1:否定式观点
用户:
> 3M 结汇 DCD,我觉得人民币不会贬值到 7.20

处理:
- "不会贬值到 7.20" → 结汇情境,`desired_strikes = 7.20`
- term + K → K 确定求 yield

调用:
```bash
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --term 3M --currency_pair USDCNY --settle_purchase settle --desired_strikes 7.20
```

---

#### 示例 B2:区间肯定式观点
用户:
> 3M 结汇 DCD,我觉得未来三个月汇率大概率在 7.00 到 7.10 之间

处理:
- "大概率在 7.00-7.10 之间" 是区间观点
- 结汇方向下 K 取区间上沿 7.10
- term=3M(与"未来三个月"一致),K=7.10 → K 确定求 yield
- 输出时在报价上方简要说明"基于您对区间的看法,选取 K=7.10 作为行权价"

调用:
```bash
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --term 3M --currency_pair USDCNY --settle_purchase settle --desired_strikes 7.10
```

---

#### 示例 B3:安全边际表达(需追问)
用户:
> 3M 结汇 DCD,K 设保守一点,我不想太冒险

处理:没有具体数值,追问补充。

输出:
```
<<<TYPE_START>>> chat <<<TYPE_END>>>
<<<CONTENT_START>>>
您希望 K 设得保守些,这一点我了解。为了给您精准报价,请问您希望:
- 提供一个具体的 K 值(如 7.20、7.25)
- 提供一个市场观点(如"不会贬值到 X"或"大概率在 X 到 Y")
- 或者提供一个目标补贴收益率(如 3%),由系统反求 K
<<<CONTENT_END>>>
```

---

### C. 双目标探索

> 双目标探索 = 在**给定 `term` 的切片上**,同时接近用户对 K 和 yield 提出的两个目标值。脚本返回一组折中解。`--term`、`--desired_strikes`、`--desired_yields` 三个参数都要传。

#### 示例 C1:term 明确、K 和 yield 都给目标值
用户:
> 3M 结汇 DCD,K 定在 7.20,收益率希望 3.5%

处理:
- term=3M(明确期限)
- desired_strikes=7.20(K 目标,单点)
- desired_yields=3.5(yield 目标,单点)
- 进入双目标探索:在 3M 切片内寻找同时接近 K=7.20 和 yield=3.5% 的几组折中解

调用:
```bash
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --term 3M --currency_pair USDCNY --settle_purchase settle --desired_strikes 7.20 --desired_yields 3.5
```

---

#### 示例 C2:K 和 yield 都给但 term 缺失(需追问)
用户:
> 结汇 DCD,K 要 7.20,收益率希望 3.5%

处理:
- K 和 yield 都是单点目标,但 term 未给
- 脚本需要 `--term`,不能跳过
- 需要追问期限;若用户愿意由系统横评多个期限,可走组合调用(期限横评 × 双目标探索)

输出:
```
<<<TYPE_START>>> chat <<<TYPE_END>>>
<<<CONTENT_START>>>
您希望 K=7.20、收益率 3.5%,这两项我已记下。DCD 报价需要明确期限。
请问您希望:
- 指定一个期限(如 1M、3M、6M),在该期限下寻找接近两目标的方案
- 由系统横评 1M、3M、6M 三个期限(每个期限下各返回一组接近两目标的方案,供您比较)
<<<CONTENT_END>>>
```

---

### D. 区间扫描

#### 示例 D1:K 区间
用户:
> 3M 结汇 DCD,K 从 7.10 到 7.30 看一下

处理:K 区间 → 脚本内置 5 梯度,单次调用。

调用:
```bash
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --term 3M --desired_strikes 7.1 7.3 --default-currency --settle_purchase settle
```

---

#### 示例 D2:收益率区间
用户:
> 3M 结汇 DCD,收益率 2% 到 5% 排几档

处理:yield 区间 → 脚本内置 5 梯度,单次调用。

调用:
```bash
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --term 3M --desired_yields 2 5 --default-currency --settle_purchase settle
```

---

### E. 风格化

#### 示例 E1:结汇激进
用户:
> 3M 结汇 DCD,激进一点

处理:`direction=settle` + 激进 → 查表得 `delta = +0.2`。

调用:
```bash
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --term 3M --delta 0.2 --default-currency --settle_purchase settle
```

---

#### 示例 E2:购汇保守
用户:
> 3M 购汇 DCD,稳一点

处理:`direction=purchase` + 保守 → 查表得 `delta = +0.15`。

调用:
```bash
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --term 3M --delta 0.15 --default-currency --settle_purchase purchase
```

---

#### 示例 E3:风格对比(组合)
用户:
> 3M 结汇 DCD,激进和保守都看看

处理:组合调用。
- 调用 1:`--delta 0.2`(激进)
- 调用 2:`--delta -0.15`(保守)
- 输出:两行一表

---

### F. 方向映射(语义耦合)

#### 示例 F1:"不会贬值到" 表达
用户:
> 3M DCD,我觉得人民币不会贬值到 7.2

处理:
- "不会贬值到" → `direction = settle`
- 数字 → `desired_strikes = 7.2`

调用:
```bash
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --term 3M --currency_pair USDCNY --settle_purchase settle --desired_strikes 7.2
```

---

#### 示例 F2:"不会升值到" 表达
用户:
> 3M DCD,人民币不会升值到 6.80

处理:
- "不会升值到" → `direction = purchase`
- 数字 → `desired_strikes = 6.80`

调用:
```bash
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --term 3M --currency_pair USDCNY --settle_purchase purchase --desired_strikes 6.80
```

---

### G. K 和 yield 中某一项为区间(走区间扫描而不是双目标)

#### 示例 G1:K 为单点 + yield 为区间
用户:
> 3M 结汇 DCD,K 定 7.20,收益率 2% 到 5%

处理:
K=7.20 是单点目标,yield 是区间。在 K 已确定后,yield 是 K 的函数结果,不能同时要求为区间。需追问用户:到底是 K 要走单点还是 yield 走区间扫描。

输出:
```
<<<TYPE_START>>> chat <<<TYPE_END>>>
<<<CONTENT_START>>>
您提到 K=7.20 和收益率在 2%-5% 区间。在一个给定期限下,一旦 K 确定,收益率也随之唯一决定。请问您希望:
- 希望以 K=7.20 为准,看该 K 对应的收益率是多少
- 希望看收益率在 2%-5% 区间里排几档,每一档对应一个 K
<<<CONTENT_END>>>
```

输出:
```
<<<TYPE_START>>> chat <<<TYPE_END>>>
<<<CONTENT_START>>>
您给出了期限 3M、行权价 7.20、目标收益率 3.5% 三项约束,这三者通常不能同时精确满足。
请问您希望放弃哪一项作为自由变量?
- 放弃期限约束,由系统在期限维度寻找最接近的 5 组方案
- 放弃行权价约束,由期限和收益率反求
- 放弃收益率约束,由期限和行权价正向求解
<<<CONTENT_END>>>
```

---

### H. 组合调用

#### 示例 H1:期限横评
用户:
> 结汇 DCD,1M、3M、6M 都给我报一下

处理:三次调用,期限分别为 1M / 3M / 6M,其他参数相同。三行一表。

---

#### 示例 H2:方向对比
用户:
> 3M DCD,结汇和购汇都看一下

处理:两次调用,方向分别为 settle 和 purchase。两行一表。

---

### I. 收益率的多种表达

#### 示例 I1:百分比
用户:
> 3M 结汇 DCD,收益率 5%

处理:直接取 5。

调用参数:`--desired_yields 5`

---

#### 示例 I2:小数
用户:
> 3M 结汇 DCD,收益率 0.035

处理:乘以 100 转换 → `3.5`。

调用参数:`--desired_yields 3.5`

---

#### 示例 I3:口语化"几个点"
用户:
> 3M 结汇 DCD,希望补贴 3 个点左右

处理:"3 个点" → `3`。

调用参数:`--desired_yields 3`

---

### J. 结果导向表达

#### 示例 J1:用"到手"描述收益
用户:
> 3M 结汇 DCD,希望到手收益率 3%

处理:这里"到手"指补贴折年化,而非总利率。归一化为 `desired_yields = 3`。

调用参数:`--desired_yields 3`

---

### K. 不完整输入

#### 示例 K1:只给方向和币种
用户:
> 来个结汇 DCD

处理:term、K、yield、delta 全缺失,需追问。

输出:
```
<<<TYPE_START>>> chat <<<TYPE_END>>>
<<<CONTENT_START>>>
请问您希望以哪一侧作为约束?
- 指定一个期限(如 1M、3M、6M 等)
- 指定一个行权价 K
- 指定一个目标补贴收益率(如 3.5%)
- 或者描述风险偏好(如激进、保守)
<<<CONTENT_END>>>
```

---

#### 示例 K2:只给交割日
用户:
> 2026-09-01 交割的结汇 DCD

处理:有 `delivery_date`,走基准报价。

调用:
```bash
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --delivery_date 2026-09-01 --settle_purchase settle --currency_pair USDCNY
```

---

### L. 自由期限

#### 示例 L1:非预设档位
用户:
> 2M 结汇 DCD

处理:2M 不在常见档位,但 `term` 支持自由期限,直接传。

调用:
```bash
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --term 2M --currency_pair USDCNY --settle_purchase settle
```

---

### M. 多轮上下文

#### 示例 M1:指代上一轮
用户(上一轮已报过 3M 结汇 USDCNY):
> 刚才那个换成购汇看看

处理:继承 `term=3M`、`currency_pair=USDCNY`,仅替换 `direction=purchase`。单次调用。

---

### N. 极端值

#### 示例 N1:极端收益率
用户:
> 3M 结汇 DCD,希望收益率 50%

> 超过10%的收益率为不合理

处理:50% 在当前市场下明显不合理。通过 chat 确认是否输入有误。

输出:
```
<<<TYPE_START>>> chat <<<TYPE_END>>>
<<<CONTENT_START>>>
您给出的目标收益率 50% 远超当前市场常见区间,请确认是否输入有误?
若确认无误可继续,系统将按实际可报价能力返回结果。
<<<CONTENT_END>>>
```

---

### O. 带市场观点(不评论)

#### 示例 O1:
用户:
> 我觉得人民币要贬,帮我做个 3M 购汇 DCD

处理:不评价观点。按 `purchase` + `term=3M` 走基准报价。

调用:
```bash
python bank-derivative-quoting/scripts/dcd_query.py --user_id {userId} --term 3M --currency_pair USDCNY --settle_purchase purchase
```

---

## 12. 最小测试案例集

> 以下为快速校验用最小用例,不替代 §11 的全覆盖。

### 12.1 传统报价案例

#### 12.1.1 齐备要素

```
双货币存款 USDCNY 3M 10pips 结汇 产品报价
双币存款 EURCNY 20260512 10 购汇 报价
双货币存款 USDCNY 1M 10pips 结汇
DCD 3M 结汇 USDCNY
```

#### 12.1.2 部分缺省要素

```
USDCNY 3M 10pips 结汇 报价
双币存款 20260512 10 购汇 报价
双货币存款 USDCNY 1M 10pips 结汇
```

### 12.2 自然语言报价

#### 12.2.1 单次求解

```
DCD 执行价 6.8177  3M  10pips  报价
```
- perm + K 确定 → 求 yield，叠加中收参数。单次调用

```
DCD 6M 5% 收益 报价
3M 结汇 DCD,希望补贴 3 个点左右 收益率
```
- yield -> 反解 K  叠加 中收参数 

``` 
DCD 3M 结汇 HKDCNY 收益更高
```
- 市场观点

```
3M 结汇 DCD,K 定在 7.20,收益率希望 3.5%
3M 结汇 DCD,我觉得人民币不会贬值到 7.20
3M 结汇 DCD,K 设保守一点,我不想太冒险
3M 结汇 DCD,我觉得未来三个月汇率大概率在 7.00 到 7.10 之间
结汇 DCD,K 要 7.20,收益率希望 3.5%
3M 结汇 DCD,K 从 7.10 到 7.30 看一下
```
- 双目标求解

#### 12.2.2 多次求解

```
1）DCD 结汇 批量报价 
2）结汇 DCD,1M、3M、6M 都给我报一下

```
通过追问 期限 币种 风格 多个价格
