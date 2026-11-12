# stitch

A modular web analysis framework for authorized security testing.

`stitch` crawls a target within a defined scope, maps its attack surface, and
probes for common web vulnerabilities. It bundles reconnaissance helpers
(security header audit, technology fingerprinting, port scan, TLS inspection),
an interactive menu, a flag-based CLI, and optional integrations with `nmap`,
`sqlmap`, and `nuclei` when they are installed on your system.

![python](https://img.shields.io/badge/python-3.11%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)
![status](https://img.shields.io/badge/status-active-brightgreen)

---

## Authorized use only

`stitch` is a security testing tool. Use it **only** against systems you own or
have **explicit written permission** to test. Unauthorized scanning and
exploitation is illegal in most jurisdictions (CFAA in the US, CMA in the UK,
and equivalents worldwide).

The maintainers assume **no liability** for misuse. If you are unsure whether
you have permission, you do not have permission.

Recommended legal practice:

- Get written authorization that names the target, the scope, and the time window.
- Test against your own lab first:
  - [OWASP Juice Shop](https://owasp.org/www-project-juice-shop/)
  - [DVWA](https://github.com/digininja/DVWA)
  - [PortSwigger Web Security Academy](https://portswigger.net/web-security)
- Report findings responsibly.

---

## Features

### Scanner

- Scoped crawler (host + subdomains), form and parameter extraction
- SQL injection: error-based and boolean differential
- Reflected XSS
- Local file inclusion (LFI)
- Server-side template injection (SSTI) — polyglot probes
- XML external entity (XXE) on POST forms
- Open redirect
- SSRF (opt-in, requires external responder)
- Command injection (timing differential, non-destructive)
- Concurrent crawler and engine (configurable worker count)
- Findings cache (dedupe across runs)

### Reconnaissance

- Security header audit (HSTS, CSP, X-Frame-Options, etc.)
- Technology fingerprinting (WordPress, Laravel, Django, nginx, React, jQuery, ...)
- Common port scan (TCP connect, 17 services)
- TLS certificate inspection (subject, issuer, expiry)
- Optional `nmap` integration (`-sV` scan) if installed

### Integrations (optional, auto-detected)

- `nmap` — deeper port scan with service detection
- `sqlmap` — confirm SQL injection findings
- `nuclei` — run community templates against the target
- Each is skipped if the binary is not found on `PATH`

### Interface

- Interactive numbered menu (persists across actions)
- Flag-based CLI for scripting / CI
- Terminal banner + boot animation
- Optional Tkinter intro animation
- Session auth (cookie + custom header) shared across menu actions
- Config persistence (remembers last URL, scope, and menu defaults)
- JSON report output
- `--version` flag

---

## Table of contents

1. [Installation](#installation)
2. [Quick start](#quick-start)
3. [Interactive mode tutorial](#interactive-mode-tutorial)
4. [CLI mode tutorial](#cli-mode-tutorial)
5. [Integrations](#integrations)
6. [Configuration](#configuration)
7. [How it works](#how-it-works)
8. [Report format](#report-format)
9. [What it does *not* do](#what-it-does-not-do)
10. [Troubleshooting](#troubleshooting)
11. [Contributing](#contributing)
12. [License](#license)

---

## Installation

### Requirements

- **Python 3.11+**
- `pip`
- Optional: `nmap`, `sqlmap`, `nuclei` on `PATH` for integrations
- Optional: Tkinter (`python3-tk` on Debian/Ubuntu) for the intro animation

### Steps

```bash
# 1. clone
git clone https://github.com/<you>/stitch.git
cd stitch

# 2. virtualenv
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

# 3. deps
pip install -r requirements.txt

# 4. install as editable command (optional but recommended)
pip install -e .
