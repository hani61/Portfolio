# hanylockedin.com

Static, multi-page site for Hany — “I turn websites into revenue systems. WordPress + AI.”

Plain HTML, one compiled Tailwind stylesheet, one vanilla JS file. No React, no runtime
framework, no server. Deploys straight to GitHub Pages.

## Run it

```sh
bun install          # once
bun run dev          # builds CSS, serves on http://localhost:3000
```

Other scripts:

```sh
bun run css          # rebuild assets/css/site.css (minified)
bun run css:watch    # rebuild on change while editing
bun run images       # regenerate OG images, favicons, mockups (Python + Pillow)
bun run pdf          # regenerate the lead magnet PDF (Python + Pillow)
```

`assets/css/site.css` is committed, so the site works without a build step. If you edit
`src/input.css` or any HTML class names, run `bun run css` again.

## Pages

| File | Purpose |
| --- | --- |
| `index.html` | Home: hero, services, work, about teaser, lead magnet |
| `services.html` | Pricing in EGP + USD, what's included, process, FAQ |
| `portfolio.html` | Marketing agency + dental clinic case studies |
| `about.html` | The barracks story, milestones, working principles |
| `contact.html` | Validated contact form + DM CTA |
| `founder-playbook.html` | “The 15-Minute Founder” landing page + inline thank-you state |
| `thank-you.html` | Post-submission confirmation (noindex) |
| `privacy.html`, `terms.html` | Legal pages (indexable on purpose) |
| `404.html` | GitHub Pages serves this for unknown URLs |
| `robots.txt`, `sitemap.xml`, `site.webmanifest`, `CNAME`, `.nojekyll` | Indexing, PWA, custom domain |

## Edit the content

- **Copy, prices, page text** live directly in the `.html` files.
- **Design tokens** (colours, type, animations) are in `src/input.css` under `@theme`.
- **Instagram / email** appear in every page and footer. Update with:
  `grep -rl "hany.lockedin" *.html` and `grep -rl "hello@hanylockedin.com" *.html`.
- **Prices:** WordPress (EGP 10,000–24,000 / $1,500–3,000) come from the brief. WooCommerce,
  Odoo and maintenance figures are estimates — confirm them before launch and update
  `services.html` (table + each section) and the three cards on `index.html`.
- **Screenshots:** `assets/img/work-agency.png` and `work-dental.png` are generated mockups.
  Replace them with real screenshots (1600×1200 or any 4:3 crop) and update the `alt` text.
  `about-portrait.png` is a typographic placeholder for a real photo (900×1100).
- **Case study results:** `portfolio.html` has `<!-- TODO -->` markers where the 30-day
  numbers go. The page currently makes no unmeasured claims — keep it that way.

## Connect the forms

Forms work out of the box: validation, error states, loading spinner, demo redirect. They do
**not** deliver anything until you add an endpoint.

1. Create a form at [Formspree](https://formspree.io), [Web3Forms](https://web3forms.com) or
   any service that accepts a JSON `POST`. GitHub Pages cannot run server code.
2. In `assets/js/site.js`, set `FORM_ENDPOINT` to your endpoint URL (near the top).
3. Add that host to the `Content-Security-Policy` in every page: `connect-src` and
   `form-action`. Example: `connect-src 'self' https://plausible.io https://formspree.io`.
4. Submit once and confirm the redirect to `/thank-you.html` (without `?demo=1`), plus the
   lead magnet's inline thank-you panel and PDF download.

While `FORM_ENDPOINT` is empty the thank-you page shows a **Demo mode** notice instead of
pretending the message was delivered.

## Analytics

Plausible is included (`data-domain="hanylockedin.com"`, cookieless, no cookie banner
needed). Create the site at [plausible.io](https://plausible.io) and the script starts
reporting. To use something else, replace that `<script>` tag on each page and update the CSP
`script-src` / `connect-src`. Note that the local preview will 404 that script — harmless.

## Deploy to GitHub Pages

```sh
git add .
git commit -m "Rebuild site"
git push origin main
```

Then: **Settings → Pages → Source: Deploy from a branch → main / (root)**.

- `CNAME` (`hanylockedin.com`) and `.nojekyll` are already in place.
- If you deploy to a **project** URL (`user.github.io/repo/`) instead of the custom domain,
  delete `CNAME` and change every `/assets/...` and `/page.html` link to a relative path,
  otherwise assets 404.
- Enable **Enforce HTTPS** after the certificate is issued.

## Redirects (only if old URLs exist)

GitHub Pages cannot issue server-side 301s. If the old site had URLs that were shared or
indexed, create a small page at each old path:

```html
<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<title>Moved</title>
<link rel="canonical" href="https://hanylockedin.com/services.html">
<meta http-equiv="refresh" content="0; url=/services.html">
<meta name="robots" content="noindex">
</head>
<body><p>This page moved to <a href="/services.html">/services.html</a>.</p></body></html>
```

Then add the new URL to `sitemap.xml`. Send me the old URL list and this can be generated.

## Structure

```
├── *.html                 pages (shared header/footer markup is inline in each)
├── assets/
│   ├── css/site.css       compiled Tailwind (committed)
│   ├── js/site.js         nav, reveals, cookie banner, form logic
│   ├── fonts/             self-hosted Montserrat variable woff2
│   ├── img/               OG images, favicons, mockups, portrait
│   └── pdf/               the lead magnet
├── src/input.css          Tailwind source + component classes
├── scripts/
│   ├── serve.mjs          dependency-free preview server (404 → 404.html)
│   ├── make-images.py     regenerates every bitmap asset
│   └── make-pdf.py        regenerates the 9-page PDF
├── robots.txt · sitemap.xml · site.webmanifest · CNAME · .nojekyll · favicon.ico
```

## Before launch — replace these

- [ ] Real email address (`hello@hanylockedin.com` is a placeholder)
- [ ] Full street address in the footer (currently “Cairo, Egypt”)
- [ ] Confirmed WooCommerce / Odoo / maintenance prices
- [ ] Real screenshots for the two case studies + a real photo on About
- [ ] Form endpoint + CSP update
- [ ] Plausible account
- [ ] Real Instagram handle if different from `@hany.lockedin`
