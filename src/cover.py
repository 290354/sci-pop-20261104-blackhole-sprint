import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E
from PIL import ImageFilter
img = E.render_at(20).filter(ImageFilter.GaussianBlur(3))
base = E.Image.new("RGB", (E.W, E.H), E.BG)
img = E.Image.blend(img, base, 0.60)
d = E.ImageDraw.Draw(img, "RGBA")
E.starfield(img, 0, n=90, bright=0.35)
E.tw_c(d=d, x=640, y=118, s="科普爆点动画周刊", font=E.F("sansb", 26), fill=E.BLUE, a=1.0)
E.tw_c(d=d, x=640, y=160, s="第 03 期 · 2026.11.04", font=E.F("sans", 20), fill=E.DIM, a=1.0)
E.tw_c(d=d, x=640, y=280, s="四十倍", font=E.F("serifb", 150), fill=E.INK, a=1.0)
d.line([(490, 366), (790, 366)], fill=E.col_a(E.RED, 1.0), width=4)
E.tw_c(d=d, x=640, y=412, s="一个黑洞吃得太快，快过了物理上限", font=E.F("sans", 34), fill=E.INK, a=0.95)
E.tw_c(d=d, x=640, y=470, s="LID-568 · 韦布望远镜 · 爱丁顿极限", font=E.F("sans", 24), fill=E.BLUE, a=0.9)
E.tw_c(d=d, x=640, y=640, s="1280×720 · 30fps · 5:03", font=E.F("sans", 18), fill=E.DIM, a=0.8)
img.save("cover.png")
print("cover ok")
