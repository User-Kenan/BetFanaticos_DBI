# DBI Projekt-Planung

## 1. Team & Projektidee

### Team 
```
Schüler 1: Kenan Pipic
Schüler 2: Emir Alici
```


### Domäne beschrieben

Die WPF-Applikation simuliert Sportwetten zu Bildungszwecken. Benutzer erhalten virtuelle Wett-Coins und können auf verschiedene Sportspiele wetten. Die App zeigt Quoten, Spiele und Gewinne/Verluste an. Ziel ist es, die Auswirkungen von Sportwetten zu demonstrieren. Eine Sport-Api wird verwendet, welches mit FastApi die Daten Speichert in unserem SportWettverwaltung

### Erste Überlegung zu Entitäten und Beziehungen


# Entity-Relationship-Modell

| Entität | Beschreibung | Beziehungen (Kardinalitäten) |
|---|---|---|
| User | Registrierter Spieler im System | User 1 — 1 Wallet, User 1 — 1 Statistic, User 1 — N Bet, User N — M Sidequest (über SidequestProgress) |
| Wallet | Spielgeld-Konto eines Users | Wallet 1 — 1 User |
| Statistic | Statistiken eines Users (Gewinne, Verluste, Quests etc.) | Statistic 1 — 1 User |
| Bet | Wette eines Users | Bet N — 1 User, Bet N — M Match (über BetItem) |
| BetItem | Einzelner Tipp innerhalb einer Wette (Join-Tabelle) | BetItem N — 1 Bet, BetItem N — 1 Match |
| Match | Spiel-/Matchdaten aus externer Sport-API | Match N — M Bet (über BetItem) |
| Sidequest | Definierte Aufgaben/Challenges im Spiel | Sidequest N — M User|

### Must-Haves

- Userdaten speichern (Anmeldedaten)
- Kontostand speichern
- User kann Wetten auf mehrere Spiele (auch verschiedene Sportarten)
- User kann Sidequests machen und Geld verdienen
- Statistiken können Dargestellt werden 

### Nice-To-Haves

- Einstellungen eines Users speichern
- im Statistik dann Anzeigen, wie oft man z.B eingelogged war 
- Playlist (Musik)
- Erweiterte Sport-APi (Mehr Daten z.B wetten wie viele Tore ein Spieler schießt)
- Lieblingsteam auswählen
- Side-Quest Fortschritt

### Zuweisungen 

| Aufgabe | Zuweisung |
|---|---|
| Projektidee | Kenan & Emir |
| Erste Überlegung Entitäten & Beziehungen | Kenan & Emir |
| ERM erstellen | Kenan & Emir |
| Relationales Modell (RM) | Kenan |
| Normalisierung | Emir |
| Git Repository erstellen | Kenan |
| Ordnerstruktur anlegen | Emir |
| Datenbank erstellen | Kenan |
| FastAPI Backend | Emir |
| CRUD-Endpunkte | Emir & Kenan |
| API-Testing | Emir & Kenan |
| Dokumentation | Emir & Kenan |
| Präsentation | Emir & Kenan |


## 2. Modellierungen

### ERM
![](Bilder/ERM.png)

### RM
![](Bilder/RM.png)

### 1 NF

- Wird erfüllt, weil Attribute Atomar vorliegen
- Alle Tabellen haben Key-Pairs
- Datentypen sind vordefiniert

### 2 NF

- 1NF wird erfüllt
- Jedes Nicht-Schlüssel-Attribut ist von jedem Teil des Primärschlüssels voll funktional abhängig

### 3 NF

- 2NF wird erfüllt
- Keine transitiven Abhängigkeiten (Statistik wird in c# Berechnet und in Statistic Table dann gespeichert)