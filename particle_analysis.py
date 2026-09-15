#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
particle_analysis.py

Replication code for the particle-distribution and sentence-construction
analyses in the article on the frame (proem + epilogue) of Alcidamas'
On the Sophists (Soph.).

The script reads section-divided Greek texts from data/ and writes CSV
files to output/ reproducing the article's quantitative tables:

  table1_sentences.csv      sentence stats, six controls + Soph. (Table 1)
  table2_soph_particles.csv sixteen-particle panel for Soph. (Table 2)
  table3_control_ratios.csv cross-section ratios, six controls + Soph. (Table 3)
  table4_sentences.csv      sentence stats, five supplementary comparanda (Table 4)
  table5_ratios.csv         ratios + per-section argumentative densities,
                            five supplementary comparanda + Soph. (Table 5, revised)
  particle_panels.csv       full sixteen-particle panel for every text
                            (Tables 2 and 5a-5e, extended to all texts)
  sliding_window.csv        frame-length sliding-window test for every text
                            (robustness section)
  outlier_test.csv          Soph.'s composite-density ratio tested against the
                            comparison texts as a sample of single-author
                            variation (note to the Table 3 discussion)

DATA FORMAT
  Each file in data/ is UTF-8 plain text with three sections introduced by
  marker lines "# SECTION: Proem", "# SECTION: Main Body", "# SECTION: Epilogue".
  The texts were taken from the Perseus Digital Library (Scaife Viewer);
  the edition Perseus reproduces for each text is listed in data/SOURCES.md
  (Blass 1892/1908 for Alcidamas, Gorgias and Antisthenes; Littre 1849 for
  the Hippocratic texts; Norlin and Marchant for the controls).  Editorial
  page/section numbers and English headers are not part of the data files.

COUNTING RULES (as documented in the article and its analysis notes)
  * Sixteen particle types (Table 2): γάρ, μέν, δέ, οὖν, καί, τε, ἀλλά, ἤ,
    ἔτι, τοίνυν, καίτοι, ὥστε, ἔπειτα, χωρίς, ἄρα, δή.
  * Composite argumentative density: γάρ, δέ, μέν, οὖν, τοίνυν, ἀλλά, ὥστε,
    ἔτι, δή, per 100 words.
  * Elided forms (δ᾽, ἀλλ᾽, ὥστ᾽, τ᾽, ἔτ᾽) count under their full forms;
    files that transmit elisions without an apostrophe (Gorgias' Helen,
    Alcidamas' Soph.) have the bare tokens δ, ἀλλ, ὥστ, τ, ἔτ counted
    likewise.  Elisions of non-particle words (δι᾽, ἐπ᾽, οὐδ᾽ ...) never
    count.
  * Not counted under any type: crasis forms (κἀν, κἀκ ...); γοῦν and
    οὔκουν (not under οὖν); interrogative ἆρα/ἆρ᾽ (not under inferential
    ἄρα); μέντοι, ἤδη, καίπερ, and all other distinct words.
  * Matching is exact on the accent variants listed in VARIANTS (so ἦ, ᾖ,
    ἡ, ἥ never count as ἤ), case-insensitive.
  * Editorial brackets are dropped, the bracketed words retained; runs of
    spaced lacuna dots are removed from the token stream; free-standing
    numerals are ignored.
  * Text-critical adjustments per text are declared in ADJUSTMENTS below.

SENTENCE SEGMENTATION
  One uniform rule for every text: sentences end at the full stops of the
  modern edited text (question marks and exclamation points, where a
  transcription carries them as "?" or "!", are likewise final; the Greek
  question mark ";" and the middle stop are not boundaries).  Sentence
  counts are punctuation-dependent, as the article concedes; the counts
  reflect the punctuation of the transmitted files, with the one documented
  exception listed in ADJUSTMENTS (the stray stop at De arte 8).

SLIDING-WINDOW TEST
  For each text, every contiguous window of the Main Body with length equal
  to the text's frame (P+E) in words is examined (step = 1 word; the number
  of windows is MB_words - frame_words + 1).  For each window the rates per
  100 words of γάρ, μέν, δέ, καί and the composite argumentative density
  are computed.  The frame's value on each feature is standardised against
  the window distribution (z = (frame - mean) / population SD).  The script
  also reports, per feature, the share of windows at least as extreme as
  the frame in the frame's own direction relative to the window mean, and
  the share of windows matching the frame jointly on all five features and
  on the three main features (γάρ, καί, density).

USAGE
  python3 particle_analysis.py            # reads ./data, writes ./output
  python3 particle_analysis.py DATA OUT   # explicit directories

No dependencies beyond the Python 3 standard library.
"""

import csv
import math
import os
import re
import sys
import unicodedata

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

def N(s):
    """NFC-normalise a string (the files mix precomposed and combining marks)."""
    return unicodedata.normalize('NFC', s)

# Apostrophe characters found in the transmitted files (RIGHT SINGLE
# QUOTATION MARK, GREEK KORONIS, MODIFIER LETTER APOSTROPHE, ASCII).
APOSTROPHES = "’᾽ʼ'"

# The sixteen particle types, with their exact accepted accent variants.
VARIANTS = {
    'γάρ':    ['γάρ', 'γὰρ'],
    'μέν':    ['μέν', 'μὲν'],
    'δέ':     ['δέ', 'δὲ'],
    'οὖν':    ['οὖν'],
    'καί':    ['καί', 'καὶ'],
    'τε':     ['τε', 'τέ', 'τὲ'],
    'ἀλλά':   ['ἀλλά', 'ἀλλὰ'],
    'ἤ':      ['ἤ', 'ἢ'],
    'ἔτι':    ['ἔτι'],
    'τοίνυν': ['τοίνυν'],
    'καίτοι': ['καίτοι'],
    'ὥστε':   ['ὥστε'],
    'ἔπειτα': ['ἔπειτα'],
    'χωρίς':  ['χωρίς', 'χωρὶς'],
    'ἄρα':    ['ἄρα'],
    'δή':     ['δή', 'δὴ'],
}
SIXTEEN = list(VARIANTS)

# Elided stems -> particle type (with or without a trailing apostrophe).
# NB ἄλλ᾽ (elided ἄλλα/ἄλλο, "other") is not a particle and is not listed.
# ὥσθ, θ, ἔθ are the aspirated elisions (before rough breathing) of ὥστε,
# τε, ἔτι, transmitted as ὥσθ᾽, θ᾽, ἔθ᾽ or (in the apostrophe-less files)
# bare.
ELIDED = {'δ': 'δέ', 'ἀλλ': 'ἀλλά', 'ὥστ': 'ὥστε',
          'ὥσθ': 'ὥστε', 'τ': 'τε', 'θ': 'τε', 'ἔτ': 'ἔτι', 'ἔθ': 'ἔτι'}

# Composite argumentative-density set (see article, Argument 2).
ARGUMENTATIVE = {'γάρ', 'δέ', 'μέν', 'οὖν', 'τοίνυν', 'ἀλλά', 'ὥστε',
                 'ἔτι', 'δή'}

LOOKUP = {}
for particle, forms in VARIANTS.items():
    for form in forms:
        LOOKUP[N(form)] = particle
ELIDED = {N(k): v for k, v in ELIDED.items()}

# The texts.  order: (id, short label used in the tables, corpus group).
# Sentence segmentation follows one uniform rule for every text: sentences
# end at the full stops of the modern edited text (see SENTENCE SEGMENTATION
# in the module docstring).
TEXTS = [
    ('isocrates_csoph',    'Isoc., C. soph.',    'control'),
    ('isocrates_paneg',    'Isoc., Paneg.',      'control'),
    ('isocrates_helen',    'Isoc., Helen',       'control'),
    ('xenophon_vect',      'Xen., Vect.',        'control'),
    ('xenophon_eqmag',     'Xen., Eq. mag.',     'control'),
    ('xenophon_lac',       'Xen., Lac.',         'control'),
    ('gorgias_helen',      'Gorg., Helen',       'supplementary'),
    ('hippocrates_dearte', 'Hipp., De arte',     'supplementary'),
    ('hippocrates_flat',   'Hipp., Flat.',       'supplementary'),
    ('antisthenes_ajax',   'Antisth., Ajax',     'supplementary'),
    ('antisthenes_od',     'Antisth., Od.',      'supplementary'),
    ('alcidamas_soph',     'Alcidamas, Soph.',   'alcidamas'),
    ('alcidamas_od',       '"Alcidamas", Od.',   'alcidamas'),
]

# Text-critical adjustments, applied to the named section's raw text before
# tokenisation.  Each entry documents a deviation recorded in the article's
# methods notes.
def _excise_helen_12(text):
    """Gorgias, Helen 12: the corrupt stretch (obelised in the editions),
    41 words from τίς οὖν αἰτία κωλύει to τὴν αὐτὴν ἔχει, is excluded from
    all word and particle counts."""
    start = text.find('τίς οὖν αἰτία κωλύει')
    end = text.find('τὴν αὐτὴν ἔχει')
    if start == -1 or end == -1:
        raise ValueError('Helen 12 corrupt stretch not found')
    end += len('τὴν αὐτὴν ἔχει.')
    return text[:start] + ' ' + text[end:]

def _merge_kaitoi(text):
    """Hippocrates, De arte 5 and 11: the divided Καί τοι of the transmitted
    file is read as καίτοι."""
    return re.sub(r'([Κκ])αί τοι\b', r'\1αίτοι', text)

def _dearte_stray_stop(text):
    """Hippocrates, De arte 8: one stray full stop (πῦρ. ὄργανον) in the
    transmitted file is treated as non-final (affects sentence counts only,
    never word or particle counts)."""
    return re.sub(r'πῦρ\.\s+ὄργανον', 'πῦρ ὄργανον', text)

ADJUSTMENTS = {
    ('gorgias_helen', 'Main Body'): [_excise_helen_12],
    ('hippocrates_dearte', 'Proem'): [_merge_kaitoi],
    ('hippocrates_dearte', 'Main Body'): [_merge_kaitoi, _dearte_stray_stop],
    ('hippocrates_dearte', 'Epilogue'): [_merge_kaitoi],
}

SECTIONS = ['Proem', 'Main Body', 'Epilogue']

# --------------------------------------------------------------------------
# Tokenisation and counting
# --------------------------------------------------------------------------

LACUNA = re.compile(r'(?:\.\s+){2,}\.?')       # runs of spaced lacuna dots
FREE_NUMBER = re.compile(r'(?<![\w])\d+\.?(?![\w])')
STRIP_CHARS = '.,··;:!?—–()«»"…‧*/⋯„“”‚‘'

def clean(text):
    text = N(text)
    text = LACUNA.sub(' ', text)
    text = text.replace('[', '').replace(']', '')
    text = text.replace('(', '').replace(')', '')
    text = FREE_NUMBER.sub(' ', text)
    return text

def tokenize(text):
    """Split cleaned text into word tokens (punctuation stripped, elision
    apostrophes retained on the token)."""
    tokens = []
    for word in clean(text).split():
        word = word.strip(STRIP_CHARS)
        if word:
            tokens.append(word)
    return tokens

def particle_type(token):
    """Return the particle type of a token, or None."""
    t = N(token)
    if t and t[-1] in APOSTROPHES:              # explicit elision
        return ELIDED.get(N(t[:-1].lower()))
    low = N(t.lower())
    if low in LOOKUP:
        return LOOKUP[low]
    return ELIDED.get(low)                       # bare elision (no apostrophe)

def count_particles(tokens):
    counts = dict.fromkeys(SIXTEEN, 0)
    for token in tokens:
        p = particle_type(token)
        if p:
            counts[p] += 1
    return counts

def arg_count(counts):
    return sum(counts[p] for p in ARGUMENTATIVE)

# --------------------------------------------------------------------------
# Sentence segmentation
# --------------------------------------------------------------------------

SENTENCE_END = re.compile(r'[.!?]')

def sentences(text):
    """Return word counts per sentence.  Sentences end at the full stops of
    the modern edited text; neither the Greek middle stop nor the Greek
    question mark (";") is a boundary.  One uniform rule for every text."""
    parts = SENTENCE_END.split(clean(text))
    lengths = []
    for part in parts:
        n = len(tokenize(part))
        if n:
            lengths.append(n)
    return lengths

# --------------------------------------------------------------------------
# Sliding-window test
# --------------------------------------------------------------------------

def window_features(tokens, window_len):
    """Per-window rates (per 100 words) of γάρ, μέν, δέ, καί and composite
    argumentative density, for every window of window_len words, step 1.
    Computed incrementally over the token stream."""
    types = [particle_type(t) for t in tokens]
    feats = []
    n = len(tokens)
    if n < window_len:
        return feats
    counts = {'γάρ': 0, 'μέν': 0, 'δέ': 0, 'καί': 0, 'arg': 0}
    def bump(i, d):
        p = types[i]
        if p:
            if p in counts:
                counts[p] += d
            if p in ARGUMENTATIVE:
                counts['arg'] += d
    for i in range(window_len):
        bump(i, +1)
    scale = 100.0 / window_len
    feats.append({k: v * scale for k, v in counts.items()})
    for i in range(window_len, n):
        bump(i - window_len, -1)
        bump(i, +1)
        feats.append({k: v * scale for k, v in counts.items()})
    return feats

def mean_sd(values):
    m = sum(values) / len(values)
    var = sum((v - m) ** 2 for v in values) / len(values)   # population SD
    return m, math.sqrt(var)

def sliding_window(mb_tokens, frame_tokens):
    """Standardised distance of the frame from the body's frame-length
    window distribution, plus at-least-as-extreme shares."""
    window_len = len(frame_tokens)
    feats = window_features(mb_tokens, window_len)
    if not feats:
        return None
    fc = count_particles(frame_tokens)
    scale = 100.0 / window_len
    frame = {'γάρ': fc['γάρ'] * scale, 'μέν': fc['μέν'] * scale,
             'δέ': fc['δέ'] * scale, 'καί': fc['καί'] * scale,
             'arg': arg_count(fc) * scale}
    out = {'windows': len(feats)}
    extreme = {}
    for key in ['γάρ', 'μέν', 'δέ', 'καί', 'arg']:
        values = [f[key] for f in feats]
        m, sd = mean_sd(values)
        z = (frame[key] - m) / sd if sd > 0 else float('nan')
        out['z_' + key] = z
        if frame[key] <= m:      # frame below body mean: extreme = at or below
            flags = [f[key] <= frame[key] for f in feats]
        else:                     # frame above body mean: extreme = at or above
            flags = [f[key] >= frame[key] for f in feats]
        extreme[key] = flags
        out['pct_' + key] = 100.0 * sum(flags) / len(feats)
    joint5 = [all(extreme[k][i] for k in ['γάρ', 'μέν', 'δέ', 'καί', 'arg'])
              for i in range(len(feats))]
    joint3 = [all(extreme[k][i] for k in ['γάρ', 'καί', 'arg'])
              for i in range(len(feats))]
    out['pct_joint5'] = 100.0 * sum(joint5) / len(feats)
    out['pct_joint3'] = 100.0 * sum(joint3) / len(feats)
    return out

# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------

def load_text(path):
    sections = {}
    current = None
    for line in open(path, encoding='utf-8'):
        stripped = line.strip()
        if stripped.startswith('# SECTION:'):
            current = stripped.split(':', 1)[1].strip()
            sections[current] = []
            continue
        if stripped.startswith('#'):
            continue
        if current is not None and stripped:
            sections[current].append(stripped)
    return {sec: ' '.join(parts) for sec, parts in sections.items()}

def analyze_text(tid, data_dir):
    path = os.path.join(data_dir, tid + '.txt')
    if not os.path.exists(path):
        return None
    raw = load_text(path)
    result = {'sections': {}}
    for sec in SECTIONS:
        text = raw.get(sec, '')
        for adjust in ADJUSTMENTS.get((tid, sec), []):
            text = adjust(N(text))
        tokens = tokenize(text)
        counts = count_particles(tokens)
        sent = sentences(text)
        result['sections'][sec] = {
            'tokens': tokens,
            'words': len(tokens),
            'counts': counts,
            'arg': arg_count(counts),
            'sentences': len(sent),
            'sent_lengths': sent,
        }
    p = result['sections']['Proem']
    e = result['sections']['Epilogue']
    frame_counts = {k: p['counts'][k] + e['counts'][k] for k in SIXTEEN}
    result['frame'] = {
        'tokens': p['tokens'] + e['tokens'],
        'words': p['words'] + e['words'],
        'counts': frame_counts,
        'arg': arg_count(frame_counts),
    }
    return result

# --------------------------------------------------------------------------
# Derived quantities
# --------------------------------------------------------------------------

def rate(count, words):
    return 100.0 * count / words if words else float('nan')

def ratios(result):
    """Frame:body ratios for γάρ, μέν, δέ, καί and the composite density
    ratio MB / (P+E)."""
    mb = result['sections']['Main Body']
    fr = result['frame']
    out = {}
    for particle in ['γάρ', 'μέν', 'δέ', 'καί']:
        mb_rate = rate(mb['counts'][particle], mb['words'])
        fr_rate = rate(fr['counts'][particle], fr['words'])
        out[particle] = fr_rate / mb_rate if mb_rate else float('nan')
    mb_density = rate(mb['arg'], mb['words'])
    fr_density = rate(fr['arg'], fr['words'])
    out['density'] = mb_density / fr_density if fr_density else float('nan')
    return out

def sentence_row(result):
    row = {}
    for sec, key in [('Proem', 'P'), ('Main Body', 'MB'), ('Epilogue', 'E')]:
        s = result['sections'][sec]
        mean = s['words'] / s['sentences'] if s['sentences'] else float('nan')
        row[key + '_mean'] = mean
        row[key + '_n'] = s['sentences']
        row[key + '_words'] = s['words']
    means = [row['P_mean'], row['MB_mean'], row['E_mean']]
    row['range'] = max(means) - min(means)
    return row

# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------

def fmt(x, nd=2):
    if isinstance(x, float):
        if math.isnan(x):
            return '—'
        return f'{x:.{nd}f}'
    return str(x)

def write_csv(path, header, rows):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    print('wrote', path)

# --------------------------------------------------------------------------
# Outlier test on the composite-density ratio (note to the Table 3 discussion)
# --------------------------------------------------------------------------

def _betacf(a, b, x):
    """Continued fraction for the incomplete beta function (Numerical
    Recipes, betacf)."""
    MAXIT, EPS, FPMIN = 200, 3e-14, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    if abs(d) < FPMIN:
        d = FPMIN
    d = 1.0 / d
    h = d
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < EPS:
            break
    return h

def _betainc(a, b, x):
    """Regularised incomplete beta function I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(lbeta + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b

def t_sf(t, df):
    """Upper-tail probability P(T > t) for Student's t with df degrees of
    freedom (one-sided p-value)."""
    x = df / (df + t * t)
    p = 0.5 * _betainc(df / 2.0, 0.5, x)
    return p if t >= 0 else 1.0 - p

def outlier_test(results, comparison_ids, test_id='alcidamas_soph'):
    """Prediction-interval t-test: is the test text's composite-density
    ratio (MB : P+E, Table 3 final column) consistent with the comparison
    texts treated as a sample of single-author variation?

    Ratios are compared on the natural-log scale, so that ratios below and
    above 1.00 are weighted symmetrically.  With n comparison values of mean
    m and sample standard deviation s, the statistic for a new value x is
    t = (x - m) / (s * sqrt(1 + 1/n)) on n - 1 degrees of freedom; the
    one-sided p is the probability that a further single-author text would
    show a ratio at least as large.
    """
    def log_ratio(r):
        return math.log(ratios(r)['density'])
    vals = [log_ratio(results[i]) for i in comparison_ids if i in results]
    n = len(vals)
    m = sum(vals) / n
    s = math.sqrt(sum((v - m) ** 2 for v in vals) / (n - 1))   # sample SD
    x = log_ratio(results[test_id])
    z = (x - m) / s
    t = (x - m) / (s * math.sqrt(1.0 + 1.0 / n))
    return {'n': n, 'mean': m, 'sd': s, 'x': x, 'sd_units': z,
            't': t, 'df': n - 1, 'p': t_sf(t, n - 1)}

def main():
    data_dir = sys.argv[1] if len(sys.argv) > 1 else 'data'
    out_dir = sys.argv[2] if len(sys.argv) > 2 else 'output'
    os.makedirs(out_dir, exist_ok=True)

    results = {}
    for tid, label, group in TEXTS:
        r = analyze_text(tid, data_dir)
        if r is None:
            print(f'note: {tid} not found in {data_dir} — skipped')
            continue
        results[tid] = r

    # Tables 1 and 4: sentence construction
    for table, groups in [('table1_sentences.csv', ('control', 'soph')),
                          ('table4_sentences.csv', ('supplementary', 'soph'))]:
        rows = []
        for tid, label, group in TEXTS:
            if tid not in results:
                continue
            want = group in groups or (tid == 'alcidamas_soph' and 'soph' in groups)
            if not want or (group == 'alcidamas' and tid != 'alcidamas_soph'):
                continue
            row = sentence_row(results[tid])
            rows.append([label,
                         f"{fmt(row['P_mean'], 1)} ({row['P_n']})",
                         f"{fmt(row['MB_mean'], 1)} ({row['MB_n']})",
                         f"{fmt(row['E_mean'], 1)} ({row['E_n']})",
                         fmt(row['range'], 1),
                         row['P_words'], row['MB_words'], row['E_words']])
        write_csv(os.path.join(out_dir, table),
                  ['Text', 'Proem mean (N)', 'MB mean (N)', 'Epil. mean (N)',
                   'Range', 'P words', 'MB words', 'E words'], rows)

    # Table 2 and the 5a-5e panels: full particle panel for every text
    rows = []
    for tid, label, group in TEXTS:
        if tid not in results:
            continue
        r = results[tid]
        p, mb, e = (r['sections'][s] for s in SECTIONS)
        fr = r['frame']
        for particle in SIXTEEN:
            mb_rate = rate(mb['counts'][particle], mb['words'])
            fr_rate = rate(fr['counts'][particle], fr['words'])
            rows.append([label, particle,
                         p['counts'][particle], fmt(rate(p['counts'][particle], p['words'])),
                         mb['counts'][particle], fmt(mb_rate),
                         e['counts'][particle], fmt(rate(e['counts'][particle], e['words'])),
                         fmt(fr_rate),
                         fmt(fr_rate / mb_rate) if mb_rate else '—'])
    write_csv(os.path.join(out_dir, 'particle_panels.csv'),
              ['Text', 'Particle', 'P n', 'P /100', 'MB n', 'MB /100',
               'E n', 'E /100', 'P+E /100', 'Ratio PE:MB'], rows)

    # Table 2 alone (Soph.), for convenience
    if 'alcidamas_soph' in results:
        r = results['alcidamas_soph']
        p, mb, e = (r['sections'][s] for s in SECTIONS)
        fr = r['frame']
        rows = []
        for particle in SIXTEEN:
            mb_rate = rate(mb['counts'][particle], mb['words'])
            fr_rate = rate(fr['counts'][particle], fr['words'])
            rows.append([particle,
                         p['counts'][particle], fmt(rate(p['counts'][particle], p['words'])),
                         mb['counts'][particle], fmt(mb_rate),
                         e['counts'][particle], fmt(rate(e['counts'][particle], e['words'])),
                         fmt(fr_rate),
                         fmt(fr_rate / mb_rate) if mb_rate else '—'])
        write_csv(os.path.join(out_dir, 'table2_soph_particles.csv'),
                  ['Particle', 'P n', 'P /100', 'MB n', 'MB /100',
                   'E n', 'E /100', 'P+E /100', 'Ratio PE:MB'], rows)

    # Tables 3 and 5: cross-section ratios (+ per-section densities, Table 5)
    for table, wanted in [('table3_control_ratios.csv', 'control'),
                          ('table5_ratios.csv', 'supplementary')]:
        rows = []
        for tid, label, group in TEXTS:
            if tid not in results:
                continue
            if group != wanted and tid != 'alcidamas_soph':
                continue
            r = results[tid]
            rr = ratios(r)
            p, mb, e = (r['sections'][s] for s in SECTIONS)
            rows.append([label, fmt(rr['γάρ']), fmt(rr['μέν']), fmt(rr['δέ']),
                         fmt(rr['καί']),
                         fmt(rate(p['arg'], p['words'])),
                         fmt(rate(mb['arg'], mb['words'])),
                         fmt(rate(e['arg'], e['words'])),
                         fmt(rr['density'])])
        write_csv(os.path.join(out_dir, table),
                  ['Text', 'γάρ', 'μέν', 'δέ', 'καί',
                   'P dens/100', 'MB dens/100', 'E dens/100',
                   'Density (MB:P+E)'], rows)

    # Sentence statistics for every text (including both Alcidamas texts)
    rows = []
    for tid, label, group in TEXTS:
        if tid not in results:
            continue
        row = sentence_row(results[tid])
        rows.append([label,
                     f"{fmt(row['P_mean'], 1)} ({row['P_n']})",
                     f"{fmt(row['MB_mean'], 1)} ({row['MB_n']})",
                     f"{fmt(row['E_mean'], 1)} ({row['E_n']})",
                     fmt(row['range'], 1),
                     row['P_words'], row['MB_words'], row['E_words']])
    write_csv(os.path.join(out_dir, 'sentences_all.csv'),
              ['Text', 'Proem mean (N)', 'MB mean (N)', 'Epil. mean (N)',
               'Range', 'P words', 'MB words', 'E words'], rows)

    # Sliding-window robustness test
    rows = []
    for tid, label, group in TEXTS:
        if tid not in results:
            continue
        r = results[tid]
        sw = sliding_window(r['sections']['Main Body']['tokens'],
                            r['frame']['tokens'])
        if sw is None:
            rows.append([label, 0] + ['—'] * 12)
            continue
        rows.append([label, sw['windows'],
                     fmt(sw['z_γάρ']), fmt(sw['z_μέν']), fmt(sw['z_δέ']),
                     fmt(sw['z_καί']), fmt(sw['z_arg']),
                     fmt(sw['pct_γάρ'], 1), fmt(sw['pct_μέν'], 1),
                     fmt(sw['pct_δέ'], 1), fmt(sw['pct_καί'], 1),
                     fmt(sw['pct_arg'], 1),
                     fmt(sw['pct_joint5'], 1), fmt(sw['pct_joint3'], 1)])
    write_csv(os.path.join(out_dir, 'sliding_window.csv'),
              ['Text', 'Windows', 'z γάρ', 'z μέν', 'z δέ', 'z καί',
               'z density', '% ≥extreme γάρ', '% μέν', '% δέ', '% καί',
               '% density', '% joint 5-feature', '% joint 3-main'], rows)

    # Outlier test on the composite-density ratio (note to the Table 3 discussion)
    if 'alcidamas_soph' in results:
        controls = [tid for tid, label, group in TEXTS if group == 'control']
        supplementary = [tid for tid, label, group in TEXTS
                         if group == 'supplementary']
        rows = []
        for name, ids in [('six control texts (Table 3)', controls),
                          ('eleven comparison texts (Tables 3 and 5)',
                           controls + supplementary)]:
            o = outlier_test(results, ids)
            rows.append([name, o['n'], fmt(o['mean'], 3), fmt(o['sd'], 3),
                         fmt(o['x'], 3), fmt(o['sd_units'], 2),
                         fmt(o['t'], 2), o['df'], fmt(o['p'], 4)])
        write_csv(os.path.join(out_dir, 'outlier_test.csv'),
                  ['Comparison set', 'n', 'Mean log ratio', 'SD log ratio',
                   'Soph. log ratio', 'SD units from mean', 't', 'df',
                   'one-sided p'], rows)

    print('done.')

if __name__ == '__main__':
    main()
