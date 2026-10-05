// Renders TeX to SVG with MathJax, for scripts/render_epub.py.
//
//   node tex_to_svg.mjs <mathjax package dir> < [[tex, display], ...] > [svg, ...]
//
// Glyphs are drawn as paths (fontCache "none"), so each SVG stands alone as an
// image file. The package is imported by path because it is installed globally
// (setup_dev.sh), where ES modules cannot resolve it by name.

import { readFileSync } from "node:fs";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

const { default: MathJax } = await import(pathToFileURL(join(process.argv[2], "node-main.mjs")));
await MathJax.init({ loader: { load: ["input/tex", "output/svg"] }, svg: { fontCache: "none" } });
const adaptor = MathJax.startup.adaptor;

const svgs = [];
for (const [tex, display] of JSON.parse(readFileSync(0, "utf8"))) {
  const svg = adaptor.serializeXML(adaptor.firstChild(await MathJax.tex2svgPromise(tex, { display })));
  // Undefined macros render in red rather than as an error node.
  const error = svg.match(/data-mjx-error="([^"]*)"/)?.[1] ?? (svg.includes('fill="red"') ? "undefined macro" : null);
  if (error) {
    process.stderr.write(`warning: MathJax: ${error}: ${tex}\n`);
  }
  svgs.push(svg);
}
process.stdout.write(JSON.stringify(svgs));
