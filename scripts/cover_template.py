#!/usr/bin/env python3
"""
AI前沿 - 视频封面模板生成器
品牌：AI前沿 | 风格：暗夜科技蓝 | 输出：竖屏(1080x1920) + 横屏(1920x1080)

用法：
  python cover_template.py --title "Cerebras推理速度革命" --ep 01
  python cover_template.py --title "OpenAI发布GPT-5" --ep 02 --date 2026-05-26
"""

import argparse
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ── 品牌设定 ──────────────────────────────────────────
BRAND = "AI前沿"
TAGLINE = "第一时间 · 深度解读"

# ── 配色 ──────────────────────────────────────────────
class Palette:
    BG_TOP       = (8, 12, 38)       # 深蓝黑
    BG_BOTTOM    = (22, 8, 56)       # 暗紫
    NEON_BLUE    = (0, 212, 255)     # 霓虹蓝
    NEON_PURPLE  = (139, 92, 246)    # 电紫
    WHITE        = (255, 255, 255)
    GREY_LIGHT   = (180, 190, 210)
    GREY_DIM     = (80, 90, 110)
    ACCENT_LINE  = (0, 180, 240, 60) # 半透明蓝线
    GLOW_BLUE    = (0, 160, 255, 40)

# ── 字体 ──────────────────────────────────────────────
FONT_DIR = Path(r"C:\Windows\Fonts")

def find_font(candidates, size):
    """按优先级尝试字体"""
    for name in candidates:
        path = FONT_DIR / name
        if path.exists():
            return ImageFont.truetype(str(path), size)
    # 回退默认
    return ImageFont.load_default()

# 中文字体优先级
CN_FONTS = ["NotoSansSC-VF.ttf", "msyh.ttc", "simhei.ttf", "STXIHEI.TTF"]
# 英文/数字字体
EN_FONTS = ["NotoSansSC-VF.ttf", "msyh.ttc", "consola.ttf", "arial.ttf"]


# ── 绘图工具 ──────────────────────────────────────────

def gradient_bg(w, h, top_color, bottom_color):
    """垂直渐变背景"""
    img = Image.new("RGB", (w, h))
    for y in range(h):
        t = y / h
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        for x in range(w):
            img.putpixel((x, y), (r, g, b))
    return img

def gradient_bg_fast(w, h, top_color, bottom_color):
    """快速渐变背景（行级绘制）"""
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return img

def draw_hexagon(draw, cx, cy, size, outline_color, width=1):
    """绘制六边形"""
    points = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        x = cx + size * math.cos(angle)
        y = cy + size * math.sin(angle)
        points.append((x, y))
    draw.polygon(points, outline=outline_color, width=width)

def draw_circuit_lines(draw, w, h, color, count=12):
    """绘制电路板风格线条"""
    random.seed(42)  # 固定种子保持一致性
    for _ in range(count):
        x1 = random.randint(0, w)
        y1 = random.randint(0, h)
        # 水平或垂直线段
        direction = random.choice(['h', 'v'])
        length = random.randint(40, 200)
        if direction == 'h':
            x2 = x1 + length
            y2 = y1
        else:
            x2 = x1
            y2 = y1 + length
        draw.line([(x1, y1), (x2, y2)], fill=color, width=1)
        # 端点圆点
        draw.ellipse([x1-2, y1-2, x1+2, y1+2], fill=color)
        # 随机拐角
        if random.random() > 0.5:
            if direction == 'h':
                draw.line([(x2, y2), (x2, y2 + random.randint(20, 60))], fill=color, width=1)
            else:
                draw.line([(x2, y2), (x2 + random.randint(20, 60), y2)], fill=color, width=1)

def draw_particles(draw, w, h, color, count=40):
    """绘制散点粒子"""
    random.seed(88)
    for _ in range(count):
        x = random.randint(0, w)
        y = random.randint(0, h)
        size = random.randint(1, 3)
        alpha = random.randint(30, 120)
        c = (*color[:3], alpha) if len(color) == 4 else (*color, alpha)
        draw.ellipse([x-size, y-size, x+size, y+size], fill=c)

def draw_scan_lines(draw, w, h, color, gap=4):
    """绘制扫描线效果"""
    for y in range(0, h, gap):
        draw.line([(0, y), (w, y)], fill=color, width=1)

def draw_neon_glow(img, x, y, radius, color):
    """在指定位置绘制霓虹辉光"""
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    for r in range(radius, 0, -2):
        alpha = int(15 * (1 - r / radius))
        c = (*color[:3], alpha)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=c)
    # 合成
    img_rgba = img.convert("RGBA")
    result = Image.alpha_composite(img_rgba, glow)
    return result.convert("RGB")

def draw_text_with_glow(draw, text, x, y, font, fill, glow_color=None, glow_radius=2):
    """绘制带辉光的文字"""
    if glow_color:
        # 描边作为辉光
        for ox in range(-glow_radius, glow_radius+1):
            for oy in range(-glow_radius, glow_radius+1):
                if ox*ox + oy*oy <= glow_radius*glow_radius:
                    draw.text((x+ox, y+oy), text, font=font, fill=glow_color)
    draw.text((x, y), text, font=font, fill=fill)


# ── 竖屏封面 (9:16) ──────────────────────────────────

def create_vertical_cover(title, ep_num, date_str, output_path):
    W, H = 1080, 1920
    P = Palette

    # 1. 渐变背景
    img = gradient_bg_fast(W, H, P.BG_TOP, P.BG_BOTTOM)
    draw = ImageDraw.Draw(img)

    # 2. 扫描线（极淡）
    scan_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    scan_draw = ImageDraw.Draw(scan_overlay)
    draw_scan_lines(scan_draw, W, H, (0, 200, 255, 8), gap=3)
    img = Image.alpha_composite(img.convert("RGBA"), scan_overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 3. 电路线条
    circuit_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    circuit_draw = ImageDraw.Draw(circuit_overlay)
    draw_circuit_lines(circuit_draw, W, H, (*P.NEON_BLUE, 25), count=18)
    img = Image.alpha_composite(img.convert("RGBA"), circuit_overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 4. 六边形网格（装饰）
    hex_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hex_draw = ImageDraw.Draw(hex_overlay)
    for cx in range(80, W, 160):
        for cy in range(120, H, 180):
            offset_x = 80 if (cy // 180) % 2 else 0
            draw_hexagon(hex_draw, cx + offset_x, cy, 50, (*P.NEON_BLUE, 12), width=1)
    img = Image.alpha_composite(img.convert("RGBA"), hex_overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 5. 粒子
    particle_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    particle_draw = ImageDraw.Draw(particle_overlay)
    draw_particles(particle_draw, W, H, P.NEON_BLUE, count=50)
    img = Image.alpha_composite(img.convert("RGBA"), particle_overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 6. 霓虹辉光点
    img = draw_neon_glow(img, 540, 400, 200, P.NEON_BLUE)
    img = draw_neon_glow(img, 200, 1200, 120, P.NEON_PURPLE)
    img = draw_neon_glow(img, 880, 1500, 100, P.NEON_BLUE)
    draw = ImageDraw.Draw(img)

    # 7. 顶部品牌区
    # 品牌名
    brand_font = find_font(CN_FONTS, 56)
    draw_text_with_glow(draw, BRAND, 60, 100, brand_font, P.WHITE,
                        glow_color=P.NEON_BLUE, glow_radius=3)

    # 品牌下划线
    brand_bbox = draw.textbbox((60, 100), BRAND, font=brand_font)
    line_x1 = 60
    line_x2 = brand_bbox[2] + 20
    line_y = brand_bbox[3] + 15
    draw.line([(line_x1, line_y), (line_x2, line_y)], fill=P.NEON_BLUE, width=3)

    # 标语
    tagline_font = find_font(CN_FONTS, 24)
    draw.text((60, line_y + 12), TAGLINE, font=tagline_font, fill=P.GREY_LIGHT)

    # 8. 集号徽标（右上角）
    ep_font = find_font(EN_FONTS, 36)
    ep_text = f"EP.{ep_num:02d}"
    ep_bbox = draw.textbbox((0, 0), ep_text, font=ep_font)
    ep_w = ep_bbox[2] - ep_bbox[0] + 40
    ep_h = ep_bbox[3] - ep_bbox[1] + 20
    ep_x = W - ep_w - 50
    ep_y = 110
    # 徽标背景
    draw.rounded_rectangle(
        [ep_x, ep_y, ep_x + ep_w, ep_y + ep_h],
        radius=8, fill=(*P.NEON_BLUE, 180) if len(P.NEON_BLUE) == 3 else P.NEON_BLUE,
        outline=P.NEON_BLUE, width=2
    )
    draw.text((ep_x + 20, ep_y + 8), ep_text, font=ep_font, fill=P.BG_TOP)

    # 9. 主标题区（居中偏上）
    # 自动换行
    title_font = find_font(CN_FONTS, 72)
    max_chars_per_line = 8
    lines = []
    remaining = title
    while remaining:
        if len(remaining) <= max_chars_per_line:
            lines.append(remaining)
            break
        lines.append(remaining[:max_chars_per_line])
        remaining = remaining[max_chars_per_line:]

    # 计算总高度
    line_height = 90
    total_text_h = len(lines) * line_height
    start_y = 550 - total_text_h // 2  # 垂直居中偏上

    for i, line in enumerate(lines):
        ly = start_y + i * line_height
        draw_text_with_glow(draw, line, 60, ly, title_font, P.WHITE,
                           glow_color=(*P.NEON_BLUE, 60), glow_radius=4)

    # 标题下方装饰线
    dec_y = start_y + len(lines) * line_height + 20
    draw.line([(60, dec_y), (260, dec_y)], fill=P.NEON_BLUE, width=4)
    draw.line([(270, dec_y), (360, dec_y)], fill=P.NEON_PURPLE, width=4)
    draw.ellipse([370, dec_y-4, 378, dec_y+4], fill=P.NEON_BLUE)

    # 10. 底部信息区
    bottom_y = H - 160
    # 日期
    date_font = find_font(EN_FONTS, 28)
    draw.text((60, bottom_y), date_str, font=date_font, fill=P.GREY_DIM)

    # 底部分割线
    draw.line([(60, bottom_y - 15), (W - 60, bottom_y - 15)],
              fill=(*P.GREY_DIM, 60) if len(P.GREY_DIM) == 4 else P.GREY_DIM, width=1)

    # 底部品牌标记
    brand_small_font = find_font(CN_FONTS, 22)
    brand_mark = f"© {BRAND} | AI TECH DAILY"
    draw.text((60, bottom_y + 40), brand_mark, font=brand_small_font, fill=P.GREY_DIM)

    # 11. 右下角装饰小六边形
    for i, (sz, off) in enumerate([(30, 0), (20, 50), (15, 85)]):
        draw_hexagon(draw, W - 100 + off - 30, H - 250 + i * 45,
                    sz, P.NEON_BLUE, width=1)

    # 保存
    img.save(output_path, quality=95)
    print(f"✅ 竖屏封面: {output_path} ({img.size[0]}x{img.size[1]})")
    return output_path


# ── 横屏封面 (16:9) ──────────────────────────────────

def create_horizontal_cover(title, ep_num, date_str, output_path):
    W, H = 1920, 1080
    P = Palette

    # 1. 渐变背景
    img = gradient_bg_fast(W, H, P.BG_TOP, P.BG_BOTTOM)
    draw = ImageDraw.Draw(img)

    # 2. 扫描线
    scan_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    scan_draw = ImageDraw.Draw(scan_overlay)
    draw_scan_lines(scan_draw, W, H, (0, 200, 255, 6), gap=3)
    img = Image.alpha_composite(img.convert("RGBA"), scan_overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 3. 电路线条
    circuit_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    circuit_draw = ImageDraw.Draw(circuit_overlay)
    draw_circuit_lines(circuit_draw, W, H, (*P.NEON_BLUE, 20), count=15)
    img = Image.alpha_composite(img.convert("RGBA"), circuit_overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 4. 六边形网格
    hex_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hex_draw = ImageDraw.Draw(hex_overlay)
    for cx in range(100, W, 160):
        for cy in range(100, H, 160):
            offset_x = 80 if (cy // 160) % 2 else 0
            draw_hexagon(hex_draw, cx + offset_x, cy, 45, (*P.NEON_BLUE, 10), width=1)
    img = Image.alpha_composite(img.convert("RGBA"), hex_overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 5. 粒子
    particle_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    particle_draw = ImageDraw.Draw(particle_overlay)
    draw_particles(particle_draw, W, H, P.NEON_BLUE, count=40)
    img = Image.alpha_composite(img.convert("RGBA"), particle_overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 6. 霓虹辉光
    img = draw_neon_glow(img, 500, 540, 250, P.NEON_BLUE)
    img = draw_neon_glow(img, 1600, 300, 150, P.NEON_PURPLE)
    draw = ImageDraw.Draw(img)

    # 7. 左侧品牌区
    brand_font = find_font(CN_FONTS, 48)
    draw_text_with_glow(draw, BRAND, 80, 60, brand_font, P.WHITE,
                        glow_color=P.NEON_BLUE, glow_radius=3)

    brand_bbox = draw.textbbox((80, 60), BRAND, font=brand_font)
    line_y = brand_bbox[3] + 10
    draw.line([(80, line_y), (brand_bbox[2] + 15, line_y)], fill=P.NEON_BLUE, width=3)

    tagline_font = find_font(CN_FONTS, 20)
    draw.text((80, line_y + 8), TAGLINE, font=tagline_font, fill=P.GREY_LIGHT)

    # 集号
    ep_font = find_font(EN_FONTS, 30)
    ep_text = f"EP.{ep_num:02d}"
    ep_bbox = draw.textbbox((0, 0), ep_text, font=ep_font)
    ep_w = ep_bbox[2] - ep_bbox[0] + 30
    ep_h = ep_bbox[3] - ep_bbox[1] + 16
    ep_x = brand_bbox[2] + 40
    ep_y = 72
    draw.rounded_rectangle(
        [ep_x, ep_y, ep_x + ep_w, ep_y + ep_h],
        radius=6, fill=P.NEON_BLUE, outline=P.NEON_BLUE, width=2
    )
    draw.text((ep_x + 15, ep_y + 6), ep_text, font=ep_font, fill=P.BG_TOP)

    # 8. 主标题（居中）
    title_font = find_font(CN_FONTS, 80)
    max_chars_per_line = 12
    lines = []
    remaining = title
    while remaining:
        if len(remaining) <= max_chars_per_line:
            lines.append(remaining)
            break
        lines.append(remaining[:max_chars_per_line])
        remaining = remaining[max_chars_per_line:]

    line_height = 100
    total_text_h = len(lines) * line_height
    start_y = (H - total_text_h) // 2

    for i, line in enumerate(lines):
        ly = start_y + i * line_height
        # 居中
        bbox = draw.textbbox((0, 0), line, font=title_font)
        lw = bbox[2] - bbox[0]
        lx = (W - lw) // 2
        draw_text_with_glow(draw, line, lx, ly, title_font, P.WHITE,
                           glow_color=(*P.NEON_BLUE, 60), glow_radius=4)

    # 标题下方装饰线
    dec_y = start_y + len(lines) * line_height + 20
    line_w = 300
    lx_start = (W - line_w) // 2
    draw.line([(lx_start, dec_y), (lx_start + line_w * 2 // 3, dec_y)], fill=P.NEON_BLUE, width=4)
    draw.line([(lx_start + line_w * 2 // 3 + 10, dec_y), (lx_start + line_w, dec_y)], fill=P.NEON_PURPLE, width=4)
    draw.ellipse([lx_start + line_w + 10, dec_y-4, lx_start + line_w + 18, dec_y+4], fill=P.NEON_BLUE)

    # 9. 底部信息
    bottom_y = H - 80
    date_font = find_font(EN_FONTS, 22)
    draw.text((80, bottom_y), date_str, font=date_font, fill=P.GREY_DIM)

    brand_small_font = find_font(CN_FONTS, 18)
    draw.text((80, bottom_y + 30), f"© {BRAND} | AI TECH DAILY", font=brand_small_font, fill=P.GREY_DIM)

    # 右下角装饰
    for i, (sz, off) in enumerate([(25, 0), (18, 40), (12, 70)]):
        draw_hexagon(draw, W - 80 + off - 25, H - 180 + i * 40,
                    sz, P.NEON_BLUE, width=1)

    img.save(output_path, quality=95)
    print(f"✅ 横屏封面: {output_path} ({img.size[0]}x{img.size[1]})")
    return output_path


# ── 主入口 ────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AI前沿视频封面生成器")
    parser.add_argument("--title", required=True, help="视频标题")
    parser.add_argument("--ep", type=int, default=1, help="集号")
    parser.add_argument("--date", default=None, help="日期 (默认今天)")
    parser.add_argument("--output-dir", default=".", help="输出目录")
    args = parser.parse_args()

    if args.date is None:
        from datetime import date
        args.date = date.today().strftime("%Y.%m.%d")

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 竖屏
    v_path = out_dir / f"cover_{args.ep:02d}_vertical.png"
    create_vertical_cover(args.title, args.ep, args.date, str(v_path))

    # 横屏
    h_path = out_dir / f"cover_{args.ep:02d}_horizontal.png"
    create_horizontal_cover(args.title, args.ep, args.date, str(h_path))

    print(f"\n📁 输出目录: {out_dir}")
    print(f"   竖屏: {v_path.name}")
    print(f"   横屏: {h_path.name}")


if __name__ == "__main__":
    main()
