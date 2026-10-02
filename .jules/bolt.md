## 2023-10-27 - Missing Foreign Key Indexes
**Learning:** PostgreSQL does not automatically create indexes on foreign keys. This leads to O(N) full sequential table scans when querying child records (like `article_blocks` by `article_id`), and inefficient memory sorting when querying data sorted by unindexed timestamp columns (like `created_at` or `published_at`).
**Action:** Always verify query plans for joins and `ORDER BY` clauses to ensure critical columns are indexed to optimize performance.

## 2026-09-24 - Lazy Loading External Assets
**Learning:** Images and iframes (like YouTube embeds) rendered dynamically from AST blocks can significantly slow down the initial page load time if loaded eagerly.
**Action:** Always include `loading="lazy"` for `<img>` and `<iframe>` tags, especially when content is dynamic or frequently falls below the fold.

## 2026-09-27 - [Memoize expensive JSON.parse in render]
**Learning:** Inline JSON.parse in React components can cause significant performance degradation when state updates frequently (like during simulation pulses). Parsing JSON is a synchronous, blocking operation that runs on every render if not memoized.
**Action:** Use useMemo to cache parsed JSON payloads in React components that experience high-frequency state updates to prevent unnecessary re-parsing.

## 2026-03-30 - Eliminating Redundant NumPy Conditional Array Allocations
**Learning:** In NumPy array operations, applying conditional guards like `np.where(abs_res == 0, 1e-8, abs_res)` before indexing with a boolean mask (e.g. `abs_res > delta` where `delta > 0`) is redundant because elements selected by the mask are already guaranteed to be non-zero. Eliminating `np.where` avoids creating unnecessary intermediate array allocations, reducing latency and memory bandwidth overhead.
**Action:** Always check whether boolean masks strictly constrain array values before introducing conditional zero-guard allocations like `np.where`.
