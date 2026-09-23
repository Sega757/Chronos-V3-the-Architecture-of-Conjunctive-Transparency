## 2026-09-10 - [Gitleaks PR Scanning Needs Explicit Permissions]
**Vulnerability:** N/A (Tooling issue)
**Learning:** The Gitleaks GitHub Action workflow requires explicit `permissions` for `contents: read` and `pull-requests: read` to avoid 403 'Resource not accessible by integration' errors when scanning pull requests.
**Prevention:** Always explicitly define required permissions block in GitHub Actions workflows, especially those involving automated PR checks.
## 2024-05-24 - [Information Disclosure] Prevent Exposing Raw Error Messages
**Vulnerability:** The API endpoints in `sccs-ace-platform/backend/server.js` directly returned raw database error messages (`err.message`) to clients, potentially exposing sensitive database schema, queries, or internals.
**Learning:** Returning unhandled or raw exceptions from the database or other internal services directly to the client is a significant information disclosure risk. Attackers can use this information to map out the backend system or construct targeted attacks like SQL injection.
**Prevention:** Always log the full error details internally (e.g., using `console.error`) and return a generic, safe error message to the client, such as "Internal server error".
## 2024-05-24 - [Fix hardcoded database credentials]
**Vulnerability:** Hardcoded database connection credentials containing plain-text password (`postgresql://sccs_user:sccs_password@...`) existed as a fallback in backend codebase.
**Learning:** Found in `server.js` and `modules/scheduler/queue.js`. Always verify connection configurations for environment fallback handling to prevent committing plain text credentials.
**Prevention:** Remove hardcoded credentials from logic; instead enforce environment variables and use a 'fail-fast' startup mechanism if critical keys/credentials are missing.
