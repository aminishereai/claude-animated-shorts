# Kaggle GPU render: copies the render project from a private dataset, installs Node + Chrome, renders the whole composition on the GPU.
# Pushed with `kaggle kernels push` (kernel-metadata.json: GPU + internet on). Output: /kaggle/working/video.mp4
import json, os, subprocess, time

SRC = "/kaggle/input/3dio-render-src"  # the render/ folder, uploaded as a private Kaggle dataset (no node_modules)
COMP = "BridgeShort"
PROPS = {"w": 1080, "h": 1920}  # full size on a GPU; set post flags here to compare

def sh(cmd):
    print("+", cmd, flush=True)
    subprocess.run(cmd, shell=True, check=True)

sh("nvidia-smi || true")
sh("curl -fsSL https://deb.nodesource.com/setup_22.x | bash - >/dev/null && apt-get install -y nodejs >/dev/null")
sh("apt-get install -y libnss3 libatk-bridge2.0-0 libgbm1 libxkbcommon0 libasound2 libxcomposite1 libxdamage1 libxrandr2 libpango-1.0-0 libcairo2 libvulkan1 >/dev/null || true")
import glob
tgz = (glob.glob(SRC + "/**/render.tgz", recursive=True) + glob.glob("/kaggle/input/**/render.tgz", recursive=True))[0]
sh(f"rm -rf /kaggle/working/render && tar xzf {tgz} -C /kaggle/working")
os.chdir("/kaggle/working/render")
sh("npm ci --no-audit --no-fund")
sh("npx remotion browser ensure")

results = {}
for gl in ["angle-egl", "vulkan", "angle", "swiftshader"]:
    t0 = time.time()
    try:
        env = dict(os.environ, COMP=COMP, GL=gl)
        # 1 chunk of 200 = ~10 frames, to time this GL mode
        subprocess.run(["node", "scripts/render-chunk.mjs", f"/kaggle/working/test-{gl}.mp4", "45", "200", json.dumps(PROPS)], env=env, check=True, timeout=1200)
        results[gl] = round(time.time() - t0, 1)
    except Exception as e:
        results[gl] = f"failed: {e}"
    print("GL TEST", gl, results[gl], flush=True)
    if isinstance(results[gl], float) and results[gl] < 120:
        break

json.dump(results, open("/kaggle/working/gl-results.json", "w"), indent=1)
ok = [(v, k) for k, v in results.items() if isinstance(v, float) and k != "swiftshader"]
if not ok:
    print("NO GPU MODE WORKED", results, flush=True); raise SystemExit(0)
best = min(ok)[1]
t0 = time.time()
env = dict(os.environ, COMP=COMP, GL=best)
sh_env = " ".join(f"{k}={v}" for k, v in {"COMP": COMP, "GL": best}.items())
subprocess.run(["node", "scripts/render-chunk.mjs", "/kaggle/working/video.mp4", "0", "1", json.dumps(PROPS)], env=env, check=True)
print("FULL RENDER", best, round(time.time() - t0, 1), "s", flush=True)
