"""Uppie adapter pinned to the audited upstream commit in requirements.txt.

Uppie currently exposes only an end-to-end update() operation. The private
methods below deliberately separate download from installation/user consent.
Upgrade the pin only after running the adapter contract tests.
"""
from pathlib import Path
import platform
from PyQt6.QtCore import QThread, pyqtSignal, QStandardPaths
from uppie import Uppie
import globalVariables as GV


class UpdateService:
    def __init__(self):
        cache = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation)
        self.client = Uppie('SimoneDeAngelis95', 'FromWebpConverter', GV.APP_VERSION,
                            download_folder=str(Path(cache) / 'updates'))
        self.downloaded = None

    def check(self):
        if platform.system() not in ('Windows', 'Darwin'):
            raise RuntimeError('Automatic updates support Windows and macOS only.')
        self.client.latest_release = None
        available = self.client.is_update_available()
        if self.client.latest_release is None:
            raise RuntimeError('Cannot contact GitHub. Please try again later.')
        return available

    def download(self):
        self.downloaded = self.client._download_release()
        if not self.downloaded:
            raise RuntimeError('Download failed. Please try checking for updates again.')
        return self.downloaded

    def install(self):
        if not self.downloaded or not self.client._install_release(self.downloaded):
            raise RuntimeError('Could not open the installer.')
        return True


class UpdateTask(QThread):
    completed = pyqtSignal(str, object)
    failed = pyqtSignal(str)

    def __init__(self, service, action, parent=None):
        super().__init__(parent)
        self.service, self.action = service, action

    def run(self):
        try:
            result = getattr(self.service, self.action)()
            self.completed.emit(self.action, result)
        except Exception as exc:
            self.failed.emit(str(exc))
