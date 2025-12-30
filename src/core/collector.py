# src/core/collector.py
"""
代码收集器
"""

import os
import tempfile
import subprocess
from typing import List, Dict, Any
import requests
import json


class CodeCollector:
    """代码收集器"""

    def __init__(self, github_token: str = None):
        self.github_token = github_token
        self.headers = {
            "User-Agent": "CodeQAGenerator/1.0",
            "Accept": "application/vnd.github.v3+json"
        }

        if github_token:
            self.headers["Authorization"] = f"token {github_token}"

    def clone_repository(self, repo_url: str, target_dir: str = None) -> str:
        """
        克隆仓库到本地

        Args:
            repo_url: 仓库URL
            target_dir: 目标目录

        Returns:
            本地路径
        """
        if target_dir is None:
            # 生成临时目录
            repo_name = repo_url.split('/')[-1].replace('.git', '')# 获取当前目录
            current_dir = os.getcwd()

            # 获取上一级目录
            parent_dir = os.path.dirname(current_dir)
            print(parent_dir)

            TEMP_BASE = os.path.join(parent_dir, 'data','raw')
            # 创建临时目录在其他盘
            target_dir = tempfile.mkdtemp(dir=TEMP_BASE, prefix=f"repo_{repo_name}_")

        print(f"📥 克隆: {repo_url}")
        print(f"    到: {target_dir}")

        try:
            result = subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, target_dir],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                print("✅ 克隆成功")
                return target_dir
            else:
                print(f"❌ 克隆失败: {result.stderr[:200]}")
                return None

        except Exception as e:
            print(f"❌ 错误: {e}")
            return None

    def extract_python_files(self, repo_dir: str, max_files: int = 5) -> List[Dict[str, Any]]:
        """
        提取Python文件

        Args:
            repo_dir: 仓库本地路径
            max_files: 最大文件数量

        Returns:
            代码文件列表
        """
        print(f"🔍 从 {repo_dir} 提取Python文件...")

        python_files = []

        for root, dirs, files in os.walk(repo_dir):
            # 跳过.git目录
            if '.git' in root:
                continue

            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)

                    # 跳过测试文件
                    if 'test' in file.lower():
                        continue

                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        if len(content.strip()) < 20:
                            continue

                        rel_path = os.path.relpath(file_path, repo_dir)

                        python_files.append({
                            "path": rel_path,
                            "content": content,
                            "size": len(content),
                            "lines": len(content.split('\n'))
                        })

                        if len(python_files) >= max_files:
                            return python_files

                    except:
                        continue

        print(f"✅ 提取 {len(python_files)} 个Python文件")
        return python_files

    def search_github(self, query: str = "language:python stars:>100", per_page: int = 5) -> List[Dict[str, Any]]:
        """
        搜索GitHub仓库

        Args:
            query: 搜索查询
            per_page: 每页数量

        Returns:
            仓库列表
        """
        if not self.github_token:
            print("⚠️  GitHub Token未设置，无法搜索")
            return []

        print(f"🔍 搜索: {query}")

        try:
            response = requests.get(
                "https://api.github.com/search/repositories",
                params={
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": per_page
                },
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                repos = data.get("items", [])

                print(f"✅ 找到 {len(repos)} 个仓库")
                return repos
            else:
                print(f"❌ 搜索失败: {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ 搜索错误: {e}")

            return []
