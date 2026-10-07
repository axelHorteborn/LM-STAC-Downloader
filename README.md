<img src="lm_stac_downloader/icon.svg" alt="" width="72" align="right">

# Geodata: Ortofoto & höjd (Lantmäteriet)

A QGIS plugin for searching and downloading **raster and vector data** from Lantmäteriet's (the Swedish
mapping, cadastral and land registration authority) STAC services, with map-based search.

> **Independent plugin.** This plugin is not developed, reviewed or supported by Lantmäteriet. The name
> Lantmäteriet is used only to state which services the plugin works against. Questions about the plugin
> belong in [this repository's issues](https://github.com/matself/LM-STAC-Downloader/issues), not with
> Lantmäteriet's support. Data is fetched from Lantmäteriet's services and is subject to their terms of use.

Draw a box on the map, see which orthophoto or elevation tiles cover it, select the ones you want and
download them. The tiles are large (an orthophoto tile is roughly 640 MB), so the plugin can also download
**only the clip you selected** and mosaic it into a single file.

Covers Sweden only: it queries Lantmäteriet's Swedish STAC services. Searching is open; downloading requires a
Geotorget account (or access keys) that has ordered the products on Lantmäteriet's Geotorget (see
[Permissions](#permissions)).

| Data | Service |
|---|---|
| Orthophoto | `https://api.lantmateriet.se/stac-bild/v1` |
| Elevation data (digital terrain model) | `https://api.lantmateriet.se/stac-hojd/v1` |
| Vector data (zipped GeoPackages per municipality or for all of Sweden) | `https://api.lantmateriet.se/stac-vektor/v1` |

Point clouds and NGP catalogues are not included. For NGP, see
[ngp-downloader](https://github.com/matself/ngp-downloader).

## Install

Download the zip from [Releases](https://github.com/matself/LM-STAC-Downloader/releases) and
use *Plugins → Manage and Install Plugins → Install from ZIP*.

Requires **QGIS 3.44 or later** (the OAuth2 Client Credentials flow).

## Getting started

1. Make sure your Geotorget account (for organisations: the system account) has ordered the download
   products you want, for example *Ortofoto Nedladdning* or *Markhöjdmodell Nedladdning*.
2. Open the panel from the plugins menu or the toolbar. Click *New Lantmäteriet login…* and enter the
   Geotorget username and password, or choose access keys (Consumer Key and Consumer Secret) from
   Lantmäteriet's API manager.
3. Pick a service, draw a box on the map, search, select tiles and download.

The user interface is in Swedish; the [User interface](#user-interface) section below explains every
dialog and label in English. For the full walkthrough (in Swedish), including how clipping works and
troubleshooting, see **[docs/anvandning.md](docs/anvandning.md)**.

## User interface

The plugin's user interface (labels, buttons and messages) is in Swedish. This section explains it in
English so the plugin can be reviewed and tested without knowing Swedish.

### Main dock panel

Opened from the web menu or the web toolbar (button *Geodata: Ortofoto & höjd (Lantmäteriet)*). It has three
groups: *Anslutning* (connection), *Sökning* (search) and, once there are hits, *Träffar* (hits) and
*Hämta* (download).

| Swedish label | English meaning | What it does |
|---|---|---|
| Anslutning | Connection | Group with the login button |
| Ny Lantmäteriet-inloggning… | New Lantmäteriet login… | Opens the login dialog (see below) |
| Sökning | Search | Group with the search controls |
| Tjänst | Service | *Ortofoto* (orthophoto), *Höjddata (markhöjdmodell)* (elevation data) or *Vektordata* (vector data) |
| Flygår | Aerial survey year | Year filter for orthophoto search (has no effect for elevation or vector data) |
| Använd kartvyn | Use map view | Uses the current map extent as the search area |
| Rita ruta | Draw box | Lets you draw a rectangle on the map as the search area |
| Inget område valt | No area selected | Shown until a search area has been set |
| Sök | Search | Runs the STAC search for the selected area and service |
| Rensa sökområde och träffar | Clear search area and hits | Removes the search box and the blue/orange result boxes from the map |
| Träffar | Hits | Group listing the search results as a tree (collection, type, year, name) |
| Välj rutor i kartan | Pick tiles on the map | Toggle: click a tile on the map to select or deselect it |
| Markera alla | Select all | Selects every hit |
| Avmarkera alla | Deselect all | Deselects every hit |
| Hämta | Download | Group with the download controls |
| Hämta bara det valda området (utsnitt) | Download only the selected area (clip) | If checked, only the drawn area is downloaded and mosaicked instead of the full tiles (rasters only; hidden for vector data) |
| Lägg till i projektet när klart | Add to project when done | Adds the downloaded rasters, or the layers of the downloaded GeoPackages, to the QGIS project once finished |
| Hämta valda | Download selected | Starts downloading the selected hits |
| Avbryt | Cancel | Cancels an ongoing download |
| Fristående plugin, inte utvecklat av Lantmäteriet. | Independent plugin, not developed by Lantmäteriet. | Disclaimer label shown in the panel |

### Login dialog ("Ny inloggning för Lantmäteriet" / New Lantmäteriet login)

Opened by *Ny Lantmäteriet-inloggning…*. Creates an authentication configuration in QGIS' own
authentication manager, either Basic (Geotorget username and password) or OAuth2 (client credentials);
the password or secret is stored encrypted by QGIS, not by the plugin.

| Swedish label | English meaning | What it does |
|---|---|---|
| Typ | Type | *Geotorget-konto (användarnamn och lösenord)* (Geotorget account, username and password) or *API-nycklar (Consumer Key och Consumer Secret)* (access keys) |
| Namn | Name | Name of the QGIS authentication configuration (defaults to "Lantmäteriet Geotorget" or "Lantmäteriet STAC") |
| Användarnamn | Username | The Geotorget username (for organisations: the system account) |
| Lösenord | Password | The Geotorget password |
| Consumer Key | Consumer Key | The OAuth2 client id from Lantmäteriet's API manager |
| Consumer Secret | Consumer Secret | The OAuth2 client secret from Lantmäteriet's API manager |

### Messages

| Swedish message | English meaning | When it appears |
|---|---|---|
| Inget område valt | No area selected | No search area has been set yet |
| Ange både användarnamn och lösenord. / Ange både Consumer Key och Consumer Secret. | Enter both username and password. / Enter both Consumer Key and Consumer Secret. | One of the two login fields is empty |
| Utsnitt {n} av {N}: {namn} ({procent} %) | Clip {n} of {N}: {name} ({percent}%) | Progress while clipping/downloading |
| Avbryter… | Cancelling… | Shown while a download is being cancelled |
| åtkomst nekad. Inloggningen godtogs, men kontot får inte hämta de här filerna. … | Access denied. The login was accepted, but the account may not download these files. Check on Geotorget that the account (for organisations the system account) has ordered the download product, for example *Ortofoto Nedladdning* or *Markhöjdmodell Nedladdning*, and accepted the terms of use. With access keys, the application must also subscribe to the STAC service. | The download host returns HTTP 403 (Forbidden) |
| inloggningen godtogs inte (HTTP 401). … | The login was not accepted (HTTP 401). Check the Geotorget username and password, or the Consumer Key and Consumer Secret. | The download host returns HTTP 401 (Unauthorized) |

## Permissions

The STAC catalogues are open, so searching needs no login. The files are served from
`dl1.lantmateriet.se`, which takes either Basic authentication with a Geotorget account or an OAuth2 token
from access keys. Either way the account (for organisations: the system account) must have ordered the
download product on Geotorget, for example *Ortofoto Nedladdning* or *Markhöjdmodell Nedladdning*
(production), or the vector product in question. Keys for Nationella geodataplattformen (NGP consumer) do
not have that permission in production. The plugin does not store any credentials itself; it uses QGIS'
authentication manager.

## Limitations

* Search is limited to 1000 hits.
* The clip follows the area you searched on, not the map view at download time.
* Vector data is downloaded as whole zip files and unpacked into a folder next to the zip; it cannot be
  clipped. Datasets for all of Sweden (for example place names) match any search area.
* Elevation search returns both `mhm-*` (2.5 km tiles, roughly 8 MB) and `dtm-cog` (10 km tiles, roughly
  290 MB).
* The plugin is tested against QGIS 3.44 (Qt5). QGIS 4 / Qt6 has not been tested.

## Development

The code lives in `lm_stac_downloader/`. Hook it into a QGIS profile by linking or copying the folder into
the profile's `python/plugins`.

New version:

1. Bump `version` in `lm_stac_downloader/metadata.txt` and commit.
2. `python build.py` creates `dist/lm_stac_downloader.<version>.zip` and updates `plugins.xml`.
3. Commit `plugins.xml`, push and create the release:
   ```
   gh release create v<version> dist/lm_stac_downloader.<version>.zip --title "v<version>"
   ```

For an internal source, for example a network drive: `python build.py --base-url file:///S:/qgis-plugins`
and copy the zip file and `plugins.xml` there.

## License

GPL-2.0-or-later, see [LICENSE](LICENSE).
