# Svensk fraktur — Kraken OCR/HTR-modell

En [Kraken](https://kraken.re)-igenkänningsmodell (`.mlmodel`) för **OCR av äldre
svensk text tryckt i fraktur (blackletter)**. Den ger en diplomatarisk
transkribering som bevarar historisk stavning, lång-s (ſ) och periodens stavning,
och fungerar på skannade sidbilder.

- **Fil:** `svensk_fraktur.mlmodel`
- **Typ:** Kraken-igenkänningsmodell (baslinje/HTR-pipeline)
- **DOI:** [10.5281/zenodo.20702142](https://doi.org/10.5281/zenodo.20702142)
- **Bästa valideringsträffsäkerhet:** 0,9880 (≈ 1,2 % CER) på en utbruten del
- **Basmodell:** `german_print` (finjusterad från den)
- **Träningsdata:** Språkbanken, *Svensk fraktur 1626–1816*

## Användning

Hämta modellen direkt från Zenodo: `kraken get 10.5281/zenodo.20702142`

**Kraken (kommandorad):**

```bash
kraken -i sida.jpg ut.txt segment -bl ocr -m svensk_fraktur.mlmodel
```

För flersidiga PDF:er: rendera sidorna till bilder först (t.ex. ~300 DPI) och
skicka dem till Kraken. **eScriptorium:** importera `.mlmodel` under *Models*.

## Hur den tränades

Finjusterad från `german_print` på Språkbankens korpus *Svensk fraktur 1626–1816*
(199 sidbilder med radvisa diplomatariska transkriptioner). Sidbilderna OCR:ades
med `german_print`, och de igenkända raderna alignerades mot facittexten radvis
(≈98 % täckning) till PageXML för `ketos train`. En **låg inlärningstakt
(`-r 0.0001`) var avgörande** — den lät modellen förbättras stadigt förbi epok 0
i stället för att driva bort från den goda startpunkten. Se [`training/`](training/)
för skript och exakta kommandon.

Valideringssiffran är mätt på en utbruten del av samma korpus och är därför
optimistisk jämfört med helt nya dokument; på en verklig volym (svensk fraktur
från 1600-talet) gav den en nära felfri brödtext-transkribering med bevarat
lång-s och periodstavning, utan systematiska substitutionsfel.

## Begränsningar

- Tränad på svensk frakturtryck; inte avsedd för handskrift eller modern stil
  (antikva/roman).
- Ornerade titelsidsinitialer läses mindre tillförlitligt än brödtext.
- Utdatan är **diplomatarisk** (ordagrann): historisk stavning, lång-s och tryckta
  radbrytnings-bindestreck bevaras. Modernisering/normalisering bör ske i ett
  nedströmssteg, inte här.

## Proveniens, rättigheter och attribution

Modellen är ett derivat. Hela kedjan:

| Led | Resurs | Av | DOI | Licens |
|-----|--------|----|-----|--------|
| Basmodell | german_print (OCR-modell för tyskt tryck) | S. Weil, J. Kamlah, T. Schmidt (2023) | [10.5281/zenodo.10519596](https://doi.org/10.5281/zenodo.10519596) | **CC0-1.0** |
| Träningsdata | Svensk fraktur 1626–1816 | Språkbanken Text, Göteborgs universitet | [10.23695/5sme-7437](https://doi.org/10.23695/5sme-7437) | **CC-BY-4.0** |

Basmodellen är **CC0** (ingen attribution krävs juridiskt; anges som god sed).
Träningsdatan är **CC-BY-4.0**, vilket kräver **attribution**. När du använder
eller sprider modellen, behåll följande attribution:

> Tränad på *Svensk fraktur 1626–1816*, Språkbanken Text, Göteborgs universitet
> (digitalisering: Göteborgs universitetsbibliotek; transkription: GREPECT),
> [doi.org/10.23695/5sme-7437](https://doi.org/10.23695/5sme-7437), licens CC-BY-4.0.

Modellen släpps under **CC-BY-4.0** (se [`LICENSE`](LICENSE)).

## Citering

Se [`CITATION.cff`](CITATION.cff).
