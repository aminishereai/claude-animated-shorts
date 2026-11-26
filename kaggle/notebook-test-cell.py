# 3Dio GPU test for a Kaggle notebook (T4 + Internet on). Paste into one cell and run.
# Clones the public fork, installs Node + Chrome for Testing, tries GPU modes, renders ~2 s at 1080x1920.
import json, os, subprocess, time

COMP = "BridgeShort"
PROPS = {"w": 1080, "h": 1920}

def sh(cmd):
    print("+", cmd, flush=True)
    subprocess.run(cmd, shell=True, check=True)

sh("nvidia-smi --query-gpu=name,memory.total --format=csv || true")
sh("curl -fsSL https://deb.nodesource.com/setup_22.x | bash - >/dev/null && apt-get install -y nodejs >/dev/null")
sh("apt-get install -y libnss3 libatk-bridge2.0-0 libgbm1 libxkbcommon0 libasound2 libxcomposite1 libxdamage1 libxrandr2 libpango-1.0-0 libcairo2 libvulkan1 libegl1 libgles2 >/dev/null 2>&1 || true")
sh("rm -rf /kaggle/working/cas && git clone -q --depth 1 -b claude/project-thread-nlpbhh https://github.com/aminishereai/claude-animated-shorts /kaggle/working/cas")
os.chdir("/kaggle/working/cas/render")
sh("npm ci --no-audit --no-fund --loglevel=error")
sh("npx remotion browser ensure --chrome-mode=chrome-for-testing")

def run(out, idx, count, gl, timeout):
    env = dict(os.environ, COMP=COMP, GL=gl, CHROME_MODE="chrome-for-testing")
    p = subprocess.run(["node", "scripts/render-chunk.mjs", out, str(idx), str(count), json.dumps(PROPS)],
                       env=env, capture_output=True, text=True, timeout=timeout)
    tail = "\n".join((p.stdout + p.stderr).strip().splitlines()[-4:])
    return p.returncode == 0, tail

results = {}
for gl in ["angle-egl", "vulkan", "angle"]:
    t0 = time.time()
    try:
        ok, tail = run(f"/kaggle/working/test-{gl}.mp4", 45, 200, gl, 900)   # ~10 frames
    except subprocess.TimeoutExpired:
        ok, tail = False, "timed out"
    results[gl] = {"ok": ok, "seconds": round(time.time() - t0, 1), "log": tail}
    print("GL TEST", gl, "OK" if ok else "FAILED", results[gl]["seconds"], "s\n", tail, flush=True)

good = [(r["seconds"], gl) for gl, r in results.items() if r["ok"]]
if good:
    best = min(good)[1]
    t0 = time.time()
    ok, tail = run("/kaggle/working/test-short.mp4", 0, 30, best, 3600)  # ~67 frames, ~2 s of video
    results["test_short"] = {"gl": best, "ok": ok, "seconds": round(time.time() - t0, 1), "log": tail}
json.dump(results, open("/kaggle/working/gl-results.json", "w"), indent=1)
print("\n===== SUMMARY (send this to Claude) =====")
print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "log"} | {"last": v["log"].splitlines()[-1] if v["log"] else ""} for k, v in results.items()}, indent=1))
