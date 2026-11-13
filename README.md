# Wetterdienst

## Ausgangslage

Der Deutsche Wetterdienst benötigt eine webbasierte Anwendung, die eine Auswertung aller historischen Wetterdaten ermöglicht.

Aspekte:
* Grundlage der Auswertung: Historische Einzeldaten/Tagesdaten des DWD
* Download der Tagesdaten aus dem Archiv aus der Anwendung heraus
* Abspeicherung in Datenbank 
* Auswertung  
  * Von … bis … in Tagesbasis / Monatsbasis / Jahresbasis 
  * Auswertung für beliebigen Ort / für beliebige Adresse in Deutschland. Für eine Adresse, die nicht direkt einer Wetterstation entspricht, sollen die Daten aus benachbarten Wetterstationen zusammengefaßt werden
* Die Ergebnisdarstellung sollte tabellarisch und in grafischer Form erfolgen

---

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