# 海鸥期权规格 — 分册索引（`demo_2/references/seagull_option/`）

本目录为 [`../seagull_option_spec.md`](../seagull_option_spec.md) 的**流程拆分分册**：便于按阶段加载、控制 Agent 阅读范围。合订本未修改，与分册内容应保持一致；若有冲突以业务方后续裁定为准。

## 推荐阅读顺序（流水线）

1. [`spec.md`](spec.md) — 总述、核心原则、产品元知识、实施心法  
2. [`internal_model.md`](internal_model.md) — 内部字段与层级  
3. [`motivation_recognition.md`](motivation_recognition.md) — 自然语言归一化、结果反推、消歧  
4. [`quotation_format.md`](quotation_format.md) — 求解器注册、单次模式表、组合与预算  
5. [`script_contract.md`](script_contract.md) — Delta 表、CLI 参数与示例  
6. [`output_format.md`](output_format.md) — 追问策略、`price`/`error`/`chat` 契约、注意事项汇总  
7. [`examples.md`](examples.md) — Few-shot（分册内已修正「C 节消歧」示例编号为 **C2**）

## 合订本章节对照

| 合订本 `seagull_option_spec.md` | 分册文件 |
|--------------------------------|----------|
| §0–§2、§14 | `spec.md` |
| §3 | `internal_model.md` |
| §4 | `motivation_recognition.md` |
| §5–§7 | `quotation_format.md` |
| §8–§9 | `script_contract.md` |
| §10、§11、§13 | `output_format.md` |
| §12 | `examples.md` |
