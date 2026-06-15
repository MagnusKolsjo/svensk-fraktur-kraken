---
license: cc-by-4.0
language:
- sv
tags:
- kraken
- htr
- ocr
- fraktur
- swedish
- historical
pipeline_tag: image-to-text
---

# Swedish Fraktur — Kraken OCR/HTR model

A [Kraken](https://kraken.re) recognition model (`.mlmodel`) for **OCR of older
Swedish text printed in Fraktur (blackletter)**. It produces a diplomatic
transcription that keeps historical orthography, the long s (ſ) and period
spelling, and works on scanned page images.

- **File:** `svensk_fraktur.mlmodel`
- **Type:** Kraken recognition model (baseline/HTR pipeline)
- **DOI:** [10.5281/zenodo.20702142](https://doi.org/10.5281/zenodo.20702142)
- **Best validation accuracy:** 0.9880 (≈ 1.2 % CER) on a held-out split
- **Base model:** `german_print` (fine-tuned from it)
- **Training data:** Språkbanken, *Svensk fraktur 1626–1816*

## Usage

Fetch the model directly from Zenodo: `kraken get 10.5281/zenodo.20702142`

**Kraken (CLI):**

```bash
kraken -i page.jpg out.txt segment -bl ocr -m svensk_fraktur.mlmodel
```

For multi-page PDFs, render pages to images first (e.g. ~300 DPI) and pass them
to Kraken. **eScriptorium:** import the `.mlmodel` under *Models*.

## How it was trained

Fine-tuned from `german_print` on the Språkbanken corpus *Svensk fraktur
1626–1816* (199 page images with line-level diplomatic transcriptions). The page
images were OCR-bootstrapped and the recognized lines aligned to the ground-truth
line text (≈98 % coverage), producing PageXML for `ketos train`. A low learning
rate (`-r 0.0001`) was decisive — it let the model improve steadily past epoch 0
instead of drifting away from the strong starting point. See [`training/`](training/)
for the scripts and exact commands.

The validation accuracy is measured on a held-out split of the same corpus and is
therefore optimistic relative to entirely new documents; on a real volume
(1600s Swedish Fraktur) it produced a near-flawless body-text transcription with
preserved long-s and period spelling and no systematic substitution errors.

## Limitations

- Trained on Swedish Fraktur print; not intended for handwriting or modern
  (antiqua/roman) type.
- Ornate/decorated title-page initials are read less reliably than body text.
- Output is **diplomatic** (verbatim): historical spelling, long-s and printed
  line-break hyphens are preserved. Modernisation/normalisation should happen in
  a downstream step, not here.

## Provenance, rights and attribution

This is a derivative model. Full chain:

| Layer | Resource | By | DOI | License |
|-------|----------|----|-----|---------|
| Base model | german_print (OCR model for German prints) | S. Weil, J. Kamlah, T. Schmidt (2023) | [10.5281/zenodo.10519596](https://doi.org/10.5281/zenodo.10519596) | **CC0-1.0** |
| Training data | Svensk fraktur 1626–1816 | Språkbanken Text, University of Gothenburg | [10.23695/5sme-7437](https://doi.org/10.23695/5sme-7437) | **CC-BY-4.0** |

The base model is **CC0** (no attribution legally required; cited as courtesy).
The training data is **CC-BY-4.0**, which requires **attribution**. When you use
or redistribute this model, please keep the following attribution:

> Trained on *Svensk fraktur 1626–1816*, Språkbanken Text, University of
> Gothenburg (digitisation: Gothenburg University Library; transcription:
> GREPECT), [doi.org/10.23695/5sme-7437](https://doi.org/10.23695/5sme-7437),
> licensed CC-BY-4.0.

This model is released under **CC-BY-4.0** (see [`LICENSE`](LICENSE)).

## Citation

See [`CITATION.cff`](CITATION.cff).
