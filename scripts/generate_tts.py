#!/usr/bin/env python3
"""
TTS 生成脚本

功能：
- 从 CSV 文件读取对白列表
- 使用 Edge TTS (xiaoxiao 语音) 生成音频
- 输出到指定目录
- 生成 audio_info.json 供验证脚本使用

CSV 格式：
    filename,text
    audio_001_开场.wav,"大家好，今天我们来学习..."
    audio_002_介绍.wav,"首先，让我们来看这个图形..."

使用：
    python generate_tts.py audio_list.csv ./audio --voice xiaoxiao

支持的声音：
    xiaoxiao (晓晓，女声，默认)
    xiaoyi (晓伊，女声)
    yunyang (云扬，男声)
    yunjian (云健，男声)
"""

import sys
import os
import csv
import json
import asyncio
from pathlib import Path

# 检查 edge-tts
try:
    import edge_tts
except ImportError:
    print("Error: edge-tts 未安装")
    print("请运行: uv pip install edge-tts")
    sys.exit(1)


# 声音映射表
VOICE_MAP = {
    'xiaoxiao': 'zh-CN-XiaoxiaoNeural',      # 晓晓，女声，默认
    'xiaoyi': 'zh-CN-XiaoyiNeural',          # 晓伊，女声
    'yunyang': 'zh-CN-YunyangNeural',        # 云扬，男声
    'yunjian': 'zh-CN-YunjianNeural',        # 云健，男声
    'xiaoxiao-dialect': 'zh-CN-XiaoxiaoNeural',  # 晓晓方言
    'xiaoxiao-multilingual': 'zh-CN-XiaoxiaoMultilingualNeural',
}


async def generate_audio(text, output_path, voice='xiaoxiao'):
    """
    生成单条音频

    参数:
        text: 文本内容
        output_path: 输出文件路径
        voice: 声音名称

    返回:
        (success, duration)
    """
    voice_id = VOICE_MAP.get(voice, VOICE_MAP['xiaoxiao'])

    try:
        communicate = edge_tts.Communicate(text, voice_id)
        await communicate.save(output_path)

        # 获取时长
        duration = await get_audio_duration(output_path)
        return True, duration
    except Exception as e:
        print(f"  Error generating {output_path}: {e}")
        return False, 0


async def get_audio_duration(audio_path):
    """获取音频时长"""
    try:
        from mutagen.mp3 import MP3
        audio = MP3(audio_path)
        return audio.info.length
    except:
        pass

    try:
        import wave
        with wave.open(audio_path, 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            return frames / float(rate)
    except:
        pass

    return 0


def parse_csv(csv_path):
    """
    解析 CSV 文件

    支持格式：
    - 标准 CSV: filename,text
    - 带 BOM 的 UTF-8
    - 不同分隔符（优先逗号，支持分号）
    """
    entries = []

    # 尝试不同编码
    encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']

    for encoding in encodings:
        try:
            with open(csv_path, 'r', encoding=encoding) as f:
                # 尝试检测分隔符
                sample = f.read(2048)
                f.seek(0)

                delimiter = ','
                if ';' in sample and sample.count(';') > sample.count(','):
                    delimiter = ';'

                reader = csv.DictReader(f, delimiter=delimiter)

                for row in reader:
                    # 支持不同的列名
                    filename = row.get('filename') or row.get('文件名') or row.get('file')
                    text = row.get('text') or row.get('对白') or row.get('content') or row.get('读白')

                    if filename and text:
                        entries.append({
                            'filename': filename,
                            'text': text.strip()
                        })

            try:
                print(f"✓ 解析 CSV 成功 ({encoding}), 共 {len(entries)} 条")
            except UnicodeEncodeError:
                print(f"[OK] 解析 CSV 成功 ({encoding}), 共 {len(entries)} 条")
            return entries

        except Exception as e:
            continue

    # 如果都失败，尝试简单解析
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[1:]:  # 跳过标题行
                parts = line.strip().split(',', 1)
                if len(parts) == 2:
                    entries.append({
                        'filename': parts[0].strip(),
                        'text': parts[1].strip().strip('"')
                    })
        if entries:
            try:
                print(f"✓ 简单解析 CSV 成功, 共 {len(entries)} 条")
            except UnicodeEncodeError:
                print(f"[OK] 简单解析 CSV 成功, 共 {len(entries)} 条")
            return entries
    except:
        pass

    print("Error: 无法解析 CSV 文件")
    return []


async def generate_all(csv_path, output_dir, voice='xiaoxiao'):
    """批量生成音频"""
    # 解析 CSV
    entries = parse_csv(csv_path)
    if not entries:
        return False

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 生成音频
    results = []
    total = len(entries)

    print(f"\n开始生成音频 (声音: {voice})...")
    print("="*50)

    for i, entry in enumerate(entries, 1):
        filename = entry['filename']
        text = entry['text']

        # 确保文件扩展名正确
        if not filename.endswith(('.wav', '.mp3')):
            filename += '.wav'

        output_path = os.path.join(output_dir, filename)

        print(f"[{i}/{total}] {filename}")
        print(f"    文本: {text[:50]}{'...' if len(text) > 50 else ''}")

        success, duration = await generate_audio(text, output_path, voice)

        if success:
            # 从文件名提取幕号
            scene_num = extract_scene_number(filename)
            results.append({
                'scene': scene_num,
                'file': filename,
                'text': text,
                'duration': round(duration, 2)
            })
            try:
                print(f"    ✓ 时长: {duration:.2f}s")
            except UnicodeEncodeError:
                print(f"    [OK] 时长: {duration:.2f}s")
        else:
            try:
                print(f"    ✗ 失败")
            except UnicodeEncodeError:
                print(f"    [FAIL] 失败")

        print()

    # 生成 audio_info.json
    if results:
        info = {
            'files': results,
            'total_duration': sum(r['duration'] for r in results),
            'count': len(results),
            'voice': voice
        }

        info_path = os.path.join(output_dir, 'audio_info.json')
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)

        print(f"已生成: {info_path}")

    return len(results) == len(entries)


def extract_scene_number(filename):
    """从文件名提取幕号"""
    # 支持格式: audio_001_xxx.wav, scene_01_xxx.wav, 001_xxx.wav
    import re
    match = re.search(r'\d+', filename)
    if match:
        return int(match.group())
    return 0


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_tts.py <csv_file> [output_dir] [options]")
        print("")
        print("参数:")
        print("  csv_file      CSV 文件路径")
        print("  output_dir    输出目录 (默认: ./audio)")
        print("")
        print("选项:")
        print("  --voice VOICE 声音选择 (默认: xiaoxiao)")
        print("")
        print("可用声音:")
        for k, v in VOICE_MAP.items():
            print(f"  {k:20s} - {v}")
        print("")
        print("示例:")
        print("  python generate_tts.py audio_list.csv ./audio")
        print("  python generate_tts.py audio_list.csv ./audio --voice yunyang")
        sys.exit(1)

    csv_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else "./audio"

    # 解析选项
    voice = 'xiaoxiao'
    for i, arg in enumerate(sys.argv):
        if arg == '--voice' and i + 1 < len(sys.argv):
            voice = sys.argv[i + 1]

    # 检查文件
    if not os.path.exists(csv_path):
        print(f"Error: CSV 文件不存在: {csv_path}")
        sys.exit(1)

    print(f"CSV 文件: {csv_path}")
    print(f"输出目录: {output_dir}")
    print(f"使用声音: {voice}")
    print("")

    # 运行
    success = asyncio.run(generate_all(csv_path, output_dir, voice))

    if success:
        try:
            print("\n✅ 全部生成成功！")
        except UnicodeEncodeError:
            print("\n[OK] 全部生成成功！")
        sys.exit(0)
    else:
        try:
            print("\n⚠️ 部分生成失败")
        except UnicodeEncodeError:
            print("\n[WARN] 部分生成失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
