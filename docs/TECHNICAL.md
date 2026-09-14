# Technical guide

For people who want to build the database, run Scriptorium, or change the project. Everyday use needs none of this: see the [README](../README.md).

## Requirements

- **Python 3.10 or newer** ([python.org](https://www.python.org/downloads/); on Windows tick *Add python.exe to PATH*). On Windows, use `py` if `python` isn't recognised.
- About **1 GB** of free disk space: 350 MB of downloads plus the database.

## Build the database and run Scriptorium

From the project folder:

```
python -m pip install -r requirements.txt
python bibledb/download.py      # source data into bibledb/raw (resumable; skips files it already has)
python bibledb/build.py         # about 2 minutes; writes bibledb/bible.duckdb (~565 MB)
python bibledb/scriptorium.py   # opens http://127.0.0.1:8770 in your browser
```

Or double-click **Start Scriptorium (Windows).bat** / **Start Scriptorium (Mac).command**, which run these steps (skipping any already done).

Scriptorium also serves the Rainbow at `/rainbow/`. It keeps `bible.duckdb` open, so to rebuild from the command line close it first (Ctrl+C), or build to another file with `build.py --output`.

Scriptorium's **Data & setup** view (`/#setup`) does this for you: it shows how to start and stop Scriptorium, the database's size, build date, contents and licence status, and has buttons that run these jobs in the background, one at a time, with a live log:

| Button | Runs |
|---|---|
| Refresh the pages' data | the four `rainbow/build_*.py` scripts below |
| Rebuild the database | `build.py --output bibledb/bible.new.duckdb`, then swaps it in without restarting, then refreshes the pages |
| Get the latest data and rebuild | `download.py --refresh` (re-fetches the cross-reference votes and eBible.org catalogue), then as above |
| Make a shareable copy | `build.py --open-only --output bibledb/bible-shareable.duckdb` |

The API behind it: `GET /api/setup`, `GET /api/jobs` (status and log), and `POST /api/jobs` with `{"job": "pages" | "rebuild" | "update" | "shareable"}`, which requires the header `X-Scriptorium: 1` so other websites can't start jobs. `GET /api/ping` is the only endpoint that allows cross-origin reads: the static pages' **Scriptorium** link uses it to show whether Scriptorium is running and, if not, how to start it (`rainbow/scriptorium-link.js`).

**Sharing a database with others?** Build it with `python bibledb/build.py --open-only`. That leaves out the 25 texts whose licences forbid redistribution (non-commercial, no-derivatives, copyrighted, or unstated). See [DATA_LICENSES.md](../DATA_LICENSES.md).

## Regenerate the files the pages load

After rebuilding the database or changing authorship notes, red-letter rules, phrase settings or the translation list:

```
python rainbow/build_data.py     # rainbow/data.js: cross-references, KJV text, red letters, authorship
python rainbow/build_echoes.py   # rainbow/echoes-data.js: repeated phrases, Strong's entries
python rainbow/build_texts.py    # rainbow/texts/: the 29 English translations offered in the pages
python rainbow/build_study.py    # rainbow/study/: Hebrew/Greek words, lexicon and concordance for the reader
```

Run the tests with `python -m unittest discover -s tests -v`.

## Project layout

```
Open Reference Rainbow.html   one-click launcher for rainbow/index.html
Read the Bible.html           one-click launcher for rainbow/read.html
Start Scriptorium (…)         double-click starters: install DuckDB, download + build once, run Scriptorium
rainbow/                      static pages; no build step, work from file://
  index.html                  Reference Rainbow (WebGL 2)
  echoes.html                 Echoes: repeated phrases
  read.html                   Bible reader with verse study
  guide.html                  Guide
  morph.js                    plain-English grammar descriptions
  study/                      generated: per-book Hebrew/Greek words, lexicon.js, concordance.js
  translations.js             loads English translations on demand
  bookfilter.js               Books filter (testaments, categories, single books)
  data.js, echoes-data.js     generated data bundles
  texts/                      generated: manifest.js + one file per translation
  scriptorium-link.js         Scriptorium links: checks it's running, or shows how to start it
  build_data.py, build_echoes.py, build_texts.py, build_study.py
  buildutil.py                shared file writer for the build scripts
bibledb/                      database pipeline and Scriptorium
  download.py                 fetch sources into raw/
  build.py                    build bible.duckdb (--open-only for a shareable build)
  english_texts.py            extra English translations from eBible.org, with licences
  book_origins.py             authorship, dating and places, with citations
  red_letter.py               words of Jesus and of God
  phrases.py                  repeated-phrase search and transliteration
  scriptorium.py, web/        local, read-only browser app
tests/                        unit tests
docs/                         this guide
```

## What's in bible.duckdb

Every table and column has a description stored in the database; Scriptorium's **Tables** view shows them.

| Table | Contents |
|---|---|
| `books`, `verses` | 66 books (with categories: Law … Prophecy) plus 24 deuterocanonical books; 31,102 verses keyed by `verse_id` (KJV numbering), with red-letter flags |
| `translations`, `verse_text` | 152 texts in 57 languages (44 English) with licence, licence class, coverage and verse numbering |
| `ebible_catalog` | eBible.org's catalogue of 1,550 translations and their licences |
| `original_words` | 447,398 Hebrew, Aramaic and Greek words with transliteration, gloss, Strong's number and morphology |
| `strongs`, `lexicon_extended`, `verse_strongs` | Strong's dictionaries, STEPBible lexicons, Strong's numbers per verse |
| `translation_words` | KJV, WEB and BSB words tagged with Strong's numbers |
| `speech_spans` | Red letters by character position, with how each span was found |
| `phrase_length_stats`, `phrase_repeats`, `phrase_occurrences` | Repeated phrases of 7+ words, with transliterations and Strong's numbers |
| `cross_references` | OpenBible.info cross-references with vote counts |
| `book_authorship`, `book_authorship_sources`, `book_dating`, `places`, `scholarly_sources` | Who wrote each book, when and where: 143 views, 259 citations |
| `data_sources` | Provenance and licence of every dataset |

Example: John 3:16 in every text.

```sql
SELECT translation_id, language, text FROM v_passage WHERE osis_ref = 'John.3.16' ORDER BY language;
```

## Adding an English translation

1. Check its licence on eBible.org (`https://ebible.org/<id>/copyright.htm`); it must allow redistribution.
2. Add it to `bibledb/english_texts.py`.
3. Add a line for it to `CURATED` in `rainbow/build_texts.py`.
4. Run `download.py`, `build.py` and `build_texts.py`.
5. Record the licence in `DATA_LICENSES.md`.

## Releasing

See [CONTRIBUTING.md](../CONTRIBUTING.md#releasing-maintainers).
