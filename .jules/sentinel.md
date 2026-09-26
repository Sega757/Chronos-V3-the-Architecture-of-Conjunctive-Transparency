## 2026-09-10 - [Gitleaks PR Scanning Needs Explicit Permissions]
**Vulnerability:** N/A (Tooling issue)
**Learning:** The Gitleaks GitHub Action workflow requires explicit `permissions` for `contents: read` and `pull-requests: read` to avoid 403 'Resource not accessible by integration' errors when scanning pull requests.
**Prevention:** Always explicitly define required permissions block in GitHub Actions workflows, especially those involving automated PR checks.
## 2024-05-24 - [Information Disclosure] Prevent Exposing Raw Error Messages
**Vulnerability:** The API endpoints in `sccs-ace-platform/backend/server.js` directly returned raw database error messages (`err.message`) to clients, potentially exposing sensitive database schema, queries, or internals.
**Learning:** Returning unhandled or raw exceptions from the database or other internal services directly to the client is a significant information disclosure risk. Attackers can use this information to map out the backend system or construct targeted attacks like SQL injection.
**Prevention:** Always log the full error details internally (e.g., using `console.error`) and return a generic, safe error message to the client, such as "Internal server error".
## 2024-05-24 - [Hardcoded Database Credentials]
**Vulnerability:** Found hardcoded database credentials used as fallbacks in configuration when environment variables were not present.
**Learning:** Hardcoded credentials even as a fallback create a significant security risk and can lead to unauthorized access if pushed to a repository.
**Prevention:** Always rely strictly on environment variables or secure credential stores for configuring sensitive connections like database URLs. Throw an error if they are missing to fail securely.
