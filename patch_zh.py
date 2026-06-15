# -*- coding: utf-8 -*-
"""
Antigravity IDE 简体中文汉化补丁脚本
"""

import shutil
import os
import sys
import json
import hashlib
import base64


def find_base_path():
    # macOS 候选路径
    if sys.platform != 'win32':
        candidates = [
            '/Applications/Antigravity.app/Contents/Resources/app',
            os.path.expanduser('~/Applications/Antigravity.app/Contents/Resources/app')
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        return candidates[0]

    # Windows 候选路径列表
    local_app_data = os.environ.get('LOCALAPPDATA', '')
    candidates = [
        os.path.join(local_app_data, 'Programs', 'antigravity', 'resources', 'app'),
        r'D:\Programs\Antigravity IDE\resources\app',
        r'C:\Program Files\Antigravity\resources\app',
    ]

    # 动态检测运行中进程
    try:
        import subprocess
        cmd = ['wmic', 'process', 'where', "name='Antigravity IDE.exe'", 'get', 'ExecutablePath']
        # 避免在无 GUI 情况下弹窗
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        output = subprocess.check_output(cmd, startupinfo=si).decode('gbk', errors='ignore')
        for line in output.splitlines():
            line = line.strip()
            if line and line.endswith('.exe'):
                p = os.path.join(os.path.dirname(line), 'resources', 'app')
                if os.path.exists(p):
                    candidates.insert(0, p)
                    break
    except Exception:
        pass

    # 如果有命令行参数指定路径
    for arg in sys.argv:
        if arg.startswith('--path='):
            p = arg.split('=', 1)[1]
            if os.path.exists(p):
                return p

    for c in candidates:
        if os.path.exists(c):
            return c

    return candidates[0]


BASE = find_base_path()
TARGETS = {
    'settings': os.path.join(BASE, 'out', 'jetskiAgent', 'main.js'),
    'chat': os.path.join(BASE, 'out', 'main.js'),
    'workbench': os.path.join(BASE, 'out', 'vs', 'workbench', 'workbench.desktop.main.js'),
}
PRODUCT_JSON = os.path.join(BASE, 'product.json')


def load_dict():
    dict_path = os.path.join(os.path.dirname(__file__), 'dict_zh.json')
    if not os.path.exists(dict_path):
        # 兼容当前执行目录
        dict_path = 'dict_zh.json'
    if not os.path.exists(dict_path):
        print(f"  ❌ 找不到翻译字典文件 dict_zh.json")
        return {}
    with open(dict_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 动态加载翻译对照表
_DICT = load_dict()

def get_settings_replacements():
    return _DICT.get('settings', [])

def get_chat_replacements():
    return _DICT.get('chat', [])

def get_workbench_replacements():
    return _DICT.get('workbench', [])


def patch_file(filepath, replacements, name):
    """对单个文件应用替换"""
    backup = filepath + '.bak'

    if not os.path.exists(filepath):
        print(f'  ❌ 文件不存在: {filepath}')
        return 0

    # Backup
    if not os.path.exists(backup):
        shutil.copy2(filepath, backup)
        print(f'  ✅ 已备份: {os.path.basename(backup)}')
    else:
        # 从备份恢复，保证是干净 of 源文件进行替换，从而支持多次运行并实现 100% 匹配
        shutil.copy2(backup, filepath)
        print(f'  🔄 已从备份恢复原文件: {os.path.basename(filepath)}')

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    count = 0
    failed = []

    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            count += 1
        else:
            # 优化：如果在 content 中没有找到 old，但是找到了 new，
            # 说明这处词条已经由于前置的更长匹配（或之前运行的补丁）被汉化了，这并不是未匹配的错误。
            if new in content:
                count += 1
            else:
                failed.append(old[:50])

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'  🎉 {name}: 成功替换 {count}/{len(replacements)} 处')
    if failed:
        print(f'  ⚠️  未匹配 {len(failed)} 处:')
        for f_str in failed:
            print(f'    - {f_str}...')
    return count



def update_checksums():
    """更新 product.json 中的文件校验值，消除'安装似乎损坏'提示"""
    if not os.path.exists(PRODUCT_JSON):
        print('  ⚠️  product.json 不存在，跳过 checksum 更新')
        return

    # Backup
    backup = PRODUCT_JSON + '.bak'
    if not os.path.exists(backup):
        shutil.copy2(PRODUCT_JSON, backup)

    with open(PRODUCT_JSON, 'r', encoding='utf-8') as f:
        product = json.load(f)

    checksums = product.get('checksums', {})
    updated = 0
    for key in checksums:
        for prefix in [f'{BASE}/out/', f'{BASE}/']:
            filepath = prefix + key
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    data = f.read()
                new_hash = base64.b64encode(hashlib.sha256(data).digest()).decode('ascii').rstrip('=')
                if new_hash != checksums[key]:
                    checksums[key] = new_hash
                    updated += 1
                break

    if updated > 0:
        product['checksums'] = checksums
        with open(PRODUCT_JSON, 'w', encoding='utf-8') as f:
            json.dump(product, f, indent='\t', ensure_ascii=False)
        print(f'  ✅ 已更新 {updated} 个文件校验值')
    else:
        print('  ⏭️  校验值无需更新')



def clear_cache():
    """清空 V8 编译和页面缓存以强迫 IDE 加载汉化后的 JS 文件"""
    app_data = os.environ.get('APPDATA', '')
    if not app_data:
        return

    folders = ['Antigravity', 'Antigravity IDE']
    subfolders = ['CachedData', 'Code Cache', 'Cache', 'clp']

    cleaned = []
    for f in folders:
        for sf in subfolders:
            target_path = os.path.join(app_data, f, sf)
            if os.path.exists(target_path):
                try:
                    shutil.rmtree(target_path, ignore_errors=False)
                    cleaned.append(f"{f}/{sf}")
                except Exception:
                    pass

    if cleaned:
        print('  🧹 已清理以下缓存:')
        for item in cleaned:
            print(f'    - {item}')
    else:
        print('  ⏭️  无缓存需要清理')



def patch_nls_messages():
    """直接汉化 nls.messages.json 中的词条，这在 NLS 机制下具有最高优先级"""
    nls_path = os.path.join(BASE, 'nls.messages.json')
    if not os.path.exists(nls_path):
        nls_path = os.path.join(BASE, 'out', 'nls.messages.json')
        if not os.path.exists(nls_path):
            print('  ⚠️  nls.messages.json 不存在，跳过 NLS 汉化')
            return False

    backup = nls_path + '.bak'
    if not os.path.exists(backup):
        shutil.copy2(nls_path, backup)
        print(f'  ✅ 已备份: {os.path.basename(backup)}')

    try:
        with open(nls_path, 'r', encoding='utf-8') as f:
            msgs = json.load(f)

        replacements = {
            'Provide &&Feedback': '提供反馈(&&F)',
            'Provide Feedback': '提供反馈',
            'Download Diagnostics': '下载诊断信息',
            'Docs': '文档',
            'Report Issue': '报告问题',
            'Changelog': '更新日志',
            'Quick Settings Panel': '快速设置面板',
            'Open {0} User Settings': '{0} 设置',
            '{0} files changed': '{0} 个修改的文件'
        }

        modified = 0
        for i in range(len(msgs)):
            val = msgs[i]
            if isinstance(val, str) and val in replacements:
                msgs[i] = replacements[val]
                modified += 1

        if modified > 0:
            with open(nls_path, 'w', encoding='utf-8') as f:
                json.dump(msgs, f, ensure_ascii=False)
            print(f'  🎉 nls.messages.json: 成功汉化 {modified} 处系统菜单词条')
            return True
        else:
            print('  ⏭️  nls.messages.json 菜单词条已是汉化状态')
            return True
    except Exception as e:
        print(f'  ❌ nls.messages.json 汉化失败: {e}')
        return False



def apply_patch():
    """应用汉化补丁"""
    total = 0

    print('📦 [1/5] 汉化 Settings 面板 (jetskiAgent/main.js)...')
    total += patch_file(TARGETS['settings'], get_settings_replacements(), 'Settings')

    print()
    print('📦 [2/5] 汉化 Agent 聊天面板 (chat.js)...')
    total += patch_file(TARGETS['chat'], get_chat_replacements(), 'Chat')

    print()
    print('📦 [3/5] 汉化快速设置面板 (workbench.desktop.main.js)...')
    total += patch_file(TARGETS['workbench'], get_workbench_replacements(), 'Workbench')

    print()
    print('📦 [4/5] 汉化系统 NLS 消息包 (nls.messages.json)...')
    patch_nls_messages()

    print()
    print('📦 [5/5] 更新文件校验值 (消除"安装损坏"提示)...')
    update_checksums()

    print()
    print('🧹 [清理缓存] 清空渲染进程和 V8 编译缓存...')
    clear_cache()

    print(f'\n🎉 全部完成！共替换 {total} 处 JS 代码')
    print('📌 请完全退出 Antigravity (Cmd+Q) 后重新打开即可生效')



def revert_patch():
    """恢复所有原文件"""
    for name, filepath in TARGETS.items():
        backup = filepath + '.bak'
        if os.path.exists(backup):
            shutil.copy2(backup, filepath)
            print(f'  ✅ 已恢复: {name} ({os.path.basename(filepath)})')
        else:
            print(f'  ⏭️  无需恢复 (无备份): {name}')

    # Restore nls.messages.json
    nls_paths = [
        os.path.join(BASE, 'nls.messages.json'),
        os.path.join(BASE, 'out', 'nls.messages.json')
    ]
    for nls_p in nls_paths:
        nls_bak = nls_p + '.bak'
        if os.path.exists(nls_bak):
            shutil.copy2(nls_bak, nls_p)
            print(f'  ✅ 已恢复: {os.path.basename(nls_p)}')

    # Restore product.json
    pj_backup = PRODUCT_JSON + '.bak'
    if os.path.exists(pj_backup):
        shutil.copy2(pj_backup, PRODUCT_JSON)
        print(f'  ✅ 已恢复: product.json')

    clear_cache()
    print('📌 请完全退出 Antigravity (Cmd+Q) 后重新打开即可生效')



if __name__ == '__main__':
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            pass

    if '--revert' in sys.argv:
        revert_patch()
    else:
        apply_patch()
