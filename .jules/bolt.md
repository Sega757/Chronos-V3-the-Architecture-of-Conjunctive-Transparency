## 2023-10-27 - Missing Foreign Key Indexes
**Learning:** PostgreSQL does not automatically create indexes on foreign keys. This leads to O(N) full sequential table scans when querying child records (like `article_blocks` by `article_id`), and inefficient memory sorting when querying data sorted by unindexed timestamp columns (like `created_at` or `published_at`).
**Action:** Always verify query plans for joins and `ORDER BY` clauses to ensure critical columns are indexed to optimize performance.

## 2026-09-24 - Lazy Loading External Assets
**Learning:** Images and iframes (like YouTube embeds) rendered dynamically from AST blocks can significantly slow down the initial page load time if loaded eagerly.
**Action:** Always include `loading="lazy"` for `<img>` and `<iframe>` tags, especially when content is dynamic or frequently falls below the fold.

## 2023-10-28 - Unnecessary JSON parsing on render loop
**Learning:** Parsing JSON during the React render cycle (like `JSON.parse(activeSite.config_json)`) causes unnecessary synchronous overhead on every re-render, especially for components with frequent state updates.
**Action:** Always wrap expensive synchronous operations like `JSON.parse` inside a `useMemo` hook to ensure they are only executed when their specific dependencies change.
