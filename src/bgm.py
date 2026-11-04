"""生成低音氛围垫 + 章节起伏（无外部素材，全部合成），混入解说。"""
import subprocess, json, math

DUR = json.load(open("src/timeline.json"))
TOTAL = DUR[-1]["start"] + DUR[-1]["dur"] + 3.0

# 三个频段的正弦叠加 + 缓慢 LFO，模拟深空氛围垫
src = []
notes = [(55, 0.30), (82.4, 0.22), (110, 0.16), (164.8, 0.10), (220, 0.06), (329.6, 0.04)]
for i, (f, a) in enumerate(notes):
    lfo = 0.06 + 0.04 * i
    src.append(f"{(a):.3f}*sin(2*PI*{f}*t)*(0.65+0.35*sin(2*PI*{lfo:.3f}*t))")
expr = "+".join(src)
filt = f"aevalsrc='({expr})*0.9':s=44100:d={TOTAL:.2f}"
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", filt,
                "-af", "lowpass=f=900,aecho=0.8:0.9:60|120:0.25|0.15,volume=0.5",
                "-ac", "2", "audio/bgm.wav"], check=True)
print("bgm", TOTAL)
