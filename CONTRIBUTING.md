# Contributing

Thanks for helping. Corrections from people who know the texts and the scholarship are the most valuable
contributions this project can get.

## Reporting a data problem

Open an issue with the **Data correction** template. Include:

- the passage or book (e.g. *Exodus 3:5*, *Daniel*);
- what is shown and what it should be;
- **a source**, for anything about authorship, dates or places: an ancient text with a locator, or a published
  introduction or commentary with page numbers.

Common cases:

| Problem | Where it lives |
|---|---|
| Authorship, date or place of a book; a missing scholarly view | `bibledb/book_origins.py` |
| Words of God coloured wrongly (dark red) | detection rules in `bibledb/red_letter.py` |
| Words of Jesus coloured wrongly (red) | comes from eBible.org's markup; report it upstream too |
| A wrong cross-reference or vote | OpenBible.info's data; report it there |
| A wrong Hebrew/Greek word, gloss or Strong's number | STEPBible's data; report it there |

## Working on the code

```
git clone <this repository>
cd <folder>
python -m pip install -r requirements.txt
python bibledb/download.py        # ~350 MB, once
python bibledb/build.py           # ~1 minute
python bibledb/scriptorium.py     # http://127.0.0.1:8770
python rainbow/build_data.py      # after changing book_origins.py or red_letter.py
python rainbow/build_echoes.py    # after changing phrases.py or rebuilding the database
python rainbow/build_texts.py     # after changing the translation list or rebuilding the database
python -m unittest discover -s tests -v
```

- **Pages** (`rainbow/*.html`, `bibledb/web/index.html`) are plain HTML, CSS and JavaScript, with no build step and no
  frameworks. Keep them working when opened straight from disk (`file://`).
- **Python** is the standard library plus DuckDB. Target Python 3.10+.
- **Regenerated data files** (`rainbow/data.js`, `rainbow/echoes-data.js`, `rainbow/texts/`): commit them in the same pull request as the
  change that produced them.
- **Licences:** only add data whose licence allows redistribution, and record it in `DATA_LICENSES.md`.
- **Changelog:** add a line under *Unreleased* in `CHANGELOG.md`.

## Releasing (maintainers)

1. Move the *Unreleased* notes in `CHANGELOG.md` under a new version heading.
2. Update `VERSION` and `version:` / `date-released:` in `CITATION.cff`.
3. Commit, then tag: `git tag -a v0.2.0 -m "v0.2.0"` and `git push --follow-tags`.
4. On GitHub, create a Release from the tag and paste the changelog section.
