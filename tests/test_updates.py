from unittest.mock import Mock
import pytest
from PyQt6.QtWidgets import QApplication
from uppie import Uppie
from updates import UpdateService, UpdateTask

@pytest.fixture(scope='module')
def app():
    return QApplication.instance() or QApplication([])


def test_real_uppie_selects_windows_installer(monkeypatch):
    client = Uppie('owner', 'repo', '1.0.2')
    monkeypatch.setattr('uppie.uppie.platform.system', lambda: 'Windows')
    payload = {'tag_name': 'V1.0.3', 'assets': [
        {'name': 'mac.dmg', 'browser_download_url': 'https://example.com/mac.dmg'},
        {'name': 'Setup.exe', 'browser_download_url': 'https://example.com/Setup.exe'}]}
    response = Mock()
    response.json.return_value = payload
    client._session.get = Mock(return_value=response)
    assert client.is_update_available()
    assert client.asset_link.endswith('Setup.exe')
    client.local_version = '1.0.3'
    assert not client.is_update_available()
    assert client.asset_link is None


def test_no_installer_and_offline(monkeypatch):
    monkeypatch.setattr('updates.platform.system', lambda: 'Windows')
    service = UpdateService()
    service.client = Mock(latest_release=None)
    service.client.is_update_available.return_value = False
    with pytest.raises(RuntimeError, match='contact GitHub'):
        service.check()
    def incompatible():
        service.client.latest_release = {'tag_name': 'V1.0.3', 'assets': []}
        return False
    service.client.is_update_available.side_effect = incompatible
    assert service.check() is False


def test_download_does_not_install_and_errors_propagate():
    service = UpdateService()
    service.client = Mock()
    service.client._download_release.return_value = '/tmp/Setup.exe'
    assert service.download() == '/tmp/Setup.exe'
    service.client._install_release.assert_not_called()
    assert service.install()
    service.client._install_release.assert_called_once_with('/tmp/Setup.exe')
    service.client._download_release.return_value = None
    with pytest.raises(RuntimeError, match='Download failed'):
        service.download()
    with pytest.raises(RuntimeError, match='open the installer'):
        service.install()


def test_worker_emits_error_without_crashing(app):
    service = Mock()
    service.check.side_effect = RuntimeError('offline')
    task = UpdateTask(service, 'check')
    errors = []
    task.failed.connect(errors.append)
    task.run()
    assert errors == ['offline']


def test_window_smoke_and_update_later(app, monkeypatch):
    from MainWindow import MainWindow, QMessageBox
    window = MainWindow()
    window.show()
    app.processEvents()
    window.update_service.client.latest_release = {'tag_name': 'V1.0.3'}
    task = Mock()
    window.update_task = task
    window._update_result = ('check', True)
    monkeypatch.setattr(QMessageBox, 'question', lambda *args: QMessageBox.StandardButton.No)
    window._update_done()
    assert window.update_task is None
    assert window.update_btn.isEnabled()
    window.close()


def test_real_download_stream_and_partial_cleanup(tmp_path):
    client = Uppie('owner', 'repo', '1.0.3', str(tmp_path))
    client.asset_link = 'https://example.com/Setup.exe'
    response = Mock()
    response.headers = {'content-length': '6'}
    response.iter_content.return_value = [b'abc', b'def']
    context = Mock()
    context.__enter__ = Mock(return_value=response)
    context.__exit__ = Mock(return_value=False)
    client._session.get = Mock(return_value=context)
    assert client._download_release() == str(tmp_path / 'Setup.exe')
    assert (tmp_path / 'Setup.exe').read_bytes() == b'abcdef'
    assert client.get_progress_percentage() == 100
    client.asset_link = 'https://example.com/failed.exe'
    def broken(**kwargs):
        yield b'abc'
        raise OSError('interrupted')
    response.iter_content.side_effect = broken
    assert client._download_release() is None
    assert not (tmp_path / 'failed.exe.part').exists()


def test_background_check_finishes_and_window_blocks_close(app):
    import time
    from MainWindow import MainWindow
    window = MainWindow()
    window.show()
    window.update_service.check = lambda: (time.sleep(0.05) or False)
    window._run_update('check')
    assert not window.close()
    deadline = time.monotonic() + 3
    while window.update_task is not None and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.005)
    assert window.update_task is None
    assert window.update_btn.isEnabled()
    assert 'No newer' in window.statusBar().currentMessage()
    assert window.close()
