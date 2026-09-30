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

## 2024-05-18 - [Missing Input Validation on Express Endpoints]
**Vulnerability:** Found missing input validation for `POST /api/generate` and `POST /api/verify` in the Express backend, potentially allowing excessive payloads that could cause Denial of Service (DoS) in queues/memory.
**Learning:** In Express apps without strict built-in schema validation, it is critical to manually check payload types and enforce string length limits on incoming data, especially for fields appended to job queues (e.g., BullMQ) and RPC calls.
**Prevention:** Always validate `req.body` parameters for type and size constraints before passing them to internal queues or gRPC services. Implement schema-based validation libraries (like Joi or Zod) for more scalable prevention in the future.
