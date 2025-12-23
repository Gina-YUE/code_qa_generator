# src/config.py
import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

@dataclass
class GitHubConfig:
    """GitHub配置"""
    token: str = field(default_factory=lambda: os.getenv("GITHUB_TOKEN", ""))
    min_stars: int = 100
    max_repositories: int = 10
    languages: list = field(default_factory=lambda: ["python", "javascript"])

@dataclass
class OpenAIConfig:
    """OpenAI配置"""
    api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    model: str = "gpt-3.5-turbo"  # 先用便宜的模型测试
    temperature: float = 0.7

@dataclass
class ProcessingConfig:
    """处理配置"""
    max_chunk_size: int = 50
    questions_per_chunk: int = 2
    output_dir: str = "./data/datasets"


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_path: str = None):
        self.github = GitHubConfig()
        self.openai = OpenAIConfig()
        self.processing = ProcessingConfig()

        if config_path and Path(config_path).exists():
            self.load_from_yaml(config_path)

    def load_from_yaml(self, config_path: str):
        """从YAML文件加载配置"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)

        if not config_data:
            return

        # 更新GitHub配置
        if 'github' in config_data:
            for key, value in config_data['github'].items():
                if hasattr(self.github, key):
                    setattr(self.github, key, value)

        # 更新OpenAI配置
        if 'openai' in config_data:
            for key, value in config_data['openai'].items():
                if hasattr(self.openai, key):
                    setattr(self.openai, key, value)

        # 更新处理配置
        if 'processing' in config_data:
            for key, value in config_data['processing'].items():
                if hasattr(self.processing, key):
                    setattr(self.processing, key, value)

    def validate(self) -> bool:
        """验证配置"""
        if not self.github.token:
            print("❌ 错误：GITHUB_TOKEN 未设置")
            return False

        if not self.openai.api_key:
            print("⚠️ 警告：OPENAI_API_KEY 未设置，部分功能将受限")

        return True