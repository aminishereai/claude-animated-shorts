// Renders one chunk of a composition with software WebGL (no GPU needed).
// usage: node scripts/render-chunk.mjs <out.mp4> <chunkIndex> <chunkCount> [propsJson]
// env: CHROME (browser path, optional), COMP (default BridgeShort), GL (default swiftshader)
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import path from "node:path";
const [out, idx, count, propsJson] = process.argv.slice(2);
const inputProps = JSON.parse(propsJson || "{}");
const browserExecutable = process.env.CHROME || null;
const chromiumOptions = { gl: process.env.GL || "swiftshader" };
const id = process.env.COMP || "BridgeShort";
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts"), publicDir: path.resolve("public") });
const composition = await selectComposition({ serveUrl, id, browserExecutable, chromiumOptions, inputProps });
const n = composition.durationInFrames, c = Number(count), i = Number(idx);
const a = Math.floor((n * i) / c), b = Math.floor((n * (i + 1)) / c) - 1;
console.log(`chunk ${i + 1}/${c}: frames ${a}-${b} of ${n}, ${composition.width}x${composition.height}`);
const t0 = Date.now(); let last = -1;
await renderMedia({ composition, serveUrl, inputProps, codec: "h264", crf: 16, outputLocation: out, frameRange: [a, b], concurrency: 1,
  browserExecutable, chromiumOptions, timeoutInMilliseconds: 900000, muted: true,
  onProgress: ({ renderedFrames }) => { if (renderedFrames !== last && renderedFrames % 10 === 0) { last = renderedFrames; console.log(`frames ${renderedFrames}/${b - a + 1} ${((Date.now() - t0) / 1000).toFixed(0)}s`); } } });
console.log(`done in ${((Date.now() - t0) / 1000).toFixed(0)}s, ${(((Date.now() - t0) / 1000) / (b - a + 1)).toFixed(1)} s/frame`);
