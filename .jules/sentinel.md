## 2026-09-10 - [Gitleaks PR Scanning Needs Explicit Permissions]
**Vulnerability:** N/A (Tooling issue)
**Learning:** The Gitleaks GitHub Action workflow requires explicit `permissions` for `contents: read` and `pull-requests: read` to avoid 403 'Resource not accessible by integration' errors when scanning pull requests.
**Prevention:** Always explicitly define required permissions block in GitHub Actions workflows, especially those involving automated PR checks.
## 2026-09-14 - [React Component `src` XSS in renderer]
**Vulnerability:** The application was vulnerable to Stored XSS because dynamic `block.content` was directly injected into the `src` attribute of `<img>` and `<iframe>` components without URI scheme validation. This allows `javascript:`, `vbscript:`, and `data:text/html` payloads to be executed in the client browser.
**Learning:** React escapes HTML entities, but it does NOT validate URI schemes in elements where `src` or `href` attributes are used, meaning developers must manually sanitize them.
**Prevention:** Always use a URI sanitization wrapper function when rendering user-supplied or dynamic input into interactive attributes like `src` or `href`.
