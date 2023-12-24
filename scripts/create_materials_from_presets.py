#!/usr/bin/python
# ================================
# (C)2023 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# create materials from presets folder
# Usage:
# 1. Choose presets directory
# 2. Run Create Materials command
# ================================

from h3d_utilites.scripts.h3d_utils import get_user_value
import h3d_create_materials_from_presets.scripts.h3d_kit_constants as h3dc


def get_files(path: str, recursive: bool = False):
    pass


def create_material_mask(name: str):
    pass


def do_preset(filename):
    pass


def parent_materials(materials, material_mask):
    pass


def main():
    path = get_user_value(h3dc.USER_VAL_PRESETS_DIR_NAME)
    include_subdirs = get_user_value(h3dc.USER_VAL_PRESETS_DIR_INCLUDE_SUBDIRS)
    preset_files = get_files(path=path, recursive=include_subdirs)

    for preset_filename in preset_files:
        target_mask = create_material_mask(name=preset_filename)
        loaded_materials = do_preset(filename=preset_filename)
        parent_materials(materials=loaded_materials, material_mask=target_mask)


if __name__ == "__main__":
    main()
