## 2024-09-14 - Missing Form Labels
**Learning:** Found that custom form controls (like `<select>` and `<textarea>`) in the SCCS platform lacked proper `<label>` associations, impacting screen reader compatibility and click-to-focus behavior.
**Action:** Always ensure custom or native form inputs are explicitly linked to a `<label>` using `htmlFor` and `id` attributes.
