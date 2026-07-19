# 示例知识库文档：Python 编程入门指南

> 这是一份用于 RAG 系统演示的示例文档。你可以将本文档上传到系统中，然后对它进行提问。

---

## 1. Python 简介

Python 是一种高级、解释型、面向对象的编程语言。由 Guido van Rossum 于 1991 年首次发布。Python 以其简洁清晰的语法和强大的标准库而闻名。

### 1.1 主要特点
- **简洁易读**：使用缩进来定义代码块，语法接近自然语言
- **跨平台**：支持 Windows、macOS、Linux 等多种操作系统
- **丰富的生态**：拥有超过 40 万个第三方包（PyPI）
- **多范式**：支持面向对象、函数式、过程式编程

### 1.2 应用领域
- Web 开发（Django、FastAPI、Flask）
- 数据科学（NumPy、Pandas、Matplotlib）
- 人工智能与机器学习（PyTorch、TensorFlow、Scikit-learn）
- 自动化运维与测试
- 桌面应用开发

---

## 2. 基础语法

### 2.1 变量与数据类型

Python 是动态类型语言，变量不需要声明类型：

```python
# 基本数据类型
name = "Alice"           # 字符串 str
age = 25                 # 整数 int
height = 1.68            # 浮点数 float
is_student = True        # 布尔值 bool
hobbies = ["阅读", "编程"]  # 列表 list
profile = {"name": "Alice", "age": 25}  # 字典 dict
```

### 2.2 控制流

Python 使用 `if-elif-else` 进行条件判断：

```python
score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "D"
```

循环结构包括 `for` 循环和 `while` 循环：

```python
# for 循环
fruits = ["苹果", "香蕉", "橙子"]
for fruit in fruits:
    print(f"我喜欢吃{fruit}")

# while 循环
count = 0
while count < 5:
    print(f"计数: {count}")
    count += 1
```

---

## 3. 函数与类

### 3.1 函数定义

```python
def greet(name, greeting="你好"):
    """向用户打招呼"""
    return f"{greeting}，{name}！"

# 调用
print(greet("小明"))           # 你好，小明！
print(greet("Alice", "Hello")) # Hello，Alice！
```

### 3.2 面向对象编程

```python
class Animal:
    def __init__(self, name, species):
        self.name = name
        self.species = species

    def make_sound(self):
        return "..."

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name, "犬科")
        self.breed = breed

    def make_sound(self):
        return "汪汪！"

# 使用
buddy = Dog("Buddy", "金毛")
print(f"{buddy.name}是{buddy.breed}，属于{buddy.species}")
print(f"叫声: {buddy.make_sound()}")
```

---

## 4. 常用库介绍

### 4.1 FastAPI
FastAPI 是一个现代、快速的 Python Web 框架，用于构建 API。它基于 Python 类型注解，自动生成交互式 API 文档。

特点：
- 高性能：基于 Starlette 和 Pydantic
- 自动生成 Swagger UI 和 ReDoc 文档
- 内置数据验证和序列化
- 原生支持异步编程

### 4.2 NumPy
NumPy 是 Python 科学计算的基础库，提供高性能的多维数组对象和数学运算工具。

```python
import numpy as np

arr = np.array([1, 2, 3, 4, 5])
print(f"平均值: {arr.mean()}")  # 3.0
print(f"标准差: {arr.std()}")   # 1.414
```

### 4.3 Pandas
Pandas 提供数据分析和数据处理功能，核心数据结构是 DataFrame。

```python
import pandas as pd

df = pd.DataFrame({
    "姓名": ["张三", "李四", "王五"],
    "年龄": [22, 25, 23],
    "城市": ["北京", "上海", "深圳"]
})

print(df.describe())  # 统计描述
```

---

## 5. 最佳实践

1. **遵循 PEP 8 代码风格**：使用 4 空格缩进，每行不超过 79 字符
2. **编写文档字符串**：为函数和类添加清晰的 docstring
3. **使用类型注解**：提高代码可读性和 IDE 支持
4. **异常处理**：使用 try-except 优雅处理错误
5. **编写测试**：使用 pytest 确保代码质量
6. **使用虚拟环境**：隔离项目依赖，避免冲突
7. **版本控制**：使用 Git 管理代码，编写有意义的 commit 信息

---

## 6. 常见问题

### Q: Python 2 和 Python 3 有什么区别？
Python 3 是当前的主要版本（Python 2 已于 2020 年停止支持）。主要区别包括：
- `print` 从语句变为函数
- 整数除法 `/` 默认返回浮点数
- 字符串默认使用 Unicode
- 许多标准库进行了重新组织

### Q: 如何管理项目依赖？
推荐使用以下方案：
1. 创建虚拟环境：`python -m venv venv`
2. 激活虚拟环境后安装依赖
3. 使用 `requirements.txt` 或 `pyproject.toml` 记录依赖
4. 使用 `pip freeze > requirements.txt` 导出当前依赖

### Q: Python 适合做什么类型的项目？
Python 几乎适合所有类型的项目，特别适合：
- 需要快速开发原型的项目
- 数据分析和科学计算
- AI/机器学习项目
- Web 后端开发
- 自动化脚本和工具
