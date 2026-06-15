---
id: svensk-fraktur-kraken
summary: "Kraken recognition model for older Swedish Fraktur (1626-1816), fine-tuned from german_print."
authors:
  - name: Magnus Kolsjö
license: CC-BY-4.0
software_name: kraken
language:
  - swe
script:
  - Latf
model_type:
  - recognition
metrics:
  cer: 1.2
base_model:
  - 10.5281/zenodo.10519596
datasets:
  - 10.23695/5sme-7437
keywords:
  - fraktur
  - swedish
  - historical
---

# Swedish Fraktur — Kraken recognition model

A Kraken recognition model for OCR of older Swedish text printed in Fraktur
(blackletter). It produces a diplomatic transcription that preserves historical
orthography, the long s (ſ) and period spelling.

## Training data and standards

Fine-tuned from `german_print` (CC0) on Språkbanken's *Svensk fraktur 1626-1816*
(CC-BY-4.0; DOI 10.23695/5sme-7437) — 199 page images with line-level diplomatic
transcriptions (double-keyed by GREPECT, digitised by Gothenburg University
Library). Page images were OCR-bootstrapped and the lines aligned to the
ground-truth line text (~98 % coverage) to produce PageXML for `ketos train`.
Trained with a low learning rate (-r 0.0001); best validation accuracy 0.9880
(~1.2 % CER) on a held-out split.

Transcription standard: diplomatic — historical spelling, long-s and printed
line-break hyphens are preserved; modernisation is left to downstream steps.

## Attribution

Trained on *Svensk fraktur 1626-1816*, Språkbanken Text, University of Gothenburg,
https://doi.org/10.23695/5sme-7437, licensed CC-BY-4.0.
