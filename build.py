"""Builds the Curiosity & Learning website.

Add a new project: write a .md file in content/ (copy an existing one),
put its pictures in images/, then run:  python3 build.py
"""
import re, html, pathlib, markdown, math

ROOT = pathlib.Path(__file__).parent
OUT = ROOT
SITE_NAME = "Curiosity & Learning"
YEAR = 2026

# Subjects, in the order shown on the blog page. (slug, name, symbol)
SUBJECTS = [
    ("maths", "Maths", "∑"),
    ("philosophy", "Philosophy", "?"),
    ("statistics", "Statistics", "σ"),
    ("physics", "Physics", "F=ma"),
    ("biology", "Biology", "ATGC"),
    ("chemistry", "Chemistry", "H₂O"),
    ("english", "English", "Aa"),
    ("history", "History", "1066"),
    ("psychology", "Psychology", "ψ"),
    ("economics", "Economics", "£"),
    ("artificial-intelligence", "Artificial Intelligence", "P(y|x)"),
    ("engineering", "Engineering", "kN"),
]
SUBJECT = {s: (n, sym) for s, n, sym in SUBJECTS}

HOME_INTRO = [
    "My name is Aaryan Malik, and I’m 13 years old. This website shows a collection of the work I’ve been "
    "doing over time, including different ideas, experiments and finished pieces. It brings everything "
    "together in one place so you can see what I’ve worked on and the topics I’ve explored. The site acts "
    "as a record of my work and how it has developed, showing the range of things I’ve been involved in.",
    "On this website, you’ll find work related to a wide range of subjects and interests. These include "
    "areas such as philosophy, maths, chemistry, physics, biology, computer science and engineering, as "
    "well as other topics I’ve explored along the way. Each section reflects something I’ve been learning "
    "about or experimenting with, showing the variety of subjects I’m interested in. Together, they give "
    "an overview of the different fields I’ve spent time working on and thinking about.",
]

# ---------------------------------------------------------------- content
def load_posts():
    posts = []
    for f in sorted((ROOT / "content").glob("*.md")):
        raw = f.read_text(encoding="utf-8")
        head, body = raw.split("\n---\n", 1)
        meta = {}
        for line in head.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        meta["slug"] = f.stem
        meta["categories"] = [c.strip() for c in meta.get("categories", "").split(",") if c.strip()]
        meta["short"] = meta.get("short", meta["title"])
        meta["order"] = int(meta.get("order", 0))
        meta["body"] = body
        words = len(re.findall(r"\w+", body))
        meta["minutes"] = max(1, math.ceil(words / 200))
        for c in meta["categories"]:
            assert c in SUBJECT, f"{f.name}: unknown subject '{c}'"
        posts.append(meta)
    return posts

def figure(src, alt, kind):
    return (f'<figure class="fig fig-{kind}"><img src="images/{src}" alt="{html.escape(alt)}" '
            f'loading="lazy"></figure>')

def render_body(md_text):
    out, eq = [], []
    def flush_eq():
        if eq:
            out.append('\n<div class="equation">' + "".join(f"<div>{html.escape(e)}</div>" for e in eq) + "</div>\n")
            eq.clear()
    for line in md_text.splitlines():
        if line.startswith("@equation "):
            eq.append(line[10:].strip()); continue
        flush_eq()
        if line.startswith("@img "):
            parts = [p.strip() for p in line[5:].split("|")]
            out.append("\n" + figure(parts[0], parts[1], parts[2] if len(parts) > 2 else "full") + "\n")
        elif line.startswith("@quote "):
            out.append(f'\n<blockquote class="big-q"><p>{html.escape(line[7:].strip())}</p></blockquote>\n')
        elif line.startswith("@note "):
            out.append(f'\n<p class="note">{html.escape(line[6:].strip())}</p>\n')
        else:
            out.append(line)
    flush_eq()
    h = markdown.markdown("\n".join(out), extensions=["tables", "sane_lists"])
    h = h.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    h = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', h)
    return h

# ---------------------------------------------------------------- page shell
CSS = r"""
/* Layout: a clean exercise-book page. Narrow reading column, faint graph-paper ground on the home hero, mono labels for subjects. */
:root{
  --paper:#f5f7fb; --card:#ffffff; --ink:#1c2140; --ink-2:#4a5070; --muted:#7c8199;
  --line:#dde2ee; --grid:#e6eaf3; --accent:#2f5bd3; --accent-ink:#ffffff; --accent-soft:#e7edfc;
  --quote:#f0f3fb;
  --display:"Bricolage Grotesque", "Avenir Next", "Segoe UI", system-ui, sans-serif;
  --body:"Literata", Georgia, "Times New Roman", serif;
  --ui:"Bricolage Grotesque", "Avenir Next", "Segoe UI", system-ui, sans-serif;
  --mono:"IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --paper:#12152a; --card:#1a1e36; --ink:#e9ecf7; --ink-2:#b8bdd4; --muted:#8a90ab;
  --line:#2c3150; --grid:#1d2240; --accent:#7f9cf5; --accent-ink:#0f1430; --accent-soft:#232a4e;
  --quote:#1d2240; color-scheme:dark; } }
:root[data-theme="dark"]{
  --paper:#12152a; --card:#1a1e36; --ink:#e9ecf7; --ink-2:#b8bdd4; --muted:#8a90ab;
  --line:#2c3150; --grid:#1d2240; --accent:#7f9cf5; --accent-ink:#0f1430; --accent-soft:#232a4e;
  --quote:#1d2240; color-scheme:dark; }

*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--ui);font-size:17px;line-height:1.55}
a{color:var(--accent)}
a:focus-visible,button:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:4px}
img{max-width:100%;height:auto;display:block}
.wrap{max-width:1080px;margin:0 auto;padding-left:max(20px, env(safe-area-inset-left, 0px));padding-right:max(20px, env(safe-area-inset-right, 0px))}

/* header */
.site-head{border-bottom:1px solid var(--line);background:var(--paper)}
.site-head .wrap{display:flex;align-items:center;justify-content:space-between;gap:16px;padding-block:18px;flex-wrap:wrap}
.brand{font-family:var(--display);font-weight:700;font-size:1.15rem;color:var(--ink);text-decoration:none;letter-spacing:-.01em}
.brand span{color:var(--accent)}

.site-head nav ul{list-style:none;margin:0;padding:0;display:flex;gap:6px}
.site-head nav a{display:block;padding:8px 14px;border-radius:999px;color:var(--ink-2);text-decoration:none;font-weight:600;font-size:.98rem}
.site-head nav a:hover{color:var(--ink);background:var(--accent-soft)}
.site-head nav a[aria-current="page"]{color:var(--accent-ink);background:var(--accent)}

.site-foot{border-top:1px solid var(--line);margin-top:72px}
.site-foot .wrap{padding-block:28px;color:var(--muted);font-size:.9rem;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}

.eyebrow{font-family:var(--mono);font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0}
h1,h2,h3{font-family:var(--display);text-wrap:balance;letter-spacing:-.015em;color:var(--ink)}
.crumbs{font-family:var(--mono);font-size:.8rem;color:var(--muted);display:flex;flex-wrap:wrap;gap:8px;margin:36px 0 0}
.crumbs a{color:var(--muted);text-decoration:none}
.crumbs a:hover{color:var(--accent);text-decoration:underline}

/* home */
.hero{border-bottom:0}
.hero .wrap{display:grid;grid-template-columns:1.2fr .8fr;gap:56px;align-items:center;padding-block:72px 24px}
.hero h1{font-size:clamp(2.6rem,6vw,4.4rem);line-height:1;margin:12px 0 22px;font-weight:800}
.hero h1 em{font-style:normal;color:var(--accent)}
.hero p.lead{font-family:var(--body);font-size:1.08rem;color:var(--ink-2);max-width:60ch;margin:0 0 14px}
.hero-art img{width:100%;border-radius:12px}
.btn{display:inline-flex;align-items:center;gap:8px;margin-top:14px;background:var(--accent);color:var(--accent-ink);text-decoration:none;font-weight:700;padding:12px 20px;border-radius:999px}
.btn:hover{filter:brightness(1.08)}
.section-title{display:flex;align-items:baseline;justify-content:space-between;gap:12px;margin:56px 0 18px}
.section-title h2{font-size:1.5rem;margin:0}
.section-title a{font-weight:600;font-size:.95rem;text-decoration:none}

/* lists of posts */
.post-list{list-style:none;margin:0;padding:0;border-top:1px solid var(--line)}
.post-list li{border-bottom:1px solid var(--line)}
.post-list a{display:grid;grid-template-columns:1fr auto;gap:6px 24px;padding:22px 4px;text-decoration:none;color:inherit}
.post-list a:hover h3{color:var(--accent)}
.post-list h3{margin:0;font-size:1.22rem;transition:color .15s}
.post-list p{margin:0;grid-column:1;color:var(--ink-2);font-family:var(--body);font-size:.98rem;max-width:68ch}
.post-list .meta{grid-row:1/span 2;grid-column:2;align-self:center;font-family:var(--mono);font-size:.78rem;color:var(--muted);white-space:nowrap;text-align:right}
.series-label{font-family:var(--mono);font-size:.75rem;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin:0 0 4px}

/* blog subjects */
.page-head h1{font-size:clamp(2.2rem,5vw,3.4rem);margin:10px 0 8px;font-weight:800}
.page-head p{font-family:var(--body);color:var(--ink-2);margin:0;max-width:60ch}
.subjects{list-style:none;margin:40px 0 0;padding:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));column-gap:48px;border-top:1px solid var(--line)}
.subjects li{border-bottom:1px solid var(--line)}
.subject{display:grid;grid-template-columns:1fr auto 24px;align-items:center;gap:16px;padding:20px 4px;text-decoration:none;color:var(--ink)}
.s-name{font-family:var(--display);font-weight:600;font-size:1.2rem}
.s-count{font-size:.9rem;color:var(--muted)}
.s-arrow{color:var(--accent);font-weight:700;transition:transform .15s}
a.subject:hover .s-name{color:var(--accent)}
a.subject:hover .s-arrow{transform:translateX(4px)}
.subject.empty .s-name{color:var(--muted);font-weight:500}
@media (max-width:760px){.subjects{grid-template-columns:1fr}}

/* article */
.article-head{max-width:760px;margin:0 auto}
.article-head h1{font-size:clamp(2rem,4.6vw,3.1rem);line-height:1.08;margin:14px 0 14px;font-weight:800}
.article-head .summary{font-family:var(--body);font-size:1.12rem;color:var(--ink-2);margin:0 0 18px}
.tags{display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-size:.9rem;color:var(--muted);padding-bottom:28px;border-bottom:1px solid var(--line)}
.tag{color:var(--accent);text-decoration:none;font-weight:500}
.tag:hover{text-decoration:underline}
.article{max-width:760px;margin:36px auto 0;font-family:var(--body);font-size:1.06rem;line-height:1.72;color:var(--ink)}
.article::after{content:"";display:block;clear:both}
.article h2{font-size:1.55rem;line-height:1.2;margin:2.4em 0 .6em;padding-top:.9em;border-top:1px solid var(--line);clear:both}
.article h2:first-child{margin-top:0;border-top:0;padding-top:0}
.article h3{font-size:1.15rem;margin:1.6em 0 .4em}
.article p{margin:0 0 1em}
.article ul,.article ol{margin:0 0 1.2em;padding-left:1.3em}
.article li{margin:.3em 0}
.article li::marker{color:var(--accent)}
.article strong{font-weight:700}
.fig{margin:.4em 0 1.4em}
.fig img{border-radius:8px;border:1px solid var(--line)}
.fig-full{clear:both}
.fig-full img{width:100%}
.fig-side,.fig-side-small{float:right;margin:.3em 0 1em 28px}
.fig-side{width:42%}
.fig-side-small{width:32%}
.big-q{clear:both;margin:2.4em 0;padding:28px 30px;background:var(--quote);border-radius:10px}
.big-q p{margin:0;font-family:var(--display);font-weight:700;font-size:clamp(1.35rem,3vw,1.8rem);line-height:1.25;color:var(--ink);text-wrap:balance}
.big-q::before{content:"The big question";display:block;font-family:var(--mono);font-size:.75rem;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin-bottom:10px}
.equation{margin:0 0 1.2em;padding:16px 20px;border-left:3px solid var(--accent);background:var(--quote);border-radius:0 8px 8px 0;font-family:var(--mono);font-size:1rem;display:grid;gap:6px}
.note{font-family:var(--ui);font-size:.95rem;font-weight:600;padding:12px 16px;border-radius:8px;background:var(--accent-soft);color:var(--ink)}
.note::before{content:"⚠  ";}
.table-wrap{overflow-x:auto;margin:0 0 1.4em;border:1px solid var(--line);border-radius:8px;clear:both}
table{border-collapse:collapse;width:100%;font-family:var(--ui);font-size:.95rem;font-variant-numeric:tabular-nums}
th,td{padding:10px 14px;text-align:left;border-bottom:1px solid var(--line)}
th{background:var(--quote);font-weight:700}
tr:last-child td{border-bottom:0}
.more{max-width:760px;margin:64px auto 0}
.more h2{font-size:1.25rem;margin:0 0 12px}
.empty-state{margin-top:36px;padding:40px;border:1px dashed var(--line);border-radius:10px;color:var(--muted);text-align:center;font-family:var(--body)}

@media (max-width:760px){
  body{font-size:16px}
  .hero .wrap{grid-template-columns:1fr;gap:32px;padding-block:44px}
  .hero-art{max-width:360px}
  .fig-side,.fig-side-small{float:none;width:100%;max-width:340px;margin:.4em 0 1.2em}
  .post-list a{grid-template-columns:1fr}
  .post-list .meta{grid-row:auto;grid-column:1;text-align:left}
  .site-head nav a{padding:7px 11px}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,700;12..96,800'
         '&family=IBM+Plex+Mono:wght@400;500&family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,600;0,7..72,700;1,7..72,400&display=swap">')

def nav(active):
    items = [("index.html", "Home", "home"), ("about.html", "About", "about"), ("blog.html", "Blog", "blog")]
    lis = "".join(f'<li><a href="{h}"{" aria-current=\"page\"" if k == active else ""}>{t}</a></li>' for h, t, k in items)
    return (f'<header class="site-head"><div class="wrap"><a class="brand" href="index.html">Curiosity <span>&amp;</span> Learning</a>'
            f'<nav aria-label="Main"><ul>{lis}</ul></nav></div></header>')

FOOT = (f'<footer class="site-foot"><div class="wrap"><span>{html.escape(SITE_NAME)}</span>'
        f'<span>© {YEAR} Aaryan Malik</span></div></footer>')

def page(title, active, main, desc, full_doc=True):
    t = html.escape(title if title == SITE_NAME else f"{title} · {SITE_NAME}")
    inner = (f'<title>{t}</title>\n<meta name="description" content="{html.escape(desc)}">\n'
             f'<meta name="claude:viewport-fit-sides" content="cover">\n{FONTS}\n<style>{CSS}</style>\n'
             f'{nav(active)}\n<main>{main}</main>\n{FOOT}\n')
    if not full_doc:
        return inner
    head, body = inner.split(f"{nav(active)}", 1)
    return ('<!doctype html>\n<html lang="en-GB">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            f'{head}</head>\n<body>\n{nav(active)}{body}</body>\n</html>\n')

# ---------------------------------------------------------------- pages
def post_items(posts):
    lis = []
    for p in posts:
        series = f'<p class="series-label">{html.escape(p["series"])}</p>' if p.get("series") else ""
        lis.append(f'<li><a href="{p["slug"]}.html"><div>{series}<h3>{html.escape(p["short"])}</h3></div>'
                   f'<p>{html.escape(p["summary"])}</p><span class="meta">{p["minutes"]} min read</span></a></li>')
    return '<ul class="post-list">' + "".join(lis) + "</ul>"

def sort_posts(ps):
    return sorted(ps, key=lambda p: (p.get("series", p["title"]), p["order"], p["title"]))

def build(full_doc_home=True):
    OUT.mkdir(exist_ok=True)
    (OUT / "images").mkdir(exist_ok=True)
    for img in (ROOT / "source-images").iterdir():
        (OUT / "images" / img.name).write_bytes(img.read_bytes())
    posts = load_posts()
    by_cat = {s: sort_posts([p for p in posts if s in p["categories"]]) for s, _, _ in SUBJECTS}

    # home
    home = (f'<section class="hero"><div class="wrap"><div><p class="eyebrow">Welcome to my site</p>'
            f'<h1>Curiosity <em>&amp;</em> Learning</h1>'
            + "".join(f'<p class="lead">{html.escape(t)}</p>' for t in HOME_INTRO) +
            f'<a class="btn" href="blog.html">Explore the blog →</a></div>'
            f'<div class="hero-art"><img src="images/home-curiosity.jpg" alt="A colourful brain surrounded by symbols of science, art, maths and music"></div>'
            f'</div></section>')
    (OUT / "index.html").write_text(page(SITE_NAME, "home", home, "Aaryan Malik's projects in maths, science, philosophy and more.", full_doc_home), encoding="utf-8")

    # about
    about = ('<div class="wrap"><div class="page-head" style="margin-top:48px"><p class="eyebrow">About</p><h1>About me</h1>'
             '<p>This page is coming soon.</p></div></div>')
    (OUT / "about.html").write_text(page("About", "about", about, "About Aaryan Malik."), encoding="utf-8")

    # blog
    rows = []
    for slug, n, _sym in SUBJECTS:
        c = len(by_cat[slug])
        if c:
            rows.append(f'<li><a class="subject" href="blog-{slug}.html"><span class="s-name">{n}</span>'
                        f'<span class="s-count">{c} {"project" if c == 1 else "projects"}</span><span class="s-arrow" aria-hidden="true">→</span></a></li>')
        else:
            rows.append(f'<li><div class="subject empty"><span class="s-name">{n}</span><span class="s-count">Coming soon</span><span class="s-arrow"></span></div></li>')
    blog = ('<div class="wrap"><div class="page-head" style="margin-top:56px"><p class="eyebrow">Blog</p><h1>Subjects</h1>'
            '<p>Choose a subject to see my projects.</p></div>'
            f'<ul class="subjects">{"".join(rows)}</ul></div>')
    (OUT / "blog.html").write_text(page("Blog", "blog", blog, "Projects by subject."), encoding="utf-8")

    # subject pages
    for s, n, sym in SUBJECTS:
        ps = by_cat[s]
        body = post_items(ps) if ps else '<div class="empty-state">Nothing here yet. Projects are coming soon.</div>'
        main = (f'<div class="wrap"><nav class="crumbs" aria-label="Breadcrumb"><a href="blog.html">Blog</a><span>/</span><span>{n}</span></nav>'
                f'<div class="page-head" style="margin:14px 0 30px"><h1>{n}</h1><p>{len(ps)} {"project" if len(ps)==1 else "projects"}</p></div>{body}</div>')
        (OUT / f"blog-{s}.html").write_text(page(n, "blog", main, f"{n} projects."), encoding="utf-8")

    # posts
    for p in posts:
        first = p["categories"][0]
        tags = "".join(f'<a class="tag" href="blog-{c}.html">{SUBJECT[c][0]}</a>' for c in p["categories"])
        others = [q for q in by_cat[first] if q["slug"] != p["slug"]]
        more = (f'<section class="more"><h2>More in {SUBJECT[first][0]}</h2>{post_items(others)}</section>' if others else "")
        series = f'<p class="series-label" style="margin-top:22px">{html.escape(p["series"])}</p>' if p.get("series") else ""
        main = (f'<div class="wrap"><div class="article-head"><nav class="crumbs" aria-label="Breadcrumb"><a href="blog.html">Blog</a><span>/</span>'
                f'<a href="blog-{first}.html">{SUBJECT[first][0]}</a></nav>{series}'
                f'<h1>{html.escape(p["title"])}</h1><p class="summary">{html.escape(p["summary"])}</p>'
                f'<div class="tags">{tags}<span>· {p["minutes"]} min read</span></div></div>'
                f'<article class="article">{render_body(p["body"])}</article>{more}</div>')
        (OUT / f'{p["slug"]}.html').write_text(page(p["title"], "blog", main, p["summary"]), encoding="utf-8")
    return posts

if __name__ == "__main__":
    import sys
    ps = build(full_doc_home="--preview" not in sys.argv)
    print(f"Built {len(ps)} projects into {OUT}")
