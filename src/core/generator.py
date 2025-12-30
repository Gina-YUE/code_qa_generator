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
