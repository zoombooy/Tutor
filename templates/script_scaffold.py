"""
Math Video Scene Scaffold
数学教学视频场景脚手架

根据分镜脚本和音频信息生成完整动画

使用方式：
1. 复制此文件为 script.py
2. 根据题目实现 TODO 部分
3. 运行 manim -pqh script.py MathScene

常见问题：
- 渲染卡住：通常是音频文件问题，尝试禁用 add_scene_audio
- deepcopy 错误：不要存储 self 引用到 Mobject 中
- 视频未生成：检查 copy_video_to_root 路径是否正确
"""

from manim import *
import json
import os


class MathScene(Scene):
    """
    数学教学视频场景

    核心原则：
    1. 数学先行 - 先建立正确的数学模型
    2. 音画同步 - 画面等待音频，确保讲解和动画同步
    3. 高亮对应 - 配音提到什么，画面高亮什么
    4. 最小验证 - assert_geometry 只验证关键事实和画布范围
    """

    # ========== 1. 配置参数 ==========
    # 画布配置 (横屏 1920x1080)
    config.pixel_width = 1920
    config.pixel_height = 1080
    config.frame_rate = 60

    # 颜色定义
    COLORS = {
        'background': '#1a1a2e',      # 深蓝背景
        'primary': '#4ecca3',          # 主色（青色）
        'secondary': '#e94560',        # 辅助色（红色）
        'highlight': '#ffc107',        # 高亮色（黄色/金色）
        'text': '#ffffff',             # 文字白色
        'text_secondary': '#aaaaaa',   # 次要文字
        'grid': '#2a2a4e',             # 网格线
        'axis': '#444466',             # 坐标轴
    }

    # ========== 2. 幕信息数组（从分镜读取） ==========
    # 格式：(幕号，幕名，音频文件名，时长秒数)
    # 注意：时长从 audio/audio_info.json 读取
    SCENES = [
        # 示例：(1, "开场", "audio_001_开场.wav", None),
        # TODO: 根据分镜脚本填写
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.audio_dir = "audio"
        self.audio_info_file = os.path.join(self.audio_dir, "audio_info.json")
        self.audio_timings = self._load_audio_timings()

    # ========== 3. 音频管理 ==========
    def _load_audio_timings(self):
        """
        从 audio_info.json 加载音频时长

        返回：dict {幕号：时长秒数}
        """
        timings = {}
        if os.path.exists(self.audio_info_file):
            try:
                with open(self.audio_info_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data.get('files', []):
                        scene_num = item.get('scene')
                        duration = item.get('duration')
                        if scene_num and duration:
                            timings[scene_num] = duration
            except Exception as e:
                print(f"Warning: Failed to load audio info: {e}")

        # 更新 SCENES 数组的时长
        for i, (scene_num, name, audio_file, _) in enumerate(self.SCENES):
            if scene_num in timings:
                self.SCENES[i] = (scene_num, name, audio_file, timings[scene_num])

        return timings

    def add_scene_audio(self, scene_num):
        """
        添加指定幕的音频

        ⚠️ 注意：如果渲染卡住，尝试注释掉 self.add_sound() 行

        使用：在每幕开始时调用 self.add_scene_audio(幕号)
        """
        for sn, name, audio_file, duration in self.SCENES:
            if sn == scene_num:
                audio_path = os.path.join(self.audio_dir, audio_file)
                if os.path.exists(audio_path):
                    # self.add_sound(audio_path)  # 如果卡住，注释这行
                    return duration
                else:
                    print(f"Warning: Audio file not found: {audio_path}")
                    return 0
        return 0

    # ========== 4. 几何计算（必须实现） ==========
    def calculate_geometry(self):
        """
        计算所有几何元素的位置和属性

        坐标系说明（重要）：
        - Manim 使用 3D 坐标系，但本脚手架只使用 2D
        - 所有点的格式：(x, y) - z 坐标始终为 0
        - 建议将几何图形放在 (-5, 5) x (-4, 4) 区域内

        返回：dict 包含所有几何对象的数据
        """
        geometry = {
            'points': {},      # {'A': (x, y), 'B': (x, y), ...}
            'lines': {},       # {'AB': {'start': A, 'end': B, 'length': L}, ...}
            'circles': {},     # {'circle1': {'center': (x, y), 'radius': r}, ...}
            'arcs': {},        # 圆弧定义
            'polygons': {},    # 多边形
        }

        # TODO: 【必须实现】根据题目几何关系计算所有点的坐标
        return geometry

    # ========== 5. 几何验证（必须实现） ==========
    def assert_geometry(self, geometry):
        """
        验证几何计算的正确性（最小验证原则）

        验证内容：
        1. 题目给定的事实（如：两条边相等）
        2. 精度问题：使用相对误差比较
        3. 画布范围检查：确保图形在可视区域内
        """
        def approx_equal(a, b, epsilon=1e-4):
            return abs(a - b) < epsilon

        # TODO: 【必须实现】验证几何计算的正确性

        # 画布范围检查
        def check_canvas_bounds(geometry):
            all_points = list(geometry['points'].values())
            for circle in geometry['circles'].values():
                cx, cy = circle['center']
                r = circle['radius']
                all_points.extend([(cx+r, cy), (cx-r, cy), (cx, cy+r), (cx, cy-r)])

            if not all_points:
                return True

            xs = [p[0] for p in all_points]
            ys = [p[1] for p in all_points]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)

            CANVAS_MIN_X, CANVAS_MAX_X = -6, 6
            CANVAS_MIN_Y, CANVAS_MAX_Y = -5, 5
            MARGIN = 0.5

            assert min_x >= CANVAS_MIN_X + MARGIN, f"图形超出左边界：{min_x}"
            assert max_x <= CANVAS_MAX_X - MARGIN, f"图形超出右边界：{max_x}"
            assert min_y >= CANVAS_MIN_Y + MARGIN, f"图形超出下边界：{min_y}"
            assert max_y <= CANVAS_MAX_Y - MARGIN, f"图形超出上边界：{max_y}"

            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
            assert abs(center_x) < 1.5, f"图形中心偏离 x 轴：{center_x}"
            assert abs(center_y) < 1.0, f"图形中心偏离 y 轴：{center_y}"
            return True

        check_canvas_bounds(geometry)
        print("Geometry validation passed!")

    # ========== 6. 图形元素定义 ==========
    def define_elements(self, geometry):
        """
        定义 Manim 图形对象（但不创建动画）

        返回：dict 包含所有 Manim Mobject
        """
        elements = {
            'points': {},
            'lines': {},
            'circles': {},
            'labels': {},
        }

        # 辅助函数：2D 坐标转 3D（Manim 需要）
        def to_3d(p):
            return (p[0], p[1], 0.0)

        # TODO: 根据分镜需求定义图形元素
        return elements

    # ========== 7. 字幕工具 ==========
    def create_subtitle(self, text, position=DOWN * 3.5):
        """
        创建字幕对象（返回普通 Text，避免 pickle 问题）

        参数:
            text: 字幕文本
            position: 字幕位置（默认底部）

        返回：Text 对象
        """
        subtitle = Text(text, font_size=36, color=self.COLORS['text'])
        subtitle.to_edge(position)
        return subtitle

    def fade_in(self, mobject, run_time=0.5):
        """辅助方法：淡入动画"""
        return FadeIn(mobject, run_time=run_time)

    def fade_out(self, mobject, run_time=0.5):
        """辅助方法：淡出动画"""
        return FadeOut(mobject, run_time=run_time)

    def show_subtitle_timed(self, text, duration, position=DOWN * 3.5, fade_in_time=0.5, fade_out_time=0.5):
        """
        显示字幕并在指定时间后自动退场（避免文字残留）

        参数:
            text: 字幕文本
            duration: 显示总时长（秒），包含淡入淡出时间
            position: 字幕位置
            fade_in_time: 淡入时间
            fade_out_time: 淡出时间

        使用场景：分镜动画中标注了"持续X秒"或"→退场"时
        """
        subtitle = self.create_subtitle(text, position)
        self.play(self.fade_in(subtitle), run_time=fade_in_time)
        self.wait(duration - fade_in_time - fade_out_time)
        self.play(self.fade_out(subtitle), run_time=fade_out_time)
        return subtitle

    def show_subtitle_with_audio(self, text, audio_duration, position=DOWN * 3.5):
        """
        显示字幕并持续到音频结束（适用于幕内主要字幕）

        参数:
            text: 字幕文本
            audio_duration: 音频时长（秒）
            position: 字幕位置
        """
        subtitle = self.create_subtitle(text, position)
        self.play(self.fade_in(subtitle), run_time=0.5)
        self.wait(audio_duration - 1.0)  # 预留退场时间
        self.play(self.fade_out(subtitle), run_time=0.5)
        return subtitle

    # ========== 8. 高亮工具 ==========
    def highlight_element(self, element, color=None, scale=1.3, duration=0.8):
        """高亮指定元素"""
        color = color or self.COLORS['highlight']
        original_color = element.get_color()

        self.play(
            element.animate.scale(scale).set_color(color),
            run_time=0.4
        )
        self.wait(duration - 0.4)
        self.play(
            element.animate.scale(1/scale).set_color(original_color),
            run_time=0.4
        )

    def indicate_equal_lines(self, line1, line2, duration=1.2):
        """指示两条线段相等（同时高亮）"""
        self.play(
            line1.animate.set_color(self.COLORS['highlight']).set_stroke(width=6),
            line2.animate.set_color(self.COLORS['highlight']).set_stroke(width=6),
            run_time=0.5
        )
        self.wait(duration - 0.8)
        self.play(
            line1.animate.set_color(self.COLORS['primary']).set_stroke(width=3),
            line2.animate.set_color(self.COLORS['primary']).set_stroke(width=3),
            run_time=0.5
        )

    # ========== 9. 主流程 ==========
    def construct(self):
        """主构造流程"""
        # 设置背景
        self.camera.background_color = self.COLORS['background']

        # 计算和验证几何
        geometry = self.calculate_geometry()
        self.assert_geometry(geometry)

        # 定义元素
        elements = self.define_elements(geometry)

        # 按场景执行
        for scene_num, scene_name, audio_file, duration in self.SCENES:
            method_name = f"play_scene_{scene_num}"
            if hasattr(self, method_name):
                getattr(self, method_name)(elements, geometry)
            else:
                print(f"Warning: play_scene_{scene_num} not implemented")

        # 拷贝视频到根目录
        self.copy_video_to_root()

    def copy_video_to_root(self):
        """渲染完成后拷贝视频到项目根目录"""
        import shutil
        from pathlib import Path

        scene_name = self.__class__.__name__
        possible_paths = [
            Path(f"media/videos/script/1920p60/{scene_name}.mp4"),
            Path(f"media/videos/script/1080p60/{scene_name}.mp4"),
            Path(f"media/videos/script/720p30/{scene_name}.mp4"),
        ]

        video_src = None
        for path in possible_paths:
            if path.exists():
                video_src = path
                break

        if video_src:
            video_dst = Path(f"{scene_name}.mp4")
            try:
                shutil.copy2(video_src, video_dst)
                print(f"\n✓ 视频已拷贝到：{video_dst.absolute()}")
            except Exception as e:
                print(f"\n⚠️ 视频拷贝失败：{e}")
        else:
            print(f"\n⚠️ 未找到视频文件")


# ========== 使用说明 ==========
"""
关键提醒：
1. 所有几何计算必须在 calculate_geometry() 中完成
2. assert_geometry() 必须检查画布范围
3. 每幕动画时长必须 >= 音频时长
4. 配音提到什么，画面就高亮什么
5. 使用 create_subtitle() 创建字幕，不要用 Subtitle 类
6. 如果渲染卡住，禁用 add_scene_audio 中的 self.add_sound()
7. 所有点坐标使用 2D (x, y)，define_elements 中用 to_3d() 转换
8. 字幕退场：使用 show_subtitle_timed() 或 show_subtitle_with_audio() 确保文字退场
   - 分镜中的 "→" 标记表示退场时机
   - 幕结束前必须让所有文字退场，避免残留到下一幕
"""
