# Training / reproduction

How `svensk_fraktur.mlmodel` was produced, so it can be reproduced or improved.

## Requirements

- [Kraken](https://kraken.re) (provides `kraken` and `ketos`), Python ≤ 3.13.
- The base model **german_print**: `kraken get 10.5281/zenodo.10519596`
- The dataset **Svensk fraktur 1626-1816** (CC-BY-4.0):
  https://doi.org/10.23695/5sme-7437 — 199 page images + line-level
  transcriptions. (Not redistributed here; download from Språkbanken.)

## Steps

1. **Build training data (PageXML).** `bygg_traningsdata.py` renders each page,
   OCRs it with german_print to get line coordinates, aligns the recognised lines
   to the dataset's ground-truth line text, and writes one PageXML per page.
   Configure paths via environment variables (`KRAKEN`, `KETOS`, `GERMAN_PRINT`)
   and point it at the unpacked dataset.

2. **Compile + fine-tune.** `trana.sh`:

   ```bash
   # compile a binary dataset (one-time line extraction)
   ketos --workers 0 compile -f page -o svensk_fraktur.arrow train_xml/*.xml
   # fine-tune from german_print, low learning rate
   ketos -d cpu --workers 0 train -f binary -i german_print.mlmodel \
     --resize union -r 0.0001 -q early --lag 5 -p 0.9 \
     -o modell/svensk_fraktur svensk_fraktur.arrow
   ```

## Notes

- **Low learning rate (`-r 0.0001`) is decisive.** With the default 0.001 the
  model degraded after epoch 0; with 1e-4 it improved steadily (best val 0.9880).
- On macOS, run with `--workers 0` (the spawn start method cannot pickle Kraken's
  local transform functions otherwise).
- Kraken training runs on CPU (PyTorch Lightning does not support Apple MPS for
  training).
