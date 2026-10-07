# Användning

> **Fristående plugin.** Det här pluginet är inte utvecklat, granskat eller supportat av Lantmäteriet. Namnet Lantmäteriet används bara för att säga vilka tjänster pluginet fungerar mot. Frågor om pluginet ställer du i [det här repots ärenden](https://github.com/matself/LM-STAC-Downloader/issues), inte till Lantmäteriets support. Data hämtas från Lantmäteriets tjänster och omfattas av deras användningsvillkor.

Geodata: Ortofoto & höjd (Lantmäteriet) hämtar ortofoto, höjddata och vektordata från Lantmäteriet. Den här sidan går igenom hela flödet, hur utsnitt
fungerar och vad man gör när något inte fungerar.

## Innan du börjar

Du behöver:

* **QGIS 3.44 eller senare.**
* **Åtkomstnycklar** (Consumer Key och Consumer Secret) från Lantmäteriets
  [API-manager](https://apimanager.lantmateriet.se/), **eller** användarnamn och lösenord för ditt
  **Geotorget-konto**. För organisationer är det systemkontot som har beställt produkterna.
* Att kontot har **beställt behörigheten** på Geotorget, till exempel:
  * *Ortofoto Nedladdning* för ortofoto
  * *Markhöjdmodell Nedladdning* för höjddata
  * nedladdningstjänsten för respektive vektorprodukt, till exempel byggnader eller fastighetsindelning

Sökningen kräver ingen inloggning, eftersom katalogerna är öppna. Nedladdningen kräver inloggning och behörighet.
Ortofotona och vissa vektorprodukter har dessutom särskilda användningsvillkor som du godkänner hos Lantmäteriet.

### Hur kontona hänger ihop

Med Geotorget-konto loggar du in direkt med kontots användarnamn och lösenord, och resten av det här avsnittet behövs
inte. Det gäller åtkomstnycklar:

* **Systemkonto**: äger behörigheterna du har beställt på Geotorget.
* **Applikation** (i API-managern): ett nyckelpar som ett program, här QGIS, använder. Den har inga behörigheter själv, utan
  kan bara använda det systemkontot har.
* **Prenumeration**: vilka API:er applikationen får anropa. Prenumerera på *STAC-bild*, *STAC-hojd* och *STAC-vektor*.

Nycklar för Nationella geodataplattformen (NGP-konsument) fungerar för sökning men får inte hämta filer i produktion.
Använd nycklar från ett systemkonto av typen *Geodataprodukter* som har beställt nedladdningstjänsterna.

## 1. Skapa en inloggning

1. Öppna panelen: menyn *Insticksprogram → Geodata: Ortofoto & höjd (Lantmäteriet)* eller ikonen i verktygsfältet.
2. Under **Anslutning** finns väljaren *Autentisering*. Här kan du välja en befintlig konfiguration, eller klicka på
   **Ny Lantmäteriet-inloggning…**.
3. Välj **typ**:
   * **Geotorget-konto (användarnamn och lösenord)**: ange användarnamn och lösenord för Geotorget. Pluginet skapar en
     Basic-konfiguration i QGIS autentiseringshanterare.
   * **API-nycklar (Consumer Key och Consumer Secret)**: pluginet skapar en OAuth 2-konfiguration (Client Credentials).

   Lösenordet eller nyckeln sparas krypterat av QGIS, inte av pluginet.
4. Har du redan en fungerande konfiguration i QGIS (Basic med Geotorget-kontot, eller Client Credentials mot
   `https://apimanager.lantmateriet.se/oauth2/token`) kan du välja den direkt.

QGIS kan be om huvudlösenord första gången.

## 2. Sök

1. Välj **tjänst**: *Ortofoto*, *Höjddata (markhöjdmodell)* eller *Vektordata*.
2. För ortofoto: välj **flygår** (från och till). Bilderna finns för många olika år, så begränsa till de år du vill ha.
3. Välj **område**, antingen:
   * **Använd kartvyn**: området blir det som syns i kartan just nu.
   * **Rita ruta**: dra en ruta i kartan.
4. Klicka **Sök**.

Sökområdet visas som en röd ruta, träffarna som blå konturer och de rutor du markerat som orange fyllning.
**Rensa sökområde och träffar** tar bort allt från kartan.

Sökningen kräver ingen inloggning. Sökningen tar som mest 1000 träffar. Blir det fler visas ett meddelande. Snäva då in området eller åren.

## 3. Välj rutor

Träffarna listas med rutans namn (för vektordata datamängdens namn), kollektion (för ortofoto områdets namn och år), typ, år, upplösning, när datat senast ändrats (höjd) och filstorlek. Typen är bildtyp för ortofoto (`rgb` för färg, `cir` för färginfraröd) och rutstorlek för höjd. Klicka på
kolumnrubrikerna för att sortera.

Markera rutor genom att:

* kryssa i dem i listan, eller använda **Markera alla** och **Avmarkera alla**, eller
* klicka på **Välj rutor i kartan** och sedan på en ruta i kartan. Klicket markerar eller avmarkerar rutan. Där flera rutor
  överlappar, till exempel olika år, visas en meny där du väljer vilken det gäller.

Under listan står hur många rutor som är valda och deras sammanlagda storlek.

Överlappande rutor, till exempel samma plats från olika år, ligger kvar i listan. Du väljer själv vilken bild du vill ha.
Vill du ha den senaste, begränsa **flygår** innan du söker.

## 4. Hämta

Välj **målmapp** under *Hämta*. Du kan också kryssa i:

* **Hämta bara det valda området (utsnitt)**, se nedan.
* **Lägg till i projektet när klart**, som öppnar filerna som rasterlager.

Klicka **Hämta valda**. Framsteget visas i panelen, och **Avbryt** stoppar hämtningen. En avbruten hämtning lämnar ingen
ofullständig fil.

Pluginet frågar innan det hämtar mer än cirka 2 GB.

### Hela filer

Utan utsnitt hämtas varje vald ruta som en hel fil, sparad som `<målmapp>/<kollektion>/<fil>.tif`. Redan hämtade filer av
rätt storlek hoppas över.

Filerna är stora:

| Data | Rutans storlek | Filstorlek |
|---|---|---|
| Ortofoto | 2,5 × 2,5 km | cirka 640 MB |
| Höjd, `mhm-*` | 2,5 × 2,5 km | cirka 8 MB |
| Höjd, `dtm-cog` | 10 × 10 km | cirka 290 MB |

### Utsnitt

Rutorna är Cloud Optimized GeoTIFF, alltså filer där en läsare kan hämta just de delar den behöver. Med
**Hämta bara det valda området (utsnitt)** hämtas därför bara de delar som täcker området du sökte på.

* Rutorna som området berör **slås ihop till en fil per kollektion och bildtyp**. För ortofoto blir det alltså en fil per år, och färgbilder (`rgb`) och färginfraröda bilder (`cir`) av samma ruta hamnar i varsin fil.
* Filen heter `<kollektion>[_<bildtyp>]_utsnitt_<minx>_<miny>_<maxx>_<maxy>.tif`, med koordinater i filens eget koordinatsystem.
* Koordinatsystemet, upplösningen och banden behålls som i originalet.
* Storleken följer området. Ett litet område ger några MB, medan en yta större än en ruta ger stora filer.
* Rutor som ligger helt utanför området hoppas över. Rutor som inte är Cloud Optimized GeoTIFF kan inte klippas.
* Utsnittet följer området du sökte på, inte kartvyn när du hämtar. Ritar du om området måste du söka och markera igen.

Ett exempel: fyra ortofotorutor (2,6 GB) som möts i ett hörn gav ett utsnitt på 436 × 436 m som en enda fil på 15 MB.

### Vektordata

Vektordata hämtas alltid som hela filer, en zip-fil per kommun eller för hela Sverige, med en GeoPackage i. Utsnitt
finns inte för vektordata, så kryssrutan döljs. Zip-filen sparas som `<målmapp>/<kollektion>/<fil>.zip` och packas upp
i en mapp med samma namn bredvid. Med **Lägg till i projektet när klart** läggs alla lager i GeoPackage-filen till i en
grupp med filens namn.

Datamängder för hela Sverige, till exempel ortnamn och kommun-, läns- och riksgränser, träffas av alla sökområden.

### Höjdkollektioner

Höjdsökningen kan ge träffar i två sorters kollektioner. I kolumnen *Typ* syns rutstorleken:

* **`dtm-cog`, 10 km-blad**: blad om 10 × 10 km, cirka 290 MB. Det är Lantmäteriets nya format, med brytgeometrier i GeoPackage
  för ytor där vatten har plattats till, och en infofil med metadata. Blad vid kusten och gränsen är avskurna till den del
  som är land och kan därför vara mindre (till exempel 10 × 5 km eller bara några MB), men de räknas ändå som 10 km-blad.
* **`mhm-*`, 2,5 km-ruta**: de äldre rutorna om 2,5 × 2,5 km, cirka 8–10 MB. Enligt Lantmäteriet slutade de uppdateras
  15 juni och avvecklas på sikt. Något slutdatum anges inte.

Båda är markhöjdmodeller med 1 m upplösning i Cloud Optimized GeoTIFF, och de täcker samma platser, så du kan få båda för
samma område. Kolumnen *Ändrad* visar när datat senast ändrats, så du ser vilken som är nyast. Välj den du vill ha. Med
utsnitt spelar filstorleken mindre roll. Se
[Lantmäteriets nyhet](https://www.lantmateriet.se/sv/geodata/vara-produkter/Produktnyheter/Geografisk-information/markhojdmodell-nedladdning-utokas-med-mer-innehall/).

## Felsökning

**"inloggningen godtogs inte" när du hämtar (HTTP 401).** Användarnamnet, lösenordet eller nycklarna stämmer inte.
Kontrollera dem, eller skapa en ny inloggning. Försöker du med Geotorget-kontot, kontrollera att du kan logga in på
Geotorget med samma uppgifter.

**"åtkomst nekad" när du hämtar (HTTP 403).** Inloggningen godtogs, men kontot får inte hämta filerna. Kontrollera att
kontot (för organisationer systemkontot) har beställt nedladdningstjänsten för produkten, till exempel *Ortofoto
Nedladdning* eller *Markhöjdmodell Nedladdning* (produktion), på Geotorget och godkänt användningsvillkoren. Med
nycklar ska applikationen dessutom prenumerera på STAC-bild, STAC-hojd respektive STAC-vektor. Nycklar för NGP räcker
inte.

**"Välj eller skapa en autentisering först".** Ingen inloggning är vald när du hämtar. Skapa eller välj en under
*Anslutning*.

**Sökningen ger inga träffar.** Kontrollera området och, för ortofoto, flygåren. Alla år finns inte överallt.

**"Sökningen begränsades till 1000".** Snäva in området eller årsintervallet.

**Inloggningen frågar efter huvudlösenord.** QGIS skyddar autentiseringsdatabasen. Ange ditt huvudlösenord.

**Hämtningen går långsamt.** Filerna är stora. Använd utsnitt, och begränsa området så mycket det går.

**Utsnittet hoppar över rutor.** Antingen ligger rutan utanför området, eller så är filen inte Cloud Optimized GeoTIFF. Då
kan du avmarkera utsnitt och hämta den som en hel fil.

Loggmeddelanden hittar du i QGIS *Loggmeddelanden*-panel, under fliken *Geodata: Ortofoto & höjd (Lantmäteriet)*.
