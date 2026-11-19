"""Builds every page of the site in every supported language.

    python tools/site/build.py
    python tools/site/build.py --site-url https://example.com/pocket_glance/ --out dist/pocket_glance

Templates:
    page.html                 the homepage
    legal.html                the Privacy Policy, Terms and Delete-your-data pages
    partials/bar.*            the top bar (styles, markup, script), shared by both

Wording:
    i18n/<code>.json          short strings for every page (en.json is the source of truth)
    legal/<code>/<page>.html  the text of each legal page: a "title:" line, a "description:"
                              line, "---", then the page body (en/ is the source of truth)

It writes, for each of index.html, privacy.html, terms.html and delete-data.html:

    <page>          English, at the site root
    <code>/<page>   every other language, e.g. es/privacy.html

To change copy, edit the strings or legal files and rebuild. To add a language, add a row to
LANGS, a strings file with the same keys as en.json, and a legal/<code>/ folder. The build
stops if a key is missing, extra, a legal file is missing, or a placeholder is left unfilled.
Values may contain the small bits of markup the English uses (<span class="gold">,
<em class="gold">, a link to terms.html).

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


def _star(cx, cy, r, rot=0.0):
    """Points of a five-pointed star, for the small flags below."""
    import math
    pts = []
    for i in range(10):
        a = math.radians(rot - 90 + i * 36)
        rr = r if i % 2 == 0 else r * 0.4
        pts.append(f"{cx + rr * math.cos(a):.2f},{cy + rr * math.sin(a):.2f}")
    return f'<polygon points="{" ".join(pts)}"/>'


# Small flags drawn inline (30x20), so the menu needs no images and no emoji font: Windows
# shows flag emoji as two letters. Simplified on purpose; at 20 pixels wide the detail is lost anyway.
_US_STRIPES = "".join(f'<rect y="{20 / 13 * i:.3f}" width="30" height="{20 / 13:.3f}" fill="#fff"/>' for i in range(1, 13, 2))
FLAGS = {
    "en": f'<rect width="30" height="20" fill="#B22234"/>{_US_STRIPES}<rect width="13" height="10.77" fill="#3C3B6E"/>'
          '<g fill="#fff">' + "".join(_star(2.2 + 2.2 * x + (1.1 if y % 2 else 0), 1.6 + 1.9 * y, 0.65) for y in range(5) for x in range(5 if y % 2 == 0 else 4)) + "</g>",
    "es": '<rect width="10" height="20" fill="#006847"/><rect x="10" width="10" height="20" fill="#fff"/><rect x="20" width="10" height="20" fill="#CE1126"/><circle cx="15" cy="10" r="2.4" fill="#8C6A3A"/>',
    "pt": '<rect width="30" height="20" fill="#009C3B"/><polygon points="3,10 15,2.5 27,10 15,17.5" fill="#FFDF00"/><circle cx="15" cy="10" r="4.6" fill="#002776"/><path d="M10.6 9.2c3-.9 6.3-.6 8.8.9" stroke="#fff" stroke-width="1" fill="none"/>',
    "fr": '<rect width="10" height="20" fill="#0055A4"/><rect x="10" width="10" height="20" fill="#fff"/><rect x="20" width="10" height="20" fill="#EF4135"/>',
    "de": '<rect width="30" height="6.67" fill="#000"/><rect y="6.67" width="30" height="6.67" fill="#DD0000"/><rect y="13.33" width="30" height="6.67" fill="#FFCE00"/>',
    "hi": '<rect width="30" height="6.67" fill="#FF9933"/><rect y="6.67" width="30" height="6.67" fill="#fff"/><rect y="13.33" width="30" height="6.67" fill="#138808"/><circle cx="15" cy="10" r="2.6" fill="none" stroke="#000080" stroke-width=".8"/><circle cx="15" cy="10" r=".6" fill="#000080"/>',
    "ar": '<rect width="30" height="20" fill="#006C35"/><path d="M8 7.2h14M9 9.3c1.5-1 3 1 4.5 0s3 1 4.5 0 2.5 1 3.5 0" stroke="#fff" stroke-width=".9" fill="none" stroke-linecap="round"/><path d="M8.5 13.5h12.5l1.5-.8" stroke="#fff" stroke-width=".9" fill="none" stroke-linecap="round"/>',
    "ja": '<rect width="30" height="20" fill="#fff"/><circle cx="15" cy="10" r="6" fill="#BC002D"/>',
    "ko": '<rect width="30" height="20" fill="#fff"/><circle cx="15" cy="10" r="5" fill="#0047A0"/><path d="M10 10a5 5 0 0 1 10 0a2.5 2.5 0 0 1-5 0a2.5 2.5 0 0 0-5 0z" fill="#CD2E3A"/>'
          '<g stroke="#000" stroke-width="1"><path d="M4.4 5.4l2.2-2.4M5.4 6.3l2.2-2.4M6.4 7.2l2.2-2.4"/><path d="M21.4 15.6l2.2-2.4M22.4 16.5l2.2-2.4M23.4 17.4l2.2-2.4"/><path d="M21.4 4.4l2.2 2.4M22.4 3.5l2.2 2.4M20.4 5.3l2.2 2.4"/><path d="M4.4 14.6l2.2 2.4M5.4 13.7l2.2 2.4M6.4 12.8l2.2 2.4"/></g>',
    "zh": '<rect width="30" height="20" fill="#DE2910"/><g fill="#FFDE00">' + _star(5, 5, 3) + _star(10, 2, 1, 23) + _star(12, 4, 1, 45) + _star(12, 7, 1, 70) + _star(10, 9, 1, 20) + "</g>",
}


def flag(code):
    return f'<svg class="flag" viewBox="0 0 30 20" width="21" height="14" aria-hidden="true">{FLAGS[code]}</svg>'


def folder(code):
    return "" if code == "en" else code + "/"


def rel(from_code, to_code, page=""):
    """Relative link from one language's copy of a page to another language's copy."""
    if from_code == to_code:
        return page or "./"
    up = "" if from_code == "en" else "../"
    return (up + folder(to_code) + page) or "./"


# The pages built for every language: (file, template). Legal pages take their wording from
# legal/<code>/<file>: a title line, a description line, "---", then the page's body.
PAGES = [("index.html", "page.html"), ("privacy.html", "legal.html"), ("terms.html", "legal.html"), ("delete-data.html", "legal.html")]
# Links in the bar, three on every page: two homepage sections and the Privacy Policy, or the
# three legal pages. Terms stays in the footer.
HOME_LINKS = [("#features", "nav_features"), ("#pro", "nav_pro"), ("privacy.html", "nav_privacy")]
LEGAL_LINKS = [("privacy.html", "nav_privacy"), ("terms.html", "nav_terms"), ("delete-data.html", "nav_delete")]


def include(template):
    """Pastes in shared pieces: {{>bar.css}} is the file partials/bar.css."""
    return re.sub(r"\{\{>([\w.]+)\}\}", lambda m: (HERE / "partials" / m.group(1)).read_text(encoding="utf-8").rstrip("\n"), template)


def fill(text, *tables):
    for table in tables:
        text = re.sub(r"\{\{(\w+)\}\}", lambda m: table[m.group(1)] if m.group(1) in table else m.group(0), text)
    return text


def legal_content(code, file):
    path = HERE / "legal" / code / file
    if not path.exists():
        sys.exit(f"missing {path}")
    head, body = path.read_text(encoding="utf-8").split("\n---\n", 1)
    meta = dict(line.split(": ", 1) for line in head.strip().splitlines())
    return meta["title"], meta["description"], body.rstrip("\n")


def main(site_url=SITE_URL, out_root=ROOT):
    site_url = site_url.rstrip("/") + "/"
    out_root = Path(out_root)
    templates = {t: include((HERE / t).read_text(encoding="utf-8")) for _, t in PAGES}
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

    for file, template in PAGES:
        page_path = "" if file == "index.html" else file
        alternates = "\n".join(
            f'  <link rel="alternate" hreflang="{lang}" href="{site_url}{folder(code)}{page_path}">' for code, lang, *_ in LANGS
        ) + f'\n  <link rel="alternate" hreflang="x-default" href="{site_url}{page_path}">'

        for code, lang, og, name, direction in LANGS:
            s = strings[code]
            # One list, used twice: the bar's dropdown (wide screens) and the grid of chips in the
            # menu panel (phones). Each entry: flag, code, the language's own name, and it leads
            # to this same page in that language.
            menu = "".join(
                f'<li><a href="{rel(code, c, page_path)}" hreflang="{l}" lang="{l}" data-lang="{c}"'
                + (' aria-current="true"' if c == code else "")
                + f">{flag(c)}<b>{c.upper()}</b><span>{n}</span></a></li>"
                for c, l, _o, n, _d in LANGS
            )
            links = HOME_LINKS if file == "index.html" else LEGAL_LINKS
            bar_links = "\n".join(
                f'      <a href="{href}"' + (' aria-current="page"' if href == file else "") + f">{s[key]}</a>"
                for href, key in links
            )
            system = {
                "lang": lang, "dir": direction, "code": code, "og_locale": og,
                "root": "" if code == "en" else "../",
                "site": site_url,
                "alternates": alternates + f'\n  <link rel="canonical" href="{site_url}{folder(code)}{page_path}">',
                "lang_menu": menu,
                "lang_flag": flag(code),
                "lang_code": code.upper(),
                "lang_name": name,
                "bar_links": bar_links,
                "brand_current": ' aria-current="page"' if file == "index.html" else "",
            }
            text = templates[template]
            if template == "legal.html":
                title, description, body = legal_content(code, file)
                system["page_title"], system["page_description"] = title, description
                # A translated legal page says so and links to the English original.
                system["tr_note"] = "" if code == "en" else (
                    f'    <p class="tr-note">{s["legal_tr_note"]} '
                    f'<a href="../{file}" hreflang="en" lang="en">{s["legal_tr_link"]}</a></p>\n'
                )
                text = text.replace("{{content}}", body)
            out_text = fill(text, s, system)
            left = re.findall(r"\{\{>?[\w.]+\}\}", out_text)
            if left:
                sys.exit(f"{code}/{file}: unfilled {sorted(set(left))}")
            out = out_root / folder(code) / file
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(out_text, encoding="utf-8", newline="\n")
            print("wrote", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--site-url", default=SITE_URL, help=f"public address of the site (default {SITE_URL})")
    ap.add_argument("--out", default=str(ROOT), help="folder to write into (default: the repo root)")
    args = ap.parse_args()
    main(args.site_url, args.out)
