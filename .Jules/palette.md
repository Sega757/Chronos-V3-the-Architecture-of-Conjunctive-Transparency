## 2024-09-14 - Missing Form Labels
**Learning:** Found that custom form controls (like `<select>` and `<textarea>`) in the SCCS platform lacked proper `<label>` associations, impacting screen reader compatibility and click-to-focus behavior.
**Action:** Always ensure custom or native form inputs are explicitly linked to a `<label>` using `htmlFor` and `id` attributes.

## 2024-09-16 - Non-Semantic Interactive Elements
**Learning:** Found that interactive list items (specifically, the article feed cards) in the SCCS platform were implemented as clickable `<div>` elements instead of native `<button>` or `<a>` elements. This prevented keyboard navigation (tabbing) and screen reader interaction.
**Action:** Always use native interactive elements like `<button>` for actions and `<a>` for navigation. Ensure they have proper focus styles (e.g., `focus-visible:ring-2`) and layout styles (like `w-full text-left` to match previous `<div>` block layouts) to maintain design intent while restoring accessibility.
## 2024-10-26 - Accessible Dynamic Interfaces
**Learning:** When developing developer or audit-focused real-time terminals (like the SCCS Terminal), visual indicators of state changes aren't enough for screen reader users. Dynamic log containers require aria-live="polite" and aria-atomic="false" to ensure real-time terminal outputs are announced sequentially without interrupting the user. Similarly, async operations triggered by user actions need aria-busy attributes combined with clear disabled visual states (like cursor-wait) to provide immediate feedback.
**Action:** Always add aria-live to terminal/log styled output containers and use aria-busy on buttons initiating complex simulations.
