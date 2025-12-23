# # src/core/generator.py
# import json
# import uuid
# from typing import List, Dict, Any
# from dataclasses import dataclass, field
# from datetime import datetime
# import time,re,os
#
# import openai
# from pydantic import BaseModel
#
#
# @dataclass
# class Question:
#     """问题"""
#     text: str
#     type: str = "code_understanding"
#     difficulty: str = "beginner"
#
#
# @dataclass
# class Answer:
#     """答案"""
#     text: str
#     explanation: str = ""
#
#
# @dataclass
# class QAPair:
#     """问答对"""
#     question: Question
#     answer: Answer
#     code: str
#     file_path: str
#     language: str = "python"
#     id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
#
#
# class SimpleQAGenerator:
#     """简化的QA生成器"""
#
#     def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
#         """
#         初始化生成器
#
#         Args:
#             api_key: OpenAI API密钥
#             model: 模型名称
#         """
#         self.client = openai.OpenAI(api_key=api_key)
#         self.model = model
#
#         # 问题模板
#         self.question_templates = [
#             "这段Python代码的功能是什么？",
#             "解释一下这段代码是如何工作的？",
#             "这段代码实现了什么功能？",
#             "这个函数的主要作用是什么？",
#             "这段代码的核心逻辑是什么？"
#         ]
#
#     def generate_for_code(self, code: str, file_path: str, num_questions: int = 2) -> List[QAPair]:
#         """
#         为代码生成问答对
#
#         Args:
#             code: 代码
#             file_path: 文件路径
#             num_questions: 生成的问题数量
#
#         Returns:
#             问答对列表
#         """
#         print(f"🤖 为 {file_path} 生成QA对...")
#
#         qa_pairs = []
#
#         try:
#             # 使用模板生成问题
#             for i in range(min(num_questions, len(self.question_templates))):
#                 template = self.question_templates[i]
#
#                 # 1. 生成更具体的问题
#                 question = self._enhance_question(template, code)
#
#                 # 2. 生成答案
#                 answer = self._generate_answer(question, code)
#
#                 # 3. 创建QA对
#                 qa_pair = QAPair(
#                     question=Question(text=question),
#                     answer=Answer(text=answer),
#                     code=code[:500],  # 限制代码长度
#                     file_path=file_path
#                 )
#
#                 qa_pairs.append(qa_pair)
#                 print(f"  ✓ 生成QA对 {i + 1}/{num_questions}")
#
#                 # 避免API速率限制
#                 time.sleep(1)
#
#         except Exception as e:
#             print(f"❌ 生成QA对失败: {e}")
#
#         return qa_pairs
#
#     def _enhance_question(self, template: str, code: str, file_path: str) -> str:
#         """
#         增强问题，使其更具体
#
#         Args:
#             template: 问题模板
#             code: 代码
#             file_path: 文件路径
#
#         Returns:
#             增强后的问题
#         """
#         # 从文件名中提取信息
#         file_name = file_path.split('/')[-1]
#
#         # 尝试提取函数名
#         function_names = self._extract_function_names(code)
#
#         # 根据模板创建具体问题
#         if "功能" in template or "实现" in template:
#             if function_names:
#                 return f"文件 {file_name} 中的函数 {function_names[0]} 具体实现了什么功能？"
#             else:
#                 return f"文件 {file_name} 的主要功能是什么？"
#
#         elif "工作" in template or "解释" in template:
#             if function_names:
#                 return f"请解释一下函数 {function_names[0]} 的工作流程"
#             else:
#                 return f"请解释 {file_name} 中的代码逻辑"
#
#         elif "作用" in template:
#             if function_names:
#                 return f"函数 {function_names[0]} 在代码中起什么作用？"
#             else:
#                 return f"这段代码的主要作用是什么？"
#
#         elif "核心逻辑" in template:
#             if function_names:
#                 return f"函数 {function_names[0]} 的核心逻辑是什么？"
#             else:
#                 return f"这段代码的核心逻辑是什么？"
#
#         else:
#             # 默认增强
#             if function_names:
#                 return f"关于函数 {function_names[0]}，{template}"
#             else:
#                 return f"关于代码文件 {file_name}，{template}"
#
#     def _generate_answer(self, question: str, code: str) -> str:
#         """
#         生成答案
#
#         Args:
#             question: 问题
#             code: 代码
#
#         Returns:
#             答案文本
#         """
#         try:
#             prompt = f"""
#             请回答以下关于代码的问题：
#
#             代码：
#             python{code[:500]}  # 只取前500字符
#             问题：{question}
#
#             请用中文提供详细的解释，包括：
#             1. 代码的主要功能
#             2. 关键步骤的解释
#             3. 如果有的话，提到重要的函数或变量
#
#             保持回答简洁明了，适合初学者理解。
#             """
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=[
#                     {"role": "system", "content": "你是一个编程专家，擅长用简单语言解释代码。"},
#                     {"role": "user", "content": prompt}
#                 ],
#                 temperature=0.3,
#                 max_tokens=300
#             )
#
#             answer = response.choices[0].message.content.strip()
#             return answer
#
#         except Exception as e:
#             print(f"⚠️ OpenAI API生成答案失败: {e}")
#             return self._generate_answer_offline(question, code)
#
#
#     def _generate_answer_offline(self, question: str, code: str) -> str:
#         """
#         离线生成答案（不使用API）
#
#         Args:
#         question: 问题
#         code: 代码
#
#         Returns:
#         答案文本
#         """
#         # 从代码中提取信息
#         lines = len(code.split('\n'))
#         function_names = self._extract_function_names(code)
#         imports = self._extract_imports(code)
#
#         # 根据问题类型生成不同的答案
#         if "功能" in question or "作用" in question or "实现" in question:
#             if function_names:
#                 functions_str = "、".join(function_names[:2])
#                 if len(function_names) > 2:
#                     functions_str += f" 等 {len(function_names)} 个函数"
#
#                     answer = f"""这段代码定义了 {functions_str}。
#
#                             主要功能包括：
#                             1. 处理输入数据
#                             2. 执行计算或逻辑判断
#                             3. 返回处理结果
#
#                             代码共有 {lines} 行，结构清晰，易于理解。"""
#                 else:
#                     answer = f"""这是一个 {lines} 行的Python脚本，实现了特定的数据处理功能。
#
#                                 主要功能包括：
#                                 1. 数据读取和预处理
#                                 2. 核心计算逻辑
#                                 3. 结果输出
#
#                                 代码逻辑完整，适合学习Python编程。"""
#
#         elif "工作" in question or "解释" in question or "逻辑" in question:
#             if function_names:
#                 main_func = function_names[0] if function_names else "主程序"
#                 answer = f"""代码的工作流程如下：
#
#                         1. 初始化：导入必要的模块{', '.join(imports[:2]) if imports else ''}
#                         2. 数据处理：{main_func}函数接收输入参数
#                         3. 计算逻辑：执行核心算法
#                         4. 结果返回：输出处理后的数据
#
#                         整个流程逻辑清晰，易于跟踪和理解。"""
#             else:
#                 answer = f"""代码执行流程：
#
#                         1. 初始化阶段：设置变量和参数
#                         2. 数据处理：读取和转换输入
#                         3. 核心计算：执行主要算法
#                         4. 结果输出：返回或保存计算结果
#
#                         代码共有 {lines} 行，结构合理，注释清晰。"""
#
#         elif "改进" in question or "优化" in question:
#             answer = f"""可以考虑以下改进：
#
#                 1. 添加错误处理：使用try-except捕获异常
#                 2. 提高性能：优化算法复杂度
#                 3. 增强可读性：添加更多注释
#                 4. 模块化：将功能拆分为更小的函数
#                 5. 添加类型提示：使用类型注解
#
#                 当前代码结构良好，但仍有优化空间。"""
#
#         else:
#             # 通用答案
#             if function_names:
#                 answer = f"""这段代码定义了 {len(function_names)} 个函数，主要用于处理特定业务逻辑。
#
#                     代码特点：
#             - 清晰的函数结构
#             - 适当的代码注释
#             - 合理的逻辑流程
#             - 易于维护的代码风格
#
#             适合作为学习Python编程的参考示例。"""
#             else:
#                 answer = f"""这是一个功能完整的Python脚本，实现了特定的业务需求。
#
#                 代码特点：
#                 - 结构清晰，逻辑完整
#                 - 代码风格一致
#                 - 有基本的错误处理
#                 - 易于理解和扩展
#
#                 适合初学者学习和参考。"""
#
#             return answer
#
#
#     def _extract_function_names(self, code: str) -> List[str]:
#         """
#         从代码中提取函数名
#
#         Args:
#         code: Python代码
#
#         Returns:
#         函数名列表
#         """
#
#
#         function_names = []
#
#         # 使用正则表达式查找函数定义
#         function_pattern = r'^\s*def\s+(\w+)\s*\('
#
#         lines = code.split('\n')
#         for line in lines:
#             match = re.search(function_pattern, line)
#         if match:
#             function_names.append(match.group(1))
#
#         return function_names
#
#
#     def _extract_imports(self, code: str) -> List[str]:
#         """
#         从代码中提取导入语句
#
#         Args:
#         code: Python代码
#
#         Returns:
#         导入语句列表
#         """
#
#
#         imports = []
#
#         import_pattern = r'^\s*(import\s+\w+|from\s+\w+\s+import\s+\w+)'
#
#         lines = code.split('\n')
#         for line in lines:
#             match = re.search(import_pattern, line)
#         if match:
#             imports.append(match.group(1).strip())
#
#         return imports
#
#
#     def save_qa_pairs(self, qa_pairs: List[QAPair], output_path: str):
#         """
#         保存QA对到文件
#
#         Args:
#         qa_pairs: QA对列表
#         output_path: 输出文件路径
#         """
#
#
#         print(f"💾 保存QA对到 {output_path}")
#
#         data = []
#         for qa in qa_pairs:
#             data.append({
#                 "id": qa.id,
#                 "question": qa.question.text,
#                 "answer": qa.answer.text,
#                 "code_preview": qa.code[:200] + "..." if len(qa.code) > 200 else qa.code,
#                 "file_path": qa.file_path,
#                 "language": qa.language,
#                 "generated_at": datetime.now().isoformat()
#             })
#
#         # 保存为JSON
#         with open(output_path, 'w', encoding='utf-8') as f:
#             json.dump(data, f, ensure_ascii=False, indent=2)
#
#         print(f"✅ 已保存 {len(qa_pairs)} 个QA对")
#
#
# # 测试函数
# def test_generator():
#     """测试生成器"""
#     # 检查API密钥
#     api_key = os.getenv("OPENAI_API_KEY")
#
#     generator = SimpleQAGenerator(api_key=api_key, model="gpt-3.5-turbo")
#
#     # 测试代码
#     test_code = """def calculate_average(numbers):
#     \"\"\"计算列表中数字的平均值\"\"\"
#     if not numbers:
#     return 0
#     total = sum(numbers)
#     return total / len(numbers)
#
#     def filter_positive(numbers):
#     \"\"\"过滤出正数\"\"\"
#     return [n for n in numbers if n > 0]
#
#     def process_data(data_list):
#     \"\"\"处理数据列表\"\"\"
#     positive_numbers = filter_positive(data_list)
#     if positive_numbers:
#     return calculate_average(positive_numbers)
#     return 0
#     """
#
#     # 生成QA
#     qa_pairs = generator.generate_for_code(test_code, "math_utils.py", 2)
#
#     # 显示结果
#     if qa_pairs:
#         print("\n📋 生成的QA对:")
#     for i, qa in enumerate(qa_pairs):
#         print(f"\n{i + 1}. 问题: {qa.question.text}")
#     print(f"   答案: {qa.answer.text[:100]}...")
#
#     return qa_pairs
#
# if __name__ == "__main__":
#     test_generator()

# src/core/generator.py
"""
QA生成器
"""

import json
import uuid
import random
import re
from typing import List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Question:
    """问题"""
    text: str
    type: str = "understanding"
    difficulty: str = "beginner"


@dataclass
class Answer:
    """答案"""
    text: str
    explanation: str = ""


@dataclass
class QAPair:
    """问答对"""
    question: Question
    answer: Answer
    code: str
    file_path: str
    language: str = "python"
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])


class FreeQAGenerator:
    """免费的QA生成器"""

    def __init__(self):
        # 问题模板
        self.question_templates = [
            "这段代码的功能是什么？",
            "解释一下这段代码如何工作？",
            "这个函数的主要作用是什么？",
            "代码的核心逻辑是什么？",
            "如何理解这段代码？"
        ]

        # 难度级别
        self.difficulty_levels = {
            "beginner": ["基础", "简单", "入门"],
            "intermediate": ["深入", "详细", "进阶"],
            "advanced": ["高级", "复杂", "专业"]
        }

    def generate_for_code(self, code: str, file_path: str, num_questions: int = 2) -> List[QAPair]:
        """
        为代码生成问答对

        Args:
            code: 代码
            file_path: 文件路径
            num_questions: 问题数量

        Returns:
            问答对列表
        """
        print(f"🤖 生成QA: {file_path}")

        qa_pairs = []

        # 分析代码
        features = self._analyze_code(code)
        file_name = file_path.split('/')[-1]

        for i in range(min(num_questions, len(self.question_templates))):
            template = self.question_templates[i]

            # 生成具体问题
            question_text = self._make_question_specific(template, features, file_name)

            # 生成答案
            answer_text = self._generate_answer(question_text, code, features)

            # 确定难度
            difficulty = self._determine_difficulty(code, features)

            # 创建QA对
            qa_pair = QAPair(
                question=Question(
                    text=question_text,
                    type=self._get_question_type(question_text),
                    difficulty=difficulty
                ),
                answer=Answer(text=answer_text),
                code=code[:300],  # 限制长度
                file_path=file_path
            )

            qa_pairs.append(qa_pair)
            print(f"  ✅ 生成QA {i + 1}")

        return qa_pairs

    def _analyze_code(self, code: str) -> dict:
        """分析代码特征"""
        lines = code.split('\n')

        return {
            "lines": len(lines),
            "functions": re.findall(r'def\s+(\w+)\s*\(', code),
            "imports": re.findall(r'^import\s+|^from\s+', code, re.MULTILINE),
            "has_classes": bool(re.search(r'class\s+\w+', code)),
            "has_loops": bool(re.search(r'for\s+|while\s+', code)),
            "has_conditionals": bool(re.search(r'if\s+|elif\s+|else:', code))
        }

    def _make_question_specific(self, template: str, features: dict, file_name: str) -> str:
        """使问题更具体"""
        if features["functions"]:
            func_name = features["functions"][0]
            if "功能" in template or "作用" in template:
                return f"函数 {func_name} 有什么功能？"
            elif "解释" in template or "工作" in template:
                return f"请解释函数 {func_name} 的工作原理"
            elif "逻辑" in template:
                return f"函数 {func_name} 的核心逻辑是什么？"

        # 使用文件名的通用问题
        if "功能" in template:
            return f"文件 {file_name} 的主要功能是什么？"
        else:
            return f"关于 {file_name} 的代码，{template}"

    def _generate_answer(self, question: str, code: str, features: dict) -> str:
        """生成答案"""
        lines = features["lines"]

        if "功能" in question or "作用" in question:
            if features["functions"]:
                func_names = "、".join(features["functions"][:2])
                return f"这段代码定义了函数 {func_names}，主要用于实现特定的业务逻辑。代码共有 {lines} 行，结构清晰。"
            else:
                return f"这是一个 {lines} 行的Python脚本，实现了特定的数据处理或计算功能。"

        elif "解释" in question or "工作" in question:
            return f"代码的执行流程包括：初始化变量、处理数据、执行计算、返回结果。具体实现取决于业务需求。"

        elif "逻辑" in question:
            return f"核心逻辑是通过算法处理输入数据，生成预期的输出。代码结构合理，易于理解和维护。"

        else:
            return f"这段Python代码实现了特定的功能。代码质量良好，适合作为学习参考。"

    def _determine_difficulty(self, code: str, features: dict) -> str:
        """确定难度级别"""
        lines = features["lines"]

        if lines > 50 or features["has_classes"]:
            return "advanced"
        elif lines > 20 or len(features["functions"]) > 1:
            return "intermediate"
        else:
            return "beginner"

    def _get_question_type(self, question: str) -> str:
        """获取问题类型"""
        if "功能" in question or "作用" in question:
            return "function_understanding"
        elif "解释" in question or "工作" in question:
            return "code_explanation"
        elif "逻辑" in question:
            return "logic_analysis"
        else:
            return "general"