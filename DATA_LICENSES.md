# Data licences and attribution

The project's own code and writing are under the [MIT licence](LICENSE). The data it uses comes from other people,
under their own terms. This page lists every source, what it may be used for, and what you owe when you share it.

> This is a practical summary, not legal advice. Each source's own licence text is the authority.

## 1. Files committed to this repository

These ship in the download so the pages work without building anything.

| File | Contains | Licence of the file | Attribution required |
|---|---|---|---|
| `rainbow/data.js` | OpenBible.info cross-references and vote scores; King James Version text; words-of-Jesus markup; detected words of God; authorship and dating summaries | **CC BY 4.0** (because of the cross-references) | OpenBible.info |
| `rainbow/echoes-data.js` | Repeated phrases in Hebrew, Aramaic and Greek, with glosses and transliterations from STEPBible; Septuagint words; Strong's dictionary entries (Open Scriptures edition) | **CC BY-SA 4.0** (the Strong's entries are share-alike) | STEPBible.org / Tyndale House; Open Scriptures; OpenBible.info |
| `rainbow/texts/*.js` | 30 English Bible translations (the KJV is in `data.js`), listed with their licences in the Guide and `texts/manifest.js` | **Each keeps its own licence:** public domain (most); CC BY 4.0 (Orthodox Jewish Bible, Text-Critical English NT); CC BY-SA 4.0 (Literal Standard Version, Free Bible Version, Translation for Translators, Unlocked Literal Bible, Wycliffe) | The copyright holders named in the Guide |
| everything else (`*.py`, `*.html`, docs) | Project code, page text, the guide, authorship summaries in `bibledb/book_origins.py` | MIT | — |

The page footers and the guide already carry the attributions below. If you publish these files elsewhere, keep them.

## 2. Data downloaded when you build the database

`python bibledb/download.py` fetches these into `bibledb/raw/` (ignored by git). Nothing here is committed.

| Source | Used for | Licence |
|---|---|---|
| [OpenBible.info cross-references](https://www.openbible.info/labs/cross-references/) (from the Treasury of Scripture Knowledge) | `cross_references`, the Rainbow | CC BY 4.0 |
| [STEPBible Data](https://github.com/STEPBible/STEPBible-Data), Tyndale House Cambridge: TAHOT, TAGNT, TBESH, TBESG | `original_words`, `lexicon_extended`, Echoes, interlinear | CC BY 4.0 |
| [Open Scriptures Strong's dictionaries](https://github.com/openscriptures/strongs) | `strongs` | Strong's text public domain; this JSON edition CC BY-SA |
| [eBible.org](https://ebible.org/): World English Bible, King James Version (with Strong's tags), Septuagint, translation catalogue; 10 more English translations listed in `bibledb/english_texts.py` | `verse_text`, `translation_words`, `speech_spans`, `ebible_catalog` | Public domain (catalogue: facts about translations); the extra translations are public domain, CC BY 4.0 or CC BY-SA 4.0 as listed |
| [Berean Standard Bible tables](https://bereanbible.com/) | `translation_words` (BSB) | Public domain (dedicated 2023) |
| [scrollmapper/bible_databases](https://github.com/scrollmapper/bible_databases) (from CrossWire SWORD modules) | 140 texts in `verse_text` | Repository MIT; **each text has its own licence** (below) |

### Licences of the 152 texts

Recorded per text in `translations.license` and summarised in `translations.license_class` (152 texts in all, including those added from eBible.org and STEPBible):

| Class | Count | May you share a database containing them? |
|---|---|---|
| Public domain | 111 | Yes |
| Attribution (CC BY) | 7 | Yes, with attribution |
| Share-alike (CC BY-SA) | 9 | Yes, under the same licence |
| Copyleft (GPL) | 3 | Yes, under the GPL |
| No derivatives (CC BY-ND) | 2 | Verbatim only; a combined database is a grey area |
| Non-commercial only (CC BY-NC-SA, BY-NC-ND, "free non-commercial distribution") | 19 | Only non-commercially, and not for sale |
| Copyrighted, free distribution | 1 | Only as the owner allows |
| Not stated | 3 | Unknown: don't redistribute |

## 3. What this means in practice

- **Using everything yourself, or in a classroom:** fine. Keep the attributions visible.
- **Sharing this repository:** fine. It contains only MIT code plus the two data files in section 1, which carry their attributions.
- **Sharing a built `bible.duckdb`:** build it with
  ```
  python bibledb/build.py --open-only
  ```
  That leaves out the non-commercial, no-derivatives, copyrighted and unlabelled texts, so the file contains only public-domain, attribution, share-alike and GPL material. Because it then includes CC BY-SA material (the Strong's dictionary and some texts), share it under **CC BY-SA 4.0** with the attributions listed here.
- **Commercial use** of a full build is not permitted for the non-commercial texts. Build with `--open-only` and check the remaining share-alike and GPL terms.

## 4. Required attribution text

Copy this wherever the data is shown or shared:

> Cross-references: OpenBible.info, CC BY 4.0, drawn from the Treasury of Scripture Knowledge.
> Hebrew, Aramaic and Greek word data and lexicons: STEPBible.org / Tyndale House Cambridge, CC BY 4.0.
> Strong's dictionaries: Open Scriptures, CC BY-SA.
> Bible texts: see each text's licence in the `translations` table; public-domain texts from eBible.org and CrossWire (via scrollmapper/bible_databases).

## 5. Other notes

- **Design credit.** The Reference Rainbow follows the design of *Bible Cross-References* (2008) by Chris Harrison and Christoph Römhild. This project is an independent remake from open data. It does not use their image or data and is not affiliated with them; their poster is © Chris Harrison.
- **Authorship and dating** (`bibledb/book_origins.py`) are summaries written for this project, with citations to the ancient and modern works they draw on. The cited works belong to their authors and publishers.
- **King James Version.** Public domain in most countries. In the United Kingdom the Crown holds perpetual rights through Letters Patent.
- **Fonts** load from Google Fonts under the SIL Open Font Licence. Without an internet connection the pages fall back to system fonts.
- **Detected words of God** are computed by this project and are a heuristic, not an editorial marking. Say so if you publish them.
