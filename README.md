# KI in der Radiologie – Slides

Diese Präsentation ist ein LaTeX-Beamer-Projekt mit einem eigenen Theme und mehreren Inhaltsdateien.

## Projektstruktur

- `main.tex` – Haupteinstiegspunkt
- `panqueques.sty` – Theme/Styling/Beamer-Konfiguration
- `1-title-page/custom.tex` – Titelblatt
- `2-content/content.tex` – Hauptinhalt der Präsentation
- `3-reference/ref.tex` – Literatur-/Referenzfolie
- `build.sh` – Build-Skript für die PDF-Kompilierung
- `bootstrap.sh` – Installationsskript für die benötigten LaTeX-Pakete

## Voraussetzungen

Auf Ubuntu/Debian:

```bash
./bootstrap.sh
```

Das installiert die notwendigen TeX-Pakete, inklusive des Gillius-Fonts und TeXCount für die Wortzählung in VS Code.

## PDF bauen

Nach der Installation einfach:

```bash
./build.sh
```

Das erzeugt die Datei `main.pdf` im Projektordner.

## Manuell bauen

Wenn du nur die PDF neu kompilieren willst:

```bash
latexmk -pdf -interaction=nonstopmode -synctex=1 main.tex
```

## Hinweise

- Die Präsentation nutzt Beamer mit `metropolis`-Theme und ein angepasstes Styling aus `panqueques.sty`.
- Nach Änderungen am Inhalt oder an der Biblographie reicht normalerweise ein erneuter Build.
- Falls LaTeX-Fehler auftreten, zuerst `./bootstrap.sh` ausführen, damit die benötigten Pakete vorhanden sind.
