#!/usr/bin/env python3
"""
使用 Edge TTS 从分镜脚本生成配音文件

用法:
    python generate_edge_tts.py <分镜脚本.md> [输出目录] [--voice VOICE]

示例:
    python generate_edge_tts.py 几何_20260128_正方形面积问题_分镜.md ./audio
    python generate_edge_tts.py 分镜.md ./audio --voice zh-CN-YunjianNeural
"""

import asyncio
import edge_tts
import re
import os
import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Optional

try:
    import miniaudio
    HAS_MINIAUDIO = True
except ImportError:
    HAS_MINIAUDIO = False

# Edge TTS 支持的中文语音
VOICES = {
    'xiaoxiao': 'zh-CN-XiaoxiaoNeural',      # 女声，温暖（默认）
    'xiaoyi': 'zh-CN-XiaoyiNeural',          # 女声，清脆
    'yunjian': 'zh-CN-YunjianNeural',        # 男声，沉稳
    'yunxi': 'zh-CN-YunxiNeural',            # 男声，温和
    'yunxia': 'zh-CN-YunxiaNeural',          # 男声，活力
    'yunyang': 'zh-CN-YunyangNeural',        # 男声，专业
}

DEFAULT_VOICE = 'zh-CN-XiaoxiaoNeural'


def get_audio_duration(audio_path: str) -> float:
    """
    获取音频文件的时长（秒）

    参数:
        audio_path: 音频文件路径

    返回:
        时长（秒）
    """
    try:
        if HAS_MINIAUDIO:
            info = miniaudio.get_file_info(audio_path)
            return info.duration
        else:
            # 使用 ffprobe 或 fallback
            import subprocess
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                 '-of', 'default=noprint_wrappers=1:nokey=1', audio_path],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return float(result.stdout.strip())
    except Exception as e:
        print(f"  警告: 无法获取音频时长: {e}")
    return 0.0


def parse_storyboard(md_content: str):
    """解析分镜脚本，提取读白"""
    scenes = []
    num_map = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}

    lines = md_content.split('\n')
    current_scene = None
    in_voiceover = False
    voiceover_lines = []

    for line in lines:
        if line.startswith('###') and '第' in line and '幕' in line and '（' in line and '秒）' in line:
            if current_scene and current_scene.get('voiceover'):
                scenes.append(current_scene)

            num_char = ''
            for c in line:
                if c in num_map:
                    num_char = c
                    break

            idx_mu = line.find('幕')
            idx_bracket = line.find('（')
            if idx_mu > 0 and idx_bracket > idx_mu:
                title = line[idx_mu+1:idx_bracket].strip()
                if ':' in title:
                    title = title[1:]
                if '：' in title:
                    title = title[1:]

                idx_end = line.find('秒）')
                duration = line[idx_bracket+1:idx_end] if idx_end > 0 else '0'

                current_scene = {
                    "scene_num": num_map.get(num_char, len(scenes) + 1),
                    "title": title.strip(),
                    "duration": f"{duration}秒",
                    "voiceover": ""
                }
                in_voiceover = False
                voiceover_lines = []
                continue

        if current_scene and '**读白**' in line:
            in_voiceover = True
            if ':' in line or '：' in line:
                content_part = line.split(':', 1)[-1].split('：', 1)[-1].strip()
                if content_part and content_part.startswith('"') and content_part.endswith('"'):
                    content_part = content_part[1:-1]
                if content_part and not content_part.startswith('-') and not content_part.startswith('示例'):
                    voiceover_lines = [content_part]
            continue

        if in_voiceover and current_scene:
            if line.startswith('**') and '读白' not in line:
                in_voiceover = False
                if voiceover_lines:
                    current_scene['voiceover'] = ' '.join(voiceover_lines).strip()
                continue

            if line.strip() and not line.strip().startswith('示例') and not line.strip().startswith('-'):
                voiceover_lines.append(line.strip())

        if current_scene and '**情感**' in line:
            if ':' in line or '：' in line:
                content_part = line.split(':', 1)[-1].split('：', 1)[-1].strip()
                if content_part and not content_part.startswith('-'):
                    current_scene['emotion'] = content_part.split('/')[0].strip()

    if current_scene and current_scene.get('voiceover'):
        scenes.append(current_scene)

    return scenes


async def generate_audio(text: str, output_file: str, voice: str = DEFAULT_VOICE):
    """使用 Edge TTS 生成音频"""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)
    return output_file


async def main():
    parser = argparse.ArgumentParser(
        description='从分镜脚本生成 Edge TTS 配音音频',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用默认语音（Xiaoxiao 女声）
  python generate_edge_tts.py 分镜.md ./audio

  # 使用 Yunjian 男声
  python generate_edge_tts.py 分镜.md ./audio --voice yunjian

可用语音:
  xiaoxiao  - 女声，温暖（默认）
  xiaoyi    - 女声，清脆
  yunjian   - 男声，沉稳
  yunxi     - 男声，温和
  yunxia    - 男声，活力
  yunyang   - 男声，专业
        """
    )

    parser.add_argument('storyboard', help='分镜脚本 Markdown 文件路径')
    parser.add_argument('output_dir', nargs='?', default='./audio', help='音频输出目录（默认：./audio）')
    parser.add_argument('--voice', default='xiaoxiao', choices=list(VOICES.keys()),
                       help='语音选择（默认：xiaoxiao）')
    parser.add_argument('--yes', action='store_true', help='跳过确认直接生成')

    args = parser.parse_args()

    # 检查分镜文件
    storyboard_path = Path(args.storyboard)
    if not storyboard_path.exists():
        print(f"错误: 分镜文件不存在: {storyboard_path}")
        sys.exit(1)

    # 读取分镜内容
    print(f"读取分镜脚本: {storyboard_path}")
    with open(storyboard_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 解析分镜
    print("解析分镜脚本...")
    scenes = parse_storyboard(content)
    print(f"找到 {len(scenes)} 个场景\n")

    if not scenes:
        print("错误: 未找到任何场景（请检查分镜脚本格式）")
        sys.exit(1)

    # 创建输出目录
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    # 获取语音
    voice = VOICES.get(args.voice, DEFAULT_VOICE)

    # 显示场景列表
    print("场景列表:")
    for scene in scenes:
        print(f"  场景 {scene['scene_num']}: {scene['title']}")
        print(f"    读白: {scene['voiceover'][:50]}...")
        print()

    # 确认
    if not args.yes:
        response = input(f"是否继续生成音频? (使用语音: {args.voice}) (y/n): ").strip().lower()
        if response != 'y':
            print("已取消")
            sys.exit(0)

    # 生成所有场景的音频
    print(f"\n开始生成音频 (使用 Edge TTS - {voice})...\n")

    generated_files = []
    scenes_with_duration = []

    for scene in scenes:
        num = scene['scene_num']
        title = scene['title']
        voiceover = scene['voiceover']

        if not voiceover:
            print(f"跳过场景 {num}: 无读白内容")
            continue

        filename = f"audio_{num:03d}_{title}.mp3"
        output_path = output_dir / filename

        print(f"生成场景 {num}: {title}")
        try:
            await generate_audio(voiceover, str(output_path), voice)
            file_size = output_path.stat().st_size / 1024

            # 获取音频时长
            duration = get_audio_duration(str(output_path))
            scene['duration'] = duration
            scenes_with_duration.append(scene)

            print(f"  ✓ 已生成: {filename} ({file_size:.1f} KB, {duration:.2f}秒)")
            generated_files.append(output_path)
        except Exception as e:
            print(f"  ✗ 错误: {e}")

    # 生成清单文件（包含时长）
    manifest_path = output_dir / "audio_manifest.json"
    manifest = {
        "total_scenes": len(scenes_with_duration),
        "voice": voice,
        "scenes": [
            {
                "scene_num": s['scene_num'],
                "title": s['title'],
                "voiceover": s['voiceover'],
                "duration": s.get('duration', 0),
                "audio_file": f"audio_{s['scene_num']:03d}_{s['title']}.mp3"
            }
            for s in scenes_with_duration
        ]
    }
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    # 生成时间轴文件（用于Manim生成）
    timeline_path = output_dir / "timeline.json"
    timeline = {
        "total_duration": sum(s.get('duration', 0) for s in scenes_with_duration),
        "scenes": [
            {
                "index": i + 1,
                "scene_num": s['scene_num'],
                "title": s['title'],
                "duration": s.get('duration', 0),
                "audio_file": f"audio_{s['scene_num']:03d}_{s['title']}.mp3",
                "voiceover": s['voiceover'][:100] + "..." if len(s['voiceover']) > 100 else s['voiceover']
            }
            for i, s in enumerate(scenes_with_duration)
        ]
    }
    with open(timeline_path, 'w', encoding='utf-8') as f:
        json.dump(timeline, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"音频生成完成！")
    print(f"生成文件数: {len(generated_files)}/{len(scenes)}")
    print(f"总时长: {timeline['total_duration']:.2f}秒")
    print(f"输出目录: {output_dir}")
    print(f"语音: {voice}")
    print(f"\n生成的文件:")
    for f in sorted(generated_files):
        size_kb = f.stat().st_size / 1024
        print(f"  - {f.name} ({size_kb:.1f} KB)")
    print(f"\n音频清单: {manifest_path}")
    print(f"时间轴文件: {timeline_path}")
    print(f"{'='*60}")
    print("\n✅ 音频时长已自动记录，可直接用于生成Manim代码")


if __name__ == "__main__":
    asyncio.run(main())
