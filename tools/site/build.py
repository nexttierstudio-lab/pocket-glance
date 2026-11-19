"""Builds the homepage in every supported language.

    python tools/site/build.py
    python tools/site/build.py --site-url https://example.com/pocket_glance/ --out dist/pocket_glance

Reads tools/site/page.html (the template) and tools/site/i18n/<code>.json (one strings
file per language, with en.json as the source of truth), and writes:

    index.html           English, at the site root
    <code>/index.html    every other language, e.g. es/index.html

To change copy, edit the strings files and rebuild. To add a language, add a row to LANGS
and a strings file with the same keys as en.json. The build stops if a key is missing,
extra, or a placeholder is left unfilled. Values may contain the small bits of markup the
English uses (<span class="gold">, <em class="gold">, a link to {{root}}terms.html).

--site-url only changes the absolute addresses search engines and link previews read
(canonical, hreflang, og:image); every link a visitor clicks is relative. --out writes the
pages somewhere other than the repo root (tools/publish.py uses both).
"""
import argparse
import json
import re
import sys
from pathlib import Path

SITE_URL = "https://nexttierstudio-lab.github.io/pocket-glance/"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

# code (folder), html lang, og:locale, name in its own language, direction
LANGS = [
    ("en", "en", "en_US", "English", "ltr"),
    ("es", "es-419", "es_LA", "Español", "ltr"),
    ("pt", "pt-BR", "pt_BR", "Português", "ltr"),
    ("fr", "fr", "fr_FR", "Français", "ltr"),
    ("de", "de", "de_DE", "Deutsch", "ltr"),
    ("hi", "hi", "hi_IN", "हिन्दी", "ltr"),
    ("ar", "ar", "ar_AR", "العربية", "rtl"),
    ("ja", "ja", "ja_JP", "日本語", "ltr"),
    ("ko", "ko", "ko_KR", "한국어", "ltr"),
    ("zh", "zh-Hans", "zh_CN", "简体中文", "ltr"),
]


def folder(code):
    return "" if code == "en" else code + "/"


def rel(from_code, to_code):
    """Relative link from one language's page to another's."""
    up = "" if from_code == "en" else "../"
    target = folder(to_code)
    if from_code == to_code:
        return "./"
    return (up + target) or "./"


def main(site_url=SITE_URL, out_root=ROOT):
    site_url = site_url.rstrip("/") + "/"
    out_root = Path(out_root)
    template = (HERE / "page.html").read_text(encoding="utf-8")
    strings = {c: json.loads((HERE / "i18n" / f"{c}.json").read_text(encoding="utf-8")) for c, *_ in LANGS}
    keys = set(strings["en"])
    bad = False
    for code, s in strings.items():
        missing, extra = keys - set(s), set(s) - keys
        if missing or extra:
            bad = True
            print(f"{code}: missing {sorted(missing)} extra {sorted(extra)}")
    if bad:
        sys.exit(1)

    alternates = "\n".join(
        f'  <link rel="alternate" hreflang="{lang}" href="{site_url}{folder(code)}">' for code, lang, *_ in LANGS
    ) + f'\n  <link rel="alternate" hreflang="x-default" href="{site_url}">'

    for code, lang, og, _name, direction in LANGS:
        s = strings[code]
        menu = "".join(
            f'<li><a href="{rel(code, c)}" hreflang="{l}" lang="{l}" data-lang="{c}"'
            + (' aria-current="true"' if c == code else "")
            + f">{n}</a></li>"
            for c, l, _o, n, _d in LANGS
        )
        system = {
            "lang": lang, "dir": direction, "code": code, "og_locale": og,
            "root": "" if code == "en" else "../",
            "site": site_url,
            "alternates": alternates + f'\n  <link rel="canonical" href="{site_url}{folder(code)}">',
            "lang_menu": menu,
            "legal_note": "" if code == "en" else f'    <p class="legal-note">{s["legal_note"]}</p>\n',
        }
        page = re.sub(r"\{\{(\w+)\}\}", lambda m: s[m.group(1)] if m.group(1) in s else m.group(0), template)
        page = re.sub(r"\{\{(\w+)\}\}", lambda m: system[m.group(1)] if m.group(1) in system else m.group(0), page)
        left = re.findall(r"\{\{\w+\}\}", page)
        if left:
            sys.exit(f"{code}: unfilled {sorted(set(left))}")
        out = out_root / folder(code) / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8", newline="\n")
        print("wrote", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--site-url", default=SITE_URL, help=f"public address of the site (default {SITE_URL})")
    ap.add_argument("--out", default=str(ROOT), help="folder to write into (default: the repo root)")
    args = ap.parse_args()
    main(args.site_url, args.out)
