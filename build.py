#!/usr/bin/env python3
"""Cookbook builder for a folder of recipes.

Layout (ROOT = the Recipes folder):
  ROOT/Kitchen.md
  ROOT/Rankings.md            (generated)
  ROOT/Cookbook.pdf           (generated)
  ROOT/rankings.json          (source of truth for ranking order)
  ROOT/_system/recipe_template.html, build.py, fonts/
  ROOT/_inbox/                (photos dropped from phone, waiting to be filed)
  ROOT/<YYYY-MM-DD>_<slug>/recipe.json, recipe.html (generated), photo-<date>.jpg

Commands:
  python3 build.py artifact <recipe.json> <out.html>   page to publish as an Artifact (no doctype)
  python3 build.py score <ROOT>                        recompute 1-10 scores from rankings.json
  python3 build.py render <ROOT>                       write recipe.html into every recipe folder
  python3 build.py book <ROOT>                         write Cookbook.pdf (needs playwright)
  python3 build.py all <ROOT>                          score + render + book
  python3 build.py photo <src_image> <recipe_dir> <YYYY-MM-DD>   photo-<date>.jpg + thumb-<date>.jpg (HEIC ok)

score and render need only the Python standard library, so they run on the Mac directly.
book needs playwright + Pillow; photo needs Pillow (+ pillow-heif for HEIC).

Scoring: each cooked dish sits in the bucket of its latest 1-5 gut rating, ordered best to worst
by head-to-head comparisons. Bucket bands: 5 -> 9.0-10.0, 4 -> 7.0-8.9, 3 -> 5.0-6.9,
2 -> 3.0-4.9, 1 -> 1.0-2.9. Position i (0 = best) of n in a band scores
hi - (hi - lo) * (i + 0.5) / n, rounded to 0.1. Every insert reshuffles the scores of the
whole bucket, so scores compound as the list grows.
"""
import base64
import datetime as dt
import html
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "recipe_template.html"
FONTS = HERE / "fonts"
BANDS = {5: (9.0, 10.0), 4: (7.0, 8.9), 3: (5.0, 6.9), 2: (3.0, 4.9), 1: (1.0, 2.9)}
OWNER = os.environ.get("COOKBOOK_OWNER", "")
BOOK_TITLE = os.environ.get("COOKBOOK_TITLE", "My Cookbook")


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def dump(p, obj):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


def recipe_dirs(root):
    root = Path(root)
    return sorted(d for d in root.iterdir() if d.is_dir() and not d.name.startswith(("_", ".")) and (d / "recipe.json").exists())


def safe_json(obj):
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")


def fill(recipes, cfg):
    tpl = TEMPLATE.read_text(encoding="utf-8")
    title = recipes["title"] if isinstance(recipes, dict) else cfg.get("title", BOOK_TITLE)
    return (tpl.replace("__TITLE__", html.escape(title))
               .replace("__RECIPE_JSON__", safe_json(recipes))
               .replace("__RENDER_CONFIG__", safe_json(cfg)))


def font_faces():
    faces = [("Gloock", "gloock-latin-400-normal.woff2", 400, "normal"),
             ("IBM Plex Sans", "ibm-plex-sans-latin-400-normal.woff2", 400, "normal"),
             ("IBM Plex Sans", "ibm-plex-sans-latin-400-italic.woff2", 400, "italic"),
             ("IBM Plex Sans", "ibm-plex-sans-latin-500-normal.woff2", 500, "normal"),
             ("IBM Plex Sans", "ibm-plex-sans-latin-600-normal.woff2", 600, "normal"),
             ("IBM Plex Mono", "ibm-plex-mono-latin-400-normal.woff2", 400, "normal"),
             ("IBM Plex Mono", "ibm-plex-mono-latin-600-normal.woff2", 600, "normal")]
    out = []
    for fam, fn, w, st in faces:
        p = FONTS / fn
        if p.exists():
            b = base64.b64encode(p.read_bytes()).decode()
            out.append(f"@font-face{{font-family:'{fam}';src:url(data:font/woff2;base64,{b}) format('woff2');font-weight:{w};font-style:{st};}}")
    return "<style>" + "".join(out) + "</style>"


def wrap_document(body, inline_fonts=False):
    head = '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
    if inline_fonts:
        head += font_faces()
        body = "\n".join(l for l in body.splitlines() if "fonts.googleapis.com" not in l and "fonts.gstatic.com" not in l)
    return head + "</head><body>\n" + body + "\n</body></html>\n"


# ---------- commands ----------

def cmd_artifact(recipe_json, out_html):
    r = load(recipe_json)
    Path(out_html).write_text(fill(r, {"mode": "app"}), encoding="utf-8")
    print(f"artifact page -> {out_html}")


def cmd_score(root):
    root = Path(root)
    rp = root / "rankings.json"
    rk = load(rp) if rp.exists() else {"buckets": {str(k): [] for k in range(5, 0, -1)}, "history": []}
    by_slug = {d.name: d for d in recipe_dirs(root)}
    scores = {}
    order = []
    for g in range(5, 0, -1):
        slugs = [s for s in rk["buckets"].get(str(g), []) if s in by_slug]
        rk["buckets"][str(g)] = slugs
        lo, hi = BANDS[g]
        n = len(slugs)
        for i, s in enumerate(slugs):
            scores[s] = round(hi - (hi - lo) * (i + 0.5) / n, 1)
            order.append(s)
    total = len(order)
    for s, d in by_slug.items():
        r = load(d / "recipe.json")
        if s in scores:
            r["score"] = scores[s]
            r["rank"] = order.index(s) + 1
            r["rank_total"] = total
        else:
            for k in ("score", "rank", "rank_total"):
                r.pop(k, None)
        dump(d / "recipe.json", r)
    rk["updated"] = dt.date.today().isoformat()
    dump(rp, rk)
    lines = ["# Rankings", "", f"Updated {rk['updated']}. Score bands: gut 5 = 9.0-10, 4 = 7.0-8.9, 3 = 5.0-6.9, 2 = 3.0-4.9, 1 = 1.0-2.9.", "",
             "| # | Dish | Score | Gut | Last cooked | Folder |", "|---|---|---|---|---|---|"]
    for i, s in enumerate(order, 1):
        r = load(by_slug[s] / "recipe.json")
        last = (r.get("cooks") or [{}])[-1]
        lines.append(f"| {i} | {r['title']} | {scores[s]:.1f} | {last.get('gut', '')}/5 | {last.get('date', '')} | {s} |")
    uncooked = [s for s in by_slug if s not in scores]
    if uncooked:
        lines += ["", "## Not cooked or not rated yet", ""] + [f"- {load(by_slug[s] / 'recipe.json')['title']} ({s})" for s in uncooked]
    (root / "Rankings.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"scored {total} dishes; {len(uncooked)} unrated")
    for i, s in enumerate(order, 1):
        print(f"  {i:>2}. {scores[s]:4.1f}  {s}")


def cmd_render(root):
    for d in recipe_dirs(root):
        r = load(d / "recipe.json")
        (d / "recipe.html").write_text(wrap_document(fill(r, {"mode": "app"})), encoding="utf-8")
        print(f"rendered {d.name}/recipe.html")


def pdf_photo(src, cache):
    """Downsize a photo for the PDF so the book stays small."""
    from PIL import Image
    cache.mkdir(parents=True, exist_ok=True)
    out = cache / (src.parent.name + "__" + src.stem + ".jpg")
    if out.exists() and out.stat().st_mtime >= src.stat().st_mtime:
        return out
    im = Image.open(src)
    im = im.convert("RGB")
    im.thumbnail((1400, 1400))
    im.save(out, "JPEG", quality=82)
    return out


def cmd_book(root):
    root = Path(root).resolve()
    build = HERE / "_build"
    build.mkdir(exist_ok=True)
    recipes, bases = [], {}
    dirs = recipe_dirs(root)
    for d in dirs:
        r = load(d / "recipe.json")
        cooks = r.get("cooks") or []
        ph = cooks[-1].get("photo") if cooks else None
        if ph:
            thumb = d / ph.replace("photo-", "thumb-", 1)
            src = thumb if thumb.exists() else (d / ph if (d / ph).exists() else None)
            if src:
                small = pdf_photo(src, build / "photos")
                r = json.loads(json.dumps(r))
                r["cooks"][-1]["photo"] = small.name
                bases[r["slug"]] = "photos/"
        recipes.append(r)
    # ranked first (best to worst), then uncooked by date
    recipes.sort(key=lambda r: (r.get("rank") is None, r.get("rank") or 0, r.get("created", "")))
    cfg = {"mode": "cookbook", "title": BOOK_TITLE, "owner": OWNER, "updated": dt.date.today().strftime("%B %-d, %Y"), "photoBases": bases}
    page = build / "cookbook.html"
    page.write_text(wrap_document(fill(recipes, cfg), inline_fonts=True), encoding="utf-8")
    from playwright.sync_api import sync_playwright
    out = root / "Cookbook.pdf"
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.emulate_media(color_scheme="light")
        pg.goto(page.as_uri())
        pg.wait_for_timeout(400)
        pg.pdf(path=str(out), format="Letter", print_background=True,
               margin={"top": "0.6in", "bottom": "0.6in", "left": "0.6in", "right": "0.6in"},
               display_header_footer=True, header_template="<span></span>",
               footer_template='<div style="font-size:8px;width:100%;text-align:center;color:#888;font-family:monospace"><span class="pageNumber"></span> / <span class="totalPages"></span></div>')
        b.close()
    print(f"Cookbook.pdf -> {out} ({len(recipes)} recipes)")


def cmd_photo(src, recipe_dir, date):
    """Write photo-<date>.jpg (2400px) and thumb-<date>.jpg (1400px, for the PDF) into recipe_dir."""
    from PIL import Image, ImageOps
    try:
        import pillow_heif
        pillow_heif.register_heif_opener()
    except ImportError:
        pass
    d = Path(recipe_dir)
    d.mkdir(parents=True, exist_ok=True)
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    full = im.copy(); full.thumbnail((2400, 2400))
    full.save(d / f"photo-{date}.jpg", "JPEG", quality=88)
    th = im.copy(); th.thumbnail((1400, 1400))
    th.save(d / f"thumb-{date}.jpg", "JPEG", quality=80)
    print(f"photo -> {d / f'photo-{date}.jpg'} and thumb-{date}.jpg")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit(1)
    c = a[0]
    if c == "artifact": cmd_artifact(a[1], a[2])
    elif c == "score": cmd_score(a[1])
    elif c == "render": cmd_render(a[1])
    elif c == "book": cmd_book(a[1])
    elif c == "all": cmd_score(a[1]); cmd_render(a[1]); cmd_book(a[1])
    elif c == "photo": cmd_photo(a[1], a[2], a[3])
    else: print(__doc__); sys.exit(1)
