## 2023-10-27 - Missing Foreign Key Indexes
**Learning:** PostgreSQL does not automatically create indexes on foreign keys. This leads to O(N) full sequential table scans when querying child records (like `article_blocks` by `article_id`), and inefficient memory sorting when querying data sorted by unindexed timestamp columns (like `created_at` or `published_at`).
**Action:** Always verify query plans for joins and `ORDER BY` clauses to ensure critical columns are indexed to optimize performance.

## 2026-09-24 - Lazy Loading External Assets
**Learning:** Images and iframes (like YouTube embeds) rendered dynamically from AST blocks can significantly slow down the initial page load time if loaded eagerly.
**Action:** Always include `loading="lazy"` for `<img>` and `<iframe>` tags, especially when content is dynamic or frequently falls below the fold.

## 2026-09-27 - [Memoize expensive JSON.parse in render]
**Learning:** Inline JSON.parse in React components can cause significant performance degradation when state updates frequently (like during simulation pulses). Parsing JSON is a synchronous, blocking operation that runs on every render if not memoized.
**Action:** Use useMemo to cache parsed JSON payloads in React components that experience high-frequency state updates to prevent unnecessary re-parsing.
## 2023-10-28 - Memoize Static List Rendering
**Learning:** During rapid state updates (like real-time simulation ticks with `simLog`, `simEntropy`, `simHuber`), re-rendering the entire parent component forces React to recreate and re-reconcile the Virtual DOM nodes for lists (`articles.map`, `sites.map`, `categories.map`), even though their source data is completely static. This leads to severe rendering bottlenecks and UI stuttering.
**Action:** Inline `useMemo` for mapped JSX lists to prevent unnecessary VDOM reconciliation during frequent state updates.

## 2023-10-28 - Cache Expensive SSR Renders
**Learning:** Next.js SSR pages without caching headers will block and hit the backend on every single request. This creates a severe performance bottleneck when traffic spikes, causing server overload and slow response times.
**Action:** Use `stale-while-revalidate` in `getServerSideProps` for heavily read content to serve cached responses instantly from the edge while revalidating data in the background.
## 2023-10-28 - Element Caching for Selected Articles
**Learning:** In the `SCCSControlPanel` component, updating high-frequency state like `simLog` or `simEntropy` causes the entire component to re-render, forcing React to unnecessarily recreate and reconcile the virtual DOM for static child components. When rendering lists of items that do not depend on the high-frequency state (such as the blocks of a selected article), this introduces a significant performance hit.
**Action:** Use `useMemo` to cache the generated React elements for static lists (e.g., `selectedArticle.blocks`) so that React skips their reconciliation during unrelated state updates, significantly reducing the render time.
## 2026-10-07 - Composite Index for Filtering and Sorting
**Learning:** When queries filter by a foreign key and sort by another column (e.g., `WHERE article_id = $1 ORDER BY position ASC`), a single-column index on the foreign key still requires an expensive in-memory sort. A composite index covering both the filter column and the sort column prevents this.
**Action:** Add composite indexes for frequently queried pairs of (filter_column, sort_column) to avoid database memory sorts.
## 2026-10-30 - Optimize Expensive Queries with Composite Indexes and Column Pruning
**Learning:** Unbounded raw SQL queries with `SELECT *` and unindexed sorts result in massive network serialization overhead and expensive O(N) sequential table scans / in-memory sorts.
**Action:** Add composite indexes covering filtering and sorting columns (e.g. `(category_id, published_at DESC)`), and explicitly project only the required columns in API endpoints (e.g. `SELECT a.id, a.title...`) instead of using `SELECT *` to optimize database and network load without breaking pagination contracts.
## 2026-10-31 - Extract State to Prevent List Re-renders
**Learning:** Hoisting interactive transient state (like `copiedBlockId`) to the root of a large list component (like `SCCSControlPanel`) invalidates list memoization (e.g., `renderedSelectedArticleBlocks`) on every interaction, causing an O(N) re-render of all list items.
**Action:** Extract interactive elements with localized state into their own isolated React components to prevent massive parent re-renders.
## 2023-11-01 - Preventing O(N) List Re-renders on Selection Change
**Learning:** When a list is rendered from an array in React, and selecting an item updates the parent's state (e.g., `selectedArticle`), it forces all items in the list to re-render, creating an O(N) performance bottleneck.
**Action:** Extract the list item into its own component wrapped with `React.memo()`. Pass primitive or stable references (like `isSelected` boolean) as props, and use `useCallback` for the selection handler to ensure referential equality across parent renders.
## 2026-11-01 - Avoid Column Pruning on Single-Row Fetches\n**Learning:** As the 'Bolt' persona, explicitly projecting columns (column pruning) to replace `SELECT *` in queries that only fetch a single row (e.g., fetching a specific entity by ID or slug) is considered a micro-optimization with zero measurable impact and introduces high risk of frontend regressions.\n**Action:** Focus column pruning strictly on unbounded list queries or tables with massive text columns, and avoid it for single-row fetch endpoints.
## 2026-11-03 - Extract Complex JSX to Memoized Components
**Learning:** Mapping over an array and creating complex inline JSX elements (like the Forensic Logs in `SCCSControlPanel`) within a large component causes slow renders, even if `useMemo` is used, because the massive JSX still needs to be evaluated when the array changes (like during the simulation when a new log is pushed).
**Action:** Extract the inline JSX block into a separate `React.memo` component (e.g., `LogItem`).
## 2026-10-24 - Isolate High-Frequency Input State
**Learning:** Keeping high-frequency input state (like keystrokes in a textarea) in the root of a large component forces the entire component tree to re-render on every keystroke, causing severe input lag.
**Action:** Extract input elements with transient state into their own isolated React components to prevent parent re-renders.
