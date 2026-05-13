# 结构性掉期产品的报价范式

## 0. 文档定位
本文件定义结构性掉期报价 agent 的 **合法的报价方式**。

每一种报价范式规定了此情形下：
- 如何调用接口
- 如何将接口所得到的报价结果汇总。
- 汇总报价结果的输出格式

硬约束要求：
- 所有 agent 的动机识别最终**必须**落在所枚举的合法报价范式的其中一种。
- 所有的报价结果**必须**通过调用接口得到，接口的调用IO格式见 `spec.md` 的 `3. 报价接口 IO 格式`
- 先规划后执行，组合方式需要先确定所有需要调用的单点报价传参，然后逐一调用脚本获取结果
- 组合方式调用的单点报价总次数不得超过6
## 1. 合法的报价范式
- `userId` 作为脚本调用的传参，需要从 memory 中读取

### 1.1 基准单点报价给 term 求 K
- 传入：term, settle, currency_pair
- 处理：term 作为 `--term`, settle 作为 `--settle-purchase` 的接口传参，求对应的 K。

调用：
```bash
python bank-derivative-quoting/scripts/opt_structured_swap_query.py --user-id {userId} --currency-pair {currency_pair} --settle-purchase {settle} --term {term}
```

### 1.2 基准单点报价给 K 求 term
- 传入：K, settle, currency_pair
- 处理：K 作为 `--desired-strike`, settle 作为 `--settle-purchase`, currency_pair 作为 `--currency-pair` 的接口传参，求对应的 term。

调用:
```bash
python bank-derivative-quoting/scripts/opt_structured_swap_query.py --user-id {userId} --currency-pair {currency_pair} --settle-purchase {settle} --desired-strike {K}
```

### 1.3 沿曲线扫描 term 区间
此为组合方式，给出 terms 区间扫出对应 term,得到一组 (term, K) 值
- 传入：terms 区间, settle, currency_pair
- 处理：
    - 在区间内选择若干个代表性 term 点位(建议 3~5 个,均匀分布)
    - foreach term 按照 `1.2 基准单点报价给 term 求 K` 传参调一次脚本
    - 汇总为表格,列头含 term 与对应 K
    - 调用次数需控制在 6 次以内

### 1.4 沿曲线扫描 K 区间
此为组合方式，给出 K 区间扫出对应 term,得到一组 (term, K) 值
- 传入：K 的区间, settle, currency_pair
- 处理：
    - 在区间内选择若干代表性 K 点位(建议 3~5 个)
    - foreach K 按照 `1.1 基准单点报价给 K 求 term` 传参调一次脚本
    - 汇总为表格,列头含 K 与对应 term
    - 调用次数需控制在 6 次以内

### 1.5 按近端补贴点数反查
此为组合方式，给出用户期望的近端补贴点数, agent 扫描 term,筛选出补贴最接近目标的两个 term 点位返回。
- 传入：target_prem_pips, settle, currency_pair
- 处理：
    1. **扫描阶段**:在 1M~12M 期限范围内,选取一组代表性 term(如 1M、2M、3M、4M、6M、9M、12M 等,总数不超过 6 次预算), foreach term 按照 `1.2 基准单点报价给 term 求 K` 传参调一次脚本,取回对应的补贴点数，得到一组 (term, 补贴) 数据点
    2. **筛选阶段**:对扫描得到的 (term, 补贴) 数据点,找出补贴数值**最接近用户目标的两个 term 点位**(一个略高、一个略低,方便用户对比)
    3. **输出阶段**:只把筛选出的两个方案返回给用户,表格列明 term、K、补贴点数,并标注"这是最接近您目标 {target_prem_pips} 点的两个方案"

#### 1.5.1 corner case
若扫描后发现目标补贴点数**明显高于或低于**曲线所有点的取值:
- 仍然返回补贴最接近目标的那个 term 点位
- 在**输出阶段**中明确说明:"您目标的补贴点数在当前市场曲线上不可达,以下是最接近的方案"

### 1.6 方向对比
此为 1.1-1.5 的组合方式，将 settle 和 purchase 两组方案调用并将结果汇总
- 传入：被组合范式除了 settle 以外的传入，{purchase, settle}
- 处理：
    1. foreach settle in {purchase, settle}，将 settle 作为被组合范式的传参调用
    2. 将两组调用结果汇总，两行一表。

### 1.7 币种对比
此为 1.1-1.5 的组合方式，将不同的 currency_pair 传参调用并将结果汇总
- 传入：被组合范式除了 currency_pair 以外的传入, currency_pairs
- 处理：
    1. foreach currency_pair in currency_pairs，将 currency_pair 作为被组合范式的传参调用
    2. 将 N 组调用结果汇总，N 行一表。

### 1.8 兜底报价范式
由于强制要求**动机识别**必须落在枚举的合法报价范式中，因此规定一个**兜底报价范式**，当 agent 在动机识别中无法将客户动机映射到任何一种合法报价范式时，将它映射到兜底报价范式。
- 传入：无
- 处理：
    - 将 currency_pair 设定为 USDCNY
    - foreach settle in {purchase, settle}, for each term in {3M, 6M, 9M}，将 (term, settle, currency_pair)按照 `1.2 基准单点报价给 term 求 K` 传参调一次脚本
    - 将调用结果用表格汇总