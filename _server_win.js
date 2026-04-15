// Servidor auxiliar para Windows via Node.js (fallback se Python não disponível)
const http = require('http');
const fs   = require('fs');
const path = require('path');

const PORT = 8765;
const DIR  = __dirname;

const MIME = {
  '.html': 'text/html', '.js': 'application/javascript',
  '.wasm': 'application/wasm', '.css': 'text/css',
  '.mp4': 'video/mp4', '.webm': 'video/webm',
  '.png': 'image/png', '.jpg': 'image/jpeg',
};

http.createServer((req, res) => {
  let filePath = path.join(DIR, req.url === '/' ? 'index.html' : req.url);
  const ext = path.extname(filePath);

  res.setHeader('Cross-Origin-Opener-Policy', 'same-origin');
  res.setHeader('Cross-Origin-Embedder-Policy', 'require-corp');
  res.setHeader('Access-Control-Allow-Origin', '*');

  fs.readFile(filePath, (err, data) => {
    if (err) { res.writeHead(404); res.end('Not found'); return; }
    res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream' });
    res.end(data);
  });
}).listen(PORT, () => {
  console.log(`Servidor rodando em http://localhost:${PORT}`);
});
