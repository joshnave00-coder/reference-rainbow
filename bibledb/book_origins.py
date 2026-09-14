"""Authorship, date and place of writing for the 66 books, with competing views and sources.

Conventions
-----------
* Years are integers; negative = BC/BCE, positive = AD/CE (no year zero is modelled).
* view:
    consensus    - traditional and critical scholarship broadly agree
    traditional  - ancient Jewish/Christian attribution, maintained by many conservative scholars
    critical     - the prevailing position in critical (historical-critical) scholarship
    alternative  - a significant minority or competing proposal
* consensus (per book):
    broad    - little dispute on author, date or place
    divided  - traditional and critical scholarship differ, each fairly settled
    open     - no agreement even within critical scholarship
* Ancient sources are cited with passage locators. Modern reference works are cited at the level
  of the work (see their chapter on the book in question). These are summaries compiled for this
  database - check the cited works before relying on them in published writing.
"""

SOURCES = {
    # ---- ancient
    "bt-bb": dict(kind="ancient", author="Babylonian Talmud", title="Bava Batra 14b–15a (baraita naming the writers of the biblical books)", date="compiled c. AD 500", url="https://www.sefaria.org/Bava_Batra.14b"),
    "bt-meg": dict(kind="ancient", author="Babylonian Talmud", title="Megillah 15a", date="compiled c. AD 500", url="https://www.sefaria.org/Megillah.15a"),
    "bt-sanh": dict(kind="ancient", author="Babylonian Talmud", title="Sanhedrin 39b", date="compiled c. AD 500", url="https://www.sefaria.org/Sanhedrin.39b"),
    "josephus-apion": dict(kind="ancient", author="Josephus", title="Against Apion", date="c. AD 95", url=None),
    "josephus-ant": dict(kind="ancient", author="Josephus", title="Jewish Antiquities", date="c. AD 93–94", url=None),
    "irenaeus": dict(kind="ancient", author="Irenaeus of Lyon", title="Against Heresies", date="c. AD 180", url=None),
    "eusebius-he": dict(kind="ancient", author="Eusebius of Caesarea", title="Ecclesiastical History (preserving Papias, Clement of Alexandria, Origen and Dionysius of Alexandria)", date="c. AD 313–325", url=None),
    "muratorian": dict(kind="ancient", author="Anonymous", title="The Muratorian Fragment (Latin list of New Testament books)", date="late 2nd or 4th c. AD (debated)", url=None),
    "antimarcionite": dict(kind="ancient", author="Anonymous", title="Anti-Marcionite Prologue to Luke", date="2nd–4th c. AD (debated)", url=None),
    "tertullian": dict(kind="ancient", author="Tertullian", title="On Modesty (De Pudicitia)", date="c. AD 210s", url=None),
    "jerome-dan": dict(kind="ancient", author="Jerome", title="Commentary on Daniel, prologue (reporting the arguments of Porphyry)", date="AD 407", url=None),
    # ---- modern
    "dewette": dict(kind="modern", author="W. M. L. de Wette", title="Dissertatio critico-exegetica (Jena)", date="1805", url=None),
    "wellhausen": dict(kind="modern", author="Julius Wellhausen", title="Prolegomena to the History of Israel", date="1878/1883 (English 1885)", url=None),
    "duhm": dict(kind="modern", author="Bernhard Duhm", title="Das Buch Jesaia (Göttingen)", date="1892", url=None),
    "noth": dict(kind="modern", author="Martin Noth", title="Überlieferungsgeschichtliche Studien (English: The Deuteronomistic History, 1981)", date="1943", url=None),
    "cross": dict(kind="modern", author="Frank Moore Cross", title="Canaanite Myth and Hebrew Epic (Harvard University Press)", date="1973", url=None),
    "japhet": dict(kind="modern", author="Sara Japhet", title="“The Supposed Common Authorship of Chronicles and Ezra–Nehemiah Investigated Anew,” Vetus Testamentum 18: 330–371", date="1968", url=None),
    "milgrom": dict(kind="modern", author="Jacob Milgrom", title="Leviticus 1–16 (Anchor Bible 3; Doubleday)", date="1991", url=None),
    "collins-hb": dict(kind="modern", author="John J. Collins", title="Introduction to the Hebrew Bible (Fortress Press, 3rd ed.)", date="2018", url=None),
    "collins-dan": dict(kind="modern", author="John J. Collins", title="Daniel (Hermeneia; Fortress Press)", date="1993", url=None),
    "schmid": dict(kind="modern", author="Konrad Schmid", title="The Old Testament: A Literary History (Fortress Press)", date="2012", url=None),
    "finkelstein": dict(kind="modern", author="Israel Finkelstein & Neil Asher Silberman", title="The Bible Unearthed (Free Press)", date="2001", url=None),
    "longman-dillard": dict(kind="modern", author="Tremper Longman III & Raymond B. Dillard", title="An Introduction to the Old Testament (Zondervan, 2nd ed.)", date="2006", url=None),
    "harrison-ot": dict(kind="modern", author="R. K. Harrison", title="Introduction to the Old Testament (Eerdmans)", date="1969", url=None),
    "kitchen": dict(kind="modern", author="K. A. Kitchen", title="On the Reliability of the Old Testament (Eerdmans)", date="2003", url=None),
    "abd": dict(kind="modern", author="David Noel Freedman (ed.)", title="The Anchor Bible Dictionary, 6 vols. (Doubleday), articles on individual books", date="1992", url=None),
    "brown-nt": dict(kind="modern", author="Raymond E. Brown", title="An Introduction to the New Testament (Anchor Bible Reference Library; Doubleday)", date="1997", url=None),
    "carson-moo": dict(kind="modern", author="D. A. Carson & Douglas J. Moo", title="An Introduction to the New Testament (Zondervan, 2nd ed.)", date="2005", url=None),
    "ehrman-nt": dict(kind="modern", author="Bart D. Ehrman", title="The New Testament: A Historical Introduction to the Early Christian Writings (Oxford University Press; several editions)", date="1997–", url=None),
    "robinson": dict(kind="modern", author="John A. T. Robinson", title="Redating the New Testament (SCM Press)", date="1976", url=None),
    "pervo": dict(kind="modern", author="Richard I. Pervo", title="Dating Acts: Between the Evangelists and the Apologists (Polebridge Press)", date="2006", url=None),
}

# place_id: (name, latitude, longitude, precision)  precision: site | region
PLACES = {
    "sinai": ("Mount Sinai (traditional site, Jebel Musa)", 28.539, 33.975, "site"),
    "moab": ("Plains of Moab, east of the Jordan", 31.83, 35.62, "region"),
    "canaan": ("Canaan", 31.9, 35.2, "region"),
    "israel": ("Northern kingdom of Israel", 32.3, 35.25, "region"),
    "judah": ("Judah / Yehud", 31.6, 35.1, "region"),
    "jerusalem": ("Jerusalem", 31.778, 35.235, "site"),
    "samaria": ("Samaria", 32.280, 35.197, "site"),
    "bethel": ("Bethel", 31.930, 35.222, "site"),
    "moresheth": ("Moresheth-gath", 31.606, 34.897, "site"),
    "babylon": ("Babylon", 32.536, 44.421, "site"),
    "telabib": ("Tel-abib by the Chebar canal, near Nippur (Babylonia)", 32.127, 45.233, "region"),
    "susa": ("Susa (Shushan), Persia", 32.189, 48.258, "site"),
    "persia": ("Eastern Jewish diaspora (Persian Empire)", 32.5, 48.0, "region"),
    "egypt": ("Egypt (Tahpanhes)", 30.867, 32.10, "site"),
    "judea": ("Judea", 31.7, 35.2, "region"),
    "galilee": ("Galilee", 32.8, 35.5, "region"),
    "syria": ("Roman Syria", 34.5, 36.5, "region"),
    "antioch": ("Antioch on the Orontes (Syria)", 36.202, 36.160, "site"),
    "rome": ("Rome", 41.893, 12.483, "site"),
    "corinth": ("Corinth", 37.906, 22.879, "site"),
    "ephesus": ("Ephesus", 37.941, 27.342, "site"),
    "macedonia": ("Macedonia (e.g., Philippi)", 41.013, 24.284, "region"),
    "caesarea": ("Caesarea Maritima", 32.500, 34.892, "site"),
    "achaia": ("Achaia (Greece)", 37.9, 22.5, "region"),
    "asiaminor": ("Roman province of Asia (western Asia Minor)", 38.5, 28.0, "region"),
    "patmos": ("Patmos", 37.321, 26.546, "site"),
}


def v(view, author, frm, to, date_display, place=None, place_display=None, held_by=None, sources=(), section=None, note=None):
    return dict(view=view, author=author, date_from=frm, date_to=to, date_display=date_display, place_id=place,
                place_display=place_display or (PLACES[place][0] if place else "Not known"), held_by=held_by,
                sources=list(sources), section=section, note=note)


TRAD = "Ancient Jewish and Christian tradition; many conservative scholars"
CRIT = "Most critical scholars"

_moses = dict(author="Moses (the Talmud credits Joshua with the final verses on Moses' death, Deut 34:5–12)",
              frm=-1446, to=-1406,
              date="c. 1446–1406 BC on the early-Exodus chronology (1 Kgs 6:1); c. 1260–1220 BC on the late-Exodus chronology")
_moses_src = [("bt-bb", "14b–15a"), ("josephus-apion", "1.37–40"), ("longman-dillard", None), ("harrison-ot", None), ("kitchen", "on the date of the Exodus")]
_pent_crit = "Anonymous scribes and editors; analysed as J, E and P sources (Documentary Hypothesis) or as Priestly and non-Priestly layers (supplementary models)"
_dtr = "Deuteronomistic historians"
_dtr_date = "First edition under Josiah (late 7th c. BC), revised during the exile (6th c. BC)"
_dtr_src = [("noth", None), ("cross", None), ("collins-hb", None)]
_twelve = ("bt-bb", "15a (the Men of the Great Assembly committed the Twelve to writing)")
_pastoral_crit = v("critical", "A later follower of Paul writing in his name (the Pastoral Epistles)", 90, 130, "c. AD 90–130", None, "Not known", CRIT, [("brown-nt", None), ("ehrman-nt", None)])

ORIGINS = {
    "Gen": dict(consensus="divided", views=[
        v("traditional", _moses["author"], _moses["frm"], _moses["to"], _moses["date"], "sinai", "Wilderness of Sinai", TRAD, _moses_src),
        v("critical", _pent_crit, -950, -400, "Sources from c. 10th–6th c. BC; final form c. 5th c. BC", "judah", "Judah (Jerusalem), partly in the Babylonian exile", CRIT + " (models differ)", [("wellhausen", None), ("collins-hb", None), ("schmid", None)]),
    ]),
    "Exod": dict(consensus="divided", views=[
        v("traditional", _moses["author"], _moses["frm"], _moses["to"], _moses["date"], "sinai", "Wilderness of Sinai", TRAD, _moses_src),
        v("critical", _pent_crit, -950, -400, "Sources from c. 10th–6th c. BC; final form c. 5th c. BC", "judah", "Judah (Jerusalem), partly in the Babylonian exile", CRIT + " (models differ)", [("wellhausen", None), ("collins-hb", None), ("schmid", None)]),
    ]),
    "Lev": dict(consensus="divided", views=[
        v("traditional", _moses["author"], _moses["frm"], _moses["to"], _moses["date"], "sinai", "Wilderness of Sinai", TRAD, _moses_src),
        v("critical", "Priestly writers (P), with the Holiness Code (H, chs 17–26)", -600, -400, "c. 6th–5th c. BC (exilic and Persian periods)", "judah", "Judah (Jerusalem) and the Babylonian exile", CRIT, [("wellhausen", None), ("collins-hb", None)]),
        v("alternative", "Priestly writers, largely before the exile", -850, -600, "Mostly pre-exilic (before 586 BC)", "jerusalem", None, "Yehezkel Kaufmann, Jacob Milgrom and others", [("milgrom", None)]),
    ]),
    "Num": dict(consensus="divided", views=[
        v("traditional", _moses["author"], _moses["frm"], _moses["to"], _moses["date"], "moab", "Wilderness of Sinai and the plains of Moab", TRAD, _moses_src),
        v("critical", _pent_crit, -700, -400, "Mostly Priestly and late non-Priestly material, c. 7th–5th c. BC", "judah", "Judah (Jerusalem), partly in the Babylonian exile", CRIT, [("wellhausen", None), ("collins-hb", None)]),
    ]),
    "Deut": dict(consensus="divided", views=[
        v("traditional", _moses["author"], _moses["frm"], _moses["to"], _moses["date"], "moab", "Plains of Moab (Deut 1:1–5)", TRAD, _moses_src),
        v("critical", "Scribes linked to King Josiah's reform (core: chs 12–26), expanded during the exile", -650, -540, "Core c. 7th c. BC (cf. 2 Kgs 22–23, 622 BC); framing chapters 6th c. BC", "jerusalem", None, CRIT, [("dewette", None), ("collins-hb", None), ("noth", None)]),
    ]),
    "Josh": dict(consensus="divided", views=[
        v("traditional", "Joshua (the Talmud credits Eleazar and Phinehas with the account of his death)", -1400, -1370, "c. 1400–1370 BC (early chronology)", "canaan", None, TRAD, [("bt-bb", "15a"), ("harrison-ot", None)]),
        v("critical", _dtr, -640, -550, _dtr_date, "judah", "Judah and the Babylonian exile", CRIT, _dtr_src + [("finkelstein", None)]),
    ]),
    "Judg": dict(consensus="divided", views=[
        v("traditional", "Samuel", -1050, -1000, "c. 1050–1000 BC", None, "Not stated in the tradition", TRAD, [("bt-bb", "14b–15a")]),
        v("critical", _dtr + ", reworking older hero stories", -640, -550, _dtr_date, "judah", "Judah and the Babylonian exile", CRIT, _dtr_src),
    ]),
    "Ruth": dict(consensus="open", views=[
        v("traditional", "Samuel", -1050, -1000, "c. 1050–1000 BC", None, "Not stated in the tradition", TRAD, [("bt-bb", "14b–15a")]),
        v("critical", "Anonymous", -500, -350, "Post-exilic, c. 5th–4th c. BC", "judah", None, "Many critical scholars", [("collins-hb", None)]),
        v("alternative", "Anonymous", -950, -700, "Monarchic period, c. 10th–8th c. BC", "judah", None, "Some critical and many conservative scholars", [("longman-dillard", None), ("abd", None)]),
    ]),
    "1Sam": dict(consensus="divided", views=[
        v("traditional", "Samuel, completed by the prophets Gad and Nathan (cf. 1 Chr 29:29)", -1010, -930, "c. 1010–930 BC", None, "Not stated in the tradition", TRAD, [("bt-bb", "14b–15a")]),
        v("critical", _dtr + " using older sources (the Ark Narrative, the History of David's Rise)", -640, -550, _dtr_date, "judah", "Judah and the Babylonian exile", CRIT, _dtr_src),
    ]),
    "2Sam": dict(consensus="divided", views=[
        v("traditional", "The prophets Gad and Nathan, completing Samuel's work (cf. 1 Chr 29:29)", -1000, -930, "c. 1000–930 BC", None, "Not stated in the tradition", TRAD, [("bt-bb", "15a")]),
        v("critical", _dtr + " using older sources (the Succession Narrative, 2 Sam 9–20)", -640, -550, _dtr_date, "judah", "Judah and the Babylonian exile", CRIT, _dtr_src),
    ]),
    "1Kgs": dict(consensus="divided", views=[
        v("traditional", "Jeremiah", -586, -560, "c. 586–560 BC", None, "Not stated (Jeremiah was last in Egypt, Jer 43–44)", TRAD, [("bt-bb", "15a")]),
        v("critical", _dtr + ": a Josianic edition revised after Jehoiachin's release in 561 BC", -620, -540, "c. 620 BC, revised c. 560–540 BC", "judah", "Judah and the Babylonian exile", CRIT, _dtr_src),
    ]),
    "2Kgs": dict(consensus="divided", views=[
        v("traditional", "Jeremiah", -586, -560, "c. 586–560 BC (the last event is 561 BC, 2 Kgs 25:27)", None, "Not stated (Jeremiah was last in Egypt, Jer 43–44)", TRAD, [("bt-bb", "15a")]),
        v("critical", _dtr + ": a Josianic edition revised after Jehoiachin's release in 561 BC", -620, -540, "c. 620 BC, revised c. 560–540 BC", "judah", "Judah and the Babylonian exile", CRIT, _dtr_src),
    ]),
    "1Chr": dict(consensus="divided", views=[
        v("traditional", "Ezra (the Talmud: Ezra wrote the genealogies of Chronicles; Nehemiah completed them)", -450, -400, "c. 450–400 BC", "jerusalem", None, TRAD, [("bt-bb", "15a")]),
        v("critical", "An anonymous Levitical writer (the Chronicler), probably not the author of Ezra–Nehemiah", -400, -300, "c. 4th c. BC (proposals range c. 520–200 BC)", "jerusalem", None, CRIT, [("japhet", None), ("collins-hb", None)]),
    ]),
    "2Chr": dict(consensus="divided", views=[
        v("traditional", "Ezra, completed by Nehemiah", -450, -400, "c. 450–400 BC", "jerusalem", None, TRAD, [("bt-bb", "15a")]),
        v("critical", "An anonymous Levitical writer (the Chronicler), probably not the author of Ezra–Nehemiah", -400, -300, "c. 4th c. BC (proposals range c. 520–200 BC)", "jerusalem", None, CRIT, [("japhet", None), ("collins-hb", None)]),
    ]),
    "Ezra": dict(consensus="divided", views=[
        v("traditional", "Ezra", -458, -440, "c. 458–440 BC", "jerusalem", None, TRAD, [("bt-bb", "15a")]),
        v("critical", "An anonymous compiler using an Ezra memoir, Persian-era documents and lists", -400, -300, "c. 4th c. BC (Ezra's mission itself is dated 458 or 398 BC)", "jerusalem", None, CRIT, [("collins-hb", None), ("abd", None)]),
    ]),
    "Neh": dict(consensus="divided", views=[
        v("traditional", "Nehemiah (first-person memoir); the Talmud credits him with completing Ezra's work", -432, -420, "c. 432–420 BC", "jerusalem", None, TRAD, [("bt-bb", "15a")]),
        v("critical", "Nehemiah's own memoir (c. 430 BC) incorporated by a later compiler", -430, -300, "Memoir c. 430 BC; compiled c. 400–300 BC", "jerusalem", None, CRIT, [("collins-hb", None)]),
    ]),
    "Esth": dict(consensus="divided", views=[
        v("traditional", "The Men of the Great Assembly (Talmud); Mordecai has also been proposed, from Esth 9:20", -470, -400, "c. 470–400 BC, after the reign of Xerxes I", "susa", None, TRAD, [("bt-bb", "15a"), ("harrison-ot", None)]),
        v("critical", "An anonymous writer of the eastern Jewish diaspora", -400, -200, "Late Persian or early Hellenistic period, c. 4th–3rd c. BC", "persia", None, CRIT, [("collins-hb", None)]),
    ]),
    "Job": dict(consensus="divided", views=[
        v("traditional", "Moses (one opinion in the Talmud, which records others)", -1440, -1400, "c. 1440–1400 BC", None, "Not stated in the tradition", TRAD, [("bt-bb", "14b–15b")]),
        v("critical", "An anonymous Judahite poet; the Elihu speeches (chs 32–37) are often thought to be a later addition", -600, -400, "c. 6th–4th c. BC", "judah", None, CRIT, [("collins-hb", None), ("abd", None)]),
    ]),
    "Ps": dict(consensus="divided", views=[
        v("traditional", "David, with Asaph, the sons of Korah, Solomon, Moses (Ps 90), Heman, Ethan and others named in the superscriptions (the Talmud: David with ten elders)", -1440, -500, "Mostly c. 1000–950 BC (David), from c. 1400 BC (Ps 90) to the exile (Ps 137)", "jerusalem", None, TRAD, [("bt-bb", "14b–15a"), ("longman-dillard", None)]),
        v("critical", "Many anonymous poets and temple singers over several centuries, collected into five books", -950, -200, "Individual psalms c. 10th–4th c. BC; collection completed c. 4th–2nd c. BC", "jerusalem", None, CRIT, [("collins-hb", None), ("schmid", None)]),
    ]),
    "Prov": dict(consensus="divided", views=[
        v("traditional", "Solomon (1:1; 10:1; 25:1), with the sayings of the wise (22:17), Agur (ch. 30) and King Lemuel (ch. 31); partly compiled by Hezekiah's men (25:1)", -970, -700, "c. 970–930 BC (Solomon); c. 715–686 BC (Hezekiah's collection)", "jerusalem", None, TRAD, [("bt-bb", "15a"), ("longman-dillard", None)]),
        v("critical", "Several collections of different ages (22:17–24:22 parallels the Egyptian Instruction of Amenemope); chs 1–9 and final editing after the exile", -900, -350, "Collections from the monarchy (10th–7th c. BC); final form c. 5th–4th c. BC", "jerusalem", None, CRIT, [("collins-hb", None), ("abd", None)]),
    ]),
    "Eccl": dict(consensus="divided", views=[
        v("traditional", "Solomon (“son of David, king in Jerusalem”, 1:1); written down by Hezekiah's circle (Talmud)", -970, -930, "c. 970–930 BC", "jerusalem", None, TRAD, [("bt-bb", "15a")]),
        v("critical", "An anonymous sage, “Qohelet”, with an editor's epilogue (12:9–14)", -300, -200, "c. 3rd c. BC (late Hebrew with Persian loanwords)", "jerusalem", None, CRIT + "; many conservative scholars also accept a post-Solomonic date", [("collins-hb", None), ("longman-dillard", None)]),
    ]),
    "Song": dict(consensus="open", views=[
        v("traditional", "Solomon (1:1)", -970, -930, "c. 970–930 BC", "jerusalem", None, TRAD, [("bt-bb", "15a")]),
        v("critical", "Anonymous poet(s): a collection of love poems", -500, -250, "Proposals range from the 10th to the 3rd c. BC; many favour the Persian or Hellenistic period", "judah", None, "Many critical scholars", [("collins-hb", None), ("abd", None)]),
    ]),
    "Isa": dict(consensus="divided", views=[
        v("traditional", "Isaiah son of Amoz (the whole book)", -740, -681, "c. 740–681 BC", "jerusalem", None, TRAD, [("bt-bb", "15a"), ("longman-dillard", None), ("harrison-ot", None)]),
        v("critical", "Isaiah of Jerusalem, with later additions (e.g., chs 24–27, 34–35)", -740, -700, "Core c. 740–700 BC", "jerusalem", None, CRIT, [("duhm", None), ("collins-hb", None)], section="chs 1–39"),
        v("critical", "An anonymous prophet of the exile (“Second Isaiah”)", -550, -539, "c. 550–539 BC", "babylon", "Babylonia", CRIT, [("duhm", None), ("collins-hb", None)], section="chs 40–55"),
        v("critical", "Disciples in Jerusalem after the return (“Third Isaiah”)", -520, -450, "c. 520–450 BC", "jerusalem", None, CRIT, [("duhm", None), ("collins-hb", None)], section="chs 56–66"),
    ]),
    "Jer": dict(consensus="divided", views=[
        v("traditional", "Jeremiah, dictating to his scribe Baruch (Jer 36)", -627, -580, "c. 627–580 BC", "jerusalem", "Jerusalem, and later Egypt (Jer 43–44)", TRAD, [("bt-bb", "15a")]),
        v("critical", "Jeremiah's oracles and a Baruch narrative, expanded by Deuteronomistic editors; a shorter (Septuagint) and longer (Masoretic) edition survive", -627, -450, "Oracles c. 627–586 BC; editing through the 6th–5th c. BC", "judah", "Judah, Egypt and Babylonia", CRIT, [("collins-hb", None), ("abd", None)]),
    ]),
    "Lam": dict(consensus="divided", views=[
        v("traditional", "Jeremiah (Septuagint preface; Talmud; cf. 2 Chr 35:25)", -586, -580, "c. 586–580 BC", "jerusalem", None, TRAD, [("bt-bb", "15a")]),
        v("critical", "One or more anonymous poets in Judah after the fall of Jerusalem", -586, -520, "c. 586–520 BC", "judah", None, CRIT, [("collins-hb", None)]),
    ]),
    "Ezek": dict(consensus="broad", views=[
        v("traditional", "Ezekiel son of Buzi, a priest among the exiles (the Talmud says the Men of the Great Assembly committed it to writing)", -593, -571, "593–571 BC (dated oracles, 1:2; 29:17)", "telabib", None, TRAD, [("bt-bb", "15a")]),
        v("critical", "Ezekiel, with additions by a circle of disciples (e.g., parts of chs 40–48)", -593, -500, "Core 593–571 BC; editing into the late 6th c. BC", "telabib", None, CRIT, [("collins-hb", None)]),
    ]),
    "Dan": dict(consensus="divided", views=[
        v("traditional", "Daniel (the Talmud says the Men of the Great Assembly committed it to writing)", -605, -530, "c. 605–530 BC", "babylon", None, TRAD, [("bt-bb", "15a"), ("harrison-ot", None), ("longman-dillard", None)]),
        v("critical", "Anonymous Judean authors: court tales (chs 1–6) from the Persian–early Hellenistic era; visions (chs 7–12) written during Antiochus IV's persecution", -167, -164, "Final form c. 167–164 BC; tales earlier (4th–3rd c. BC)", "judea", None, CRIT + " (already argued by Porphyry, 3rd c. AD)", [("jerome-dan", "prologue"), ("collins-dan", None), ("collins-hb", None)]),
    ]),
    "Hos": dict(consensus="broad", views=[
        v("traditional", "Hosea son of Beeri", -750, -722, "c. 750–722 BC", "israel", None, TRAD, [_twelve]),
        v("critical", "Hosea's oracles, collected and edited in Judah after 722 BC", -750, -550, "Core c. 750–725 BC; editing 7th–6th c. BC", "israel", "Northern Israel; edited in Judah", CRIT, [("collins-hb", None)]),
    ]),
    "Joel": dict(consensus="open", views=[
        v("traditional", "Joel son of Pethuel", -835, -796, "Often placed in the 9th c. BC (reign of Joash) from its position among early prophets; some conservative scholars prefer c. 600 BC or later", "jerusalem", None, "Some conservative scholars", [("harrison-ot", None), ("longman-dillard", None)]),
        v("critical", "Joel son of Pethuel (otherwise unknown)", -450, -350, "Post-exilic, c. 5th–4th c. BC", "jerusalem", None, CRIT, [("collins-hb", None)]),
    ]),
    "Amos": dict(consensus="broad", views=[
        v("traditional", "Amos, a herdsman from Tekoa in Judah (1:1)", -760, -750, "c. 760–750 BC", "bethel", "Bethel, northern Israel (7:10–13)", TRAD, [_twelve, ("longman-dillard", None)]),
        v("critical", "Amos's oracles with later additions (e.g., 9:11–15 from the exile)", -760, -500, "Core c. 760–750 BC; additions 7th–5th c. BC", "bethel", "Bethel; edited in Judah", CRIT, [("collins-hb", None)]),
    ]),
    "Obad": dict(consensus="divided", views=[
        v("traditional", "Obadiah (the Talmud identifies him with Ahab's steward of 1 Kgs 18)", -848, -841, "c. 848–841 BC (Edom's revolt under Jehoram); many conservative scholars instead date it after 586 BC", None, "Not stated", TRAD, [("bt-sanh", "39b"), ("harrison-ot", None)]),
        v("critical", "Obadiah (otherwise unknown)", -586, -550, "Shortly after the fall of Jerusalem in 586 BC", "judah", None, CRIT, [("collins-hb", None)]),
    ]),
    "Jonah": dict(consensus="divided", views=[
        v("traditional", "Jonah son of Amittai (2 Kgs 14:25)", -785, -750, "c. 785–750 BC", "israel", None, TRAD, [_twelve, ("harrison-ot", None)]),
        v("critical", "An anonymous post-exilic author writing about the 8th-c. prophet", -500, -300, "c. 5th–4th c. BC", "judah", None, CRIT, [("collins-hb", None)]),
    ]),
    "Mic": dict(consensus="divided", views=[
        v("traditional", "Micah of Moresheth", -735, -700, "c. 735–700 BC", "moresheth", "Moresheth-gath and Jerusalem, Judah", TRAD, [_twelve, ("longman-dillard", None)]),
        v("critical", "Micah's oracles (chiefly chs 1–3) with exilic and post-exilic additions (chs 4–7)", -735, -450, "Core c. 735–700 BC; additions 6th–5th c. BC", "judah", None, CRIT, [("collins-hb", None)]),
    ]),
    "Nah": dict(consensus="broad", views=[
        v("traditional", "Nahum the Elkoshite (Elkosh is unidentified)", -663, -612, "Between the fall of Thebes (663 BC, 3:8) and the fall of Nineveh (612 BC)", "judah", None, TRAD, [_twelve, ("longman-dillard", None)]),
        v("critical", "Nahum, with an editorial acrostic hymn (1:2–8)", -663, -612, "Between 663 and 612 BC", "judah", None, CRIT, [("collins-hb", None)]),
    ]),
    "Hab": dict(consensus="broad", views=[
        v("traditional", "Habakkuk", -609, -598, "c. 609–598 BC, as Babylon rose", "judah", None, TRAD, [_twelve, ("longman-dillard", None)]),
        v("critical", "Habakkuk; the psalm of ch. 3 may have circulated separately", -609, -550, "Core c. 609–598 BC", "judah", None, CRIT, [("collins-hb", None)]),
    ]),
    "Zeph": dict(consensus="broad", views=[
        v("traditional", "Zephaniah son of Cushi, in the reign of Josiah (1:1)", -640, -609, "c. 640–609 BC", "jerusalem", None, TRAD, [_twelve]),
        v("critical", "Zephaniah's oracles with exilic additions", -630, -500, "Core c. 630–620 BC; additions 6th c. BC", "jerusalem", None, CRIT, [("collins-hb", None)]),
    ]),
    "Hag": dict(consensus="broad", views=[
        v("consensus", "Haggai (oracles set in an editorial framework)", -520, -520, "520 BC (oracles dated to Darius I's second year)", "jerusalem", None, "Traditional and critical scholarship", [_twelve, ("collins-hb", None)]),
    ]),
    "Zech": dict(consensus="divided", views=[
        v("traditional", "Zechariah son of Berechiah (the whole book)", -520, -480, "Chs 1–8 dated 520–518 BC; chs 9–14 later in his ministry", "jerusalem", None, TRAD, [_twelve, ("longman-dillard", None)]),
        v("critical", "Zechariah son of Berechiah", -520, -518, "520–518 BC", "jerusalem", None, CRIT, [("collins-hb", None)], section="chs 1–8"),
        v("critical", "Anonymous (“Second Zechariah”)", -450, -300, "c. 5th–4th c. BC (a minority date parts before the exile)", "judah", None, CRIT, [("collins-hb", None)], section="chs 9–14"),
    ]),
    "Mal": dict(consensus="divided", views=[
        v("traditional", "Malachi (the Talmud and the Targum also identify him with Ezra)", -460, -430, "c. 460–430 BC", "jerusalem", None, TRAD, [("bt-meg", "15a"), _twelve]),
        v("critical", "Anonymous (“Malachi” means “my messenger”, 3:1)", -500, -450, "c. 500–450 BC", "jerusalem", None, CRIT, [("collins-hb", None)]),
    ]),
    # ------------------------------------------------------------------ New Testament
    "Matt": dict(consensus="divided", views=[
        v("traditional", "Matthew (Levi), apostle and former tax collector", 50, 65, "c. AD 50–65 (Irenaeus: while Peter and Paul preached in Rome)", "judea", "Judea, “among the Hebrews” (Irenaeus)", TRAD, [("irenaeus", "3.1.1"), ("eusebius-he", "3.39.16 (Papias)"), ("carson-moo", None)]),
        v("critical", "An anonymous Jewish-Christian author using Mark and a sayings source (Q)", 80, 90, "c. AD 80–90", "antioch", None, CRIT, [("brown-nt", None), ("ehrman-nt", None)]),
        v("alternative", "An anonymous Jewish-Christian author", 80, 90, "c. AD 80–90", "galilee", "Galilee or elsewhere in Syria-Palestine", "Some critical scholars", [("brown-nt", None)]),
    ]),
    "Mark": dict(consensus="divided", views=[
        v("traditional", "John Mark, recording Peter's preaching (Papias)", 55, 68, "c. AD 55–68, around the time of Peter's death", "rome", None, TRAD, [("eusebius-he", "3.39.15 (Papias); 6.14.6–7 (Clement of Alexandria)"), ("irenaeus", "3.1.1")]),
        v("critical", "Anonymous (traditionally Mark), writing around the Jewish War", 66, 74, "c. AD 66–74", "rome", None, "Many critical scholars", [("brown-nt", None), ("ehrman-nt", None)]),
        v("alternative", "Anonymous", 66, 74, "c. AD 66–74", "syria", "Syria or Galilee", "Other critical scholars", [("brown-nt", None)]),
    ]),
    "Luke": dict(consensus="divided", views=[
        v("traditional", "Luke the physician, Paul's companion (Col 4:14)", 59, 63, "c. AD 59–63, before Acts", "achaia", "Achaia (Anti-Marcionite Prologue)", TRAD, [("irenaeus", "3.1.1"), ("muratorian", None), ("antimarcionite", None), ("carson-moo", None)]),
        v("critical", "The anonymous author of Luke–Acts (possibly Luke)", 80, 90, "c. AD 80–90", None, "Not known (Antioch, Achaia, Ephesus and Rome are proposed)", CRIT, [("brown-nt", None), ("ehrman-nt", None)]),
    ]),
    "John": dict(consensus="divided", views=[
        v("traditional", "John the apostle, son of Zebedee, “the disciple whom Jesus loved”", 85, 95, "c. AD 85–95", "ephesus", None, TRAD, [("irenaeus", "3.1.1"), ("eusebius-he", "3.24")]),
        v("critical", "Anonymous author(s) of the Johannine community, perhaps drawing on the Beloved Disciple's witness; composed in stages", 90, 110, "Final form c. AD 90–110", "ephesus", "Ephesus (Syria and Palestine are also proposed)", CRIT, [("brown-nt", None), ("ehrman-nt", None)]),
        v("alternative", "John the apostle", 60, 70, "Before AD 70", None, "Not known", "J. A. T. Robinson and some others", [("robinson", None)]),
    ]),
    "Acts": dict(consensus="open", views=[
        v("traditional", "Luke, Paul's companion (the “we” passages)", 62, 63, "c. AD 62, when the narrative ends", "rome", None, TRAD, [("irenaeus", "3.14.1"), ("muratorian", None), ("carson-moo", None)]),
        v("critical", "The anonymous author of Luke (possibly Luke)", 80, 90, "c. AD 80–90", None, "Not known (Rome, Ephesus and Antioch are proposed)", CRIT, [("brown-nt", None)]),
        v("alternative", "Anonymous", 110, 120, "c. AD 110–120", None, "Not known (Ephesus is proposed)", "Richard Pervo and others", [("pervo", None)]),
    ]),
    "Rom": dict(consensus="broad", views=[
        v("consensus", "Paul (written down by Tertius, 16:22)", 56, 57, "c. AD 56–57", "corinth", "Corinth (16:1, 23)", "Traditional and critical scholarship", [("brown-nt", None), ("carson-moo", None)]),
    ]),
    "1Cor": dict(consensus="broad", views=[
        v("consensus", "Paul, with Sosthenes (1:1)", 53, 55, "c. AD 53–55", "ephesus", "Ephesus (16:8)", "Traditional and critical scholarship", [("brown-nt", None), ("carson-moo", None)]),
    ]),
    "2Cor": dict(consensus="broad", views=[
        v("consensus", "Paul, with Timothy (1:1); many critical scholars see several letters combined (e.g., chs 10–13)", 55, 56, "c. AD 55–56", "macedonia", "Macedonia (2:13; 7:5)", "Traditional and critical scholarship", [("brown-nt", None), ("carson-moo", None)]),
    ]),
    "Gal": dict(consensus="divided", views=[
        v("consensus", "Paul", 48, 57, "c. AD 48–57 (exact date disputed)", None, "Disputed", "Traditional and critical scholarship", [("brown-nt", None), ("carson-moo", None)]),
        v("alternative", "Paul, before the Jerusalem Council (“South Galatian” view)", 48, 49, "c. AD 48–49", "antioch", None, "Many conservative and some critical scholars", [("carson-moo", None)]),
        v("alternative", "Paul, on his third journey (“North Galatian” view)", 53, 57, "c. AD 53–57", "ephesus", "Ephesus or Macedonia", "Many critical scholars", [("brown-nt", None)]),
    ]),
    "Eph": dict(consensus="divided", views=[
        v("traditional", "Paul, while imprisoned (3:1; 4:1; 6:20)", 60, 62, "c. AD 60–62", "rome", None, TRAD, [("carson-moo", None)]),
        v("critical", "A follower of Paul writing in his name", 80, 100, "c. AD 80–100", "asiaminor", None, "Most critical scholars", [("brown-nt", None), ("ehrman-nt", None)]),
    ]),
    "Phil": dict(consensus="divided", views=[
        v("consensus", "Paul, with Timothy (1:1)", 54, 62, "c. AD 54–62, depending on where Paul was imprisoned", None, "Disputed (see alternatives)", "Traditional and critical scholarship", [("brown-nt", None), ("carson-moo", None)]),
        v("traditional", "Paul, imprisoned in Rome", 60, 62, "c. AD 60–62", "rome", None, "Tradition; many scholars", [("carson-moo", None)]),
        v("alternative", "Paul, imprisoned in Ephesus", 54, 55, "c. AD 54–55", "ephesus", None, "A number of critical scholars", [("brown-nt", None)]),
        v("alternative", "Paul, imprisoned in Caesarea", 57, 59, "c. AD 57–59", "caesarea", None, "A minority of scholars", [("brown-nt", None)]),
    ]),
    "Col": dict(consensus="divided", views=[
        v("traditional", "Paul, with Timothy, while imprisoned", 60, 62, "c. AD 60–62", "rome", "Rome (Ephesus is also proposed)", TRAD, [("carson-moo", None)]),
        v("critical", "A disciple of Paul writing in his name", 70, 90, "c. AD 70–90", "asiaminor", None, "Many (not all) critical scholars", [("brown-nt", None), ("ehrman-nt", None)]),
    ]),
    "1Thess": dict(consensus="broad", views=[
        v("consensus", "Paul, with Silvanus and Timothy (1:1)", 50, 51, "c. AD 50–51; often considered the earliest New Testament writing", "corinth", "Corinth (cf. Acts 18)", "Traditional and critical scholarship", [("brown-nt", None), ("carson-moo", None)]),
    ]),
    "2Thess": dict(consensus="divided", views=[
        v("traditional", "Paul, with Silvanus and Timothy", 51, 52, "c. AD 51–52", "corinth", None, TRAD, [("carson-moo", None)]),
        v("critical", "A later follower of Paul writing in his name", 80, 100, "c. AD 80–100", None, "Not known", "Critical scholars are divided; many hold this view", [("brown-nt", None), ("ehrman-nt", None)]),
    ]),
    "1Tim": dict(consensus="divided", views=[
        v("traditional", "Paul, after release from a first Roman imprisonment", 62, 64, "c. AD 62–64", "macedonia", "Macedonia (1:3)", TRAD, [("carson-moo", None)]),
        _pastoral_crit,
    ]),
    "2Tim": dict(consensus="divided", views=[
        v("traditional", "Paul, during a final Roman imprisonment", 64, 67, "c. AD 64–67", "rome", "Rome (1:17)", TRAD, [("eusebius-he", "2.22"), ("carson-moo", None)]),
        _pastoral_crit,
    ]),
    "Titus": dict(consensus="divided", views=[
        v("traditional", "Paul, after release from a first Roman imprisonment", 62, 64, "c. AD 62–64", None, "Not stated (Paul plans to winter at Nicopolis, 3:12)", TRAD, [("carson-moo", None)]),
        _pastoral_crit,
    ]),
    "Phlm": dict(consensus="divided", views=[
        v("consensus", "Paul, with Timothy (1:1)", 54, 62, "c. AD 54–62, depending on where Paul was imprisoned", None, "Disputed (see alternatives)", "Traditional and critical scholarship", [("brown-nt", None), ("carson-moo", None)]),
        v("traditional", "Paul, imprisoned in Rome", 60, 62, "c. AD 60–62", "rome", None, "Tradition; many scholars", [("carson-moo", None)]),
        v("alternative", "Paul, imprisoned in Ephesus", 54, 55, "c. AD 54–55", "ephesus", None, "A number of critical scholars", [("brown-nt", None)]),
    ]),
    "Heb": dict(consensus="open", views=[
        v("traditional", "Paul (Clement of Alexandria: written in Hebrew and translated by Luke)", 64, 68, "Before AD 70", None, "Not stated", "Eastern church tradition; later the Western church", [("eusebius-he", "6.14.2–4")]),
        v("alternative", "Barnabas", 64, 68, "Before AD 70", None, "Not stated", "Tertullian", [("tertullian", "20")]),
        v("alternative", "Apollos", 60, 69, "Before AD 70", None, "Not stated", "Proposed by Martin Luther; favoured by some modern scholars", [("carson-moo", None), ("brown-nt", None)]),
        v("critical", "Unknown (Origen: “who wrote the epistle, God knows”)", 60, 95, "c. AD 60–95", None, "Not known; connected with Italy (13:24)", "Most modern scholars", [("eusebius-he", "6.25.11–14 (Origen)"), ("brown-nt", None), ("ehrman-nt", None)]),
    ]),
    "Jas": dict(consensus="divided", views=[
        v("traditional", "James, brother of Jesus and leader of the Jerusalem church", 45, 62, "Before his death in AD 62 (Josephus)", "jerusalem", None, TRAD, [("josephus-ant", "20.200"), ("carson-moo", None)]),
        v("critical", "An unknown author writing in James's name", 80, 100, "c. AD 80–100", None, "Not known", "Many critical scholars", [("brown-nt", None), ("ehrman-nt", None)]),
    ]),
    "1Pet": dict(consensus="divided", views=[
        v("traditional", "Peter, with Silvanus (5:12)", 62, 64, "c. AD 62–64", "rome", "Rome, called “Babylon” (5:13)", TRAD, [("eusebius-he", "2.15.2 (Papias)"), ("carson-moo", None)]),
        v("critical", "A Petrine circle in Rome writing in Peter's name", 70, 95, "c. AD 70–95", "rome", None, "Many critical scholars", [("brown-nt", None), ("ehrman-nt", None)]),
    ]),
    "2Pet": dict(consensus="divided", views=[
        v("traditional", "Peter, shortly before his death (1:14)", 64, 68, "c. AD 64–68", "rome", "Traditionally Rome (not stated in the letter)", TRAD, [("carson-moo", None)]),
        v("critical", "An unknown author writing in Peter's name; often considered the latest New Testament writing", 100, 130, "c. AD 100–130", None, "Not known", CRIT + " (its authorship was already disputed in Eusebius's day)", [("eusebius-he", "3.25.3"), ("brown-nt", None), ("ehrman-nt", None)]),
    ]),
    "1John": dict(consensus="divided", views=[
        v("traditional", "John the apostle", 85, 95, "c. AD 85–95", "ephesus", None, TRAD, [("irenaeus", "3.16.5")]),
        v("critical", "An author from the Johannine community", 100, 110, "c. AD 100–110", "ephesus", None, CRIT, [("brown-nt", None)]),
    ]),
    "2John": dict(consensus="divided", views=[
        v("traditional", "John the apostle, writing as “the elder”", 85, 95, "c. AD 85–95", "ephesus", None, TRAD, [("irenaeus", "3.16.8")]),
        v("critical", "“The elder”, possibly the John the Elder whom Papias distinguishes from the apostle", 100, 110, "c. AD 100–110", "ephesus", None, CRIT, [("eusebius-he", "3.39.4–6 (Papias)"), ("brown-nt", None)]),
    ]),
    "3John": dict(consensus="divided", views=[
        v("traditional", "John the apostle, writing as “the elder”", 85, 95, "c. AD 85–95", "ephesus", None, TRAD, [("eusebius-he", "3.25.3 (listed among disputed books)")]),
        v("critical", "“The elder”, possibly the John the Elder whom Papias distinguishes from the apostle", 100, 110, "c. AD 100–110", "ephesus", None, CRIT, [("eusebius-he", "3.39.4–6 (Papias)"), ("brown-nt", None)]),
    ]),
    "Jude": dict(consensus="divided", views=[
        v("traditional", "Jude, brother of James and of Jesus (1:1)", 60, 80, "c. AD 60–80", None, "Not known", TRAD, [("carson-moo", None)]),
        v("critical", "An unknown author writing in Jude's name", 80, 120, "c. AD 80–120", None, "Not known", "Many critical scholars", [("brown-nt", None), ("ehrman-nt", None)]),
    ]),
    "Rev": dict(consensus="divided", views=[
        v("traditional", "John the apostle, exiled on Patmos (1:9)", 95, 96, "c. AD 95, late in Domitian's reign (Irenaeus)", "patmos", None, TRAD, [("irenaeus", "5.30.3"), ("eusebius-he", "3.18")]),
        v("critical", "John of Patmos, a Christian prophet probably distinct from the apostle (as Dionysius of Alexandria argued from its style)", 90, 96, "c. AD 90–96", "patmos", None, CRIT, [("eusebius-he", "7.25 (Dionysius of Alexandria)"), ("brown-nt", None), ("ehrman-nt", None)]),
        v("alternative", "John, writing under Nero or Galba", 68, 70, "c. AD 68–70", "patmos", None, "J. A. T. Robinson and some others", [("robinson", None)]),
    ]),
}

CONSENSUS_NOTE = {
    "broad": "Traditional and critical scholarship largely agree.",
    "divided": "Traditional and critical scholarship differ; see each view and its sources.",
    "open": "No settled answer even within critical scholarship; several proposals are listed.",
}


def representative_year(book, view):
    """Midpoint year for a book under 'traditional' or 'critical' dating (used by the rainbow's time colouring)."""
    rows = ORIGINS[book]["views"]
    pick = [r for r in rows if r["view"] == view and r["section"] is None] or [r for r in rows if r["view"] == view]
    if not pick:
        pick = [r for r in rows if r["view"] == "consensus"]
    lo = min(r["date_from"] for r in pick)
    hi = max(r["date_to"] for r in pick)
    return (lo + hi) / 2
