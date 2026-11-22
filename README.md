# Pocket Glance website

Homepage, Privacy Policy, Terms & Conditions and Help & Support (including data deletion) for the Pocket Glance
Android app, served with GitHub Pages.

- `index.html`, `privacy.html`, `terms.html`, `help.html`: homepage, Privacy Policy,
  Terms & Conditions and Help & Support in English (generated, see below). `delete-data.html` is
  generated as a redirect to `help.html#delete`, so the Google Play deletion link keeps working
- `es/`, `pt/`, `fr/`, `de/`, `hi/`, `ar/`, `ja/`, `ko/`, `zh/`: the same pages in the app's
  other languages (generated)
- `img/`: app icon and phone screenshots used by the homepage
- `tools/site/`: the page templates, the wording for every language, and the build script
- `tools/make-screens.py`: rebuilds `img/*.webp` from the app's raw Play Store captures

Each page is self-contained (inline CSS, plus a little inline script for the light/dark switch and,
on the homepage, the language menu and scroll motion that is switched off for visitors who ask for
reduced motion).

## Editing the pages

Don't edit the four pages or the language folders by hand: they are overwritten by the build.

- Homepage layout, styles and script: `tools/site/page.html`
- Legal pages layout and styles: `tools/site/legal.html`
- Top bar (shared by every page): `tools/site/partials/bar.css`, `bar.html`, `bar.js`
- Short wording: `tools/site/i18n/<code>.json` (`en.json` is the source; every other file must
  have exactly the same keys)
- Legal text: `tools/site/legal/<code>/privacy.html`, `terms.html`, `help.html`
  (`en/` is the source). When the English text changes, update every language. Translated
  legal pages say that the English version applies if they differ.

Then rebuild every language (needs Python 3):

```bash
python tools/site/build.py
```

The build stops if a language is missing a key, has an extra one, or leaves a placeholder unfilled.
To add a language, add a row to `LANGS` in `tools/site/build.py` and a matching strings file.

Wording follows the app's own strings and the Play Store listing translations, so feature names
match what people see in the app. Arabic pages are laid out right to left. Scripts other than
Latin use the visitor's system serif and sans, because Bodoni Moda and Inter only cover Latin.

## Screenshots

To refresh the screenshots after new captures, from this folder (needs Python with Pillow):

```bash
python tools/make-screens.py ../Finorvia/docs/launch/play-store/src/raw
```

## Preview on your computer

Before publishing, build every language and serve the site locally (needs Python 3):

```bash
python tools/serve.py
```

Then open <http://localhost:8765/>. The script rebuilds the homepage first, so you always see your
latest edits to `tools/site/`. Options: `--port 9000` for another port, `--no-build` to serve what is
already built, `--open` to open the browser for you. Stop it with Ctrl+C. It only listens on this
computer, and since every link is relative, pages behave as they will on GitHub Pages.

Check the homepage, a couple of language folders (for example `/es/` and the right-to-left `/ar/`),
and the Privacy, Terms and Help pages, then commit and push.

## Publish on your own domain

The site is published at <https://nexttierstudio.co.in/pocket_glance/>, and
`nexttierstudio.co.in` and `www.nexttierstudio.co.in` send visitors there. Every push to `main`
runs `.github/workflows/pages.yml`, which builds `dist/` with `tools/publish.py --stubs` and
deploys it with GitHub Pages:

- `dist/pocket_glance/`: the whole site. Only the canonical, hreflang and link-preview addresses
  point at the domain; every visitor link is relative.
- `dist/index.html`: sends the bare domain on to `/pocket_glance/`.
- `dist/privacy.html`, `dist/es/`, ...: send the old top-level addresses on to their new place, so
  links to the old `nexttierstudio-lab.github.io/pocket-glance/` address (such as the Play Store
  privacy link) keep working once GitHub redirects it to the domain.

One-time setup (already done if the site is live):

1. GoDaddy DNS for nexttierstudio.co.in: four `A` records for `@` pointing to `185.199.108.153`,
   `185.199.109.153`, `185.199.110.153` and `185.199.111.153` (remove any other `A` record for
   `@`), and a `CNAME` for `www` pointing to `nexttierstudio-lab.github.io`.
2. GitHub, Settings > Pages: Source "GitHub Actions", custom domain `nexttierstudio.co.in`, then
   "Enforce HTTPS" once the certificate is ready. Re-run the "Publish site" workflow.

Until the Source is "GitHub Actions" the workflow only checks the build. To build the same thing
locally, or a copy for other hosting (Apache `.htaccess` and Netlify `_redirects` are included):

```bash
python tools/publish.py --domain nexttierstudio.co.in
```

The fonts in `fonts/` are Bodoni Moda and Inter, both licensed under the
[SIL Open Font License 1.1](https://openfontlicense.org/open-font-license-official-text/).
