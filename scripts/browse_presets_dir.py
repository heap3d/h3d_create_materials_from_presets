#!/usr/bin/python
# ================================
# (C)2023 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# browse directory and store it to user value
# ================================

from h3d_utilites.scripts.h3d_utils import get_directory, get_user_value, set_user_value
import h3d_create_materials_from_presets.scripts.h3d_kit_constants as h3dc


def browse_preset_dir() -> None:
    path = get_user_value(h3dc.USER_VAL_PRESETS_DIR_NAME)
    dialog_result = get_directory(title="Select Presets directory", path=path)
    if dialog_result:
        set_user_value(h3dc.USER_VAL_PRESETS_DIR_NAME, dialog_result)


def main():
    browse_preset_dir()


if __name__ == "__main__":
    main()
