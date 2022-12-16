## Installation und Einrichtung des Projektes

### Clone Git Repository
Falls git noch nicht installiert ist: http://git-scm.com/download/

In den Ordner navigieren wo das Projekt liegen soll, Terminal öffnen und die folgenden Befehle ausführen:
- $ git clone https://github.com/T-Berger/minveo_graph.git


### API Key Tool
Da das Projekt in Github öffentlich ist, soll der Api-Key nicht im Code ersichtlich sein. Dafür gibt es ein Tool welches installiert werden muss.

In das lokale Git-Repository navigieren, Terminal öffnen und folgende Befehle ausführen:
- $ pip install python-decouple
- $ touch .env; open .env

Die Datei .env sollte nun erstellt sein und sich geöffnet haben. Nun den in Miro hinterlegten API_KEY in die Datei schreiben.

### EOD-Historical Data Package
Um die benötigten Daten zu erhalten müssen wir ein package installieren:
- $ pip install git+https://github.com/femtotrader/python-eodhistoricaldata.git

