# Pocket Glance website

Homepage, Privacy Policy, Terms & Conditions and data-deletion instructions for the Pocket Glance
Android app, served with GitHub Pages.

- `index.html`: homepage in English (generated, see below)
- `es/`, `pt/`, `fr/`, `de/`, `hi/`, `ar/`, `ja/`, `ko/`, `zh/`: the homepage in the app's other
  languages (generated)
- `privacy.html`: Privacy Policy (English)
- `terms.html`: Terms & Conditions (English)
- `delete-data.html`: how to delete your data (English)
- `img/`: app icon and phone screenshots used by the homepage
- `tools/site/`: the homepage template, one strings file per language, and the build script
- `tools/make-screens.py`: rebuilds `img/*.webp` from the app's raw Play Store captures

Each page is self-contained (inline CSS, plus a little inline script for the light/dark switch and,
on the homepage, the language menu and scroll motion that is switched off for visitors who ask for
reduced motion).

## Editing the homepage

Don't edit `index.html` or the language folders by hand: they are overwritten by the build.

- Layout, styles and script: `tools/site/page.html`
- Wording: `tools/site/i18n/<code>.json` (`en.json` is the source; every other file must have
  exactly the same keys)

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
and the Privacy, Terms and Delete data pages, then commit and push.

The fonts in `fonts/` are Bodoni Moda and Inter, both licensed under the
[SIL Open Font License 1.1](https://openfontlicense.org/open-font-license-official-text/).
