# 科普爆点动画周刊 · 第 3 期：四十倍

> **40× 爱丁顿极限：一个黑洞的吃相，为什么快过了物理上限**
> 韦布望远镜拍到 LID-568：它所在的时代，宇宙才 15 亿岁；它的进食速度，却被推算出是理论极限的 40 倍。
> 一个被光"撑开"的盘，会把规则推开一条旁路——这就是本期要讲的事。

- **成片**：[`video/episode.mp4`](video/episode.mp4)（1280×720 / 30fps / 4 分 59 秒 / 含解说音轨与配乐）
- **字幕**：[`video/episode.srt`](video/episode.srt)（79 条，随片交付；画面内也已烧录字幕）
- **封面**：[`cover.png`](cover.png)（1280×720）
- **脚本**：[`script.md`](script.md)｜**选题**：[`选题.md`](选题.md)

## 本期规格

| 项 | 值 |
|---|---|
| 分辨率 | 1280×720（横屏 16:9） |
| 帧率 | 30 fps（9066 帧） |
| 时长 | 302.21 秒（5:02.2，含 3.4 秒片尾卡） |
| 音轨 | AAC 立体声 44.1kHz：中文解说（edge-tts `zh-CN-YunxiNeural`，语速 −4%）＋ 合成深空氛围垫（−26 dB 量级，压在解说之下） |
| 字幕 | 分段字幕，每段对应一个分镜，单条 ≤ 26 字 |

## 制作路线：B —— HTML/Canvas 同类"逐帧渲染"

**为什么不是 A（Manim）**：本期是天文 × 物理机制 × 尺度对比，画面几乎全是连续量——吸积盘旋臂、粒子外流、水位上涨、指数增长曲线、弓形激波横移。这类画面的关键是"每一帧都能被 t 精确决定"，用逐帧渲染比 Manim 的矢量对象动画更省时；同时全片中文密度高，避免 LaTeX / TeX Live 依赖，符合"宁可降配置，不可交半成品"。

**实现**（`src/`）：

- `engine.py` —— 纯 PIL 渲染引擎，暴露确定性接口 `render_at(t)`（t 秒 → 1280×720 帧），全部图形由 `smoothstep / ease-out` 驱动，无随机时钟；星野与粒子用固定 seed 的伪随机数，保证同 t 必得同帧。
- `render.py` —— 6 进程并行逐帧输出 `frames/f%06d.jpg`（9066 帧，约 90 秒渲完）。
- `gen_segs.py` / `tts.py` / `mksubs.py` —— 解说词 → edge-tts 分段合成 → `ffprobe` 取实际时长 → 生成 `timeline.json`（每段起点/时长）与 `subs.json`、`video/episode.srt`。
- `bgm.py` —— 用 `aevalsrc` 合成 6 个分音的低频 drone + 长延时回声，作为氛围床，混音时压到解说之下 20 dB 以上。
- `cover.py` —— 取 20 秒处画面虚化后叠字生成封面。
- 合成：`ffmpeg -framerate 30 -i frames/f%06d.jpg` → H.264（本机 ffmpeg 无 libx264，改用同质量的 `libopenh264`）→ yuv420p。

**视觉规范**：背景 `#0E1116`、正文 `#ECE6D9`，主色仅三色 `#58C4DD` / `#F4D345` / `#FC6255`；中文 Noto Serif/Sans CJK SC；所有文字绘制前用 `textlength` 校验宽度，长句自动缩字号，字幕区（y ≥ 620）不被画面文字占用。

**风格参考**：整体取 `code-animation-prompts` 中 M1（"先看见、再命名"）与 B3（粒子聚形）的提示词思路——先让粒子把"光压顶住气体"演出来，再出现"爱丁顿极限"这个词；分镜节奏参考 `fy-code-animation` 的 modules/recipes 组织方式，只取规范不套依赖。

## 配音档位：L1（edge-tts）

- 音色：`zh-CN-YunxiNeural`（男声，数字与术语清楚，句尾不塌）。
- 41 段分镜逐段合成，语速 `-4%`，段间 0.5s 停顿（结论句由 UI 内 0.5–1.2s 的 `hold` 拉长）。
- 判定：分段试听后未出现断句错误或明显机械感，**未降级到 L2/L3**。
- 配乐为程序合成的氛围床，不是人工作曲；要求"AI 配乐"时本节为可选的降级替代（见 L3 策略）。

## 选题来源（全部为真实可访问链接）

| 来源 | 链接 |
|---|---|
| 中国青年网（LID-568 报道） | https://www.cnyouth.com/706e778c82.html |
| 科学网 · 《自然》大脑"大扫除"（备选选题） | https://news.sciencenet.cn/htmlnews/2026/11/574113.shtm |
| 今日头条 · 逃逸黑洞 1 号（对照案例） | https://www.toutiao.com/article/7703911222689481256/ |
| 科技日报 · 纳赫兹引力波（备选选题） | https://www.stdaily.com/web/gdxw/2026-11/03/content_607656.html |

## 事实与边界

- 40 倍是**由外流速度与外流尺度反推的瞬时吸积率**，不是长期平均；正片第三章已明确"它撑不了多久"。
- "外流带走角动量与部分辐射压力 → 上限被抬高"是当前超爱丁顿吸积模型的主流解释，正片称之为"绕过规则"而非"打破规则"。
- 逃逸黑洞 954 km/s / 20 万光年尾迹为 2026 年 7 月的引力波反冲重建结果，用作"黑洞可长期处于非平衡态"的对照，不代表与 LID-568 直接相关。
- 中文科普媒体在 2026 年 11 月初集中转载该研究；正片只陈述"韦布望远镜观测到"，不把转载日当作首发日。

## 复现

```bash
pip3 install pillow edge-tts
python3.11 src/gen_segs.py        # 生成解说词分段
python3.11 src/tts.py             # 合成 + 拼接 + 生成 timeline.json
python3.11 src/mksubs.py          # 生成 subs.json 与 video/episode.srt
python3.11 src/bgm.py             # 合成配乐
python3.11 src/render.py frames   # 逐帧渲染（约 9066 帧）
python3.11 src/cover.py
ffmpeg -framerate 30 -i frames/f%06d.jpg -i audio/voice.m4a -i audio/bgm.m4a \
  -filter_complex "[1:a]volume=1.6,apad[v];[2:a]volume=0.010,apad[b];[v][b]amix=inputs=2:duration=longest,alimiter=limit=0.95[a]" \
  -map 0:v -map "[a]" -c:v libopenh264 -b:v 2400k -pix_fmt yuv420p -r 30 -c:a aac -b:a 160k -t 302.21 video/episode.mp4
```

> 若你的 ffmpeg 带 libx264，把 `-c:v libopenh264 -b:v 2400k` 换成 `-c:v libx264 -crf 21 -preset medium` 即可，画质略优、体积更小。

## 目录

```
README.md            本期说明
选题.md              候选表、打分与选定理由
script.md            分镜表（41 镜，含时间码）
cover.png            封面 1280×720
src/engine.py        逐帧渲染引擎（render_at(t)）
src/render.py        并行渲染
src/gen_segs.py      解说词
src/tts.py           配音流水线
src/mksubs.py        SRT 生成
src/bgm.py           配乐合成
src/cover.py         封面
src/timeline.json    每段起始/时长（由音频实测得出）
audio/voice.m4a      解说（后期可直接复用）
audio/bgm.m4a        配乐
video/episode.mp4    成片
video/episode.srt    字幕
```

## 返修记录（2026-11-06）

初版成片 4:58.8，但**片尾卡整段没有进画面**。根因有两处，都已修：

1. `engine.py` 里 `TOTAL` 写死为 `303.3`，而 `timeline.json` 实际只到 `298.81`；
2. 合成命令用了 `-shortest`，音频一结束就切视频，最后 4.5 秒被丢掉。

现在 `TOTAL = 最后一段解说结束 + TAIL(3.4s)`，由时间轴推导；合成改用 `apad` 把音轨补到画面长度，不再用 `-shortest`。
同时修了 `render_at()` 里 `PLAN[idx]` 取不到 `"end"` 的问题——`PLAN` 只有 41 项，索引最大 40，片尾卡函数 `sc_end` 从来没被调用过，所以即使补时长也只会停在最后一句问话上。

成片：302.21 秒（5:02.2），末帧为「四十倍 / 不是打破物理，是我们把吸积盘想得太干净了 / 更会卸力，而不是更用力」。
