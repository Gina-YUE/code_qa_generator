#!/usr/bin/env python3
"""
修复版主程序
解决JSON序列化问题
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent))


def qa_pair_to_dict(qa_pair):
    """将QAPair对象转换为字典"""
    return {
        "id": qa_pair.id,
        "question": {
            "text": qa_pair.question.text,
            "type": qa_pair.question.type,
            "difficulty": qa_pair.question.difficulty
        },
        "answer": {
            "text": qa_pair.answer.text,
            "explanation": qa_pair.answer.explanation
        },
        "code": qa_pair.code,
        "file_path": qa_pair.file_path,
        "language": qa_pair.language
    }


def main():
    """主函数"""
    print("=" * 50)
    print("    代码QA数据生成器 (修复版)")
    print("=" * 50)

    from core.collector import CodeCollector
    from core.parser import CodeParser
    from core.generator import FreeQAGenerator

    # 配置
    config = {
        "github_token": os.getenv("GITHUB_TOKEN"),
        "max_repositories": 1,
        "max_files_per_repo": 3,
        "questions_per_file": 2
    }

    print("1. 初始化组件...")
    collector = CodeCollector(config["github_token"])
    parser = CodeParser()
    generator = FreeQAGenerator()

    # 选择仓库
    repo_url = "https://github.com/pallets/flask.git"
    print(f"\n2. 处理仓库: {repo_url}")

    # 克隆仓库
    repo_dir = collector.clone_repository(repo_url)
    if not repo_dir:
        print("❌ 克隆失败")
        return

    all_qa = []

    try:
        # 收集Python文件
        print("\n3. 收集Python文件...")
        python_files = collector.extract_python_files(repo_dir, config["max_files_per_repo"])

        if not python_files:
            print("❌ 没有找到Python文件")
            return

        print(f"✅ 找到 {len(python_files)} 个文件")

        # 处理每个文件
        for file_info in python_files:
            print(f"\n4. 处理: {file_info['path']}")

            # 解析代码
            chunks = parser.parse_python_file(file_info["content"], file_info["path"])

            if chunks:
                # 为每个代码块生成QA
                for chunk in chunks[:1]:  # 只处理第一个代码块
                    qa_pairs = generator.generate_for_code(
                        chunk.code,
                        chunk.file_path,
                        config["questions_per_file"]
                    )
                    all_qa.extend(qa_pairs)

        # 保存结果
        if all_qa:
            # 转换为字典
            qa_dicts = [qa_pair_to_dict(qa) for qa in all_qa]

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"qa_dataset_{timestamp}.json"

            result = {
                "repository": repo_url,
                "generated_at": datetime.now().isoformat(),
                "total_qa": len(all_qa),
                "qa_pairs": qa_dicts
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            print(f"\n✅ 完成！")
            print(f"   生成 {len(all_qa)} 个QA对")
            print(f"   保存到: {output_file}")

            # 显示示例
            print("\n📋 示例:")
            for i, qa_dict in enumerate(qa_dicts[:3], 1):
                print(f"\n{i}. 问题: {qa_dict['question']['text']}")
                print(f"   答案: {qa_dict['answer']['text'][:100]}...")
        else:
            print("❌ 没有生成QA")

    finally:
        # 清理
        if os.path.exists(repo_dir):
            shutil.rmtree(repo_dir, ignore_errors=True)
            print(f"\n🧹 已清理临时目录")


if __name__ == "__main__":
    main()