#!/usr/bin/env python3
# run.py
"""
运行脚本 - 最简单的启动方式
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent))


def check_environment():
    """检查环境"""
    print("🔍 检查环境...")

    # 检查Python版本
    print(f"Python版本: {sys.version.split()[0]}")

    # 检查虚拟环境
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 运行在虚拟环境中")
    else:
        print("⚠️  未在虚拟环境中运行")

    return True


def main():
    """主函数"""
    print("=" * 50)
    print("   代码QA生成器")
    print("=" * 50)

    # 1. 检查环境
    if not check_environment():
        return

    # 2. 检查环境变量
    print("\n🔐 检查环境变量...")
    if not os.getenv("GITHUB_TOKEN"):
        print("❌ 请先设置 GITHUB_TOKEN 环境变量")
        print("   1. 复制 .env.example 为 .env")
        print("   2. 在 .env 文件中设置您的GitHub token")
        sys.exit(1)

    # 加载 .env 文件
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env 文件不存在")
        print("请创建 .env 文件，内容参考 .env.example")
        print("在 .env 文件中设置您的GitHub token")
        return



    github_token = os.getenv("GITHUB_TOKEN")
    # openai_key = os.getenv("OPENAI_API_KEY")

    if not github_token or github_token == "your_github_token_here":
        print("❌ GitHub Token 未设置")
        print("请编辑 .env 文件，设置正确的 token")
        return

    # if not openai_key or openai_key == "your_openai_api_key_here":
    #     print("⚠️  OpenAI API Key 未设置，将使用离线模式")

    # 4. 运行简单测试
    print("\n🚀 运行简单测试...")
    try:
        # 导入简单测试
        from src.simple_test import run_simple_test
        run_simple_test()
    except ImportError:
        print("❌ 无法导入测试模块")
        print("请确保项目结构正确")

    print("\n" + "=" * 50)
    print("🎉 启动完成!")
    print("下一步:")
    print("1. 检查上面的输出")
    print("2. 如有错误，按照提示修复")
    print("3. 运行: python run.py")
    print("=" * 50)


if __name__ == "__main__":
    main()