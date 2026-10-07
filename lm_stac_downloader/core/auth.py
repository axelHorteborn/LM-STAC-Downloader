"""Helpers around QGIS' built-in authentication manager.

The plugin never stores credentials itself. It only keeps the id of a QGIS
authentication configuration (authcfg); secrets live in QGIS' encrypted
auth database. Two kinds are supported: Basic (Geotorget username and
password) and OAuth2 client credentials, whose tokens QGIS fetches/refreshes.
"""

from __future__ import annotations

import json

from qgis.core import QgsApplication, QgsAuthMethodConfig

from ..config import TOKEN_URL

# Values from QgsAuthOAuth2Config (not exposed to Python).
_GRANT_FLOW_CLIENT_CREDENTIALS = 4
_CONFIG_TYPE_CUSTOM = 1
_ACCESS_METHOD_HEADER = 0


def create_basic_config(name: str, username: str, password: str) -> str:
    """Create a Basic auth config with a Geotorget username and password.

    The download host (dl1.lantmateriet.se) takes Basic auth with the Geotorget
    account (for organisations: the system account that ordered the products)
    as well as OAuth2 tokens. Returns the new authcfg id.
    """
    config = QgsAuthMethodConfig("Basic")
    config.setName(name)
    config.setConfig("username", username)
    config.setConfig("password", password)
    config.setConfig("realm", "")
    return _store(config)


def create_client_credentials_config(name: str, client_id: str, client_secret: str) -> str:
    """Create an OAuth2 (client credentials) auth config for Lantmäteriet.

    Returns the new authcfg id. Raises RuntimeError if the config could not
    be stored (e.g. the user cancelled the master password prompt).
    """
    oauth2 = {
        "version": 1,
        "configType": _CONFIG_TYPE_CUSTOM,
        "grantFlow": _GRANT_FLOW_CLIENT_CREDENTIALS,
        "name": name,
        "tokenUrl": TOKEN_URL,
        "clientId": client_id,
        "clientSecret": client_secret,
        "accessMethod": _ACCESS_METHOD_HEADER,
        "persistToken": False,
        "requestTimeout": 30,
    }

    config = QgsAuthMethodConfig("OAuth2")
    config.setName(name)
    config.setConfig("oauth2config", json.dumps(oauth2))
    return _store(config)


def _store(config: QgsAuthMethodConfig) -> str:
    """Store `config` in QGIS' auth database and return its id.

    Raises RuntimeError if the config could not be stored (e.g. the user
    cancelled the master password prompt).
    """
    auth_manager = QgsApplication.authManager()
    if not auth_manager.setMasterPassword(True):
        raise RuntimeError("QGIS huvudlösenord krävs för att spara autentiseringen.")

    result = auth_manager.storeAuthenticationConfig(config)
    # SIP_INOUT: some QGIS versions return (bool, config), others just bool.
    if isinstance(result, tuple):
        ok, config = result
    else:
        ok = result
    if not ok or not config.id():
        raise RuntimeError("Kunde inte spara autentiseringskonfigurationen.")
    return config.id()


def authcfg_exists(authcfg: str) -> bool:
    return bool(authcfg) and authcfg in QgsApplication.authManager().configIds()
