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
## 2026-10-15 - [Stored XSS] Prevent Arbitrary Execution via Element src attributes
**Vulnerability:** The application rendered dynamic article content using `<img>` and `<iframe>` tags in `frontend/lib/renderer.tsx`, where the `src` attribute was populated directly from user-controlled database inputs (`block.content`) without validation.
**Learning:** If user input is passed directly to a `src` attribute, an attacker can supply malicious URIs like `javascript:alert(1)` for images or completely arbitrary pages for iframes. These Stored XSS vectors would execute directly within the viewer's context without needing `dangerouslySetInnerHTML`.
**Prevention:** Always sanitize URLs intended for `src` or `href` attributes. For images, ensure they use `http://` or `https://` schemas. For embedded objects like iframes, enforce strict domain allow-listing (e.g. `https://www.youtube.com/embed/`) to prevent unauthorized content or scripts from loading.
## 2026-10-24 - [Defense-in-Depth] HTTP Security Headers
**Vulnerability:** The Express backend lacked comprehensive HTTP security headers, leaving it potentially exposed to clickjacking, MIME-sniffing, and other web-based attacks.
**Learning:** Even if an API is intended primarily for a specific frontend, applying standard security headers is a critical defense-in-depth measure. Relying on default Express settings omits essential browser protections.
**Prevention:** Always implement `helmet` or equivalent middleware in Express applications to automatically configure robust baseline HTTP security headers.
## 2026-11-04 - [Missing Rate Limits on Resource Intensive Endpoints]
**Vulnerability:** The POST endpoints `/api/generate` and `/api/verify` trigger expensive downstream processing (like gRPC ML/LLM services or worker queues) but had no rate limiting.
**Learning:** Missing rate limits on resource-intensive endpoints can allow an attacker to cause Denial of Service (DoS) and queue starvation, severely impacting application availability and infrastructure costs.
**Prevention:** Always implement rate limiting on sensitive, state-mutating, or resource-heavy endpoints (like those creating tasks or communicating with heavy services) to limit each IP or user to a safe number of requests per window.
## 2026-11-20 - [Missing Authentication on Admin Endpoints]
**Vulnerability:** The `/api/logs` endpoint, which exposed sensitive generation logs (including raw user prompts and internal model execution details), was completely unauthenticated and publicly accessible.
**Learning:** Administrative and diagnostic API routes must never assume they are hidden or inaccessible simply because they aren't directly linked in the main UI. Attackers often enumerate standard administrative paths (`/api/logs`, `/api/admin`, etc.) to find unprotected sensitive data.
**Prevention:** Always enforce strict authentication and authorization checks (e.g., API keys, robust session validation) on endpoints that return sensitive application internals, logs, or administrative controls. Apply a default-deny mindset for data exposure.
