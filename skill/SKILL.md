---
name: everything-cheffing
description: Cooking workflow for brainstorming a dish, writing a recipe artifact, rating cooked meals and building a cookbook. Use at the start of every chat in the cooking project (loads the cookbook repo first) and whenever the user wants to decide what to cook, get a recipe or grocery list, shares a photo of a finished dish, rates a meal or asks about their cookbook or rankings.
---

# Cooking workflow

One procedure, every time: **Brainstorm → Develop the dish → Groceries, prep and equipment → Recipe artifact → Cook → Photo, rating and cookbook save.**

Enter at the stage the request fits:
- No dish in mind ("what should I make") → Stage 1.
- A named dish ("I want birria tacos") → Stage 2 (collect Stage 1 logistics first if missing).
- A photo of a finished meal, or "rate this" → Stage 5.
- "Add my past dishes", "backfill" → Backfill.

Never skip a stage's exit condition. Ask questions in batches and wait for answers. Never assume what the cook wants.

## Files

Everything lives in the private GitHub repo **<owner>/<cookbook-repo>** (create it yourself, set it to Private, and replace these placeholders). No Mac needed. Working copy: the folder where the repo is cloned (called `REPO` below).

```
<cookbook-repo>/
  Cookbook.pdf          generated: cover, rankings table, every recipe with photo and score
  Rankings.md           generated: ranked list
  rankings.json         ranking source of truth: {"buckets": {"5": [slugs best→worst], ... "1": []}, "history": [...]}
  Kitchen.md            equipment (source of truth) + spice/pantry pool (reference only)
  _system/              recipe_template.html, build.py, fonts/, SKILL.md (copy of this skill)
  YYYY-MM-DD_dish-slug/ recipe.json (source of truth), recipe.html (generated), photo-DATE.jpg, thumb-DATE.jpg
```

`build.py` commands (run from the repo root): `artifact <recipe.json> <out.html>`, `score .`, `render .`, `book .` (needs playwright + Pillow), `all .`, `photo <src> <recipe_dir> <date>` (needs Pillow, plus pillow-heif for HEIC), `match . <photo>...` (optional: ranks recipes by how close their cook date is to a photo's capture date).

## Session start (silent)

1. Make sure the repo is in this session and cloned. If `REPO` exists, run `git -C /home/claude/everything-cheffing- pull --ff-only`. Otherwise attach the repo with push access (in Claude Code on the web that is the `add_repo` tool), clone it with a long timeout and register the clone. If attaching is denied, ask the user to name the repo in chat and retry.
2. Read `Kitchen.md` and `rankings.json` from the repo.
3. Read past chats in the cooking project only when they bear on the dish (a dish he already made, a technique he liked).

## Committing

After any change to the repo: `git add -A`, commit (use the user's git identity, preferably their GitHub noreply address), push to main. If the push is rejected, `git pull --rebase` and push again. Say in one line what was saved.

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
   - Note hard-to-find items and where to look (international aisle, Asian or Indian grocer; search for stores near the user's location when it matters). Give the label or package wording to look for.
3. **Substitutions:** for anything he can't get, sort into "fine to swap" (give the swap and the adjusted amount) and "must buy" (say why nothing replaces it).
4. **Equipment:** list what the recipe needs. Items in Kitchen.md "Have" are assumed. Ask only about items under "Not confirmed yet" or missing from the file, then record the answer. If he lacks something, adapt the method.
5. **Prep walkthrough:** what happens before cooking (marinating, soaking, brining, chopping, thawing, toasting), how far ahead, and what runs during cooking. Build the timeline back from the meal time.
6. Update `Kitchen.md`: move confirmed equipment into Have / Don't have, update the spice pool's "Last seen" dates, add anything new, and move items he said he's out of to Known gaps. Commit it to the repo.

**Exit:** grocery list, substitutions, equipment and prep plan are agreed → Stage 4.

## Stage 4: Recipe artifact

Write `recipe.json` (schema below), render it with the template, publish it as one Artifact. The page has three tabs: **Shop** (interactive checklist), **Prep**, **Cook**.

1. The template and builder are in `_system/` of the repo.
2. Write `recipe.json`. Slug: `YYYY-MM-DD_dish-name-kebab` using the date it will be cooked.
3. `python3 _system/build.py artifact <slug>/recipe.json recipe-artifact.html`, then publish with the Artifact tool (icon `recipe`, a one-sentence description). On every later change, edit `recipe.json`, rebuild, and republish to the same file path so the link stays the same.
4. Save the uncooked recipe right away so it is never lost: write `<slug>/recipe.json` in the repo and commit.

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

### Save (always the same, no Mac needed)

1. Photo: the cook sends it in this chat. Convert it: `python3 _system/build.py photo <upload> <slug> <cook date>` → `photo-DATE.jpg` + `thumb-DATE.jpg` in the recipe folder. If he sends several, open them and use the best one. If no photo yet, save everything else and ask for it; when it arrives, file it the same way.
2. Update `<slug>/recipe.json` (new `cooks` entry with gut, comparisons, notes) and `rankings.json` (insertion plus `history`).
3. `python3 _system/build.py all .` (score, render, PDF).
4. Commit and push (see Committing).
5. Confirm in one line: the score and rank. Offer to send Cookbook.pdf with SendUserFile only if he asks.

If he sends a photo with no context ("here's dinner"), work out which recipe it is from the picture and recent cook dates (`build.py match . <photo>` helps). State what you picked.

## Backfill (adding past dishes)

1. Find the dish in the user's past chats (`conversation_search`, `read_conversation`) and any artifact or doc it produced (`Artifact` read). Use the **final** version he cooked, with every substitution and change he made in that chat.
2. Rebuild it as a full `recipe.json` to Stage 4 standards. Fill gaps (plating, fixes, per-step quantities) with research, and keep his choices. Use the date he cooked it as the slug date.
3. Ask for the photo, then run the rating procedure, then save. One dish at a time, so each new rating compares against the dishes already filed.

## Kitchen.md rules

- **Equipment** is the source of truth. Don't ask about Have items. Ask once about anything else, then record it.
- **Spices and pantry** are a reference pool. Assume them, list them, and confirm each one in every Stage 3 check. After each check, update "Last seen" dates and move anything he's out of to Known gaps.
