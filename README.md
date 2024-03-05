# Introductie

De repository bevat de SQL scripts en Python scripts voor het inrichten van de HAS sensor data infrastructuur.

## Werken met Codespace

We maken gebruik van [Codespaces](https://docs.github.com/en/codespaces/overview), een online omgeving voor het draaien van de Python scripts. Hiervoor heb je een Github account nodig. [hier](https://docs.github.com/en/get-started/start-your-journey/creating-an-account-on-github) krijg je uitleg over het aanmaken van een Github account. Maak een Github account aan als je nog geen account hebt.

- Open je browser en open de volgende link: https://github.com/MarkTerlien/ttn_workshop en `Sign in`. 
- Open de template _ttn\_workshop_ in je eigen Codespace via `Use this template => Open in a codespace`

Er wordt nu online een nieuwe Codespace gemaakt op basis van de template. Deze template bevat verschillende folders met Python scripts. Ga naar de folder _sensor_\database_\v2_. Hier vind je het script *register_new_device.py* dat nodig is om nieuwe devices met sensoren te registreren. Open het script *register_new_device.py*.

Het script wordt herkend als een Python script en daarom vraagt Codespaces om een Python extensie te installeren. Klik op `Install` om deze te installeren. 

Om databasetoegang te krijgen, hernoem je het bestand _db-dummy.txt_ naar _db.txt_ en vervangt u *db_user* door uw databaseaccount en vervangt u *db_password* door uw databasewachtwoord. Zorg ervoor dat je de regel afsluit met `:`. Het bestand *db.txt* staat niet onder versiebeheer en wordt niet opgeslagen in Github.

## Foldersctructuur

De folder *datamodel* bevat een beschrijving van het datamodel, het ERD van het datamodel en het SQL script *QuickDBD-Sensor Database 2.0.sql* om de tabellen en de views op de database te creëren en de metadata van de devices toe te voegen.

De folder *sensor_metadata* bevat de volgende csv-bestanden:

- *model_url.csv* met de devices die ondersteund worden.
- *sensor_parameters.csv* met de parameters (sensoren) die per device gemeten worden.

De bestanden zijn ingelezen in de database in de tabellen *model* en *parameter*. 

