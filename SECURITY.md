# Security Policy 🔒

We take the security of Shiny Fishstick seriously. Because our tools handle sensitive web credentials, cookies, and localStorage session data, protecting contributor and user environments is a top priority.

## Reporting a Vulnerability

Do **not** open a public GitHub issue for security vulnerabilities. Instead, please report any security issues by emailing us privately at **adityapdixit2006@gmail.com**.

We will review your submission and respond within 48 hours to coordinate a security patch.

## Sensitive Data Guidelines

If you are contributing to our crawler or database engines, please be aware:
1.  **Session Indicators**: Never commit or push database files containing active session storage indicators, passwords, or decrypted credentials parameters.
2.  **Encryption Protection**: All database storage of authentication tokens, cookies, and localstorage values must utilize standard `security.py` cryptography layers.
3.  **No Logs for Secrets**: Credentials, API tokens, and proxy secrets must never be routed to standard logs or console outputs.
