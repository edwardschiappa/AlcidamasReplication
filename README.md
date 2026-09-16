# Replication package
## *The Proem and Epilogue of Alcidamas' On the Sophists: A Case for Interpolation*

Edward Schiappa. Forthcoming in *Rhetorica: A Journal of the History of Rhetoric*.

This package contains everything needed to reproduce the quantitative results in the article: the Greek texts as analysed (thirteen texts, each divided into Proem / Main Body / Epilogue), the single Python script that computes every figure, the script's output, and a description of the counting rules, the sentence-segmentation rule, and the sliding-window robustness test. Running the script regenerates Tables 1–5 and the figures quoted in the text (the sliding-window z-scores and percentages, the *Odysseus* comparison, the composite-density values, and the outlier test in the note to the Table 3 discussion).

If you use this package, please cite the article and this archive (see `CITATION.cff`).

---

## 1. Contents

| Path | What it is |
|---|---|
| `particle_analysis.py` | The analysis program. Python 3 (3.8 or later), standard library only, no installation required. Runs in a few seconds. |
| `data/*.txt` | The thirteen texts, one UTF-8 plain-text file each, divided by marker lines `# SECTION: Proem`, `# SECTION: Main Body`, `# SECTION: Epilogue`. |
| `data/SOURCES.md` | Edition and source of each text, and the section boundaries used. |
| `output/*.csv` | Files written by the script (regenerated each run). |
| `expected_output/*.csv` | The same files as produced for the published article, for comparison. |
| `CITATION.cff` | Citation metadata. |
| `LICENSE` | MIT licence for the code; notes on the texts. |

## 2. Quick start

```
python3 particle_analysis.py
```

Run from the package directory. The script reads `data/` and writes `output/`. To verify that your run matches the published figures, compare `output/` with `expected_output/` (e.g. `diff -r output expected_output`); they should be identical.

`python3 particle_analysis.py DATA_DIR OUT_DIR` reads and writes elsewhere.

## 3. What each output file reproduces

| Output file | Article |
|---|---|
| `table1_sentences.csv` | Table 1 — sentence counts and mean sentence lengths, six control texts and *Soph.* |
| `table2_soph_particles.csv` | Table 2 — sixteen-particle panel for *Soph.* by section, with P+E:MB ratios |
| `table3_control_ratios.csv` | Table 3 — cross-section ratios (γάρ, μέν, δέ, καί) and composite density ratio, six controls and *Soph.* |
| `table4_sentences.csv` | Table 4 — sentence statistics, five supplementary comparanda and *Soph.* |
| `table5_ratios.csv` | Table 5 — cross-section ratios and per-section argumentative densities, five supplementary comparanda and *Soph.* |
| `sentences_all.csv` | Sentence statistics and section word counts for all thirteen texts (including "Alcidamas", *Odysseus*, discussed in the text but not tabled) |
| `particle_panels.csv` | Full sixteen-particle panel for every text (the per-text data behind Tables 2, 3 and 5, and the *Odysseus* figures) |
| `sliding_window.csv` | The robustness test: for every text, the number of frame-length windows, the frame's standardised distance (z) from the window distribution on γάρ, μέν, δέ, καί and density, and the share of windows at least as extreme as the frame on each feature, on all five jointly, and on the three main features (γάρ, καί, density) jointly. These are the figures in the section "Robustness: Local Variation and Supplementary Comparanda" and in the note listing z-scores for the six controls. |
| `outlier_test.csv` | The prediction-interval test reported in the note to the Table 3 discussion: Soph.'s composite-density ratio compared with the six control texts, and with all eleven comparison texts, treated as samples of single-author variation (see §5.6). |

Other figures quoted in the text and where to find them:

- Section word counts (e.g. *Soph.* P 101 / MB 1,979 / E 94; frame 195): `sentences_all.csv`.
- MB mean sentence length 44.0 and SD 31.4 for *Soph.*; SD 59.2 for the *Vect.* epilogue: the means are in `table1_sentences.csv`; the SDs are computed from the same segmentation and can be obtained by calling `sentences()` in the script on the relevant section.
- The MB §§3–4 counter-window (the first 195 words of the *Soph.* Main Body): its feature values are those of the first window in the sliding-window pass; `window_features()` in the script returns them.
- The γάρ rates for *C. soph.* by section (1.35 / 1.12 / 1.08) and the *Paneg.* epilogue (1.60 against 1.13): `particle_panels.csv`.

## 4. The texts

Thirteen texts: the six control texts (Isocrates, *Against the Sophists*, *Panegyricus*, *Helen*; Xenophon, *Poroi*, *Hipparchicus*, *Constitution of the Lacedaemonians*), the five supplementary comparanda (Gorgias, *Helen*; Hippocrates, *De arte* and *De flatibus*; Antisthenes, *Ajax* and *Odysseus*), and the two texts transmitted under Alcidamas' name (*On the Sophists*; the *Odysseus*). The edition followed for each, the source of the transcription, and the Proem / Main Body / Epilogue boundaries are listed in `data/SOURCES.md`. The data files carry the Greek text only: editorial page numbers, English headings, apparatus and footnote markers are removed; editorial punctuation is retained, because sentence segmentation depends on it (see §5.3). Three files (the two Hippocratic texts and the *Odysseus*) still carry the editions' section numbers (`1.`, `2)` …); the script ignores free-standing numerals, and a full stop belonging to a section number is not a sentence boundary.

## 5. Method

### 5.1 Tokenisation
All text is Unicode-normalised (NFC). Words are whitespace-separated tokens after stripping punctuation; elision apostrophes are kept as part of the token (the files use U+02BC, U+2019 or U+1FBD as the apostrophe; the script treats them alike). Editorial brackets are dropped and the bracketed words retained; runs of spaced lacuna dots (in Gorgias' *Helen*) are removed from the token stream; free-standing numerals are ignored. Word counts are token counts.

### 5.2 Particles
Sixteen particle types are counted (Table 2): γάρ, μέν, δέ, οὖν, καί, τε, ἀλλά, ἤ, ἔτι, τοίνυν, καίτοι, ὥστε, ἔπειτα, χωρίς, ἄρα, δή. Matching is case-insensitive and exact on an explicit list of accent variants, so that ἦ, ᾖ, ἡ and ἥ never count as ἤ, and ἤδη never counts as δή. Elided forms count under their full forms, including aspirated elisions (ὥστ᾽ and ὥσθ᾽ under ὥστε; τ᾽ and θ᾽ under τε; ἔτ᾽ and ἔθ᾽ under ἔτι); files that transmit elision without an apostrophe (Gorgias' *Helen*, Alcidamas' *Soph.*, both Antisthenes speeches and the *Odysseus*) have the bare tokens δ, ἀλλ, ὥστ, ὥσθ, τ counted likewise. ἄλλ᾽ (elided ἄλλα/ἄλλο, "other") is not ἀλλά and is not counted. Not counted under any type: crasis forms (κἀν, κἀκ …), γοῦν, οὐκοῦν/οὔκουν, interrogative ἆρα, μέντοι. No disambiguation of identically spelled non-particle uses is performed.

Rates are per 100 words of the section. The composite "argumentative density" sums γάρ, δέ, μέν, οὖν, τοίνυν, ἀλλά, ὥστε, ἔτι, δή. Cross-section ratios divide the frame rate (P+E combined) by the Main Body rate for γάρ, μέν, δέ and καί, and the Main Body density by the frame density for the composite measure. Ratios are computed from unrounded rates and rounded once, at output.

### 5.3 Sentence segmentation
One rule for every text: a sentence ends at a full stop of the modern edited text (an exclamation mark, which occurs twice in Gorgias' *Helen*, is likewise final). Neither the Greek question mark (;) nor the raised dot is a boundary; editorial paragraph breaks are not boundaries. Standard deviations of sentence length quoted in the article are sample standard deviations (n − 1). The rule affects only sentence counts and mean lengths, never word or particle counts. The one documented exception is a stray full stop at *De arte* 8 (πῦρ. ὄργανον), treated as non-final.

### 5.4 Text-critical adjustments
Applied programmatically, each as a named function in the script (`ADJUSTMENTS`): runs of spaced lacuna dots (in Gorgias' *Helen* and once in the *Odysseus* proem) are removed from the token stream without creating a sentence boundary; the corrupt 41-word stretch of *Helen* 12 (τίς οὖν αἰτία κωλύει … τὴν αὐτὴν ἔχει) is excluded from all counts; the divided Καί τοι of *De arte* 5 and 11 is read as καίτοι; the *De arte* 8 stop is treated as above.

### 5.5 Sliding-window test
For each text, every contiguous window of the Main Body whose length equals that text's own frame (P+E) in words is examined, advancing one word at a time (a body of W words yields W − frame + 1 windows; for *Soph.*, 1,785 windows of 195 words). For each window the rates of γάρ, μέν, δέ, καί and the composite density are computed. The frame's value on each feature is standardised against the window distribution: z = (frame − window mean) ÷ population standard deviation. The script also reports, per feature, the share of windows at least as extreme as the frame in the frame's own direction relative to the window mean, and the share of windows jointly at least as extreme on all five features and on the three main features (γάρ, καί, density). Overlapping windows are not independent samples; the procedure is an exhaustive search, not an inferential test, as the article states.

### 5.6 Outlier test on the composite-density ratio
The note to the Table 3 discussion asks whether Soph.'s composite-density ratio (MB ÷ P+E, the final column of Tables 3 and 5) could be a further draw from the single-author variation shown by the comparison texts. Each text's ratio is taken on the natural-log scale, so that ratios below and above 1.00 are weighted symmetrically. With n comparison values of mean m and sample standard deviation s (n − 1 denominator), Soph.'s value x is reported as (x − m) ÷ s standard deviations from the mean, and as a prediction-interval statistic t = (x − m) ÷ (s·√(1 + 1/n)) on n − 1 degrees of freedom, with the one-sided p-value P(T ≥ t). The test is run twice, against the six control texts of Table 3 (n = 6) and against all eleven comparison texts of Tables 3 and 5 (n = 11). The t-distribution tail is evaluated with the regularised incomplete beta function (standard library only); values agree with scipy.stats to the printed precision.

### 5.7 Rounding
All published figures are the script's values rounded once at output. Where a ratio is quoted in the text, it is the unrounded ratio (e.g. the *Soph.* density ratio 1.88 = 7.731/4.103, i.e. 153/1,979 ÷ 8/195, not the quotient of the displayed rates). Ranges in Tables 1 and 4 are computed from unrounded means.

## 6. Data provenance and licensing

Licensing: the code and documentation are released under the MIT licence (see `LICENSE`); the Greek text files in `data/` are released under the Creative Commons Attribution-ShareAlike 4.0 International licence (CC BY-SA 4.0; see `data/LICENSE`), as derivatives of Perseus Digital Library texts. The texts reproduce editions in the public domain as digitised by the Perseus Digital Library / Scaife Viewer, whose texts are distributed under a Creative Commons Attribution-ShareAlike licence; `data/SOURCES.md` gives the edition and source for each file. All thirteen texts were taken from the Perseus Digital Library (Tufts University), read through the Scaife Viewer; none derives from the Thesaurus Linguae Graecae. The TLG was used in the article only for lexical proximity searches, which are described in the article's notes and are reproducible by any TLG subscriber.

## 7. Acknowledgement of AI assistance

The analysis program in this package and the tabulation of its results were developed with the assistance of Claude, an AI model made by Anthropic, used as a programming and analysis assistant during 2026. The author defined the questions, the counting rules, the section boundaries and the text-critical decisions; supplied and checked the Greek texts; and verified every figure reported in the article against the script's output. Claude was also used in drafting this documentation. Responsibility for the analyses, and for their interpretation in the article, rests with the author.

## 8. Contact

Edward Schiappa — schiappa@mit.edu
