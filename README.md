# Wetterdienst

Eine kleine Wetterdienst-Webanwendung auf Basis von Flask, SQLite und Tailwind CSS. Flask stellt die Seiten bereit; Tailwind erzeugt das Stylesheet aus den Templates.

## Voraussetzungen

- Git
- Python 3
- Node.js mit npm

## Projekt lokal aufsetzen

Repository klonen und in das Projektverzeichnis wechseln:

```sh
git clone https://github.com/ohayentbs1/Wetterdienst.git
cd Wetterdienst
```

Virtuelle Python-Umgebung anlegen und aktivieren. Unter Windows (PowerShell):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Python-Abhängigkeiten und Tailwind-Entwicklungswerkzeuge installieren:

```sh
python -m pip install -r requirements.txt
npm install
```

## Entwicklungsserver starten

Tailwind und Flask laufen während der Entwicklung parallel in zwei Terminals. Im ersten Terminal im Projektverzeichnis den CSS-Watcher starten:

```sh
npm run watch
```

Im zweiten Terminal die virtuelle Python-Umgebung aktivieren (siehe oben). Bei einer neuen oder leeren Datenbank zuerst das Datenbankschema anlegen:

```sh
flask db upgrade
```

Anschließend den Flask-Entwicklungsserver starten:

```sh
flask run
```

Die Anwendung ist anschließend unter <http://127.0.0.1:5000> erreichbar. `flask db upgrade` wendet die vorhandenen Migrationen an und legt die SQLite-Datenbank bei Bedarf an. Der Tailwind-Watcher aktualisiert `app/static/css/style.css`, wenn sich die CSS-Eingabe oder Templates ändern.

Nach der Ortsauswahl kann ein Start- und Enddatum gewählt werden. Beim Laden werden weiterhin die historischen DWD-Tagesdaten der Stationen im 50-km-Umkreis synchron heruntergeladen, in `storage/tmp` gespeichert und in die Datenbank importiert. Für die Anzeige werden höchstens die fünf nächstgelegenen Stationen berücksichtigt; die Messwerte jeder Kategorie werden pro Tag mit `1 / Entfernung in km` gewichtet. Ein Liniendiagramm zeigt die kontinuierlichen Wetter-Messgrößen im gewählten Zeitraum. Qualitätskennzahlen und der Niederschlagsform-Code werden nicht als Messwertlinien dargestellt.
