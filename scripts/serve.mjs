// Minimal static server for local preview: serves extensionless URLs,
// /index.html for "/", and 404.html with a real 404 status.
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { extname, join, normalize, sep } from 'node:path';

const ROOT = process.cwd();
const PORT = Number(process.env.PORT || 5173);

const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.webmanifest': 'application/manifest+json; charset=utf-8',
  '.xml': 'application/xml; charset=utf-8',
  '.txt': 'text/plain; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.ico': 'image/x-icon',
  '.pdf': 'application/pdf',
  '.woff2': 'font/woff2',
};

async function tryFile(path) {
  try {
    const body = await readFile(path);
    return body;
  } catch {
    return null;
  }
}

const server = createServer(async (req, res) => {
  const url = new URL(req.url || '/', 'http://localhost');
  let pathname = decodeURIComponent(url.pathname);
  if (pathname.endsWith('/')) pathname += 'index.html';

  // Block path traversal
  const target = normalize(join(ROOT, pathname));
  if (!target.startsWith(ROOT + sep) && target !== ROOT) {
    res.writeHead(403).end('Forbidden');
    return;
  }

  let body = await tryFile(target);
  let filePath = target;
  if (!body && !extname(target)) {
    body = await tryFile(target + '.html');
    if (body) filePath = target + '.html';
  }

  if (!body) {
    const notFound = await tryFile(join(ROOT, '404.html'));
    res.writeHead(404, { 'Content-Type': TYPES['.html'] });
    res.end(notFound || 'Not found');
    return;
  }

  res.writeHead(200, {
    'Content-Type': TYPES[extname(filePath)] || 'application/octet-stream',
    'Cache-Control': 'no-store',
  });
  res.end(body);
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`hanylockedin.com preview → http://0.0.0.0:${PORT}`);
});
