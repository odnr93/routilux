#!/usr/bin/env python
"""
运行所有测试的脚本
"""
import os
import subprocess


def run_tests():
    """运行所有测试"""
    print("=" * 70)
    print("Running FlowForge Test Suite")
    print("=" * 70)
    
    # 运行 pytest
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
        cwd=os.path.dirname(__file__),
        capture_output=False
    )
    
    return result.returncode == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

