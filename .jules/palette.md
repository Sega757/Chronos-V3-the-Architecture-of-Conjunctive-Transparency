## 2026-10-03 - Master-Detail Empty States
**Learning:** When using a master-detail layout (like a feed and a viewer), leaving the detail section completely blank before selection is disorienting and looks broken. An empty state explicitly informs the user that an action is required in the master view to populate the detail view.
**Action:** Always include a visual 'empty state' fallback in the detail section of master-detail components to guide the user on how to interact with the interface.

## 2026-10-04 - Keyboard Accessibility for Primary Actions
**Learning:** Primary action buttons were missing visible focus indicators, making them invisible to keyboard navigation users. Relying only on hover states excludes a significant portion of users.
**Action:** Always add explicit `focus-visible:ring` styles to all interactive elements to ensure clear visual feedback during keyboard navigation.

## 2026-10-05 - Dynamic and Accessible Status Badges
**Learning:** Visual-only status indicators provide no context to screen readers or users who don't understand the color code. Hardcoded colors fail to reflect dynamic states like errors. Additionally, solid bright backgrounds with similar colored text fail WCAG contrast guidelines.
**Action:** Always add semantic meaning via role="status", aria-label, and title for hover tooltips. Ensure badges dynamically reflect their state using accessible styling (e.g., red for errors, green for success) rather than statically hardcoding colors. Use a semi-transparent background combined with a solid or semi-transparent border to ensure readability.
