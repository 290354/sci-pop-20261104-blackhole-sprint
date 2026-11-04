# -*- coding: utf-8 -*-
"""科普爆点动画周刊 第 3 期 —— 40 倍极限：LID-568 黑洞的暴食
纯 PIL 逐帧渲染引擎（确定性 renderAt(t) 语义：t 秒 -> 1280x720 帧）。
3b1b 配色：底 #0E1116 / 正文 #ECE6D9 / 主色 #58C4DD #F4D345 #FC6255
"""
import json, math, random, os
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
BG = (14, 17, 22)
INK = (236, 230, 217)
DIM = (110, 116, 126)
BLUE = (88, 196, 221)
YEL = (244, 211, 69)
RED = (252, 98, 85)
FR = 30

SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"
SERIFB = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
SANS = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
SANSB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"

_fc = {}
def F(kind, size):
    key = (kind, int(size))
    if key not in _fc:
        path = {"serif": SERIF, "serifb": SERIFB, "sans": SANS, "sansb": SANSB}[kind]
        _fc[key] = ImageFont.truetype(path, int(size), index=2)
    return _fc[key]

def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x

def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)

def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3

def lerp(a, b, u):
    return a + (b - a) * u

def mixc(c1, c2, u):
    u = clamp(u)
    return tuple(int(lerp(c1[k], c2[k], u)) for k in range(3))

def col_a(c, a):
    return (c[0], c[1], c[2], int(255 * clamp(a)))

def tw(d, xy, s, font, fill, anchor="la"):
    if not isinstance(xy, (tuple, list)):
        raise TypeError("xy must be tuple")
    if not isinstance(fill, tuple):
        fill = (fill, fill, fill)
    xy = (round(xy[0]), round(xy[1]))
    if len(fill) == 3:
        d.text(xy, s, font=font, fill=fill, anchor=anchor)
        return
    d.text((xy[0] + 2, xy[1] + 2), s, font=font, fill=(0, 0, 0, int(fill[3] * 0.55)), anchor=anchor)
    d.text(xy, s, font=font, fill=fill, anchor=anchor)

def tw_c(d, x, y, s, font, fill, a=1.0):
    if a <= 0.005:
        return
    c = col_a(fill, a)
    d.text((x + 2, y + 2), s, font=font, fill=(0, 0, 0, int(c[3] * 0.55)), anchor="mm")
    d.text((x, y), s, font=font, fill=c, anchor="mm")

def fit(d, s, kind_b, kind, maxw, maxsize, minsize=14):
    """按 maxw 自动缩字号，返回 font"""
    size = maxsize
    while size > minsize:
        f = F(kind_b, size)
        if d.textlength(s, font=f) <= maxw:
            return f
        size -= 2
    return F(kind, minsize)

# ---------------- 时间轴 ----------------
TL = json.load(open(os.path.join(os.path.dirname(__file__), "timeline.json")))
SUBS = json.load(open(os.path.join(os.path.dirname(__file__), "subs.json")))
TOTAL = float(os.environ.get("EP_TOTAL", "303.3"))

CHAP = [
    (0.0, "冷开场"),
    (25.0, "第一章 · 为什么它还能吃"),
    (70.0, "第二章 · 溢出的盘"),
    (140.0, "第三章 · 尺度与对照"),
    (210.0, "第四章 · 它什么时候不成立"),
    (270.0, "回到那个数字"),
]

def chapter_at(t):
    lab = CHAP[0][1]
    for t0, name in CHAP:
        if t >= t0:
            lab = name
    return lab

def typ(i):
    """时间段，返回段内进度 u"""
    s = TL[i]
    return s["start"], s["dur"], s["hold"]

# ---------------- 底层绘制工具 ----------------
def vgrad(img, top, bot):
    d = ImageDraw.Draw(img)
    for y in range(H):
        d.line([(0, y), (W, y)], fill=mixc(top, bot, y / H))

def starfield(img, t, n=170, seed=7, bright=1.0, drift=1.0):
    rnd = random.Random(seed)
    d = ImageDraw.Draw(img, "RGBA")
    for k in range(n):
        x0 = rnd.random() * W
        y0 = rnd.random() * H
        r = rnd.choice([0.6, 0.8, 1.0, 1.0, 1.4, 1.9])
        ph = rnd.random() * 6.28
        sp = 0.6 + rnd.random() * 1.8
        a = (0.20 + 0.55 * (0.5 + 0.5 * math.sin(t * sp + ph))) * bright
        x = (x0 + t * 3.0 * drift) % W
        d.ellipse([x - r, y0 - r, x + r, y0 + r], fill=(236, 230, 217, int(255 * a)))

def nebula(img, t, cx, cy, rad, color, a=0.12, seed=3):
    rnd = random.Random(seed)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for k in range(26):
        ang = rnd.random() * 6.28
        rr = rad * (0.3 + rnd.random() * 0.7)
        x = cx + math.cos(ang) * rr * 0.9
        y = cy + math.sin(ang) * rr * 0.45
        s = rad * (0.25 + rnd.random() * 0.45) * (1 + 0.05 * math.sin(t * 0.6 + k))
        d.ellipse([x - s, y - s * 0.7, x + s, y + s * 0.7], fill=col_a(color, a * (0.4 + 0.6 * rnd.random())))
    ov = ov.filter(__import__("PIL.ImageFilter", fromlist=["x"]).GaussianBlur(rad * 0.22))
    img.alpha_composite(ov) if img.mode == "RGBA" else img.paste(ov, (0, 0), ov)

def glow_dot(img, x, y, r, color, a=1.0, layers=3):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for k in range(layers):
        rr = r * (2.6 - k * 0.7)
        aa = a * (0.10 + 0.16 * k)
        d.ellipse([x - rr, y - rr * 0.72, x + rr, y + rr * 0.72], fill=col_a(color, aa))
    d.ellipse([x - r, y - r * 0.72, x + r, y + r * 0.72], fill=col_a(color, a))
    img.paste(ov, (0, 0), ov)

def arrow(d, x1, y1, x2, y2, color, w=2, head=7, a=1.0):
    c = col_a(color, a)
    d.line([(x1, y1), (x2, y2)], fill=c, width=w)
    ang = math.atan2(y2 - y1, x2 - x1)
    for s in (-1, 1):
        ang2 = ang + math.pi - s * 0.42
        d.line([(x2, y2), (x2 + head * math.cos(ang2), y2 + head * math.sin(ang2))], fill=c, width=w)

def dashed_ellipse(d, cx, cy, rx, ry, color, a=0.5, n=64, dash=2, w=1):
    for k in range(0, n, dash * 2):
        p0 = k / n * 2 * math.pi
        p1 = (k + dash) / n * 2 * math.pi
        pts = []
        for p in (p0, p1):
            pts.append((cx + rx * math.cos(p), cy + ry * math.sin(p)))
        d.line(pts, fill=col_a(color, a), width=w)

# ---------------- 场景 ----------------
def sc_title(img, d, t, u):
    starfield(img, t, n=200, bright=0.8 + 0.2 * math.sin(t))
    a1 = smooth((u - 0.05) / 0.40)
    a2 = smooth((u - 0.42) / 0.35)
    tw_c(d, W / 2, 300, "科普爆点动画周刊", F("sansb", 22), BLUE, a1 * 0.9)
    tw_c(d, W / 2, 336, "第 03 期", F("sans", 18), DIM, a1)
    f = F("serifb", 128)
    n = 168
    tw(d=d, xy=((W - n) / 2, 372), s="四十倍", font=f, fill=col_a(INK, a1))
    # 红色下划线从中间张开
    wl = ease_out((u - 0.45) / 0.35) * 300
    d.line([(W / 2 - wl / 2, 520), (W / 2 + wl / 2, 520)], fill=col_a(RED, a1), width=4)
    tw_c(d, W / 2, 570, "一个黑洞的吃相，为什么超越了物理上限", F("sans", 30), INK, a2 * 0.92)

def frame_blackhole(img, d, cx, cy, r, t, disk=1.0, spin=1.0, ring=True, color=YEL, rays=0.0):
    # 吸积盘（椭圆环带）
    if disk > 0:
        for k in range(9):
            rr0 = r * (1.25 + k * 0.22)
            ry = rr0 * 0.22
            aa = (0.55 - k * 0.05) * disk
            d.ellipse([cx - rr0, cy - ry, cx + rr0, cy + ry], outline=col_a(mixc(color, (255, 255, 255), k * 0.08), aa), width=2)
        # 旋臂粒子
        for k in range(70):
            ph = k * 0.37 + t * 0.9 * spin
            rr = r * (1.3 + (k % 23) * 0.11)
            ang = ph + (k % 7) * 0.2
            y = math.sin(ang)
            x = math.cos(ang)
            depth = 0.5 + 0.5 * math.cos(ang)
            aa = disk * (0.25 + 0.65 * depth)
            px, py = cx + rr * x, cy + rr * 0.22 * y
            d.ellipse([px - 1.6, py - 1.6, px + 1.6, py + 1.6], fill=col_a(mixc(color, INK, 0.35), aa))
    # 视界
    d.ellipse([cx - r, cy - r * 0.72, cx + r, cy + r * 0.72], fill=(4, 5, 7))
    if ring:
        d.ellipse([cx - r, cy - r * 0.72, cx + r, cy + r * 0.72], outline=col_a(color, 0.92), width=3)
        d.ellipse([cx - r * 1.04, cy - r * 0.76, cx + r * 1.04, cy + r * 0.76], outline=col_a(color, 0.22), width=2)

def sc_cold1(img, d, t, u):
    vgrad(img, (24, 14, 18), (9, 10, 14))
    starfield(img, t, n=120, bright=0.5)
    k = ease_out((u - 0.1) / 0.7)
    tw_c(d, W / 2, 250, "40 ×", F("serifb", int(lerp(50, 190, k))), mixc(INK, RED, k), smooth((u - 0.05) / 0.3))
    tw_c(d, W / 2, 470, "吸积速度 / 爱丁顿极限", F("sans", 34), INK, smooth((u - 0.55) / 0.3))
    # 刻度条
    a = smooth((u - 0.7) / 0.3)
    if a > 0:
        x0, x1, y = 390, 890, 545
        d.line([(x0, y), (x1, y)], fill=col_a(DIM, a), width=2)
        xm = x0 + (x1 - x0) * 0.16
        d.line([(xm, y - 9), (xm, y + 9)], fill=col_a(INK, a), width=2)
        tw_c(d, xm, y + 26, "极限 1×", F("sans", 18), DIM, a)
        xp = lerp(xm, x1 + 40, ease_out((u - 0.72) / 0.25))
        d.line([(xm, y), (xp, y)], fill=col_a(RED, a), width=4)

def sc_cold2(img, d, t, u):
    vgrad(img, (18, 14, 16), (8, 9, 12))
    starfield(img, t, n=150, bright=0.6)
    cx, cy = 420, 380
    a = smooth((u - 0.05) / 0.5)
    nebula(img, t, cx, cy, 300, RED, 0.10 * a)
    r = 58 * ease_out((u - 0.08) / 0.35)
    frame_blackhole(img, d, cx, cy, max(r, 1), t, disk=a)
    tw_c(d, cx, cy + 130, "LID-568", F("serifb", 40), INK, smooth((u - 0.3) / 0.3))
    # 红移 1.4 / 15 亿年
    a2 = smooth((u - 0.42) / 0.3)
    tw_c(d, 900, 320, "红移 z ≈ 1.4", F("sans", 30), BLUE, a2)
    tw_c(d, 900, 372, "宇宙只有 15 亿岁时", F("sans", 30), INK, a2 * 0.9)
    a3 = smooth((u - 0.62) / 0.25)
    tw_c(d, 900, 440, "已重 1,000 万倍太阳质量", F("sans", 26), DIM, a3)

def sc_number(img, d, t, u):
    vgrad(img, (16, 14, 16), (8, 9, 12))
    starfield(img, t, n=110, bright=0.45)
    k = ease_out(u / 0.6)
    tw_c(d, W / 2, 290, "一顿", F("serifb", 104), INK, smooth(u / 0.25))
    tw_c(d, W / 2, 420, "吃出整个体重", F("serifb", 72), RED, smooth((u - 0.2) / 0.3))
    # 体重饼图：一顿占 80%
    a = smooth((u - 0.5) / 0.3)
    if a > 0:
        cx, cy, r = W / 2, 600, 0.1
        px = lerp(W / 2, W / 2, k)
        bw = 420
        d.rounded_rectangle([W / 2 - bw / 2, 585, W / 2 + bw / 2, 610], radius=12, outline=col_a(DIM, a), width=1)
        d.rounded_rectangle([W / 2 - bw / 2, 585, W / 2 - bw / 2 + bw * 0.8 * ease_out((u - 0.6) / 0.35), 610], radius=12, fill=col_a(RED, a))
        tw_c(d, W / 2 - bw / 2, 640, "现有质量的大部分来自一次进食", F("sans", 20), DIM, a)

def sc_nonsense(img, d, t, u):
    vgrad(img, (14, 16, 22), (8, 9, 12))
    rnd = random.Random(11)
    # 背景细微噪点
    for k in range(60):
        x = rnd.random() * W; y = rnd.random() * H
        d.point((x, y), fill=col_a(INK, 0.05))
    jit = math.sin(t * 22) * 3 * (1 - clamp(u / 0.5))
    a = smooth(u / 0.25)
    tw_c(d, W / 2 + jit, H / 2 - 6, "这说不通", F("serifb", 120), INK, a)
    a2 = smooth((u - 0.35) / 0.3)
    if a2 > 0:
        tw_c(d, W / 2, H / 2 + 110, "光越亮 → 推得越狠 → 就吃得更慢", F("sans", 30), DIM, a2)

def sc_edington1(img, d, t, u):
    vgrad(img, (14, 16, 22), (8, 9, 12))
    starfield(img, t, n=70, bright=0.3)
    # 左侧：气体团被推住
    cx, cy = 640, 340
    r = 70
    a = smooth(u / 0.3)
    # 气体团粒子
    rnd = random.Random(5)
    for k in range(48):
        ang = rnd.random() * 6.28
        rr = 120 + rnd.random() * 80
        x = cx + math.cos(ang) * rr
        y = cy + math.sin(ang) * rr * 0.6 - 60 * ease_out((u - 0.1) / 0.6)
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=col_a(BLUE, a * 0.7))
    frame_blackhole(img, d, cx, cy, r, t, disk=a * 0.8)
    tw_c(d, cx, cy + 130, "黑洞", F("sans", 22), DIM, a)
    # 箭头：向内引力 vs 向外光压
    aa = smooth((u - 0.3) / 0.25)
    if aa > 0:
        for sgn in (-1, 1):
            x1 = cx + sgn * 240
            y1 = cy + 40
            arrow(d, x1, y1, cx + sgn * (r + 30), y1, YEL, 3, 9, aa)
            tw_c(d, x1 + sgn * 34, y1 - 22, "引力", F("sans", 20), YEL, aa)
            arrow(d, cx + sgn * (r + 20), cy + 30, cx + sgn * (r + 20 + 130), cy + 30, RED, 3, 9, aa)
            tw_c(d, cx + sgn * (r + 20 + 150), cy + 30, "光压", F("sans", 20), RED, aa)

def sc_edington2(img, d, t, u):
    vgrad(img, (14, 16, 22), (8, 9, 12))
    a = smooth(u / 0.3)
    # 天平：引力 vs 光压
    cx, cy = 640, 470
    d.line([(cx, cy), (cx, cy - 210)], fill=col_a(INK, a), width=4)
    tilt = lerp(-0.0, 0.16, ease_out((u - 0.2) / 0.5))
    L = 260
    x1 = cx - L * math.cos(tilt); y1 = cy - 210 - L * math.sin(tilt)
    x2 = cx + L * math.cos(tilt); y2 = cy - 210 + L * math.sin(tilt)
    d.line([(x1, y1), (x2, y2)], fill=col_a(INK, a), width=4)
    tw_c(d, x1, y1 - 34, "引力", F("sans", 24), YEL, a)
    tw_c(d, x2, y2 - 34, "光压", F("sans", 24), RED, a)
    d.line([(cx - 70, cy), (cx + 70, cy)], fill=col_a(INK, a), width=3)
    a2 = smooth((u - 0.4) / 0.3)
    tw_c(d, W / 2, 590, "两者打平的那一点 = 爱丁顿极限", F("serifb", 40), YEL, a2)
    a3 = smooth((u - 0.65) / 0.25)
    tw_c(d, W / 2, 650, "超过它，气体就停在门外", F("sans", 24), DIM, a3)

def sc_mechanism_intro(img, d, t, u):
    vgrad(img, (16, 16, 20), (8, 9, 12))
    starfield(img, t, n=90, bright=0.4)
    a = smooth(u / 0.25)
    tw_c(d, W / 2, 200, "教科书里的黑洞", F("sans", 24), DIM, a)
    cx, cy = W / 2, 420
    # 薄盘：一层一层喂
    for k in range(6):
        prog = ease_out((u - 0.1 - k * 0.08) / 0.4)
        if prog <= 0:
            continue
        rr = 280 - k * 34
        d.ellipse([cx - rr * prog, cy - rr * prog * 0.24, cx + rr * prog, cy + rr * prog * 0.24],
                  outline=col_a(mixc(BLUE, YEL, k / 6), 0.35 + 0.08 * k), width=2)
    frame_blackhole(img, d, cx, cy, 40, t, disk=0.6)
    a2 = smooth((u - 0.45) / 0.3)
    tw_c(d, W / 2, 560, "薄盘模型：规规矩矩，一层一层往里喂", F("sans", 28), INK, a2)

def sc_not_thin(img, d, t, u):
    vgrad(img, (18, 14, 16), (8, 9, 12))
    a = smooth(u / 0.25)
    cx, cy = W / 2, 380
    # 薄盘（半透明，作为对照）
    d.ellipse([cx - 280, cy - 60, cx + 280, cy + 60], outline=col_a(DIM, a * 0.5), width=1)
    # 鼓起的盘：厚度随时间增大
    hgt = 34 + 90 * ease_out((u - 0.05) / 0.6)
    for k in range(5):
        rr = 260 - k * 46
        d.ellipse([cx - rr, cy - hgt * (1 - k * 0.1), cx + rr, cy + hgt * (1 - k * 0.1)],
                  outline=col_a(YEL, a * (0.2 + 0.12 * k)), width=2)
    frame_blackhole(img, d, cx, cy, 44, t, disk=0.0, ring=True, color=RED)
    # 喂入的料流：从左右两侧被抓进盘
    if u > 0.15:
        for sgn in (-1, 1):
            for k in range(9):
                ph = ((u * 2.2 + k / 9) % 1.0)
                x = cx + sgn * lerp(430, 90, ph)
                y = cy - 20 + 40 * math.sin(ph * 6 + k) * (1 - ph)
                d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=col_at(YEL, a * (1 - ph) * 0.9))
            arrow(d, cx + sgn * 470, cy + 120, cx + sgn * 330, cy + 90, YEL, 2, 8, a * 0.8)
    a2 = smooth((u - 0.5) / 0.3)
    tw_c(d, W / 2, 560, "盘被塞满了 → 鼓起来 → 横截面像一只胖气球", F("sans", 26), INK, a2)

def sc_outflow(img, d, t, u):
    vgrad(img, (20, 14, 14), (8, 9, 12))
    starfield(img, t, n=140, bright=0.6)
    cx, cy = W / 2, 400
    a = smooth(u / 0.2)
    frame_blackhole(img, d, cx, cy, 62, t, disk=a)
    # 喷流：向外流动的粒子
    rnd = random.Random(21)
    for k in range(90):
        life = ((t * 0.45 + rnd.random()) % 1.0)
        sgn = 1 if k % 2 == 0 else -1
        spread = (rnd.random() - 0.5) * 0.5
        d0 = 90 + life * 520
        x = cx + sgn * d0 * 0.86 + spread * 60
        y = cy - life * 30 + spread * d0 * 0.7
        al = (1 - life) * a * 0.85
        d.ellipse([x - 2.2, y - 2.2, x + 2.2, y + 2.2], fill=col_a(mixc(BLUE, INK, life * 0.5), al))
        if k % 9 == 0:
            d.line([(x - sgn * 26, y + 6), (x, y)], fill=col_a(BLUE, al * 0.5), width=2)
    a2 = smooth((u - 0.35) / 0.3)
    tw_c(d, cx, 640, "气体外流：速度上千公里每秒，尺度上千光年", F("sans", 26), INK, a2)

def sc_overflow(img, d, t, u):
    vgrad(img, (16, 18, 24), (8, 9, 12))
    cx, cy = W / 2, 300
    # 碗
    a = smooth(u / 0.2)
    d.arc([cx - 200, cy - 60, cx + 200, cy + 170], start=0, end=180, fill=col_a(INK, a), width=4)
    level = ease_out((u - 0.05) / 0.55)
    ly = lerp(cy + 150, cy - 40, level)
    for yy in range(int(ly), int(cy) + 166, 2):
        hw = 196 * math.sqrt(max(0.0, 1 - ((yy - (cy + 55)) / 115.0) ** 2))
        d.line([(cx - hw, yy), (cx + hw, yy)], fill=col_a(BLUE, a * 0.16))
    lw = 196 * math.sqrt(max(0.0, 1 - ((ly - (cy + 55)) / 115.0) ** 2))
    d.line([(cx - lw, ly), (cx + lw, ly)], fill=col_a(BLUE, a * 0.9), width=3)
    # 漏水粒子
    if level > 0.85:
        rnd = random.Random(31)
        for k in range(26):
            ph = (t * 0.8 + rnd.random()) % 1
            x = cx + (rnd.random() - 0.5) * 380
            y = cy + 20 + ph * 260
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=col_a(BLUE, (1 - ph) * 0.8))
    a2 = smooth((u - 0.55) / 0.3)
    tw_c(d, cx, 520, "池子满了，多出来的只能从边沿走", F("sans", 28), INK, a2)
    a3 = smooth((u - 0.75) / 0.2)
    tw_c(d, cx, 610, "LID-568 就处在这个状态", F("sans", 22), DIM, a3)

def sc_angmom(img, d, t, u):
    vgrad(img, (16, 18, 24), (8, 9, 12))
    cx, cy = 420, 380
    a = smooth(u / 0.2)
    frame_blackhole(img, d, cx, cy, 50, t, disk=a)
    # 角动量：旋涡箭头
    for k in range(3):
        R = 120 + k * 34
        for j in range(22):
            ang0 = j / 22 * 6.28 + t * 0.8
            ang1 = ang0 + 0.14
            d.arc([cx - R, cy - R * 0.35, cx + R, cy + R * 0.35],
                  math.degrees(ang0), math.degrees(ang0 + 9), fill=col_a(INK, a * 0.7), width=2)
    # 外流带走角动量的箭头
    aa = smooth((u - 0.3) / 0.3)
    arrow(d, cx + 210, cy - 110, cx + 360, cy - 170, BLUE, 3, 10, aa)
    tw_c(d, cx + 430, cy - 190, "带走角动量", F("sans", 22), BLUE, aa)
    tw_c(d, cx + 430, cy - 150, "剩下气体掉得更快", F("sans", 20), DIM, aa)
    # 右侧公式块
    a2 = smooth((u - 0.5) / 0.3)
    if a2 > 0:
        tw(d=d, xy=(760, 250), s="L / r³ 变少", font=F("serifb", 44), fill=col_a(YEL, a2))
        tw(d=d, xy=(760, 320), s="→ 轨道开始收缩", font=F("sans", 26), fill=col_a(INK, a2 * 0.9))
        tw(d=d, xy=(760, 372), s="→ 落得越快", font=F("sans", 26), fill=col_a(INK, a2 * 0.9))
        tw(d=d, xy=(760, 424), s="→ 吃得越快", font=F("sans", 26), fill=col_a(RED, a2))

def sc_relief(img, d, t, u):
    vgrad(img, (16, 16, 22), (8, 9, 12))
    a = smooth(u / 0.2)
    cx, cy = 640, 390
    # 阀门/管路示意：上游 → 分岔
    d.line([(200, cy), (560, cy)], fill=col_a(DIM, a), width=10)
    d.line([(720, cy), (1080, cy)], fill=col_a(DIM, a), width=10)
    open_ = ease_out((u - 0.15) / 0.45)
    # 旁路
    bx = 640
    d.line([(640, cy), (640, cy - 180 * open_)], fill=col_a(BLUE, a * 0.8), width=8)
    d.line([(640, cy - 180 * open_), (1000 - 140 * (1 - open_), cy - 180 * open_)], fill=col_a(BLUE, a * 0.8), width=8)
    # 流动粒子
    rnd = random.Random(41)
    for k in range(30):
        ph = (t * 0.7 + rnd.random()) % 1
        x = 210 + ph * 330
        d.ellipse([x - 3, cy - 3, x + 3, cy + 3], fill=col_a(YEL, a * 0.8))
    tw_c(d, 300, cy - 40, "进料", F("sans", 22), YEL, a)
    tw_c(d, 940, cy - 40, "落入黑洞", F("sans", 22), RED, a)
    a2 = smooth((u - 0.45) / 0.3)
    tw_c(d, 800, cy - 210, "旁路：把光压也带走一部分", F("sans", 22), BLUE, a2)
    a3 = smooth((u - 0.6) / 0.3)
    tw_c(d, W / 2, 600, "压力一松，阀门 = 上限，就跟着抬高", F("sans", 28), INK, a3)

def sc_bypass(img, d, t, u):
    vgrad(img, (14, 16, 22), (8, 9, 12))
    rnd = random.Random(51)
    a = smooth(u / 0.25)
    # 一张"规则墙"，旁边一条绕行的小路
    for k in range(9):
        x = 420 + k * 46
        d.line([(x, 220), (x, 470)], fill=col_a(DIM, a * 0.55), width=2)
    d.line([(400, 220), (860, 220)], fill=col_a(DIM, a * 0.8), width=3)
    d.line([(400, 470), (860, 470)], fill=col_a(DIM, a * 0.8), width=3)
    tw_c(d, 640, 190, "规则：爱丁顿极限", F("sans", 22), DIM, a)
    # 粒子沿曲线绕过
    for k in range(14):
        ph = ((t * 0.28 + k / 14) % 1.0)
        x = lerp(240, 1040, ph)
        y = 345 - 210 * math.sin(ph * math.pi) ** 0.9 * ease_out((u - 0.1) / 0.4)
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=col_a(YEL, a * 0.9))
    a2 = smooth((u - 0.5) / 0.3)
    tw_c(d, W / 2, 560, "它不是撞破了规则，是给规则开了一条旁路", F("serifb", 40), INK, a2)

def sc_scale1(img, d, t, u):
    vgrad(img, (14, 16, 22), (8, 9, 12))
    a = smooth(u / 0.25)
    # 质量增长曲线
    x0, y0, wgt, hgt = 260, 560, 760, 360
    d.line([(x0, y0), (x0 + wgt, y0)], fill=col_a(DIM, a), width=2)
    d.line([(x0, y0), (x0, y0 - hgt)], fill=col_a(DIM, a), width=2)
    prog = ease_out((u - 0.1) / 0.55)
    pts = []
    for k in range(61):
        f = k / 60 * prog
        x = x0 + f * wgt
        y = y0 - (1 - 2 ** (-f * 4.2)) * hgt
        pts.append((x, y))
    if len(pts) > 1:
        d.line(pts, fill=col_a(RED, a), width=4)
        px, py = pts[-1]
        glow_dot(img, px, py, 4, RED, a)
    tw(d=d, xy=(x0 + 10, y0 - hgt - 30), s="质量", font=F("sans", 20), fill=col_at(DIM, a))
    tw(d=d, xy=(x0 + wgt - 90, y0 + 14), s="时间", font=F("sans", 20), fill=col_at(DIM, a))
    a2 = smooth((u - 0.45) / 0.3)
    tw(d=d, xy=(x0 + wgt * 0.42, y0 - hgt * 0.82), s="40× 进食：翻倍只要几百万年", font=F("sans", 26), fill=col_at(INK, a2))
    a3 = smooth((u - 0.65) / 0.25)
    tw(d=d, xy=(x0 + 40, 616), s="同样时间，1× 进食几乎看不出变化（虚线）", font=F("sans", 20), fill=col_at(DIM, a3))
    if a3 > 0:
        pts2 = []
        for k in range(31):
            f = k / 30 * prog
            pts2.append((x0 + f * wgt, y0 - (1 - 2 ** (-f * 0.55)) * hgt))
        d.line(pts2, fill=col_a(DIM, a3 * 0.8), width=2)

def col_at(c, a):
    return col_a(c, a)

def sc_scale2(img, d, t, u):
    vgrad(img, (12, 14, 20), (8, 9, 12))
    starfield(img, t, n=160, bright=0.5)
    a = smooth(u / 0.2)
    # 从左到右：3 km 视界 → 太阳系尺度
    cx, cy = 330, 380
    frame_blackhole(img, d, cx, cy, 12, t, disk=a * 0.8)
    tw_c(d, cx, cy + 90, "视界 ≈ 3 km", F("sans", 22), INK, a)
    tw_c(d, cx, cy + 126, "（1 倍太阳质量）", F("sans", 17), DIM, a)
    # 尺度放大箭头
    aa = smooth((u - 0.25) / 0.3)
    arrow(d, 480, cy, 760, cy, BLUE, 3, 12, aa)
    tw_c(d, 620, cy - 30, "放大", F("sans", 22), BLUE, aa)
    # 太阳系示意
    b = smooth((u - 0.45) / 0.35)
    if b > 0:
        ox = 960
        for k in range(5):
            rr = (40 + k * 34) * b
            d.ellipse([ox - rr, cy - rr * 0.34, ox + rr, cy + rr * 0.34], outline=col_at(DIM, b * 0.55), width=1)
        d.ellipse([ox - 9, cy - 9, ox + 9, cy + 9], fill=col_at(YEL, b))
        d.ellipse([ox + 118 - 5, cy - 5, ox + 118 + 5, cy + 5], fill=col_at(BLUE, b))
        tw_c(d, ox, cy + 150, "吸积盘横跨整个太阳系", F("sans", 22), INK, b)

def sc_scale3(img, d, t, u):
    vgrad(img, (12, 14, 20), (8, 9, 12))
    starfield(img, t, n=120, bright=0.5)
    a = smooth(u / 0.2)
    cx, cy = W / 2, 360
    zoom = 1.0 + 0.6 * ease_out((u - 0.1) / 0.6)
    r = 40 * zoom
    frame_blackhole(img, d, cx, cy, r, t, disk=a, color=mixc(YEL, RED, smooth((u - 0.4) / 0.3)))
    # 距离刻度
    if a > 0:
        d.line([(cx - 260, 600), (cx + 260, 600)], fill=col_at(DIM, a * 0.7), width=1)
        tw_c(d, cx, 626, "10⁶ 倍太阳质量 → 视界直径约 4×10⁶ km ≈ 太阳直径的 3 倍", F("sans", 19), DIM, a)

def sc_escape(img, d, t, u):
    vgrad(img, (12, 14, 20), (8, 9, 12))
    starfield(img, t, n=200, bright=0.6, drift=3 * ease_out((u - 0.1) / 0.7))
    a = smooth(u / 0.2)
    travel = ease_out((u - 0.05) / 0.8) * 500
    hx = 260 + travel
    hy = 420
    # 弓形激波
    if a > 0:
        for k in range(4):
            rr = 60 + k * 22
            d.arc([hx - rr, hy - rr * 0.9, hx + rr, hy + rr * 0.9], 120, 240, fill=col_at(BLUE, a * (0.6 - k * 0.1)), width=2)
    # 尾迹
    tr = 300
    for k in range(1, 7):
        xx = hx - tr * k / 7
        d.line([(xx, hy - 6 * k / 7), (xx, hy + 6 * k / 7)], fill=col_at(mixc(RED, BG, k / 7), a * 0.5), width=2)
    frame_blackhole(img, d, hx, hy, 16, t, disk=a)
    a2 = smooth((u - 0.3) / 0.3)
    tw(d=d, xy=(120, 200), s="954 km/s", font=F("serifb", 60), fill=col_at(INK, a2))
    tw(d=d, xy=(120, 292), s="≈ 每小时 340 万公里", font=F("sans", 24), fill=col_at(BLUE, a2))
    a3 = smooth((u - 0.55) / 0.3)
    tw(d=d, xy=(120, 346), s="身后拖着 20 万光年的恒星尾巴", font=F("sans", 24), fill=col_at(DIM, a3))

def sc_recoil(img, d, t, u):
    vgrad(img, (12, 14, 20), (8, 9, 12))
    starfield(img, t, n=90, bright=0.4)
    cx, cy = 640, 380
    a = smooth(u / 0.2)
    sep = 40 + 80 * ease_out((u - 0.1) / 0.5)
    merge = ease_out((u - 0.55) / 0.35)
    # 两个黑洞绕转后合并
    ang = t * 1.4
    x1 = cx - sep * math.cos(ang); y1 = cy - sep * 0.4 * math.sin(ang)
    x2 = cx + sep * math.cos(ang); y2 = cy + sep * 0.4 * math.sin(ang)
    frame_blackhole(img, d, x1, y1, 26, t, disk=a * 0.6, color=BLUE)
    frame_blackhole(img, d, x2, y2, 26, t, disk=a * 0.6, color=BLUE)
    # 引力波涟漪
    if a > 0:
        for k in range(5):
            rr = (80 + k * 55 + (t * 40) % 55)
            d.ellipse([cx - rr, cy - rr * 0.4, cx + rr, cy + rr * 0.4], outline=col_at(YEL, a * 0.25 * (1 - k / 5)), width=1)
    # 反冲箭头
    aa = smooth((u - 0.5) / 0.3)
    arrow(d, cx - 120, cy + 170, cx - 330, cy + 170, RED, 4, 12, aa)
    tw_c(d, cx - 400, cy + 170, "反冲", F("sans", 22), RED, aa)
    a2 = smooth((u - 0.6) / 0.3)
    tw_c(d, W / 2, 620, "引力波往一边多漏一点，新黑洞就被推向另一边", F("sans", 26), INK, a2)

def sc_balance_break(img, d, t, u):
    vgrad(img, (14, 14, 18), (8, 9, 12))
    a = smooth(u / 0.2)
    cy = 380
    # 平衡点上下的两个状态
    xs = [(380, "安静的平衡态", DIM), (900, "非平衡的暴食态", RED)]
    for k, (x, lab, c) in enumerate(xs):
        aa = smooth((u - 0.1 - k * 0.15) / 0.3)
        d.ellipse([x - 90, cy - 55, x + 90, cy + 55], outline=col_at(c, aa), width=3)
        frame_blackhole(img, d, x, cy, 26, t, disk=aa * 0.7, color=c)
        tw_c(d, x, cy + 110, lab, F("sans", 24), c, aa)
    aa = smooth((u - 0.45) / 0.3)
    # 状态之间的箭头与裂痕
    d.line([(500, cy), (780, cy)], fill=col_at(YEL, aa), width=2)
    for k in range(6):
        xx = 560 + k * 30
        d.line([(xx, cy - 10), (xx + 15, cy + 10)], fill=col_at(YEL, aa), width=2)
    a2 = smooth((u - 0.6) / 0.3)
    tw_c(d, W / 2, 600, "黑洞不总是待在安静的那个点上", F("serifb", 42), INK, a2)

def sc_evidence(outflow_scale=1.0):
    def f(img, d, t, u):
        vgrad(img, (14, 14, 18), (8, 9, 12))
        a = smooth(u / 0.2)
        tw(d=d, xy=(110, 120), s="证据", font=F("sansb", 22), fill=col_at(BLUE, a))
        tw(d=d, xy=(120, 146), s="为什么信这个 40 倍", font=F("serifb", 44), fill=col_at(INK, a))
        rows = [
            ("外流速度 ~ 上千 km/s", "气体被推得比爱丁顿盘允许多得多"),
            ("外流尺度 ~ 上千光年", "一次事件，撑开了整个尺度的气体"),
            ("外流质量 × 时间", "反推出瞬时吸积率 ≈ 40 × 极限"),
            ("单个事件贡献主体质量", "不是长期稳态，是一次性暴食"),
        ]
        for k, (h, s) in enumerate(rows):
            aa = smooth((u - 0.15 - k * 0.13) / 0.25)
            if aa <= 0:
                continue
            y = 250 + k * 92
            d.rectangle([120, y - 8, 124, y + 46], fill=col_at(YEL, aa))
            tw(d=d, xy=(150, y), s=h, font=F("sansb", 28), fill=col_at(INK, aa))
            tw(d=d, xy=(150, y + 40), s=s, font=F("sans", 21), fill=col_at(DIM, aa))
        a2 = smooth((u - 0.7) / 0.25)
        tw_c(d, W / 2, 640, "对照：韦布另一批观测也在早期宇宙看到类似的强外流", F("sans", 20), col_at(DIM, a2))
    return f

def sc_cond1(img, d, t, u):
    vgrad(img, (14, 16, 22), (8, 9, 12))
    starfield(img, t, n=80, bright=0.35)
    a = smooth(u / 0.2)
    cx, cy = 400, 380
    # 冷气体流：从右上角流向中心
    rnd = random.Random(61)
    for k in range(60):
        ph = (t * 0.35 + rnd.random()) % 1
        x = lerp(1100, cx, ph ** 1.3) + (rnd.random() - 0.5) * 120 * (1 - ph)
        y = lerp(160, cy, ph ** 1.3) + (rnd.random() - 0.5) * 90 * (1 - ph)
        d.ellipse([x - 2.2, y - 2.2, x + 2.2, y + 2.2], fill=col_at(BLUE, a * 0.8 * (1 - ph * 0.4)))
    frame_blackhole(img, d, cx, cy, 46, t, disk=a)
    tw(d=d, xy=(720, 260), s="条件一", font=F("sansb", 22), fill=col_at(YEL, a))
    tw(d=d, xy=(720, 300), s="足够多的冷气体", font=F("serifb", 46), fill=col_at(INK, a))
    tw(d=d, xy=(720, 372), s="温度低 → 声速慢 → 落得快", font=F("sans", 24), fill=col_at(DIM, smooth((u - 0.3) / 0.3)))
    tw(d=d, xy=(720, 412), s="流量大 → 盘容不下 → 溢出", font=F("sans", 24), fill=col_at(DIM, smooth((u - 0.45) / 0.3)))

def sc_cond2(img, d, t, u):
    vgrad(img, (10, 12, 18), (8, 9, 12))
    starfield(img, t, n=110, bright=0.4)
    a = smooth(u / 0.2)
    tw(d=d, xy=(120, 120), s="条件二", font=F("sansb", 22), fill=col_at(YEL, a))
    tw(d=d, xy=(120, 160), s="宇宙早期", font=F("serifb", 48), fill=col_at(INK, a))
    # 时间轴：z=6 → z=1.4 → 今天
    y = 420
    d.line([(140, y), (1140, y)], fill=col_at(DIM, a * 0.7), width=2)
    marks = [(260, "宇宙 10 亿岁", "z≈6"), (620, "15 亿岁 · LID-568", "z≈1.4"), (1000, "138 亿岁", "z=0")]
    for k, (x, s1, s2) in enumerate(marks):
        aa = smooth((u - 0.2 - k * 0.12) / 0.25)
        d.line([(x, y - 12), (x, y + 12)], fill=col_at(YEL if k == 1 else INK, aa), width=3)
        tw_c(d, x, y + 48, s1, F("sans", 21), INK if k == 1 else DIM, aa)
        tw_c(d, x, y + 78, s2, F("sans", 17), DIM, aa * 0.9)
    a2 = smooth((u - 0.6) / 0.3)
    tw_c(d, 620, 600, "气体密、金属少、盘没被恒星搅乱 —— 这才喂得出这种吃法", F("sans", 24), INK, a2)

def sc_today(img, d, t, u):
    vgrad(img, (14, 14, 18), (8, 9, 12))
    a = smooth(u / 0.2)
    # 银河系中心：一颗恒星以极快速度掠过（示意）
    cx, cy = 640, 380
    frame_blackhole(img, d, cx, cy, 22, t, disk=a * 0.9, color=BLUE)
    # 恒星轨迹
    for k in range(3):
        R = 200 + k * 60
        d.ellipse([cx - R, cy - R * 0.55, cx + R, cy + R * 0.55], outline=col_at(DIM, a * 0.3), width=1)
    ang = t * 2.2
    sx = cx + 260 * math.cos(ang); sy = cy + 143 * math.sin(ang)
    d.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=col_at(YEL, a))
    a2 = smooth((u - 0.4) / 0.3)
    tw(d=d, xy=(120, 120), s="今天的银河系中心", font=F("sansb", 24), fill=col_at(INK, a2))
    tw(d=d, xy=(120, 164), s="气体稀薄 · 恒星乱飞", font=F("serifb", 40), fill=col_at(RED, a2))
    a3 = smooth((u - 0.6) / 0.25)
    tw(d=d, xy=(120, 520), s="想在这里复刻 40 倍暴食：非常难", font=F("sans", 26), fill=col_at(DIM, a3))

def sc_transient(img, d, t, u):
    vgrad(img, (14, 14, 18), (8, 9, 12))
    a = smooth(u / 0.2)
    # 亮度曲线：尖峰
    x0, y0, wg, hg = 220, 520, 840, 340
    d.line([(x0, y0), (x0 + wg, y0)], fill=col_at(DIM, a), width=2)
    pts = []
    prog = ease_out((u - 0.05) / 0.5)
    for k in range(81):
        f = k / 80
        if f > prog:
            break
        x = x0 + f * wg
        peak = 1.0 if 0.34 < f < 0.46 else 0.0
        y = y0 - hg * (0.10 + (0.85 * math.exp(-((f - 0.40) ** 2) / 0.006)))
        pts.append((x, y))
    if len(pts) > 1:
        d.line(pts, fill=col_at(YEL, a), width=4)
    # 上限线
    d.line([(x0, y0 - hg * 0.32), (x0 + wg, y0 - hg * 0.32)], fill=col_at(RED, a * 0.8), width=2)
    tw(d=d, xy=(x0 + wg - 160, y0 - hg * 0.32 - 30), s="爱丁顿极限", font=F("sans", 20), fill=col_at(RED, a))
    a2 = smooth((u - 0.5) / 0.3)
    tw(d=d, xy=(x0 + 10, y0 - hg - 26), s="瞬时亮度", font=F("sans", 20), fill=col_at(DIM, a2))
    tw(d=d, xy=(x0 + wg * 0.55, y0 - 70), s="只维持很短一段时间", font=F("sans", 22), fill=col_at(INK, a2))

def sc_boundary(img, d, t, u):
    vgrad(img, (14, 14, 18), (8, 9, 12))
    a = smooth(u / 0.2)
    cx, cy = W / 2, 300
    # 火箭助推级示意
    d.polygon([(cx, cy - 150), (cx - 46, cy + 20), (cx + 46, cy + 20)], outline=col_at(INK, a))
    # 火焰
    fk = (1 - ease_out((u - 0.5) / 0.5)) * (1 if u < 0.6 else 0)
    if a > 0:
        for k in range(7):
            rnd = random.Random(k)
            yy = cy + 24 + k * 20 * fk
            hw = (44 - k * 5) * max(fk, 0.2)
            d.line([(cx, yy), (cx - hw, yy + 16 * fk + 4), (cx, yy + 10), (cx + hw, yy + 16 * fk + 4), (cx, yy)],
                   fill=col_at(mixc(YEL, RED, k / 7), a * 0.8 * (0.3 + fk)), width=2)
    tw_c(d=d, x=cx, y=520, s="超速只发生在头几分钟", font=F("serifb", 40), fill=INK, a=smooth((u - 0.2) / 0.3))
    a2 = smooth((u - 0.6) / 0.3)
    tw_c(d, cx, 630, "之后它必须回到极限之内，慢慢地吃", F("sans", 24), DIM, a2)

def sc_model(img, d, t, u):
    vgrad(img, (14, 16, 22), (8, 9, 12))
    a = smooth(u / 0.2)
    # 左：允许失控；右：长期结果对上
    lx, rx, cy = 360, 920, 380
    tw_c(d, lx, 220, "模型假设", F("sans", 22), col_at(DIM, a))
    tw_c(d, rx, 220, "观测结果", F("sans", 22), col_at(DIM, a))
    aa = smooth((u - 0.15) / 0.3)
    d.rounded_rectangle([lx - 150, cy - 70, lx + 150, cy + 70], radius=14, outline=col_at(YEL, aa), width=2)
    tw_c(d, lx, cy, "短期允许超速", F("sansb", 30), YEL, aa)
    bb = smooth((u - 0.4) / 0.3)
    d.rounded_rectangle([rx - 150, cy - 70, rx + 150, cy + 70], radius=14, outline=col_at(BLUE, bb), width=2)
    tw_c(d, rx, cy, "巨型黑洞按时长大", F("sansb", 30), BLUE, bb)
    cc = smooth((u - 0.6) / 0.25)
    arrow(d, lx + 170, cy, rx - 170, cy, INK, 2, 10, cc)
    tw_c(d, W / 2, 560, "不是每口都要守规矩，是总账要对得上", F("serifb", 40), INK, cc)

def sc_question(img, d, t, u):
    vgrad(img, (14, 16, 22), (8, 9, 12))
    starfield(img, t, n=90, bright=0.4)
    a = smooth(u / 0.25)
    # 一堆点：吃出来 vs 并出来
    rnd = random.Random(71)
    for k in range(80):
        x = 300 + rnd.random() * 680
        y = 200 + rnd.random() * 260
        eaten = k < 52
        aa = smooth((u - 0.05 - (k % 20) * 0.01) / 0.3) * a
        c = RED if eaten else BLUE
        rr = 4 if eaten else 6
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=col_at(c, aa))
    tw_c(d, W / 2, 560, "吃出来的 与 并出来的，比例是多少？", F("serifb", 40), INK, smooth((u - 0.4) / 0.3))

def sc_end(img, d, t, u):
    vgrad(img, (14, 16, 22), (8, 9, 12))
    starfield(img, t, n=160, bright=0.5)
    cx, cy = W / 2, 320
    a = smooth(u / 0.25)
    frame_blackhole(img, d, cx, cy, 60, t, disk=a, color=YEL)
    a1 = smooth((u - 0.15) / 0.3)
    tw_c(d, cx, 470, "四十倍", F("serifb", 76), INK, a1)
    a2 = smooth((u - 0.4) / 0.3)
    tw_c(d, cx, 560, "不是打破物理，是我们把吸积盘想得太干净了", F("sans", 28), DIM, a2)
    a3 = smooth((u - 0.62) / 0.3)
    tw_c(d, cx, 610, "更会卸力，而不是更用力", F("sansb", 26), RED, a3)

SCENES = {
    "title": sc_title, "cold1": sc_cold1, "cold2": sc_cold2, "number": sc_number,
    "nonsense": sc_nonsense, "edington1": sc_edington1, "edington2": sc_edington2,
    "mech_intro": sc_mechanism_intro, "not_thin": sc_not_thin, "outflow": sc_outflow,
    "overflow": sc_overflow, "angmom": sc_angmom, "relief": sc_relief, "bypass": sc_bypass,
    "scale1": sc_scale1, "scale2": sc_scale2, "scale3": sc_scale3, "escape": sc_escape,
    "recoil": sc_recoil, "balance_break": sc_balance_break, "evidence": sc_evidence(),
    "cond1": sc_cond1, "cond2": sc_cond2, "today": sc_today, "transient": sc_transient,
    "boundary": sc_boundary, "model": sc_model, "question": sc_question, "end": sc_end,
}
# 每段的画面方案（对应 script.md 分镜）
PLAN = [
    "title", "cold1", "cold2", "number",
    "nonsense", "edington1", "edington1", "edington2",
    "edington2", "balance_break", "mech_intro", "not_thin",
    "outflow", "overflow", "overflow", "angmom",
    "angmom", "relief", "bypass",
    "scale1", "scale3", "scale2", "escape", "escape",
    "recoil", "balance_break",
    "evidence", "evidence", "balance_break",
    "cond1", "cond2", "today",
    "transient", "boundary", "model",
    "end", "end", "end", "end", "end", "question",
]

def render(idx, u):
    t = TL[idx]["start"] + u * (TL[idx]["dur"] + TL[idx]["hold"])
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img, "RGBA")
    key = PLAN[idx] if idx < len(PLAN) else "end"
    SCENES[key](img, d, t, u)
    # 章节小标
    chap = chapter_at(TL[idx]["start"])
    if idx > 0 and TL[idx]["start"] > 2:
        d.text((44, 34), chap, font=F("sans", 17), fill=col_a(DIM, 0.55))
    # 字幕
    render_subs(img, d)
    return img

def wrap_cn(d, s, font, maxw):
    lines, cur = [], ""
    for ch in s:
        if d.textlength(cur + ch, font=font) > maxw and cur:
            lines.append(cur); cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines

SUB_Y = 664
SUB_MAXW = 1120

def render_subs(img, d):
    for x in SUBS:
        if x["s"] - 0.06 <= T_current[0] <= x["e"] + 0.10:
            lines = wrap_cn(d, x["text"], F("sansb", 27), SUB_MAXW)
            n = len(lines)
            y0 = SUB_Y if n == 1 else SUB_Y - 34
            for k, ln in enumerate(lines):
                f = fit(d, ln, "sansb", "sansb", SUB_MAXW, 27)
                d.text((W / 2 + 2, y0 + k * 34 + 2), ln, font=f, fill=(0, 0, 0, 120), anchor="mm")
                d.text((W / 2, y0 + k * 34), ln, font=f, fill=(245, 242, 235), anchor="mm")
            break

T_current = [0.0]

def render_at(t):
    T_current[0] = t
    idx = 0
    for i, s in enumerate(TL):
        if t >= s["start"]:
            idx = i
    s = TL[idx]
    u = clamp((t - s["start"]) / max(s["dur"] + s["hold"], 1e-6))
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img, "RGBA")
    key = PLAN[idx] if idx < len(PLAN) else "end"
    SCENES[key](img, d, t, u)
    chap = chapter_at(s["start"])
    if s["start"] > 2:
        d.text((44, 34), chap, font=F("sans", 17), fill=col_a(DIM, 0.55))
    render_subs(img, d)
    return img
