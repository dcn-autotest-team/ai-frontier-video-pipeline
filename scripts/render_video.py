#!/usr/bin/env python3
"""
AI前沿 — 通用视频渲染器
品牌：AI前沿 | 风格：暗夜科技蓝
Ken Burns 运镜 + xfade 转场 + 暗角调色 + 字幕烧录 + 音频混流

用法：
  python render_video.py --slides-dir slides_branded --voice voice.mp3 --bgm bgm.mp3 --srt subtitle.srt --ep 01 --output output.mp4
"""

import subprocess, re, shutil, math, argparse, sys
from pathlib import Path

# ─── 固定配置 ─────────────────────────────────────────
import shutil
FFMPEG = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe") or r"ffmpeg.exe"
W, H = 1080, 1920
FPS = 30
XFADE_DUR = 0.7
SCALE_W = W * 3 // 2   # 1620 — Ken Burns 预放大
SCALE_H = H * 3 // 2   # 2880


# ─── 工具函数 ─────────────────────────────────────────

def get_duration(path):
    r = subprocess.run([FFMPEG, "-i", str(path)], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", r.stderr)
    return int(m.group(1))*3600 + int(m.group(2))*60 + float(m.group(3)) if m else 50.0


def probe_size(path):
    r = subprocess.run([FFMPEG, "-i", str(path)], capture_output=True, text=True)
    m = re.search(r"(\d+)x(\d+)", r.stderr)
    return (int(m.group(1)), int(m.group(2))) if m else (1080, 1920)


def run_ffmpeg(cmd, label=""):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ❌ {label} 失败: {r.stderr[-600:]}")
        return False
    return True


# ─── Ken Burns 运镜预设 ───────────────────────────────
# 每张幻灯片使用不同的运镜方案，循环使用

CAMERA_PRESETS = [
    {"name": "推近·紧迫", "z": "min(1+0.3*on/{f},1.3)",
     "x": "iw/2-(iw/zoom/2)", "y": "max(ih/2-(ih/zoom/2)+ih*0.05*on/{f},0)"},
    {"name": "平移·跟随", "z": "1.15",
     "x": "(iw-iw/zoom)*on/{f}", "y": "ih/2-(ih/zoom/2)"},
    {"name": "拉远·揭示", "z": "max(1.35-0.35*on/{f},1.0)",
     "x": "iw/2-(iw/zoom/2)", "y": "ih/2-(ih/zoom/2)"},
    {"name": "急推·冲击", "z": "min(1+0.5*on/{f},1.5)",
     "x": "iw/2-(iw/zoom/2)", "y": "(ih-ih/zoom)*0.25"},
    {"name": "拉远·扩展", "z": "max(1.3-0.3*on/{f},1.0)",
     "x": "(iw-iw/zoom)*0.15*on/{f}", "y": "ih/2-(ih/zoom/2)"},
    {"name": "推近·上行", "z": "min(1.05+0.2*on/{f},1.25)",
     "x": "iw/2-(iw/zoom/2)", "y": "max((ih-ih/zoom)*(0.6-0.4*on/{f}),0)"},
]

TRANSITIONS = ["fadeblack", "smoothright", "fade", "dissolve", "fadeblack"]


# ═══════════════════════════════════════════════════════
# 渲染主流程
# ═══════════════════════════════════════════════════════

def render_video(slides_dir, voice_path, bgm_path, srt_path, output_path, ep_num):
    slides_dir = Path(slides_dir)
    voice_path = Path(voice_path)
    bgm_path = Path(bgm_path) if bgm_path else None
    srt_path = Path(srt_path) if srt_path else None
    output_path = Path(output_path)

    temp_dir = output_path.parent / "_render_temp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    # 收集幻灯片
    slides = sorted(slides_dir.glob("slide_*.png"))
    if not slides:
        print("❌ 未找到分镜图片！")
        sys.exit(1)
    num_slides = len(slides)

    # 计算时长
    audio_dur = get_duration(voice_path)
    slide_dur = (audio_dur + (num_slides - 1) * XFADE_DUR) / num_slides
    slide_frames = int(slide_dur * FPS)

    print("=" * 60)
    print(f"AI前沿 EP.{ep_num:02d} — 通用视频渲染器")
    print("=" * 60)
    print(f"  音频时长: {audio_dur:.2f}s")
    print(f"  幻灯片数: {num_slides}")
    print(f"  每张时长: {slide_dur:.2f}s ({slide_frames} frames)")
    print(f"  转场次数: {num_slides - 1}")
    print()

    # ─── Step 1: Ken Burns 运镜片段 ───────────────────
    print("[1/4] 生成 Ken Burns 运镜片段...")
    seg_paths = []

    for i, slide_path in enumerate(slides):
        seg_path = temp_dir / f"seg_{i:02d}.mp4"
        seg_paths.append(seg_path)

        cam = CAMERA_PRESETS[i % len(CAMERA_PRESETS)]
        f = slide_frames
        z_expr = cam['z'].format(f=f)
        x_expr = cam['x'].format(f=f)
        y_expr = cam['y'].format(f=f)

        vf = (
            f"scale={SCALE_W}:{SCALE_H},"
            f"zoompan=z='{z_expr}':x='{x_expr}':y='{y_expr}'"
            f":d={slide_frames}:s={W}x{H}:fps={FPS}"
        )

        cmd = [
            FFMPEG, "-y",
            "-i", str(slide_path),
            "-vf", vf,
            "-t", f"{slide_dur:.3f}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-pix_fmt", "yuv420p",
            str(seg_path),
        ]

        print(f"  Slide {i+1}: {cam['name']}")
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            # 降级：简单居中推近
            print(f"    ⚠️ 降级到简单推近...")
            vf_fb = (
                f"scale={SCALE_W}:{SCALE_H},"
                f"zoompan=z='min(zoom+0.0012,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                f":d={slide_frames}:s={W}x{H}:fps={FPS}"
            )
            cmd_fb = cmd.copy()
            cmd_fb[cmd_fb.index("-vf") + 1] = vf_fb
            r2 = subprocess.run(cmd_fb, capture_output=True, text=True)
            if r2.returncode != 0:
                # 终极降级：静态缩放
                cmd_static = [
                    FFMPEG, "-y",
                    "-loop", "1", "-i", str(slide_path),
                    "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS}",
                    "-t", f"{slide_dur:.3f}",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "20",
                    "-pix_fmt", "yuv420p",
                    str(seg_path),
                ]
                subprocess.run(cmd_static, capture_output=True, text=True)
        else:
            seg_dur = get_duration(seg_path)
            print(f"    ✅ {seg_dur:.2f}s")

    print("  全部片段生成完成！")

    # ─── Step 2: xfade 转场合成 ──────────────────────
    print("\n[2/4] xfade 转场合成...")

    inputs = []
    for p in seg_paths:
        inputs.extend(["-i", str(p)])

    offsets = []
    for i in range(num_slides - 1):
        off = (i + 1) * slide_dur - (i + 1) * XFADE_DUR
        offsets.append(off)

    filter_parts = []
    prev_label = "0:v"
    for i in range(num_slides - 1):
        next_input = f"{i+1}:v"
        out_label = f"v{i:02d}" if i < num_slides - 2 else "vout"
        trans = TRANSITIONS[i % len(TRANSITIONS)]
        filter_parts.append(
            f"[{prev_label}][{next_input}]xfade=transition={trans}"
            f":duration={XFADE_DUR}:offset={offsets[i]:.3f}[{out_label}]"
        )
        prev_label = out_label

    visual_mp4 = temp_dir / "visual_xfade.mp4"

    cmd_xfade = [
        FFMPEG, "-y",
        *inputs,
        "-filter_complex", ";".join(filter_parts),
        "-map", "[vout]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p",
        str(visual_mp4),
    ]

    r = subprocess.run(cmd_xfade, capture_output=True, text=True)
    if r.returncode != 0:
        # 降级：全部用 fade
        print("  ⚠️ 降级到 fade 转场...")
        filter_parts_fb = []
        prev_label = "0:v"
        for i in range(num_slides - 1):
            next_input = f"{i+1}:v"
            out_label = f"v{i:02d}" if i < num_slides - 2 else "vout"
            filter_parts_fb.append(
                f"[{prev_label}][{next_input}]xfade=transition=fade"
                f":duration={XFADE_DUR}:offset={offsets[i]:.3f}[{out_label}]"
            )
            prev_label = out_label
        cmd_fb = [
            FFMPEG, "-y",
            *inputs,
            "-filter_complex", ";".join(filter_parts_fb),
            "-map", "[vout]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-pix_fmt", "yuv420p",
            str(visual_mp4),
        ]
        r2 = subprocess.run(cmd_fb, capture_output=True, text=True)
        if r2.returncode != 0:
            # 终极降级：concat
            print("  ⚠️ 终极降级：concat 拼接...")
            concat_txt = temp_dir / "concat.txt"
            lines = [f"file '{str(p).replace(chr(92), '/')}'" for p in seg_paths]
            concat_txt.write_text("\n".join(lines), encoding="utf-8")
            cmd_concat = [
                FFMPEG, "-y", "-f", "concat", "-safe", "0",
                "-i", str(concat_txt),
                "-c:v", "libx264", "-preset", "fast", "-crf", "20",
                "-pix_fmt", "yuv420p",
                str(visual_mp4),
            ]
            subprocess.run(cmd_concat, capture_output=True, text=True)

    vis_dur = get_duration(visual_mp4)
    print(f"  ✅ 视觉视频: {vis_dur:.2f}s")

    # ─── Step 3: 暗角 + 调色 + 字幕 + 混音 ──────────
    print("\n[3/4] 暗角 + 调色 + 字幕 + 混音...")

    # 音频混合
    if bgm_path and bgm_path.exists():
        bgm_dur = min(get_duration(bgm_path), audio_dur + 5)
        audio_filter = (
            f"[1:a]volume=1.0[voice];"
            f"[2:a]atrim=0:{bgm_dur:.0f},afade=t=out:st={audio_dur-4:.0f}:d=4,volume=0.12[bgm];"
            f"[voice][bgm]amix=inputs=2:duration=first:dropout_transition=3[aout]"
        )
        audio_inputs = ["-i", str(voice_path), "-i", str(bgm_path)]
    else:
        audio_filter = None
        audio_inputs = ["-i", str(voice_path)]

    # 字幕处理
    video_filter_parts = [
        "vignette=angle=0.3:mode=forward",
        "eq=contrast=1.08:brightness=0.01:saturation=1.1",
    ]

    subtitle_style = (
        "FontName=Noto Sans SC,"
        "FontSize=30,"
        "PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00000000,"
        "BackColour=&HA0000000,"
        "BorderStyle=4,"
        "Outline=3,"
        "Shadow=0.5,"
        "Alignment=2,"
        "MarginV=80"
    )

    if srt_path and srt_path.exists():
        # 拷贝SRT到临时目录（避免路径中文问题）
        temp_srt = temp_dir / "subtitle.srt"
        shutil.copy2(srt_path, temp_srt)
        srt_escaped = str(temp_srt).replace("\\", "/").replace(":", "\\\\:")
        video_filter_parts.append(
            f"subtitles='{srt_escaped}':force_style='{subtitle_style}'"
        )

    video_filter = ",".join(video_filter_parts)

    # 构建最终合成命令
    cmd_final = [
        FFMPEG, "-y",
        "-i", str(visual_mp4),
        *audio_inputs,
    ]

    if audio_filter:
        cmd_final.extend(["-filter_complex", audio_filter])
        cmd_final.extend(["-map", "0:v", "-map", "[aout]"])
    else:
        cmd_final.extend(["-map", "0:v", "-map", "1:a"])

    cmd_final.extend([
        "-vf", video_filter,
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        str(output_path),
    ])

    success = False
    r = subprocess.run(cmd_final, capture_output=True, text=True)
    if r.returncode == 0:
        success = True
    else:
        # 去字幕重试
        print("  ⚠️ 字幕失败，尝试无字幕版...")
        vf_nosub = "vignette=angle=0.3:mode=forward,eq=contrast=1.08:brightness=0.01:saturation=1.1"
        cmd_nosub = cmd_final.copy()
        cmd_nosub[cmd_nosub.index("-vf") + 1] = vf_nosub
        r2 = subprocess.run(cmd_nosub, capture_output=True, text=True)
        if r2.returncode == 0:
            success = True
            print("  ✅ 无字幕版合成完成")

    if not success:
        print("  ❌ 视频合成失败！")
        sys.exit(1)

    # ─── Step 4: 质检 ────────────────────────────────
    print("\n[4/4] 质检...")

    size = output_path.stat().st_size
    actual_dur = get_duration(output_path)

    print()
    print("=" * 60)
    print(f"✅ AI前沿 EP.{ep_num:02d} — 质检报告")
    print("=" * 60)
    print(f"  输出路径: {output_path}")
    print(f"  文件大小: {size:,} bytes ({size/1024/1024:.2f} MiB)")
    print(f"  实际时长: {actual_dur:.2f}s")
    print(f"  目标时长: {audio_dur:.2f}s")
    print(f"  运镜方案: {num_slides} 张幻灯片")
    print("=" * 60)

    # 清理临时文件
    print("\n清理临时片段...")
    for p in seg_paths:
        if p.exists():
            p.unlink()
    print("  ✅ 临时片段已清理")

    return str(output_path)


# ─── 命令行入口 ──────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AI前沿 通用视频渲染器")
    parser.add_argument("--slides-dir", required=True, help="分镜图片目录")
    parser.add_argument("--voice", required=True, help="旁白音频文件路径")
    parser.add_argument("--bgm", default=None, help="BGM音频文件路径（可选）")
    parser.add_argument("--srt", default=None, help="SRT字幕文件路径（可选）")
    parser.add_argument("--ep", type=int, default=1, help="集号")
    parser.add_argument("--output", default=None, help="输出MP4文件路径（默认: output/epXX.mp4）")
    args = parser.parse_args()

    if args.output is None:
        output_dir = Path("output")
        output_dir.mkdir(parents=True, exist_ok=True)
        args.output = str(output_dir / f"ep{args.ep:02d}.mp4")

    render_video(args.slides_dir, args.voice, args.bgm, args.srt, args.output, args.ep)


if __name__ == "__main__":
    main()
