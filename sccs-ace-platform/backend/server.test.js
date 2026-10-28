const request = require('supertest');
const express = require('express');

const mPool = {
    query: jest.fn().mockResolvedValue({
        rows: [
            { article_id: 1, views: 100, clicks: 10, avg_time_seconds: 50, bounce_rate: 0.1 }
        ]
    }),
};

const app = express();
app.get('/api/metrics', async (req, res) => {
    try {
        const result = await mPool.query(`
            SELECT m.article_id, m.views, m.clicks, m.avg_time_seconds, m.bounce_rate
            FROM metrics m
            JOIN articles a ON m.article_id = a.id
            WHERE a.status = 'published'
        `);
        const metricsMap = {};
        result.rows.forEach(row => {
            metricsMap[row.article_id] = row;
        });
        res.json(metricsMap);
    } catch (err) {
        res.status(500).json({ error: 'Internal server error' });
    }
});

describe('GET /api/metrics', () => {
    it('returns a metrics map for published articles', async () => {
        const res = await request(app).get('/api/metrics');
        expect(res.statusCode).toEqual(200);
        expect(res.body).toHaveProperty('1');
        expect(res.body['1'].views).toEqual(100);
        expect(mPool.query).toHaveBeenCalledWith(expect.stringContaining('JOIN articles a ON m.article_id = a.id'));
        expect(mPool.query).toHaveBeenCalledWith(expect.stringContaining("WHERE a.status = 'published'"));
    });
});
