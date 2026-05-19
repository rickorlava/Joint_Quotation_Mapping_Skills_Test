---
name: dual_delta_iteration
description: 双约束场景下 Dual Delta 迭代模式完整案例（3轮），适用于任意产品
type: example
---

# Dual Delta 迭代模式案例

## 适用产品
本案例以海鸥期权演示，但 §11.4 定义的迭代模式适用于**任意产品**的组合约束场景。

## 场景设定
- 产品：海鸥期权
- 方向：结汇(settle)
- 期限：3M
- 币种：USDCNY
- 客户输入："我要做到6.8，我认为不会贬值到7.2"

此为客户**双约束**表达：`target_all_in_rate = 6.8`（结果目标）+ `desired_strikes = 7.2`（市场观点K）。按 §11.4，不以反解走区间扫描，而以观点 K=7.2 做初始锚定报价，通过 delta 步进迭代找到客户真实隐含的 dual delta 期望点位。

## 适用规范索引
- **交互模式**: SKILL.md §11.4 — Dual Delta 迭代模式
- **思考链路**: SKILL.md §12 — 一步一块实时暴露
- **Dual Delta 知识**: `contract_knowledge.md` §3 Dual Delta
- **海鸥产品规格**: `seagull_option_prod/` 各文档

---

## 第 1 轮 — 初始锚定报价

### 思考链路

>>> ① 意图识别: 输入"海鸥期权 3M 结汇 做到6.8 不会贬值到7.2"
→ 产品"海鸥期权" → 方向"结汇" → settle
→ 出现双约束：`target_all_in_rate = 6.8` + `desired_strikes = 7.2`
→ 按 §11.4 迭代模式：以观点 K=7.2 做初始锚定报价，不做反解

>>> ② 搜索知识: `motivation_recognition.md` §2.2（否定式→ settle+7.2）
→ `contract_knowledge.md` §3 dual delta 认知偏差：客户假设 dual delta=1，OTM 真实值远小于 1

>>> ③ 确认范式: 非标准范式 → §11.4.3 搭载表，转为单点锚定报价

>>> ④ 确认接口: `seagull_option_term_with_desired_strikes_and_currency` → `--term 3M --currency_pair USDCNY --settle_purchase settle --desired_strikes 7.2`
→ 结果目标 6.8 暂不入参，仅做对比展示

### 输出

```
<<<TYPE_START>>> price <<<TYPE_END>>>
<<<CONTENT_START>>>
海鸥期权 USDCNY 3M | 结汇
远期基准: 7.0000
K=7.2000 | 补贴=120 pips | 最终结汇价=6.9880
Dual delta ≈ 0.08（1/|dC/dK| ≈ 12.5）
目标6.8与实际6.9880差距: 1880 pips
<<<CONTENT_END>>>
```

```
<<<TYPE_START>>> chat <<<TYPE_END>>>
<<<CONTENT_START>>>
当前 K=7.2 处于价外(OTM)，dual delta 仅 0.08——K 移动约 12.5 pips 才能改变 1 pip 期权费。
真实补贴远低于您原来预期的"7.2-6.8=4000 pips"的线性假设。
您觉得这个补贴量如何？
<<<CONTENT_END>>>
```

---

## 第 2 轮 — 首次移位迭代

### 用户输入
"太少了，帮我提一提"

### 思考链路

>>> ① 意图识别: "太少了" → 客户在锚定报价后获得方向感 → 要求提高补贴 → 沿 delta 向 ITM 步进

>>> ② 搜索知识: `contract_knowledge.md` §3 第95行 → 默认步长 **5d** → 结汇(sell call)向左移 = 向 ITM = delta +5d

>>> ③ 确认范式: §11.4.2 步进迭代 → 第一次移位

>>> ④ 确认接口: 先调 `common_vanilla_option_delta_reverse` 以 K=7.2 查当前 delta ≈ -0.08
→ +5d（向 ITM）: new_delta ≈ -0.13 → 反解新 K ≈ 7.14
→ 调 `seagull_option_term_with_desired_strikes_and_currency` → `--desired_strikes 7.14`

### 输出

```
<<<TYPE_START>>> price <<<TYPE_END>>>
<<<CONTENT_START>>>
海鸥期权 USDCNY 3M | 结汇 | 迭代 #1
Δ+5d ITM: K 7.2000 → 7.1400
补贴: 120 pips → 290 pips (+170 pips)
最终结汇价: 6.9880 → 6.9710 (-170 pips改善)
Dual delta: 0.08 → 0.14（1/|dC/dK|: 12.5 → 7.1）
<<<CONTENT_END>>>
```

```
<<<TYPE_START>>> chat <<<TYPE_END>>>
<<<CONTENT_START>>>
向左移动5d后，K 从 7.20 到 7.14，补贴从 120 提高到 290 pips。
dual delta 从 0.08 升至 0.14。
是否还需要继续提高？
<<<CONTENT_END>>>
```

---

## 第 3 轮 — 二次移位 + 收敛

### 用户输入
"再提一点"

### 思考链路

>>> ① 意图识别: 继续要求提高 → 再次步进

>>> ② 搜索知识: 同上，步长固定 5d

>>> ③ 确认范式: §11.4.2 步进迭代第 2 轮 ← 已达推荐收敛轮次

>>> ④ 确认接口: new_delta ≈ -0.18 → 反解新 K ≈ 7.08
→ 调 `seagull_option_term_with_desired_strikes_and_currency`

### 输出

```
<<<TYPE_START>>> price <<<TYPE_END>>>
<<<CONTENT_START>>>
海鸥期权 USDCNY 3M | 结汇 | 迭代 #2（共2次）
Δ+5d ITM: K 7.1400 → 7.0800
补贴: 290 pips → 510 pips (+220 pips)
最终结汇价: 6.9710 → 6.9490 (-220 pips改善)
Dual delta: 0.14 → 0.24（1/|dC/dK|: 7.1 → 4.2）
<<<CONTENT_END>>>
```

```
<<<TYPE_START>>> chat <<<TYPE_END>>>
<<<CONTENT_START>>>
再次左移5d后，K=7.08，补贴增至 510 pips，结汇价 6.9490。
当前 1/|dual delta| ≈ 4.2。
您看这个位置是否合适？
<<<CONTENT_END>>>
```

### 用户确认
"差不多了，就这个"

### 最终输出

```
<<<TYPE_START>>> price <<<TYPE_END>>>
<<<CONTENT_START>>>
**最终确认 — 海鸥期权 USDCNY 3M | 结汇 | K=7.0800 | 补贴=510 pips | 最终结汇价=6.9490**
<<<CONTENT_END>>>
```

---

## 收敛路径汇总

| 轮次 | 触发 | K | 补贴(pips) | 结汇价 | \|dual delta\| | 1/\|dC/dK\| |
|---|---|---|---|---|---|---|---|
| 初始锚点 | 客户观点K | 7.2000 | 120 | 6.9880 | 0.08 | 12.5 |
| 移位 #1 | "太少了，提一提" | 7.1400 | 290 | 6.9710 | 0.14 | 7.1 |
| 移位 #2 | "再提一点" | 7.0800 | 510 | 6.9490 | 0.24 | 4.2 |

客户从"6.8"的线性假设起步，3 轮迭代收敛至真实 dual delta 期望点位（|dual delta| ≈ 0.24，OTM-ATM 过渡区），接受 6.9490。

## 关键要点

1. **初始必锚定观点K**：不以反解满足客户约束，目的是让客户看到真实 dual delta
2. **步长固定 5d**：不微调，2~3 轮收敛
3. **每轮暴露 dual delta**：逐步纠正客户的线性假设
4. **适用于所有产品**：本案例以海鸥期权演示，但模式本身接入 K→yield 关系的任意产品
