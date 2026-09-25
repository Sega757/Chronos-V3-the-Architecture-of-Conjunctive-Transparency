## 2023-10-27 - Missing Foreign Key Indexes
**Learning:** PostgreSQL does not automatically create indexes on foreign keys. This leads to O(N) full sequential table scans when querying child records (like `article_blocks` by `article_id`), and inefficient memory sorting when querying data sorted by unindexed timestamp columns (like `created_at` or `published_at`).
**Action:** Always verify query plans for joins and `ORDER BY` clauses to ensure critical columns are indexed to optimize performance.

## 2026-09-24 - Lazy Loading External Assets
**Learning:** Images and iframes (like YouTube embeds) rendered dynamically from AST blocks can significantly slow down the initial page load time if loaded eagerly.
**Action:** Always include `loading="lazy"` for `<img>` and `<iframe>` tags, especially when content is dynamic or frequently falls below the fold.
## 2026-09-25 - Memoization of Dynamic Configs in Next.js
**Learning:** Frequent React state updates during data streaming or simulation intervals can trigger expensive unmemoized operations on every render, such as parsing inline JSON strings from configurations.
**Action:** Use `useMemo` to parse JSON strings from external config data that remains static for long periods, mitigating UI locking or CPU bottlenecking during high-frequency render updates.
