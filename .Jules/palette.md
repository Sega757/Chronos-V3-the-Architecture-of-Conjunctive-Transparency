## 2024-09-14 - Missing Form Labels
**Learning:** Found that custom form controls (like `<select>` and `<textarea>`) in the SCCS platform lacked proper `<label>` associations, impacting screen reader compatibility and click-to-focus behavior.
**Action:** Always ensure custom or native form inputs are explicitly linked to a `<label>` using `htmlFor` and `id` attributes.

## 2024-09-16 - Non-Semantic Interactive Elements
**Learning:** Found that interactive list items (specifically, the article feed cards) in the SCCS platform were implemented as clickable `<div>` elements instead of native `<button>` or `<a>` elements. This prevented keyboard navigation (tabbing) and screen reader interaction.
**Action:** Always use native interactive elements like `<button>` for actions and `<a>` for navigation. Ensure they have proper focus styles (e.g., `focus-visible:ring-2`) and layout styles (like `w-full text-left` to match previous `<div>` block layouts) to maintain design intent while restoring accessibility.
## 2026-09-24 - Prevent Inputs While Simulating\n**Learning:** The simulation process blocks user interaction with a visual indicator, but screen readers need explicit `role="log"` and `aria-live="polite"` on the output terminal to properly hear updates. Visual disabled states like `disabled:opacity-50` and `disabled:cursor-not-allowed` should be applied on both buttons and textareas.\n**Action:** Always pair visual disabled states with programmatic disabled states and explicitly announce real-time updates for screen readers.

## 2024-10-24 - Loading State Accessibility
**Learning:** Adding a visual spinner to a button during a simulated long-running operation is good UX, but screen readers also need to know the state is busy.
**Action:** Always add `aria-busy={true}` to elements when they are in a loading state, in addition to visual indicators like spinners.
## 2024-05-24 - Explain Disabled States
**Learning:** Users can feel stuck when primary action buttons (like "Execute" or "Clear") are disabled without any explanation of *why* they cannot be clicked. The terminal app interface relies heavily on user input state to determine button availability.
**Action:** Always provide a native `title` attribute (or a custom tooltip component) on disabled buttons to explain exactly what the user needs to do to enable the action, converting a point of friction into a helpful guide.

## 2026-10-06 - Terminal Shortcuts Accessibility
**Learning:** Discovered that terminal-like textareas (e.g., prompt inputs) require both a clear visual hint and an accessible shortcut (like Ctrl/Cmd + Enter) to submit, as standard users and power users rely heavily on keyboards in these contexts. Adding a visible hint inside the label is hidden from screen readers via `aria-hidden="true"` as they often mispronounce symbols like ⌘, which is standard practice.
**Action:** Always provide keyboard shortcuts for primary actions in terminal/code-editor interfaces, and ensure the shortcut hint is visually present and semantically associated with the input's label.

## 2026-10-07 - Auto-scrolling in Real-time Terminals
**Learning:** Real-time log feeds and simulated terminals create immediate UX friction if they overflow their container without auto-scrolling. Users lose context and have to manually scroll continuously, which violates basic expectations for terminal-like interfaces.
**Action:** Always inject a bottom sentinel ref (`terminalEndRef`) and use a `useEffect` hook tied to the log state array to automatically trigger `scrollIntoView()` whenever new content is appended to dynamic feeds.

## 2026-10-08 - Character Limits on Textareas
**Learning:** Found that long-running simulated systems require user input constraints to prevent unexpected memory or processing issues, and users need to know those limits. Textareas with character limits must provide accessible feedback using `aria-describedby` linked to a live character count.
**Action:** Always add `maxLength` to textareas representing complex inputs, and implement a visual character count element that is programmatically associated via `aria-describedby` to ensure screen reader users are aware of the limit and their current progress.

## 2026-10-09 - Code Block Copy Button
**Learning:** Developer-focused interfaces with code snippets greatly benefit from a quick 'Copy' button. These buttons must be keyboard accessible (focus-visible) and provide screen reader feedback (aria-live) when the copy action is completed, otherwise the action is invisible to AT.
**Action:** Always wrap code blocks with a relative container and add an accessible, focusable copy button that provides immediate text feedback.
