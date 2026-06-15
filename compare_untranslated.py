# -*- coding: utf-8 -*-
import json
import os

with open('untranslated.json', 'r', encoding='utf-8') as f:
    untranslated = json.load(f)

with open('dict_zh.json', 'r', encoding='utf-8') as f:
    dict_zh = json.load(f)

# 我们把 dict_zh 中的所有 old 替换键提出来
dict_keys = set()
for section in ['settings', 'chat', 'workbench']:
    for item in dict_zh.get(section, []):
        dict_keys.add(item[0])

# 检查 untranslated 中的 block 字段，看是否在 dict_keys 中
missing = []
for idx, item in enumerate(untranslated):
    block = item['block']
    # 因为 JSON 中的转义，我们将 block 里的双引号转义为 \"
    # dict_zh 里面也可能是转义了双引号的，我们测试直接匹配，或者做一些基础的清理匹配
    block_escaped = block.replace('"', '\\"')
    
    # 尝试多种匹配可能
    found = False
    for k in dict_keys:
        if block in k or block_escaped in k or k in block or k in block_escaped:
            found = True
            break
    if not found:
        missing.append((idx, item['label'], block))

print(f"Total untranslated: {len(untranslated)}")
print(f"Missing from dict_zh.json: {len(missing)}")
for idx, label, block in missing:
    print(f"  [{idx}] {label} -> {block[:80]}...")
