#!/usr/bin/env bash
# Finjusterar german_print pa den svenska fraktur-traningsdatan (PageXML i
# train_xml/) och skapar en svensk fraktur-modell. Kor pa CPU.
set -euo pipefail
cd "$(dirname "$0")"

KETOS="${KETOS:-ketos}"
GERMAN_PRINT="${GERMAN_PRINT:-german_print.mlmodel}"

mkdir -p modell
ANTAL=$(ls train_xml/*.xml 2>/dev/null | wc -l | tr -d ' ')
echo "Tranar pa $ANTAL sidor (finjustering av german_print, CPU)..."

# --resize union: behall german_prints teckenuppsattning och lagg till ev. nya
#                 tecken i svensk fraktur. -q early: tidig stopp pa valideringen.
# -d (device) och --workers ar globala ketos-flaggor och maste sta fore "train".
# --workers 0: ladda data i huvudprocessen. Pa macOS startar workers via spawn,
# vilket kraschar nar kraken forsoker pickla sina lokala transform-funktioner.
# Tranar fran det forkompilerade binara datasetet (svensk_fraktur.arrow) -
# radbilderna ar redan utklippta, sa varje epok blir mycket snabbare. Skapas med:
#   ketos --workers 0 compile -f page -o svensk_fraktur.arrow train_xml/*.xml
# -r 0.0001: lag inlarningstakt for finjustering. Med standard 0.001 forsamrades
# valideringen efter epok 0 (modellen drev bort fran german_print). Lagre lr later
# den forbattras forbi epok 0. Utdata till v2-mapp sa forsta korningen behalls.
"$KETOS" -d cpu --workers 0 train \
  -f binary \
  -i "$GERMAN_PRINT" \
  --resize union \
  -r 0.0001 \
  -q early \
  --lag 5 \
  -p 0.9 \
  -o modell/svensk_fraktur_v2 \
  svensk_fraktur.arrow

echo "Klart."
