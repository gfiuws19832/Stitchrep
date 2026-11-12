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
