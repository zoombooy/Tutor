"""
示例：三角形内角和证明
完整可运行的 Manim 脚本，演示脚手架的使用方法

使用：
    manim -pqh script_example.py TriangleAngleSum

输入文件：
    - audio/audio_info.json
    - audio/audio_001_开场.wav
    - audio/audio_002_画三角形.wav
    - ...
"""

from manim import *
import json
import os
import numpy as np


class TriangleAngleSum(Scene):
    """
    三角形内角和证明动画
    演示：通过平行线证明三角形内角和为180度
    """

    # ========== 配置 ==========
    config.pixel_width = 1080
    config.pixel_height = 1920
    config.frame_rate = 60

    # 颜色定义
    COLORS = {
        'background': '#1a1a2e',
        'primary': '#4ecca3',      # 青色 - 主要线条
        'secondary': '#e94560',    # 红色 - 辅助线
        'highlight': '#ffc107',    # 黄色 - 高亮
        'text': '#ffffff',
        'angle_a': '#ff6b6b',      # 红色系 - 角A
        'angle_b': '#4ecdc4',      # 青色系 - 角B
        'angle_c': '#ffe66d',      # 黄色系 - 角C
    }

    # 幕信息
    SCENES = [
        (1, "开场", "audio_001_开场.wav", None),
        (2, "画三角形", "audio_002_画三角形.wav", None),
        (3, "标角度", "audio_003_标角度.wav", None),
        (4, "画平行线", "audio_004_画平行线.wav", None),
        (5, "证明", "audio_005_证明.wav", None),
        (6, "总结", "audio_006_总结.wav", None),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.audio_dir = "audio"
        self.audio_info_file = os.path.join(self.audio_dir, "audio_info.json")
        self.audio_timings = self._load_audio_timings()

    # ========== 音频管理 ==========
    def _load_audio_timings(self):
        """加载音频时长"""
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
                print(f"Warning: 加载音频信息失败: {e}")

        # 更新 SCENES
        for i, (scene_num, name, audio_file, _) in enumerate(self.SCENES):
            if scene_num in timings:
                self.SCENES[i] = (scene_num, name, audio_file, timings[scene_num])

        return timings

    def get_scene_duration(self, scene_num):
        """获取幕时长"""
        return self.audio_timings.get(scene_num, 5.0)

    def add_scene_audio(self, scene_num):
        """添加音频"""
        for sn, name, audio_file, duration in self.SCENES:
            if sn == scene_num:
                audio_path = os.path.join(self.audio_dir, audio_file)
                if os.path.exists(audio_path):
                    self.add_sound(audio_path)
                    return duration or 5.0
                else:
                    print(f"Warning: 音频不存在: {audio_path}")
                    return 5.0
        return 5.0

    # ========== 几何计算 ==========
    def calculate_geometry(self):
        """
        计算三角形几何信息

        三角形ABC，A在顶部，BC水平在底部
        """
        # 三角形顶点（适配竖屏）
        A = np.array([0, 2, 0])
        B = np.array([-3, -2, 0])
        C = np.array([3, -2, 0])

        # 计算边长
        def dist(p1, p2):
            return np.linalg.norm(p1 - p2)

        AB = dist(A, B)
        AC = dist(A, C)
        BC = dist(B, C)

        # 计算角度（弧度）
        def angle_at(p_vertex, p1, p2):
            v1 = p1 - p_vertex
            v2 = p2 - p_vertex
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            return np.arccos(np.clip(cos_angle, -1, 1))

        angle_A = angle_at(A, B, C)  # 弧度
        angle_B = angle_at(B, A, C)
        angle_C = angle_at(C, A, B)

        # 过A点作BC的平行线（用于证明）
        # 平行线方向与BC相同
        parallel_direction = (C - B) / np.linalg.norm(C - B)
        parallel_start = A - parallel_direction * 4
        parallel_end = A + parallel_direction * 4

        geometry = {
            'points': {'A': A, 'B': B, 'C': C},
            'lines': {
                'AB': {'start': A, 'end': B, 'length': AB},
                'AC': {'start': A, 'end': C, 'length': AC},
                'BC': {'start': B, 'end': C, 'length': BC},
                'parallel': {'start': parallel_start, 'end': parallel_end},
            },
            'angles': {
                'A': {'value': angle_A, 'deg': np.degrees(angle_A)},
                'B': {'value': angle_B, 'deg': np.degrees(angle_B)},
                'C': {'value': angle_C, 'deg': np.degrees(angle_C)},
            },
        }

        return geometry

    # ========== 几何验证 ==========
    def assert_geometry(self, geometry):
        """验证几何计算"""
        # 1. 验证三角形内角和 ≈ 180度
        angles = geometry['angles']
        total_deg = angles['A']['deg'] + angles['B']['deg'] + angles['C']['deg']
        assert abs(total_deg - 180) < 0.1, f"内角和错误: {total_deg}"

        # 2. 验证画布范围
        points = list(geometry['points'].values())
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]

        assert max(abs(x) for x in xs) < 5, "图形超出水平范围"
        assert max(abs(y) for y in ys) < 4, "图形超出垂直范围"

        # 3. 验证中心位置
        center_x = (min(xs) + max(xs)) / 2
        assert abs(center_x) < 1, "图形中心偏离"

        print(f"✓ 几何验证通过 (内角和: {total_deg:.1f}°)")

    # ========== 图形元素定义 ==========
    def define_elements(self, geometry):
        """定义 Manim 图形元素"""
        pts = geometry['points']
        elements = {
            'points': {},
            'lines': {},
            'angles': {},
            'labels': {},
        }

        # 点
        for name, coord in pts.items():
            elements['points'][name] = Dot(
                point=coord,
                color=self.COLORS['text'],
                radius=0.1
            )
            elements['labels'][name] = MathTex(name).next_to(
                elements['points'][name],
                UP if name == 'A' else (DOWN + LEFT if name == 'B' else DOWN + RIGHT),
                buff=0.2
            ).set_color(self.COLORS['text'])

        # 边
        lines_cfg = geometry['lines']
        for name, cfg in lines_cfg.items():
            if name == 'parallel':
                # 平行线用虚线
                elements['lines'][name] = DashedLine(
                    start=cfg['start'],
                    end=cfg['end'],
                    color=self.COLORS['secondary'],
                    dash_length=0.2
                )
            else:
                elements['lines'][name] = Line(
                    start=cfg['start'],
                    end=cfg['end'],
                    color=self.COLORS['primary'],
                    stroke_width=4
                )

        # 角度标记（Sector）
        angle_colors = {
            'A': self.COLORS['angle_a'],
            'B': self.COLORS['angle_b'],
            'C': self.COLORS['angle_c'],
        }

        # 角A
        elements['angles']['A'] = Sector(
            outer_radius=0.8,
            angle=geometry['angles']['A']['value'],
            start_angle=-geometry['angles']['A']['value']/2 + PI/2,
            color=angle_colors['A'],
            fill_opacity=0.3
        ).move_arc_center_to(pts['A'])

        # 角B
        elements['angles']['B'] = Sector(
            outer_radius=0.8,
            angle=geometry['angles']['B']['value'],
            start_angle=geometry['angles']['B']['value'] + PI,
            color=angle_colors['B'],
            fill_opacity=0.3
        ).move_arc_center_to(pts['B'])

        # 角C
        elements['angles']['C'] = Sector(
            outer_radius=0.8,
            angle=geometry['angles']['C']['value'],
            start_angle=-geometry['angles']['C']['value'],
            color=angle_colors['C'],
            fill_opacity=0.3
        ).move_arc_center_to(pts['C'])

        return elements

    # ========== 字幕工具 ==========
    def create_subtitle(self, text):
        """创建字幕"""
        return Text(
            text,
            font_size=40,
            color=self.COLORS['text']
        ).to_edge(DOWN, buff=0.5)

    # ========== 构造主流程 ==========
    def construct(self):
        # 强制检查：必须实现 calculate_geometry 和 assert_geometry
        if not hasattr(self, 'calculate_geometry') or not callable(getattr(self, 'calculate_geometry')):
            raise NotImplementedError("必须实现 calculate_geometry() 方法")
        if not hasattr(self, 'assert_geometry') or not callable(getattr(self, 'assert_geometry')):
            raise NotImplementedError("必须实现 assert_geometry() 方法")

        # 初始化
        geometry = self.calculate_geometry()
        if geometry is None:
            raise ValueError("calculate_geometry() 必须返回几何数据字典")

        self.assert_geometry(geometry)
        elements = self.define_elements(geometry)
        self.camera.background_color = self.COLORS['background']

        # 按幕执行
        self.play_scene_1_title(elements, geometry)
        self.play_scene_2_draw_triangle(elements, geometry)
        self.play_scene_3_angles(elements, geometry)
        self.play_scene_4_parallel(elements, geometry)
        self.play_scene_5_proof(elements, geometry)
        self.play_scene_6_summary(elements, geometry)

    # ========== 第1幕：开场 ==========
    def play_scene_1_title(self, elements, geometry):
        """开场标题"""
        duration = self.get_scene_duration(1)
        self.add_scene_audio(1)

        title = Text("三角形内角和定理", font_size=60, color=self.COLORS['highlight'])
        subtitle = Text("证明：∠A + ∠B + ∠C = 180°", font_size=36, color=self.COLORS['text'])

        title.move_to(UP * 2)
        subtitle.next_to(title, DOWN, buff=0.5)

        self.play(FadeIn(title), run_time=1)
        self.play(FadeIn(subtitle), run_time=1)

        self.wait(duration - 2)
        self.play(FadeOut(title), FadeOut(subtitle))

    # ========== 第2幕：画三角形 ==========
    def play_scene_2_draw_triangle(self, elements, geometry):
        """画出三角形ABC"""
        duration = self.get_scene_duration(2)
        self.add_scene_audio(2)

        subtitle = self.create_subtitle("首先画一个任意三角形ABC")
        self.play(FadeIn(subtitle))

        # 逐步画三角形
        self.play(Create(elements['lines']['AB']), run_time=1)
        self.play(Create(elements['lines']['AC']), run_time=1)
        self.play(Create(elements['lines']['BC']), run_time=1)

        # 显示顶点和标签
        self.play(
            *[FadeIn(elements['points'][p]) for p in 'ABC'],
            *[Write(elements['labels'][p]) for p in 'ABC'],
            run_time=1
        )

        self.wait(duration - 4)
        self.play(FadeOut(subtitle))

    # ========== 第3幕：标角度 ==========
    def play_scene_3_angles(self, elements, geometry):
        """标注三个内角"""
        duration = self.get_scene_duration(3)
        self.add_scene_audio(3)

        subtitle = self.create_subtitle("标记三个内角：∠A、∠B、∠C")
        self.play(FadeIn(subtitle))

        # 依次显示角度
        for angle_name in ['A', 'B', 'C']:
            angle_arc = elements['angles'][angle_name]
            self.play(FadeIn(angle_arc), run_time=0.8)

            # 显示角度值
            angle_val = geometry['angles'][angle_name]['deg']
            label = MathTex(f"{angle_val:.0f}^\\circ").scale(0.6)
            label.set_color(self.COLORS[f'angle_{angle_name.lower()}'])

            if angle_name == 'A':
                label.next_to(elements['points']['A'], UP, buff=0.3)
            elif angle_name == 'B':
                label.next_to(elements['points']['B'], DOWN + LEFT, buff=0.3)
            else:
                label.next_to(elements['points']['C'], DOWN + RIGHT, buff=0.3)

            self.play(Write(label), run_time=0.5)

        self.wait(duration - 4)
        self.play(FadeOut(subtitle))

    # ========== 第4幕：画平行线 ==========
    def play_scene_4_parallel(self, elements, geometry):
        """过A点画BC的平行线"""
        duration = self.get_scene_duration(4)
        self.add_scene_audio(4)

        subtitle = self.create_subtitle("过顶点A作BC的平行线")
        self.play(FadeIn(subtitle))

        # 画平行线
        parallel = elements['lines']['parallel']
        self.play(Create(parallel), run_time=1.5)

        # 标注平行符号
        parallel_label = Text("// BC", font_size=24, color=self.COLORS['secondary'])
        parallel_label.next_to(parallel.get_right(), UP, buff=0.2)
        self.play(Write(parallel_label), run_time=0.5)

        self.wait(duration - 2.5)
        self.play(FadeOut(subtitle), FadeOut(parallel_label))

    # ========== 第5幕：证明 ==========
    def play_scene_5_proof(self, elements, geometry):
        """核心证明过程"""
        duration = self.get_scene_duration(5)
        self.add_scene_audio(5)

        subtitle = self.create_subtitle("利用平行线性质：内错角相等")
        self.play(FadeIn(subtitle))

        # 高亮演示：角B的内错角
        # 创建与角B相等的角在平行线上方
        angle_B_alt = Sector(
            outer_radius=0.8,
            angle=geometry['angles']['B']['value'],
            start_angle=PI/2,
            color=self.COLORS['angle_b'],
            fill_opacity=0.5
        ).move_arc_center_to(geometry['points']['A'])

        self.play(FadeIn(angle_B_alt), run_time=1)
        self.wait(0.5)

        # 高亮演示：角C的内错角
        angle_C_alt = Sector(
            outer_radius=0.8,
            angle=-geometry['angles']['C']['value'],
            start_angle=PI/2,
            color=self.COLORS['angle_c'],
            fill_opacity=0.5
        ).move_arc_center_to(geometry['points']['A'])

        self.play(FadeIn(angle_C_alt), run_time=1)

        # 结论：三个角组成平角
        self.wait(0.5)
        conclusion = Text("∴ ∠A + ∠B + ∠C = 180°", font_size=48, color=self.COLORS['highlight'])
        conclusion.to_edge(DOWN, buff=1.5)
        self.play(Write(conclusion), run_time=1)

        self.wait(duration - 4.5)
        self.play(FadeOut(subtitle), FadeOut(conclusion), FadeOut(angle_B_alt), FadeOut(angle_C_alt))

    # ========== 第6幕：总结 ==========
    def play_scene_6_summary(self, elements, geometry):
        """总结"""
        duration = self.get_scene_duration(6)
        self.add_scene_audio(6)

        subtitle = self.create_subtitle("三角形内角和恒等于180度")
        self.play(FadeIn(subtitle))

        # 高亮所有元素
        all_elements = (
            list(elements['lines'].values()) +
            list(elements['angles'].values()) +
            list(elements['points'].values())
        )

        self.play(
            *[element.animate.set_color(self.COLORS['highlight']) for element in all_elements],
            run_time=1
        )

        # 最终文字
        final_text = Text("证毕", font_size=72, color=self.COLORS['highlight'])
        self.play(Write(final_text), run_time=1)
        self.wait(1)
        self.play(FadeOut(final_text))

        self.wait(duration - 4)
        self.play(FadeOut(subtitle))
