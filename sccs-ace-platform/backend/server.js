require('dotenv').config({ path: '../.env' });
const express = require('express');
const rateLimit = require('express-rate-limit');
const cors = require('cors');
const helmet = require('helmet');
const { Pool } = require('pg');
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const path = require('path');
const { sccsQueue } = require('./modules/scheduler/queue');

const app = express();
const PORT = process.env.PORT || 3000;

// 🛡️ Sentinel: Rate limiting for expensive/resource-intensive API endpoints
const apiLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // Limit each IP to 100 requests per `window` (here, per 15 minutes)
    message: { error: 'Too many requests from this IP, please try again after 15 minutes' },
    standardHeaders: true, // Return rate limit info in the `RateLimit-*` headers
    legacyHeaders: false, // Disable the `X-RateLimit-*` headers
});


app.use(helmet());
app.use(cors());
app.use(express.json());

// Database connection
if (!process.env.DATABASE_URL) {
  console.error("CRITICAL: DATABASE_URL environment variable is not set.");
  process.exit(1);
}

const pool = new Pool({
  connectionString: process.env.DATABASE_URL
});

// Setup gRPC Client
const PROTO_PATH = path.join(__dirname, '../sccs_core/protos/chronos_interface.proto');
const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
    keepCase: true,
    longs: String,
    enums: String,
    defaults: true,
    oneofs: true
});
const sccs_proto = grpc.loadPackageDefinition(packageDefinition).sccs.v1.chronos;

const chronosHost = process.env.CHRONOS_GRPC_HOST || 'sccs_core:50051';
const chronosClient = new sccs_proto.RealityFilter(
    chronosHost,
    grpc.credentials.createInsecure()
);

// API Routes
app.get('/api/health', (req, res) => {
    res.json({ status: 'healthy', service: 'SCCS Control Plane' });
});

app.get('/api/sites', async (req, res) => {
    try {
        const result = await pool.query('SELECT * FROM sites WHERE is_active = true');
        res.json(result.rows);
    } catch (err) {
        console.error('API Error:', err);
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.get('/api/articles', async (req, res) => {
    try {
        const result = await pool.query(`
            SELECT a.id, a.title, a.slug, a.summary, a.status, a.views_count, a.published_at, c.name as category_name, c.frequency_type
            FROM articles a
            LEFT JOIN categories c ON a.category_id = c.id
            ORDER BY a.published_at DESC
        `);
        res.json(result.rows);
    } catch (err) {
        console.error('API Error:', err);
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.get('/api/articles/slug/:slug', async (req, res) => {
    try {
        const { slug } = req.params;
        const articleResult = await pool.query(`
            SELECT a.*, c.name as category_name, c.frequency_type
            FROM articles a
            LEFT JOIN categories c ON a.category_id = c.id
            WHERE a.slug = $1
        `, [slug]);

        if (articleResult.rows.length === 0) {
            return res.status(404).json({ error: 'Article not found' });
        }

        const article = articleResult.rows[0];
        const blocksResult = await pool.query('SELECT * FROM article_blocks WHERE article_id = $1 ORDER BY position ASC', [article.id]);
        article.blocks = blocksResult.rows;

        res.json(article);
    } catch (err) {
        console.error('API Error:', err);
        res.status(500).json({ error: 'Internal server error' });
    }
});


app.get('/api/articles/:id/blocks', async (req, res) => {
    try {
        // 🛡️ Sentinel: Validate ID to be a number before passing to database to avoid internal query errors
        const articleId = parseInt(req.params.id, 10);
        if (isNaN(articleId)) {
            return res.status(400).json({ error: 'Invalid ID format' });
        }

        const result = await pool.query('SELECT * FROM article_blocks WHERE article_id = $1 ORDER BY position ASC', [articleId]);
        res.json(result.rows);
    } catch (err) {
        console.error('API Error:', err);
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.get('/api/logs', async (req, res) => {
    try {
        // ⚡ Bolt: Omit heavy unused text columns (like response_text) in API queries
        // to save significant network and serialization overhead.
        const result = await pool.query('SELECT id, model_used, prompt_hash, prompt_text, execution_time_ms, status, created_at FROM generation_logs ORDER BY created_at DESC LIMIT 50');
        res.json(result.rows);
    } catch (err) {
        console.error('API Error:', err);
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.get('/api/metrics', async (req, res) => {
    try {
        const result = await pool.query('SELECT article_id, views, clicks, avg_time_seconds, bounce_rate FROM metrics');
        // Transform into a map by article_id for the frontend
        const metricsMap = {};
        result.rows.forEach(row => {
            metricsMap[row.article_id] = row;
        });
        res.json(metricsMap);
    } catch (err) {
        console.error('API Error:', err);
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.get('/api/categories', async (req, res) => {
    try {
        const result = await pool.query('SELECT * FROM categories');
        res.json(result.rows);
    } catch (err) {
        console.error('API Error:', err);
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.post('/api/generate', apiLimiter, async (req, res) => {
    const { prompt } = req.body;
    if (typeof prompt !== 'string' || prompt.length === 0 || prompt.length > 5000) {
        return res.status(400).json({ error: 'Invalid prompt parameter' });
    }
    await sccsQueue.add('generateArticle', { prompt });
    res.json({ status: 'queued', message: 'Article generation queued.' });
});

// Trigger a Chronos verification via gRPC
app.post('/api/verify', apiLimiter, (req, res) => {
    const { session_id, query_target } = req.body;

    if (typeof session_id !== 'string' || session_id.length === 0 || session_id.length > 255) {
        return res.status(400).json({ error: 'Invalid session_id parameter' });
    }
    if (typeof query_target !== 'string' || query_target.length === 0 || query_target.length > 5000) {
        return res.status(400).json({ error: 'Invalid query_target parameter' });
    }

    chronosClient.IngestTelemetry({ session_id, query_target }, (error, response) => {
        if (error) {
            console.error(error);
            return res.status(500).json({ status: 'error', message: 'gRPC Communication failed' });
        }

        if (response.signal_absent) {
            return res.json({ status: 'fail-fast', message: 'Signal Absent' });
        }

        // Pass to Sterilize
        chronosClient.SterilizeAndAlign({
            session_id,
            raw_values: response.raw_values,
            huber_delta: 1.35
        }, (err, alignResponse) => {
            if (err) {
                 return res.status(500).json({ status: 'error', message: 'Sterilization failed' });
            }
            res.json({
                status: 'success',
                knowledge_object: alignResponse
            });
        });
    });
});

app.listen(PORT, () => {
    console.log(`SCCS Control Plane running on port ${PORT}`);
});
