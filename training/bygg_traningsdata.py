"""Bygger Kraken-traningsdata (PageXML) fran Sprakbankens fraktur-dataset.

Steg per sida:
  1. Segmentera + OCR med german_print -> PageXML med radkoordinater + OCR-text.
  2. Rensa facit-transkriptionen (ta bort <fr>/<aq>-taggar och tomrader).
  3. Alignera OCR-radernas text mot facitraderna (sekvens-alignment pa likhet).
  4. Behall matchade rader: ersatt OCR-texten med facit. Ta bort omatchade
     extrarader (sidnummer, custos, kolumntitlar som saknar facit).
  5. Skriv en tranings-PageXML som pekar pa originalbilden.

Anrop:
  python bygg_traningsdata.py [antal]   # antal = begransa for validering
"""
import difflib
import glob
import os
import re
import subprocess
import sys

from lxml import etree

ROT = os.path.dirname(os.path.abspath(__file__))
KRAKEN = "${KRAKEN:-kraken}"
GERMAN_PRINT = "${GERMAN_PRINT:-german_print.mlmodel}"
RAW = os.path.join(ROT, "raw_xml")
TRAIN = os.path.join(ROT, "train_xml")
NS = {"p": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15"}
SIM_TROSKEL = 0.5  # lagsta likhet for att para en OCR-rad med en facitrad


def hitta_par():
    """Returnerar (bild, facit-txt)-par dar bada finns."""
    par = []
    for img in sorted(glob.glob(os.path.join(ROT, "images", "*", "*.jpg"))):
        bok = os.path.basename(os.path.dirname(img))
        sida = os.path.splitext(os.path.basename(img))[0]
        txt = os.path.join(ROT, "transcriptions", f"{bok}_{sida}.txt")
        if os.path.exists(txt):
            par.append((img, txt, f"{bok}_{sida}"))
    return par


def rensa_facit(txt_vag):
    """Tar bort <fr>/<aq>-taggar och tomrader -> ordnad lista av radtexter."""
    rader = []
    for rad in open(txt_vag, encoding="utf-8"):
        rad = re.sub(r"<[^>]+>", " ", rad)
        rad = re.sub(r"\s+", " ", rad).strip()
        if rad:
            rader.append(rad)
    return rader


def kor_ocr(par):
    """Kor segmentering + OCR pa alla sidor i ett anrop (modell laddas en gang)."""
    os.makedirs(RAW, exist_ok=True)
    cmd = [KRAKEN, "-x", "-f", "image"]
    att_kora = []
    for img, _, namn in par:
        ut = os.path.join(RAW, namn + ".xml")
        if not os.path.exists(ut):
            cmd += ["-i", img, ut]
            att_kora.append(namn)
    if att_kora:
        print(f"OCR pa {len(att_kora)} sidor (kan ta en stund)...", flush=True)
        cmd += ["segment", "-bl", "ocr", "-m", GERMAN_PRINT]
        subprocess.run(cmd)


def las_ocr_rader(xml_vag):
    """Returnerar [(TextLine-element, OCR-text)] i dokumentordning."""
    trad = etree.parse(xml_vag)
    rader = []
    for tl in trad.findall(".//p:TextLine", NS):
        # radnivans text ligger i TextLine/TextEquiv/Unicode (sista, ej ord/glyf)
        txt = ""
        for te in tl.findall("./p:TextEquiv/p:Unicode", NS):
            txt = te.text or ""
        rader.append((tl, txt.strip()))
    return trad, rader


def alignera(ocr_rader, facit):
    """Needleman-Wunsch pa likhet. Returnerar par av (ocr_idx, facit_idx)."""
    likhet = lambda a, b: difflib.SequenceMatcher(None, a, b).ratio()
    n, m = len(ocr_rader), len(facit)
    GAP = -0.4
    dp = [[0.0] * (m + 1) for _ in range(n + 1)]
    bt = [[""] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        dp[i][0] = dp[i - 1][0] + GAP; bt[i][0] = "u"
    for j in range(1, m + 1):
        dp[0][j] = dp[0][j - 1] + GAP; bt[0][j] = "l"
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            diag = dp[i - 1][j - 1] + likhet(ocr_rader[i - 1], facit[j - 1])
            up = dp[i - 1][j] + GAP
            left = dp[i][j - 1] + GAP
            dp[i][j] = max(diag, up, left)
            bt[i][j] = "d" if dp[i][j] == diag else ("u" if dp[i][j] == up else "l")
    i, j, par = n, m, []
    while i > 0 and j > 0:
        if bt[i][j] == "d":
            par.append((i - 1, j - 1)); i -= 1; j -= 1
        elif bt[i][j] == "u":
            i -= 1
        else:
            j -= 1
    par.reverse()
    return [(pi, gj) for pi, gj in par
            if likhet(ocr_rader[pi], facit[gj]) >= SIM_TROSKEL]


def satt_radtext(tl, text):
    """Satter TextLine-radens text till facit och tar bort ord/glyf-barn."""
    for barn in list(tl):
        tag = etree.QName(barn).localname
        if tag in ("Word", "TextEquiv"):
            tl.remove(barn)
    te = etree.SubElement(tl, f"{{{NS['p']}}}TextEquiv")
    uni = etree.SubElement(te, f"{{{NS['p']}}}Unicode")
    uni.text = text


def bygg_sida(img, xml_vag, facit_rader, namn):
    """Producerar tranings-PageXML for en sida. Returnerar antal behallna rader."""
    trad, ocr = las_ocr_rader(xml_vag)
    ocr_txt = [t for _, t in ocr]
    par = alignera(ocr_txt, facit_rader)
    behall = {pi: facit_rader[gj] for pi, gj in par}
    for idx, (tl, _) in enumerate(ocr):
        if idx in behall:
            satt_radtext(tl, behall[idx])
        else:
            tl.getparent().remove(tl)  # omatchad extrarad
    # peka pa absolut bildsokvag sa ketos hittar bilden oavsett cwd
    sida = trad.find(".//p:Page", NS)
    if sida is not None:
        sida.set("imageFilename", os.path.abspath(img))
    os.makedirs(TRAIN, exist_ok=True)
    trad.write(os.path.join(TRAIN, namn + ".xml"),
               encoding="UTF-8", xml_declaration=True)
    return len(behall), len(ocr), len(facit_rader)


def main():
    par = hitta_par()
    if len(sys.argv) > 1:
        steg = max(1, len(par) // int(sys.argv[1]))
        par = par[::steg][: int(sys.argv[1])]
    print(f"Bearbetar {len(par)} sidor.\n")
    kor_ocr(par)
    tot_behall = tot_ocr = tot_facit = 0
    print(f"{'sida':18} {'behall':>6} {'ocr':>4} {'facit':>5} {'tackn.':>7}")
    for img, txt, namn in par:
        xml_vag = os.path.join(RAW, namn + ".xml")
        if not os.path.exists(xml_vag):
            continue
        facit = rensa_facit(txt)
        b, o, f = bygg_sida(img, xml_vag, facit, namn)
        tot_behall += b; tot_ocr += o; tot_facit += f
        print(f"{namn:18} {b:>6} {o:>4} {f:>5} {b / max(f,1) * 100:>6.0f}%")
    print(f"\nTotalt: {tot_behall} traningsrader behallna "
          f"(av {tot_facit} facitrader, {tot_behall / max(tot_facit,1) * 100:.0f}% tackning).")


if __name__ == "__main__":
    main()
