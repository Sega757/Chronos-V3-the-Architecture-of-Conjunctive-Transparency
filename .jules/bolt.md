## 2023-10-27 - Missing Foreign Key Indexes
**Learning:** PostgreSQL does not automatically create indexes on foreign keys. This leads to O(N) full sequential table scans when querying child records (like `article_blocks` by `article_id`), and inefficient memory sorting when querying data sorted by unindexed timestamp columns (like `created_at` or `published_at`).
**Action:** Always verify query plans for joins and `ORDER BY` clauses to ensure critical columns are indexed to optimize performance.

## 2026-09-20 - Missing Media Lazy Loading in Block Renderer
**Learning:** The dynamic block rendering system (`renderer.tsx`) renders all media blocks (images and YouTube iframes) eagerly by default. In articles with many multimedia blocks, this causes significant network congestion and main-thread blocking as off-screen media loads simultaneously with the initial page render.
**Action:** Always verify that dynamic content rendering components include `loading="lazy"` attributes on heavy media elements (`<img>`, `<iframe>`) to defer their loading until they enter the viewport.
