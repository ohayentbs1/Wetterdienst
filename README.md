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

Beim Klick auf „Wetterdaten ansehen“ lädt die Anwendung synchron die passenden historischen DWD-Tagesdaten der Stationen im 50-km-Umkreis, speichert die ZIP-Dateien in `storage/tmp` im Projektverzeichnis und importiert die enthaltenen Beobachtungen fortlaufend in die Datenbank.
