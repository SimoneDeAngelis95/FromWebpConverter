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


@pytest.mark.parametrize('loop,expected', [(0, 0), (1, None), (2, 1), (4, 3)])
def test_animation_preserves_total_play_count(tmp_path, loop, expected):
    source = tmp_path / 'loop.webp'
    frames = [Image.new('RGB', (8, 8), c) for c in ('red', 'blue')]
    frames[0].save(source, save_all=True, append_images=frames[1:], duration=100, loop=loop, lossless=True)
    convertFile(source, tmp_path)
    with Image.open(tmp_path / 'loop.gif') as output:
        assert output.n_frames == 2
        assert output.info.get('loop') == expected


def test_animation_transparency_and_disposal(tmp_path):
    source = tmp_path / 'transparent.webp'
    frames = []
    for x, color in [(0, (255, 0, 0, 255)), (4, (0, 0, 255, 255))]:
        frame = Image.new('RGBA', (8, 8), (255, 255, 255, 0))
        frame.paste(color, (x, 2, x + 2, 4))
        frames.append(frame)
    frames[0].save(source, save_all=True, append_images=frames[1:], duration=[100, 200], lossless=True)
    with Image.open(source) as original:
        assert original.convert('RGBA').getpixel((7, 7))[3] == 0
    convertFile(source, tmp_path)
    with Image.open(tmp_path / 'transparent.gif') as output:
        assert output.n_frames == 2
        for i in range(2):
            output.seek(i)
            rgba = output.convert('RGBA')
            assert rgba.getpixel((7, 7))[3] == 0
            assert rgba.getpixel((i * 4, 2)) == frames[i].getpixel((i * 4, 2))
            assert rgba.getpixel(((1-i) * 4, 2))[3] == 0


def test_gif_write_error_is_reported_instead_of_silent_still_fallback(tmp_path, monkeypatch):
    source = tmp_path / 'animated.webp'
    frames = [Image.new('RGB', (8, 8), c) for c in ('red', 'blue')]
    frames[0].save(source, save_all=True, append_images=frames[1:], duration=100)
    real_save = Image.Image.save
    def failing_save(self, fp, format=None, **kwargs):
        if format == 'GIF':
            raise OSError('Cannot write GIF')
        return real_save(self, fp, format=format, **kwargs)
    monkeypatch.setattr(Image.Image, 'save', failing_save)
    with pytest.raises(OSError, match='Cannot write GIF'):
        convertFile(source, tmp_path)
