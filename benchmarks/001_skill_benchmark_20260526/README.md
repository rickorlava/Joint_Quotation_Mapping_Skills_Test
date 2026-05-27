# Benchmark 001: Skill 双模型对比 (ds-v4 vs qwen3.6-27b)

**日期:** 2026-05-26
**用例:** 97 个 (结构性掉期 34 + 双货币存款 31 + 海鸥期权 32)

## 内容

| 文件 | 说明 |
|------|------|
| `runner.py` | 原始 benchmark 脚本，调用两模型并记录响应 |
| `analyze.py` | 统计分析脚本，生成统计数据 |
| `fixup_qwen.py` | 补充重跑 qwen 失败案例（补跑 17 个因欠费/超时失败的案例） |
| `format_analysis.py` | 输出格式与范式映射详细分析 |
| `benchmark_results.txt` | 全部 97 案例 × 2 模型的原始输出（6076 行） |
| `benchmark_analysis_final.txt` | 最终统计数据与对比结论 |
| `benchmark_analysis.txt` | 中间版本的分析报告 |
| `format_paradigm_analysis.txt` | 格式与范式映射的细粒度分析 |

## 结论

- ds-v4 速度快 5x、零失败；qwen 输出格式更规范但慢 5x
- 两模型范式选择完全一致
- 详细见 `benchmark_analysis_final.txt`
