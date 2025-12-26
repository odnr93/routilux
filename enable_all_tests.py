#!/usr/bin/env python
"""
批量启用所有注释掉的测试用例
"""
import re
import os
import sys

def enable_test_in_file(filepath):
    """启用文件中的所有注释测试"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 添加导入语句（如果还没有）
    if 'sys.path.insert' not in content and 'flowforge' in content:
        # 在文件开头添加导入
        import_pattern = r'(^"""[\s\S]*?"""\s*\n)'
        match = re.match(import_pattern, content)
        if match:
            imports = """import sys
import os




"""
            content = match.group(1) + imports + content[match.end():]
    
    # 取消注释测试方法中的代码
    # 匹配模式：以 # 开头的行，后面跟着 assert 或其他代码
    lines = content.split('\n')
    new_lines = []
    in_test_method = False
    indent_level = 0
    
    for i, line in enumerate(lines):
        # 检测是否进入测试方法
        if re.match(r'^\s*def test_', line):
            in_test_method = True
            indent_level = len(line) - len(line.lstrip())
            new_lines.append(line)
            continue
        
        # 检测是否离开测试方法
        if in_test_method:
            current_indent = len(line) - len(line.lstrip()) if line.strip() else indent_level + 1
            if line.strip() and current_indent <= indent_level and not line.strip().startswith('#'):
                in_test_method = False
        
        # 在测试方法中，取消注释
        if in_test_method and line.strip().startswith('#'):
            # 检查是否是注释掉的代码
            if re.match(r'^\s*#\s+(assert|from|import|def |class |\w+\s*=|if |for |while |return |yield )', line):
                # 取消注释
                uncommented = re.sub(r'^(\s*)#\s*', r'\1', line)
                new_lines.append(uncommented)
                continue
        
        new_lines.append(line)
    
    return '\n'.join(new_lines)

def main():
    """主函数"""
    test_dir = os.path.join(os.path.dirname(__file__), 'tests')
    
    test_files = [
        'test_job_state.py',
        'test_flow.py',
        'test_persistence.py',
        'test_integration.py',
        'test_resume.py',
    ]
    
    for test_file in test_files:
        filepath = os.path.join(test_dir, test_file)
        if os.path.exists(filepath):
            print(f"Processing {test_file}...")
            new_content = enable_test_in_file(filepath)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  ✓ Updated {test_file}")
        else:
            print(f"  ✗ File not found: {test_file}")

if __name__ == "__main__":
    main()

