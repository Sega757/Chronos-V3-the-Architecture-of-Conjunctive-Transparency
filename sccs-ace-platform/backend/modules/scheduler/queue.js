const { Queue, Worker } = require('bullmq');
const Redis = require('ioredis');

const connection = new Redis(process.env.REDIS_URL || 'redis://redis:6379');

const sccsQueue = new Queue('sccsGenerationQueue', { connection });

const worker = new Worker('sccsGenerationQueue', async job => {
    console.log(`Processing job ${job.id}: ${job.name}`);
    // Simulate generation and DB persistence
    return { status: 'success' };
}, { connection });

module.exports = { sccsQueue };
