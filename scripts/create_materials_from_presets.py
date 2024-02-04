#!/usr/bin/python
# ================================
# (C)2023 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# create materials from presets folder
# Usage:
# 1. Create a new empty scene
# 2. Choose presets directory
# 3. Run Create Materials command
# ================================

import os
import glob
import random
from typing import Union

import lx
import modo
import modo.constants as c

import h3d_create_materials_from_presets.scripts.h3d_kit_constants as h3dc
from h3d_utilites.scripts.h3d_utils import get_user_value
from h3d_utilites.scripts.h3d_debug import H3dDebug


class RandomColors:
    def __init__(self, num_of_colors: int) -> None:
        self.number_of_colors = num_of_colors
        self.colors = self.init_colors(self.number_of_colors)

    def init_colors(self, number_of_colors: int) -> list[str]:
        color_strings = [
            " ".join([f"{random.random():.2f}" for j in range(3)])
            for i in range(number_of_colors)
        ]

        return color_strings

    def get_random_color_str(self) -> str:
        if not self.colors:
            self.init_colors(self.number_of_colors)

        color_str = random.choice(self.colors)
        self.colors.remove(color_str)

        return color_str


def get_presets(
    root_dir: str, recursive: bool = False, ext: str = ".lxp", pattern: str = "/**"
) -> dict:
    if not root_dir:
        return dict()

    search_str = root_dir + pattern
    filenames = [
        i
        for i in glob.glob(pathname=search_str, recursive=recursive)
        if any([i.endswith(j) for j in ext.split()])
    ]

    presets: dict[str, dict[str, str]] = {}
    for filename in filenames:
        basename: str = os.path.basename(filename)[:-4]
        dirname: str = os.path.dirname(filename)
        subdirs: str = dirname[len(root_dir):]
        preset_info: dict[str, str] = {
            "basename": basename,
            "subdirs": subdirs,
            "path": filename,
        }

        presets[filename] = preset_info

    return presets


def folder_name(name: str) -> str:
    return name + " /SUBDIR/"


def is_group_exist(name: str) -> bool:
    selected: list[modo.Item] = modo.Scene().selectedByType(itype=c.MASK_TYPE)
    if selected:
        groups = selected[0].childrenByType(itype=c.MASK_TYPE)
    else:
        groups = [
            group
            for group in modo.Scene().items(itype=c.MASK_TYPE)
            if group.parent == modo.Scene().renderItem
        ]

    for group in groups:
        if name == group.name:
            return True

    return False


def parent_materials(sources: set[modo.Item], target: Union[modo.Item, None]) -> None:
    if not target:
        return
    for item in sources:
        lx.eval(f"texture.parent {target.id} 1 item:{item.id}")


def create_group(name: str) -> modo.Item:
    lx.eval("shader.create mask")
    lx.eval(f'item.name "{name}" mask')
    lx.eval("item.editorColor white")
    group: modo.Item = modo.Scene().selectedByType(itype=c.MASK_TYPE)[0]
    parent = group.parent
    if not parent:
        return group
    children_masks = parent.childrenByType(itype=c.MASK_TYPE)
    group_masks = [i for i in children_masks if i.channel("ptag").get() == ""]  # type: ignore
    is_first_subdir = bool((parent == modo.Scene().renderItem) and group_masks)
    parent_index = parent.childCount() - len(group_masks)
    if is_first_subdir:
        default_shaders = modo.Scene().renderItem.childrenByType(
            itype=c.DEFAULTSHADER_TYPE
        )
        if default_shaders:
            parent_index = default_shaders[0].parentIndex - len(group_masks)  # type: ignore
    group.setParent(parent, parent_index)

    return group


def select_group(name: str) -> modo.Item:
    group = [mask for mask in modo.Scene().items(itype=c.MASK_TYPE, name=name)][0]
    group.select(replace=True)
    return group


def set_group(subdirs_str) -> Union[modo.Item, None]:
    subdirs = [
        subdir for subdir in os.path.normpath(subdirs_str).split(os.sep) if subdir
    ]
    # using folder_name() to distinct GROUP from Material Mask by name
    latest_group = None
    for subdir in subdirs:
        if not is_group_exist(folder_name(subdir)):
            latest_group = create_group(folder_name(subdir))
        else:
            latest_group = select_group(folder_name(subdir))

    return latest_group


def create_material_mask(preset: dict[str, str], color_str: str) -> Union[modo.Item, None]:
    basename = preset["basename"]

    # set material
    modo.Scene().deselect()
    lx.eval("shader.create mask")
    lx.eval(f'mask.setPTag "{basename}"')
    masks: list[modo.Item] = modo.Scene().selectedByType(itype=c.MASK_TYPE)
    if not masks:
        return None
    new_mask: modo.Item = masks[0]

    lx.eval("shader.create advancedMaterial")
    lx.eval(f'item.name "M_{basename}" advancedMaterial')
    lx.eval(f"item.channel advancedMaterial$diffCol {{{color_str}}}")

    parent = modo.Scene().renderItem
    lx.eval(f"texture.parent {parent.id} 1 item:{new_mask.id}")

    # create folders for subdirs if option enabled
    create_subfolders = 0 != get_user_value(h3dc.USER_VAL_PRESETS_CREATE_SUBFOLDERS)
    if not create_subfolders:
        return new_mask

    subdirs_str = preset["subdirs"]
    if not subdirs_str:
        return new_mask

    modo.Scene().deselect()
    latest_mask = set_group(subdirs_str)
    # parent new_mask to latest subdir
    parent_pos = 0
    if latest_mask:
        lx.eval(f"texture.parent {latest_mask.id} {parent_pos} item:{new_mask.id}")

    return new_mask


def get_shader_tree_items() -> set[modo.Item]:
    shader_tree_items = modo.Scene().renderItem.children(recursive=True)
    return set(shader_tree_items)


def do_preset(filename: str) -> set[modo.Item]:
    before_do_items = get_shader_tree_items()

    lx.eval(
        "layout.createOrClose PresetBrowser presetBrowserPalette true \
            Presets width:800 height:600 persistent:true style:palette"
    )
    lx.eval("select.presetDrop")
    lx.eval("select.drop filepath")
    lx.eval(f'select.preset "{filename}" mode:set')
    lx.eval(f'select.filepath "{filename}" set')
    lx.eval("preset.do")

    after_do_items = get_shader_tree_items()
    new_items = after_do_items - before_do_items

    return new_items


def main():
    # create and select mesh item Plate for material assignment
    lx.eval('script.run "macro.scriptservice:32235733444:macro"')

    root_dir = get_user_value(h3dc.USER_VAL_PRESETS_DIR_NAME)
    # convert to True|False
    include_subdirs = 0 != get_user_value(h3dc.USER_VAL_PRESETS_DIR_INCLUDE_SUBDIRS)
    ext = get_user_value(h3dc.USER_VAL_PRESETS_DIR_SEARCH_EXT)

    presets = get_presets(root_dir=root_dir, recursive=include_subdirs, ext=ext)
    print(f"{len(presets)} presets found")
    random_colors = RandomColors(num_of_colors=len(presets))

    for preset in presets.values():
        color_str = random_colors.get_random_color_str()
        target_mask = create_material_mask(preset=preset, color_str=color_str)
        loaded_materials = do_preset(filename=preset["path"])
        parent_materials(sources=loaded_materials, target=target_mask)


logname = "D:\\work\\scripts\\modo\\h3d tools\\h3d_create_materials_from_presets\\create materials from presets.txt"
h3dd = H3dDebug(enable=False, fullpath=logname)

if __name__ == "__main__":
    main()
