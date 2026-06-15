# -*- coding: utf-8 -*-
import json
import os
import re

translations_dir = r'e:\2025\APP\20260615\translations'

# 判断字符串是否含有中文字符
def has_chinese(s):
    return len(re.findall(r'[\u4e00-\u9fff]', s)) > 0

# 遍历目录
for root, dirs, files in os.walk(translations_dir):
    for file in files:
        if not file.endswith('.json'):
            continue
        filepath = os.path.join(root, file)
        rel_path = os.path.relpath(filepath, translations_dir)
        print(f"=== Scanning {rel_path} ===")
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"  Error parsing JSON: {e}")
                continue
            
            # 我们递归扫描所有的值
            untranslated = []
            def scan_dict(d, path_prefix=""):
                for k, v in d.items():
                    current_path = f"{path_prefix}.{k}" if path_prefix else k
                    if isinstance(v, dict):
                        scan_dict(v, current_path)
                    elif isinstance(v, str):
                        # 如果值是字符串，且不含有中文字符，并且值里有英文字母 (排除全数字/特殊符号等)
                        if not has_chinese(v) and len(re.findall(r'[a-zA-Z]', v)) > 0:
                            untranslated.append((current_path, v))
            
            scan_dict(data)
            print(f"  Total keys: {len(untranslated) + len(data)}") # 简单估计
            print(f"  Un-translated keys found: {len(untranslated)}")
            for k, v in untranslated[:20]:
                print(f"    - [{k}]: {repr(v)}")
            if len(untranslated) > 20:
                print(f"    - ... and {len(untranslated) - 20} more.")
            print("-" * 40)
