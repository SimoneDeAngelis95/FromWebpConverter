import time
import pytest
from PIL import Image
from PyQt6.QtWidgets import QApplication
from MainWindow import MainWindow


@pytest.fixture(scope='module')
def app():
    return QApplication.instance() or QApplication([])


def test_overlapping_folder_file_and_repeated_paths_are_unique(app, tmp_path):
    source = tmp_path / 'image.webp'
    Image.new('RGB', (8, 8)).save(source)
    window = MainWindow()
    try:
        window._on_files_dropped([str(tmp_path), str(source), str(source)])
        assert window._files == [str(source)]
        window._on_files_dropped([str(source)])
        assert window._files == [str(source)]
    finally:
        window.close()


def test_drop_during_conversion_cannot_change_queue_or_start_second_worker(app, tmp_path, monkeypatch):
    import MainWindow as module
    source = tmp_path / 'source.webp'
    extra = tmp_path / 'extra.webp'
    for path in (source, extra):
        Image.new('RGB', (8, 8), 'red').save(path)
    real_convert = module.convertFile
    def slow_convert(*args):
        time.sleep(0.1)
        real_convert(*args)
    monkeypatch.setattr(module, 'convertFile', slow_convert)
    window = MainWindow()
    window.dest_edit.setText(str(tmp_path))
    window._on_files_dropped([str(source)])
    window._start_conversion()
    original_thread = window.conversion_thread
    try:
        window._on_files_dropped([str(extra)])
        assert window._files == [str(source)]
        assert not window.list_widget.acceptDrops()
        assert not window.convert_btn.isEnabled()
        assert not window.remove_btn.isEnabled()
        window._start_conversion()
        assert window.conversion_thread is original_thread
    finally:
        deadline = time.monotonic() + 5
        while window.conversion_thread is not None and time.monotonic() < deadline:
            app.processEvents()
            time.sleep(.005)
        assert window.conversion_thread is None
        window.close()
    assert (tmp_path / 'source.jpg').exists()
    assert not (tmp_path / 'extra.jpg').exists()
    assert window.list_widget.acceptDrops()
