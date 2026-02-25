#!/bin/bash
# 一键渲染脚本 - 音频驱动画面同步
# 流程: 生成音频 → 记录时长 → 渲染视频(根据时长) → 合并音视频

set -e

echo "=========================================="
echo "  Manim 视频渲染 - 音频驱动版"
echo "=========================================="
echo ""
echo "🎬 本脚本将根据实际音频时长自动同步画面"
echo ""

# 检查参数
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "用法: ./render.sh [选项]"
    echo ""
    echo "选项:"
    echo "  --audio       重新生成音频并渲染（默认）"
    echo "  --skip-audio  使用现有音频，仅重新渲染视频"
    echo "  --clean       清理环境并重新创建"
    echo "  --help        显示此帮助"
    echo ""
    echo "流程:"
    echo "  1. 生成 TTS 音频"
    echo "  2. 记录每段音频实际时长 → audio/timeline.json"
    echo "  3. 渲染视频（画面自动等待对应音频时长）"
    echo "  4. 合并音视频 → final_video.mp4"
    exit 0
fi

# 检查 uv
if ! command -v uv &> /dev/null; then
    echo "❌ 错误: 未找到 uv"
    echo ""
    echo "请安装 uv:"
    echo "  macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "  或访问: https://github.com/astral-sh/uv"
    exit 1
fi

# 检查 ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ 错误: 未找到 ffmpeg"
    echo "请安装: brew install ffmpeg (macOS) 或 apt install ffmpeg (Linux)"
    exit 1
fi

# 设置环境
VENV_DIR=".venv"

# 清理环境
if [ "$1" == "--clean" ]; then
    echo "🧹 清理环境..."
    rm -rf "$VENV_DIR" media/ final_video.mp4
    echo "✅ 环境已清理"
    echo ""
fi

# 创建虚拟环境
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 创建虚拟环境..."
    uv venv "$VENV_DIR"
    echo "✅ 虚拟环境已创建"
    echo ""
fi

# 安装依赖
echo "📦 安装依赖..."
if [ -f "requirements.txt" ]; then
    echo "   使用 requirements.txt"
    uv pip install --python "$VENV_DIR/bin/python" -r requirements.txt -q
else
    echo "   使用默认依赖"
    uv pip install --python "$VENV_DIR/bin/python" manim edge-tts -q
fi
echo "✅ 依赖安装完成"
echo ""

PYTHON="$VENV_DIR/bin/python"
MANIM="$VENV_DIR/bin/manim"

# 步骤 1: 生成音频
generate_audio() {
    echo "📢 步骤 1: 生成 TTS 音频"
    echo "----------------------------------------"

    # 查找分镜文件
    STORYBOARD=$(ls *.md 2>/dev/null | grep -E "(分镜|storyboard)" | head -1)
    if [ -z "$STORYBOARD" ]; then
        STORYBOARD=$(ls *.md 2>/dev/null | head -1)
    fi

    if [ -z "$STORYBOARD" ]; then
        echo "❌ 错误: 未找到分镜脚本 (.md 文件)"
        exit 1
    fi

    echo "使用分镜: $STORYBOARD"
    echo ""

    # 生成音频（会自动创建 audio/timeline.json）
    "$PYTHON" generate_edge_tts.py "$STORYBOARD" ./audio --yes

    if [ ! -f "audio/timeline.json" ]; then
        echo "❌ 错误: timeline.json 未生成"
        exit 1
    fi

    echo ""
    echo "✅ 音频生成完成，时长已记录"
    echo ""
}

# 步骤 2: 渲染视频
render_video() {
    echo "🎬 步骤 2: 渲染视频（音频驱动）"
    echo "----------------------------------------"

    # 确定场景文件
    SCENE_NAME="GeometryProof"
    if [ -f "scene.py" ]; then
        SCENE_FILE="scene.py"
    else
        echo "❌ 错误: 未找到 scene.py"
        exit 1
    fi

    echo "场景: $SCENE_FILE - $SCENE_NAME"
    echo "分辨率: 1080x1920 (竖屏)"
    echo ""

    # 检查 timeline.json
    if [ -f "audio/timeline.json" ]; then
        TOTAL_DURATION=$(cat audio/timeline.json | grep -o '"total_duration": [0-9.]*' | cut -d' ' -f2)
        echo "📊 音频总时长: ${TOTAL_DURATION}秒"
        echo "   (视频将自动同步各场景时长)"
        echo ""
    fi

    # 渲染高质量 MP4
    "$MANIM" -pqh --format=mp4 "$SCENE_FILE" "$SCENE_NAME"

    echo ""
    echo "✅ 视频渲染完成"
    echo ""
}

# 步骤 3: 合并音视频
merge_audio_video() {
    echo "🔧 步骤 3: 合并音视频"
    echo "----------------------------------------"

    # 查找生成的视频
    VIDEO_FILE="media/videos/scene/1920p30/GeometryProof.mp4"

    if [ ! -f "$VIDEO_FILE" ]; then
        echo "❌ 错误: 未找到视频文件"
        exit 1
    fi

    VIDEO_DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$VIDEO_FILE" 2>/dev/null | cut -d. -f1)
    echo "视频时长: ${VIDEO_DURATION}秒"

    # 合并音频
    if [ -d "audio" ] && [ "$(ls audio/audio_*.mp3 2>/dev/null | wc -l)" -gt 0 ]; then
        echo "合并音频..."

        # 创建音频列表
        AUDIO_LIST="audio_list.txt"
        echo "" > "$AUDIO_LIST"
        for f in audio/audio_*.mp3; do
            [ -f "$f" ] && echo "file '../$f'" >> "$AUDIO_LIST"
        done

        # 合并音频
        ffmpeg -f concat -safe 0 -i "$AUDIO_LIST" -c copy /tmp/combined_audio.mp3 -y 2>/dev/null || true

        if [ -f "/tmp/combined_audio.mp3" ]; then
            AUDIO_DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 /tmp/combined_audio.mp3 2>/dev/null | cut -d. -f1)
            echo "音频时长: ${AUDIO_DURATION}秒"
            echo ""

            # 合并视频和音频（取较长者）
            ffmpeg -i "$VIDEO_FILE" -i /tmp/combined_audio.mp3 -c:v copy -c:a aac \
                   -shortest final_video.mp4 -y 2>&1 | grep -E "(Duration|Output|Stream)" || true

            echo ""
            echo "✅ 已生成: final_video.mp4"

            # 验证时长
            if [ -f "final_video.mp4" ]; then
                FINAL_DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 final_video.mp4 2>/dev/null | cut -d. -f1)
                echo "   最终时长: ${FINAL_DURATION}秒"
            fi
        else
            cp "$VIDEO_FILE" final_video.mp4
            echo "⚠️  未找到音频，仅复制视频"
        fi
    else
        cp "$VIDEO_FILE" final_video.mp4
        echo "⚠️  未找到音频，仅复制视频"
    fi
}

# 执行流程
if [ "$1" != "--skip-audio" ]; then
    generate_audio
else
    echo "📢 步骤 1: 跳过音频生成"
    echo "   (使用现有 audio/timeline.json)"
    echo ""

    if [ ! -f "audio/timeline.json" ]; then
        echo "❌ 错误: audio/timeline.json 不存在"
        echo "   请先运行: ./render.sh (不带 --skip-audio)"
        exit 1
    fi
    echo ""
fi

render_video
merge_audio_video

echo ""
echo "=========================================="
echo "✅ 全部完成！"
echo "=========================================="
echo ""
echo "输出文件:"
echo "  📹 final_video.mp4     - 最终视频（含音频）"
echo "  📁 media/videos/        - 原始视频文件"
echo "  🎵 audio/               - 音频文件和时长数据"
echo "  📊 audio/timeline.json  - 音频时长记录"
echo ""
echo "💡 提示:"
echo "   - 修改分镜后重新运行 ./render.sh 即可"
echo "   - 画面会自动根据 audio/timeline.json 中的时长同步"
echo ""
