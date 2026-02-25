"""
第九十九题：证明四点共圆 - Manim 动画 (音频驱动版本)
根据 timeline.json 中的实际音频时长自动同步画面
"""

from manim import *
import numpy as np
import json
import os

# 配置 - 竖屏 9:16
config.background_color = "#1a1a2e"
config.frame_rate = 30
config.pixel_height = 1920
config.pixel_width = 1080
config.frame_height = 16
config.frame_width = 9

# 加载实际音频时长
def load_audio_timings():
    """从 timeline.json 加载音频时长，如果不存在则使用默认值"""
    timeline_path = "audio/timeline.json"
    if os.path.exists(timeline_path):
        with open(timeline_path, 'r', encoding='utf-8') as f:
            timeline = json.load(f)
            # 转换为秒数
            timings = {}
            for scene in timeline.get('scenes', []):
                idx = scene.get('index', 0)
                duration = scene.get('duration', 5)
                # 根据索引映射到场景名称
                scene_names = ['opening', 'show_figure', 'tangent', 'hyperbola', 'monge', 'summary']
                if idx <= len(scene_names):
                    timings[scene_names[idx-1]] = duration
            print(f"✅ 已加载音频时长: {timings}")
            return timings
    # 默认时长（当 timeline.json 不存在时使用）
    print("⚠️  未找到 timeline.json，使用默认时长")
    return {
        "opening": 11.66,
        "show_figure": 17.18,
        "tangent": 18.46,
        "hyperbola": 25.25,
        "monge": 25.22,
        "summary": 16.66
    }

AUDIO_TIMINGS = load_audio_timings()

# 颜色定义
CIRCLE_I_COLOR = "#3498db"   # 蓝色 - 内切圆 I (虚线)
CIRCLE_J_COLOR = "#e74c3c"   # 红色 - 内切圆 J (虚线)
TRIANGLE_COLOR = "#2c3e50"   # 深蓝灰 - 三角形 ABC
TRIANGLE_INNER_COLOR = "#7f8c8d"  # 灰色 - 三角形 KBC
HIGHLIGHT_COLOR = "#ffc107"  # 黄色 - 高亮
HYPERBOLA_COLOR = "#9c27b0"  # 紫色 - 双曲线
AUX_CIRCLE_COLOR = "#00bcd4" # 青色 - 辅助圆（四点共圆）
POINT_COLOR = "#000000"      # 黑色 - 点
I_POINT_COLOR = "#3498db"    # 蓝色 - 内心 I
J_POINT_COLOR = "#e74c3c"    # 红色 - 内心 J


def calculate_geometry():
    """根据 6.html 的数学模型计算所有点和圆"""

    # 缩放因子（适配竖屏 9:16）
    SCALE = 0.7

    # 1. 定义 B、C 在 x 轴上
    B = np.array([-5.0, 0.0, 0.0]) * SCALE
    C = np.array([5.0, 0.0, 0.0]) * SCALE

    # 2. 定义 A 点 (AB > AC，所以 A 在右侧)
    A = np.array([1.5, 9.0, 0.0]) * SCALE

    # 3. 计算边长
    def dist(p1, p2):
        return np.linalg.norm(p1 - p2)

    AB = dist(A, B)
    AC = dist(A, C)
    BC = dist(B, C)

    # 4. 计算 D 点（内切圆 I 在 BC 上的切点）
    # BD = (AB + BC - AC) / 2
    BD = (AB + BC - AC) / 2
    CD = BC - BD

    # D 在 BC 上，从 B 向 C 移动 BD 距离
    D = B + (BD / BC) * (C - B)

    # 5. 计算双曲线参数（K 点在双曲线上）
    # 双曲线焦点：B(-5,0), C(5,0), 中心在原点
    # 2a = |AB - AC|
    diff_ABC = abs(AB - AC)
    a_hyp = diff_ABC / 2
    c_hyp = 5.0  # 焦点到中心的距离
    b_hyp = np.sqrt(c_hyp**2 - a_hyp**2)

    # 6. 定义 K 点（在双曲线上，y < y_A，在三角形内部）
    yK = 4.5
    # x^2 = a^2 * (1 + y^2/b^2)
    xK = a_hyp * np.sqrt(1 + (yK**2) / (b_hyp**2))
    K = np.array([xK, yK, 0.0])

    # 7. 计算切点 F（在 AB 上，BF = BD）
    vec_BA = (A - B) / AB
    F = B + BD * vec_BA

    # 8. 计算切点 E（在 AC 上，CE = CD）
    vec_CA = (A - C) / AC
    E = C + CD * vec_CA

    # 9. 计算切点 M（在 KB 上，BM = BD）
    KB = dist(K, B)
    vec_BK = (K - B) / KB
    M = B + BD * vec_BK

    # 10. 计算切点 N（在 KC 上，CN = CD）
    KC = dist(K, C)
    vec_CK = (K - C) / KC
    N = C + CD * vec_CK

    # 11. 计算内心 I 和 J
    # 因为 BC 是水平的，切点在 D，所以 I 和 J 都在 x = D.x 的垂直线上
    # I.y = r_I, J.y = r_J

    # 三角形 ABC 的面积和半周长
    area_ABC = 0.5 * BC * A[1]
    s_ABC = (AB + AC + BC) / 2
    r_I = area_ABC / s_ABC

    I = np.array([D[0], r_I, 0.0])

    # 三角形 KBC 的面积和半周长
    area_KBC = 0.5 * BC * K[1]
    s_KBC = (KB + KC + BC) / 2
    r_J = area_KBC / s_KBC

    J = np.array([D[0], r_J, 0.0])

    return {
        'A': A, 'B': B, 'C': C, 'D': D, 'E': E, 'F': F,
        'K': K, 'M': M, 'N': N, 'I': I, 'J': J,
        'r_I': r_I, 'r_J': r_J,
        'AB': AB, 'AC': AC, 'BC': BC,
        'BD': BD, 'CD': CD,
        'KB': KB, 'KC': KC
    }


class GeometryProof(Scene):
    """几何证明动画 - 音频驱动，画面自动同步语音时长"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scene_start_time = 0
        self.current_scene_name = ""

    def start_scene(self, scene_name):
        """开始一个场景，记录开始时间"""
        self.current_scene_name = scene_name
        self.scene_start_time = self.time
        print(f"\n▶️  场景: {scene_name} (音频时长: {AUDIO_TIMINGS.get(scene_name, 5):.2f}秒)")

    def wait_for_audio(self, animation_time=0):
        """等待直到音频播放完成

        参数:
            animation_time: 已经用于动画的时间（秒）
        """
        total_time = AUDIO_TIMINGS.get(self.current_scene_name, 5)
        remaining = total_time - animation_time
        if remaining > 0:
            print(f"   ⏱️  动画用时 {animation_time:.2f}秒, 等待 {remaining:.2f}秒")
            self.wait(remaining)
        else:
            print(f"   ⚠️  动画用时 {animation_time:.2f}秒 已超过音频时长!")

    def construct(self):
        # 计算所有几何元素
        geo = calculate_geometry()

        # ========== 第一幕：开场 ==========
        self.start_scene("opening")
        # 标题动画
        title = Text("第九十九题：证明四点共圆", font_size=52, color=WHITE)
        subtitle = Text("三角形内切圆与双曲线性质的综合运用", font_size=32, color=GRAY_B)
        subtitle.next_to(title, DOWN, buff=0.5)

        # 题目描述
        problem_text = VGroup(
            Text("已知：", font_size=28, color=GRAY_B),
            Text("△ABC 内切圆⊙I 切 BC、CA、AB 于 D、E、F", font_size=24),
            Text("K 为△ABC 内一点，△KBC 内切圆⊙J 切 BC 于 D", font_size=24),
            Text("求证：E、F、M、N 四点共圆", font_size=28, color=HIGHLIGHT_COLOR)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        problem_text.to_edge(DOWN, buff=1.5)

        self.play(Write(title), run_time=3)
        self.play(FadeIn(subtitle), run_time=2)
        self.wait(2)
        self.play(
            FadeOut(title),
            FadeOut(subtitle),
            Write(problem_text),
            run_time=4
        )
        # 等待音频完成
        self.wait_for_audio(animation_time=10)

        # 淡出问题描述
        self.play(FadeOut(problem_text), run_time=1)

        # ========== 第二幕：展示完整图形 ==========
        self.start_scene("show_figure")
        # 1. 先画三角形 ABC
        triangle = Polygon(geo['A'], geo['B'], geo['C'],
                          color=TRIANGLE_COLOR, stroke_width=2.5, fill_opacity=0.05)

        self.play(Create(triangle), run_time=2)
        self.wait(0.5)

        # 2. 显示顶点和标签
        labels_ABC = VGroup(
            Text("A", font_size=32).next_to(geo['A'], UP, buff=0.15),
            Text("B", font_size=32).next_to(geo['B'], LEFT, buff=0.15),
            Text("C", font_size=32).next_to(geo['C'], RIGHT, buff=0.15)
        )

        dots_ABC = VGroup(
            Dot(geo['A'], color=POINT_COLOR, radius=0.08),
            Dot(geo['B'], color=POINT_COLOR, radius=0.08),
            Dot(geo['C'], color=POINT_COLOR, radius=0.08)
        )

        self.play(
            FadeIn(dots_ABC),
            FadeIn(labels_ABC),
            run_time=2
        )

        # 3. 计算并显示 D 点
        D_dot = Dot(geo['D'], color=POINT_COLOR, radius=0.08)
        D_label = Text("D", font_size=32).next_to(geo['D'], DOWN, buff=0.15)

        # BD 和 CD 的长度标注
        BD_mid = (geo['B'] + geo['D']) / 2
        BD_text = Text(f"BD = {geo['BD']:.2f}", font_size=24, color=GRAY_B)
        BD_text.next_to(BD_mid, DOWN, buff=0.3)

        self.play(
            FadeIn(D_dot),
            FadeIn(D_label),
            Write(BD_text),
            run_time=2
        )
        self.wait(0.5)
        self.play(FadeOut(BD_text), run_time=0.5)

        # 4. 画内切圆 I (蓝色虚线)
        circle_I = DashedVMobject(
            Circle(radius=geo['r_I'], color=CIRCLE_I_COLOR, stroke_width=3),
            num_dashes=30,
            dashed_ratio=0.5
        )
        circle_I.set_stroke(opacity=0.9)
        circle_I.move_to(geo['I'])

        I_dot = Dot(geo['I'], color=I_POINT_COLOR, radius=0.08)
        I_label = Text("I", font_size=28, color=CIRCLE_I_COLOR).next_to(geo['I'], RIGHT, buff=0.1)

        self.play(
            Create(circle_I),
            FadeIn(I_dot),
            FadeIn(I_label),
            run_time=3
        )

        # 5. 显示切点 E、F
        E_dot = Dot(geo['E'], color=POINT_COLOR, radius=0.08)
        E_label = Text("E", font_size=28).next_to(geo['E'], RIGHT, buff=0.1)
        F_dot = Dot(geo['F'], color=POINT_COLOR, radius=0.08)
        F_label = Text("F", font_size=28).next_to(geo['F'], LEFT, buff=0.1)

        self.play(
            FadeIn(E_dot), FadeIn(E_label),
            FadeIn(F_dot), FadeIn(F_label),
            run_time=2
        )
        self.wait(0.5)

        # 6. 显示点 K
        K_dot = Dot(geo['K'], color=POINT_COLOR, radius=0.08)
        K_label = Text("K", font_size=28).next_to(geo['K'], UP, buff=0.15)

        self.play(
            FadeIn(K_dot), FadeIn(K_label),
            run_time=2
        )

        # 7. 画三角形 KBC
        triangle_KBC = Polygon(geo['K'], geo['B'], geo['C'],
                               color=TRIANGLE_INNER_COLOR, stroke_width=1.5, fill_opacity=0)

        self.play(Create(triangle_KBC), run_time=1.5)

        # 8. 画内切圆 J (红色虚线)
        circle_J = DashedVMobject(
            Circle(radius=geo['r_J'], color=CIRCLE_J_COLOR, stroke_width=3),
            num_dashes=25,
            dashed_ratio=0.5
        )
        circle_J.move_to(geo['J'])
        circle_J.set_stroke(opacity=0.9)

        J_dot = Dot(geo['J'], color=J_POINT_COLOR, radius=0.08)
        J_label = Text("J", font_size=28, color=CIRCLE_J_COLOR).next_to(geo['J'], RIGHT, buff=0.1)

        self.play(
            Create(circle_J),
            FadeIn(J_dot),
            FadeIn(J_label),
            run_time=2.5
        )

        # 9. 显示切点 M、N
        M_dot = Dot(geo['M'], color=POINT_COLOR, radius=0.08)
        M_label = Text("M", font_size=28).next_to(geo['M'], LEFT, buff=0.1)
        N_dot = Dot(geo['N'], color=POINT_COLOR, radius=0.08)
        N_label = Text("N", font_size=28).next_to(geo['N'], RIGHT, buff=0.1)

        self.play(
            FadeIn(M_dot), FadeIn(M_label),
            FadeIn(N_dot), FadeIn(N_label),
            run_time=2
        )

        # 显示字幕：已知条件
        subtitle1 = Text("已知：两内切圆共切点 D", font_size=32, color=WHITE)
        subtitle1.to_edge(DOWN, buff=0.8)
        self.play(Write(subtitle1), run_time=2)
        self.wait(1)
        self.play(FadeOut(subtitle1), run_time=0.5)

        # 等待音频完成 (2+0.5+2+2+0.5+3+2+0.5+2+1.5+2.5+2+2+1+0.5 = 大约16秒)
        self.wait_for_audio(animation_time=16)

        # ========== 第三幕：切线长定理 ==========
        self.start_scene("tangent")
        # 简化图形，突出切线长
        self.play(
            triangle.animate.set_stroke(width=0.8).set_fill(opacity=0.3),
            triangle_KBC.animate.set_stroke(width=0.5).set_fill(opacity=0.3),
            circle_I.animate.set_stroke(width=0.8, opacity=0.3),
            circle_J.animate.set_stroke(width=0.8, opacity=0.3),
            run_time=0.5
        )

        # 标题
        tangent_title = Text("切线长定理", font_size=40, color=HIGHLIGHT_COLOR)
        tangent_title.to_edge(UP, buff=0.5)
        self.play(Write(tangent_title), run_time=1)

        # 1. BF = BD
        BF_line = Line(geo['B'], geo['F'], color=HIGHLIGHT_COLOR, stroke_width=6)
        BD_line_1 = Line(geo['B'], geo['D'], color=HIGHLIGHT_COLOR, stroke_width=6)
        eq1 = Text("BF = BD", font_size=36, color=HIGHLIGHT_COLOR).to_edge(RIGHT, buff=0.5).shift(UP * 2.5)

        self.play(
            Create(BF_line),
            Create(BD_line_1),
            Write(eq1),
            run_time=2
        )
        self.wait(1)
        self.play(FadeOut(BF_line), FadeOut(BD_line_1), FadeOut(eq1), run_time=0.5)

        # 2. CE = CD
        CE_line = Line(geo['C'], geo['E'], color=HIGHLIGHT_COLOR, stroke_width=6)
        CD_line_1 = Line(geo['C'], geo['D'], color=HIGHLIGHT_COLOR, stroke_width=6)
        eq2 = Text("CE = CD", font_size=36, color=HIGHLIGHT_COLOR).to_edge(RIGHT, buff=0.5).shift(UP * 1.8)

        self.play(
            Create(CE_line),
            Create(CD_line_1),
            Write(eq2),
            run_time=2
        )
        self.wait(1)
        self.play(FadeOut(CE_line), FadeOut(CD_line_1), FadeOut(eq2), run_time=0.5)

        # 3. BM = BD
        BM_line = Line(geo['B'], geo['M'], color=HIGHLIGHT_COLOR, stroke_width=6)
        BD_line_2 = Line(geo['B'], geo['D'], color=HIGHLIGHT_COLOR, stroke_width=6)
        eq3 = Text("BM = BD", font_size=36, color=HIGHLIGHT_COLOR).to_edge(RIGHT, buff=0.5).shift(UP * 1.1)

        self.play(
            Create(BM_line),
            Create(BD_line_2),
            Write(eq3),
            run_time=2
        )
        self.wait(1)
        self.play(FadeOut(BM_line), FadeOut(BD_line_2), FadeOut(eq3), run_time=0.5)

        # 4. CN = CD
        CN_line = Line(geo['C'], geo['N'], color=HIGHLIGHT_COLOR, stroke_width=6)
        CD_line_2 = Line(geo['C'], geo['D'], color=HIGHLIGHT_COLOR, stroke_width=6)
        eq4 = Text("CN = CD", font_size=36, color=HIGHLIGHT_COLOR).to_edge(RIGHT, buff=0.5).shift(UP * 0.4)

        self.play(
            Create(CN_line),
            Create(CD_line_2),
            Write(eq4),
            run_time=2
        )
        self.wait(1.5)
        self.play(
            FadeOut(CN_line), FadeOut(CD_line_2), FadeOut(eq4),
            FadeOut(tangent_title),
            run_time=0.5
        )

        # 恢复图形
        self.play(
            triangle.animate.set_stroke(width=2.5, opacity=1),
            triangle_KBC.animate.set_stroke(width=1.5, opacity=1),
            circle_I.animate.set_stroke(width=2, opacity=1),
            circle_J.animate.set_stroke(width=2, opacity=1),
            run_time=1
        )

        # 等待音频完成
        self.wait_for_audio(animation_time=17)

        # ========== 第四幕：双曲线性质推导 ==========
        self.start_scene("hyperbola")
        hyperbola_title = Text("双曲线性质", font_size=40, color=HYPERBOLA_COLOR)
        hyperbola_title.to_edge(UP, buff=0.5)
        self.play(Write(hyperbola_title), run_time=1.5)

        # 公式推导（分步显示）
        # 步骤 1: AB - AC 的计算
        formula1 = Text("AB - AC = (BD + AF) - (CD + AE)", font_size=30, color=WHITE)
        formula1.to_edge(UP, buff=1.2)

        # 高亮 AB 和 AC
        AB_highlight = Line(geo['A'], geo['B'], color=BLUE, stroke_width=8)
        AB_highlight.set_stroke(opacity=0.5)
        AC_highlight = Line(geo['A'], geo['C'], color=BLUE, stroke_width=8)
        AC_highlight.set_stroke(opacity=0.5)

        self.play(
            Write(formula1),
            Create(AB_highlight),
            Create(AC_highlight),
            run_time=2.5
        )
        self.wait(1)
        self.play(FadeOut(AB_highlight), FadeOut(AC_highlight), run_time=0.5)

        # 步骤 2: 化简
        formula2 = Text("= BD - CD    (∵ AF = AE)", font_size=30, color=WHITE)
        formula2.next_to(formula1, DOWN, buff=0.3, aligned_edge=LEFT)

        self.play(Write(formula2), run_time=2)
        self.wait(1)

        # 步骤 3: KB - KC 的计算
        formula3 = Text("KB - KC = (BM + MK) - (CN + NK)", font_size=30, color=WHITE)
        formula3.next_to(formula2, DOWN, buff=0.5)

        KB_highlight = Line(geo['K'], geo['B'], color=GREEN, stroke_width=8)
        KB_highlight.set_stroke(opacity=0.5)
        KC_highlight = Line(geo['K'], geo['C'], color=GREEN, stroke_width=8)
        KC_highlight.set_stroke(opacity=0.5)

        self.play(
            Write(formula3),
            Create(KB_highlight),
            Create(KC_highlight),
            run_time=2.5
        )
        self.wait(1)
        self.play(FadeOut(KB_highlight), FadeOut(KC_highlight), run_time=0.5)

        # 步骤 4: 化简
        formula4 = Text("= BM - CN = BD - CD", font_size=30, color=WHITE)
        formula4.next_to(formula3, DOWN, buff=0.3, aligned_edge=LEFT)

        self.play(Write(formula4), run_time=2)
        self.wait(1)

        # 结论
        conclusion_hyperbola = Text("∴ AB - AC = KB - KC", font_size=38, color=HIGHLIGHT_COLOR)
        conclusion_hyperbola.next_to(formula4, DOWN, buff=0.5)

        self.play(Write(conclusion_hyperbola), run_time=1.5)
        self.wait(2)

        # 清除公式
        self.play(
            FadeOut(formula1), FadeOut(formula2), FadeOut(formula3),
            FadeOut(formula4), FadeOut(conclusion_hyperbola),
            run_time=1
        )

        # 绘制双曲线
        hyperbola = self._create_hyperbola(geo['B'], geo['C'], abs(geo['AB'] - geo['AC']) / 2)
        hyperbola.set_stroke(HYPERBOLA_COLOR, width=2.5)
        hyperbola.set_stroke(opacity=0.7)

        self.play(Create(hyperbola), run_time=3)

        # 显示 A 和 K 在双曲线上
        A_on_curve = Text("A 在双曲线上", font_size=28, color=WHITE).next_to(geo['A'], UR, buff=0.2)
        K_on_curve = Text("K 在双曲线上", font_size=28, color=WHITE).next_to(geo['K'], UR, buff=0.2)

        # 创建 A 和 K 的高亮点
        A_highlight = Dot(geo['A'], color=HIGHLIGHT_COLOR, radius=0.15)
        K_highlight = Dot(geo['K'], color=HIGHLIGHT_COLOR, radius=0.15)

        self.play(
            Write(A_on_curve),
            Create(A_highlight),
            run_time=1.5
        )
        self.wait(0.5)
        self.play(
            Write(K_on_curve),
            Create(K_highlight),
            run_time=1.5
        )
        self.wait(2)

        # 清除双曲线相关
        self.play(
            FadeOut(hyperbola), FadeOut(A_on_curve), FadeOut(K_on_curve),
            FadeOut(A_highlight), FadeOut(K_highlight),
            run_time=1
        )

        # 等待音频完成
        self.wait_for_audio(animation_time=24)

        # ========== 第五幕：蒙日定理应用 ==========
        monge_title = Text("蒙日定理推论", font_size=40, color=AUX_CIRCLE_COLOR)
        monge_title.to_edge(UP, buff=0.5)
        self.play(Write(monge_title), run_time=1.5)

        # 显示定理内容
        monge_text = VGroup(
            Text("从双曲线上的点向有公共切点的两圆作切线，", font_size=28),
            Text("四个切点共圆", font_size=28, color=HIGHLIGHT_COLOR)
        ).arrange(DOWN, buff=0.3)
        monge_text.next_to(monge_title, DOWN, buff=0.5)

        self.play(Write(monge_text), run_time=3)
        self.wait(1)

        # 绘制辅助圆（E、F、M、N 的外接圆）
        aux_circle = self._create_circumcircle(geo['E'], geo['F'], geo['M'])
        aux_circle.set_stroke(AUX_CIRCLE_COLOR, width=3.5)

        self.play(Create(aux_circle), run_time=3)

        # 高亮 E、F、M、N 四点
        EFMN_dots = VGroup(
            Dot(geo['E'], color=AUX_CIRCLE_COLOR, radius=0.12),
            Dot(geo['F'], color=AUX_CIRCLE_COLOR, radius=0.12),
            Dot(geo['M'], color=AUX_CIRCLE_COLOR, radius=0.12),
            Dot(geo['N'], color=AUX_CIRCLE_COLOR, radius=0.12)
        )

        # 连接四点形成四边形
        quad = Polygon(geo['E'], geo['F'], geo['M'], geo['N'],
                       color=AUX_CIRCLE_COLOR, stroke_width=1.5)
        quad.set_fill(opacity=0.1)

        self.play(
            Create(quad),
            FadeIn(EFMN_dots),
            run_time=2.5
        )

        # 显示结论
        conclusion_final = Text("∴ E、F、M、N 四点共圆", font_size=44, color=HIGHLIGHT_COLOR)
        conclusion_final.to_edge(DOWN, buff=1.5)

        self.play(Write(conclusion_final), run_time=2)
        self.wait(3)

        # 清除
        self.play(
            FadeOut(monge_title), FadeOut(monge_text),
            FadeOut(conclusion_final),
            FadeOut(quad), FadeOut(EFMN_dots),
            run_time=1
        )

        # 等待音频完成
        self.wait_for_audio(animation_time=24)

        # ========== 第六幕：总结 ==========
        summary_title = Text("证明步骤总结", font_size=44, color=WHITE)
        summary_title.to_edge(UP, buff=0.5)

        step1 = Text("1. 切线长定理 → 相等线段", font_size=34, color=WHITE)
        step2 = Text("2. 双曲线识别 → AB - AC = KB - KC", font_size=34, color=WHITE)
        step3 = Text("3. 蒙日定理 → 四点共圆", font_size=34, color=HIGHLIGHT_COLOR)

        steps = VGroup(step1, step2, step3).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        steps.next_to(summary_title, DOWN, buff=0.8)

        # 逐步显示步骤
        self.play(Write(summary_title), run_time=1.5)
        self.wait(0.5)

        self.play(Write(step1), run_time=2)
        self.wait(1)

        self.play(Write(step2), run_time=2)
        self.wait(1)

        self.play(Write(step3), run_time=2)
        self.wait(2)

        # 证明完成
        done_text = Text("证明完成！", font_size=64, color=HIGHLIGHT_COLOR)
        done_text.next_to(steps, DOWN, buff=1)

        self.play(Write(done_text), run_time=2)

        # 等待音频完成
        self.wait_for_audio(animation_time=15)

        # 结束
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1.5
        )

    def _create_hyperbola(self, F1, F2, a, num_points=200):
        """创建双曲线"""
        c = np.linalg.norm(F1 - F2) / 2
        center = (F1 + F2) / 2

        if c > a:
            b = np.sqrt(c**2 - a**2)
        else:
            b = 0.5

        # 生成双曲线点（两支）
        t = np.linspace(-1.5, 1.5, num_points)
        points = []

        for ti in t:
            # 右支
            x_r = a * np.cosh(ti)
            y_r = b * np.sinh(ti)
            points.append([center[0] + x_r, center[1] + y_r, 0])
            # 左支
            x_l = -a * np.cosh(ti)
            y_l = b * np.sinh(ti)
            points.append([center[0] + x_l, center[1] + y_l, 0])

        # 创建曲线
        hyperbola = VGroup()
        for p in points:
            if -6 < p[1] < 10:  # 限制显示范围
                dot = Dot(p, radius=0.025, color=HYPERBOLA_COLOR)
                hyperbola.add(dot)

        return hyperbola

    def _create_circumcircle(self, A, B, C):
        """创建外接圆"""
        # 计算外心
        D = 2 * (A[0] * (B[1] - C[1]) + B[0] * (C[1] - A[1]) + C[0] * (A[1] - B[1]))
        if abs(D) < 1e-10:
            # 三点共线，返回一个大圆
            return Circle(radius=10, color=AUX_CIRCLE_COLOR)

        Ux = ((A[0]**2 + A[1]**2) * (B[1] - C[1]) +
              (B[0]**2 + B[1]**2) * (C[1] - A[1]) +
              (C[0]**2 + C[1]**2) * (A[1] - B[1])) / D
        Uy = ((A[0]**2 + A[1]**2) * (C[0] - B[0]) +
              (B[0]**2 + B[1]**2) * (A[0] - C[0]) +
              (C[0]**2 + C[1]**2) * (B[0] - A[0])) / D

        center = np.array([Ux, Uy, 0])
        radius = np.linalg.norm(A - center)

        return Circle(radius=radius, color=AUX_CIRCLE_COLOR).move_to(center)


if __name__ == "__main__":
    # 使用命令行渲染：python -m manim -qh geometry_proof_audio.py GeometryProof
    pass
