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

import glob
import os
from pathlib import Path
import random

import lx

from h3d_utilites.scripts.h3d_utils import get_user_value
import h3d_create_materials_from_presets.scripts.h3d_kit_constants as h3dc


class RandomColors:
    def __init__(self, num_of_colors: int) -> None:
        self.number_of_colors: int = num_of_colors
        self.colors: list[str] = self.init_colors(self.number_of_colors)

    def init_colors(self, number_of_colors: int) -> [str]:
        self.colors = [" ".join([f"{random.random():.2f}" for j in range(3)])
                       for i in range(number_of_colors)]

    def get_random_color_str(self) -> str:
        if not self.colors:
            self.init_colors(self.number_of_colors)
            print("Random Colors has been reset")

        color_str = random.choice(self.colors)
        self.colors.remove(color_str)

        return color_str


def get_files(path: str, pattern="/*.*", recursive: bool = False) -> list[str]:
    if not path:
        return []

    search_str = path + pattern
    files = glob.glob(pathname=search_str, recursive=recursive)

    return map(os.path.basename, files)


def create_material_mask(filename: str, color_str: str) -> None:
    basename = Path(filename).stem
    lx.eval(f"poly.setMaterial {{{basename}}} {{{color_str}}} 0.8 0.04 true false")


def do_preset(filename: str) -> list:
    pass


def parent_materials(materials, material_mask):
    pass


def main():
    # create and select plate for material assignment
    lx.eval('script.run "macro.scriptservice:32235733444:macro"')

    path = get_user_value(h3dc.USER_VAL_PRESETS_DIR_NAME)
    include_subdirs = get_user_value(h3dc.USER_VAL_PRESETS_DIR_INCLUDE_SUBDIRS)
    search_pattern = get_user_value(h3dc.USER_VAL_PRESETS_DIR_SEARCH_PATTERN)

    preset_files = list(get_files(path=path, pattern=search_pattern, recursive=include_subdirs))
    random_colors = RandomColors(num_of_colors=len(preset_files))

    for preset_filename in reversed(preset_files):
        color_str = random_colors.get_random_color_str()
        target_mask = create_material_mask(filename=preset_filename, color_str=color_str)
        loaded_materials = do_preset(filename=preset_filename)
        parent_materials(materials=loaded_materials, material_mask=target_mask)


if __name__ == "__main__":
    main()
