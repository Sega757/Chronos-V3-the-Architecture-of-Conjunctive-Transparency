## 2026-10-03 - Master-Detail Empty States
**Learning:** When using a master-detail layout (like a feed and a viewer), leaving the detail section completely blank before selection is disorienting and looks broken. An empty state explicitly informs the user that an action is required in the master view to populate the detail view.
**Action:** Always include a visual 'empty state' fallback in the detail section of master-detail components to guide the user on how to interact with the interface.

## 2026-10-04 - Keyboard Accessibility for Primary Actions
**Learning:** Primary action buttons were missing visible focus indicators, making them invisible to keyboard navigation users. Relying only on hover states excludes a significant portion of users.
**Action:** Always add explicit `focus-visible:ring` styles to all interactive elements to ensure clear visual feedback during keyboard navigation.
