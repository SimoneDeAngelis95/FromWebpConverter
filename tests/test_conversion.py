from PIL import Image
import pytest
from conversionFn import convertFile

@pytest.mark.parametrize('mode,extension', [('RGB', '.jpg'), ('RGBA', '.png')])
def test_still_conversion_and_duplicates(tmp_path, mode, extension):
    source = tmp_path / 'source.webp'
    Image.new(mode, (12, 8), (255, 0, 0, 128) if mode == 'RGBA' else 'red').save(source)
    convertFile(source, tmp_path)
    convertFile(source, tmp_path)
    for name in ['source' + extension, 'source(1)' + extension]:
        with Image.open(tmp_path / name) as output:
            assert output.size == (12, 8)
            assert output.format == {'.jpg': 'JPEG', '.png': 'PNG'}[extension]


def test_animation_preserves_frames_and_duration(tmp_path):
    source = tmp_path / 'animated.webp'
    frames = [Image.new('RGB', (12, 8), color) for color in ('red', 'blue')]
    frames[0].save(source, save_all=True, append_images=frames[1:], duration=[100, 200], lossless=True)
    convertFile(source, tmp_path)
    with Image.open(tmp_path / 'animated.gif') as output:
        assert output.n_frames == 2
        assert output.info['duration'] == 100
        output.seek(1)
        assert output.info['duration'] == 200


def test_rejects_other_formats_disguised_as_webp(tmp_path):
    source = tmp_path / 'fake.webp'
    Image.new('RGB', (8, 8)).save(source, format='PNG')
    with pytest.raises(Exception):
        convertFile(source, tmp_path)
    assert not (tmp_path / 'fake.jpg').exists()
