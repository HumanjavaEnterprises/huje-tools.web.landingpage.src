#!/usr/bin/env python3
"""Fail the build if the site advertises an install the registry does not back.

For every tool card in docs/index.html that shows a `pip install` / `npm install`
command alongside a PyPI/npm link, this check asserts that the package exists in
the registry (huje.registry.src/packages.yaml) as a row that is BOTH
`status: published` and `advertise_install: true`, and whose install name matches
the one printed on the site.

Cards that do not advertise an install (e.g. "source-only", "in design",
"planned") are ignored on purpose: they make no install claim to verify.

Stdlib only. Exit code 0 = clean, 1 = at least one violation.
"""
from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE_INDEX = os.path.join(HERE, os.pardir, "docs", "index.html")
DEFAULT_REGISTRY = os.path.join(
    HERE, os.pardir, os.pardir, "huje.registry.src", "packages.yaml"
)
REGISTRY = os.environ.get("HUJE_REGISTRY", DEFAULT_REGISTRY)

INSTALL_RE = re.compile(r"\b(?:pip|npm)\s+install\s+([A-Za-z0-9._\-]+)")


def pkg_from_install(text: str):
    """Return the bare package name from an install command, or None."""
    m = INSTALL_RE.search(text or "")
    if not m:
        return None
    # strip pip "extras" like social-value[liquid] (regex already drops "[")
    return m.group(1)


def parse_registry(path: str):
    """Minimal YAML reader for the flat package rows we care about.

    Returns {install_name: {"status":..., "advertise_install":bool,
                            "install_pkg":...}}.
    """
    with open(path, encoding="utf-8") as fh:
        lines = fh.readlines()

    rows = {}
    cur = None

    def flush(row):
        if not row:
            return
        name = row.get("current_name")
        if name:
            rows[name] = row

    for raw in lines:
        line = raw.rstrip("\n")
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            continue
        # new package row starts with "- id:"
        m = re.match(r"\s*-\s+id:\s*(.+)$", line)
        if m:
            flush(cur)
            cur = {"id": m.group(1).strip()}
            continue
        if cur is None:
            continue
        # only capture top-level scalar fields of the row (4-space indent)
        fm = re.match(r"\s{4}([A-Za-z_]+):\s*(.*)$", line)
        if not fm:
            continue
        key, val = fm.group(1), fm.group(2).strip()
        if key == "current_name":
            cur["current_name"] = val
        elif key == "status":
            cur["status"] = val
        elif key == "advertise_install":
            cur["advertise_install"] = val.lower() in ("true", "yes", "1")
        elif key == "install":
            cur["install"] = val
            cur["install_pkg"] = pkg_from_install(val)
    flush(cur)
    return rows


def parse_site_cards(path: str):
    """Yield (card_name, advertised_pkg) for cards that claim an install."""
    with open(path, encoding="utf-8") as fh:
        html = fh.read()

    cards = re.split(r'<article class="tool-card">', html)[1:]
    out = []
    for card in cards:
        name_m = re.search(r"<h2>([^<]+)</h2>", card)
        name = name_m.group(1).strip() if name_m else "(unknown)"
        install_m = re.search(r'<div class="card-install">(.*?)</div>', card, re.S)
        install_txt = install_m.group(1) if install_m else ""
        pkg = pkg_from_install(install_txt)
        has_pkg_link = bool(
            re.search(r'href="https://pypi\.org/project/', card)
            or re.search(r'href="https://www\.npmjs\.com/package/', card)
        )
        if pkg and has_pkg_link:
            out.append((name, pkg))
        elif pkg and not has_pkg_link:
            # an install command with no package link is still a claim -> check it
            out.append((name, pkg))
    return out


def main() -> int:
    if not os.path.exists(REGISTRY):
        print(f"ERROR: registry not found at {REGISTRY}", file=sys.stderr)
        print("Set HUJE_REGISTRY to the path of packages.yaml.", file=sys.stderr)
        return 1

    registry = parse_registry(REGISTRY)
    cards = parse_site_cards(SITE_INDEX)

    violations = []
    for name, pkg in cards:
        row = registry.get(pkg)
        if row is None:
            violations.append(
                f"[{name}] advertises `install {pkg}` but no registry row "
                f"has current_name '{pkg}'."
            )
            continue
        if row.get("status") != "published":
            violations.append(
                f"[{name}] advertises `install {pkg}` but registry status is "
                f"'{row.get('status')}', not 'published'."
            )
        if not row.get("advertise_install"):
            violations.append(
                f"[{name}] advertises `install {pkg}` but registry has "
                f"advertise_install: false."
            )
        if row.get("install_pkg") and row["install_pkg"] != pkg:
            violations.append(
                f"[{name}] install name '{pkg}' does not match registry "
                f"install name '{row['install_pkg']}'."
            )

    print(f"Checked {len(cards)} advertised-install card(s) against {REGISTRY}")
    for name, pkg in cards:
        print(f"  - {name}: {pkg}")

    if violations:
        print("\nFAIL: site advertises installs the registry does not back:")
        for v in violations:
            print(f"  * {v}")
        return 1

    print("\nOK: every advertised install maps to a published, advertise_install row.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
