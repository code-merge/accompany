from app.core.config.config import settings
from app.core.i18n.locale import compile_translations

def compile_all_translations():
    """
    Compiles translation files for all enabled modules and their submodules.

    Iterates through each module listed in `settings.ENABLED_MODULES`. For normal modules,
    it compiles translations from <module>/i18n. For the special 'base' module, it also
    iterates through each submodule directory and compiles translations from
    <base>/<sub>/i18n if present.
    """
    for module in settings.ENABLED_MODULES:
        mod_root = settings.MODULES_DIR / module

        # Case 1: flat module (onboarding, accounting, etc.)
        i18n_path = mod_root / "i18n"
        if i18n_path.exists():
            compile_translations(i18n_path)

        # Case 2: base module with nested submodules
        if module == "base":
            for sub in mod_root.iterdir():
                if sub.is_dir():
                    sub_i18n = sub / "i18n"
                    if sub_i18n.exists():
                        compile_translations(sub_i18n)
