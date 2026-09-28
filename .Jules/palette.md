## 2024-09-14 - Missing Form Labels
**Learning:** Found that custom form controls (like `<select>` and `<textarea>`) in the SCCS platform lacked proper `<label>` associations, impacting screen reader compatibility and click-to-focus behavior.
**Action:** Always ensure custom or native form inputs are explicitly linked to a `<label>` using `htmlFor` and `id` attributes.

## 2024-09-16 - Non-Semantic Interactive Elements
**Learning:** Found that interactive list items (specifically, the article feed cards) in the SCCS platform were implemented as clickable `<div>` elements instead of native `<button>` or `<a>` elements. This prevented keyboard navigation (tabbing) and screen reader interaction.
**Action:** Always use native interactive elements like `<button>` for actions and `<a>` for navigation. Ensure they have proper focus styles (e.g., `focus-visible:ring-2`) and layout styles (like `w-full text-left` to match previous `<div>` block layouts) to maintain design intent while restoring accessibility.
## 2026-09-24 - Prevent Inputs While Simulating\n**Learning:** The simulation process blocks user interaction with a visual indicator, but screen readers need explicit `role="log"` and `aria-live="polite"` on the output terminal to properly hear updates. Visual disabled states like `disabled:opacity-50` and `disabled:cursor-not-allowed` should be applied on both buttons and textareas.\n**Action:** Always pair visual disabled states with programmatic disabled states and explicitly announce real-time updates for screen readers.

## 2026-09-28 - Missing Empty State for Detail Views
**Learning:** Found that the SCCS platform's 'Detailed Article Core Viewer' was completely hidden when no article was selected, leaving a visual void and causing confusion about how to populate the area.
**Action:** Always provide a helpful empty state for detail or preview panes that explains how to populate the area and why it is currently empty, improving discoverability and overall user experience.
