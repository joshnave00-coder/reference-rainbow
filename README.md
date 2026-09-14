# Reference Rainbow

**A free tool for exploring how the Bible connects to itself.** It runs on your own computer, with no account, no sign-up and no internet connection needed.

![version](https://img.shields.io/badge/version-0.1.0-8C6A1C)

## What you can do with it

- **See every cross-reference in the Bible at once.** 344,756 links between verses are drawn as colored arcs, after Chris Harrison and Christoph Römhild's well-known 2008 poster. Click any chapter to read the verses it connects to.
- **Read in your preferred translation.** 29 English Bibles, including the King James Version, World English Bible, Berean Standard Bible, American Standard Version, Young's Literal and Geneva Bible.
- **Focus on part of the Bible.** Show only the Old or New Testament, categories such as the Gospels, Paul's Letters or the Minor Prophets, or single books.
- **Find repeated phrases in the original languages.** *Echoes* lists every run of 7 or more words that appears more than once in the Hebrew, Aramaic or Greek, such as quotations, refrains and events told twice. Hover any Hebrew or Greek word to see its Strong's number and meaning.
- **See who wrote each book, when and where.** Each book shows the traditional view and the view of modern scholarship side by side, with their sources.
- **See who is speaking.** The words of Jesus are shown in red, and words spoken by God in dark red.
- **Just read, then dig deeper.** A clean Bible reader: click any verse to see its Hebrew or Greek words, what each word means, how translators have rendered it elsewhere, every other verse that uses it, and the verse's cross-references.

---

## How to open it (about 2 minutes)

1. **Download.** Click [this download link](https://github.com/joshnave00-coder/reference-rainbow/archive/refs/heads/main.zip). (Or, on the [project page](https://github.com/joshnave00-coder/reference-rainbow), click the green **Code** button, then **Download ZIP**.)
2. **Unzip.** Find the file in your *Downloads* folder.
   - **Windows:** right-click it and choose **Extract All…**, then **Extract**.
   - **Mac:** double-click it.
3. **Open.** In the new folder, double-click:
   - **Read the Bible.html** to read and study, or
   - **Open Reference Rainbow.html** for the cross-reference picture.

   Either opens in your web browser, and each page links to the others.

**Tip:** once it's open, bookmark the page (Ctrl+D on Windows, ⌘+D on Mac) so you can come back to it easily.

It works best on a computer (not a phone) in a recent version of **Chrome, Edge, Firefox or Safari**.

---

## Finding your way around

| To… | Do this |
|---|---|
| **Just read the Bible** | Open **Read the Bible.html** (or click **Read the Bible** on the Rainbow). Choose the book and chapter at the top. |
| **Study a verse** | In the reader, click the verse. Click a Hebrew or Greek word in the panel to see its meaning and every place it's used. |
| **Read a chapter's connections** | On the Rainbow, click one of the grey bars along the bottom of the picture. A panel opens on the right. |
| **Go to a passage** | Type it in the search box at the top right, e.g. *John 3:16*, *Psalm 23* or *Isaiah*, and press Enter. |
| **Change the translation** | Use **Translation** in the controls at the bottom, or **Reading in** at the top of any chapter panel. |
| **Show only some books** | Click **Books** at the bottom and tick what you want: whole testaments, categories or single books. **Select all** and **Deselect all** are at the top of the list. |
| **Show more or fewer arcs** | Move the **Relevance** slider. It starts at about the same number of arcs as the original poster; slide it all the way left to see every cross-reference. |
| **Zoom in** | Scroll with your mouse wheel over the picture, and drag to move sideways. **Fit** zooms back out. |
| **Find repeated phrases** | Click **Echoes: repeated phrases** under the search box. |
| **Understand a button** | Rest your mouse on it for a moment. A short explanation appears, often with a **Learn more** link. |
| **Get help** | Press the **?** key, or click **? Help**. The **Guide** explains everything in detail. |
| **Switch to a dark screen** | **Theme** at the bottom: Light, Dark, or System (follows your computer). |

---

## Which translations are included?

29 English translations that anyone is allowed to share:

- **Modern:** Berean Standard Bible, World English Bible (and its Updated edition), Majority Standard Bible, New Heart English Bible, Literal Standard Version, Free Bible Version, Translation for Translators, Unlocked Literal Bible, Bible in Basic English, Open English Bible (partial), Text-Critical English New Testament.
- **King James family:** King James Version, KJV Pure Cambridge Edition, Updated King James Version, Webster Bible, Restored Name KJV, A Conservative Version.
- **Classic:** American Standard Version, Revised Version, Young's Literal Translation, Darby, Rotherham.
- **Historic:** Geneva Bible (1599), Tyndale (partial), Wycliffe (c. 1395).
- **Jewish and Messianic:** JPS Tanakh (1917), Orthodox Jewish Bible, World Messianic Bible.

**Why isn't the NIV, NKJV or ESV here?** Those translations (along with the NASB, NLT, CSB and others) are owned by publishers who don't allow their full text to be copied into other programs. The closest options included here:
- Berean Standard Bible or World English Bible, for readable modern English;
- Literal Standard Version, for word-for-word modern English;
- Updated King James Version, for King James wording in modern English.

---

## If something doesn't work

- **The picture is blank or grey.** The Rainbow needs a graphics feature called *WebGL 2*. Update your browser, or try Chrome or Edge. If it's still blank, open your browser's settings, search for **graphics acceleration** (or **hardware acceleration**), and make sure it's turned on.
- **"The data files did not load" or "texts folder" messages.** Make sure you unzipped the download (opening the files from inside the ZIP won't work), and keep all the folders together as they came.
- **A verse says "Not in this translation".** Some translations number a few chapters differently, and some cover only part of the Bible. Choose another translation for that passage.
- **Something else.** See *Questions and corrections* below.

---

## Is it accurate?

- **Cross-references, Bible texts and the Hebrew and Greek word data** come straight from respected published sources, listed below.
- **The Relevance slider** uses votes from readers of OpenBible.info. A high score means readers found a link helpful; it is not a scholarly rating.
- **Words of God (dark red)** are found automatically by a computer, so some will be missed or slightly off. The words of Jesus (red) follow the standard red-letter editions.
- **Who wrote each book and when** are summaries written for this project, showing both traditional and modern scholarly views with their sources. Check the sources before quoting them in published work.

---

## For advanced users: the full Bible database

The download also includes **Scriptorium**, a larger research database and reading room:
- 152 texts in 57 languages;
- word-by-word Hebrew and Greek with Strong's numbers;
- a Strong's concordance;
- a timeline of who wrote each book;
- a place to run your own database searches.

To start it:

1. Install **Python** (free) from [python.org](https://www.python.org/downloads/). On Windows, tick **Add python.exe to PATH** on the first screen.
2. In the project folder, double-click **Start Scriptorium (Windows).bat** or **Start Scriptorium (Mac).command**. The first time, it downloads about 350 MB and builds the database, which takes a few minutes.
3. Scriptorium opens in your browser at http://127.0.0.1:8770. Keep the black window open while you use it; close it to stop.

On a Mac, if the file won't open, right-click it and choose **Open**. On Windows, if you see "Windows protected your PC", click **More info**, then **Run anyway**.

You don't need to remember these steps: the **Scriptorium** link on every page checks whether it's running and shows them again if it isn't. Inside Scriptorium, **Data & setup** explains how to stop and restart it, and has buttons to get the latest data, rebuild, or make a copy you can share. More detail is in **[docs/TECHNICAL.md](docs/TECHNICAL.md)**.

---

## Credits and permissions

- **Cross-references:** [OpenBible.info](https://www.openbible.info/labs/cross-references/), from the *Treasury of Scripture Knowledge*.
- **Hebrew, Aramaic and Greek word data:** [STEPBible.org](https://www.stepbible.org/) / Tyndale House, Cambridge.
- **Strong's dictionaries:** [Open Scriptures](https://github.com/openscriptures/strongs).
- **Bible texts:** [eBible.org](https://ebible.org/), CrossWire, and the publishers named in the Guide.
- **Design:** after *Bible Cross-References* (2008) by Chris Harrison and Christoph Römhild. This is an independent project, not affiliated with them.

The program itself is free to use and share under the [MIT licence](LICENSE). The Bible texts and data keep their own permissions; [DATA_LICENSES.md](DATA_LICENSES.md) explains them in plain terms. To cite this project, use [CITATION.cff](CITATION.cff) (on GitHub, click **Cite this repository**).

## Questions and corrections

Found a mistake, such as a wrong date, a missed red letter or a verse in the wrong place? On GitHub, open the **Issues** tab and click **New issue**. The *Data correction* form asks for what you found and, for questions of authorship or dating, a source.
