# twitter-analyzer
Eine Sammlung an Skripten um die Twitteraktivität von Mitgliedern des deutschen Bundestag zu scannen und zu analysieren.

## Motivation

Inspiriert ist dieses Projekt durch das Paper [Im Zerrspiegel des Populismus](https://rdcu.be/cbptI). Aus diesem landete ein Grafik in einem meiner Chats und ich hatte Lust die Daten selbst zu analysieren und für jeden reproduzierbar anzubieten. Die Quelle der Grafik habe ich erst spät in der Entwicklung entdeckt und ein Vergleich mit meinen Ergebnissen steht noch aus.

## Status des Projekts

Während der Entwicklung hat Twitter die alte Schnittstelle für Daten abgeschaltet, die genutzt wurde um an die Daten zu kommen. Dadurch steht das Projekt momentan still.

Ein Ausweichen auf die offizielle API ist nicht möglich, da Sie Limitation für die History hat. Dies würde dazu führen, dass für einzelne Politiker mit super hoher Aktivität nur ein Teil der Daten ausgewertet werden würde.

## How to

1. Kopie des Git erstellen

    ```
    git clone https://github.com/Aiyubi/twitter-analyzer.git
    ```

1. Installieren der nötigen Pakete

    ```
    pip install -r requirements.txt
    ```

1. Datenbank anlegen

    ```
    python3 database_model.py
    ```

1. Um die Datenbank mit Daten zu füllen wird Abgeornetenwatch genutzt

    ```
    python3 scrape-abgeordnetenwatch.py
    ```

1. Daten per Hand bearbeiten

    Hierfür muss man je nach Datenbank ein passendes Programm benutzen.

1. Daten von Twitter laden

    ```
    python3 scrape-twitter.py
    ```
    
1. Links zu Webseiten aus den Tweets extrahieren und prüfen wohin sie zeigen

    ```
    python3 scrape-links.py
    ```

1. Create the graphs for the results
    ```
    python3 visualize.py
    python3 visualize-links.py
    ```

## Ergebnisse

TODO
