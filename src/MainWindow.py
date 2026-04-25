import os
import sys
import platform

from PyQt6.QtCore import Qt, QObject, pyqtSignal, QThread
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QFileDialog,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QProgressBar,
    QStatusBar,
)
from conversionFn import convertFile
import globalVariables as GV


class DropListWidget(QListWidget):
    filesDropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if not event.mimeData().hasUrls():
            event.ignore()
            return
        paths = [u.toLocalFile() for u in event.mimeData().urls()]
        self.filesDropped.emit(paths)
        event.acceptProposedAction()


class ConverterWorker(QObject):
    progress = pyqtSignal(int, int)  # current, total
    item_status = pyqtSignal(int, str)  # index, status: 'pending'|'ok'|'error'
    finished = pyqtSignal(int, int)  # success_count, total

    def __init__(self, files, dest):
        super().__init__()
        self.files = files
        self.dest = dest

    def run(self):
        ok = 0
        total = len(self.files)
        for i, path in enumerate(self.files):
            try:
                self.progress.emit(i + 1, total)
                self.item_status.emit(i, 'pending')
                convertFile(path, self.dest)
                ok += 1
                self.item_status.emit(i, 'ok')
            except Exception:
                self.item_status.emit(i, 'error')
                # continue to next
        self.finished.emit(ok, total)

# ==============================================
#                 MAIN WINDOW
# ==============================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(GV.APP_NAME + " " + GV.APP_VERSION)
        self.setMinimumSize(650, 340)

        # Try set app icon if available (Qt uses .icns on macOS)
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icon.icns')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._files = []
        self._setup_ui()
        self._setup_connections()

        # Default destination path
        self.dest_edit.setText(GV.DEFAULT_PATH)
        self._update_controls(enable_essentials=False, enable_all=True)

    def _setup_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)

        self.select_btn = QPushButton('Select Files')
        self.list_widget = DropListWidget()

        self.dest_edit = QLineEdit()
        self.dest_edit.setReadOnly(True)
        self.dest_btn = QPushButton('Select Destination')

        self.remove_btn = QPushButton('Remove')
        self.remove_all_btn = QPushButton('Remove All')
        self.convert_btn = QPushButton('Convert')

        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 1)
        self.progress.setVisible(False)

        layout = QVBoxLayout()
        layout.addWidget(self.select_btn)
        layout.addWidget(self.list_widget)

        dest_row = QHBoxLayout()
        dest_row.addWidget(self.dest_edit, stretch=2)
        dest_row.addWidget(self.dest_btn, stretch=1)
        layout.addLayout(dest_row)

        actions_row = QHBoxLayout()
        actions_row.addWidget(self.remove_btn)
        actions_row.addWidget(self.remove_all_btn)
        actions_row.addWidget(self.convert_btn)
        layout.addLayout(actions_row)

        layout.addWidget(self.progress)

        central.setLayout(layout)

        status = QStatusBar(self)
        self.setStatusBar(status)
        self.statusBar().showMessage(GV.APP_NAME + ' ' + GV.APP_VERSION)

    def _setup_connections(self):
        self.select_btn.clicked.connect(self._select_files)
        self.remove_btn.clicked.connect(self._remove_file)
        self.remove_all_btn.clicked.connect(self._remove_all)
        self.dest_btn.clicked.connect(self._select_dest)
        self.convert_btn.clicked.connect(self._start_conversion)
        self.list_widget.filesDropped.connect(self._on_files_dropped)

    # UI actions
    def _select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, 'Choose files', GV.DEFAULT_PATH,
                                                'WebP files (*.webp);;All files (*.*)')
        if not files:
            return

        # Filter: unique + only .webp (case-insensitive)
        existing = set(self._files)
        to_add = [f for f in files if f.lower().endswith('.webp') and f not in existing]
        if not to_add:
            return
        self._files.extend(to_add)
        self._refresh_list()
        self._update_controls(enable_essentials=True)

    def _remove_file(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            self._files.pop(row)
            self.list_widget.takeItem(row)
        if not self._files:
            self._update_controls(enable_essentials=False)

    def _remove_all(self):
        if not self._files:
            return
        self._files.clear()
        self.list_widget.clear()
        self._update_controls(enable_essentials=False)

    def _select_dest(self):
        current = self.dest_edit.text() or GV.DEFAULT_PATH
        chosen = QFileDialog.getExistingDirectory(self, 'Select destination', current)
        if chosen:
            self.dest_edit.setText(chosen)

    def _start_conversion(self):
        if not self._files:
            return
        self._set_busy(True)
        self.statusBar().setStyleSheet('color: black;')
        self.statusBar().showMessage('Starting conversion...')

        self.thread = QThread(self)
        self.worker = ConverterWorker(self._files.copy(), self.dest_edit.text())
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self._on_progress)
        self.worker.item_status.connect(self._on_item_status)
        self.worker.finished.connect(self._on_finished)
        self.worker.finished.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def _on_files_dropped(self, paths: list[str]):
        # Filter dropped files: unique + .webp only
        existing = set(self._files)
        to_add = []
        for p in paths:
            if not p:
                continue
            if os.path.isdir(p):
                # Optionally, collect .webp from the folder
                for root, _, files in os.walk(p):
                    for f in files:
                        full = os.path.join(root, f)
                        if full.lower().endswith('.webp') and full not in existing:
                            to_add.append(full)
            else:
                if p.lower().endswith('.webp') and p not in existing:
                    to_add.append(p)
        if not to_add:
            return
        self._files.extend(to_add)
        self._refresh_list()
        self._update_controls(enable_essentials=True)

    # Worker callbacks
    def _on_progress(self, current, total):
        self.statusBar().showMessage(f'Converting... {current} / {total}')

    def _on_item_status(self, index, status):
        item = self.list_widget.item(index)
        if not item:
            return
        if status == 'pending':
            color = QColor('orange')
        elif status == 'ok':
            color = QColor('green')
        else:
            color = QColor('red')
        item.setBackground(color)

    def _on_finished(self, ok, total):
        self.progress.setVisible(False)
        self._set_busy(False)
        self._files.clear()
        self._refresh_list()
        self._update_controls(enable_essentials=False)

        msg = f'Converted {ok} / {total}'
        if ok == total:
            self.statusBar().setStyleSheet('color: green;')
        else:
            self.statusBar().setStyleSheet('color: red;')
        self.statusBar().showMessage(msg)

    # Helpers
    def _refresh_list(self):
        self.list_widget.clear()
        for path in self._files:
            item = QListWidgetItem(path)
            self.list_widget.addItem(item)

    def _update_controls(self, enable_essentials: bool, enable_all: bool | None = None):
        self.remove_btn.setEnabled(enable_essentials)
        self.remove_all_btn.setEnabled(enable_essentials)
        self.convert_btn.setEnabled(enable_essentials)
        if enable_all is not None:
            self.dest_btn.setEnabled(enable_all)
            self.select_btn.setEnabled(enable_all)

    def _set_busy(self, busy: bool):
        self.convert_btn.setEnabled(False if busy else bool(self._files))
        self.remove_btn.setEnabled(not busy)
        self.remove_all_btn.setEnabled(not busy)
        self.dest_btn.setEnabled(not busy)
        self.select_btn.setEnabled(not busy)
        self.progress.setVisible(busy)
        if busy:
            # Indeterminate
            self.progress.setRange(0, 0)
        else:
            self.progress.setRange(0, 1)