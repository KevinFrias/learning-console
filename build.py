#!/usr/bin/env python3
"""Build a fully-static HTML portal from the pages/ directory."""

import shutil, json
from pathlib import Path

BASE = Path(__file__).parent
SRC_PAGES = BASE / "pages"
OUT = BASE / "site"

PAGE_EXT = {".html", ".htm"}

# ---------- templates ----------
HOME_TPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>HTML Portal</title>
<style>
  :root {{ --bg:#0b0d13; --bg2:#12151f; --bg3:#1a1e2c; --border:#262c3f; --text:#e7eaf0; --muted:#6f7995; --accent:#6ee7ff; }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ font-family:system-ui,Segoe UI,Inter,sans-serif; background:var(--bg); color:var(--text); min-height:100vh; padding:40px 28px; }}
  header {{ margin-bottom:34px; }}
  h1 {{ font-size:14px; letter-spacing:.3em; text-transform:uppercase; color:var(--accent); }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:16px; }}
  a.card {{ display:block; background:var(--bg2); border:1px solid var(--border); border-radius:10px; padding:24px 20px; text-decoration:none; color:var(--text); transition:transform .12s,border-color .15s,background .15s; }}
  a.card:hover {{ transform:translateY(-2px); border-color:#3d455e; background:var(--bg3); }}
  .card .name {{ font-size:20px; font-weight:600; word-break:break-word; }}
  .card .meta {{ margin-top:8px; font-size:13px; color:var(--muted); }}
  .empty {{ color:var(--muted); padding:40px 20px; text-align:center; }}
</style>
</head>
<body>
  <header><h1>HTML Portal</h1></header>
  <div class="grid">
    {cards}
  </div>
</body>
</html>"""

DIR_TPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{title} — HTML Portal</title>
<style>
  :root {{ --bg:#0b0d13; --bg2:#12151f; --bg3:#1a1e2c; --border:#262c3f; --text:#e7eaf0; --muted:#6f7995; --accent:#6ee7ff; }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ font-family:system-ui,Segoe UI,Inter,sans-serif; background:var(--bg); color:var(--text); min-height:100vh; padding:40px 28px; }}
  a {{ color:var(--accent); text-decoration:none; }}
  a:hover {{ text-decoration:underline; }}
  h1 {{ font-size:14px; letter-spacing:.3em; text-transform:uppercase; color:var(--accent); margin-bottom:8px; }}
  .crumb {{ color:var(--muted); font-size:13px; margin-bottom:22px; }}
  .title {{ font-size:42px; font-weight:700; margin-bottom:8px; letter-spacing:-.02em; line-height:1.1; }}
  .meta {{ color:var(--muted); margin-bottom:22px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); gap:14px; }}
  a.card {{ display:flex; justify-content:space-between; align-items:center; background:var(--bg2); border:1px solid var(--border); border-radius:8px; padding:18px 18px; text-decoration:none; color:var(--text); transition:transform .12s,border-color .15s,background .15s; }}
  a.card:hover {{ transform:translateY(-1px); border-color:#3d455e; background:var(--bg3); }}
  .card .name {{ font-size:16px; font-weight:500; }}
  .card .fn {{ font-size:12px; color:var(--muted); font-family:ui-monospace,Menlo,monospace; }}
  .empty {{ color:var(--muted); padding:40px 20px; text-align:center; border:1px dashed var(--border); border-radius:8px; }}
</style>
</head>
<body>
  <h1>HTML Portal</h1>
  <div class="crumb"><a href="/">← Directories</a></div>
  <div class="title">{dir_name}</div>
  <div class="meta">{n} page{n_s}</div>
  <div class="grid">
    {cards}
  </div>
</body>
</html>"""


def build():
    # wipe out dir
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    if not SRC_PAGES.exists():
        print("No pages/ directory found.")
        return

    dirs = sorted([d for d in SRC_PAGES.iterdir() if d.is_dir()])
    directories = []
    for d in dirs:
        pages = sorted([f for f in d.iterdir() if f.is_file() and f.suffix.lower() in PAGE_EXT])
        if not pages:
            continue
        directories.append((d.name, pages))

    if not directories:
        print("No directories with HTML files found.")
        return

    # --- home ---
    cards = "\n    ".join(
        f'<a class="card" href="{name}/"><div class="name">{name}</div><div class="meta">{len(pages)} page{"s" if len(pages)!=1 else ""}</div></a>'
        for name, pages in directories
    )
    (OUT / "index.html").write_text(HOME_TPL.format(cards=cards), encoding="utf-8")

    # --- per-directory indexes + page copies ---
    for name, pages in directories:
        out_dir = OUT / name
        out_dir.mkdir(parents=True, exist_ok=True)
        cards = "\n    ".join(
            f'<a class="card" href="{p.name}"><div class="name">{p.stem}</div><div class="fn">{p.name}</div></a>'
            for p in pages
        )
        n = len(pages)
        (out_dir / "index.html").write_text(
            DIR_TPL.format(
                title=name, dir_name=name,
                n=n, n_s="s" if n != 1 else "",
                cards=cards
            ), encoding="utf-8"
        )
        for p in pages:
            shutil.copy2(p, out_dir / p.name)

    print(f"Built static site → {OUT}")
    print("\nDirectory layout:")
    for p in sorted(OUT.rglob("*")):
        if p.is_file():
            print(f"  {p.relative_to(OUT)}")


if __name__ == "__main__":
    build()
