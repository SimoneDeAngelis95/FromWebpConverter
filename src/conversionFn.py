from PIL import Image, ImageSequence
import os


def convertFile(image_path, pathToSave):
    """Convert a .webp image to GIF (if animated), PNG (if has alpha), or JPG otherwise."""
    img = Image.open(image_path, formats=["WEBP"])
    base_name = os.path.join(pathToSave, extractFileName(image_path))

    try:
        if isGif(img):
            name = getAvailableFilePath(base_name, ".gif")
            _save_as_gif(img, name)
        elif hasAlphaChannel(img):
            name = getAvailableFilePath(base_name, ".png")
            img.save(name, format='PNG', lossless=True)
        else:
            name = getAvailableFilePath(base_name, ".jpg")
            img.save(name, format='JPEG', quality=95)
    finally:
        img.close()


def _save_as_gif(img, out_path):
    """Save an animated image as GIF with frame durations preserved when possible."""
    frames = []
    durations = []
    loop = img.info.get('loop', 1)

    try:
        for frame in ImageSequence.Iterator(img):
            rgba = frame.convert('RGBA')
            # GIF supports binary transparency only. Reserve index 255 so
            # transparent pixels never replace a visible palette colour.
            pal = rgba.convert('RGB').quantize(colors=255)
            palette = pal.getpalette()
            pal.putpalette(palette[:765] + [0] * (768 - len(palette[:765])))
            mask = rgba.getchannel('A').point(lambda alpha: 255 if alpha < 128 else 0)
            pal.paste(255, mask=mask)
            pal.info.clear()  # Do not inherit WebP loop/background metadata.
            frames.append(pal)
            durations.append(frame.info.get('duration', img.info.get('duration', 100)))

        # WebP counts total plays; GIF counts repeats after the first play.
        options = {} if loop == 1 else {'loop': 0 if loop == 0 else loop - 1}
        frames[0].save(
            out_path,
            save_all=True,
            append_images=frames[1:],
            format='GIF',
            duration=durations,
            disposal=2,
            transparency=255,
            background=255,
            optimize=False,
            **options,
        )
    finally:
        for frame in frames:
            frame.close()


def isGif(img):
    try:
        return getattr(img, 'is_animated', False) or getattr(img, 'n_frames', 1) > 1
    except Exception:
        return False


def extractFileName(filePath):
    base = os.path.basename(filePath)
    name, _ = os.path.splitext(base)
    return name


def getAvailableFilePath(basePath, extension):
    file_path = basePath + extension
    if not os.path.exists(file_path):
        return file_path

    counter = 1
    while True:
        file_path = f"{basePath}({counter}){extension}"
        if not os.path.exists(file_path):
            return file_path
        counter += 1


def hasAlphaChannel(img):
    """Return True if image has an alpha channel or transparency info."""
    try:
        if img.info.get("transparency", None) is not None:
            return True
        return img.mode in ("LA", "RGBA")
    except Exception:
        return False
