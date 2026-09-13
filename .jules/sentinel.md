## 2026-09-10 - [Gitleaks PR Scanning Needs Explicit Permissions]
**Vulnerability:** N/A (Tooling issue)
**Learning:** The Gitleaks GitHub Action workflow requires explicit `permissions` for `contents: read` and `pull-requests: read` to avoid 403 'Resource not accessible by integration' errors when scanning pull requests.
**Prevention:** Always explicitly define required permissions block in GitHub Actions workflows, especially those involving automated PR checks.
## 2023-10-27 - [Hardcoded Database Credentials]
**Vulnerability:** Hardcoded database credentials were used as fallbacks in configuration files (`sccs-ace-platform/backend/server.js`, `sccs-ace-platform/backend/modules/scheduler/queue.js`, and `sccs-ace-platform/sccs_core/posp_consensus.py`).
**Learning:** Hardcoding credentials as fallbacks can easily lead to exposing secrets in public repositories. Using environment variables explicitly without default strings containing credentials is safer.
**Prevention:** Ensure that sensitive information like database URLs, API keys, and passwords are only accessed via environment variables and never hardcoded in the source code.
