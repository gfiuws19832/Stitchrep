# stitch

A modular web analysis framework for authorized security testing.

`stitch` crawls a target within a defined scope, maps its attack surface, and probes for common web vulnerabilities. It also bundles reconnaissance helpers: security header audit, technology fingerprinting, common port scan, and TLS certificate inspection.

![python](https://img.shields.io/badge/python-3.11%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)

---

## ⚠️ Authorized use only

`stitch` is a security testing tool. Use it **only** against systems you own or have **explicit written permission** to test. Unauthorized scanning and exploitation is illegal in most jurisdictions (Computer Fraud and Abuse Act in the US, Computer Misuse Act in the UK, and equivalents worldwide).

The maintainers assume **no liability** for misuse. If you are unsure whether you have permission, you do not have permission.

Recommended legal practice:
- Get written authorization that names the target, the scope, and the time window.
- Test against your own lab first: [OWASP Juice Shop](https://owasp.org/www-project-juice-shop/), [DVWA](https://github.com/digininja/DVWA), [PortSwigger Web Security Academy](https://portswigger.net/web-security).
- Report findings responsibly.

---

## Features

**Scanner**
- Scoped crawler (host + subdomains), form and parameter extraction
- SQL injection: error-based and boolean differential
- Reflected XSS
- Local file inclusion (LFI)
- Server-side template injection (SSTI) — polyglot probes
- XML external entity (XXE) on POST forms
- Open redirect
- SSRF (opt-in, requires external responder)
- Command injection (timing differential, non-destructive)

**Reconnaissance**
- Security header audit (HSTS, CSP, X-Frame-Options, etc.)
- Technology fingerprinting (WordPress, Laravel, Django, nginx, React, jQuery, ...)
- Common port scan (TCP connect, 17 services)
- TLS certificate inspection (subject, issuer, expiry)

**Interface**
- Interactive menu (numbered options)
- Flag-based CLI for scripting
- Terminal banner + boot animation
- Optional Tkinter intro animation
- Session auth (cookie + custom header) shared across menu actions
- JSON report output

---

## Installation

```bash
git clone https://github.com/<you>/stitch.git
cd stitch
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
