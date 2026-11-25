# 3Dio render farm

Remotion + three.js project for the cartoon style (2D cards in a 3D world), set up to render without a GPU.

- `src/videos/bridge/`: the bridge demo from `templates/bridge/`, patched so size, anti-aliasing (`post.msaa`),
  shadows (`post.shadows`) and character texture size (`post.tier`) come from input props.
- `public/bridge/kenney/`: Kenney Nature Kit and Fantasy Town Kit models (CC0, kenney.nl).
- `scripts/render-chunk.mjs`: renders chunk i of n with software WebGL.
- `.github/workflows/render.yml`: run it from the Actions tab ("render" → Run workflow). It renders 20 chunks in
  parallel at 540x960, joins them and upscales to 1080x1920. The result is the `video` artifact (silent; the voice
  and music are mixed in afterwards).

Measured on 4 CPU cores: ~36 s per frame at 540x960 on the busiest crowd shot; full 1080x1920 is ~100 s per frame.
