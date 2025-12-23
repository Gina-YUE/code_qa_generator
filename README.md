代码QA数据生成器

📦 一个自动化生成代码问答对的工具，用于训练专有代码助手模型

🚀 功能特性

从GitHub仓库自动收集代码

解析Python代码结构

生成高质量的问答对

支持本地和远程代码分析

易于扩展和定制

📦 安装
1. 克隆仓库
git clone https://github.com/yourusername/code_qa_generator.git
cd code_qa_generator

2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

3. 安装依赖
pip install -r requirements.txt

4. 配置环境变量
复制.env.example为 .env并填入你的GitHub Token：
GITHUB_TOKEN=your_github_token_here

🎯 快速开始
1. 简单测试
python run_simple_fixed.py
2. 完整运行
python src/main.py
3. 自定义配置

编辑 config/default.yaml调整参数：

github:
  max_repositories: 3      # 最大仓库数
  min_stars: 100          # 最小星标数
  languages: ["python"]   # 目标语言

processing:
  max_files_per_repo: 5   # 每个仓库最大文件数
  questions_per_file: 2   # 每个文件生成的问题数

📂 项目结构

code_qa_generator/
├── data/                   # 数据目录
│   ├── datasets/           # 生成的QA数据集
│   ├── processed/          # 处理后的数据
│   └── raw/                # 原始数据
├── src/                    # 源代码
│   ├── core/               # 核心模块
│   │   ├── collector.py    # 代码收集器
│   │   ├── generator.py    # QA生成器
│   │   ├── parser.py       # 代码解析器
│   │   └── validator.py    # 数据验证器
│   ├── storage/            # 存储模块
│   ├── utils/              # 工具函数
│   └── main.py             # 主程序入口
├── config/                 # 配置文件
├── tests/                  # 测试代码
├── scripts/                # 脚本目录
├── .env.example            # 环境变量示例
├── requirements.txt        # Python依赖
└── README.md               # 项目文档


📊 生成的数据格式

{
  "metadata": {
    "repository": "https://github.com/pallets/flask.git",
    "generated_at": "2024-01-15T12:30:00Z",
    "total_qa": 10
  },
  "qa_pairs": [
    {
      "id": "qa_abc123",
      "question": {
        "text": "函数 hello_world 的功能是什么？",
        "type": "function_understanding",
        "difficulty": "beginner"
      },
      "answer": {
        "text": "这个函数打印 'Hello, World!' 消息",
        "explanation": "这是一个简单的示例函数"
      },
      "code": "def hello_world():\n    print('Hello, World!')",
      "file": "example.py",
      "language": "python"
    }
  ]
}

🛠️ 开发指南

如需添加新的问题模板，请编辑 src/core/generator.py中的 question_templates：

self.question_templates = [
    "这段代码的功能是什么？",
    "解释一下这段代码如何工作？",
    # 添加更多模板...
]

📧 联系

如有问题，请联系！