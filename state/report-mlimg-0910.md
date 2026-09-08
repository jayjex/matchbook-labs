# ML image fix — 2026-09-10

Task: replace old-bucket R2 image URLs (09036907-ed43-467f-b927-1bf75b922bd6) still referenced in matchbook-labs pages with new-store images (e2c48e03 bucket) or local backup covers.

## Result

- Before: 40 occurrences of bucket 09036907 across 17 HTML files
- After: 0 occurrences
- 29 URLs swapped to new-store bucket e2c48e03 (newimgs from live API, priority 1)
- 21 URLs swapped to local `img/*.png` backup covers (post-rework covers; pending_review products have no public API images)

## Method

1. Product context per file from getly.store product href (already mapped to new slugs); catalog/index cards matched by filename + card href.
2. Replacement priority: newimgs[newslug] (live API) > oldimgs[oldslug] (post-rework cover) > local backup cover from money-mission artifacts / getly-backup-0909.
3. og:image: none present in affected files; no e2c48e03 og tags touched.

## Notes

- Intermediate pass accidentally doubled `images/api/` prefix in 29 replaced URLs; caught and fixed same session (`images/api/images/api/` -> `images/api/`), grep-verified 0 remaining.
- 10 new local covers added under `img/` (wedding planner, 40-social templates, web3 icon/logo packs, homestead journal, case-files puzzle book, crypto trader desk kit, dark tech humor stickers, wallpaper vol3 sample, superteam free sample).
- R2 old bucket still serves 200; remaining swap was done anyway for consistency since correct covers existed locally.
- README untouched. Journal/STATUS untouched.

## Verify

- Sample 10 files: all img src = e2c48e03 bucket or local img/ file. 10/10 pass.
- grep 09036907 across repo: 0.
