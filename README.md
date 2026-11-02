# Recipe Cookbook Builder

Turn a folder of recipes into a ranked, clickable PDF cookbook, and cook from the same recipe data on your phone.

Each recipe is one `recipe.json` file. The builder renders it three ways:

- **App page**: a mobile page with three tabs (Shop, Prep, Cook), a tappable grocery checklist, per-step ingredients and a "keep screen on" button.
- **Print page**: everything expanded, no controls.
- **Cookbook PDF**: every recipe in one book, sorted best to worst, with a clickable rankings table.

The repo also includes the Claude skill that drives the whole workflow (brainstorm, recipe, cook, photo, rating).

## What you get

- A grocery list with status chips: buy, confirm you have it, optional.
- A prep timeline, including steps that run alongside cooking.
- Step cards with the exact ingredients and quantities for that step, timing, a "done when" cue, tips, fixes and sources.
- A score from 1 to 10 for every dish you cook. Scores come from head-to-head comparisons, so the ranking re-sorts as your list grows.
- A PDF with a rankings table. Click a dish to jump to its page. Click "Rankings" on any recipe to jump back.
- Full photos. Nothing is cropped.

## Layout

```
build.py               the builder (score, render, book, photo)
recipe_template.html   the page template, shared by app, print and PDF
fonts/                 Gloock, IBM Plex Sans, IBM Plex Mono (inlined into the PDF)
skill/SKILL.md         the Claude skill that runs the cooking workflow
example/               a sample cookbook folder with one recipe
```

Your own cookbook folder (called ROOT below) looks like this:

```
ROOT/
  rankings.json                    ranking order, best to worst, per gut-rating bucket
  Rankings.md                      generated table
  Cookbook.pdf                     generated book
  2026-11-01_red-wine-braised-beef/
    recipe.json                    the source of truth
    recipe.html                    generated
    photo-2026-11-01.jpg           full photo
    thumb-2026-11-01.jpg           smaller photo used in the PDF
```

Folder names are `YYYY-MM-DD_slug`. Folders that start with `_` or `.` are ignored.

## Setup

`score` and `render` use only the Python 3 standard library.

`book` and `photo` need extra packages:

```bash
pip install playwright pillow pillow-heif
playwright install chromium
```

`pillow-heif` is only needed for iPhone HEIC photos.

## Usage

Run from anywhere. Point each command at your ROOT folder.

```bash
# Try the example
python3 build.py all example

# Individual steps
python3 build.py score  ROOT      # recompute scores from rankings.json, write Rankings.md
python3 build.py render ROOT      # write recipe.html into every recipe folder
python3 build.py book   ROOT      # write ROOT/Cookbook.pdf
python3 build.py all    ROOT      # score + render + book

# Match photos to recipes by capture date (prints JSON, needs Pillow)
python3 build.py match ROOT photo1.jpg photo2.heic

# File a photo for a recipe (makes photo-DATE.jpg and thumb-DATE.jpg)
python3 build.py photo IMG_1234.HEIC ROOT/2026-11-01_red-wine-braised-beef 2026-11-01

# Page to publish somewhere as a mobile recipe page
python3 build.py artifact ROOT/<recipe>/recipe.json out.html
```

Set the book title and author name with environment variables:

```bash
COOKBOOK_TITLE="Sam's Cookbook" COOKBOOK_OWNER="Sam Lee" python3 build.py book ROOT
```

## Recipe format

`recipe.json` holds these top-level keys. See `example/` for a full file.

| Key | Contents |
|---|---|
| `slug`, `title`, `created` | Identity. `slug` matches the folder name. |
| `cuisine`, `genre`, `tags`, `servings`, `difficulty`, `time` | Header and chips. |
| `summary`, `authenticity_note` | Short description and what is traditional versus adapted. |
| `shopping` | Sections of items: `name`, `qty`, `status` (`buy`, `have`, `optional`), `note`. |
| `equipment` | List of tools. |
| `prep` | `intro`, `timeline`, `concurrent`, `steps`. |
| `cook` | `warnings` and `steps`. Each step has `title`, `time`, `heat`, `ingredients`, `instructions`, `done_when`, `tips`, `howto`. |
| `plating`, `tips`, `fixes`, `sources` | Plating notes, general tips, problem and fix pairs, links. |
| `cooks` | One entry per time you cooked it: `date`, `photo`, `gut` (1 to 5), `comparisons`, `notes`, `change_next_time`. |
| `score`, `rank`, `rank_total` | Written by `build.py score`. Do not edit. |

## Photo matching

`build.py match` reads each photo's capture date (EXIF, then file time) and ranks the recipes that have no photo yet by how close their cook date is.

- `confident`: exactly one recipe is within 1 day of the photo.
- `ambiguous`: several recipes, or none within a day. Decide by looking at the photo.

Photos sent in chat are filed directly, so matching is optional. Use it for loose photos that arrive without context. Filenames are never used, so photos can keep their camera names. Keep originals, not screenshots, so the capture date stays attached.

## How scoring works

1. After cooking, give the dish a gut rating from 1 to 5. That picks its bucket in `rankings.json`.
2. Compare it to dishes already in that bucket, one at a time, to find its position (best to worst).
3. `build.py score` turns position into a 1 to 10 score. Each bucket owns a band:

| Gut | Score band |
|---|---|
| 5 | 9.0 to 10.0 |
| 4 | 7.0 to 8.9 |
| 3 | 5.0 to 6.9 |
| 2 | 3.0 to 4.9 |
| 1 | 1.0 to 2.9 |

Position `i` (0 is best) of `n` dishes in a band scores `hi - (hi - lo) * (i + 0.5) / n`, rounded to one decimal. Every new dish reshuffles the scores in its bucket, so the ranking stays consistent as the cookbook grows.

`rankings.json` looks like this:

```json
{
  "buckets": { "5": ["slug-a", "slug-b"], "4": ["slug-c"], "3": [], "2": [], "1": [] },
  "history": [],
  "updated": "2026-11-01"
}
```

## The Claude skill

`skill/SKILL.md` runs the full workflow in a Claude session:

1. **Brainstorm**: narrow cuisine, genre, flavors and dish. Ask about difficulty, time, servings, meal time and foods to avoid.
2. **Develop the dish**: settle on variants, research unconventional ideas, finish with a full concept.
3. **Groceries and equipment**: build the list and confirm what you already have. Spices are confirmed every time.
4. **Recipe page**: publish the three-tab page.
5. **Photo, rating and cookbook save**: send the photo in chat, run the rating questions, rebuild `Cookbook.pdf`, commit and push.

### Cloud-only setup (no computer needed)

The skill keeps your whole cookbook in a private GitHub repo that Claude clones at the start of each chat. Your own computer is never involved, so you can cook, send the photo and rate from your phone.

1. Create an empty **private** repo for your cookbook. Keep it separate from this public builder repo, because it holds your photos.
2. Copy `build.py`, `recipe_template.html` and `fonts/` into `_system/` in that repo, and put your `Kitchen.md` at the root.
3. Install `skill/SKILL.md` as a Claude skill and replace `<owner>/<cookbook-repo>` with your repo.
4. In Claude Code on the web, attach the repo with push access when a chat asks for it.

After each cooked dish, Claude converts the photo, updates `recipe.json` and `rankings.json`, rebuilds `Cookbook.pdf` and pushes. Open the PDF from the repo in the GitHub app or ask Claude to send it.

The skill assumes a `Kitchen.md` file listing your equipment and a pool of spices. It is not included here because it is personal.

## Notes

- The example photo is a generated placeholder.
- The PDF is Letter size with 0.6 inch margins.
- The page template loads fonts from Google Fonts in the browser. The PDF inlines the files in `fonts/`, so it builds offline.

## License

MIT for the code. Fonts are under the SIL Open Font License 1.1.
