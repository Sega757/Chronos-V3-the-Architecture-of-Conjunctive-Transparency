## 2026-09-10 - [Gitleaks PR Scanning Needs Explicit Permissions]
**Vulnerability:** N/A (Tooling issue)
**Learning:** The Gitleaks GitHub Action workflow requires explicit `permissions` for `contents: read` and `pull-requests: read` to avoid 403 'Resource not accessible by integration' errors when scanning pull requests.
**Prevention:** Always explicitly define required permissions block in GitHub Actions workflows, especially those involving automated PR checks.
## 2024-05-24 - [Information Disclosure] Prevent Exposing Raw Error Messages
**Vulnerability:** The API endpoints in `sccs-ace-platform/backend/server.js` directly returned raw database error messages (`err.message`) to clients, potentially exposing sensitive database schema, queries, or internals.
**Learning:** Returning unhandled or raw exceptions from the database or other internal services directly to the client is a significant information disclosure risk. Attackers can use this information to map out the backend system or construct targeted attacks like SQL injection.
**Prevention:** Always log the full error details internally (e.g., using `console.error`) and return a generic, safe error message to the client, such as "Internal server error".
## 2024-05-15 - [CRITICAL] Hardcoded Secrets Fallback
**Vulnerability:** Found hardcoded database credentials (`postgresql://sccs_user:sccs_password@postgres:5432/sccs_db`) used as fallbacks for missing environment variables in backend queue workers, API server configuration, and consensus core engine.
**Learning:** Fallbacks can inadvertently leak secrets in version control. Even if intended for local development, they present a significant security risk if the codebase is exposed or shared.
**Prevention:** Strictly enforce that secrets must be provided via environment variables (e.g. throwing an error if the variable is missing) rather than supplying default sensitive strings.
