const express = require('express');
const { Pool } = require('pg');

const app = express();
app.use(express.json());

const pool = new Pool({
  host: process.env.DB_HOST || 'db',
  port: process.env.DB_PORT || 5432,
  user: process.env.DB_USER || 'admin',
  password: process.env.DB_PASSWORD || 'adminpassword',
  database: process.env.DB_NAME || 'appdb',
});

// 系統狀態 API
app.get('/api/status', (req, res) => {
  res.json({
    status: 'Running',
    node_version: process.version,
    hostname: process.env.HOSTNAME,
    time: new Date().toISOString()
  });
});

// 取得資料列表
app.get('/api/data', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM messages ORDER BY id DESC');
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 新增訊息至 PostgreSQL
app.post('/api/data', async (req, res) => {
  const { content } = req.body;
  if (!content) return res.status(400).json({ error: '內容不能為空' });
  try {
    const result = await pool.query('INSERT INTO messages (content) VALUES ($1) RETURNING *', [content]);
    res.status(201).json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`API running on port ${PORT}`));