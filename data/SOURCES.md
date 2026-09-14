# Sources of the texts and section boundaries

Each file is UTF-8 plain text with three sections introduced by the marker lines `# SECTION: Proem`, `# SECTION: Main Body`, `# SECTION: Epilogue`. Section numbers below are those of the standard editions; the files themselves carry no section numbers. Word counts are the script's token counts.

| File | Text | Edition followed / source of transcription | Proem | Main Body | Epilogue | Words (P / MB / E) |
|---|---|---|---|---|---|---|
| `alcidamas_soph.txt` | Alcidamas, *On the Sophists* (*Soph.*) | F. Blass, *Antiphontis orationes et fragmenta, adiunctis Gorgiae, Antisthenis, Alcidamantis declamationibus* (Leipzig: Teubner, 1892), as transmitted in the Scaife/Perseus corpus | §§1–2 | §§3–33 | §§34–35 | 101 / 1,979 / 94 |
| `alcidamas_od.txt` | "Alcidamas", *Odysseus* | Blass 1892 | §§1–4 (to the statement of the charge, before the narrative begins at §5, Σχεδὸν μὲν γὰρ ἴστε) | §§5–28 | §29 (Ἀξιῶ δ᾽ ὑμᾶς … to the end) | 243 / 1,269 / 65 |
| `isocrates_csoph.txt` | Isocrates, *Against the Sophists* (*C. soph.*) | G. Norlin, *Isocrates*, vol. 2 (Loeb, 1929), via Scaife/Perseus | §1 | §§2–20 | §§21–22 | 74 / 1,157 / 93 |
| `isocrates_paneg.txt` | Isocrates, *Panegyricus* (*Paneg.*) | G. Norlin, *Isocrates*, vol. 1 (Loeb, 1928), via Scaife/Perseus | §§1–15 | §§16–180 | §§181–189 | 720 / 9,498 / 561 |
| `isocrates_helen.txt` | Isocrates, *Helen* | G. Norlin, *Isocrates*, vol. 2 (Loeb, 1929), via Scaife/Perseus | §§1–14 | §§15–66 | §§67–69 | 720 / 2,852 / 157 |
| `xenophon_vect.txt` | Xenophon, *Poroi* (*Vect.*) | E. C. Marchant, *Xenophontis opera omnia*, vol. 5 (OCT, 1920), via Scaife/Perseus | §1 | §§2–5 | §6 | 363 / 3,319 / 171 |
| `xenophon_eqmag.txt` | Xenophon, *Hipparchicus* (*Eq. mag.*) | Marchant, OCT vol. 5, via Scaife/Perseus | §1 | §§2–8 | §9 | 1,160 / 4,259 / 361 |
| `xenophon_lac.txt` | Xenophon, *Constitution of the Lacedaemonians* (*Lac.*) | Marchant, OCT vol. 5, via Scaife/Perseus | §1 | §§2–13 | §§14–15 | 397 / 4,083 / 445 |
| `gorgias_helen.txt` | Gorgias, *Helen* | F. Blass, *Antiphontis orationes et fragmenta, adiunctis Gorgiae, Antisthenis, Alcidamantis declamationibus* (Leipzig: Teubner, 1908), via Perseus/Scaife | §§1–5 | §§6–19 | §§20–21 | 315 / 911 / 61 |
| `hippocrates_dearte.txt` | Hippocrates, *De arte* | É. Littré, *Œuvres complètes d'Hippocrate*, vol. 6 (Paris: Baillière, 1849), via Perseus/Scaife | §1 to … μωμέεσθαι | §1 from Τοὺς μὲν οὖν … to §12 | §13 | 124 / 2,502 / 71 |
| `hippocrates_flat.txt` | Hippocrates, *De flatibus* (*Flat.*) | Littré, vol. 6 (1849), via Perseus/Scaife | §1 | §§2–14 | §15 | 300 / 2,458 / 82 |
| `antisthenes_ajax.txt` | Antisthenes, *Ajax* | F. Blass, *Antiphontis orationes et fragmenta, adiunctis Gorgiae, Antisthenis, Alcidamantis declamationibus* (Leipzig: Teubner, 1908), via Perseus/Scaife | §1 | §§2–6 | §§7–9 | 59 / 274 / 169 |
| `antisthenes_od.txt` | Antisthenes, *Odysseus* (*Od.*) | F. Blass, *Antiphontis orationes et fragmenta, adiunctis Gorgiae, Antisthenis, Alcidamantis declamationibus* (Leipzig: Teubner, 1908), via Perseus/Scaife | §1 | §§2–13 | §14 | 61 / 817 / 46 |

## Notes

- All texts were taken from the Perseus Digital Library (Tufts University) through the Scaife Viewer; the editions and dates above are those given in the Perseus catalogue records. Download dates: Alcidamas, *On the Sophists*, September 2025; the six Isocrates and Xenophon control texts, January 2026; the five supplementary comparanda and the *Odysseus*, August 2026. Perseus texts are corrected over time, so a later download may differ in small ways from the files here; sentence boundaries follow the editorial punctuation of the files as downloaded (see README §5.3).
- Two transcription duplications in the Perseus *Odysseus* text (34 words repeated in §2, 15 words in §12) were removed from the data file. Both repetitions are present in Perseus's own source XML (First1KGreek, tlg0610.tlg001) and neither is in Blass's 1892 edition (pp. 183, 186–187), where each passage appears once; footnote markers `[*]` and lacuna marks `⋯` left by the download were likewise removed; the section division is P §§1–4 / MB §§5–28 / E §29, as in the article.
- Text-critical adjustments applied by the script are listed in README §5.4 and declared in `ADJUSTMENTS` in `particle_analysis.py`.
- Licensing: editions of 1849–1929 are in the public domain; texts taken from Scaife/Perseus are redistributed under Perseus's Creative Commons Attribution-ShareAlike terms.
