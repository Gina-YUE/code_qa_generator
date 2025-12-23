# # src/core/collector.py
# import os
# import tempfile
# import time
# from pathlib import Path
# from typing import List, Dict, Any
# import logging
# from datetime import datetime
#
# from github import Github
# from git import Repo
#
# logger = logging.getLogger(__name__)
#
#
# class SimpleCodeCollector:
#     """简化的代码收集器"""
#
#     def __init__(self, github_token: str):
#         """
#         初始化收集器
#
#         Args:
#             github_token: GitHub API token
#         """
#         self.github = Github(github_token)
#         self.rate_limit_wait = 60
#
#     def search_repositories(self, query: str = "language:python stars:>100", max_repos: int = 5) -> List[Dict]:
#         """
#         搜索GitHub仓库
#
#         Args:
#             query: GitHub搜索查询
#             max_repos: 最大仓库数量
#
#         Returns:
#             仓库信息列表
#         """
#         print(f"🔍 搜索仓库: {query}")
#
#         repositories = []
#         try:
#             # 搜索仓库
#             result = self.github.search_repositories(query=query, sort="stars", order="desc")
#
#             for i, repo in enumerate(result[:max_repos]):
#                 repo_info = {
#                     "name": repo.full_name,
#                     "url": repo.clone_url,
#                     "stars": repo.stargazers_count,
#                     "forks": repo.forks_count,
#                     "language": repo.language or "Unknown",
#                     "description": repo.description or "No description",
#                     "created_at": repo.created_at.isoformat() if repo.created_at else "",
#                     "updated_at": repo.updated_at.isoformat() if repo.updated_at else ""
#                 }
#                 repositories.append(repo_info)
#                 print(f"  ✓ 找到仓库: {repo.full_name} ({repo.stargazers_count} stars)")
#
#                 # 每处理2个仓库检查一次速率限制
#                 if (i + 1) % 2 == 0:
#                     self._check_rate_limit()
#
#         except Exception as e:
#             print(f"❌ 搜索仓库时出错: {e}")
#
#         return repositories
#
#     def clone_repository(self, repo_url: str, repo_name: str = None) -> str:
#         """
#         克隆仓库到本地
#
#         Args:
#             repo_url: 仓库URL
#             repo_name: 仓库名称
#
#         Returns:
#             本地路径
#         """
#
#         if repo_name is None:
#             repo_name = repo_url.split('/')[-1].replace('.git', '')
#
#
#         # 指定D盘或其他盘的临时目录
#         TEMP_BASE = "E:/QA_project/"  # 或 E:/temp/
#         # 创建临时目录在其他盘
#         temp_dir = tempfile.mkdtemp(dir=TEMP_BASE, prefix="repo_")
#         local_path = Path(temp_dir) / repo_name
#
#         print(f"📥 克隆仓库: {repo_url}")
#         print(f"   保存到: {local_path}")
#
#         try:
#             # 克隆仓库
#             Repo.clone_from(repo_url, str(local_path))
#             print(f"  ✓ 克隆成功")
#             return str(local_path)
#
#         except Exception as e:
#             print(f"❌ 克隆失败: {e}")
#             return None
#
#     def extract_python_files(self, repo_path: str, max_files: int = 20) -> List[Dict]:
#         """
#         提取Python文件
#
#         Args:
#             repo_path: 仓库本地路径
#             max_files: 最大文件数量
#
#         Returns:
#             代码文件列表
#         """
#         print(f"📂 从 {repo_path} 提取Python文件...")
#
#         code_files = []
#         repo_path = Path(repo_path)
#
#         # 查找.py文件
#         python_files = list(repo_path.rglob("*.py"))
#
#         for py_file in python_files[:max_files]:
#             # 跳过测试文件和其他不需要的文件
#             file_str = str(py_file)
#             if any(skip in file_str for skip in ["test", "tests", "__pycache__", ".git"]):
#                 continue
#
#             try:
#                 # 读取文件内容
#                 content = py_file.read_text(encoding='utf-8', errors='ignore')
#
#                 # 跳过空文件或太小的文件
#                 if len(content.strip()) < 10:
#                     continue
#
#                 # 获取相对路径
#                 rel_path = str(py_file.relative_to(repo_path))
#
#                 file_info = {
#                     "path": rel_path,
#                     "content": content,
#                     "size": len(content),
#                     "lines": content.count('\n') + 1,
#                     "language": "python"
#                 }
#                 code_files.append(file_info)
#
#                 print(f"  ✓ 提取文件: {rel_path} ({len(content)} 字符)")
#
#             except Exception as e:
#                 print(f"  ⚠️ 读取文件失败 {py_file}: {e}")
#
#         print(f"📊 共提取 {len(code_files)} 个Python文件")
#         return code_files
#
#     def _check_rate_limit(self):
#         """检查GitHub API速率限制"""
#         try:
#             rate_limit = self.github.get_rate_limit()
#             remaining = rate_limit.core.remaining
#
#             print(f"📊 GitHub API 剩余次数: {remaining}")
#
#             if remaining < 10:
#                 print(f"⚠️ API次数不足，剩余 {remaining}")
#                 if remaining == 0:
#                     reset_time = rate_limit.core.reset
#                     wait_seconds = (reset_time - datetime.now()).total_seconds()
#                     if wait_seconds > 0:
#                         print(f"⏳ 等待 {wait_seconds:.0f} 秒后重试...")
#                         time.sleep(wait_seconds)
#
#         except Exception as e:
#             print(f"⚠️ 检查速率限制时出错: {e}")

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
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            # 指定D盘或其他盘的临时目录
            TEMP_BASE = "E:/QA_project/"  # 或 E:/temp/
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