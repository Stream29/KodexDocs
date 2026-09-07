import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { resolve, sep, extname } from 'node:path';

const root = fileURLToPath(new URL('../docs/', import.meta.url));
const types = { '.html': 'text/html; charset=utf-8', '.md': 'text/plain; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.xml': 'application/xml' };
createServer(async (request, response) => {
  try {
    let path = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
    if (path === '/' || path === '/KodexDocs') {
      response.writeHead(302, { Location: '/KodexDocs/' }).end();
      return;
    }
    if (!path.startsWith('/KodexDocs/')) throw new Error('Not found');
    path = path.slice('/KodexDocs/'.length);
    if (path.endsWith('/') || !path) path += 'index.html';
    const file = resolve(root, path);
    if (!file.startsWith(root.endsWith(sep) ? root : root + sep)) throw new Error('Not found');
    const body = await readFile(file);
    response.writeHead(200, { 'Content-Type': types[extname(file)] ?? 'application/octet-stream', 'Cache-Control': 'no-store' }).end(body);
  } catch {
    response.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' });
    response.end(await readFile(resolve(root, '404.html')));
  }
}).listen(4173, '127.0.0.1', () => console.log('Preview: http://127.0.0.1:4173/KodexDocs/'));
