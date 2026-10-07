"""Sequential file downloads with QgsFileDownloader.

QgsFileDownloader streams to disk, which matters here: one orthophoto file is
hundreds of MB. It runs on the main thread's event loop, so the UI stays
responsive and progress arrives as signals. Files are written to `<name>.part`
and renamed on success, so a cancelled download never looks complete.

Vector data comes as zipped GeoPackages; those are unpacked next to the zip.
"""

from __future__ import annotations

import os
import shutil
import zipfile
from pathlib import Path

from qgis.core import QgsFileDownloader
from qgis.PyQt.QtCore import QObject, QUrl, pyqtSignal

from .items import StacItem


def target_path(output_dir: Path, item: StacItem) -> Path:
    return output_dir / item.collection / item.filename


def unpack(zip_path: Path, fresh: bool) -> list[str]:
    """Unpack `zip_path` into a folder of the same name; return its GeoPackages.

    An existing folder is kept unless `fresh` (the zip was just downloaded).
    Returns the zip itself if it holds no GeoPackage.
    """
    folder = zip_path.with_suffix("")
    if fresh or not folder.exists():
        part = folder.with_name(folder.name + ".part")
        shutil.rmtree(part, ignore_errors=True)
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(part)  # strips absolute paths and ".." from member names
        shutil.rmtree(folder, ignore_errors=True)
        os.replace(part, folder)
    return sorted(str(p) for p in folder.rglob("*.gpkg")) or [str(zip_path)]


class DownloadQueue(QObject):
    # file index (1-based), file count, current file name, bytes received, bytes total
    progress = pyqtSignal(int, int, str, "qlonglong", "qlonglong")
    # downloaded (or already present) paths, failure messages, cancelled
    finished = pyqtSignal(list, list, bool)

    def __init__(self, items: list[StacItem], authcfg: str, output_dir: Path, parent=None):
        super().__init__(parent)
        self.items = items
        self.authcfg = authcfg
        self.output_dir = output_dir
        self.paths: list[str] = []
        self.failures: list[str] = []
        self._index = -1
        self._downloader: QgsFileDownloader | None = None
        self._cancelled = False

    def start(self) -> None:
        self._next()

    def cancel(self) -> None:
        self._cancelled = True
        if self._downloader:
            self._downloader.cancelDownload()
        else:
            self._done()

    def _next(self) -> None:
        self._downloader = None
        self._index += 1
        if self._cancelled or self._index >= len(self.items):
            self._done()
            return

        item = self.items[self._index]
        final = target_path(self.output_dir, item)
        if final.exists() and (item.size is None or final.stat().st_size == item.size):
            self._add_result(item, final, fresh=False)
            self.progress.emit(self._index + 1, len(self.items), item.filename, 1, 1)
            self._next()
            return

        final.parent.mkdir(parents=True, exist_ok=True)
        part = final.with_name(final.name + ".part")
        downloader = QgsFileDownloader(QUrl(item.href), str(part), self.authcfg, True)
        self._downloader = downloader
        downloader.downloadProgress.connect(
            lambda received, total, item=item: self.progress.emit(
                self._index + 1, len(self.items), item.filename, received, total
            )
        )
        downloader.downloadCompleted.connect(
            lambda _url, item=item, part=part, final=final: self._completed(item, part, final)
        )
        downloader.downloadError.connect(lambda errors, item=item: self._error(item, errors))
        downloader.downloadCanceled.connect(lambda part=part: self._discard(part))
        downloader.downloadExited.connect(self._exited)
        downloader.startDownload()

    def _completed(self, item: StacItem, part: Path, final: Path) -> None:
        os.replace(part, final)
        self._add_result(item, final, fresh=True)

    def _add_result(self, item: StacItem, path: Path, fresh: bool) -> None:
        if item.is_raster:
            self.paths.append(str(path))
            return
        try:
            self.paths.extend(unpack(path, fresh))
        except (OSError, zipfile.BadZipFile) as e:
            self.failures.append(f"{item.filename}: kunde inte packas upp: {e}")

    def _error(self, item: StacItem, errors: list) -> None:
        message = "; ".join(str(e) for e in errors)
        if "Forbidden" in message:
            # The login was accepted, but the download host also checks the
            # entitlement, which is ordered on Geotorget per (system) account.
            message = (
                "åtkomst nekad. Inloggningen godtogs, men kontot får inte hämta de här "
                "filerna. Kontrollera på Geotorget att kontot (för organisationer "
                "systemkontot) har beställt nedladdningstjänsten för produkten, till "
                "exempel Ortofoto Nedladdning eller Markhöjdmodell Nedladdning, och "
                "godkänt användningsvillkoren. Med API-nycklar ska applikationen "
                "dessutom prenumerera på STAC-tjänsten."
            )
        elif "authentication" in message.lower() or "Unauthorized" in message:
            message = (
                "inloggningen godtogs inte (HTTP 401). Kontrollera användarnamn och "
                "lösenord för Geotorget, eller Consumer Key och Consumer Secret."
            )
        self.failures.append(f"{item.filename}: {message}")

    @staticmethod
    def _discard(part: Path) -> None:
        part.unlink(missing_ok=True)

    def _exited(self) -> None:
        # Always emitted last, whatever the outcome; move on to the next file.
        if self._downloader is not None:
            self._downloader.deleteLater()
        self._next()

    def _done(self) -> None:
        self.finished.emit(self.paths, self.failures, self._cancelled)
