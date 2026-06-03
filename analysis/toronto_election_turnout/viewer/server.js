const http = require("http");
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const repoRoot = path.resolve(__dirname, "..", "..", "..");
const port = Number(process.env.PORT || 5173);
const host = process.env.HOST || "127.0.0.1";

const types = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".geojson": "application/geo+json; charset=utf-8",
  ".csv": "text/csv; charset=utf-8",
  ".png": "image/png",
  ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
};

function safePath(urlPath) {
  const cleanUrl = decodeURIComponent(urlPath.split("?")[0]);
  const requested = cleanUrl === "/" ? "/viewer/index.html" : cleanUrl;
  const base = requested.startsWith("/data/") ? repoRoot : root;
  const resolved = path.resolve(base, "." + requested);
  return resolved.startsWith(base) ? resolved : null;
}

const server = http.createServer((req, res) => {
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
});

server.listen(port, host, () => {
  console.log(`Toronto turnout map viewer running at http://${host}:${port}`);
});
