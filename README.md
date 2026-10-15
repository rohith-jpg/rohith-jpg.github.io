# Rohith Singhu — personal portfolio

**Website:** https://rohith-jpg.github.io/

A lightweight portfolio with a dark/light theme, responsive navigation, seven project cards, category filters, five AI case studies, research, experience, education, certifications and contact details.

The public pages are plain HTML, CSS and JavaScript. There is no production build step, database, tracking script, contact-form backend or paid hosting dependency. Python is only used when editing/regenerating pages.

## Edit and preview

1. Clone this repository and open it in VS Code.
2. Edit `content.json` for project copy, links, verification URLs and the resume path.
3. Run `python build.py` to regenerate the HTML pages.
4. Run `python -m http.server 8787` and open `http://localhost:8787`.
5. Edit `assets/style.css` for presentation and `assets/site.js` for theme/filter/navigation behavior.

The home-page personal biography, timeline and skills are in `build.py`. Change those there, then rebuild; direct changes to generated HTML will be overwritten.

## Deploy free on GitHub Pages

1. Use the public repository named **rohith-jpg.github.io**.
2. Commit the generated `index.html`, `projects/`, `assets/`, `.nojekyll`, `sitemap.xml` and `robots.txt` together with the editable source.
3. Open **Settings → Pages**.
4. Under **Build and deployment**, select **Deploy from a branch**.
5. Choose **main** and **/(root)**, then **Save**.
6. When the Pages deployment finishes, visit **https://rohith-jpg.github.io/**.
7. For updates, rebuild locally and push the changed files to `main`; GitHub Pages republishes them.

No custom domain is required. [GitHub's official Pages guide](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site) explains repository names and publishing sources.

## Alternative: Vercel

1. Sign in to Vercel and import this GitHub repository as a new project.
2. Select **Other** as the framework preset.
3. Leave the build command empty and use the repository root (`.`) as the output directory.
4. Deploy. If using that URL as the primary site, update `url` in `content.json` and run `python build.py` so canonical, sitemap and Open Graph URLs match.

Use a plan whose current terms fit your use. [Vercel's official GitHub deployment guide](https://vercel.com/docs/git/vercel-for-github).

## Add the resume and verification links

- Save the actual resume as `assets/rohith-singhu-resume.pdf`.
- Set `resume` in `content.json` to `assets/rohith-singhu-resume.pdf` and rebuild. The PDF must be present before publishing the active button.
- Set each certification's `verify` value to the public credential verification URL. Leave null until supplied.
- Replace the explicit `[TODO]` dates and contribution notes in `build.py` only with confirmed facts.
- Add public demo URLs and authentic project screenshots in `content.json`; missing items are labeled rather than fabricated.

## Evidence and scope

Project descriptions were prepared from the owner's READMEs and linked artifacts. RAGenius evaluation figures come from `eval/report_v4.md`. RxSupply's 10-case regression suite explicitly does not evaluate LLM accuracy. Synthetic security and systems fixtures are labeled. VerticalDesk's repository is private; its existence and project description were authorized for this portfolio, but it is not advertised as public source.

Workflow illustrations are original SVG diagrams, clearly distinguished from application screenshots. The Lateral Movement Hunt screenshot comes from that repository. The research article lists Rohith Singhu as a co-author and is linked rather than copied.

## Accessibility and performance

The site has semantic headings, a skip link, keyboard focus styles, accessible filter state, descriptive links, reduced-motion support and responsive layouts. Core content is rendered into HTML and remains available without JavaScript. Images are lazy-loaded below the fold. Theme preferences are stored locally; no personal data is collected.

See `QA.md` for measured audit results and verification limits. A score must come from a completed Lighthouse run; source design alone does not establish a 90+ score.
