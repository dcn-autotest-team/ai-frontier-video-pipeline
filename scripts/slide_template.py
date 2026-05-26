#!/usr/bin/env python3
"""
AI前沿 - 视频分镜图片模板生成器
品牌：AI前沿 | 风格：暗夜科技蓝 | 输出：竖屏(1080x1920)

与 cover_template.py 保持完全一致的视觉语言。
支持多种幻灯片类型，后续只需更换文字即可。

用法：
  # 单张标题卡
  python slide_template.py --title "Cerebras推理比GPU快15-20倍" --type title --ep 01 --slide 2

  # 批量生成（JSON配置文件）
  python slide_template.py --config slides_config.json --ep 01

  # 快速批量（逗号分隔标题）
  python slide_template.py --titles "开场,Cerebras推理比GPU快15-20倍,200亿美元OpenAI大单,AWS合作,结尾" --ep 01
"""

import argparse
import json
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ── 品牌设定（与封面一致） ─────────────────────────────
BRAND = "AI前沿"
TAGLINE = "第一时间 · 深度解读"

# ── 配色（与封面一致） ─────────────────────────────────
class Palette:
    BG_TOP       = (8, 12, 38)
    BG_BOTTOM    = (22, 8, 56)
    NEON_BLUE    = (0, 212, 255)
    NEON_PURPLE  = (139, 92, 246)
    WHITE        = (255, 255, 255)
    GREY_LIGHT   = (180, 190, 210)
    GREY_DIM     = (80, 90, 110)
    CARD_BG      = (12, 18, 55)       # 卡片背景色
    CARD_BORDER  = (0, 180, 240, 80)  # 卡片边框

# ── 字体（与封面一致） ─────────────────────────────────
FONT_DIR = Path(r"C:\Windows\Fonts")

def find_font(candidates, size):
    for name in candidates:
        path = FONT_DIR / name
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()

CN_FONTS = ["NotoSansSC-VF.ttf", "msyh.ttc", "simhei.ttf", "STXIHEI.TTF"]
EN_FONTS = ["NotoSansSC-VF.ttf", "msyh.ttc", "consola.ttf", "arial.ttf"]

# ── 绘图工具（与封面一致） ─────────────────────────────

def gradient_bg_fast(w, h, top_color, bottom_color):
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
    points = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        x = cx + size * math.cos(angle)
        y = cy + size * math.sin(angle)
        points.append((x, y))
    draw.polygon(points, outline=outline_color, width=width)

def draw_circuit_lines(draw, w, h, color, seed=42, count=12):
    random.seed(seed)
    for _ in range(count):
        x1 = random.randint(0, w)
        y1 = random.randint(0, h)
        direction = random.choice(['h', 'v'])
        length = random.randint(40, 200)
        if direction == 'h':
            x2, y2 = x1 + length, y1
        else:
            x2, y2 = x1, y1 + length
        draw.line([(x1, y1), (x2, y2)], fill=color, width=1)
        draw.ellipse([x1-2, y1-2, x1+2, y1+2], fill=color)
        if random.random() > 0.5:
            if direction == 'h':
                draw.line([(x2, y2), (x2, y2 + random.randint(20, 60))], fill=color, width=1)
            else:
                draw.line([(x2, y2), (x2 + random.randint(20, 60), y2)], fill=color, width=1)

def draw_particles(draw, w, h, color, seed=88, count=40):
    random.seed(seed)
    for _ in range(count):
        x = random.randint(0, w)
        y = random.randint(0, h)
        size = random.randint(1, 3)
        alpha = random.randint(30, 120)
        c = (*color[:3], alpha) if len(color) == 4 else (*color, alpha)
        draw.ellipse([x-size, y-size, x+size, y+size], fill=c)

def draw_scan_lines(draw, w, h, color, gap=4):
    for y in range(0, h, gap):
        draw.line([(0, y), (w, y)], fill=color, width=1)

def draw_neon_glow(img, x, y, radius, color):
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    for r in range(radius, 0, -2):
        alpha = int(15 * (1 - r / radius))
        c = (*color[:3], alpha)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=c)
    img_rgba = img.convert("RGBA")
    result = Image.alpha_composite(img_rgba, glow)
    return result.convert("RGB")

def draw_text_with_glow(draw, text, x, y, font, fill, glow_color=None, glow_radius=2):
    if glow_color:
        for ox in range(-glow_radius, glow_radius+1):
            for oy in range(-glow_radius, glow_radius+1):
                if ox*ox + oy*oy <= glow_radius*glow_radius:
                    draw.text((x+ox, y+oy), text, font=font, fill=glow_color)
    draw.text((x, y), text, font=font, fill=fill)


# ── 公共背景层（与封面完全一致） ──────────────────────

def create_base_background(W, H, variant_seed=0):
    """生成与封面完全一致的暗夜科技蓝背景
    variant_seed: 不同幻灯片使用不同seed让装饰位置有微小变化
    """
    P = Palette

    # 1. 渐变背景
    img = gradient_bg_fast(W, H, P.BG_TOP, P.BG_BOTTOM)
    draw = ImageDraw.Draw(img)

    # 2. 扫描线
    scan_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    scan_draw = ImageDraw.Draw(scan_overlay)
    draw_scan_lines(scan_draw, W, H, (0, 200, 255, 8), gap=3)
    img = Image.alpha_composite(img.convert("RGBA"), scan_overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 3. 电路线条
    circuit_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    circuit_draw = ImageDraw.Draw(circuit_overlay)
    draw_circuit_lines(circuit_draw, W, H, (*P.NEON_BLUE, 25), seed=42 + variant_seed, count=18)
    img = Image.alpha_composite(img.convert("RGBA"), circuit_overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 4. 六边形网格
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
    draw_particles(particle_draw, W, H, P.NEON_BLUE, seed=88 + variant_seed, count=50)
    img = Image.alpha_composite(img.convert("RGBA"), particle_overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 6. 霓虹辉光点（位置随variant偏移）
    glow_positions = [
        (540, 400, 200, P.NEON_BLUE),
        (200, 1200, 120, P.NEON_PURPLE),
        (880, 1500, 100, P.NEON_BLUE),
    ]
    for gx, gy, gr, gc in glow_positions:
        img = draw_neon_glow(img, gx + variant_seed * 30, gy, gr, gc)

    return img


# ── 顶部品牌条（统一） ────────────────────────────────

def draw_brand_bar(draw, W, ep_num, slide_num):
    """顶部品牌条：品牌名 + 下划线 + EP集号 + 幻灯片序号"""
    P = Palette

    # 品牌名
    brand_font = find_font(CN_FONTS, 36)
    draw_text_with_glow(draw, BRAND, 50, 60, brand_font, P.WHITE,
                        glow_color=P.NEON_BLUE, glow_radius=2)

    # 品牌下划线
    brand_bbox = draw.textbbox((50, 60), BRAND, font=brand_font)
    line_y = brand_bbox[3] + 10
    draw.line([(50, line_y), (brand_bbox[2] + 15, line_y)], fill=P.NEON_BLUE, width=2)

    # 标语
    tagline_font = find_font(CN_FONTS, 18)
    draw.text((50, line_y + 8), TAGLINE, font=tagline_font, fill=P.GREY_LIGHT)

    # 右上角：EP集号 + 幻灯片序号
    ep_font = find_font(EN_FONTS, 24)
    ep_text = f"EP.{ep_num:02d}"
    slide_text = f"/{slide_num:02d}" if slide_num else ""
    ep_full = f"{ep_text}{slide_text}"
    ep_bbox = draw.textbbox((0, 0), ep_full, font=ep_font)
    ep_w = ep_bbox[2] - ep_bbox[0] + 30
    ep_h = ep_bbox[3] - ep_bbox[1] + 14
    ep_x = W - ep_w - 40
    ep_y = 68
    draw.rounded_rectangle(
        [ep_x, ep_y, ep_x + ep_w, ep_y + ep_h],
        radius=6, fill=P.NEON_BLUE, outline=P.NEON_BLUE, width=2
    )
    draw.text((ep_x + 15, ep_y + 5), ep_full, font=ep_font, fill=P.BG_TOP)


# ── 底部信息条（统一） ────────────────────────────────

def draw_bottom_bar(draw, W, H, date_str):
    """底部信息条：分割线 + 日期 + 品牌标记"""
    P = Palette
    bottom_y = H - 120

    # 分割线
    draw.line([(50, bottom_y), (W - 50, bottom_y)], fill=P.GREY_DIM, width=1)

    # 日期
    date_font = find_font(EN_FONTS, 22)
    draw.text((50, bottom_y + 15), date_str, font=date_font, fill=P.GREY_DIM)

    # 品牌标记
    brand_small_font = find_font(CN_FONTS, 18)
    draw.text((50, bottom_y + 45), f"© {BRAND} | AI TECH DAILY",
              font=brand_small_font, fill=P.GREY_DIM)

    # 右下角装饰小六边形
    for i, (sz, off) in enumerate([(22, 0), (15, 35), (10, 60)]):
        draw_hexagon(draw, W - 80 + off - 22, H - 200 + i * 35, sz, P.NEON_BLUE, width=1)


# ══════════════════════════════════════════════════════
# 幻灯片类型
# ══════════════════════════════════════════════════════

def wrap_text(text, max_chars):
    """自动换行"""
    lines = []
    remaining = text
    while remaining:
        if len(remaining) <= max_chars:
            lines.append(remaining)
            break
        lines.append(remaining[:max_chars])
        remaining = remaining[max_chars:]
    return lines


# ── 1. 标题卡（开场/大标题） ──────────────────────────

def create_title_slide(title, subtitle, ep_num, slide_num, date_str, output_path, variant=0):
    W, H = 1080, 1920
    P = Palette

    img = create_base_background(W, H, variant)
    draw = ImageDraw.Draw(img)

    # 顶部品牌条
    draw_brand_bar(draw, W, ep_num, slide_num)

    # 主标题（居中偏上，大字）
    title_font = find_font(CN_FONTS, 68)
    lines = wrap_text(title, 9)
    line_height = 85
    total_text_h = len(lines) * line_height
    start_y = 600 - total_text_h // 2

    for i, line in enumerate(lines):
        ly = start_y + i * line_height
        # 居中
        bbox = draw.textbbox((0, 0), line, font=title_font)
        lw = bbox[2] - bbox[0]
        lx = (W - lw) // 2
        draw_text_with_glow(draw, line, lx, ly, title_font, P.WHITE,
                           glow_color=(*P.NEON_BLUE, 50), glow_radius=4)

    # 标题下方装饰线
    dec_y = start_y + len(lines) * line_height + 25
    line_w = 280
    lx_start = (W - line_w) // 2
    draw.line([(lx_start, dec_y), (lx_start + line_w * 2 // 3, dec_y)], fill=P.NEON_BLUE, width=4)
    draw.line([(lx_start + line_w * 2 // 3 + 8, dec_y), (lx_start + line_w, dec_y)], fill=P.NEON_PURPLE, width=4)
    draw.ellipse([lx_start + line_w + 8, dec_y-4, lx_start + line_w + 16, dec_y+4], fill=P.NEON_BLUE)

    # 副标题
    if subtitle:
        sub_font = find_font(CN_FONTS, 32)
        sub_lines = wrap_text(subtitle, 14)
        sub_start_y = dec_y + 40
        for i, line in enumerate(sub_lines):
            bbox = draw.textbbox((0, 0), line, font=sub_font)
            lw = bbox[2] - bbox[0]
            lx = (W - lw) // 2
            draw.text((lx, sub_start_y + i * 45), line, font=sub_font, fill=P.GREY_LIGHT)

    # 底部信息条
    draw_bottom_bar(draw, W, H, date_str)

    img.save(output_path, quality=95)
    print(f"  ✅ 标题卡: {Path(output_path).name}")
    return output_path


# ── 2. 要点卡（关键信息点） ──────────────────────────

def create_point_slide(title, points, ep_num, slide_num, date_str, output_path, variant=0):
    W, H = 1080, 1920
    P = Palette

    img = create_base_background(W, H, variant)
    draw = ImageDraw.Draw(img)

    # 顶部品牌条
    draw_brand_bar(draw, W, ep_num, slide_num)

    # 主标题（较小，偏上）
    title_font = find_font(CN_FONTS, 52)
    lines = wrap_text(title, 10)
    title_start_y = 280
    for i, line in enumerate(lines):
        draw_text_with_glow(draw, line, 60, title_start_y + i * 65, title_font, P.WHITE,
                           glow_color=(*P.NEON_BLUE, 40), glow_radius=3)

    # 标题下方装饰线
    dec_y = title_start_y + len(lines) * 65 + 15
    draw.line([(60, dec_y), (260, dec_y)], fill=P.NEON_BLUE, width=3)
    draw.line([(270, dec_y), (360, dec_y)], fill=P.NEON_PURPLE, width=3)

    # 要点列表
    if points:
        point_font = find_font(CN_FONTS, 36)
        point_y = dec_y + 50
        for i, pt in enumerate(points[:5]):  # 最多5个要点
            # 霓虹蓝色圆点
            dot_x = 70
            dot_y = point_y + 16
            draw.ellipse([dot_x, dot_y, dot_x + 14, dot_y + 14], fill=P.NEON_BLUE)

            # 要点文字（自动换行）
            pt_lines = wrap_text(pt, 14)
            for j, pl in enumerate(pt_lines):
                draw.text((95, point_y + j * 48), pl, font=point_font, fill=P.WHITE)
            point_y += len(pt_lines) * 48 + 30

    # 底部信息条
    draw_bottom_bar(draw, W, H, date_str)

    img.save(output_path, quality=95)
    print(f"  ✅ 要点卡: {Path(output_path).name}")
    return output_path


# ── 3. 数据卡（数据亮点） ────────────────────────────

def create_data_slide(title, data_items, ep_num, slide_num, date_str, output_path, variant=0):
    """data_items: list of {"value": "15-20x", "label": "推理速度提升"}"""
    W, H = 1080, 1920
    P = Palette

    img = create_base_background(W, H, variant)
    draw = ImageDraw.Draw(img)

    # 顶部品牌条
    draw_brand_bar(draw, W, ep_num, slide_num)

    # 主标题
    title_font = find_font(CN_FONTS, 48)
    lines = wrap_text(title, 10)
    title_start_y = 280
    for i, line in enumerate(lines):
        draw_text_with_glow(draw, line, 60, title_start_y + i * 60, title_font, P.WHITE,
                           glow_color=(*P.NEON_BLUE, 40), glow_radius=3)

    dec_y = title_start_y + len(lines) * 60 + 15
    draw.line([(60, dec_y), (260, dec_y)], fill=P.NEON_BLUE, width=3)

    # 数据卡片
    if data_items:
        card_start_y = dec_y + 50
        card_h = 200
        card_gap = 30
        card_margin = 50
        card_w = W - card_margin * 2

        for i, item in enumerate(data_items[:4]):  # 最多4张卡片
            cy = card_start_y + i * (card_h + card_gap)

            # 卡片背景（半透明）
            card_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            card_draw = ImageDraw.Draw(card_overlay)
            card_draw.rounded_rectangle(
                [card_margin, cy, card_margin + card_w, cy + card_h],
                radius=16, fill=(*P.CARD_BG, 200),
                outline=P.NEON_BLUE, width=2
            )
            img = Image.alpha_composite(img.convert("RGBA"), card_overlay).convert("RGB")
            draw = ImageDraw.Draw(img)

            # 数据值（大号，霓虹蓝）
            val_font = find_font(EN_FONTS, 64)
            val_text = item.get("value", "")
            val_bbox = draw.textbbox((0, 0), val_text, font=val_font)
            val_w = val_bbox[2] - val_bbox[0]
            draw_text_with_glow(draw, val_text, card_margin + 40, cy + 30,
                               val_font, P.NEON_BLUE,
                               glow_color=(*P.NEON_BLUE, 40), glow_radius=3)

            # 数据标签
            label_font = find_font(CN_FONTS, 28)
            label_text = item.get("label", "")
            draw.text((card_margin + 40, cy + 110), label_text, font=label_font, fill=P.GREY_LIGHT)

            # 右侧装饰竖线
            draw.line([(card_margin + card_w - 8, cy + 20), (card_margin + card_w - 8, cy + card_h - 20)],
                     fill=P.NEON_BLUE, width=3)

    # 底部信息条
    draw_bottom_bar(draw, W, H, date_str)

    img.save(output_path, quality=95)
    print(f"  ✅ 数据卡: {Path(output_path).name}")
    return output_path


# ── 4. 引言卡（人物语录/金句） ──────────────────────

def create_quote_slide(quote, author, ep_num, slide_num, date_str, output_path, variant=0):
    W, H = 1080, 1920
    P = Palette

    img = create_base_background(W, H, variant)
    draw = ImageDraw.Draw(img)

    # 顶部品牌条
    draw_brand_bar(draw, W, ep_num, slide_num)

    # 大号引号装饰
    quote_mark_font = find_font(EN_FONTS, 140)
    draw.text((60, 450), "\u201C", font=quote_mark_font, fill=(*P.NEON_BLUE, 80))

    # 引言文字
    quote_font = find_font(CN_FONTS, 46)
    lines = wrap_text(quote, 12)
    quote_start_y = 580
    for i, line in enumerate(lines):
        draw_text_with_glow(draw, line, 80, quote_start_y + i * 60, quote_font, P.WHITE,
                           glow_color=(*P.NEON_BLUE, 30), glow_radius=2)

    # 引言下方装饰线
    dec_y = quote_start_y + len(lines) * 60 + 30
    draw.line([(80, dec_y), (300, dec_y)], fill=P.NEON_BLUE, width=3)

    # 作者
    if author:
        author_font = find_font(CN_FONTS, 30)
        draw.text((80, dec_y + 20), f"— {author}", font=author_font, fill=P.NEON_BLUE)

    # 底部信息条
    draw_bottom_bar(draw, W, H, date_str)

    img.save(output_path, quality=95)
    print(f"  ✅ 引言卡: {Path(output_path).name}")
    return output_path


# ── 5. 结尾卡 ──────────────────────────────────────

def create_outro_slide(ep_num, slide_num, date_str, output_path, variant=0):
    W, H = 1080, 1920
    P = Palette

    img = create_base_background(W, H, variant)
    draw = ImageDraw.Draw(img)

    # 顶部品牌条
    draw_brand_bar(draw, W, ep_num, slide_num)

    # 中央大品牌名
    brand_big_font = find_font(CN_FONTS, 80)
    bbox = draw.textbbox((0, 0), BRAND, font=brand_big_font)
    bw = bbox[2] - bbox[0]
    bx = (W - bw) // 2
    draw_text_with_glow(draw, BRAND, bx, 650, brand_big_font, P.WHITE,
                        glow_color=P.NEON_BLUE, glow_radius=5)

    # 品牌下划线
    brand_y = 650 + bbox[3] - bbox[1] + 15
    line_w = bw + 40
    lx = (W - line_w) // 2
    draw.line([(lx, brand_y), (lx + line_w * 2 // 3, brand_y)], fill=P.NEON_BLUE, width=4)
    draw.line([(lx + line_w * 2 // 3 + 8, brand_y), (lx + line_w, brand_y)], fill=P.NEON_PURPLE, width=4)
    draw.ellipse([lx + line_w + 8, brand_y-5, lx + line_w + 18, brand_y+5], fill=P.NEON_BLUE)

    # 标语
    tagline_font = find_font(CN_FONTS, 32)
    tag_bbox = draw.textbbox((0, 0), TAGLINE, font=tagline_font)
    tag_w = tag_bbox[2] - tag_bbox[0]
    draw.text(((W - tag_w) // 2, brand_y + 30), TAGLINE, font=tagline_font, fill=P.GREY_LIGHT)

    # "关注" 提示
    follow_font = find_font(CN_FONTS, 28)
    follow_text = "关注 AI前沿 · 每日科技解读不迷路"
    fol_bbox = draw.textbbox((0, 0), follow_text, font=follow_font)
    fol_w = fol_bbox[2] - fol_bbox[0]
    draw.text(((W - fol_w) // 2, brand_y + 100), follow_text, font=follow_font, fill=P.NEON_BLUE)

    # 底部信息条
    draw_bottom_bar(draw, W, H, date_str)

    img.save(output_path, quality=95)
    print(f"  ✅ 结尾卡: {Path(output_path).name}")
    return output_path


# ══════════════════════════════════════════════════════
# 批量生成入口
# ══════════════════════════════════════════════════════

def generate_slides_from_config(config, ep_num, date_str, output_dir):
    """从JSON配置批量生成幻灯片

    config格式:
    {
      "slides": [
        {"type": "title", "title": "xxx", "subtitle": "xxx"},
        {"type": "point", "title": "xxx", "points": ["p1", "p2"]},
        {"type": "data", "title": "xxx", "data_items": [{"value": "15x", "label": "速度"}]},
        {"type": "quote", "quote": "xxx", "author": "xxx"},
        {"type": "outro"}
      ]
    }
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    slides = config.get("slides", [])
    total = len(slides)
    paths = []

    for i, slide_cfg in enumerate(slides):
        slide_type = slide_cfg.get("type", "title")
        num = i + 1
        path = str(output_dir / f"slide_{num:02d}_{slide_type}.png")

        if slide_type == "title":
            create_title_slide(
                title=slide_cfg.get("title", ""),
                subtitle=slide_cfg.get("subtitle", ""),
                ep_num=ep_num, slide_num=num, date_str=date_str,
                output_path=path, variant=i
            )
        elif slide_type == "point":
            create_point_slide(
                title=slide_cfg.get("title", ""),
                points=slide_cfg.get("points", []),
                ep_num=ep_num, slide_num=num, date_str=date_str,
                output_path=path, variant=i
            )
        elif slide_type == "data":
            create_data_slide(
                title=slide_cfg.get("title", ""),
                data_items=slide_cfg.get("data_items", []),
                ep_num=ep_num, slide_num=num, date_str=date_str,
                output_path=path, variant=i
            )
        elif slide_type == "quote":
            create_quote_slide(
                quote=slide_cfg.get("quote", ""),
                author=slide_cfg.get("author", ""),
                ep_num=ep_num, slide_num=num, date_str=date_str,
                output_path=path, variant=i
            )
        elif slide_type == "outro":
            create_outro_slide(
                ep_num=ep_num, slide_num=num, date_str=date_str,
                output_path=path, variant=i
            )
        paths.append(path)

    return paths


def generate_quick_slides(titles, ep_num, date_str, output_dir):
    """快速模式：逗号分隔标题，自动判断类型"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    total = len(titles)

    for i, title in enumerate(titles):
        num = i + 1
        path = str(output_dir / f"slide_{num:02d}.png")

        if i == 0:
            # 第一张默认为标题卡
            create_title_slide(title=title, subtitle="", ep_num=ep_num,
                             slide_num=num, date_str=date_str,
                             output_path=path, variant=i)
        elif i == total - 1:
            # 最后一张默认为结尾卡
            create_outro_slide(ep_num=ep_num, slide_num=num,
                             date_str=date_str, output_path=path, variant=i)
        else:
            # 中间默认为要点卡
            create_point_slide(title=title, points=[],
                             ep_num=ep_num, slide_num=num,
                             date_str=date_str, output_path=path, variant=i)
        paths.append(path)

    return paths


# ── 命令行入口 ──────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AI前沿视频分镜图片生成器")
    parser.add_argument("--ep", type=int, default=1, help="集号")
    parser.add_argument("--date", default=None, help="日期 (默认今天)")
    parser.add_argument("--output-dir", default="./slides", help="输出目录")

    # 三种输入方式（互斥）
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--config", help="JSON配置文件路径")
    group.add_argument("--titles", help="逗号分隔的标题列表（快速模式）")
    group.add_argument("--title", help="单张标题（需配合 --type 使用）")

    parser.add_argument("--type", choices=["title", "point", "data", "quote", "outro"],
                       default="title", help="幻灯片类型（单张模式）")
    parser.add_argument("--subtitle", default="", help="副标题（标题卡）")
    parser.add_argument("--points", help="要点列表，逗号分隔（要点卡）")
    parser.add_argument("--slide", type=int, default=1, help="幻灯片序号（单张模式）")

    args = parser.parse_args()

    if args.date is None:
        from datetime import date
        args.date = date.today().strftime("%Y.%m.%d")

    if args.config:
        # JSON配置模式
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        paths = generate_slides_from_config(config, args.ep, args.date, args.output_dir)
        print(f"\n📁 共生成 {len(paths)} 张分镜图 → {args.output_dir}")

    elif args.titles:
        # 快速批量模式
        title_list = [t.strip() for t in args.titles.split(",") if t.strip()]
        paths = generate_quick_slides(title_list, args.ep, args.date, args.output_dir)
        print(f"\n📁 共生成 {len(paths)} 张分镜图 → {args.output_dir}")

    elif args.title:
        # 单张模式
        out_dir = Path(args.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        path = str(out_dir / f"slide_{args.slide:02d}_{args.type}.png")

        if args.type == "title":
            create_title_slide(args.title, args.subtitle, args.ep, args.slide,
                             args.date, path)
        elif args.type == "point":
            pts = [p.strip() for p in args.points.split(",")] if args.points else []
            create_point_slide(args.title, pts, args.ep, args.slide,
                             args.date, path)
        elif args.type == "data":
            create_data_slide(args.title, [], args.ep, args.slide,
                            args.date, path)
        elif args.type == "quote":
            create_quote_slide(args.title, "", args.ep, args.slide,
                             args.date, path)
        elif args.type == "outro":
            create_outro_slide(args.ep, args.slide, args.date, path)

        print(f"\n📁 单张输出: {path}")


if __name__ == "__main__":
    main()
