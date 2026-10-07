"""Dialog that creates a QGIS auth config preset for Lantmäteriet."""

from __future__ import annotations

from qgis.PyQt.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from ..core.auth import create_basic_config, create_client_credentials_config

BASIC, CLIENT_CREDENTIALS = "basic", "client_credentials"

# kind: (default name, user label, secret label, info text)
_KINDS = {
    BASIC: (
        "Lantmäteriet Geotorget",
        "Användarnamn",
        "Lösenord",
        "Skapar en inloggning med användarnamn och lösenord för Geotorget (Basic) i QGIS "
        "autentiseringshanterare. För organisationer är det systemkontot som har beställt "
        "produkterna. Lösenordet sparas krypterat av QGIS, inte av pluginet.",
    ),
    CLIENT_CREDENTIALS: (
        "Lantmäteriet STAC",
        "Consumer Key",
        "Consumer Secret",
        "Skapar en OAuth2-konfiguration (client credentials) i QGIS "
        "autentiseringshanterare. Nyckel och hemlighet sparas krypterat av "
        "QGIS, inte av pluginet.",
    ),
}


class CreateAuthDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ny inloggning för Lantmäteriet")
        self.authcfg: str | None = None

        self.kind_combo = QComboBox()
        self.kind_combo.addItem("Geotorget-konto (användarnamn och lösenord)", BASIC)
        self.kind_combo.addItem("API-nycklar (Consumer Key och Consumer Secret)", CLIENT_CREDENTIALS)

        self.info = QLabel()
        self.info.setWordWrap(True)

        self.name_edit = QLineEdit()
        self.user_edit = QLineEdit()
        self.secret_edit = QLineEdit()
        self.secret_edit.setEchoMode(QLineEdit.EchoMode.Password)

        self.user_label = QLabel()
        self.secret_label = QLabel()

        form = QFormLayout()
        form.addRow("Typ", self.kind_combo)
        form.addRow("Namn", self.name_edit)
        form.addRow(self.user_label, self.user_edit)
        form.addRow(self.secret_label, self.secret_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._create)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self.info)
        layout.addLayout(form)
        layout.addWidget(buttons)

        self.kind_combo.currentIndexChanged.connect(self._on_kind_changed)
        self._on_kind_changed()

    def _on_kind_changed(self) -> None:
        default_names = {name for name, *_ in _KINDS.values()}
        name, user_label, secret_label, info = _KINDS[self.kind_combo.currentData()]
        self.info.setText(info)
        self.user_label.setText(user_label)
        self.secret_label.setText(secret_label)
        # Follow the type unless the user has typed a name of their own.
        if self.name_edit.text().strip() in default_names | {""}:
            self.name_edit.setText(name)

    def _create(self) -> None:
        kind = self.kind_combo.currentData()
        default_name, user_label, secret_label, _info = _KINDS[kind]
        user = self.user_edit.text().strip()
        secret = self.secret_edit.text() if kind == BASIC else self.secret_edit.text().strip()
        if not user or not secret:
            # "användarnamn och lösenord" in lower case, the key names as written.
            fields = f"{user_label} och {secret_label}"
            QMessageBox.warning(
                self, self.windowTitle(), f"Ange både {fields.lower() if kind == BASIC else fields}."
            )
            return
        create = create_basic_config if kind == BASIC else create_client_credentials_config
        try:
            self.authcfg = create(self.name_edit.text().strip() or default_name, user, secret)
        except RuntimeError as e:
            QMessageBox.critical(self, self.windowTitle(), str(e))
            return
        self.accept()
