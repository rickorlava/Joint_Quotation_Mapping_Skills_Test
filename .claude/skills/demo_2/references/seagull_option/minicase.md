# 海鸥期权 Minicase（自测）

## 0. 文档定位

本文件提供 **2–3 个** 短用例,用于校验 agent 是否按 `spec` → `internal_model` → `motivation_recognition` → `quotation_format` → `script_contract` → `output_format` 走通。**不替代** `examples.md` 全覆盖。

约定:`{userId}` 从 memory 替换;以下「调用次数」指脚本执行次数。

---

## Minicase 1 — 基准单次

**用户输入（示例）**

> USDCNY 3M 结汇海鸥,给我看看

**期望归一化**

- `currency_pair` = USDCNY, `term` = 3M, `direction` = settle
- 无 `desired_strikes` / `prem_pips` / `target_all_in_rate`

**期望路径**

- 单次调用,**基准报价器**

**期望 CLI（示意）**

```bash
python bank-derivative-quoting/scripts/seagull_option_query.py \
  --user-id {userId} --currency-pair USDCNY --settle-purchase settle --term 3M
```

**期望对外类型**

- `price`,脚本输出透传

**通过判据**

- 仅 **1** 次调用;未编造执行价或补贴

---

## Minicase 2 — 双目标单次（勿拆成多点组合）

**用户输入（示例）**

> 3M 结汇,执行价 7.08,补贴最好 100 点附近

**期望归一化**

- `term` = 3M, `direction` = settle, `desired_strikes` = 7.08, `prem_pips` = 100（单点）

**期望路径**

- **双目标探索**,一次脚本返回多档;**禁止**为扫补贴而多次 `--prem-pips` 单点循环

**期望 CLI（示意）**

```bash
python bank-derivative-quoting/scripts/seagull_option_query.py \
  --user-id {userId} --settle-purchase settle --term 3M \
  --desired-strikes 7.08 --prem-pips 100
```

**期望对外类型**

- `price`,透传

**通过判据**

- 恰好 **1** 次调用;参数含 `--term`、单点 strike、单点 `--prem-pips`

---

## Minicase 3 — 组合：期限横评

**用户输入（示例）**

> USDCNY 结汇海鸥,1M、3M、6M 都报一下

**期望归一化**

- 币种、方向一致;三个 `term` 子问题

**期望路径**

- **组合求解**,先列计划再执行;共 **3** 次调用,汇总单表

**期望 CLI（示意）**

```bash
python bank-derivative-quoting/scripts/seagull_option_query.py \
  --user-id {userId} --currency-pair USDCNY --settle-purchase settle --term 1M
python bank-derivative-quoting/scripts/seagull_option_query.py \
  --user-id {userId} --currency-pair USDCNY --settle-purchase settle --term 3M
python bank-derivative-quoting/scripts/seagull_option_query.py \
  --user-id {userId} --currency-pair USDCNY --settle-purchase settle --term 6M
```

**期望对外类型**

- `price`,一张表三行,列明 term

**通过判据**

- 调用 **3** 次,子目标分别为 1M / 3M / 6M;不超 6 次预算;无「试到满意」式加调
