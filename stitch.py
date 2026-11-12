#!/usr/bin/env python3
"""Stitch: passive web reconnaissance for explicitly authorized targets."""

from __future__ import annotations

import argparse
import json
import re
import socket
import ssl
import sys
import time
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse, urldefrag

import requests
from bs4 import BeautifulSoup

__version__ = "0.3.0"
TIMEOUT = 12
USER_AGENT = "Stitch-Passive-Audit/0.3 (+authorized security assessment)"


@dataclass
class CrawlResult:
    pages: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def normalize_scope(scope: str) -> str:
    return scope.strip().lower().lstrip(".")


def in_scope(url: str, scope: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return host == scope or host.endswith("." + scope)


def crawl(start_url: str, scope: str, max_pages: int) -> CrawlResult:
    """Fetch ordinary HTML pages using GET; never submits forms or follows off-scope links."""
    result = CrawlResult()
    queue = deque([start_url])
    seen: set[str] = set()
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    while queue and len(seen) < max_pages:
        url = queue.popleft()
        url, _fragment = urldefrag(url)
        if url in seen or not in_scope(url, scope):
            continue
        seen.add(url)
        try:
            response = session.get(url, timeout=TIMEOUT, allow_redirects=True)
            final_url = response.url
            if not in_scope(final_url, scope):
                result.errors.append(f"Redirect outside scope blocked: {url}")
                continue
            if "text/html" not in response.headers.get("Content-Type", "").lower():
                continue
            result.pages.append(final_url)
            soup = BeautifulSoup(response.text, "html.parser")
            for anchor in soup.find_all("a", href=True):
                candidate = urljoin(final_url, anchor["href"])
                candidate, _ = urldefrag(candidate)
                if urlparse(candidate).scheme in ("http", "https") and in_scope(candidate, scope):
                    if candidate not in seen:
                        queue.append(candidate)
        except requests.RequestException as exc:
            result.errors.append(f"{url}: {type(exc).__name__}")
    return result


SECURITY_HEADERS = {
    "strict-transport-security": "HSTS",
    "content-security-policy": "CSP",
    "x-frame-options": "Protección frente a framing",
    "x-content-type-options": "Protección MIME sniffing",
    "referrer-policy": "Política de Referer",
    "permissions-policy": "Restricción de APIs del navegador",
}

TECH_SIGNATURES = {
    "WordPress": [r"wp-content", r"wp-includes", r"/wp-json"],
    "Drupal": [r"Drupal", r"sites/default/files"],
    "Joomla": [r"/components/com_", r"Joomla"],
    "Laravel": [r"laravel_session", r"XSRF-TOKEN"],
    "Django": [r"csrftoken", r"__admin__"],
    "nginx": [r"nginx"],
    "Apache": [r"Apache/"],
    "Cloudflare": [r"cf-ray", r"cloudflare"],
    "React": [r"_reactRootContainer", r"data-reactroot"],
    "Vue": [r"__VUE__", r"vue\.js"],
    "jQuery": [r"jquery[.-][0-9]"],
}


def fetch_homepage(url: str) -> requests.Response:
    response = requests.get(
        url, timeout=TIMEOUT, headers={"User-Agent": USER_AGENT}, allow_redirects=True
    )
    response.raise_for_status()
    return response


def audit_headers(response: requests.Response) -> dict:
    headers = {key.lower(): value for key, value in response.headers.items()}
    return {
        name: {"present": key in headers, "value": headers.get(key)}
        for key, name in SECURITY_HEADERS.items()
    }


def detect_technologies(response: requests.Response) -> list[str]:
    body = response.text[:1_000_000]
    blob = body + "\n" + "\n".join(f"{k}: {v}" for k, v in response.headers.items())
    return sorted(
        name for name, patterns in TECH_SIGNATURES.items()
        if any(re.search(pattern, blob, re.IGNORECASE) for pattern in patterns)
    )


def inspect_tls(host: str, port: int = 443) -> dict:
    context = ssl.create_default_context()
    try:
        with socket.create_connection((host, port), timeout=5) as raw:
            with context.wrap_socket(raw, server_hostname=host) as secured:
                cert = secured.getpeercert()
        subject = dict(item[0] for item in cert.get("subject", ()))
        issuer = dict(item[0] for item in cert.get("issuer", ()))
        expiry = cert.get("notAfter")
        return {
            "subject": subject.get("commonName"),
            "issuer": issuer.get("organizationName"),
            "expires": expiry,
        }
    except (OSError, ssl.SSLError, ValueError) as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}


def build_report(url: str, scope: str, do_crawl: bool, max_pages: int) -> dict:
    response = fetch_homepage(url)
    parsed = urlparse(response.url)
    report = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "target": response.url,
        "scope": scope,
        "http_status": response.status_code,
        "security_headers": audit_headers(response),
        "technologies": detect_technologies(response),
        "tls": inspect_tls(parsed.hostname, parsed.port or 443) if parsed.scheme == "https" else None,
    }
    if do_crawl:
        report["crawl"] = asdict(crawl(response.url, scope, max_pages))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="stitch", description="Reconocimiento web pasivo para pruebas autorizadas."
    )
    parser.add_argument("--version", action="version", version=f"stitch {__version__}")
    parser.add_argument("-u", "--url", help="URL inicial (http:// o https://)")
    parser.add_argument("--scope", help="Dominio permitido, por ejemplo example.com")
    parser.add_argument("--crawl", action="store_true", help="Recorrer enlaces del mismo ámbito")
    parser.add_argument("--recon", action="store_true", help="Auditar cabeceras, tecnología y TLS")
    parser.add_argument("--max-pages", type=int, default=30)
    parser.add_argument("--report", help="Guardar el resultado en JSON")
    args = parser.parse_args()

    if not args.url or not args.scope:
        parser.error("indica -u/--url y --scope")
    if args.max_pages < 1 or args.max_pages > 500:
        parser.error("--max-pages debe estar entre 1 y 500")
    if urlparse(args.url).scheme not in ("http", "https"):
        parser.error("la URL debe comenzar por http:// o https://")

    scope = normalize_scope(args.scope)
    if not in_scope(args.url, scope):
        parser.error("la URL inicial no pertenece al ámbito indicado")

    try:
        report = build_report(args.url, scope, args.crawl, args.max_pages)
    except requests.RequestException as exc:
        print(f"Error HTTP: {exc}", file=sys.stderr)
        raise SystemExit(2)

    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.report:
        with open(args.report, "w", encoding="utf-8") as output:
            json.dump(report, output, indent=2, ensure_ascii=False)
        print(f"\n[+] Informe guardado en {args.report}")


if __name__ == "__main__":
    main()
