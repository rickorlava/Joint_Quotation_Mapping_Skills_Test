# 海鸥期权报价 — Few-shot 样例集（分册）

## 0. 文档定位

本分册对应合订本 **§12**。学习重点是每条样例后的**处理理由**；与 [`motivation_recognition.md`](motivation_recognition.md)、[`quotation_format.md`](quotation_format.md)、[`script_contract.md`](script_contract.md) 对照阅读。

---

## 12. Few-shot 样例集

> **说明**:以下样例覆盖常见场景与边缘场景。学习重点不是样例本身,而是每条样例后附带的**处理理由**——它体现了从自然语言到内部约束的推理路径。

---

### A. 基础干净表达

#### 示例 A1:基准报价
用户:
> 海鸥,USDCNY,3M,结汇,给我看看

处理:只提供了期限 + 方向 + 币种,没有结构或收益目标,走基准报价器。

调用:
```bash
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --currency-pair USDCNY --settle-purchase settle --term 3M
```

---

#### 示例 A2:直接给执行价
用户:
> 做个 3M 结汇海鸥,执行价按 7.10 看看

处理:用户显式说"执行价",直接映射为 `desired_strikes`。

调用:
```bash
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --settle-purchase settle --term 3M --desired-strikes 7.10
```

---

#### 示例 A3:历史格式兼容
用户:
> 海鸥期权 USDCNY 3M 100pips 结汇 产品报价

处理:识别为历史六字段格式。按位置解析:币种=USDCNY、期限=3M、中收=100、方向=settle。归一化后进入基准求解。

调用:
```bash
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --currency-pair USDCNY --settle-purchase settle --term 3M --profit 100
```

---

### B. 市场观点表达(关键场景)

#### 示例 B1:否定式观点
用户:
> 3M 结汇海鸥,我觉得人民币不会贬值到 7.20

处理:否定式观点下 `direction = settle`,`desired_strikes = 7.20`。

调用:
```bash
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --settle-purchase settle --term 3M --desired-strikes 7.20
```

---

#### 示例 B2:区间肯定式观点
用户:
> 3M 结汇海鸥,我觉得未来三个月汇率大概率在 7.00 到 7.10

处理:
- 区间观点 7.00-7.10 下结汇方向 → K 取区间上沿 7.10
- 输出时说明推理过程,供客户确认

调用:
```bash
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --settle-purchase settle --term 3M --desired-strikes 7.10
```

---

#### 示例 B3:区间观点 vs 单点区间(区别)
用户 X:
> 3M 结汇海鸥,执行价 7.00 到 7.20 看看

用户 Y:
> 3M 结汇海鸥,汇率大概率在 7.00 到 7.20

处理:
- X 是"扫描两个端点"意图 → `desired_strikes = [7.00, 7.20]`,脚本返回 5 档梯度
- Y 是"市场观点"表达 → `desired_strikes = 7.20`(区间上沿),脚本返回单点报价
- 判断依据:用户是在说"这是 K 的选项"还是"这是汇率走势"

X 调用:
```bash
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --settle-purchase settle --term 3M --desired-strikes 7.00 7.20
```

Y 调用:
```bash
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --settle-purchase settle --term 3M --desired-strikes 7.20
```

---

### C. 结果语言与反推

#### 示例 C1:结果反推
用户:
> 我希望 3M 结汇最后能做到 6.90 左右

处理:6.90 是**结果目标**而非执行价(因为用户用"最后能做到"这种效果语),映射为 `target_all_in_rate`。先取 3M 远期基准价,反推 `prem_pips`,再进单目标求解。

调用:
```bash
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --settle-purchase settle --term 3M --prem-pips <反推值>
```

---

#### 示例 C2:消歧
用户:
> 3M 结汇,6.9

处理:一个孤立的 6.9 无法判断是执行价还是结果价,需要追问。

输出:
```
<<<TYPE_START>>> chat <<<TYPE_END>>>
<<<CONTENT_START>>>
请问您说的 6.9 是希望作为执行价,还是希望作为最后结汇的成交效果价?
<<<CONTENT_END>>>
```

---

### D. 双目标与区间

#### 示例 D1:双目标探索
用户:
> 3M,执行价 7.08,收益最好 100 点附近

处理:同时给出结构目标和收益目标,走双目标探索,脚本自动返回 5 档。

调用:
```bash
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --term 3M --desired-strikes 7.08 --prem-pips 100
```

---

#### 示例 D2:区间扫描(单次,不要组合)
用户:
> 3M 的,补贴 50 到 150 点排几档

处理:脚本自身就会返回 5 档梯度,**不要**让 agent 自己遍历。

调用:
```bash
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --term 3M --prem-pips 50 150
```

---

### E. 风格化

#### 示例 E1:单风格(结汇激进)
用户:
> 3M 结汇,激进一点

处理:`delta_preference = aggressive`、`direction = settle` → 查表得 `delta = -0.2`。

调用:
```bash
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --settle-purchase settle --term 3M --delta -0.2 --inverse-type delta
```

---

#### 示例 E2:风格对比(组合)
用户:
> 3M 结汇,激进和保守都看看

处理:组合调用。
- 调用 1:`--delta -0.2`(激进)
- 调用 2:`--delta +0.15`(保守)
- 输出:两行一表

---

### F. 自由期限

#### 示例 F1:非预设档位期限
用户:
> 想做 2 个月结汇,执行价 7.10

处理:2M 不在常见档位里,但 `term` 支持自由期限,直接传。

调用:
```bash
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --settle-purchase settle --term 2M --desired-strikes 7.10
```

---

### G. 组合调用

#### 示例 G1:期限横评
用户:
> USDCNY 结汇,1M、3M、6M 都给我报一下

处理:单次调用无法完成多期限横评,走组合。三次调用,期限分别为 1M/3M/6M,其他参数相同,结果汇总为三行一表。

---

#### 示例 G2:方向对比
用户:
> 3M USDCNY,结汇和购汇都看一下

处理:两次调用,方向分别为 settle 和 purchase,两行一表。

---

### H. 不完整但可推断

#### 示例 H1:方向隐含在结果语里
用户:
> 3M 想做到 6.9

处理:
- 用户没显式说方向,但"做到 6.9"配合当前 USDCNY 市场价(假设现货约 7.0)暗示是**结汇**(人民币相对走强对客户有利)
- 6.9 是结果目标 → 反推 prem_pips
- 单次调用

若上下文不确定,仍应追问方向;在上下文明确时可以合理推断。

---

#### 示例 H2:只给日期不给期限
用户:
> 2026-09-01 交割的结汇海鸥

处理:用户给了 `delivery_date` 而没给 `term`,直接用 `--delivery-date` 传。

调用:
```bash
python bank-derivative-quoting/scripts/seagull_option_query.py --user-id {userId} --settle-purchase settle --delivery-date 2026-09-01
```

---

### I. 混合表达

#### 示例 I1:结构约束 + 结果约束共存
用户:
> 3M 结汇,执行价想要 7.10,但最后结汇别差于 6.92

处理:
- `desired_strikes = 7.10`(结构约束)
- `target_all_in_rate ≥ 6.92`(结果约束的下限)
- 用 6.92 反推出 `prem_pips` 下限,与 7.10 一起进双目标探索
- 输出 5 档,明确标注"保证结汇≥6.92"的可行区间

---

### J. 反直觉 / 相对量表达

#### 示例 J1:相对比较
用户:
> 给我来个 3M 结汇,要比直接远期锁好一点

处理:
- "比远期好一点"是相对目标,映射为 `target_all_in_rate ≈ 远期价 + 合理补贴`
- 可以默认取一个温和补贴水平(如 50-80 pips),走标准单目标;或与用户确认补贴幅度

为避免误判,这种模糊表达建议先通过 `chat` 简单确认希望的补贴量级,再报价。

---

#### 示例 J2:否定约束
用户:
> 3M 购汇,别让我高过 7.15 就行

处理:
- `direction = purchase`
- "别高过 7.15" → `target_all_in_rate ≤ 7.15`(购汇方向的上限)
- 反推 `prem_pips`,单次调用

---

### K. 口语化 / 非术语

#### 示例 K1:完全口语
用户:
> 你们那个海鸥啊,3 个月的,我就想结汇的时候看着体面点

处理:
- 产品=海鸥、期限=3M、方向=结汇
- "看着体面点"是模糊的结果偏好,没有明确数值
- 建议先以中等补贴基准报价,输出时说明"若希望更高补贴或更好执行价可进一步调整"
- 或通过 `chat` 简短询问:希望补贴大致在什么量级

---

### L. 用词偏差

#### 示例 L1:术语不准
用户:
> 3M 买汇,贴水 100 个基点

处理:
- "买汇" → `purchase`
- "贴水" 在此语境下相当于 `prem_pips` 或 `target_all_in_rate` 方向的负补偿;需根据购汇方向判定
- "100 个基点" = 100 pips → `prem_pips = 100`(购汇方向上补贴方向需与结构一致)

关键是**不要因为术语不规范就拒绝**,而要在语义上做最合理的翻译,并在输出中用规范术语复述一遍,便于用户确认。

---

### M. 自相矛盾 / 极端需求

#### 示例 M1:无法同时满足
用户:
> 3M 结汇,执行价 6.5,同时补贴 500 点

处理:两者很可能在当前市场下不可行。agent 应:
1. 不要强行调用脚本
2. 通过 `chat` 说明这两个目标通常互相冲突
3. 给出两种可选降级:保留 6.5 执行价、或保留 500 补贴
4. 让用户选择继续

---

### N. 带市场观点(不评论)

#### 示例 N1:含预判
用户:
> 我觉得人民币后面肯定要贬,帮我锁一个 3M 购汇的海鸥

处理:
- "肯定要贬" 是用户的市场观点,agent **不评论观点**
- 方向=购汇、期限=3M,走基准报价
- 输出时可附一句:"您看是否需要进一步设定执行价或补贴目标"

---

### O. 多轮上下文

#### 示例 O1:指代上一轮
用户(上一轮已报过 3M 结汇):
> 刚才那个给我换成购汇看看

处理:继承上一轮的 `term=3M` 以及其他默认参数,仅替换 `direction` 为 `purchase`。单次调用。

---

### P. 边界值

#### 示例 P1:极端数值
用户:
> 3M 结汇,补贴给我 2000 点

处理:2000 点在当前市场下极不合理,agent 应:
1. 不盲目调脚本
2. 通过 `chat` 告知该数值远超常见区间,请用户确认是否输入有误
3. 如确认,则按用户意图调用,脚本层面会返回合理错误或调整

