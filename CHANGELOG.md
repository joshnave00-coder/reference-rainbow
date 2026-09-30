# Changelog

All notable changes to this project are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Reference Rainbow (`rainbow/index.html`, `rainbow/guide.html`)
- A second way to see the cross-references: **Layout → Wheel** (*Wheel within a Wheel*, after Ezekiel 1:16) bends the 1,189 chapters into a circle (Genesis at the top, clockwise to Revelation), with book names in a ring, chapter bars pointing outward and a colored band naming the sections of the Bible. Each reference is a curve across the middle. The picture morphs between the two layouts; hover, click, search, zoom, filters and colors all work in both. Every visit opens on the Rainbow; a link ending `?layout=wheel` opens the Wheel.
- The original view is now called **Rainbow** in the Layout control and stays the default.
- **Order → Chronological** (optional, never the default) lays out every verse in the order its events happened, in either layout: the Gospels' parallel accounts side by side, Chronicles beside Samuel and Kings, prophets beside their kings, letters where they fall in Acts. The picture rearranges itself in place. Built by the new `rainbow/build_chrono.py` from Theographic Bible Metadata (CC BY-SA 4.0) into `rainbow/chrono.js`.
- Hover a **book name** to light up every cross-reference touching that book, or on the Wheel a **section** of the outer band (Law, Gospels, Paul's Letters…) for the whole section; click either to zoom to it.
- The book names under the Rainbow are slanted and spread out so none overlap, each as close to its book as possible with a thin leader line when it had to move. All 66 fit on a typical laptop screen; on smaller screens the shortest books appear as you zoom in. A name is shortened only when the full name doesn't fit. The Wheel's book ring uses the same placement.
- The morphs between layouts and orders run on elapsed time, so they take the same time on a slow or busy computer.
- A **Zoom out** button appears over the picture whenever you are zoomed in, in either layout.
- Changing **Color** (Distance, Book, Years) or **Dating** now blends every arc smoothly into its new color instead of switching at once.
- Fixes found in review: the theme button no longer covers the end of the search box; on phones the Wheel and the Rainbow's bars sit above the search panel instead of behind it; zooming to a long book or a whole section on the Wheel now brings it to the middle; hovering the Wheel stays quick with every reference shown, and zoomed-in Wheels skip curves that are off screen; book names no longer disappear in chronological order on very wide screens; chapter numbers on the Verses axis appear at the same zoom as before.

### Echoes (`rainbow/echoes.html`)
- Switching between **Hebrew OT**, **Greek NT** and **Septuagint + NT** glides the chapter axis from one range to the other while the old arcs fade and the new ones rise from the baseline. The arcs also rise in when the page opens, and when a filter or search changes the list, only the phrases that come or go animate.

### Build (`rainbow/build_chrono.py`)
- Downloads go to a temporary file first, so an interrupted download is never mistaken for a complete one, and the verse order is checked reference by reference against `data.js` rather than by count alone.

## [0.2.0] - 2026-09-19

### Scriptorium (`bibledb/`)
- The "Choose translations" picker in Read now groups texts as English first, original-language texts (Hebrew, Aramaic and Greek) second, then every other translation and ancient version below, instead of a single alphabetical-by-category order.

### Scriptorium and Reference Rainbow (`bibledb/web/index.html`, `rainbow/*.html`)
- Replaced the Light/Dark/System control on every screen (Scriptorium, Reference Rainbow, Echoes, Read and Guide) with a single one-click switch pinned to the top right. It cycles Light → Dark → System, remembers your choice the same way as before, and steps out of the way while a side drawer or panel is open.

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

[Unreleased]: https://github.com/joshnave00-coder/reference-rainbow/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/joshnave00-coder/reference-rainbow/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/joshnave00-coder/reference-rainbow/releases/tag/v0.1.0
