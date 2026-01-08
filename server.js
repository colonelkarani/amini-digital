const compression = require('compression');
const express = require('express');
const path = require('path');
const app = express();

// Production mode first
process.env.NODE_ENV = 'production';

// Middleware order: compression first, then static
app.use(compression());  // Gzip brotli
app.use(express.static(path.join(__dirname, 'aminifudigital'), {  // Or your static dir
  maxAge: '1d',  // Browser cache 1 day
  etag: true,    // ETags for validation
  setHeaders: (res, path) => {
    if (path.endsWith('.js')) res.set('Cache-Control', 'public, max-age=31536000');  // 1 year JS
    if (path.endsWith('.css')) res.set('Cache-Control', 'public, max-age=31536000');
  }
}));

app.listen(3000, '0.0.0.0');

