import polib
import logging
import gettext
from pathlib import Path
from typing import Callable

DOMAIN = "messages"
logger = logging.getLogger("i18n")


def compile_translations(i18n_root: Path) -> None:
    """
    Compiles all .po translation files to .mo files within the given i18n root directory.

    This function iterates over each locale directory inside the specified i18n_root,
    searches for .po files in the LC_MESSAGES subdirectory, and compiles them into
    binary .mo files using polib. If the i18n_root does not exist, a warning is logged.
    Any errors encountered during compilation are logged as errors.

    Args:
        i18n_root (Path): The root directory containing locale subdirectories with translation files.

    Returns:
        None
    """

    if not i18n_root.exists():
        logger.warning(f"[i18n] No i18n directory found at {i18n_root}")
        return

    for locale_dir in i18n_root.iterdir():
        if not locale_dir.is_dir():
            continue

        po_path = locale_dir / "LC_MESSAGES" / f"{DOMAIN}.po"
        mo_path = po_path.with_suffix(".mo")

        if not po_path.exists():
            continue

        try:
            po = polib.pofile(str(po_path))
            mo_path.parent.mkdir(parents=True, exist_ok=True)
            po.save_as_mofile(str(mo_path))
            logger.info(f"[i18n] Compiled {po_path} → {mo_path}")
        except Exception as e:
            logger.error(f"[i18n] Error compiling {po_path}: {e}")


def get_translations(i18n_root: Path, locale: str) -> Callable[[str], str]:
    """
    Retrieve a translation function for the specified locale.

    Attempts to load translation files from the given i18n_root directory for the provided locale.
    If translation files are found, returns a function that translates input strings.
    If not found or an error occurs, returns an identity function that returns the input string unchanged.

    Args:
        i18n_root (Path): The root directory containing locale translation files.
        locale (str): The locale code (e.g., 'en', 'fr', 'es') for which to retrieve translations.

    Returns:
        Callable[[str], str]: A function that takes a string and returns its translation, or the original string if no translation is available.
    """

    try:
        translation = gettext.translation(
            DOMAIN,
            localedir=i18n_root,
            languages=[locale],
            fallback=True
        )
        return translation.gettext
    except Exception as e:
        logger.warning(f"[i18n] No translation found for locale '{locale}' in {i18n_root}: {e}")
        return lambda s: s
