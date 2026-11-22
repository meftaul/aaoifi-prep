# AAOIFI Prep

Bilingual (English & Bangla) study guides to the AAOIFI Shari'ah Standards. Built with React, TypeScript and Vite.

Guides currently on the site: SS 2 (Debit, Charge and Credit Cards) and SS 3 (Procrastinating Debtor). Each guide
opens at `?guide=ss-02`, `?guide=ss-03`. The content was converted from the study-guide PDFs with the scripts in
`tools/pdf-to-guide/`.

Live site: https://meftaul.github.io/aaoifi-prep/

## Development

```bash
npm install
npm run dev      # local dev server
npm run build    # type-check and build to dist/
npm run preview  # serve the production build
```

## Deployment

Every push (or merged PR) to `main` runs `.github/workflows/deploy.yml`, which builds the
app and publishes `dist/` to GitHub Pages. It can also be run manually from the Actions tab.

The Vite `base` is set to `/aaoifi-prep/` in `vite.config.ts` to match the Pages URL.
