# Updates and release validation

## Dependencies and security

Use Python 3.11 or newer. Pillow 13.0.0 requires Python >=3.11. The existing
main branch had already upgraded Pillow to 12.2.0; this change moves to 13.0.0,
including the FlashPix heap buffer overflow fix (GHSA-5x8w-8jj5-q52h).
The converter now explicitly accepts only WEBP decoders, so changing a filename
to `.webp` cannot enable another Pillow format parser. The GIF palette uses the
supported `Image.Palette.ADAPTIVE` API.

References:
- https://pillow.readthedocs.io/en/stable/releasenotes/13.0.0.html
- https://github.com/python-pillow/Pillow/security/advisories/GHSA-5x8w-8jj5-q52h

The authenticated Dependabot API was checked on 2026-10-24: 54 open alerts
(5 critical, 33 high, 16 moderate), all for Pillow in requirements.txt.
Pillow 13.0.0 is outside every reported vulnerable version range; this was
verified using packaging.specifiers against all 54 alert records. Updating this
branch does not itself close alerts on the default branch; confirm closure
after an approved merge. Weekly pip/Actions update checks
are configured in `.github/dependabot.yml`.

## Uppie integration

Uppie is pinned to upstream commit
`eb602c8f29be8e12f7b89eb3ba8ff8d09a6a3d14` instead of an ambiguous PyPI package
or a moving branch. Its only public end-to-end update method checks, downloads
and installs together. `src/updates.py` intentionally adapts its private download
and install methods to keep these actions separate. Re-run adapter contract
tests when updating that pin; a public split API in Uppie would be preferable.

Packaged apps check on startup; source runs check only via **Check for updates**.
Checks and downloads run in a background thread. A newer compatible release
prompts for download; opening the installer requires a second confirmation.
Declining leaves conversion available. Downloads use the application's cache
directory. Errors leave the app usable. Closing waits for active operations to
finish (network requests have Uppie's timeout/retry limits).

Uppie considers only GitHub's latest published release. Windows selection accepts
any `.exe`, so **publish exactly one Windows x64 Setup.exe asset**; do not upload
a portable `.exe` alongside it. macOS uses `.dmg` with architecture hints or a
universal DMG. Linux automatic installation is not enabled. Existing releases
V1.0.1/V1.0.2 contain macOS DMGs only; there is no Windows update until a suitable
asset is explicitly published. Version 1.0.3 is the next development version;
this PR does not publish it.

## Windows packaging

The CI workflow uses Python 3.13 x64, PyInstaller onedir and Inno Setup 6. The
installer installs per-user in LocalAppData, includes uninstallation and keeps
a stable AppId for upgrades. `APP_VERSION` in `src/globalVariables.py` supplies
the installer version and the macOS bundle version.

The workflow runs tests on Linux, Windows and macOS with Python 3.11 and 3.13,
then builds, silently installs, launches for eight seconds and uninstalls the
Windows application before uploading the installer artifact. This smoke test
detects packaging/startup failures; it does not prove upgrade or interactive
conversion behavior. It never creates a GitHub release.
Download the artifact from the PR Actions run to test installation. It is
unsigned; code signing requires a separate certificate/release decision.

Before approving a release:
1. Install the generated Setup.exe on Windows x64 and launch from Start Menu.
2. Convert an opaque WebP, a transparent WebP and an animated WebP; verify output.
3. Install a newer build over it; verify the application path and uninstaller.
4. Verify declining updates, offline checks, download failure, progress, installer
   confirmation and closing the app during an operation. Network paths are
   tested with mocked responses locally; real update installation needs a newer
   published test release in a separate test repository.
5. Confirm the icon and version in Explorer, the taskbar and the app window.
6. After explicit release approval, attach the single Setup.exe to the intended
   stable GitHub release (with DMG if available). Do not expose portable EXEs.

macOS packaging remains available with `python setup_macos.py py2app` after
installing requirements and py2app. Build Intel/Apple Silicon packages on the
corresponding architecture or validate a genuinely universal bundle before
naming a DMG universal. This change does not claim a tested universal build.

## Icon

The existing FWC monogram was recolored to neon blue with imagegen after user
review and approval. `assets/icon.png` is the source; ICO and ICNS are generated
from that same approved image. The original FWC composition remains recognizable.
Generation instruction: preserve the original FWC letters, frame, dark backdrop,
texture and shadows; change red elements to electric neon blue with restrained
cyan highlights. The earlier red conversion-arrow proposal was rejected.
