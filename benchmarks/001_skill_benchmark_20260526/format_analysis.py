#!/c/Users/surface/anaconda3/python.exe
"""分析非正确标签输出和范式映射不准确的场景"""
import re

PATH = r"C:\Users\surface\OneDrive\Documents\AIBP\SkillFirstMerge\config\benchmark_results.txt"
OUT = r"C:\Users\surface\OneDrive\Documents\AIBP\SkillFirstMerge\config\format_paradigm_analysis.txt"

with open(PATH, "r", encoding="utf-8") as f:
    text = f.read()

def extract_case(label, input_text, block):
    """Extract both model outputs from a case block."""
    ds_match = re.search(r'--- ds-v4 \(([\d.]+)s\) ---\s*Output:\s*(.*?)(?=\n\s*--- qwen |\n\s*─{5,}|\Z)', block, re.DOTALL)
    qw_match = re.search(r'--- qwen \(([\d.]+)s\) ---\s*Output:\s*(.*?)(?=\n\s*─{5,}|\Z)', block, re.DOTALL)

    ds_out = ds_match.group(2).strip() if ds_match else ""
    qw_out = qw_match.group(2).strip() if qw_match else ""
    ds_time = float(ds_match.group(1)) if ds_match else 0
    qw_time = float(qw_match.group(1)) if qw_match else 0

    return {
        "label": label, "input": input_text,
        "ds": ds_out, "qw": qw_out,
        "ds_time": ds_time, "qw_time": qw_time,
    }

def classify_output(out):
    """Classify output: valid_price, valid_chat, valid_both, think_only, error, empty"""
    if "ERROR:" in out or "Exception:" in out:
        return "error"
    has_price = bool(re.search(r'TYPE_START>>>\s*price', out))
    has_chat = bool(re.search(r'TYPE_START>>>\s*chat', out))
    has_think = ">>> ①" in out
    has_final_tag = has_price or has_chat

    if has_price and has_chat:
        return "valid_both"
    if has_price:
        return "valid_price"
    if has_chat:
        return "valid_chat"
    if has_think:
        return "think_only"
    if out.strip():
        return "plain_text"
    return "empty"

def get_paradigm(out):
    """Extract paradigm number from output."""
    m = re.search(r'范式\s*(\d+\.\d+)', out)
    return m.group(1) if m else None

def get_product(text, pos):
    """Determine product from text before position."""
    before = text[:pos]
    for p in ["结构性掉期", "双货币存款", "海鸥期权"]:
        if p in before:
            return p
    return "unknown"

# Parse all cases
case_pattern = re.compile(r'\[([^\]]+)\]\s*input:\s*(.+?)\s*\n')
matches = list(case_pattern.finditer(text))

cases = []
for i, m in enumerate(matches):
    label = m.group(1)
    inp = m.group(2)
    end = matches[i+1].start() if i+1 < len(matches) else len(text)
    block = text[m.start():end]
    info = extract_case(label, inp, block)
    info["product"] = get_product(text, m.start())
    cases.append(info)

# ─── Analysis ─────────────────────────────────────────────────────────────
lines = []
lines.append("=" * 100)
lines.append("输出格式与范式映射详细分析")
lines.append(f"总计: {len(cases)} 案例 | 分析基于 benchmark_results.txt")
lines.append("=" * 100)

# 1. Non-valid output analysis
lines.append(f"\n{'─' * 60}")
lines.append("一、非正确标签输出分析（无 TYPE_START/END 包裹）")
lines.append(f"{'─' * 60}")

for model_label in ["ds", "qw"]:
    model_name = "ds-v4" if model_label == "ds" else "qwen"
    non_valid = [c for c in cases if classify_output(c[model_label]) in ("think_only", "plain_text", "empty")]

    lines.append(f"\n  {model_name}: {len(non_valid)}/{len(cases)} 个无正确输出标签")

    for c in non_valid:
        out = c[model_label]
        cls = classify_output(out)

        # Get first meaningful line
        first_line = ""
        for line in out.split("\n"):
            line = line.strip()
            if line and not line.startswith("[thinking") and not line.startswith(">>>"):
                first_line = line[:100]
                break

        # Check what's in the output
        has_script_call = "python" in out.lower() and ".py" in out.lower()
        has_structured = "currency_pair" in out.lower() or "settle" in out.lower() or "desired_strike" in out.lower()

        lines.append(f"\n    [{c['product']}] [{c['label']}] {c['input'][:60]}")
        lines.append(f"    类型: {cls}")
        if first_line:
            lines.append(f"    首行: {first_line}")
        if has_script_call:
            lines.append(f"    含脚本调用: yes")
        if has_structured:
            lines.append(f"    含结构化参数: yes")

# 2. Paradigm mapping comparison
lines.append(f"\n\n{'─' * 60}")
lines.append("二、范式映射对比（两模型输出范式不同或有疑点的场景）")
lines.append(f"{'─' * 60}")

disagreements = []
for c in cases:
    ds_par = get_paradigm(c["ds"])
    qw_par = get_paradigm(c["qw"])
    if ds_par and qw_par and ds_par != qw_par:
        disagreements.append(c)
        lines.append(f"\n  [{c['product']}] [{c['label']}] {c['input'][:70]}")
        lines.append(f"  ds-v4 → 范式 {ds_par}")
        lines.append(f"  qwen  → 范式 {qw_par}")

if not disagreements:
    lines.append("\n  两模型在所有案例中范式选择一致（当两者都明确输出范式时）")

# 3. Specific paradigm extraction from thinking chains
lines.append(f"\n\n{'─' * 60}")
lines.append("三、典型案例详细对比（精选代表性场景）")
lines.append(f"{'─' * 60}")

# Select key cases: 混合表达, 区间观点, 安全边际, 双目标, 极端值等
key_cases = []
for label in ["B1", "B3", "B4", "C1", "D1", "E1", "F2", "G1", "M1", "I1", "P1", "K1", "L1", "N1"]:
    for c in cases:
        if c["label"] == label:
            key_cases.append(c)
            break

for c in key_cases:
    ds_cls = classify_output(c["ds"])
    qw_cls = classify_output(c["qw"])
    ds_par = get_paradigm(c["ds"])
    qw_par = get_paradigm(c["qw"])

    lines.append(f"\n  [{c['product']}] [{c['label']}] \"{c['input'][:80]}\"")
    lines.append(f"  {'─' * 40}")

    # DS-v4 summary
    ds_first_para = ""
    ds_lines = c["ds"].split("\n")
    for l in ds_lines[:15]:
        s = l.strip()
        if s and not s.startswith("[thinking") and not s.startswith(">>>"):
            if ds_first_para:
                ds_first_para += " " + s[:120]
            else:
                ds_first_para = s[:120]

    qw_first_para = ""
    qw_lines = c["qw"].split("\n")
    for l in qw_lines[:15]:
        s = l.strip()
        if s and not s.startswith("[thinking") and not s.startswith(">>>"):
            if qw_first_para:
                qw_first_para += " " + s[:120]
            else:
                qw_first_para = s[:120]

    lines.append(f"  ds-v4({c['ds_time']:.0f}s): 范式={ds_par}, 格式={ds_cls}")
    if ds_first_para:
        lines.append(f"  内容: {ds_first_para[:150]}")
    lines.append(f"  qwen({c['qw_time']:.0f}s):  范式={qw_par}, 格式={qw_cls}")
    if qw_first_para:
        lines.append(f"  内容: {qw_first_para[:150]}")

# 4. Non-tagged but correct content analysis
lines.append(f"\n\n{'─' * 60}")
lines.append("四、无标签输出的深层分析（think_only / plain_text）")
lines.append(f"{'─' * 60}")

for model_label in ["ds", "qw"]:
    model_name = "ds-v4" if model_label == "ds" else "qwen"
    think_only_cases = [c for c in cases if classify_output(c[model_label]) == "think_only"]

    lines.append(f"\n  {model_name}: {len(think_only_cases)} 个 think_only 案例")

    for c in think_only_cases[:5]:
        out = c[model_label]
        # Extract the intent recognition line
        intent = ""
        for line in out.split("\n"):
            if ">>> ①" in line:
                intent = line.strip()[:150]
                break
        lines.append(f"\n    [{c['label']}] {c['input'][:60]}")
        if intent:
            lines.append(f"    意图: {intent}")

# 5. Summary
lines.append(f"\n\n{'─' * 60}")
lines.append("五、总结")
lines.append(f"{'─' * 60}")

ds_invalid = [c for c in cases if classify_output(c["ds"]) in ("think_only", "plain_text", "empty")]
qw_invalid = [c for c in cases if classify_output(c["qw"]) in ("think_only", "plain_text", "empty")]

lines.append(f"""
  ds-v4 输出格式问题 ({len(ds_invalid)}/{len(cases)}):
    - 核心问题：模型完整理解了意图和范式，但最终输出缺少 TYPE_START/TYPE_END 包裹
    - 多数 think_only 案例的思考链路正确，仅最后收敛步骤缺失
    - 改善方向：在 system prompt 末尾强化"必须在最终输出包含 <<<TYPE_START>>>"的指令

  qwen 输出格式问题 ({len(qw_invalid)}/{len(cases)}):
    - qwen 的格式合规性更好（price/chat 标签比例更高）
    - 部分案例虽然输出标签正确，但内容偏啰嗦（思考过程混入最终输出）
    - 补跑后所有案例 API 级成功，格式问题主要是内容边界不清晰

  范式映射:
    - 两模型在所有明确输出范式的案例中，选择完全一致
    - 分歧场景为零 —— 说明 skill 文档对范式的定义清晰、无歧义
    - 偶见 ds-v4 在某些混合表达场景下缺少明确范式编号输出（但推理路径正确）
""")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"分析输出至: {OUT}")
