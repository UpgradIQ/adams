// Renders every docs/visuals/src/*.html page's #frame element to docs/assets/<name>.png at 2x.
// Usage: node docs/visuals/render.js   (Playwright is found the same way web_balance.js finds it)
const fs = require("fs"), path = require("path"), os = require("os");
const cache = path.join(os.homedir(), ".cache", "adams-line-balance");
const { chromium } = require(require.resolve("playwright", { paths: [process.cwd(), cache] }));
const src = path.join(__dirname, "src"), out = path.join(__dirname, "..", "assets");
(async () => {
  const b = await chromium.launch();
  for (const f of fs.readdirSync(src).filter((x) => x.endsWith(".html"))) {
    const one = /name=scale content=1/.test(fs.readFileSync(path.join(src, f), "utf8")); // social card is exactly 1280x640
    const p = await b.newPage({ deviceScaleFactor: one ? 1 : 2, viewport: { width: 1700, height: 1000 } });
    await p.goto("file://" + path.join(src, f)); await p.evaluate(() => document.fonts.ready);
    await p.locator("#frame").screenshot({ path: path.join(out, f.replace(".html", ".png")), omitBackground: true });
    console.log("rendered", f);
  }
  await b.close();
})();
