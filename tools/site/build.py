"""Builds the homepage in every supported language.

    python tools/site/build.py

Reads tools/site/page.html (the template) and tools/site/i18n/<code>.json (one strings
file per language, with en.json as the source of truth), and writes:

    index.html           English, at the site root
    <code>/index.html    every other language, e.g. es/index.html

To change copy, edit the strings files and rebuild. To add a language, add a row to LANGS
and a strings file with the same keys as en.json. The build stops if a key is missing,
extra, or a placeholder is left unfilled. Values may contain the small bits of markup the
English uses (<span class="gold">, <em class="gold">, a link to {{root}}terms.html).
"""
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


def main():
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
        f'  <link rel="alternate" hreflang="{lang}" href="{SITE_URL}{folder(code)}">' for code, lang, *_ in LANGS
    ) + f'\n  <link rel="alternate" hreflang="x-default" href="{SITE_URL}">'

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
            "site": SITE_URL,
            "alternates": alternates + f'\n  <link rel="canonical" href="{SITE_URL}{folder(code)}">',
            "lang_menu": menu,
            "legal_note": "" if code == "en" else f'    <p class="legal-note">{s["legal_note"]}</p>\n',
        }
        page = re.sub(r"\{\{(\w+)\}\}", lambda m: s[m.group(1)] if m.group(1) in s else m.group(0), template)
        page = re.sub(r"\{\{(\w+)\}\}", lambda m: system[m.group(1)] if m.group(1) in system else m.group(0), page)
        left = re.findall(r"\{\{\w+\}\}", page)
        if left:
            sys.exit(f"{code}: unfilled {sorted(set(left))}")
        out = ROOT / folder(code) / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8", newline="\n")
        print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
