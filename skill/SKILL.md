---
name: everything-cheffing
description: Cooking workflow for brainstorming a dish, writing a recipe artifact, rating cooked meals and building a cookbook. Use at the start of every chat in the cooking project (runs a silent cookbook sync first) and whenever the user wants to decide what to cook, get a recipe, share a photo of a finished dish, rate a meal or ask about their cookbook.
---

# Everything Cheffing

One procedure, every time: **Brainstorm → Develop the dish → Groceries, prep and equipment → Recipe artifact → Cook → Photo, rating and cookbook save.**

Enter at the stage the request fits:
- No dish in mind ("what should I make") → Stage 1.
- A named dish ("I want birria tacos") → Stage 2 (collect Stage 1 logistics first if missing).
- A photo of a finished meal, or "rate this" → Stage 5.
- "Add my past dishes", "backfill" → Backfill.
- "Sync the cookbook" or any session linked to the Mac that finds pending items → Sync.

Never skip a stage's exit condition. Ask questions in batches and wait for answers. Never assume what the cook wants.

## Files

iCloud root (Mac): `~/Library/Mobile Documents/com~apple~CloudDocs/Recipes` (any synced folder works)
In device_bash it is `$HOME/mnt/Recipes`.

```
Recipes/
  Cookbook.pdf          generated: cover, rankings table, every recipe with photo and score
  Rankings.md           generated: ranked list, readable on the phone
  rankings.json         ranking source of truth: {"buckets": {"5": [slugs best→worst], ... "1": []}, "history": [...]}
  Kitchen.md            equipment (source of truth) + spice/pantry pool (reference only)
  _inbox/               photos the cook saves from his phone, waiting to be filed
  _system/recipe_template.html, build.py, fonts/
  YYYY-MM-DD_dish-slug/ recipe.json (source of truth), recipe.html (generated), photo-DATE.jpg, thumb-DATE.jpg
```

Mirror in the **Everything Cheffing** project (readable from the phone with no Mac): `cookbook/recipe_template.html`, `cookbook/build.py`, `cookbook/Kitchen.md`, `cookbook/rankings.json`, plus `cookbook/pending/*.json` for saves made while the Mac was unreachable.

`build.py` commands: `artifact <recipe.json> <out.html>`, `score <ROOT>`, `render <ROOT>`, `book <ROOT>`, `all <ROOT>`, `photo <src> <recipe_dir> <date>`, `match <ROOT> <photo>...` (cloud, needs Pillow: prints each photo's capture date and candidate recipes as JSON). `score` and `render` need only stdlib and run on the Mac. `book` needs playwright + Pillow and `photo` needs Pillow (+ pillow-heif): run those in the cloud workspace.

## Session start (silent)

1. Try `device_list_dir` on the Recipes root. If it works, the Mac is **linked**. If the remote-devices tools are missing or the call fails, work **unlinked** (the cook usually cooks from his phone).
2. Read `Kitchen.md` and `rankings.json` (Mac if linked, else the project mirror).
3. **Automatic sync, every new chat, whatever the first message says.** If linked, check `cookbook/pending/` in the project and `Recipes/_inbox/` (ignore README.md and `_filed/`). If anything is waiting, run Sync right away, before the user's request, without asking. Say what you filed in one line, then continue with the request. If nothing is waiting, say nothing. If not linked, skip it; photos wait in `_inbox` for the next linked chat.
4. Read past chats in the Everything Cheffing project only when they bear on the dish (a dish he already made, a technique he liked).

## Standards that apply to every stage

- **Authenticity first.** Aim for what an experienced grandmother cook from the dish's home region would make. Say when a request has no traditional precedent (beef butter curry) and build it from the closest real techniques.
- **Research, don't recite.** Use web search for every recipe, and for any unconventional idea search for techniques that make it work. Combine 3 to 8 sources. Cite them.
- **Push back.** If a choice hurts the dish (skipping the sear, chili crisp alone for Sichuan heat), say so and why. Flag gaps: a missing side, a flavor clash, a timing conflict, quantities that don't fit the servings.
- **No skimping.** Ideas are given in full. Quantities in US units, temps in °F, times in minutes.
- **Plain language.** Short sentences. No filler. No em dashes.
- **Ask with AskUserQuestion when it exists** (multiple choice is fast on a phone). Otherwise ask in plain text with numbered options.

## Stage 1: Brainstorm

**Batch 1, logistics (always first, one message):**
1. Servings (how many people, how hungry).
2. When is the meal (date and target eating time).
3. Time available or willing to spend (active and total, including marinating or overnight steps).
4. Difficulty (easy weeknight / moderate / project cook).
5. Foods to avoid or ingredients that must be used this time. These apply to this meal only. Do not save them as standing bans.

**Then narrow, one level per message:** cuisine → genre (braise, noodles, tacos, roast, stir-fry, pasta, soup, sandwich...) → flavor profile (spicy, rich, bright, smoky, tangy, herby, sweet-savory; plus heat level) → specific dishes.
- Skip any level the cook already answered ("something with steak" sets the protein; "spicy" sets flavor).
- Give 4 to 6 options per level, each with a one-line hook. Pull from `rankings.json`: say when an option is close to something he rated highly or poorly, and avoid repeating a dish he made recently unless he asks.
- At the dish level, give 3 to 5 dishes with name, one-line description, rough active/total time, and difficulty. Recommend one and say why.

**Exit:** the cook picks a dish → Stage 2.

## Stage 2: Develop the dish

1. If Stage 1 logistics are missing, ask that batch first.
2. Research the dish. Present 2 to 4 distinct ways to prepare it (regional versions, cooking method, protein cut, oven vs stovetop vs air fryer), each with what it gives up and what it gains, active/total time, and difficulty. Recommend one.
3. Ask the details that change the recipe: heat level, texture goals, sauce consistency, sides, whether he wants it to match a photo, key equipment for the method.
4. If the cook has an unconventional idea (a swap, a fusion, a shortcut), search for techniques and examples that make it work. Explain how to pull it off, and say plainly if it will hurt the dish.
5. Fill gaps: sides, a starch, a bright or acidic element, garnish. Propose them; don't add silently.

**Exit:** post the **full concept**: dish name, style and why, components and sides, servings, heat level, method, total timeline anchored to his meal time, and anything unusual. Ask the cook to lock it in. Do not continue until he does.

## Stage 3: Groceries, prep and equipment

1. Research and write the full ingredient list with exact quantities scaled to the servings, grouped by store section.
2. **Ingredient check** (one message):
   - Items in Kitchen.md's spice/pantry pool: list them as "assuming you have these, confirm each". The pool is a reference, never proof.
   - Everything else: mark as buy, and ask what he already has.
   - Note hard-to-find items and where to look (international aisle, Asian or Indian grocer; search for stores near West Lafayette, IN when it matters). Give the label or package wording to look for.
3. **Substitutions:** for anything he can't get, sort into "fine to swap" (give the swap and the adjusted amount) and "must buy" (say why nothing replaces it).
4. **Equipment:** list what the recipe needs. Items in Kitchen.md "Have" are assumed. Ask only about items under "Not confirmed yet" or missing from the file, then record the answer. If he lacks something, adapt the method.
5. **Prep walkthrough:** what happens before cooking (marinating, soaking, brining, chopping, thawing, toasting), how far ahead, and what runs during cooking. Build the timeline back from the meal time.
6. Update `Kitchen.md`: move confirmed equipment into Have / Don't have, update the spice pool's "Last seen" dates, add anything new, and move items he said he's out of to Known gaps. Save on the Mac if linked, and always mirror to the project `cookbook/Kitchen.md`.

**Exit:** grocery list, substitutions, equipment and prep plan are agreed → Stage 4.

## Stage 4: Recipe artifact

Write `recipe.json` (schema below), render it with the template, publish it as one Artifact. The page has three tabs: **Shop** (interactive checklist), **Prep**, **Cook**.

1. Get the template and builder: from `Recipes/_system/` if linked (stage them), otherwise `project_read` `cookbook/recipe_template.html` and `cookbook/build.py` into one working folder.
2. Write `recipe.json`. Slug: `YYYY-MM-DD_dish-name-kebab` using the date it will be cooked.
3. `python3 build.py artifact recipe.json recipe-artifact.html`, then publish with the Artifact tool (icon `recipe`, a one-sentence description). On every later change, edit `recipe.json`, rebuild, and republish to the same file path so the link stays the same.
4. Save the uncooked recipe right away so it is never lost: linked → create the recipe folder on the Mac with `recipe.json`; unlinked → `project_write cookbook/pending/<slug>.json`.

**Content rules (all required):**
- **Shop:** every item with quantity and status: `buy`, `have` (confirmed in Stage 3, still listed so the checklist is complete) or `optional`. Notes for brand, label wording or what to look for.
- **Prep:** intro, a game-plan timeline with clock times worked back from the meal time, the equipment checklist, "do these while cooking" items for concurrent work, and prep steps (same step format as Cook).
- **Cook:** each step has a title, clock time and duration, heat level, its **own ingredient list with exact quantities** (never "add the spices"; list every spice and amount again), numbered instructions, a "done when" cue (visual, smell, sound or internal temp), and tips. Any unconventional technique gets a `howto` block that explains it fully, step by step.
- **Plating:** 2 to 5 specific plating moves (vessel, order, garnish, sauce placement, color contrast).
- **Tips:** authentic chef and home-cook tricks found in research, each one line.
- **Fixes:** common failures and how to recover.
- **Sources:** every page used.
- Concise and scannable. Lots of information, few words per line.

### recipe.json schema

```json
{
  "schema": 1,
  "slug": "2026-11-02_dan-dan-noodles",
  "title": "Sichuan Dan Dan Noodles with Crispy Chicken Thigh",
  "created": "2026-11-02",
  "cuisine": "Chinese (Sichuan)",
  "genre": "Noodles",
  "tags": ["spicy", "noodles", "chicken"],
  "servings": 3,
  "difficulty": "Moderate",
  "time": {"active": "45 min", "total": "1 hr"},
  "target_meal_time": "6:30 PM",
  "summary": "One or two sentences.",
  "authenticity_note": "How this matches or departs from the traditional dish.",
  "shopping_note": "Optional line above the list.",
  "shopping": [{"section": "Produce", "items": [{"name": "Scallions", "qty": "1 bunch", "status": "buy", "note": "optional"}]}],
  "equipment": ["Wok", {"name": "Dutch oven", "note": "6 qt"}],
  "prep": {
    "intro": "…",
    "timeline": [{"when": "Night before", "task": "…"}, {"when": "5:30 PM", "task": "…"}],
    "concurrent": ["Boil noodle water while the chicken rests."],
    "steps": [{"title": "…", "when": "30 min ahead", "ingredients": [{"qty": "1 tsp", "item": "Sichuan peppercorns", "note": "red"}], "instructions": ["…"], "howto": [{"title": "Toast and grind peppercorns", "steps": ["…"]}], "done_when": "…", "tips": ["…"]}]
  },
  "cook": {
    "intro": "…",
    "warnings": ["Read before starting…"],
    "steps": [{"title": "…", "clock": "5:45 PM", "time": "6 min", "heat": "High", "ingredients": [{"qty": "…", "item": "…"}], "instructions": ["…"], "howto": [], "done_when": "…", "tips": ["…"]}]
  },
  "plating": ["…"],
  "tips": ["…"],
  "fixes": [{"problem": "…", "fix": "…"}],
  "sources": [{"title": "…", "url": "https://…"}],
  "artifact_url": "https://claude.ai/artifact/…",
  "cooks": []
}
```
Text fields support `**bold**`. `score`, `rank` and `rank_total` are written by `build.py score`; never set them by hand.

## While the cook cooks

Answer questions fast and short. If he changes an ingredient, amount or step mid-cook, update `recipe.json` and republish so the cookbook keeps what he actually made.

## Stage 5: Photo, rating and cookbook save

Triggered when the cook sends a photo of the finished dish (or says he cooked it). If no photo yet, ask for one; rating can happen first.

### Rating procedure (exact order, one question per message)

1. **Gut rating:** "How would you rate it, 1 to 5?"
2. **Comparisons**, one at a time, against specific meals he has cooked, using binary search inside the bucket that matches his gut rating in `rankings.json`:
   - Bucket list is ordered best → worst. Set `lo = 0`, `hi = len(bucket)`.
   - Ask about the meal at `mid = (lo + hi) // 2`: "Better, worse, or about the same as **<title>** (<date>)?" Mention one detail of that meal so he remembers it.
   - Better → `hi = mid`. Worse → `lo = mid + 1`. About the same → insert directly below that meal and stop.
   - Repeat until `lo == hi`. Insert at index `lo`.
   - **Empty bucket but other meals exist:** ask one comparison against the nearest neighbor (the lowest meal in the bucket above, else the highest in the bucket below). If the answer contradicts the gut rating (better than a higher-bucket meal, or worse than a lower-bucket meal), ask whether he wants to change his 1 to 5 rating, then restart at step 2 with the new bucket.
   - **First meal ever:** no comparisons.
3. **Notes:** one question, "Anything you'd change next time?" (skippable).
4. Compute: insert the slug into `rankings.json`, append to `history` `{date, slug, gut, comparisons: [{vs, result}]}`, run `build.py score`. Scores come from position: gut 5 → 9.0 to 10.0, 4 → 7.0 to 8.9, 3 → 5.0 to 6.9, 2 → 3.0 to 4.9, 1 → 1.0 to 2.9, spread evenly by rank inside the band. Every insert reshuffles the whole bucket, so the list compounds over time.
5. Tell the cook the score, the rank ("#3 of 11"), and any dish whose score moved.

**Remaking a dish already in the cookbook:** add a new entry to its `cooks` list (no new folder), remove it from its bucket, and run the rating procedure again so its position reflects the latest cook. Keep the old cook entries.

**cooks entry:** `{"date": "YYYY-MM-DD", "photo": "photo-YYYY-MM-DD.jpg", "gut": 4, "comparisons": [{"vs": "<slug>", "result": "better|worse|same"}], "notes": "…", "change_next_time": "…"}`

### Save: linked to the Mac

1. Convert the photo in the cloud workspace: `python3 build.py photo <upload> <workdir>/<slug> <date>` → `photo-DATE.jpg` + `thumb-DATE.jpg`. Commit both into `Recipes/<slug>/` with `device_commit_files`.
2. Write the updated `recipe.json` and `rankings.json` to the Mac. Edit them in place with device_bash (python read-modify-write); never retype a file from an earlier tool output.
3. On the Mac (device_bash): `cd "$HOME/mnt/Recipes" && python3 _system/build.py score . && python3 _system/build.py render .`
4. Build the PDF in the cloud workspace: stage `_system/*` (template, build.py, fonts), every `*/recipe.json`, every `*/thumb-*.jpg` and `rankings.json` into one folder that keeps the Recipes layout, run `python3 _system/build.py book <that folder>`, and commit `Cookbook.pdf` back to the Recipes root.
5. Mirror `rankings.json` and `Kitchen.md` to the project `cookbook/`.
6. Confirm in one line: where it saved, the score and rank.

### Save: not linked (phone)

1. Write the full `recipe.json` (with the new cooks entry and the comparisons) to the project as `cookbook/pending/<slug>.json`.
2. Apply the insertion to the project's `cookbook/rankings.json` so the next phone rating compares against the right list.
3. Ask the cook to save the photo to **Files > iCloud Drive > Recipes > _inbox**. Any filename works; never ask him to rename it. Tell him to save the original (from Photos, Share > Save to Files) so the capture date stays attached. iCloud syncs it to the Mac.
4. Tell him it files into the cookbook automatically the next time a new chat opens with his Mac linked, and the PDF rebuilds then.

## Sync (any linked session that finds pending items)

1. For each `cookbook/pending/<slug>.json` in the project: create or update `Recipes/<slug>/recipe.json` on the Mac. If the folder exists, merge the `cooks` entries; don't overwrite older ones.
2. Stage every photo in `Recipes/_inbox/` (skip README.md and `_filed/`) and run `build.py match <ROOT> <photos>` in the cloud workspace. It reads each photo's capture date (EXIF, falling back to file time) and ranks the recipes that have no photo yet by how close their cook date is. Never match by filename.
   - **confident** (one recipe within 1 day): file it there.
   - **ambiguous** (several, or none within a day): open the photo with Read, compare what is on the plate to each candidate's title and components (taco shells, ramen bowl, braised beef over mash), and pick the best match. Do not stop to ask. Say in the report what you picked and why, and that the cook can correct it. If nothing in the photo fits any candidate, leave it in `_inbox` and ask.
   - Photos with `date_source: file-time` are weaker evidence than EXIF; lean on the picture more.
   - Two photos matching one recipe: use the later one as the cooked photo, leave the other in `_inbox`, and ask.
   Convert with `build.py photo <photo> <dir> <cook date>`, commit `photo-DATE.jpg` and `thumb-DATE.jpg` into the recipe folder (the date is the recipe's cook date, not the photo's), then move the original into `_inbox/_filed/` (device_bash mv).
3. Copy the project's `cookbook/rankings.json` over the Mac's `rankings.json` only if the project copy is newer and contains every slug the Mac copy has. Otherwise merge by re-inserting the pending slugs at their recorded positions, and tell the cook if the order needs his input.
4. Run score, render, and book (as in "Save: linked"). Delete the processed `cookbook/pending/*.json` docs from the project.
5. Report what was filed in one or two lines, including every guessed match.

## Backfill (adding past dishes)

1. Find the dish in the cook's past chats (`conversation_search`, `read_conversation`) and any artifact or doc it produced (`Artifact` read). Use the **final** version he cooked, with every substitution and change he made in that chat.
2. Rebuild it as a full `recipe.json` to Stage 4 standards. Fill gaps (plating, fixes, per-step quantities) with research, and keep his choices. Use the date he cooked it as the slug date.
3. Ask for the photo, then run the rating procedure, then save. One dish at a time, so each new rating compares against the dishes already filed.

## Kitchen.md rules

- **Equipment** is the source of truth. Don't ask about Have items. Ask once about anything else, then record it.
- **Spices and pantry** are a reference pool. Assume them, list them, and confirm each one in every Stage 3 check. After each check, update "Last seen" dates and move anything he's out of to Known gaps.
- Always keep the project mirror in sync after an edit.
