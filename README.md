# Pocket Glance website

Homepage, Privacy Policy, Terms & Conditions and data-deletion instructions for the Pocket Glance
Android app, served with GitHub Pages.

- `index.html`: homepage
- `privacy.html`: Privacy Policy
- `terms.html`: Terms & Conditions
- `delete-data.html`: how to delete your data
- `img/`: app icon and phone screenshots used by the homepage
- `tools/make-screens.py`: rebuilds `img/*.webp` from the app's raw Play Store captures

Each page is self-contained (inline CSS, plus a little inline script for the light/dark switch and,
on the homepage, scroll motion that is switched off for visitors who ask for reduced motion).

To refresh the screenshots after new captures, from this folder (needs Python with Pillow):

```bash
python tools/make-screens.py ../Finorvia/docs/launch/play-store/src/raw
```

To preview locally:

```bash
python -m http.server 8765
```

The fonts in `fonts/` are Bodoni Moda and Inter, both licensed under the
[SIL Open Font License 1.1](https://openfontlicense.org/open-font-license-official-text/).
