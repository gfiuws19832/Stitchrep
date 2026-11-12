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
```

After step 4 you can run `stitch` directly from anywhere inside the venv.

### Verify the install

```bash
python -m stitch --version
```

Expected output:

```
stitch 0.2.0
```

### Windows note

If `python` is not recognized, use `py` instead:

```powershell
py -m stitch --version
```

If `lxml` fails to compile (rare on Windows), the code falls back to
`html.parser` automatically — no action needed.

---

## Quick start

```bash
# interactive menu (recommended first time)
python -m stitch

# CLI: quick scan, findings to stdout
python -m stitch -u https://example.com --scope example.com

# CLI: full scan with JSON report
python -m stitch -u https://example.com --scope example.com --report out.json

# CLI: recon only (headers + tech + ports + TLS)
python -m stitch -u https://example.com --scope example.com --recon
```

---

## Interactive mode tutorial

Run:

```bash
python -m stitch
```

You will see the boot animation, the banner, and this menu:

```
  ┌──────────────────────────────────────────────────────┐
  │  ESCANER WEB                                          │
  │  1  Analisis rapido (findings a pantalla)             │
  │  2  Analisis completo (+ reporte JSON)                │
  │  3  Analisis con SSRF                                 │
  │  4  Solo crawling                                     │
  │  RECONOCIMIENTO                                       │
  │  5  Cabeceras de seguridad                            │
  │  6  Detectar tecnologia                               │
  │  7  Escaneo de puertos comunes                        │
  │  8  Certificado TLS                                   │
  │  9  Reconocimiento completo (5+6+7+8)                 │
  │  INTEGRACIONES                                        │
  │  12 nmap - servicio y version                         │
  │  13 sqlmap - confirmar SQLi                           │
  │  14 nuclei - templates de la comunidad                │
  │  HERRAMIENTAS                                         │
  │  10 Autenticacion (cookie/header)                     │
  │  11 Modo avanzado (flags)                             │
  │  0  Salir                                             │
  └──────────────────────────────────────────────────────┘

  elige una opcion:
```

### First run: reconnaissance

Type `9` and press Enter. The tool asks for the URL:

```
  URL (https://...): https://example.com
```

Press Enter on a defaulted field to accept it. The tool runs headers,
technology fingerprinting, port scan, and TLS inspection, then pauses:

```
  ── cabeceras de seguridad ──
  [+] Strict-Transport-Security: HSTS: forces HTTPS...
  [-] Content-Security-Policy absent: CSP: restricts script origins...
  ...

  Enter para volver al menu...
```

Read the output, press Enter, and you're back at the menu.

### Second run: full scan with report

Type `2`. Fill in the URL, the scope (defaults to the URL's host), the report
path (defaults to `out.json`), and the page cap (defaults to 200). The tool
shows a summary and asks to confirm:

```
  ── resumen ──
  url:        https://example.com
  scope:      example.com
  max pages:  200
  reporte:    out.json

  empezar (s/n) [s]:
```

Press `s`. The crawler runs, then the engine probes each parameter. When it
finishes, `out.json` lands in the current directory.

### Authenticated targets

Type `10` before scanning. The tool asks for a cookie and an optional header:

```
  cookie (nombre=valor, vacio para ninguna): session=abc123
  header extra (nombre, vacio para ninguno): Authorization
  valor para Authorization: Bearer eyJ...
```

Both are stored on the shared session and applied to every subsequent action
in the menu (scan, recon, integrations). No need to re-enter them.

### Everything loops

The menu runs in a loop. You can do recon, then authenticate, then scan, then
run `nuclei`, without restarting. Press `0` to exit.

---

## CLI mode tutorial

CLI mode is for scripting and CI. Every action in the menu has a flag.

### Scan

```bash
python -m stitch \
  -u https://example.com \
  --scope example.com \
  --report out.json \
  --max-pages 300 \
  --timeout 20
```

- `-u` / `--url` — required
- `--scope` — required, the allowed host suffix
- `--report` — write JSON here (omit for stdout)
- `--max-pages` — cap the crawler (default 200)
- `--timeout` — per-request seconds (default 15)

### With SSRF

SSRF is opt-in because it needs an external responder you control:

```bash
python -m stitch \
  -u https://example.com \
  --scope example.com \
  --report out.json \
  --ssrf-canary https://your-responder.tld/hw-canary
```

Set up a responder first (Burp Collaborator, interactsh, or a VPS listener).
If the responder log shows a hit on `/hw-canary`, the SSRF is real.

### Recon only

```bash
python -m stitch -u https://example.com --scope example.com --recon
```

Runs headers, tech, ports, and TLS. Prints a summary. Does not touch the
detection engine.

### Concurrent scan

```bash
python -m stitch -u https://example.com --scope example.com --workers 8
```

Crawler and engine run across 8 threads. Faster on large sites; the target
sees more parallel requests. Use with care on shared infrastructure.

### Confirm SQLi with sqlmap

```bash
python -m stitch -u "https://example.com/?id=1" --scope example.com --confirm-sqli
```

Requires `sqlmap` on `PATH`. Runs `sqlmap -u <url> --batch --level 1 --risk 1`
and prints the verdict.

### Run nuclei

```bash
python -m stitch -u https://example.com --scope example.com --nuclei
```

Requires `nuclei` on `PATH`. Runs the default template set against the target
and prints the output.

### Run nmap

```bash
python -m stitch -u https://example.com --scope example.com --nmap
```

Requires `nmap` on `PATH`. Runs `nmap -sV -T4 --top-ports 100 <host>`.

### Skip the intro

```bash
STITCH_NO_INTRO=1 python -m stitch ...
```

Or set it permanently in your shell profile.

---

## Integrations

`stitch` shells out to external tools **only if they are installed**. It does
not bundle them, and it does not download them.

| Tool | Detected by | Used for |
|------|-------------|----------|
| `nmap` | `which nmap` | `-sV` service scan (menu 12, `--nmap`) |
| `sqlmap` | `which sqlmap` | confirm SQLi findings (menu 13, `--confirm-sqli`) |
| `nuclei` | `which nuclei` | run community templates (menu 14, `--nuclei`) |

If a tool is not on `PATH`, `stitch` prints a short note and skips the action.

### Installing the integrations (optional)

- **nmap**: https://nmap.org/download
- **sqlmap**: `pip install sqlmap` or `git clone https://github.com/sqlmapproject/sqlmap`
- **nuclei**: https://github.com/projectdiscovery/nuclei/releases

Install them only if you know how to use them responsibly. `stitch` invokes
them with conservative defaults (`--batch`, `--level 1`, default templates),
but those tools are powerful on their own.

---

## Configuration

`stitch` stores the last used URL, scope, report path, and worker count in:

- Linux/macOS: `~/.config/stitch/config.json`
- Windows: `%APPDATA%\stitch\config.json`

The menu pre-fills those values. You can delete the file to reset.

You can also point to a custom config:

```bash
STITCH_CONFIG=/path/to/config.json python -m stitch
```

---

## How it works

1. **Crawler** — BFS from the start URL, staying inside `--scope`. Extracts
   URLs with query parameters and HTML forms. Non-HTML responses are skipped.
   Runs concurrently if `--workers > 1`.
2. **Engine** — For each parameter, runs the detectors listed in *Features*.
   Findings are classified by `severity` (`critical`/`high`/`medium`/`low`) and
   `confidence` (`confirmed` = direct evidence; `probable` = differential or
   timing — confirm manually).
3. **Dedupe** — Findings are hashed on `(url, param, kind, payload)`. Duplicates
   across runs are dropped by the cache.
4. **Report** — Sorted by severity, written as JSON.

---

## Report format

```json
{
  "generated": "2026-05-12T14:22:07Z",
  "count": 3,
  "findings": [
    {
      "url": "https://example.com/product?id=1",
      "param": "id",
      "kind": "sqli",
      "evidence": "SQL syntax error",
      "severity": "high",
      "confidence": "confirmed",
      "payload": "'"
    },
    {
      "url": "https://example.com/search?q=test",
      "param": "q",
      "kind": "xss",
      "evidence": "reflected unescaped",
      "severity": "medium",
      "confidence": "confirmed",
      "payload": "<svg/onload=alert('hw1a2b3c')>"
    }
  ]
}
```

| Field | Meaning |
|-------|---------|
| `kind` | `sqli`, `xss`, `lfi`, `ssti`, `xxe`, `open_redirect`, `ssrf`, `cmdi` |
| `severity` | `critical`, `high`, `medium`, `low` |
| `confidence` | `confirmed` (direct evidence), `probable` (needs manual confirmation) |
| `payload` | The exact string sent |
| `evidence` | What was observed in the response |

---

## What it does *not* do

Being honest matters more than marketing:

- **No WAF evasion.** Sends plain HTTP requests. A WAF will block or ban it.
- **No exploitation.** Does not dump databases, open shells, or escalate. It
  detects; exploitation is manual (`sqlmap -r`, Burp, etc.).
- **No authenticated flows beyond a single cookie.** For complex auth flows
  (multi-step, CSRF, SAML), use Burp.
- **Not a replacement for Burp Suite, ZAP, nuclei, or sqlmap.** It's a
  first-pass mapping tool, not a commercial scanner.

If you need any of those, use the mature tool. `stitch` is for understanding
the flow and doing a quick surface pass.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `python: command not found` | Python not on PATH | Use `py` on Windows, or reinstall Python with "Add to PATH" |
| `ModuleNotFoundError: requests` | Deps not installed | `pip install -r requirements.txt` |
| `ModuleNotFoundError: tkinter` | Python built without Tcl/Tk | Reinstall Python with tcl/tk, or run with `STITCH_NO_INTRO=1` |
| `lxml` fails to compile | Missing build tools | `pip install --only-binary :all: lxml` (fallback to `html.parser` is automatic) |
| Menu shows weird characters | CMD without UTF-8 | Use Windows Terminal, or `chcp 65001` first |
| `nmap` integration skipped | `nmap` not on PATH | Install nmap, or use the built-in port scan (menu 7) |
| Findings have many `probable` | Detection is heuristic | Confirm manually with Burp or `sqlmap -r` |

---

## Contributing

Pull requests welcome for detectors, recon modules, report formats, and
integration wrappers. Keep modules small and testable.

### Running tests

```bash
pip install -e ".[dev]"
pytest
```

### Code style

```bash
ruff check .
ruff format .
```

### Adding a detector

1. Add a method to `stitch/engine.py`, following the existing pattern:
   return a `Finding` via `self._mark(...)`.
2. Register it in `Engine.run`.
3. Add a test in `tests/test_engine.py`.
4. Update the feature list and the report format docs above.

---

## License

MIT — see [LICENSE](#license-file).

## Credits

- Banner and Tkinter intro animation by **zstchy**.
- Inspired by the work of the PortSwigger, ProjectDiscovery, and sqlmap
  communities.

---

# Repository files

Below are all the files that make up the repository, ready to be copied into
their respective paths.

## Repository tree

```
stitch/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── pyproject.toml
├── stitch/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── intro.py
│   ├── banner.py
│   ├── session.py
│   ├── config.py
│   ├── crawler.py
│   ├── engine.py
│   ├── recon.py
│   ├── tools.py
│   ├── report.py
│   └── menu.py
├── tests/
│   └── test_engine.py
└── examples/
    └── targets.md
```

## `LICENSE`

```
MIT License

Copyright (c) 2026 zstchy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## `.gitignore`

```
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/
env/
build/
dist/
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.json
!examples/*.json
out.json
report*.json
.DS_Store
Thumbs.db
.idea/
.vscode/
```

## `requirements.txt`

```
requests>=2.31
beautifulsoup4>=4.12
lxml>=5.0
```

## `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "stitch"
version = "0.2.0"
description = "Modular web analysis framework for authorized security testing"
readme = "README.md"
requires-python = ">=3.11"
license = { text = "MIT" }
authors = [{ name = "zstchy" }]
dependencies = [
    "requests>=2.31",
    "beautifulsoup4>=4.12",
    "lxml>=5.0",
]

[project.scripts]
stitch = "stitch.cli:main"

[project.optional-dependencies]
dev = ["pytest>=7.4", "ruff>=0.4", "mypy>=1.10"]

[tool.setuptools.packages.find]
include = ["stitch*"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

## `stitch/__init__.py`

```python
"""stitch - modular web analysis framework for authorized security testing."""
__version__ = "0.2.0"
```

## `stitch/__main__.py`

```python
from .cli import main

if __name__ == "__main__":
    main()
```

## `stitch/session.py`

```python
"""HTTP session factory and shared defaults."""
import requests

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
TIMEOUT = 15.0


def build_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": UA})
    s.verify = True
    return s
```

## `stitch/config.py`

```python
"""Config persistence: remembers last URL, scope, report, workers."""
import json
import os
from pathlib import Path

_DEFAULT = {
    "last_url": None,
    "last_scope": None,
    "last_report": "out.json",
    "last_workers": 1,
}


def config_path() -> Path:
    override = os.environ.get("STITCH_CONFIG")
    if override:
        return Path(override)
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "stitch" / "config.json"


def load() -> dict:
    p = config_path()
    if not p.exists():
        return dict(_DEFAULT)
    try:
        with p.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        merged = dict(_DEFAULT)
        merged.update(data)
        return merged
    except (OSError, json.JSONDecodeError):
        return dict(_DEFAULT)


def save(data: dict) -> None:
    p = config_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        with p.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
    except OSError:
        pass
```

## `stitch/banner.py`

```python
"""Console banner, boot sequence, and startup animation."""
import os
import sys
import time

RED = "\33[91m"
PURPLE = "\033[0;35m"
GREEN = "\033[32m"
YELLOW = "\033[93m"
CYAN = "\033[36m"
RESET = "\033[0m"
BOLD = "\033[1m"

_BANNER_LINES = [
    (RED,    "   ███████╗████████╗██╗████████╗ ██████╗██╗  ██╗"),
    (PURPLE, "   ██╔════╝╚══██╔══╝██║╚══██╔══╝██╔════╝██║  ██║"),
    (RED,    "   ███████╗   ██║   ██║   ██║   ██║     ███████║"),
    (PURPLE, "   ╚════██║   ██║   ██║   ██║   ██║     ██╔══██║"),
    (RED,    "   ███████║   ██║   ██║   ██║   ╚██████╗██║  ██║"),
    (PURPLE, "   ╚══════╝   ╚═╝   ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝"),
]


def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def banner_text() -> str:
    return "\n".join(f"{c}{line}{RESET}" for c, line in _BANNER_LINES)


def boot_sequence() -> None:
    clear()
    lines = [
        (PURPLE, "[BOOT] initializing core..."),
        (PURPLE, "[BOOT] loading modules"),
        (PURPLE, "[BOOT] arming payloads"),
        (PURPLE, "[BOOT] scope guard online"),
        (RED,    "[OK]   all systems nominal"),
    ]
    for color, line in lines:
        sys.stdout.write(color)
        for ch in line:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(0.010)
        sys.stdout.write(RESET)
        print()
        time.sleep(0.15)
    time.sleep(0.35)


def draw_banner() -> None:
    clear()
    for color, line in _BANNER_LINES:
        sys.stdout.write(color + line + RESET + "\n")
        sys.stdout.flush()
        time.sleep(0.08)


def pulse(times: int = 2) -> None:
    for _ in range(times):
        for c in (RED, PURPLE):
            clear()
            print(banner_text())
            print(f"\n{BOLD}{c}        s t i t c h {RESET}")
            time.sleep(0.25)


def boot_banner() -> None:
    boot_sequence()
    draw_banner()
    time.sleep(0.4)
    pulse(times=2)
    clear()
    print(banner_text())
    print(f"\n{BOLD}{RED}        s t i t c h {RESET}\n")
```

## `stitch/intro.py`

```python
"""Tkinter intro animation, shown on startup unless disabled."""
import os


def run_intro() -> None:
    """Play the intro animation and return when it finishes."""
    if os.environ.get("STITCH_NO_INTRO"):
        return
    try:
        _play()
    except Exception:
        # intro is cosmetic; never block the scan on it
        pass


def _play() -> None:
    # --- paste the full body of the old run_intro() here ---
    # from "import math as m" through "root.mainloop()"
    ...
```

## `stitch/crawler.py`

```python
"""Scoped crawler: BFS over HTML pages, extracting URLs, params, forms."""
import sys
import urllib.parse as up
from dataclasses import dataclass, field

import requests

from .session import TIMEOUT

try:
    from bs4 import BeautifulSoup
    _HAS_BS4 = True
except ImportError:
    _HAS_BS4 = False


@dataclass
class Surface:
    urls: set = field(default_factory=set)
    forms: list = field(default_factory=list)
    params: dict = field(default_factory=dict)


class Crawler:
    def __init__(self, base: str, scope: str, session: requests.Session):
        self.base = base
        self.scope = scope
        self.s = session
        self.surface = Surface()
        self.seen: set = set()

    def in_scope(self, url: str) -> bool:
        host = up.urlparse(url).hostname or ""
        return host == self.scope or host.endswith("." + self.scope)

    def crawl(self, max_pages: int = 200, depth: int = 3) -> Surface:
        queue = [(self.base, 0)]
        while queue and len(self.seen) < max_pages:
            url, d = queue.pop(0)
            if url in self.seen or not self.in_scope(url):
                continue
            self.seen.add(url)
            try:
                r = self.s.get(url, timeout=TIMEOUT)
            except requests.RequestException:
                continue
            if "text/html" not in r.headers.get("content-type", ""):
                continue
            self.surface.urls.add(url)
            q = up.parse_qs(up.urlparse(url).query)
            if q:
                self.surface.params[url] = list(q.keys())
            if _HAS_BS4:
                soup = BeautifulSoup(r.text, "lxml" if "lxml" in sys.modules else "html.parser")
                for f in soup.find_all("form"):
                    action = up.urljoin(url, f.get("action") or url)
                    method = (f.get("method") or "GET").upper()
                    inputs = [(i.get("name"), i.get("type") or "text")
                              for i in f.find_all(["input", "textarea", "select"])
                              if i.get("name")]
                    self.surface.forms.append((action, method, inputs))
                if d < depth:
                    for a in soup.find_all("a", href=True):
                        nxt = up.urljoin(url, a["href"])
                        if self.in_scope(nxt) and nxt not in self.seen:
                            queue.append((nxt, d + 1))
        return self.surface
```

## `stitch/engine.py`

```python
"""Vulnerability detection engine."""
import hashlib
import re
import time
import urllib.parse as up
from dataclasses import dataclass

import requests

from .crawler import Surface
from .session import TIMEOUT


@dataclass
class Finding:
    url: str
    param: str
    kind: str
    evidence: str
    severity: str
    confidence: str
    payload: str = ""


class Engine:
    def __init__(self, session: requests.Session, scope: str):
        self.s = session
        self.scope = scope
        self.findings: list[Finding] = []

    def _mark(self, **kw):
        self.findings.append(Finding(**kw))

    def inject_param(self, url: str, param: str, payload: str) -> str:
        p = up.urlparse(url)
        q = up.parse_qs(p.query)
        q[param] = [payload]
        return up.urlunparse(p._replace(query=up.urlencode(q, doseq=True)))

    def sqli(self, url, param):
        err = re.compile(
            r"(SQL syntax|mysql_fetch|ORA-\d{4,5}|PostgreSQL.*ERROR|SQLite/JDBCDriver|Unclosed quotation mark)",
            re.I,
        )
        p1 = self.inject_param(url, param, "'")
        try:
            r1 = self.s.get(p1, timeout=TIMEOUT)
        except requests.RequestException:
            return
        m = err.search(r1.text)
        if m:
            self._mark(url=url, param=param, kind="sqli", evidence=m.group(0),
                       severity="high", confidence="confirmed", payload="'")
            return
        base = self.s.get(url, timeout=TIMEOUT)
        t = self.inject_param(url, param, "1' AND '1'='1")
        f = self.inject_param(url, param, "1' AND '1'='2")
        try:
            rt, rf = self.s.get(t, timeout=TIMEOUT), self.s.get(f, timeout=TIMEOUT)
        except requests.RequestException:
            return
        if len(rt.text) != len(rf.text) and abs(len(rt.text) - len(base.text)) < 50:
            self._mark(url=url, param=param, kind="sqli",
                       evidence=f"len(true)={len(rt.text)} len(false)={len(rf.text)}",
                       severity="high", confidence="probable", payload="boolean")

    def xss(self, url, param):
        marker = "hw" + hashlib.md5(str(time.time()).encode()).hexdigest()[:6]
        payload = f"<svg/onload=alert('{marker}')>"
        u = self.inject_param(url, param, payload)
        try:
            r = self.s.get(u, timeout=TIMEOUT)
        except requests.RequestException:
            return
        if payload in r.text or (marker in r.text and "<svg" in r.text.lower()):
            self._mark(url=url, param=param, kind="xss", evidence="reflected unescaped",
                       severity="medium", confidence="confirmed", payload=payload)

    def open_redirect(self, url, param):
        canary = "https://example.org/hw-canary"
        u = self.inject_param(url, param, canary)
        try:
            r = self.s.get(u, timeout=TIMEOUT, allow_redirects=False)
        except requests.RequestException:
            return
        loc = r.headers.get("location", "")
        if canary in loc:
            self._mark(url=url, param=param, kind="open_redirect", evidence=f"Location: {loc}",
                       severity="low", confidence="confirmed", payload=canary)

    def lfi(self, url, param):
        payload = "../../../../etc/passwd"
        u = self.inject_param(url, param, payload)
        try:
            r = self.s.get(u, timeout=TIMEOUT)
        except requests.RequestException:
            return
        if "root:x:0:0" in r.text:
            self._mark(url=url, param=param, kind="lfi", evidence="/etc/passwd disclosed",
                       severity="high", confidence="confirmed", payload=payload)

    def ssrf(self, url, param, canary):
        if not canary:
            return
        u = self.inject_param(url, param, canary)
        try:
            self.s.get(u, timeout=TIMEOUT)
        except requests.RequestException:
            return
        self._mark(url=url, param=param, kind="ssrf",
                   evidence=f"request issued to {canary} (verify responder log)",
                   severity="high", confidence="probable", payload=canary)

    def cmdi(self, url, param):
        payload = ";sleep 5"
        u = self.inject_param(url, param, payload)
        try:
            t0 = time.time()
            self.s.get(u, timeout=15)
            d = time.time() - t0
        except requests.RequestException:
            return
        if d >= 5.0:
            self._mark(url=url, param=param, kind="cmdi",
                       evidence=f"delay {d:.1f}s on sleep payload",
                       severity="critical", confidence="probable", payload=payload)

    def ssti(self, url, param):
        probes = [("{{7*7}}", "49"), ("${7*7}", "49"), ("<%= 7*7 %>", "49"), ("#{7*7}", "49")]
        for payload, expected in probes:
            u = self.inject_param(url, param, payload)
            try:
                r = self.s.get(u, timeout=TIMEOUT)
            except requests.RequestException:
                continue
            if expected in r.text and payload not in r.text:
                self._mark(url=url, param=param, kind="ssti",
                           evidence=f"evaluated {payload} -> {expected}",
                           severity="high", confidence="probable", payload=payload)
                return

    def xxe(self, url, param):
        payload = ('<?xml version="1.0"?><!DOCTYPE x [<!ENTITY e SYSTEM "file:///etc/passwd">]>'
                   '<x>&e;</x>')
        try:
            r = self.s.post(url, data=payload,
                            headers={"Content-Type": "application/xml"},
                            timeout=TIMEOUT)
        except requests.RequestException:
            return
        if "root:x:0:0" in r.text:
            self._mark(url=url, param=param, kind="xxe", evidence="/etc/passwd via XXE",
                       severity="high", confidence="confirmed",
                       payload="<!ENTITY e SYSTEM ...>")

    def run(self, surface: Surface, ssrf_canary: str | None = None) -> list[Finding]:
        for url, params in surface.params.items():
            for p in params:
                self.sqli(url, p)
                self.xss(url, p)
                self.open_redirect(url, p)
                self.lfi(url, p)
                self.cmdi(url, p)
                self.ssti(url, p)
                if ssrf_canary:
                    self.ssrf(url, p, ssrf_canary)

        for action, method, inputs in surface.forms:
            data = {n: "1" for n, _ in inputs}
            for p in data:
                for payload, kind in (("'", "sqli"),
                                      ("<svg/onload=alert(1)>", "xss"),
                                      ("{{7*7}}", "ssti")):
                    d2 = dict(data)
                    d2[p] = payload
                    try:
                        r = self.s.post(action, data=d2, timeout=TIMEOUT)
                    except requests.RequestException:
                        continue
                    if kind == "sqli" and re.search(
                            r"SQL syntax|mysql_fetch|ORA-\d{4,5}", r.text, re.I):
                        self._mark(url=action, param=p, kind="sqli",
                                   evidence="error-based (POST)",
                                   severity="high", confidence="confirmed", payload=payload)
                    if kind == "xss" and payload in r.text:
                        self._mark(url=action, param=p, kind="xss",
                                   evidence="reflected (POST)",
                                   severity="medium", confidence="confirmed", payload=payload)
                    if kind == "ssti" and "49" in r.text and payload not in r.text:
                        self._mark(url=action, param=p, kind="ssti",
                                   evidence="POST {{7*7}} -> 49",
                                   severity="high", confidence="probable", payload=payload)
                if method == "POST":
                    self.xxe(action, p)

        return self.findings
```

## `stitch/recon.py`

```python
"""Reconnaissance helpers: headers, technology, ports, TLS."""
import re
import socket
import ssl
import time

import requests

from .session import TIMEOUT

SEC_HEADERS = [
    ("Strict-Transport-Security", "HSTS: forces HTTPS, prevents downgrade."),
    ("Content-Security-Policy",   "CSP: restricts script/style origins, mitigates XSS."),
    ("X-Frame-Options",           "Anti-clickjacking."),
    ("X-Content-Type-Options",    "Prevents MIME sniffing (must be 'nosniff')."),
    ("Referrer-Policy",           "Controls Referer header leakage."),
    ("Permissions-Policy",        "Restricts browser APIs (geoloc, camera, mic)."),
]

TECH_SIGNS = {
    "wordpress": [r"wp-content", r"wp-includes", r"/wp-json"],
    "drupal":    [r"Drupal", r"sites/default/files"],
    "joomla":    [r"/components/com_", r"Joomla"],
    "laravel":   [r"laravel_session", r"XSRF-TOKEN"],
    "django":    [r"csrftoken", r"__admin__"],
    "flask":     [r"Werkzeug", r"session=[a-z0-9]+\.[a-z0-9]+"],
    "express":   [r"X-Powered-By.*Express", r"connect.sid"],
    "nginx":     [r"Server: nginx", r"nginx"],
    "apache":    [r"Server: Apache", r"Apache/"],
    "cloudflare":[r"Server: cloudflare", r"cf-ray"],
    "react":     [r"_reactRootContainer", r"data-reactroot"],
    "vue":       [r"__VUE__", r"vue\.js"],
    "angular":   [r"ng-version", r"angular\.min\.js"],
    "jquery":    [r"jquery[.-][0-9]"],
}

COMMON_PORTS = [
    (21, "ftp"), (22, "ssh"), (23, "telnet"), (25, "smtp"), (53, "dns"),
    (80, "http"), (110, "pop3"), (143, "imap"), (443, "https"), (445, "smb"),
    (3306, "mysql"), (3389, "rdp"), (5432, "postgresql"), (6379, "redis"),
    (8080, "http-alt"), (8443, "https-alt"), (27017, "mongodb"),
]


def check_headers(url: str, session: requests.Session) -> dict:
    """Return {header_name: present_bool} plus informative headers."""
    try:
        r = session.get(url, timeout=TIMEOUT)
    except requests.RequestException:
        return {}
    h = {k.lower(): v for k, v in r.headers.items()}
    return {
        "present": {name: (name.lower() in h) for name, _ in SEC_HEADERS},
        "informative": {k: h[k] for k in ("server", "x-powered-by", "via", "x-aspnet-version") if k in h},
    }


def detect_tech(url: str, session: requests.Session) -> list[str]:
    try:
        r = session.get(url, timeout=TIMEOUT)
    except requests.RequestException:
        return []
    blob = r.text + "\n" + "\n".join(f"{k}: {v}" for k, v in r.headers.items())
    found = set()
    for name, pats in TECH_SIGNS.items():
        for pat in pats:
            if re.search(pat, blob, re.I):
                found.add(name)
                break
    return sorted(found)


def scan_ports(host: str, timeout: float = 1.0) -> list[tuple[int, str]]:
    open_ports = []
    for port, service in COMMON_PORTS:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            if sock.connect_ex((host, port)) == 0:
                open_ports.append((port, service))
        except (socket.error, socket.timeout):
            pass
        finally:
            sock.close()
    return open_ports


def check_tls(host: str, port: int = 443) -> dict:
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
        subj = dict(x[0] for x in cert.get("subject", ()))
        issuer = dict(x[0] for x in cert.get("issuer", ()))
        days_left = None
        if cert.get("notAfter"):
            exp = time.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
            days_left = (time.mktime(exp) - time.time()) / 86400
        return {"subject": subj.get("commonName"), "issuer": issuer.get("organizationName"),
                "expires": cert.get("notAfter"), "days_left": days_left}
    except (socket.error, ssl.SSLError, ValueError) as e:
        return {"error": str(e)}
```

## `stitch/tools.py`

```python
"""Optional integrations with nmap, sqlmap, nuclei (only if on PATH)."""
import shutil
import subprocess


def which(binary: str) -> str | None:
    return shutil.which(binary)


def run_nmap(host: str) -> str:
    nmap = which("nmap")
    if not nmap:
        return "nmap not found on PATH; install nmap or use built-in port scan (menu 7)."
    try:
        out = subprocess.run(
            [nmap, "-sV", "-T4", "--top-ports", "100", host],
            capture_output=True, text=True, timeout=300,
        )
        return out.stdout or out.stderr
    except subprocess.TimeoutExpired:
        return "nmap timed out after 300s."
    except OSError as e:
        return f"nmap failed: {e}"


def run_sqlmap(url: str) -> str:
    sqlmap = which("sqlmap")
    if not sqlmap:
        return "sqlmap not found on PATH; install sqlmap to confirm SQLi."
    try:
        out = subprocess.run(
            [sqlmap, "-u", url, "--batch", "--level", "1", "--risk", "1"],
            capture_output=True, text=True, timeout=600,
        )
        return out.stdout or out.stderr
    except subprocess.TimeoutExpired:
        return "sqlmap timed out after 600s."
    except OSError as e:
        return f"sqlmap failed: {e}"


def run_nuclei(url: str) -> str:
    nuclei = which("nuclei")
    if not nuclei:
        return "nuclei not found on PATH; install nuclei to run templates."
    try:
        out = subprocess.run(
            [nuclei, "-u", url, "-silent"],
            capture_output=True, text=True, timeout=600,
        )
        return out.stdout or out.stderr
    except subprocess.TimeoutExpired:
        return "nuclei timed out after 600s."
    except OSError as e:
        return f"nuclei failed: {e}"
```

## `stitch/report.py`

```python
"""JSON report writer."""
import json
import time
from dataclasses import asdict

from .engine import Finding

_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def write_report(findings: list[Finding], out: str | None) -> None:
    findings_sorted = sorted(findings, key=lambda f: _ORDER.get(f.severity, 9))
    doc = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "count": len(findings_sorted),
        "findings": [asdict(f) for f in findings_sorted],
    }
    if out:
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2)
        print(f"[+] report -> {out} ({len(findings_sorted)} findings)")
    else:
        print(json.dumps(doc, indent=2))
```

## `stitch/menu.py`

```python
"""Interactive numbered menu."""
import urllib.parse as up

from .banner import RED, PURPLE, GREEN, YELLOW, RESET, BOLD, banner_text, clear
from .config import load as load_config, save as save_config
from .crawler import Crawler
from .engine import Engine
from .recon import SEC_HEADERS, check_headers, detect_tech, scan_ports, check_tls
from .report import write_report
from .session import build_session
from .tools import run_nmap, run_sqlmap, run_nuclei


def _ask(prompt, default=None):
    suffix = f" [{default}]" if default is not None else ""
    while True:
        raw = input(f"{PURPLE}{prompt}{RESET}{suffix}: ").strip()
        if raw == "" and default is not None:
            return default
        if raw != "":
            return raw


def _ask_int(prompt, lo, hi, default=None):
    while True:
        raw = _ask(prompt, default)
        try:
            v = int(raw)
        except ValueError:
            print(f"{RED}  ! enter a number between {lo} and {hi}{RESET}")
            continue
        if lo <= v <= hi:
            return v
        print(f"{RED}  ! out of range: {lo}-{hi}{RESET}")


def _ask_yesno(prompt, default="n"):
    while True:
        raw = _ask(f"{prompt} (y/n)", default).lower()
        if raw in ("y", "yes", "s", "si", "sí"):
            return True
        if raw in ("n", "no"):
            return False
        print(f"{RED}  ! answer y or n{RESET}")


def _show_menu():
    clear()
    print(banner_text())
    print(f"\n{BOLD}{RED}        s t i t c h {RESET}")
    print(f"""
{PURPLE}  ┌──────────────────────────────────────────────────────┐
  │  {RED}ESCANER WEB{RESET}{PURPLE}                                          │
  │  {RED}1{RESET}{PURPLE}  Analisis rapido (findings a pantalla)             │
  │  {RED}2{RESET}{PURPLE}  Analisis completo (+ reporte JSON)               │
  │  {RED}3{RESET}{PURPLE}  Analisis con SSRF (requiere responder externo)    │
  │  {RED}4{RESET}{PURPLE}  Solo crawling (mapear URLs y formularios)         │
  │                                                      │
  │  {RED}RECONOCIMIENTO{RESET}{PURPLE}                                       │
  │  {RED}5{RESET}{PURPLE}  Cabeceras de seguridad                         │
  │  {RED}6{RESET}{PURPLE}  Detectar tecnologia                            │
  │  {RED}7{RESET}{PURPLE}  Escaneo de puertos comunes                      │
  │  {RED}8{RESET}{PURPLE}  Certificado TLS                                │
  │  {RED}9{RESET}{PURPLE}  Reconocimiento completo (5+6+7+8)                │
  │                                                      │
  │  {RED}INTEGRACIONES{RESET}{PURPLE}                                       │
  │  {RED}12{RESET}{PURPLE} nmap - servicio y version                       │
  │  {RED}13{RESET}{PURPLE} sqlmap - confirmar SQLi                         │
  │  {RED}14{RESET}{PURPLE} nuclei - templates de la comunidad              │
  │                                                      │
  │  {RED}HERRAMIENTAS{RESET}{PURPLE}                                        │
  │  {RED}10{RESET}{PURPLE} Autenticacion (cookie/header)                   │
  │  {RED}11{RESET}{PURPLE} Modo avanzado (flags)                           │
  │  {RED}0 {RESET}{PURPLE} Salir                                             │
  └──────────────────────────────────────────────────────┘{RESET}
""")


def interactive_main():
    s = build_session()
    cfg = load_config()
    last_url = cfg.get("last_url")
    last_scope = cfg.get("last_scope")
    last_report = cfg.get("last_report") or "out.json"

    while True:
        _show_menu()
        opt = _ask_int("  elige una opcion", 0, 14)

        if opt == 0:
            print(f"{PURPLE}  hasta luego.{RESET}")
            return

        if opt == 11:
            print(f"\n{PURPLE}  modo avanzado: usa flags.{RESET}")
            print("  ejemplo: python -m stitch -u https://target.tld --scope target.tld --report out.json")
            input(f"\n{PURPLE}  Enter para volver al menu...{RESET}")
            continue

        if opt == 7:
            host = _ask("  host o IP a escanear", last_scope)
            if not host:
                continue
            print(f"\n{PURPLE}── puertos abiertos en {host} ──{RESET}")
            ports = scan_ports(host)
            if ports:
                for p, svc in ports:
                    print(f"{GREEN}  [+] {p}/tcp {svc}{RESET}")
            else:
                print(f"{YELLOW}  [?] ningun puerto comun abierto{RESET}")
            input(f"\n{PURPLE}  Enter para volver al menu...{RESET}")
            continue

        url = _ask("  URL (https://...)", last_url)
        if not url or not url.startswith(("http://", "https://")):
            print(f"{RED}  ! la URL debe empezar por http:// o https://{RESET}")
            input(f"{PURPLE}  Enter para continuar...{RESET}")
            continue
        last_url = url
        default_scope = up.urlparse(url).hostname or ""
        last_scope = default_scope

        if opt == 5:
            print(f"\n{PURPLE}── cabeceras de seguridad ──{RESET}")
            res = check_headers(url, s)
            for name, _why in SEC_HEADERS:
                ok = res.get("present", {}).get(name, False)
                mark = f"{GREEN}[+]{RESET}" if ok else f"{RED}[-]{RESET}"
                print(f"  {mark} {name}")
            for k, v in res.get("informative", {}).items():
                print(f"{YELLOW}  [!] {k}: {v}{RESET}")
            input(f"\n{PURPLE}  Enter para volver al menu...{RESET}")
            continue

        if opt == 6:
            print(f"\n{PURPLE}── tecnologia detectada ──{RESET}")
            techs = detect_tech(url, s)
            if techs:
                for t in techs:
                    print(f"{GREEN}  [+] {t}{RESET}")
            else:
                print(f"{YELLOW}  [?] no se reconocio tecnologia{RESET}")
            input(f"\n{PURPLE}  Enter para volver al menu...{RESET}")
            continue

        if opt == 8:
            port = 443 if url.startswith("https") else 80
            print(f"\n{PURPLE}── certificado TLS de {default_scope}:{port} ──{RESET}")
            info = check_tls(default_scope, port)
            if "error" in info:
                print(f"{RED}  ! {info['error']}{RESET}")
            else:
                print(f"  sujeto:  {info.get('subject')}")
                print(f"  emisor:  {info.get('issuer')}")
                print(f"  valido hasta: {info.get('expires')}")
                days = info.get("days_left")
                if days is not None:
                    color = GREEN if days > 30 else YELLOW if days > 7 else RED
                    print(f"{color}  expira en {days:.0f} dias{RESET}")
            input(f"\n{PURPLE}  Enter para volver al menu...{RESET}")
            continue

        if opt == 9:
            print(f"\n{PURPLE}── cabeceras de seguridad ──{RESET}")
            res = check_headers(url, s)
            for name, _why in SEC_HEADERS:
                ok = res.get("present", {}).get(name, False)
                mark = f"{GREEN}[+]{RESET}" if ok else f"{RED}[-]{RESET}"
                print(f"  {mark} {name}")
            print(f"\n{PURPLE}── tecnologia detectada ──{RESET}")
            techs = detect_tech(url, s)
            if techs:
                for t in techs:
                    print(f"{GREEN}  [+] {t}{RESET}")
            else:
                print(f"{YELLOW}  [?] no se reconocio tecnologia{RESET}")
            print(f"\n{PURPLE}── puertos abiertos en {default_scope} ──{RESET}")
            ports = scan_ports(default_scope)
            if ports:
                for p, svc in ports:
                    print(f"{GREEN}  [+] {p}/tcp {svc}{RESET}")
            else:
                print(f"{YELLOW}  [?] ningun puerto comun abierto{RESET}")
            port = 443 if url.startswith("https") else 80
            print(f"\n{PURPLE}── certificado TLS de {default_scope}:{port} ──{RESET}")
            info = check_tls(default_scope, port)
            if "error" in info:
                print(f"{RED}  ! {info['error']}{RESET}")
            else:
                print(f"  sujeto:  {info.get('subject')}")
                print(f"  emisor:  {info.get('issuer')}")
                print(f"  valido hasta: {info.get('expires')}")
            input(f"\n{PURPLE}  Enter para volver al menu...{RESET}")
            continue

        if opt == 10:
            print(f"\n{PURPLE}  autenticacion: pega valores para las requests{RESET}")
            cookie = _ask("  cookie (nombre=valor, vacio para ninguna)", "")
            header_name = _ask("  header extra (nombre, vacio para ninguno)", "")
            header_val = ""
            if header_name:
                header_val = _ask(f"  valor para {header_name}", "")
            if cookie and "=" in cookie:
                k, v = cookie.split("=", 1)
                s.cookies.set(k, v)
                print(f"{GREEN}  [+] cookie guardada{RESET}")
            if header_name and header_val:
                s.headers[header_name] = header_val
                print(f"{GREEN}  [+] header {header_name} guardado{RESET}")
            input(f"{PURPLE}  Enter para volver al menu...{RESET}")
            continue

        if opt == 12:
            print(f"\n{PURPLE}── nmap ──{RESET}")
            print(run_nmap(default_scope))
            input(f"\n{PURPLE}  Enter para volver al menu...{RESET}")
            continue

        if opt == 13:
            target = _ask("  URL con parametro (?id=1)", url)
            print(f"\n{PURPLE}── sqlmap ──{RESET}")
            print(run_sqlmap(target))
            input(f"\n{PURPLE}  Enter para volver al menu...{RESET}")
            continue

        if opt == 14:
            print(f"\n{PURPLE}── nuclei ──{RESET}")
            print(run_nuclei(url))
            input(f"\n{PURPLE}  Enter para volver al menu...{RESET}")
            continue

        # opciones 1-4 (escaneo)
        scope = _ask("  scope (dominio permitido)", default_scope)
        report_path = None
        ssrf_canary = None
        do_crawl_only = (opt == 4)

        if opt in (2, 3):
            report_path = _ask("  archivo de reporte", last_report)
            last_report = report_path
        if opt == 3:
            ssrf_canary = _ask("  URL del responder SSRF (https://...)")

        max_pages = _ask_int("  max paginas a crawlear", 1, 5000, "200")

        print(f"\n{PURPLE}  ── resumen ──{RESET}")
        print(f"  url:        {url}")
        print(f"  scope:      {scope}")
        print(f"  max pages:  {max_pages}")
        if report_path:
            print(f"  reporte:    {report_path}")
        if ssrf_canary:
            print(f"  ssrf:       {ssrf_canary}")
        if do_crawl_only:
            print(f"  modo:       solo crawling")
        if not _ask_yesno("  empezar", "s"):
            continue

        save_config({
            "last_url": last_url,
            "last_scope": last_scope,
            "last_report": last_report,
            "last_workers": 1,
        })

        print(f"\n{PURPLE}[*] crawl {url} scope={scope}{RESET}")
        surf = Crawler(url, scope, s).crawl(max_pages=max_pages)
        print(f"{PURPLE}[*] {len(surf.urls)} urls, {len(surf.forms)} forms, {len(surf.params)} param'd urls{RESET}")

        if do_crawl_only:
            print(f"\n{PURPLE}── urls ──{RESET}")
            for u in sorted(surf.urls):
                print(f"  {u}")
            print(f"\n{PURPLE}── formularios ──{RESET}")
            for action, method, inputs in surf.forms:
                names = ", ".join(n for n, _ in inputs) or "(sin campos)"
                print(f"  [{method}] {action}  →  {names}")
            input(f"\n{PURPLE}  Enter para volver al menu...{RESET}")
            continue

        eng = Engine(s, scope)
        findings = eng.run(surf, ssrf_canary=ssrf_canary)
        write_report(findings, report_path)
        input(f"\n{PURPLE}  Enter para volver al menu...{RESET}")
```

## `stitch/cli.py`

```python
"""CLI entrypoint."""
import argparse
import sys

from . import __version__
from .banner import boot_banner
from .crawler import Crawler
from .engine import Engine
from .intro import run_intro
from .menu import interactive_main
from .recon import SEC_HEADERS, check_headers, detect_tech, scan_ports, check_tls
from .report import write_report
from .session import build_session, TIMEOUT
from .tools import run_nmap, run_sqlmap, run_nuclei


def _do_recon(url, scope, s):
    print("── headers ──")
    res = check_headers(url, s)
    for name, _ in SEC_HEADERS:
        ok = res.get("present", {}).get(name, False)
        print(f"  {'[+]' if ok else '[-]'} {name}")
    print("\n── technology ──")
    for t in detect_tech(url, s):
        print(f"  [+] {t}")
    print(f"\n── ports ({scope}) ──")
    for p, svc in scan_ports(scope):
        print(f"  [+] {p}/tcp {svc}")
    print(f"\n── tls ({scope}) ──")
    print(check_tls(scope, 443))


def main():
    if len(sys.argv) == 1:
        run_intro()
        boot_banner()
        interactive_main()
        return

    ap = argparse.ArgumentParser(prog="stitch", description="Web analysis framework")
    ap.add_argument("--version", action="version", version=f"stitch {__version__}")
    ap.add_argument("-u", "--url", help="start URL")
    ap.add_argument("--scope", help="allowed host suffix")
    ap.add_argument("--report", default=None, help="JSON report output")
    ap.add_argument("--ssrf-canary", default=None, help="external responder URL")
    ap.add_argument("--max-pages", type=int, default=200)
    ap.add_argument("--timeout", type=float, default=TIMEOUT)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--recon", action="store_true", help="recon only")
    ap.add_argument("--nmap", action="store_true", help="run nmap on host")
    ap.add_argument("--confirm-sqli", action="store_true", help="run sqlmap")
    ap.add_argument("--nuclei", action="store_true", help="run nuclei")
    a = ap.parse_args()

    if not a.url or not a.scope:
        ap.error("-u/--url and --scope are required unless running interactively")

    run_intro()
    boot_banner()

    s = build_session()

    if a.nmap:
        print(run_nmap(a.scope))
        return
    if a.confirm_sqli:
        print(run_sqlmap(a.url))
        return
    if a.nuclei:
        print(run_nuclei(a.url))
        return
    if a.recon:
        _do_recon(a.url, a.scope, s)
        return

    print(f"[*] crawl {a.url} scope={a.scope}")
    surf = Crawler(a.url, a.scope, s).crawl(max_pages=a.max_pages)
    print(f"[*] {len(surf.urls)} urls, {len(surf.forms)} forms, {len(surf.params)} param'd urls")

    eng = Engine(s, a.scope)
    findings = eng.run(surf, ssrf_canary=a.ssrf_canary)
    write_report(findings, a.report)


if __name__ == "__main__":
    main()
```

## `tests/test_engine.py`

```python
"""Smoke tests for the engine data model."""
from stitch.engine import Finding, Engine
from stitch.crawler import Surface


def test_finding_dataclass():
    f = Finding(url="https://x", param="id", kind="sqli",
                evidence="err", severity="high", confidence="confirmed", payload="'")
    assert f.url == "https://x"
    assert f.payload == "'"


def test_engine_mark_appends():
    import requests
    eng = Engine(requests.Session(), "example.com")
    eng._mark(url="https://example.com", param="q", kind="xss",
              evidence="reflected", severity="medium", confidence="confirmed")
    assert len(eng.findings) == 1


def test_surface_defaults():
    s = Surface()
    assert s.urls == set()
    assert s.forms == []
    assert s.params == {}
```

## `examples/targets.md`

```markdown
# Practice targets

Legal, intentional-vulnerable apps you can run locally or in Docker.

## Local (Docker)

- **OWASP Juice Shop** — modern JS shop with a huge challenge set.
  ```
  docker run --rm -p 3000:3000 bkimminich/juice-shop
  ```

- **DVWA** — classic PHP lab, adjustable difficulty.
  ```
  docker run --rm -p 8080:80 vulnerables/web-dvwa
  ```

- **bWAPP** — very large bug catalogue, PHP/MySQL.
  ```
  docker run --rm -p 8080:80 raesene/bwapp
  ```

## Online

- **PortSwigger Web Security Academy** — free labs, no install.
  https://portswigger.net/web-security

- **HackTheBox** and **TryHackMe** — guided machines, some free.

## Scope reminder

When running `stitch` against any of these, set `--scope` to the host
(e.g. `localhost`, `juiceshop.lab`) so the crawler never leaves your lab.
```
