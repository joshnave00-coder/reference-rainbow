# Changelog

All notable changes to this project are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-09-13

First public release.

### Reference Rainbow (`rainbow/index.html`)
- All 344,756 OpenBible.info cross-references drawn as arcs over the 1,189 chapters, rendered with WebGL 2.
- Color by chapter distance, by book, or by years apart (traditional or critical dating).
- Relevance slider using OpenBible.info vote scores. It starts at the setting matching Harrison & Römhild's 63,779 arcs (8+ votes, 60,635 references); slide to All for every reference.
- Chapter and verse panels with linked passages, King James Version text, red letters (words of Jesus) and dark red (words of God, detected), and authorship, dating and place of writing with sources.
- Light, dark and system themes; help panel; hover explanations with "Learn more" links into the guide.

### Echoes (`rainbow/echoes.html`)
- Phrases of 7 or more words repeated in the Hebrew & Aramaic Old Testament, the Greek New Testament, or the Septuagint with the New Testament.
- Exact or same-root-word matching; a "Repeats by length" chart with click and drag selection.
- Filters for length, places, books and cross-referencing; sorting.
- Original script or transliteration; hover any word for its Strong's number, click it for the definition.

### Read (`rainbow/read.html`)
- A simple Bible reader: book and chapter pickers, 29 translations, side-by-side comparison, paragraph or verse layout, text size, and search by passage or words.
- Click any verse to study it:
  - the Hebrew, Aramaic or Greek words with transliteration, gloss and grammar in plain English;
  - Strong's definitions and STEPBible senses;
  - how the KJV and BSB render each word across the Bible, with checkboxes to compare renderings in context;
  - every other verse that uses the word, with a Books filter;
  - cross-references, and who wrote the book.
- "Read the Bible.html" launcher, and double-click "Start Scriptorium" files for Windows and Mac.

### Translations and filters
- 29 freely licensed English translations in the Rainbow and Echoes, loaded on demand, chosen from the controls or any chapter panel and remembered between visits. Includes 10 added from eBible.org: WEB Updated, Majority Standard Bible, Revised Version, World Messianic Bible, Literal Standard Version, Free Bible Version, Translation for Translators, Unlocked Literal Bible, Text-Critical English NT and Orthodox Jewish Bible.
- Books filter with checkboxes for testaments, ten categories (Law, History, Wisdom / Poetry, Major Prophets, Minor Prophets, Gospels, Early Church History, Paul's Letters, General Letters, Prophecy) and single books, with Select all / Deselect all.
- Every filter allows several choices: Echoes' spread and cross-reference filters and Scriptorium's book, category, language and licence filters are checkbox lists.
- "Open Reference Rainbow.html" launcher and a plain-language README; technical instructions moved to docs/TECHNICAL.md.

### Guide (`rainbow/guide.html`)
- Explains relevance votes (source, distribution, caveats), colors, dating, red letters and Echoes.

### Scriptorium and `bible.duckdb` (`bibledb/`)
- Download and build scripts for a documented DuckDB database:
  - 152 texts in 57 languages, plus eBible.org's catalogue of 1,550 translations (Catholic Bibles are left out);
  - every Hebrew, Aramaic and Greek word with Strong's numbers and morphology;
  - Strong's and STEPBible lexicons, cross-references, red-letter spans and repeated phrases;
  - 143 authorship views for the 66 books, with 259 citations.
- Licence classification for every text, and `build.py --open-only` for a database that is safe to share.
- A local, read-only browser: parallel and interlinear reading, Strong's lookup, a books and dating timeline, the translation catalogue, a table browser and a SQL console.
- A **Data & setup** view: how to start, stop and restart Scriptorium, the database's status and licence mix, and buttons to refresh the pages' data, rebuild, get the latest data, or make a shareable copy, with a live log.
- The **Scriptorium** link on the Rainbow, Echoes, Read and Guide pages checks whether it is running, and if not shows step-by-step instructions to start it, with the project folder's location.

[Unreleased]: https://github.com/joshnave00-coder/reference-rainbow/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/joshnave00-coder/reference-rainbow/releases/tag/v0.1.0
