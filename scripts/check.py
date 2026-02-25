#!/usr/bin/env python3
"""
Manim 教学视频代码检查脚本
验证 script.py 是否包含必要的函数和结构

使用方法:
    python scripts/check.py [script_file]

默认检查 script.py，也可以指定其他文件
"""

import ast
import sys
import os
from pathlib import Path


def safe_print(text):
    """安全打印，处理 Windows 控制台编码问题"""
    try:
        print(text)
    except UnicodeEncodeError:
        # 替换特殊符号
        replacements = {
            '✓': '[OK]',
            '✅': '[OK]',
            '⚠️': '[WARN]',
            '❌': '[ERROR]',
            '✗': '[FAIL]',
            '🔍': '[CHECK]',
            '🎬': '[NEXT]',
            '⛔': '[STOP]',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        print(text)


class CodeChecker:
    """代码结构检查器"""

    # 必须包含的函数
    REQUIRED_FUNCTIONS = [
        'calculate_geometry',
        'assert_geometry',
        'define_elements',
    ]

    # 推荐包含的函数（警告但不阻止）
    RECOMMENDED_FUNCTIONS = [
        'play_scene',
    ]

    # 必须包含的类（内部类也算）
    REQUIRED_CLASSES = [
        'Subtitle',
        'TitleSubtitle',
    ]

    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.errors = []
        self.warnings = []
        self.tree = None
        self.classes = {}  # 类名 -> 方法列表

    def parse(self):
        """解析 Python 文件"""
        if not self.file_path.exists():
            self.errors.append(f"文件不存在: {self.file_path}")
            return False

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.tree = ast.parse(content)
            return True
        except SyntaxError as e:
            self.errors.append(f"语法错误: {e}")
            return False
        except Exception as e:
            self.errors.append(f"解析失败: {e}")
            return False

    def analyze(self):
        """分析代码结构"""
        if not self.tree:
            return

        # 遍历顶层定义
        for node in ast.iter_child_nodes(self.tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                methods = []
                inner_classes = []

                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append(item.name)
                    elif isinstance(item, ast.ClassDef):
                        inner_classes.append(item.name)
                        # 也记录内部类的方法
                        inner_methods = [n.name for n in item.body
                                        if isinstance(n, ast.FunctionDef)]
                        self.classes[f"{class_name}.{item.name}"] = inner_methods

                self.classes[class_name] = methods

    def check_required_functions(self):
        """检查必需函数是否存在"""
        all_methods = set()
        for class_name, methods in self.classes.items():
            all_methods.update(methods)

        for func_name in self.REQUIRED_FUNCTIONS:
            if func_name not in all_methods:
                self.errors.append(
                    f"缺少必需函数: {func_name}()\n"
                    f"  请在 MathScene 类中实现此方法\n"
                    f"  作用: {self._get_function_description(func_name)}"
                )

    def check_recommended_functions(self):
        """检查推荐函数"""
        all_methods = set()
        for class_name, methods in self.classes.items():
            all_methods.update(methods)

        for func_name in self.RECOMMENDED_FUNCTIONS:
            if func_name not in all_methods:
                self.warnings.append(
                    f"缺少推荐函数: {func_name}()\n"
                    f"  建议实现以更好地控制每幕动画"
                )

    def check_subtitle_classes(self):
        """检查字幕类是否存在"""
        # 检查 Subtitle 和 TitleSubtitle 是否作为内部类定义
        found_subtitle = False
        found_title = False

        for class_name in self.classes.keys():
            if '.' in class_name:
                outer, inner = class_name.split('.')
                if inner == 'Subtitle':
                    found_subtitle = True
                if inner == 'TitleSubtitle':
                    found_title = True

        if not found_subtitle:
            self.warnings.append(
                "未找到 Subtitle 类\n"
                "  建议: 从 templates/script_scaffold.py 复制 Subtitle 类定义\n"
                "  作用: 避免忘记渲染/退场导致的文字残留问题"
            )

        if not found_title:
            self.warnings.append(
                "未找到 TitleSubtitle 类\n"
                "  建议: 从 templates/script_scaffold.py 复制 TitleSubtitle 类定义"
            )

    def check_scene_class(self):
        """检查是否有场景类继承自 Scene"""
        found_scene = False
        for node in ast.iter_child_nodes(self.tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == 'Scene':
                        found_scene = True
                        break
                    elif isinstance(base, ast.Attribute):
                        if base.attr == 'Scene':
                            found_scene = True
                            break

        if not found_scene:
            self.errors.append(
                "未找到继承自 Scene 的类\n"
                "  必须有一个类继承自 Scene，例如: class MathScene(Scene):"
            )

    def check_add_sound(self):
        """检查是否有 add_sound 调用（音频集成）"""
        has_add_sound = False

        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == 'add_sound':
                        has_add_sound = True
                        break
                elif isinstance(node.func, ast.Name):
                    if node.func.id == 'add_sound':
                        has_add_sound = True
                        break

        if not has_add_sound:
            self.warnings.append(
                "未检测到 add_sound() 调用\n"
                "  提醒: 每幕动画应该添加对应的音频文件\n"
                "  示例: self.add_sound('audio/audio_001_开场.wav')"
            )

    def _get_function_description(self, func_name):
        """获取函数描述"""
        descriptions = {
            'calculate_geometry': '计算所有几何元素（点、线、圆）的坐标和属性',
            'assert_geometry': '验证几何计算的正确性和画布范围',
            'define_elements': '定义 Manim 图形对象（点、线、圆等）',
        }
        return descriptions.get(func_name, '未知功能')

    def run(self):
        """运行所有检查"""
        safe_print(f"🔍 检查文件: {self.file_path}")
        safe_print("=" * 50)

        # 解析
        if not self.parse():
            return False

        # 分析
        self.analyze()

        # 各项检查
        self.check_scene_class()
        self.check_required_functions()
        self.check_recommended_functions()
        self.check_subtitle_classes()
        self.check_add_sound()

        # 输出结果
        return self.report()

    def report(self):
        """输出检查报告"""
        success = len(self.errors) == 0

        # 错误
        if self.errors:
            safe_print("\n❌ 错误 (必须修复):")
            for i, error in enumerate(self.errors, 1):
                safe_print(f"\n  {i}. {error}")

        # 警告
        if self.warnings:
            safe_print("\n⚠️  警告 (建议修复):")
            for i, warning in enumerate(self.warnings, 1):
                safe_print(f"\n  {i}. {warning}")

        # 成功信息
        if success and not self.warnings:
            safe_print("\n✅ 所有检查通过！可以开始渲染。")
        elif success:
            safe_print("\n✅ 必要检查通过，但有警告建议处理。")

        safe_print("\n" + "=" * 50)

        if success:
            safe_print("🎬 下一步: 运行渲染命令")
            safe_print(f"   manim -pqh {self.file_path} MathScene")
        else:
            safe_print("⛔ 检查失败，请修复错误后重试。")

        return success


def main():
    """主函数"""
    # 获取要检查的文件
    if len(sys.argv) > 1:
        script_file = sys.argv[1]
    else:
        script_file = "script.py"

    # 检查文件路径
    script_path = Path(script_file)

    # 运行检查
    checker = CodeChecker(script_path)
    success = checker.run()

    # 返回退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
