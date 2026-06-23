# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 2.2.x   | ✅ Active support   |
| 2.1.x   | ⚠️ Critical fixes only |
| < 2.0   | ❌ No longer supported |

## Reporting a Vulnerability

We take security seriously. If you discover a vulnerability in Memora, please report it responsibly.

### How to Report

1. **Do NOT** open a public GitHub issue for security vulnerabilities.
2. Email your findings to the maintainer with the subject line: **`[SECURITY] Memora Vulnerability Report`**
3. Include the following details:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact assessment
   - Suggested fix (if any)

### What to Expect

- **Acknowledgment**: Within 48 hours of your report
- **Assessment**: We will evaluate the severity within 5 business days
- **Resolution**: Critical vulnerabilities will be patched within 7 days
- **Disclosure**: We will coordinate responsible disclosure with you

## Security Measures

Memora implements the following security controls:

### Authentication & Authorization
- **PBKDF2-SHA256** password hashing with 100,000 iterations and random salt
- **HMAC-SHA256** JWT tokens with configurable expiry (24h default)
- Per-endpoint authentication via FastAPI dependency injection

### API Hardening
- **Rate limiting**: Sliding window counter (60 req/min per IP)
- **Input validation**: Pydantic field constraints with max lengths and regex patterns
- **CORS**: Restricted to explicitly allowed origins
- **Security headers**: X-Content-Type-Options, X-Frame-Options, HSTS, Referrer-Policy, Permissions-Policy

### Data Protection
- SQLite database excluded from version control via `.gitignore`
- Environment secrets loaded from `.env` (never committed)
- No PII logged in application logs

## Known Considerations

> ⚠️ **JWT Secret**: The default `SECRET_KEY` in `app/auth.py` is a placeholder.  
> **You MUST change it** before deploying to production. Use a cryptographically random value:
> ```python
> import secrets
> print(secrets.token_hex(32))
> ```

> ⚠️ **SQLite**: Not recommended for production multi-user deployments.  
> Consider PostgreSQL or MySQL for concurrent access patterns.

## Dependencies

We monitor dependencies for known vulnerabilities. Run `pip audit` to check:

```bash
pip install pip-audit
pip-audit -r requirements.txt
```
