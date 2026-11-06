"""Generate a portable static portfolio. Python 3.10+, standard library only."""
import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / 'content.json').read_text(encoding='utf-8'))
PROJECTS = DATA['projects']


def esc(value):
    return html.escape(str(value), quote=True)


def write(path, text):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding='utf-8', newline='\n')


def external(url, label, extra=''):
    return f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer" {extra}>{label}<span class="visually-hidden"> (opens in new tab)</span></a>'


CERT_DATES = {'Sep 2026': '2026-09', 'May 2025': '2025-05'}
SITE = DATA['url'] + '/'
PERSON_ID = SITE + '#person'
WEBSITE_ID = SITE + '#website'
UPDATED = DATA['updated']
UPDATED_LABEL = date.fromisoformat(UPDATED).strftime('%b %Y')

# Verified against the Crossref record for the DOI.
PAPER = {
    'title': 'Physiotherapy Assistance for Patients Using Human Pose Estimation With Raspberry Pi',
    'doi': '10.55164/ajstr.v27i4.251096',
    'date': '2024-07-11',
    'journal': 'ASEAN Journal of Scientific and Technological Reports',
    'publisher': 'Thaksin University',
    'volume': '27', 'issue': '4',
    'license': 'https://creativecommons.org/licenses/by-nc-nd/4.0/',
    'url': 'https://ph02.tci-thaijo.org/index.php/tsujournal/article/view/251096',
    'coauthors': ['Khasim Vali Dudekula', 'Maruthi Venkata Chalapathi Mukkoti', 'Venkata Pavan Kumar Yellapragada',
                  'Purna Prakash Kasaraneni', 'Pradeep Reddy Challa', 'Dhiren Gangishetty', 'Manaswita Solanki'],
}


def person_ref():
    """Minimal Person node so pages that only reference the person still resolve the @id."""
    return {'@type':'Person','@id':PERSON_ID,'name':DATA['name'],'url':SITE}


def person_schema():
    return {'@type':'Person','@id':PERSON_ID,'name':DATA['name'],
            'jobTitle':'Software Developer',
            'worksFor':{'@type':'Organization','name':'Viacore Technologies Inc.'},
            'description':'Software Developer building AI tools that connect answers to evidence: retrieval-augmented generation, agent workflows and human-review checks.',
            'url':SITE,'email':DATA['email'],'image':SITE+'assets/og-image.png',
            'address':{'@type':'PostalAddress','addressLocality':'Cleveland','addressRegion':'OH','addressCountry':'US'},
            'knowsAbout':['Retrieval-augmented generation','AI agents','LangGraph','Model Context Protocol','Python','FastAPI','Security operations'],
            'sameAs':[DATA['github'], DATA['linkedin']],
            'alumniOf':[{'@type':'CollegeOrUniversity','name':'Auburn University at Montgomery'},
                        {'@type':'CollegeOrUniversity','name':'VIT-AP University'}],
            'hasCredential':[{'@type':'EducationalOccupationalCredential','name':c['name'],
                              'credentialCategory':'certification',
                              'recognizedBy':{'@type':'Organization','name':c['issuer']},
                              'dateCreated':CERT_DATES.get(c.get('earned'), c.get('earned'))}
                             for c in DATA['certifications']]}


def paper_schema():
    doi_url = 'https://doi.org/' + PAPER['doi']
    return {'@type':'ScholarlyArticle','@id':doi_url,'headline':PAPER['title'],'name':PAPER['title'],
            'datePublished':PAPER['date'],'url':PAPER['url'],'sameAs':doi_url,'license':PAPER['license'],
            'identifier':{'@type':'PropertyValue','propertyID':'DOI','value':PAPER['doi']},
            'publisher':{'@type':'Organization','name':PAPER['publisher']},
            'isPartOf':{'@type':'PublicationIssue','issueNumber':PAPER['issue'],
                        'isPartOf':{'@type':'PublicationVolume','volumeNumber':PAPER['volume'],
                                    'isPartOf':{'@type':'Periodical','name':PAPER['journal']}}},
            'author':[{'@type':'Person','name':n} for n in PAPER['coauthors']] + [{'@id':PERSON_ID}]}


def home_schema():
    return {'@context':'https://schema.org','@graph':[
        {'@type':'WebSite','@id':WEBSITE_ID,'url':SITE,'name':DATA['name'],'publisher':{'@id':PERSON_ID}},
        {'@type':'ProfilePage','@id':SITE+'#profile','url':SITE,'isPartOf':{'@id':WEBSITE_ID},
         'mainEntity':{'@id':PERSON_ID},'dateModified':UPDATED},
        person_schema(), paper_schema()]}


def case_schema(project):
    url = SITE + 'projects/' + project['slug'] + '.html'
    code = {'@type':'SoftwareSourceCode','@id':url+'#code','name':project['name'],'description':project['summary'],
            'programmingLanguage':'Python' if 'Python' in project['stack'] else project['stack'][0],
            'keywords':', '.join(project['stack']),'author':{'@id':PERSON_ID}}
    if not project.get('private'):
        code['codeRepository'] = DATA['github'] + '/' + project['repo']
    return {'@context':'https://schema.org','@graph':[
        {'@type':'TechArticle','@id':url+'#article','headline':project['name']+': '+project['headline'],
         'description':project['summary'],'url':url,'dateModified':UPDATED,'author':{'@id':PERSON_ID},
         'isPartOf':{'@id':WEBSITE_ID},'about':{'@id':url+'#code'}},
        code,
        {'@type':'BreadcrumbList','itemListElement':[
            {'@type':'ListItem','position':1,'name':'Home','item':SITE},
            {'@type':'ListItem','position':2,'name':project['name'],'item':url}]},
        person_ref()]}


def shell(title, description, body, depth=0, path='', schema=None, og_type='website', absolute=False, noindex=False):
    """absolute=True uses root-relative links (for 404.html, which GitHub Pages serves at any path)."""
    prefix = '/' if absolute else '../' * depth
    home = '/' if absolute else (prefix or './')
    base = home if (depth or absolute) else ''
    canonical = DATA['url'] + '/' + path
    nav = ''.join(f'<a href="{base}#{key}">{label}</a>' for key, label in
                  [('about','About'), ('projects','Projects'), ('experience','Experience'), ('skills','Skills'), ('contact','Contact')])
    index_meta = '<meta name="robots" content="noindex">' if noindex else f'<link rel="canonical" href="{esc(canonical)}">'
    ld = f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>' if schema else ''
    return f'''<!doctype html>
<html lang="en" data-theme="dark"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(description)}"><meta name="theme-color" content="#090a12"><meta name="referrer" content="strict-origin-when-cross-origin">
{index_meta}<meta property="og:type" content="{og_type}"><meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{esc(canonical)}">
<meta property="og:image" content="{DATA['url']}/assets/og-image.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="Rohith Singhu — AI and Software Engineer">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(description)}"><meta name="twitter:image" content="{DATA['url']}/assets/og-image.png">
<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{prefix}assets/style.css">
<script>try{{const t=localStorage.getItem('theme');if(t==='light'||t==='dark')document.documentElement.dataset.theme=t;}}catch(e){{}}</script>
{ld}<script src="{prefix}assets/site.js" defer></script>
</head><body><a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="container header-inner"><a class="wordmark" href="{home}" aria-label="Rohith Singhu home">ROHITH<span> SINGHU</span><span aria-hidden="true">.</span></a>
<nav class="nav" id="main-nav" aria-label="Main navigation">{nav}</nav><div class="header-actions"><button class="theme-toggle" type="button" aria-label="Switch to light mode" aria-pressed="false"><svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M20.5 13.2A8.6 8.6 0 0 1 10.8 3.5 8.7 8.7 0 1 0 20.5 13.2Z"/></svg></button><button class="menu-toggle" type="button" aria-expanded="false" aria-controls="main-nav">Menu</button><a class="mini-cta" href="{base}#contact">LET'S TALK ↗</a></div></div></header>
<main id="main">{body}</main><footer class="site-footer"><div class="container footer-inner"><span>© 2026 Rohith Singhu · Cleveland, Ohio</span><span>Built with HTML, CSS & a little JavaScript. <a href="{base}#contact">Say hello ↗</a></span></div></footer></body></html>'''


def hero_graphic():
    return '''<div class="hero-art"><div class="system-map"><div class="map-top"><span>BUILD NOTES / RS</span><span>● AI + SOFTWARE</span></div>
<svg viewBox="0 0 420 310" role="img" aria-labelledby="system-title"><title id="system-title">Connecting retrieval, agents and software into a system people can inspect</title><defs><radialGradient id="orb"><stop stop-color="#a786ff" stop-opacity=".3"/><stop offset="1" stop-color="#a786ff" stop-opacity="0"/></radialGradient></defs>
<circle cx="210" cy="148" r="130" fill="url(#orb)"/><g stroke="#514469" fill="none"><ellipse cx="210" cy="148" rx="120" ry="52" transform="rotate(-32 210 148)"/><ellipse cx="210" cy="148" rx="120" ry="52" transform="rotate(32 210 148)"/><ellipse cx="210" cy="148" rx="50" ry="120"/><circle cx="210" cy="148" r="96" stroke-dasharray="3 9"/></g>
<g stroke="#8e72c3" fill="none"><path d="M83 60 178 125M337 64 244 125M210 182V245"/></g><g fill="#171628" stroke="#64517f"><rect x="28" y="31" width="111" height="44" rx="8"/><rect x="280" y="31" width="111" height="44" rx="8"/><rect x="142" y="244" width="137" height="44" rx="8"/><rect x="166" y="111" width="88" height="72" rx="17" stroke="#b495ff"/></g>
<g fill="#dfd4fa" font-family="Consolas,monospace" text-anchor="middle" font-size="11"><text x="84" y="58">RETRIEVAL</text><text x="336" y="58">AGENTS</text><text x="210" y="271">SOFTWARE</text><text x="210" y="157" font-size="29" font-weight="700">RS</text></g><g fill="#b495ff"><circle cx="93" cy="171" r="4"/><circle cx="285" cy="221" r="4"/></g><circle cx="301" cy="105" r="4" fill="#70dbba"/></svg>
<div class="map-bottom"><span>Evidence first</span><span>Human review</span><span>Clear interfaces</span></div></div><p class="art-note">A simple idea: make the system understandable.</p></div>'''


def tags(project):
    return '<div class="tags">' + ''.join(f'<span class="tag">{esc(t)}</span>' for t in project['stack']) + '</div>'


def media(project, prefix='', lazy=True):
    if project.get('screenshot'):
        src = project['screenshot'] if project['screenshot'].startswith('https://') else prefix + project['screenshot']
        label = 'Actual project screenshot'
        alt = project['name'] + (' triage proposal with human approval controls' if project['slug']=='verticaldesk' else ' evidence explorer showing the synthetic event investigation')
    else:
        src = prefix + 'assets/' + project['slug'] + '.svg'
        label = 'Workflow illustration'
        alt = project['name'] + ' workflow illustration, not an application screenshot'
    loading = ' loading="lazy" decoding="async"' if lazy else ' decoding="async"'
    return f'<div class="project-media"><img src="{esc(src)}" width="800" height="425" alt="{esc(alt)}"{loading}><span class="media-label">{esc(label)}</span></div>'


def card(project):
    slug=project['slug']
    case = f'projects/{slug}.html' if project.get('problem') else None
    title = f'<a href="{case}">{esc(project["name"])}</a>' if case else esc(project['name'])
    repo=DATA['github']+'/'+project['repo']
    source = '<span class="pending">Source private · on request</span>' if project.get('private') else external(repo,'GitHub ↗')
    demo = external(project['demo'],'Live demo ↗') if project.get('demo') else ''
    more = f'<a class="case-link" href="{case}">Case study →</a>' if case else ''
    return f'''<article class="project" data-category="{esc(project['category'])}">{media(project)}<div class="project-body"><div class="project-type">{esc(project['type'])}</div><h3>{title}</h3><p>{esc(project['summary'])}</p>{tags(project)}<div class="result-box">{''.join('<p>'+esc(r)+'</p>' for r in project['results'])}<p class="result-note">{esc(project['resultNote'])}</p></div><div class="project-links">{source}{demo}{more}</div></div></article>'''


def resume_button():
    if DATA.get('resume'):
        return f'<a class="button" href="{esc(DATA["resume"])}" target="_blank" rel="noopener">Resume PDF ↓</a>'
    return ''


def home():
    body=f'''<section class="hero container" aria-labelledby="hero-heading"><div class="availability">OPEN TO ENGINEERING OPPORTUNITIES</div><div class="hero-grid"><div><h1 id="hero-heading"><span>ROHITH</span>SINGHU.</h1><p class="hero-title">AI &amp; Software Engineer</p><p class="hero-copy">I build AI tools that connect useful answers to evidence — and the software that makes them usable.</p><div class="actions"><a class="button primary" href="#projects">Explore my work <span aria-hidden="true">↗</span></a>{resume_button()}</div><div class="socials">{external(DATA['github'],'GitHub ↗')}{external(DATA['linkedin'],'LinkedIn ↗')}<a href="#contact">Contact ↗</a></div></div>{hero_graphic()}</div><div class="hero-strip"><div><b>AI with evidence</b><span>RAG · Agents · Evaluation</span></div><div><b>Software around it</b><span>APIs · Interfaces · Tools</span></div><div><b>Systems in mind</b><span>Security · Operations · Support</span></div></div></section>
<section id="about" class="section"><div class="container about-grid"><div><div class="eyebrow">01 / A little context</div><h2>The person<br>behind the code.</h2></div><div class="about-copy"><p class="lead">I'm Rohith Singhu, a Software Developer at Viacore Technologies Inc. in Cleveland, Ohio, with an M.S. in Computer Science from Auburn University at Montgomery (2026). I build projects around document retrieval, agent workflows, and the practical checks that make AI outputs easier to trust.</p><p>Before Viacore, I interned at Tech Mahindra and worked as a Student IT Assistant at the AUM library. I'm focused on AI engineering, with software development, systems support, and security shaping how I approach the work.</p><div class="focus-list"><span class="tag">Evidence-grounded AI</span><span class="tag">Backend development</span><span class="tag">Human review</span><span class="tag">Systems thinking</span></div><p class="location">Cleveland, OH · Open to on-site, hybrid and remote roles · Willing to relocate</p></div></div></section>
<section id="projects" class="section"><div class="container"><div class="section-heading"><div><div class="eyebrow">02 / Selected work</div><h2>Built to be<br><span class="accent">looked into.</span></h2></div><p>Projects across AI, software and security. Each one links to the implementation or the evidence behind it.</p></div><div class="filters" role="group" aria-label="Filter projects" hidden>{''.join(f'<button class="filter" data-filter="{esc(c)}" aria-pressed="{str(c=="All").lower()}">{esc(c)}</button>' for c in ['All','AI & retrieval','Agents & tools','Security & systems'])}</div><p id="filter-status" class="visually-hidden" aria-live="polite"></p><div class="projects-grid">{''.join(card(p) for p in PROJECTS)}</div>
<article class="research"><div><div class="eyebrow">Published research / 2024</div><svg class="pose-art" viewBox="0 0 330 210" role="img" aria-label="Illustration of joint tracking in a human pose estimation pipeline"><g fill="none" stroke="#45395f"><path d="M30 30H10V60M300 30H320V60M30 180H10V150M300 180H320V150"/><rect x="70" y="15" width="190" height="180" rx="5" stroke-dasharray="3 6"/></g><g fill="none" stroke="#a989f5" stroke-width="3"><circle cx="165" cy="44" r="17"/><path d="M165 62V112M130 78H200M130 78 104 110 80 92M200 78 223 110 249 85M165 112 136 154 121 186M165 112 191 154 213 185"/></g><g fill="#70dbba">{''.join(f'<circle cx="{x}" cy="{y}" r="4"/>' for x,y in [(130,78),(200,78),(165,112),(104,110),(223,110),(136,154),(191,154)])}</g></svg><p class="small">Illustration</p></div><div><h3>{esc(PAPER['title'])}.</h3><p>I co-authored this paper on a Raspberry Pi system that uses OpenCV and MediaPipe to track exercise poses and provide audio feedback. It connects my robotics background with computer vision and software designed around a person's task.</p><div class="research-meta">{esc(PAPER['journal'])}, vol. {PAPER['volume']}, no. {PAPER['issue']}<br>Published July 11, 2024 · DOI: {external('https://doi.org/'+PAPER['doi'], PAPER['doi'])}</div>{external(PAPER['url'],'Read the paper ↗','class="button"')}</div></article></div></section>
<section id="skills" class="section"><div class="container"><div class="section-heading"><div><div class="eyebrow">03 / My toolkit</div><h2>What I work with.</h2></div><p>Tools reflected in my projects, internship and study. No proficiency percentages — the project evidence is a better starting point.</p></div><div class="skills-grid">{''.join(f'<div class="skill-group"><h3>{title}</h3><p>{text}</p></div>' for title,text in [('AI / ML','RAG · LangGraph · Embeddings · FAISS<br>Sentence-Transformers · Ollama · OpenCV · MediaPipe'),('Languages','Python · JavaScript · TypeScript<br>Java · SQL · HTML / CSS'),('Cloud / DevOps','AWS fundamentals · Docker<br>GitHub Actions · GitHub Pages'),('Security','CompTIA Security+ · Access reviews<br>Endpoint posture · Event correlation · MITRE ATT&CK'),('Backend / Data','FastAPI · Spring Boot · Node.js<br>SQLite FTS5 · MongoDB · REST APIs'),('Tools / Interfaces','Git · GitHub · VS Code<br>React · Angular · Streamlit · MCP')])}</div></div></section>
<section id="experience" class="section"><div class="container"><div class="section-heading"><div><div class="eyebrow">04 / Background</div><h2>Experience &amp; education.</h2></div><p>Software development, hands-on support and a foundation in computer science and robotics.</p></div><div class="timeline-grid"><div><div class="timeline-title">EXPERIENCE</div><div class="timeline"><article class="timeline-item"><div class="date">SEP 2026 – PRESENT</div><h3>Viacore Technologies Inc.</h3><p class="role">Software Developer</p></article><article class="timeline-item"><div class="date">JAN 2024 – JUN 2024</div><h3>Tech Mahindra</h3><p class="role">Software Intern</p><p>Worked with Angular, Spring Boot and Node.js during a software internship.</p></article><article class="timeline-item"><h3>AUM Library</h3><p class="role">Student IT Assistant</p><p>Supported technology needs in the university library.</p></article></div></div><div><div class="timeline-title">EDUCATION</div><div class="timeline"><article class="timeline-item"><div class="date">MAY 2026</div><h3>Auburn University<br>at Montgomery</h3><p class="role">M.S. Computer Science</p></article><article class="timeline-item"><h3>VIT-AP University</h3><p class="role">B.Tech Computer Science</p><p>Robotics specialization</p></article></div></div></div></div></section>
<section id="certifications" class="section"><div class="container"><div class="section-heading"><div><div class="eyebrow">05 / Credentials</div><h2>Certifications.</h2></div></div><div class="cert-grid">{''.join(cert(c,i) for i,c in enumerate(DATA['certifications']))}</div></div></section>
<section id="contact" class="contact"><div class="container"><div class="eyebrow">06 / Let's connect</div><h2>Good work starts<br>with a <span class="accent">conversation.</span></h2><p class="lead">Hiring for an AI or software engineering role, or want to talk about a project? I'd like to hear from you.</p><a class="email" href="mailto:{DATA['email']}">{DATA['email']}</a><div class="contact-bottom"><p>Based in Cleveland, Ohio.<br>Open to on-site, hybrid and remote work. Willing to relocate.</p><div class="socials">{external(DATA['linkedin'],'LinkedIn ↗')}{external(DATA['github'],'GitHub ↗')}<a href="mailto:{DATA['email']}">Email ↗</a></div></div></div></section>'''
    write('index.html',shell('Rohith Singhu | AI & Software Engineer','AI and software engineering projects by Rohith Singhu: retrieval, agent workflows, developer tools and security. Based in Cleveland, Ohio.',body,schema=home_schema()))


def cert(c, index):
    verify = external(c['verify'],'Verify credential ↗') if c.get('verify') else ''
    return f'<article class="cert"><div class="cert-icon" aria-hidden="true">{["S+","AWS"][index]}</div><div><div class="eyebrow">{esc(c["issuer"])}</div><h3>{esc(c["name"])}</h3><p>Earned {esc(c["earned"])}</p>{verify}</div></article>'


def svg_size(path):
    """Width/height from an SVG's root viewBox, so the <img> reserves space before it loads."""
    box = re.search(r'viewBox="[\d.]+ [\d.]+ ([\d.]+) ([\d.]+)"', path.read_text(encoding='utf-8'))
    return (round(float(box[1])), round(float(box[2]))) if box else (1200, 200)


def human_list(items):
    items = list(items)
    return items[0] if len(items) == 1 else ', '.join(items[:-1]) + ' and ' + items[-1]


def overview(project):
    """Self-contained, name-attributed answer block for AI answer engines."""
    return (f"{project['name']} is a project by {DATA['name']}, built with {human_list(project['stack'])}. "
            f"{project['summary']} Key result: {project['results'][0]}.")


def case_page(project, index):
    repo=DATA['github']+'/'+project['repo']
    project = dict(project)
    if project.get('private'):
        project['evidence'] = 'mailto:' + DATA['email'] + '?subject=VerticalDesk%20project%20walkthrough'
    source = '<span class="pending">Private source · contact me for access</span>' if project.get('private') else external(repo,'Explore the source ↗','class="button"')
    w, h = svg_size(ROOT / 'assets' / (project['slug'] + '-flow.svg'))
    workflow = '<figure class="mermaid-figure"><img src="../assets/'+project['slug']+'-flow.svg" alt="'+esc(' to '.join(project['workflow']))+f'" width="{w}" height="{h}" loading="lazy"><figcaption>Workflow rendered from the Mermaid source below.</figcaption></figure>'
    if project.get('screenshot'):
        screenshot = project['screenshot'] if project['screenshot'].startswith('https://') else '../' + project['screenshot']
        captures = f'<figure class="case-capture"><img src="{screenshot}" alt="VerticalDesk triage proposal and human approval controls" loading="lazy" width="947" height="600"><figcaption>Actual project screenshot, supplied through the repository README.</figcaption></figure>'
        if project.get('screenshot2'):
            captures += f'<figure class="case-capture"><img src="{project["screenshot2"]}" alt="VerticalDesk knowledge-base citations and drafted resolution" loading="lazy" width="931" height="600"><figcaption>Retrieved knowledge-base evidence and the drafted resolution.</figcaption></figure>'
    else:
        captures = f'<figure class="case-capture"><img src="../assets/{project["slug"]}.svg" alt="{esc(project["name"])} workflow illustration" width="800" height="425" loading="lazy"><figcaption>Architecture illustration based on the README.</figcaption></figure>'
    next_project=[p for p in PROJECTS if p.get('problem')][(index+1)%5]
    body=f'''<div class="container"><section class="case-hero"><a class="back" href="../#projects">← All projects</a><div class="eyebrow">{esc(project['type'])}</div><h1>{esc(project['name'])}<span class="accent">.</span></h1><p class="lead">{esc(project['headline'])}</p>{tags(project)}<p class="small">By {esc(DATA['name'])} · Updated <time datetime="{UPDATED}">{UPDATED_LABEL}</time></p><div class="actions">{source}{external(project['evidence'],'View project evidence ↗','class="button"')}</div></section><div class="case-layout"><nav class="case-aside" aria-label="Case study sections">{''.join(f'<a href="#{k}">{t}</a>' for k,t in [('overview','01 / Overview'),('problem','02 / Problem'),('approach','03 / Approach'),('workflow','04 / Workflow'),('screenshots','05 / Visuals'),('results','06 / Results'),('learning','07 / Reflection')])}</nav><div class="case-content"><section id="overview"><h2>What is {esc(project['name'])}?</h2><p>{esc(overview(project))}</p></section><section id="problem"><h2>What problem does {esc(project['name'])} solve?</h2><p>{esc(project['problem'])}</p></section><section id="approach"><h2>How does {esc(project['name'])} work?</h2><p>{esc(project['approach'])}</p></section><section id="workflow"><h2>The workflow.</h2>{workflow}<details><summary>View Mermaid diagram source</summary><pre><code>{esc(project['mermaid'])}</code></pre><p class="small">The diagram above is a simplified visual summary. This Mermaid source captures the branching workflow.</p></details></section><section id="screenshots"><h2>A closer look.</h2>{captures}</section><section id="results"><h2>Results, with context.</h2><div class="result-box">{''.join('<p>'+esc(r)+'</p>' for r in project['results'])}<p class="result-note">{esc(project['resultNote'])}</p></div><p>{esc(project['limits'])}</p><div class="evidence-panel"><div class="eyebrow">Check the source</div><p>These results come from the project README and linked artifacts.</p><p style="margin-top:14px">{external(project['evidence'],'Open the evidence ↗')}</p></div></section><section id="learning"><h2>What I learned.</h2><p>{esc(project['learning'])}</p><a class="next-project" href="{next_project['slug']}.html"><div><div class="eyebrow">Next case study</div><strong>{esc(next_project['name'])}</strong></div><span aria-hidden="true">↗</span></a></section></div></div></div>'''
    write('projects/'+project['slug']+'.html',shell(project['name']+' | Rohith Singhu',project['summary'],body,1,'projects/'+project['slug']+'.html',schema=case_schema(project),og_type='article'))


def project_graphic(project):
    labels = project.get('workflow') or ['CSV records','Review checks','Findings','Evidence']
    labels = labels[:5]
    accent={'violet':'#b795ff','cyan':'#67d5e3','mint':'#77dbc0','amber':'#efc77b'}[project['accent']]
    width=650/len(labels)
    boxes=''
    for i,label in enumerate(labels):
        x=75+i*width
        words=label.split(' ')
        first=' '.join(words[:2]); second=' '.join(words[2:])
        boxes+=f'<rect x="{x}" y="190" width="{width-12}" height="78" rx="9" fill="#191b2f" stroke="#393d58"/><text x="{x+14}" y="218" fill="{accent}" font-size="11">0{i+1}</text><text x="{x+14}" y="240" fill="#e7e8f3" font-size="11">{esc(first)}</text><text x="{x+14}" y="256" fill="#e7e8f3" font-size="11">{esc(second)}</text>'
        if i<len(labels)-1:
            boxes+=f'<path d="M{x+width-10} 229h10" stroke="{accent}" stroke-width="2"/>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="425" viewBox="0 0 800 425" role="img" aria-labelledby="t"><title id="t">{esc(project['name'])} workflow illustration</title><defs><pattern id="g" width="30" height="30" patternUnits="userSpaceOnUse"><path d="M30 0H0V30" fill="none" stroke="#22263d" stroke-width=".5"/></pattern></defs><rect width="800" height="425" fill="#111323"/><rect width="800" height="425" fill="url(#g)"/><circle cx="720" cy="48" r="140" fill="{accent}" opacity=".045"/><g font-family="Consolas,monospace"><text x="45" y="49" fill="{accent}" font-size="11" letter-spacing="2">{esc(project['type'])}</text><text x="45" y="108" fill="#f1effa" font-family="Arial,sans-serif" font-size="37" font-weight="700">{esc(project['name'])}</text><text x="45" y="140" fill="#a3a9c1" font-size="12">{esc(project['headline'])}</text>{boxes}<path d="M76 304H724" stroke="#2d3047"/><text x="76" y="334" fill="#9ca5bd" font-size="11">{esc(' / '.join(project['stack'][:3]))}</text><text x="76" y="364" fill="{accent}" font-size="10">README-BASED WORKFLOW / ILLUSTRATION</text></g></svg>'''


def results_text(p):
    return "; ".join([p["results"][0]] + [r[:1].lower() + r[1:] for r in p["results"][1:]])


def llms_txt():
    base = DATA['url']
    lines = [f'# {DATA["name"]}', '',
             f'> {DATA["name"]} is a Software Developer at Viacore Technologies Inc. (since Sep 2026) who builds AI tools that connect answers to evidence: document retrieval (RAG), agent workflows, human-review gates and the software around them. Based in Cleveland, Ohio.', '',
             'Software Developer at Viacore Technologies Inc. (Sep 2026 – present). Previously Software Intern at Tech Mahindra (Jan 2024 – Jun 2024) and Student IT Assistant at the AUM Library. '
             'M.S. Computer Science, Auburn University at Montgomery (May 2026); B.Tech Computer Science (robotics specialization), VIT-AP University. '
             'Certifications: ' + '; '.join(f'{c["name"]} ({c["earned"]})' for c in DATA['certifications']) + '. '
             f'Contact: {DATA["email"]}.', '',
             '## Profile', '',
             f'- [Portfolio home]({base}/): about, projects, experience, skills and certifications',
             f'- [GitHub]({DATA["github"]}): source code for the public projects',
             f'- [LinkedIn]({DATA["linkedin"]}): professional profile',
             f'- [Research paper](https://doi.org/{PAPER["doi"]}): "{PAPER["title"]}", {PAPER["journal"]}, vol. {PAPER["volume"]}, no. {PAPER["issue"]}, 2024 (co-author)', '',
             '## Projects', '']
    for p in PROJECTS:
        page = f'{base}/projects/{p["slug"]}.html' if p.get('problem') else f'{DATA["github"]}/{p["repo"]}'
        lines.append(f'- [{p["name"]}]({page}): {p["summary"]} Stack: {", ".join(p["stack"])}. Result: {results_text(p)}.')
    lines += ['', '## Optional', '', f'- [Full case-study text]({base}/llms-full.txt): every case study as plain text', f'- [Sitemap]({base}/sitemap.xml)', '']
    return '\n'.join(lines)


def llms_full_txt():
    """Full plain-text case studies, for AI systems that want more than the llms.txt index."""
    out = [llms_txt().split('## Optional')[0].rstrip(), '', '## Case studies', '']
    for p in PROJECTS:
        out += [f'### {p["name"]}', '', f'URL: {DATA["url"]}/projects/{p["slug"]}.html' if p.get('problem') else f'Source: {DATA["github"]}/{p["repo"]}',
                f'Type: {p["type"]} · Stack: {", ".join(p["stack"])}', '', p['summary'], '']
        for label, key in [('Problem','problem'),('Approach','approach'),('Limits','limits'),('What I learned','learning')]:
            if p.get(key):
                out += [f'{label}: {p[key]}', '']
        if p.get('workflow'):
            out += ['Workflow: ' + ' → '.join(p['workflow']), '']
        out += [f'Results: {results_text(p)}. {p["resultNote"]}', f'Evidence: {p["evidence"]}' if not p.get('private') else 'Evidence: private repository; walkthrough on request.', '']
    return '\n'.join(out)


def not_found():
    links = ''.join(f'<li><a href="/projects/{p["slug"]}.html">{esc(p["name"])}</a> — {esc(p["headline"])}</li>' for p in PROJECTS if p.get('problem'))
    body = f'''<section class="section"><div class="container"><div class="eyebrow">404 / Not found</div><h1>That page doesn't exist.</h1><p class="lead">The link may be old or mistyped. Try one of these instead:</p><ul class="not-found-list"><li><a href="/">Home: about, projects and experience</a></li>{links}</ul></div></section>'''
    write('404.html', shell('Page not found | Rohith Singhu', "This page does not exist. Browse Rohith Singhu's portfolio and case studies instead.", body, path='404.html', absolute=True, noindex=True))


def main():
    for p in PROJECTS:
        if not p.get('screenshot'):
            write('assets/'+p['slug']+'.svg',project_graphic(p))
    home()
    for i,p in enumerate(p for p in PROJECTS if p.get('problem')):
        case_page(p,i)
    not_found()
    urls=['']+['projects/'+p['slug']+'.html' for p in PROJECTS if p.get('problem')]
    write('sitemap.xml','<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+esc(DATA['url']+'/'+u)+'</loc><lastmod>'+UPDATED+'</lastmod></url>' for u in urls)+'</urlset>\n')
    write('robots.txt','User-agent: *\nAllow: /\nSitemap: '+DATA['url']+'/sitemap.xml\n')
    write('llms.txt',llms_txt())
    write('llms-full.txt',llms_full_txt())
    print('Built home + 5 case studies + 404 with shared assets.')


if __name__=='__main__':
    main()
