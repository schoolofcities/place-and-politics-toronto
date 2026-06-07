const http = require("http");
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname);
const repoRoot = path.resolve(__dirname, "..", "..", "..", "..");
const electionVendor = path.resolve(__dirname, "..", "..", "elections", "viewer", "vendor");
const port = Number(process.env.PORT || 5174);
const host = process.env.HOST || "127.0.0.1";

const types = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".geojson": "application/geo+json; charset=utf-8",
  ".png": "image/png"
};

function safePath(urlPath) {
  const cleanUrl = decodeURIComponent(urlPath.split("?")[0]);
  const requested = cleanUrl === "/" ? "/index.html" : cleanUrl;
  let base = root;
  let relative = requested;
  if (requested.startsWith("/data/")) {
    base = repoRoot;
  } else if (requested.startsWith("/vendor/")) {
    base = electionVendor;
    relative = requested.slice("/vendor".length);
  }
  const resolved = path.resolve(base, "." + relative);
  return resolved.startsWith(base) ? resolved : null;
}

http.createServer((req, res) => {
  const filePath = safePath(req.url || "/");
  if (!filePath) {
    res.writeHead(403);
    res.end("Forbidden");
    return;
  }
  fs.readFile(filePath, (error, data) => {
    if (error) {
      res.writeHead(404);
      res.end("Not found");
      return;
    }
    res.writeHead(200, {
      "Content-Type": types[path.extname(filePath)] || "application/octet-stream",
      "Cache-Control": "no-cache"
    });
    res.end(data);
  });
}).listen(port, host, () => {
  console.log(`Toronto census geography viewer running at http://${host}:${port}`);
});
