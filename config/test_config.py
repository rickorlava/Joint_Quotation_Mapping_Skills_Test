#!/usr/bin/env python3
"""验证 config/models.yaml 中的模型配置是否可用"""
import yaml, sys, os

# 加载配置
with open("config/models.yaml", encoding="utf-8") as f:
    config = yaml.safe_load(f)

model_name = sys.argv[1] if len(sys.argv) > 1 else config.get("default_model", "ds-v4")
model_cfg = config["models"].get(model_name)
if not model_cfg:
    print(f"❌ 未知模型: {model_name}")
    sys.exit(1)

print(f"正在测试: {model_name}")
print(f"  endpoint: {model_cfg['base_url']}")
print(f"  model:    {model_cfg['model']}")

# 构造 Anthropic Messages API 请求
headers = {
    "x-api-key": model_cfg["api_key"],
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}
payload = {
    "model": model_cfg["model"],
    "max_tokens": 128,
    "messages": [{"role": "user", "content": "回复'ok'"}]
}

import requests, json
try:
    url = model_cfg["base_url"].rstrip("/") + "/messages"
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    if resp.status_code == 200:
        content = resp.json().get("content", [])
        text = "".join(b.get("text","") for b in content if b.get("type")=="text")
        print(f"  ✅ 响应成功: {text.strip()}")
    else:
        print(f"  ❌ HTTP {resp.status_code}: {resp.text[:200]}")
except Exception as e:
    print(f"  ❌ 连接失败: {e}")
