# src/simple_test.py
"""
简单测试模块
"""

import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
# src/simple_test.py
"""
修复版简单测试模块
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path


def test_basic_imports():
    """测试基本导入"""
    print("🔧 测试Python导入...")

    try:
        import sys
        import json
        import os
        from pathlib import Path
        print("✅ 基本导入成功")
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False


def test_github_api():
    """测试GitHub API（修复版）"""
    print("\n🐱 测试GitHub API...")

    token = os.getenv("GITHUB_TOKEN")
    if not token or token == "your_github_token_here":
        print("⚠️  GitHub Token未设置，跳过测试")
        return False

    try:
        from github import Github
        from github import Auth

        # 新版本认证方式
        auth = Auth.Token(token)
        g = Github(auth=auth)

        # 使用.get_page()而不是next()
        repos = g.search_repositories("python", sort="stars")

        # 获取第一页的第一个仓库
        first_page = repos.get_page(0)
        if first_page and len(first_page) > 0:
            repo = first_page[0]
            print(f"✅ GitHub API测试成功")
            print(f"   找到仓库: {repo.full_name}")
            print(f"   ⭐ Stars: {repo.stargazers_count}")
            return True
        else:
            print("❌ 没有找到仓库")
            return False

    except Exception as e:
        print(f"❌ GitHub API失败: {type(e).__name__}: {e}")
        return False


def test_openai_api():
    """测试OpenAI API"""
    print("\n🤖 测试OpenAI API...")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("⚠️  OpenAI API Key未设置，跳过测试")
        return False

    try:
        import openai
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        # 简单测试
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "你好，用一句话介绍Python"}],
            max_tokens=50
        )

        answer = response.choices[0].message.content
        print(f"✅ OpenAI API测试成功")
        print(f"   回答: {answer}")
        return True
    except Exception as e:
        print(f"❌ OpenAI API失败: {e}")
        return False


def create_sample_data():
    """创建示例数据"""
    print("\n📄 创建示例数据...")

    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)

    # 创建示例QA
    sample_qa = [
        {
            "question": "Python中如何定义函数？",
            "answer": "使用def关键字，例如: def my_function():",
            "difficulty": "beginner"
        },
        {
            "question": "什么是列表推导式？",
            "answer": "一种简洁创建列表的方法，例如: [x*2 for x in range(10)]",
            "difficulty": "intermediate"
        }
    ]

    # 保存
    current_dir = os.getcwd()
    # 获取上一级目录
    parent_dir = os.path.dirname(current_dir)
    print(parent_dir)
    output_file = os.path.join(parent_dir, 'data','processed', '/sample_qa.json')

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "created_at": datetime.now().isoformat(),
            "samples": sample_qa
        }, f, indent=2, ensure_ascii=False)

    print(f"✅ 创建示例数据: {output_file}")
    return True

def run_simple_test():
    """运行所有测试"""
    print("=" * 40)
    print("    简单测试套件（修复版）")
    print("=" * 40)

    results = []

    # 运行测试
    results.append(("基本导入", test_basic_imports()))
    results.append(("GitHub API", test_github_api()))
    # results.append(("OpenAI API", test_openai_api()))
    results.append(("创建数据", create_sample_data()))

    # 显示结果
    print("\n" + "=" * 40)
    print("📊 测试结果:")
    print("=" * 40)

    passed = 0
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{name:15} {status}")
        if success:
            passed += 1

    print(f"\n总通过率: {passed}/{len(results)}")

    if passed == len(results):
        print("🎉 所有测试通过！")
    else:
        print("⚠️  部分测试失败，请检查配置")


if __name__ == "__main__":
    run_simple_test()
