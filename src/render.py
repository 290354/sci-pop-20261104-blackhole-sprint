import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import engine
from multiprocessing import Pool

OUT = sys.argv[1] if len(sys.argv) > 1 else "frames"

def job(i):
    engine.render_at(i / engine.FR).save(os.path.join(OUT, "f%06d.jpg" % i), quality=86)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    total = int(round(engine.TOTAL * engine.FR))
    with Pool(6) as p:
        for k, _ in enumerate(p.imap_unordered(job, range(total), chunksize=60)):
            if k and k % 1500 == 0:
                print(f"{k}/{total}", flush=True)
    print("done", total)
