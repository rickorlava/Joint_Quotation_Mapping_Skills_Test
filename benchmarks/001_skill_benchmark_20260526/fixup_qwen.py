#!/c/Users/surface/anaconda3/python.exe
"""重新跑 qwen 失败案例并更新结果文件（从末尾向前替换，避免偏移）"""
import re, os, json, time, yaml, requests

BASE = r"C:\Users\surface\OneDrive\Documents\AIBP\SkillFirstMerge\config"
RESULTS = os.path.join(BASE, "benchmark_results.txt")
CFG_PATH = os.path.join(BASE, "models.yaml")

with open(CFG_PATH, encoding="utf-8") as f:
    CFG = yaml.safe_load(f)

# ─── 读取结果文件 ────────────────────────────────────────────────────────
with open(RESULTS, "r", encoding="utf-8") as f:
    text = f.read()

# ─── 找出所有 qwen 失败案例 ──────────────────────────────────────────────
# 找所有案例位置
case_pattern = re.compile(r'\[([^\]]+)\]\s*input:\s*(.+?)\s*\n')
cases = list(case_pattern.finditer(text))

failed = []
for i, m in enumerate(cases):
    label = m.group(1)
    user_input = m.group(2)
    end = cases[i+1].start() if i+1 < len(cases) else len(text)
    block = text[m.start():end]

    # 找 qwen 块
    qw_match = re.search(r'--- qwen \(', block)
    if not qw_match:
        continue

    qw_start_in_block = qw_match.start()
    qw_section = block[qw_start_in_block:]

    # 检查是否有错误
    if 'ERROR:' not in qw_section and 'Exception:' not in qw_section:
        continue

    # 确定产品（往前找产品标题）
    before = text[:m.start()]
    prod = "opt_structual_swap"
    for keyword, pid in [("结构性掉期", "opt_structual_swap"), ("双货币存款", "dual_currency_deposit"), ("海鸥期权", "seagull_option")]:
        if keyword in before:
            prod = pid

    # 全局位置
    abs_start = m.start() + qw_start_in_block
    # 找这个 qwen 块的结束：下一个 case 分隔符 或 下一个 qwen 块 或 文件尾
    rest = text[abs_start:]
    next_sep = re.search(r'\n\s*─{5,}', rest)
    next_case_pattern = re.search(r'\n\s*\[', rest)
    # 找最近的
    end_positions = []
    if next_sep:
        end_positions.append(next_sep.start())
    if next_case_pattern:
        end_positions.append(next_case_pattern.start())
    block_len = min(end_positions) if end_positions else len(rest)

    failed.append({
        "idx": i + 1,
        "label": label,
        "input": user_input,
        "product": prod,
        "abs_start": abs_start,
        "block_len": block_len,
    })

print(f"需要重跑: {len(failed)} 个 qwen 案例")

# ─── 系统提示词 ──────────────────────────────────────────────────────────
skill_path = os.path.join(BASE, "..", ".claude", "skills", "bank-derivative-quoting", "SKILL.md")
with open(skill_path, encoding="utf-8") as f:
    SKILL_MD = f.read()

def load_doc(parts):
    p = os.path.join(BASE, "..", ".claude", "skills", "bank-derivative-quoting", "references", *parts)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return f.read()
    return ""

def get_system_prompt(product_key):
    prod_map = {"opt_structual_swap": "opt_structual_swap_prod", "dual_currency_deposit": "dual_currency_deposit_prod", "seagull_option": "seagull_option_prod"}
    pkey = prod_map[product_key]
    qf = load_doc([pkey, "agent_output/quotation_format.md"])
    mr = load_doc([pkey, "intent_recognition/motivation_recognition.md"])
    return f"{SKILL_MD}\n\n## 产品参考文档\n\n### 报价范式\n{qf}\n\n### 意图识别\n{mr}"

# ─── API 调用 ─────────────────────────────────────────────────────────────
def call_qwen(system_prompt, user_input, timeout=240):
    cfg = CFG["models"]["qwen"]
    headers = {
        "x-api-key": cfg["api_key"],
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": cfg["model"],
        "max_tokens": 2048,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_input}],
    }
    url = cfg["base_url"].rstrip("/") + "/messages"

    for attempt in range(3):
        try:
            t0 = time.time()
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
            elapsed = time.time() - t0
            if resp.status_code == 200:
                data = resp.json()
                content = data.get("content", [])
                texts = []
                for b in content:
                    if b.get("type") == "text":
                        texts.append(b.get("text", ""))
                    elif b.get("type") == "thinking":
                        texts.append(f"[thinking: {b.get('thinking', '')[:300]}...]")
                output = "\n".join(texts)
                return output, elapsed, True
            else:
                output = f"ERROR: HTTP {resp.status_code}: {resp.text[:300]}"
                if attempt < 2:
                    print(f" HTTP{resp.status_code}(retry#{attempt+1})", end="", flush=True)
                    time.sleep(3)
                    continue
                return output, 0, False
        except Exception as e:
            output = f"ERROR: {str(e)}"
            if attempt < 2:
                print(f" timeout(retry#{attempt+1})", end="", flush=True)
                time.sleep(5)
                continue
            return output, 0, False

# ─── 补跑（从末尾到开头，避免位置偏移） ──────────────────────────────────
failed.sort(key=lambda x: -x["abs_start"])  # 从文件末尾开始
success_count = 0

for fc in failed:
    sys_prompt = get_system_prompt(fc["product"])
    print(f"  [{fc['idx']}/{len(cases)}] {fc['label']}: {fc['input'][:50]}...", end=" ", flush=True)

    output, elapsed, ok = call_qwen(sys_prompt, fc["input"])

    if ok:
        print(f"✅ {elapsed:.1f}s")
        success_count += 1
    else:
        print(f"❌ {elapsed:.1f}s")
        # If still failing, keep old content
        continue

    # 构造新 qwen 块
    new_qwen_block = f"--- qwen ({elapsed:.1f}s) ---\n  Output:\n"
    for line in output.split("\n"):
        new_qwen_block += f"    {line}\n"

    # 替换（从末尾开始，位置不变）
    old_qwen_block = text[fc["abs_start"]:fc["abs_start"] + fc["block_len"]]
    text = text[:fc["abs_start"]] + new_qwen_block.rstrip() + text[fc["abs_start"] + fc["block_len"]:]

    time.sleep(1)

    # 增量保存
    with open(RESULTS, "w", encoding="utf-8") as f:
        f.write(text)

# ─── 保存 ─────────────────────────────────────────────────────────────────
with open(RESULTS, "w", encoding="utf-8") as f:
    f.write(text)

print(f"\n\n重跑完成: {success_count}/{len(failed)} 成功")
if success_count < len(failed):
    print(f"仍有 {len(failed) - success_count} 个案例未修复")
print(f"结果已更新至 {RESULTS}")
