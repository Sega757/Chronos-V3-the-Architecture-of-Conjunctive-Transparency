## 2023-10-27 - Missing Foreign Key Indexes
**Learning:** PostgreSQL does not automatically create indexes on foreign keys. This leads to O(N) full sequential table scans when querying child records (like `article_blocks` by `article_id`), and inefficient memory sorting when querying data sorted by unindexed timestamp columns (like `created_at` or `published_at`).
**Action:** Always verify query plans for joins and `ORDER BY` clauses to ensure critical columns are indexed to optimize performance.
## 2024-05-18 - [Lazy Loading in Dynamic AST Renderer]
**Learning:** The dynamic AST block renderer in `lib/renderer.tsx` bypasses Next.js built-in `<Image>` component optimization since natural dimensions are unknown for dynamic external user content. This forces all media to eagerly load.
**Action:** When working with dynamic content renderers where Next/Image is not feasible, always manually enforce `loading="lazy"` on native `<img>` and `<iframe>` HTML tags to prevent blocking the initial page render with off-screen assets.
