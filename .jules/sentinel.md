## 2026-09-10 - [Gitleaks PR Scanning Needs Explicit Permissions]
**Vulnerability:** N/A (Tooling issue)
**Learning:** The Gitleaks GitHub Action workflow requires explicit `permissions` for `contents: read` and `pull-requests: read` to avoid 403 'Resource not accessible by integration' errors when scanning pull requests.
**Prevention:** Always explicitly define required permissions block in GitHub Actions workflows, especially those involving automated PR checks.
## 2024-05-24 - [Information Disclosure] Prevent Exposing Raw Error Messages
**Vulnerability:** The API endpoints in `sccs-ace-platform/backend/server.js` directly returned raw database error messages (`err.message`) to clients, potentially exposing sensitive database schema, queries, or internals.
**Learning:** Returning unhandled or raw exceptions from the database or other internal services directly to the client is a significant information disclosure risk. Attackers can use this information to map out the backend system or construct targeted attacks like SQL injection.
**Prevention:** Always log the full error details internally (e.g., using `console.error`) and return a generic, safe error message to the client, such as "Internal server error".
## 2026-09-29 - [Remove Hardcoded Passwords in Source Code]
**Vulnerability:** Hardcoded database credentials (including the password 'sccs_password') were present as fallback values in several files across the backend and core services (queue.js, server.js, posp_consensus.py).
**Learning:** Providing hardcoded credentials as fallbacks for environment variables is a critical security risk. If the environment variable fails to load, the application will attempt to connect using these hardcoded, potentially production credentials, which could be exposed in version control.
**Prevention:** Remove hardcoded credentials from the source code. If an environment variable is required for execution, fail fast with a descriptive error message instead of providing an insecure default.
## 2026-10-02 - [Type Confusion / Missing Input Validation]
**Vulnerability:** The backend API endpoints (`/api/generate`, `/api/verify`) lacked proper validation and sanitization for `req.body` parameters, leading to potential type confusion vulnerabilities and unchecked string limits when processing jobs.
**Learning:** Backend API endpoints must validate and sanitize all input parameters before passing them to internal queues or gRPC services. Unvalidated inputs can cause unexpected behavior or Denial of Service (DoS) if large payloads are handled improperly.
**Prevention:** Always enforce strict type checks (e.g. ensuring expected variables are strings) and enforce sensible length constraints to prevent unexpected backend type errors and abuse.
