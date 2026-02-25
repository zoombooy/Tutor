# Tutor — 数学教学视频制作技能

一对一辅导老师技能（Kiro Skill），面向中学数学教学场景。给定一道数学题，自动完成从题目分析、HTML 可视化、分镜脚本编写、TTS 配音生成，到 Manim 动画渲染的全流程，最终输出一段带配音讲解的教学视频。

## 功能概览

| 能力 | 说明 |
|------|------|
| 数学建模 | 推导几何事实，建立坐标无关的数学模型 |
| HTML 可视化 | 用 SVG 绘制图形，展示画图过程与解答流程 |
| 分镜脚本 | 定义视频幕结构、字幕、读白、动画时序 |
| TTS 配音 | 基于 Edge TTS 生成中文语音（支持多种声线） |
| Manim 动画 | 生成带几何验证、音画同步的教学动画视频 |
| 自动化流水线 | 代码结构检查 → 渲染 → 视频拷贝一键完成 |

## 核心工作流

```
题目输入 → ① 数学分析 → ② HTML可视化 → ③ 分镜脚本
           ╰──────── AI 对话阶段 ────────╯      ↓
         ⑧ 渲染验证 ← ⑦ 实现代码 ← ⑥ 脚手架 ← ⑤ 验证更新 ← ④ TTS生成
              ↓        ╰─ AI 生成 ─╯              ╰──── 脚本工具 ────╯
         输出视频                                        ↑
                                                  (失败时回到⑦修改)
```

工作流分为两个阶段：

**AI 对话阶段**（步骤 ①②③⑥⑦）— 由 AI 在对话中直接生成，无独立脚本

| 步骤 | 输入 | 输出 | 说明 |
|------|------|------|------|
| ① 数学分析 | 题目图片/文本 | `math_analysis.md` | AI 推导数学事实、建立几何模型 |
| ② HTML 可视化 | 数学分析 | `数学_{日期}_{题目}.html` | AI 生成 HTML+SVG 代码，用浏览器打开查看图形和解答过程 |
| ③ 分镜脚本 | HTML 内容 | `{日期}_{题目}_分镜.md` | AI 编写幕结构、字幕、读白、动画描述 |
| ⑥ 脚手架 | 分镜 + audio_info | `script.py`（伪代码框架） | AI 基于模板生成，含 TODO 占位 |
| ⑦ 实现代码 | 脚手架 + 分镜 | 完整的 `script.py` | AI 填充所有 TODO，实现动画逻辑 |

**脚本工具阶段**（步骤 ④⑤⑧）— 有对应的可执行脚本

| 步骤 | 输入 | 输出 | 脚本 |
|------|------|------|------|
| ④ TTS 生成 | `audio_list.csv` | `audio/*.wav` + `audio_info.json` | `scripts/generate_tts.py` |
| ⑤ 验证更新 | 分镜 + 音频目录 | 更新后的分镜（填充时长） | `scripts/validate_audio.py` |
| ⑧ 渲染验证 | `script.py` | `.mp4` 视频文件 | `scripts/check.py` + `scripts/render.py` |


## 环境要求

### 系统依赖

| 依赖 | 版本要求 | 必需 | 说明 |
|------|---------|------|------|
| Python | ≥ 3.10 | 是 | manim 0.18+ 要求 Python 3.10 及以上 |
| ffmpeg | 任意 | 推荐 | Manim 渲染视频所需，部分系统已预装 |
| LaTeX | — | 否 | 本技能使用 `Text` 替代 `MathTex`，无需 LaTeX |

### Python 依赖

| 包 | 版本 | 用途 |
|----|------|------|
| `manim` | ≥ 0.18.0 | 数学动画引擎 |
| `numpy` | ≥ 1.24.0 | 几何计算 |
| `edge-tts` | ≥ 6.1.0 | 微软 Edge TTS 语音合成 |
| `mutagen` | ≥ 1.47.0 | 音频时长检测 |
| `pillow` | ≥ 10.0.0 | 图像处理 |

## 环境搭建

### 方式一：使用 venv（推荐）

```bash
# 1. 创建虚拟环境（确保使用 Python 3.10+）
python3.10 -m venv .venv

# 2. 激活虚拟环境
# Linux / macOS:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (CMD):
.venv\Scripts\activate.bat

# 3. 安装依赖
pip install -r tutor/requirements.txt
```

### 方式二：使用 uv（可选）

```bash
# 安装 uv（如果尚未安装）
pip install uv

# 创建虚拟环境并安装依赖
uv venv .venv --python 3.10
uv pip install -r tutor/requirements.txt
```

### 验证安装

```bash
python -c "import manim; print('manim', manim.__version__)"
python -c "import edge_tts; print('edge-tts OK')"
python -c "import mutagen; print('mutagen OK')"
python -c "import numpy; print('numpy', numpy.__version__)"
ffmpeg -version 2>&1 | head -1
```

全部输出正常即表示环境就绪。

## 项目初始化

使用 `init.py` 在目标目录创建标准项目结构：

```bash
# 在当前目录初始化
python tutor/init.py .

# 在指定目录初始化
python tutor/init.py my_project

# 跳过依赖检查（已确认环境正常时）
python tutor/init.py my_project --skip-deps
```

初始化后的项目结构：

```
my_project/
├── audio/              # 音频文件目录（TTS 生成的 .wav 文件）
│   └── audio_info.json # 音频时长信息（自动生成）
├── media/              # Manim 渲染输出目录
├── assets/             # 静态资源（图片等）
├── script.py           # Manim 脚手架（从模板复制）
├── script_example.py   # 完整示例脚本（参考用）
├── audio_list.csv      # 音频生成清单模板
└── .gitignore
```


## 使用指南

### 步骤 1-3：AI 对话阶段（无独立脚本）

这三个步骤由 AI 在对话中完成，没有对应的自动化工具：

1. **数学分析** — 将题目（图片或文本）发给 AI，AI 推导数学事实，输出 `math_analysis.md`
2. **HTML 可视化** — AI 生成一个 HTML+SVG 文件，用浏览器打开可以看到图形绘制过程和分步解答。这一步的目的是在写分镜之前先把图形画对、解题过程理清。如果你已经有准确的 HTML 文件，可以跳过此步
3. **分镜脚本** — AI 根据 HTML 内容编写分镜，定义每一幕的画面、字幕、读白和动画时序

### 步骤 4：生成 TTS 配音

```bash
# 基本用法（默认使用晓晓女声）
python tutor/scripts/generate_tts.py audio_list.csv ./audio

# 指定声线
python tutor/scripts/generate_tts.py audio_list.csv ./audio --voice yunyang
```

`audio_list.csv` 格式：

```csv
filename,text
audio_001_开场.wav,"大家好！今天我们来学习三角形内角和定理。"
audio_002_画三角形.wav,"首先，让我们画一个任意三角形。"
```

支持的声线：

| 名称 | 声音 ID | 说明 |
|------|---------|------|
| `xiaoxiao` | zh-CN-XiaoxiaoNeural | 晓晓，女声（默认） |
| `xiaoyi` | zh-CN-XiaoyiNeural | 晓伊，女声 |
| `yunyang` | zh-CN-YunyangNeural | 云扬，男声 |
| `yunjian` | zh-CN-YunjianNeural | 云健，男声 |

输出文件：
- `audio/audio_001_开场.wav` ... 各幕音频
- `audio/audio_info.json` — 包含每幕的文件名、时长、文本等元信息

### 步骤 5：验证音频并更新分镜

```bash
python tutor/scripts/validate_audio.py 分镜.md ./audio
```

功能：
- 检查所有音频文件是否存在且时长正常（> 0 秒）
- 将实际时长回填到分镜脚本的音频清单表格中
- 生成/更新 `audio/audio_info.json`
- 如果音频缺失或异常，输出具体错误信息

### 步骤 6-7：AI 生成 Manim 代码（无独立脚本）

这两步同样由 AI 在对话中完成。AI 基于 `templates/script_scaffold.py` 模板和分镜脚本，生成完整的 `script.py`。脚手架包含以下核心结构：

```python
class MathScene(Scene):
    COLORS = { ... }                    # 颜色定义
    SCENES = [ ... ]                    # 幕信息数组

    def calculate_geometry(self):        # 几何建模（坐标、边长、角度）
    def assert_geometry(self, geo):      # 几何验证（题目条件 + 画布范围）
    def define_elements(self, geo):      # Manim 图形对象定义
    def construct(self):                 # 主流程
    def play_scene(self, ...):           # 单幕动画（含音频集成）
```

关键约束：
- 每幕第一行必须调用 `self.add_sound()` 添加音频
- 动画总时长 ≥ 音频时长（画面等待音频原则）
- 读白提到的元素必须同步高亮
- 所有文字元素必须有退场动画
- 使用 `Text` 而非 `MathTex`（无需 LaTeX）

### 步骤 8：代码检查与渲染

#### 代码结构检查

```bash
# 检查默认的 script.py
python tutor/scripts/check.py

# 检查指定文件
python tutor/scripts/check.py my_script.py
```

检查项：

| 检查项 | 级别 | 说明 |
|--------|------|------|
| `calculate_geometry()` | 必需 | 几何计算函数 |
| `assert_geometry()` | 必需 | 几何验证函数 |
| `define_elements()` | 必需 | 图形元素定义 |
| 继承 `Scene` 的类 | 必需 | Manim 场景类 |
| `add_sound()` 调用 | 建议 | 音频集成 |
| `Subtitle` 类 | 建议 | 字幕管理 |

#### 渲染视频

```bash
# 推荐方式：完整流水线（检查 → 渲染 → 拷贝到根目录）
python tutor/scripts/render.py

# 指定文件和场景
python tutor/scripts/render.py -f script.py -s MathScene

# 渲染质量选项
python tutor/scripts/render.py -q l    # 480p15  （快速预览）
python tutor/scripts/render.py -q m    # 720p30  （中等质量）
python tutor/scripts/render.py -q h    # 1080p60 （默认，高质量）
python tutor/scripts/render.py -q k    # 2160p60 （4K）

# 跳过检查（仅用于快速调试，不推荐）
python tutor/scripts/render.py --no-check

# 直接使用 manim（跳过流水线）
manim -pqh script.py MathScene
```

渲染完成后，视频自动拷贝到项目根目录。


## 目录结构

```
tutor/
├── SKILL.md                        # 技能定义文件（完整工作流规范）
├── README.md                       # 本文件
├── init.py                         # 项目初始化脚本
├── requirements.txt                # Python 依赖清单
│
├── scripts/                        # 工具脚本
│   ├── generate_tts.py             # TTS 语音合成（Edge TTS）
│   ├── validate_audio.py           # 音频验证 & 分镜时长回填
│   ├── check.py                    # Manim 代码结构检查
│   ├── render.py                   # 渲染流水线（检查 + 渲染 + 拷贝）
│   └── audio_list.example.csv      # CSV 格式示例
│
├── templates/                      # 代码模板
│   ├── script_scaffold.py          # Manim 脚手架模板（含字幕类、工具方法）
│   └── script_example.py           # 完整示例：三角形内角和证明
│
├── references/                     # 参考资料
│   └── storyboard_sample.md        # 分镜脚本示例（四点共圆证明）
│
└── sample/                         # 早期探索示例（保留参考）
    └── geometry_proof/
        ├── scene.py                # 几何证明动画
        ├── storyboard.md           # 分镜脚本
        └── ...
```

## 设计原则

### 数学解题

- 禁止使用坐标系求解，应使用几何推理（勾股定理、相似三角形、等积变换等）
- 为了动画展示可以显示坐标，但解题过程不能依赖坐标计算
- 所有证明题的结论在分镜中可作为已确立的事实使用

### 几何验证（assert_geometry）

- 验证题目给定的条件（边长相等、中点、直角等），使用相对误差 `1e-4`
- 验证画布范围：图形在 `[-6.5, 6.5] × [-3.5, 3.5]` 安全区域内
- 验证视觉中心：图形中心在 `[-1.4, 1.4] × [-0.8, 0.8]` 区域内
- 所有 assert 使用中文错误提示，包含具体数值和修复建议

### 音画同步

- 每幕第一行必须 `self.add_sound()`，否则视频无声音
- 动画总时长 ≥ 音频时长，不足时用 `self.wait()` 补齐
- 读白提到的元素必须同步高亮（边、点、角、结论等）

### 绕过 LaTeX

本技能全部使用 `Text` 替代 `MathTex`，无需安装 LaTeX 环境：

```python
# ✅ 正确（无需 LaTeX）
Text("BC² = AB² + AC²", font_size=36)
Text("∠A + ∠B + ∠C = 180°", font_size=30)

# ❌ 错误（需要 LaTeX）
MathTex(r"BC^2 = AB^2 + AC^2")
```

常用 Unicode 数学符号：`²` `³` `½` `√` `∠` `°` `∴` `∵` `≈` `≠` `≤` `≥` `×` `÷` `π`

## 快速上手示例

以下演示从零开始生成一个"三角形内角和证明"教学视频的完整流程：

```bash
# 1. 创建项目目录并初始化
mkdir my_math_video && cd my_math_video
python ../tutor/init.py . --skip-deps

# 2. 编辑 audio_list.csv（init 已生成示例内容，可直接使用）

# 3. 生成 TTS 配音
python ../tutor/scripts/generate_tts.py audio_list.csv ./audio --voice xiaoxiao

# 4. 验证音频（如果有分镜脚本）
# python ../tutor/scripts/validate_audio.py 分镜.md ./audio

# 5. 编辑 script.py 实现动画逻辑（或让 AI 根据分镜生成）

# 6. 检查代码结构
python ../tutor/scripts/check.py script.py

# 7. 渲染视频
python ../tutor/scripts/render.py -f script.py -s MathScene -q h

# 视频输出到项目根目录
```

也可以直接运行已有的示例脚本：

```bash
cd my_math_video
manim -ql --disable_caching script_example.py TriangleAngleSum
# 输出: media/videos/script_example/1920p60/TriangleAngleSum.mp4
```

## 已知注意事项

1. manim 0.19+ 中 `Sector` 构造函数使用 `radius` 参数而非 `outer_radius`
2. `self.wait()` 的 duration 必须 > 0，建议使用 `max(0.1, duration - N)` 防护
3. Windows 控制台可能无法显示 Unicode 符号（✓/✗/⚠），脚本已内置 fallback 处理
4. Edge TTS 需要网络连接（调用微软在线服务）
5. 渲染 1080p60 视频约需 30-60 秒（取决于幕数和动画复杂度）

## 许可

内部技能，仅供教学用途。
