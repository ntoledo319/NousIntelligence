# Security Policy

The NOUS team takes security seriously. We appreciate your efforts to responsibly disclose your findings, and will make every effort to acknowledge your contributions.

## Supported Versions

Only the latest major version of NOUS receives security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0.0 | :x:                |

## Reporting a Vulnerability

To report a security vulnerability, please send an email to `security@example.com` with the subject line "SECURITY: Vulnerability in NOUS".

**Please do not report security vulnerabilities through public GitHub issues.**

You should receive an initial response within 48 hours. We will keep you informed of the progress towards a fix and full announcement.

## Disclosure Timeline

1.  **Initial Report:** You send a detailed report to `security@example.com`.
2.  **Confirmation:** We confirm the vulnerability within 2 business days.
3.  **Update:** We provide a status update every 5 business days.
4.  **Resolution:** We release a patch and notify you.
5.  **Public Disclosure:** We publish a security advisory after the patch is released.

## Secret Handling

-   **NEVER** commit secrets (API keys, passwords, client secrets) to the repository.
-   All secrets must be managed through Replit Secrets or a local `.env` file for development.
-   The application loads all secrets from environment variables. Refer to `ENV_VARS.md` for a complete list.
-   When adding a new integration, ensure its secrets are loaded from the environment and documented in `ENV_VARS.md`. 