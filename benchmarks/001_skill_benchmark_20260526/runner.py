#!/c/Users/surface/anaconda3/python.exe
"""benchmark: 运行 skill 所有 example/minicase 在 ds-v4 和 qwen 上的表现对比"""
import json, yaml, time, os, sys, requests
from datetime import datetime

# ─── Config ───────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
CFG_PATH = os.path.join(BASE, "models.yaml")
OUT_PATH = os.path.join(BASE, "benchmark_results.txt")

with open(CFG_PATH, encoding="utf-8") as f:
    CFG = yaml.safe_load(f)

# ─── Skill context (system prompt) ────────────────────────────────────────
# Load key reference docs
def load_doc(rel_path):
    parts = rel_path.replace("/", os.sep).split(os.sep)
    path = os.path.join(BASE, "..", ".claude", "skills", "bank-derivative-quoting", "references", *parts)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    return f"# {rel_path} (NOT FOUND)"

skill_path = os.path.join(BASE, "..", ".claude", "skills", "bank-derivative-quoting", "SKILL.md")
with open(skill_path, encoding="utf-8") as f:
    SKILL_MD = f.read()

CTX = {
    "opt_structual_swap": {
        "quotation_format": load_doc("opt_structual_swap_prod/agent_output/quotation_format.md"),
        "motivation_recognition": load_doc("opt_structual_swap_prod/intent_recognition/motivation_recognition.md"),
    },
    "dual_currency_deposit": {
        "quotation_format": load_doc("dual_currency_deposit_prod/agent_output/quotation_format.md"),
        "motivation_recognition": load_doc("dual_currency_deposit_prod/intent_recognition/motivation_recognition.md"),
    },
    "seagull_option": {
        "quotation_format": load_doc("seagull_option_prod/agent_output/quotation_format.md"),
        "motivation_recognition": load_doc("seagull_option_prod/intent_recognition/motivation_recognition.md"),
    },
}

def build_system_prompt(product_key):
    """Build system prompt for a given product."""
    info = CTX[product_key]
    return f"""{SKILL_MD}

## 产品参考文档

### 报价范式
{info['quotation_format']}

### 意图识别
{info['motivation_recognition']}
"""

# ─── Examples ─────────────────────────────────────────────────────────────
EXAMPLES = {
    "结构性掉期 (opt_structual_swap)": {
        "key": "opt_structual_swap",
        "cases": [
            ("A1", "3M 结汇结构性掉期"),
            ("A2", "结构性掉期,结汇,K 定在 7.05"),
            ("A3", "结构性掉期 USDCNY 3M 100pips 结汇 产品报价"),
            ("A4", "2026-09-01 交割的结汇结构性掉期"),
            ("A5", "给我6m交割的结汇结构性掉期，美元和欧元都看下"),
            ("B1", "3M 结汇结构性掉期,我觉得人民币不会贬值到 7.20"),
            ("B2", "结汇结构性掉期,我觉得人民币不会贬值到 7.20"),
            ("B3", "结构性掉期结汇,我觉得未来三个月汇率大概率在 7.00 到 7.10 之间"),
            ("B4", "给我3个月结汇的结构性掉期报价,我觉得未来三个月汇率大概率在 7.00 到 7.10 之间"),
            ("C1", "结构性掉期结汇,K 别太冒险,远一点"),
            ("D1", "结构性掉期,结汇,希望近端补贴 100 点左右"),
            ("D2", "结构性掉期,结汇,希望近端补贴 500 点"),
            ("D3", "半年以内的结构性掉期,希望补贴 80 点"),
            ("E1", "3M 结汇结构性掉期,K 要 7.05"),
            ("F1", "3M 到 1Y 之间的结汇结构性掉期都看一下"),
            ("F2", "3M 结汇结构性掉期,K 从 7.00 到 7.20 扫一下"),
            ("G1", "3M 结构性掉期,结汇和购汇都报一下"),
            ("H1", "刚才那个换成购汇看看"),
            ("I1", "来个结汇结构性掉期"),
            ("J1", "2M 结汇结构性掉期"),
            ("K1", "结构性掉期,希望近端做到 6.90"),
            ("L1", "人民币后面肯定要贬,帮我锁一个 3M 购汇的结构性掉期"),
            ("M1", "结构性掉期,K 给我 10"),
            ("A6", "3个月的结构性掉期结汇，近端补贴500pips"),
            ("A7", "结构性掉期结汇方向，美元人民币，近端补贴500pips"),
            ("N1", "3M 结汇结构性掉期，K 定在 7.05"),
            ("N2", "2026-09-01 交割的结构性掉期结汇，K 做到 7.10"),
            ("O1", "3M 结汇结构性掉期，希望近端补贴 200 点"),
            ("O2", "3M 结汇结构性掉期，希望近端补贴 1000 点"),
            ("P1", "3M 结汇结构性掉期，K 大概 7.05，补贴想做到 300 点左右"),
            ("Q1", "3M 结汇结构性掉期，补贴从 100 到 300 点都看看"),
            ("R1", "3M 结汇结构性掉期，保守一点"),
            ("R2", "6M 购汇结构性掉期，激进一点，补贴多点"),
            ("样1", "我要做一个购汇的结构性掉期，近端我想补贴200个点"),
            ("样2", "给我一个6m的结构性掉期报价，EURCNY，结汇"),
        ]
    },
    "双货币存款 (DCD)": {
        "key": "dual_currency_deposit",
        "cases": [
            ("A1", "DCD,3M 结汇 USDCNY"),
            ("A2", "3M 结汇双货币存款,K 定在 7.20"),
            ("A3", "3M 结汇 DCD,希望补贴收益率 3.5%"),
            ("A4", "双货币存款 USDCNY 3M 100pips 结汇 产品报价"),
            ("A5", "双货币报价"),
            ("B1", "3M 结汇 DCD,我觉得人民币不会贬值到 7.20"),
            ("B2", "3M 结汇 DCD,我觉得未来三个月汇率大概率在 7.10"),
            ("B3", "3M 结汇 DCD,K 设保守一点,我不想太冒险"),
            ("C1", "3M 结汇 DCD,K 定在 7.20,收益率希望 3.5%"),
            ("C2", "结汇 DCD,K 要 7.20,收益率希望 3.5%"),
            ("D1", "3M 结汇 DCD,K 从 7.10 到 7.30 看一下"),
            ("D2", "3M 结汇 DCD,收益率 2% 到 5% 排几档"),
            ("D3", "未来三个月 DCD 结汇 7.0 7.10"),
            ("D4", "3M 结汇 DCD 6.4到7.3震荡"),
            ("E1", "3M 结汇 DCD,激进一点"),
            ("E2", "3M 购汇 DCD,稳一点"),
            ("E3", "3M 结汇 DCD,激进和保守都看看"),
            ("F1", "3M DCD,我觉得人民币不会贬值到 7.2"),
            ("F2", "3M DCD,人民币不会升值到 6.80"),
            ("G1", "3M 结汇 DCD,K 定 7.20,收益率 2% 到 5%"),
            ("H1", "结汇 DCD,1M、3M、6M 都给我报一下"),
            ("H2", "3M DCD,结汇和购汇都看一下"),
            ("I1", "3M 结汇 DCD,收益率 5%"),
            ("I2", "3M 结汇 DCD,收益率 0.035"),
            ("I3", "3M 结汇 DCD,希望补贴 3 个点左右"),
            ("J1", "3M 结汇 DCD,希望到手收益率 3%"),
            ("K1", "来个结汇 DCD"),
            ("K2", "2026-09-01 交割的结汇 DCD"),
            ("L1", "2M 结汇 DCD"),
            ("M1", "刚才那个换成购汇看看"),
            ("N1", "3M 结汇 DCD,希望收益率 50%"),
            ("O1", "我觉得人民币要贬,帮我做个 3M 购汇 DCD"),
        ]
    },
    "海鸥期权 (Seagull)": {
        "key": "seagull_option",
        "cases": [
            ("A1", "海鸥,USDCNY,3M,结汇,给我看看"),
            ("A2", "做个 3M 结汇海鸥,执行价按 7.10 看看"),
            ("A3", "海鸥期权 USDCNY 3M 100pips 结汇 产品报价"),
            ("B1", "3M 结汇海鸥,我觉得人民币不会贬值到 7.20"),
            ("B2", "3M 结汇海鸥,我觉得未来三个月汇率大概率在 7.00 到 7.10"),
            ("B3-X", "3M 结汇海鸥,执行价 7.00 到 7.20 看看"),
            ("B3-Y", "3M 结汇海鸥,汇率大概率在 7.00 到 7.20"),
            ("C1", "我希望 3M 结汇最后能做到 6.90 左右"),
            ("C2", "3M 结汇,6.9"),
            ("D1", "3M,执行价 7.08,收益最好 100 点附近"),
            ("D2", "3M 的,补贴 50 到 150 点排几档"),
            ("E1", "3M 结汇,激进一点"),
            ("E2", "3M 结汇,激进和保守都看看"),
            ("F1", "想做 2 个月结汇,执行价 7.10"),
            ("G1", "USDCNY 结汇,1M、3M、6M 都给我报一下"),
            ("G2", "3M USDCNY,结汇和购汇都看一下"),
            ("H1", "3M 想做到 6.9"),
            ("H2", "2026-09-01 交割的结汇海鸥"),
            ("I1", "3M 结汇,执行价想要 7.10,但最后结汇别差于 6.92"),
            ("J1", "给我来个 3M 结汇,要比直接远期锁好一点"),
            ("J2", "3M 购汇,别让我高过 7.15 就行"),
            ("K1", "你们那个海鸥啊,3 个月的,我就想结汇的时候看着体面点"),
            ("L1", "3M 买汇,贴水 100 个基点"),
            ("M1", "3M 结汇,执行价 6.5,同时补贴 500 点"),
            ("N1", "我觉得人民币后面肯定要贬,帮我锁一个 3M 购汇的海鸥"),
            ("O1", "刚才那个给我换成购汇看看"),
            ("P1", "3M 结汇,补贴给我 2000 点"),
            ("Mini1", "USDCNY 3M 结汇海鸥,给我看看"),
            ("Mini2", "3M 结汇,执行价 7.08,补贴最好 100 点附近"),
            ("Mini3", "USDCNY 结汇海鸥,1M、3M、6M 都报一下"),
        ]
    },
}

# ─── API caller ───────────────────────────────────────────────────────────
def call_model(model_name, user_input, system_prompt, max_retries=2):
    cfg = CFG["models"][model_name]
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

    for attempt in range(max_retries):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=90)
            if resp.status_code == 200:
                data = resp.json()
                # Extract text from content blocks
                content = data.get("content", [])
                texts = []
                for b in content:
                    if b.get("type") == "text":
                        texts.append(b.get("text", ""))
                    elif b.get("type") == "thinking":
                        texts.append(f"[thinking: {b.get('thinking', '')[:300]}...]")
                return {"status": "ok", "output": "\n".join(texts), "raw": json.dumps(data, ensure_ascii=False)[:500]}
            else:
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
                return {"status": "error", "output": f"HTTP {resp.status_code}: {resp.text[:300]}"}
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(3)
                continue
            return {"status": "error", "output": f"Exception: {str(e)}"}

# ─── Main ─────────────────────────────────────────────────────────────────
def main():
    results = []
    results.append("=" * 100)
    results.append(f"Skill Benchmark Report")
    results.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    results.append(f"Models: ds-v4 ({CFG['models']['ds-v4']['model']}), qwen ({CFG['models']['qwen']['model']})")
    results.append("=" * 100)
    results.append("")

    total_cases = sum(len(v["cases"]) for v in EXAMPLES.values())
    processed = 0

    for product_name, product_data in EXAMPLES.items():
        product_key = product_data["key"]
        cases = product_data["cases"]
        system_prompt = build_system_prompt(product_key)

        results.append(f"\n{'#' * 80}")
        results.append(f"# 产品: {product_name}")
        results.append(f"{'#' * 80}\n")

        for label, user_input in cases:
            processed += 1
            results.append(f"\n{'─' * 60}")
            results.append(f"  [{label}] input: {user_input}")
            results.append(f"  ({processed}/{total_cases})")
            results.append(f"{'─' * 60}")

            for model_name in ["ds-v4", "qwen"]:
                print(f"  [{processed}/{total_cases}] {product_name} [{label}] → {model_name} ...", end=" ", flush=True)
                t0 = time.time()
                result = call_model(model_name, user_input, system_prompt)
                elapsed = time.time() - t0
                print(f"{elapsed:.1f}s {'OK' if result['status'] == 'ok' else 'FAIL'}", flush=True)

                results.append(f"\n  --- {model_name} ({elapsed:.1f}s) ---")
                if result["status"] == "ok":
                    results.append(f"  Output:")
                    for line in result["output"].split("\n"):
                        results.append(f"    {line}")
                else:
                    results.append(f"  ERROR: {result['output']}")

                time.sleep(0.5)  # rate limiting

        # Flush after each product
        with open(OUT_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(results))

    # ─── Summary comparison ───────────────────────────────────────────────
    results.append("\n\n")
    results.append("=" * 100)
    results.append("SUMMARY: DS v4 vs Qwen 对比")
    results.append("=" * 100)

    # Re-read results to build summary counts
    ds_ok = 0
    qw_ok = 0
    ds_err = 0
    qw_err = 0
    lines = "\n".join(results)

    # Compare output types for each case
    results.append("\n\n逐项对比:\n")

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(results))

    print(f"\n✅ Benchmark complete. Results saved to: {OUT_PATH}")
    print(f"   Total cases: {total_cases}")
    print(f"   Total API calls: {total_cases * 2}")

if __name__ == "__main__":
    main()
