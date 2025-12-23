# # src/core/parser.py
# import re
# import ast
# from typing import List, Dict, Any
# from dataclasses import dataclass
# from pathlib import Path
#
#
# @dataclass
# class CodeChunk:
#     """代码块"""
#     code: str
#     language: str
#     file_path: str
#     start_line: int
#     end_line: int
#     chunk_type: str = "function"
#
#
# class SimpleCodeParser:
#     """简化的代码解析器"""
#
#     def __init__(self, max_chunk_size: int = 50):
#         self.max_chunk_size = max_chunk_size
#
#     def parse_python_file(self, content: str, file_path: str) -> List[CodeChunk]:
#         """
#         解析Python文件
#
#         Args:
#             content: 文件内容
#             file_path: 文件路径
#
#         Returns:
#             代码块列表
#         """
#         print(f"🔍 解析Python文件: {file_path}")
#
#         chunks = []
#
#         try:
#             # 尝试使用AST解析
#             tree = ast.parse(content)
#
#             for node in ast.walk(tree):
#                 if isinstance(node, ast.FunctionDef):
#                     chunk = self._extract_function(node, content, file_path)
#                     if chunk:
#                         chunks.append(chunk)
#                 elif isinstance(node, ast.ClassDef):
#                     # 处理类中的方法
#                     for subnode in node.body:
#                         if isinstance(subnode, ast.FunctionDef):
#                             chunk = self._extract_function(subnode, content, file_path)
#                             if chunk:
#                                 chunks.append(chunk)
#
#         except SyntaxError as e:
#             print(f"⚠️ AST解析失败，使用简单解析: {e}")
#             chunks = self._simple_parse(content, file_path)
#
#         print(f"📊 解析出 {len(chunks)} 个代码块")
#         return chunks
#
#     def _extract_function(self, node, content: str, file_path: str) -> CodeChunk:
#         """提取函数代码块"""
#         try:
#             # 获取源代码行
#             lines = content.split('\n')
#             start_line = node.lineno - 1  # 转换为0索引
#             end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 1
#
#             # 提取代码
#             function_lines = lines[start_line:end_line]
#
#             # 如果函数太大，截断
#             if len(function_lines) > self.max_chunk_size:
#                 function_lines = function_lines[:self.max_chunk_size]
#                 end_line = start_line + self.max_chunk_size
#
#             function_code = '\n'.join(function_lines)
#
#             return CodeChunk(
#                 code=function_code,
#                 language="python",
#                 file_path=file_path,
#                 start_line=start_line + 1,  # 转换回1索引
#                 end_line=end_line,
#                 chunk_type="function"
#             )
#
#         except Exception as e:
#             print(f"⚠️ 提取函数失败: {e}")
#             return None
#
#     def _simple_parse(self, content: str, file_path: str) -> List[CodeChunk]:
#         """简单解析（正则表达式）"""
#         chunks = []
#         lines = content.split('\n')
#
#         # 查找函数定义
#         function_pattern = r'^\s*def\s+\w+\s*\([^)]*\)\s*:'
#
#         for i, line in enumerate(lines):
#             if re.match(function_pattern, line):
#                 # 找到函数开始
#                 start_line = i
#
#                 # 查找函数结束（通过缩进判断）
#                 current_indent = len(line) - len(line.lstrip())
#
#                 for j in range(i + 1, min(i + self.max_chunk_size, len(lines))):
#                     next_line = lines[j]
#                     if next_line.strip() and len(next_line) - len(next_line.lstrip()) <= current_indent:
#                         end_line = j
#                         break
#                 else:
#                     end_line = min(i + self.max_chunk_size, len(lines))
#
#                 # 提取代码
#                 function_lines = lines[start_line:end_line]
#                 function_code = '\n'.join(function_lines)
#
#                 chunks.append(CodeChunk(
#                     code=function_code,
#                     language="python",
#                     file_path=file_path,
#                     start_line=start_line + 1,
#                     end_line=end_line,
#                     chunk_type="function"
#                 ))
#
#         return chunks

# src/core/parser.py
"""
代码解析器
"""

import re
from typing import List
from dataclasses import dataclass


@dataclass
class CodeChunk:
    """代码块"""
    code: str
    file_path: str
    start_line: int
    end_line: int
    chunk_type: str = "function"


class CodeParser:
    """代码解析器"""

    def parse_python_file(self, content: str, file_path: str) -> List[CodeChunk]:
        """
        解析Python文件

        Args:
            content: 文件内容
            file_path: 文件路径

        Returns:
            代码块列表
        """
        print(f"🔍 解析: {file_path}")

        chunks = []
        lines = content.split('\n')

        # 查找函数定义
        for i, line in enumerate(lines):
            line = line.strip()

            if line.startswith('def '):
                # 找到函数开始
                start_line = i
                func_name = line[4:].split('(')[0].strip()

                # 查找函数结束
                end_line = self._find_function_end(lines, i)

                # 提取代码
                chunk_code = '\n'.join(lines[start_line:end_line])

                chunk = CodeChunk(
                    code=chunk_code,
                    file_path=file_path,
                    start_line=start_line + 1,
                    end_line=end_line,
                    chunk_type="function"
                )

                chunks.append(chunk)
                print(f"  ✅ 提取函数: {func_name} (行 {start_line + 1}-{end_line})")

        if not chunks:
            # 如果没有找到函数，将整个文件作为一个代码块
            chunk = CodeChunk(
                code=content,
                file_path=file_path,
                start_line=1,
                end_line=len(lines),
                chunk_type="file"
            )
            chunks.append(chunk)
            print(f"  ✅ 提取文件内容 (行 1-{len(lines)})")

        return chunks

    def _find_function_end(self, lines: List[str], start_line: int) -> int:
        """
        查找函数结束行

        Args:
            lines: 代码行列表
            start_line: 函数开始行

        Returns:
            函数结束行
        """
        indent = len(lines[start_line]) - len(lines[start_line].lstrip())

        for i in range(start_line + 1, len(lines)):
            current_line = lines[i]
            if current_line.strip():
                current_indent = len(current_line) - len(current_line.lstrip())
                if current_indent <= indent:
                    return i

        return len(lines)