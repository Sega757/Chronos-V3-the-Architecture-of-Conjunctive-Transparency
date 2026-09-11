## 2026-09-11 - Configurable Simulation Delays in Next.js UI
**Problem:** Artificial `setTimeout` delays during UI simulation runs cause unnecessary waiting during automated testing or interactive workflows.
**Learning:** Making step delays configurable via state (defaulting to 0ms instant mode) bypasses blocking delays without breaking state machine transitions or visual UI consistency.
**Prevention:** Avoid hardcoded blocking delays in UI simulation routines; provide an instant execution path by default or make delays configurable through state/props.
