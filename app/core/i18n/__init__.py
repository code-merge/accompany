from app.core.config.config import settings
from app.core.i18n.locale import compile_translations

def compile_all_translations():
    """
    Compiles translation files for all enabled modules.

    Iterates through each module listed in `settings.ENABLED_MODULES`, constructs the path to its `i18n` directory,
    and if the directory exists, compiles the translation files within it using `compile_translations`.

    Assumes the existence of `settings.ENABLED_MODULES`, `settings.MODULES_DIR`, and a `compile_translations` function.
    """
    for module in settings.ENABLED_MODULES:
        i18n_path = settings.MODULES_DIR / module / "i18n"
        if i18n_path.exists():
            print(i18n_path)
            compile_translations(i18n_path)
