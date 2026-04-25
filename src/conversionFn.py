from PIL import Image, ImageSequence
import os


def convertFile(image_path, pathToSave):
    """Convert a .webp image to GIF (if animated), PNG (if has alpha), or JPG otherwise."""
    img = Image.open(image_path)
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

    try:
        for frame in ImageSequence.Iterator(img):
            rgba = frame.convert('RGBA')
            pal = rgba.convert('P', palette=Image.ADAPTIVE, colors=255)
            frames.append(pal)
            durations.append(frame.info.get('duration', img.info.get('duration', 100)))

        base = frames[0]
        append = frames[1:] if len(frames) > 1 else []
        base.save(
            out_path,
            save_all=True,
            append_images=append,
            format='GIF',
            loop=0,
            duration=durations if durations else 100,
            disposal=2,
        )
    except Exception:
        # Fallback: save first frame only
        img.convert('RGB').save(out_path, format='GIF')


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
