#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# normalize materials:
# - set mask name according to polygon tag
# - set advanced material name according to mask name
# - add images from octane override to respective mask (to control antialiasing in octane render)


from typing import Union

import lx
import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_debug import H3dDebug
from h3d_utilites.scripts.h3d_utils import get_ptag


ARG_SELECTED = 'selected'
ARG_RECURSIVE = 'recursive'


def main():
    mask_fn = {
        ARG_SELECTED: get_selected_material_masks,
        ARG_RECURSIVE: get_recursive_selected_material_masks,
    }

    masks = mask_fn.get(lx.arg(), get_material_masks)()  # type: ignore

    for mask in masks:
        update_mask_name(mask)
        update_adv_material_name(mask)
        update_octane_override_name(mask)
        fill_image_maps(mask)


def get_material_masks() -> tuple[modo.Item, ...]:
    masks = modo.Scene().items(itype=c.MASK_TYPE)
    masks = [i for i in masks if get_ptag(i)]

    return tuple(masks)


def get_recursive_selected_material_masks() -> tuple[modo.Item, ...]:
    items: list[modo.Item] = modo.Scene().selectedByType(itype=c.MASK_TYPE)
    children: list[modo.Item] = []
    for item in items:
        children.extend(item.children(recursive=True, itemType=c.MASK_TYPE))
    items.extend(children)
    masks = [i for i in items if get_ptag(i)]

    return tuple(masks)


def get_selected_material_masks() -> tuple[modo.Item, ...]:
    items: list[modo.Item] = modo.Scene().selectedByType(itype=c.MASK_TYPE)
    masks = [i for i in items if get_ptag(i)]

    return tuple(masks)


def update_mask_name(mask: modo.Item):
    mask.name = ''


def update_adv_material_name(mask: modo.Item):
    adv_materials = mask.children(itemType=c.ADVANCEDMATERIAL_TYPE)

    if not adv_materials:
        return

    for material in adv_materials:
        material.name = f'M_{get_ptag(mask)}'


def update_octane_override_name(mask: modo.Item):
    octane_overrides = mask.children(itemType='material.octaneRenderer')

    if not octane_overrides:
        return

    for octane_override in octane_overrides:
        octane_override.name = f'O_{get_ptag(mask)}'


def fill_image_maps(mask: modo.Item):
    oc_overrides = mask.children(itemType='material.octaneRenderer')
    oc_override_video_stills: list[modo.Item] = []
    for oc_override in oc_overrides:
        oc_override_video_stills.extend(get_video_stills_from_oc_override(oc_override))

    if not oc_override_video_stills:
        return

    mask_image_maps = mask.children(itemType=c.IMAGEMAP_TYPE)
    mask_video_stills: list[modo.Item] = []
    for mask_image_map in mask_image_maps:
        image_map_video_still = get_video_stills_from_image_map(mask_image_map)
        if image_map_video_still:
            mask_video_stills.append(image_map_video_still)
    video_stills_to_fill = set(oc_override_video_stills) - set(mask_video_stills)
    for video_still in video_stills_to_fill:
        create_image_map(mask, video_still)


def get_video_stills_from_oc_override(oc_override: modo.Item) -> tuple[modo.Item, ...]:
    item_group = oc_override.itemGraph('itemGroups').reverse(0)

    return tuple([i for i in item_group.itemGraph('itemGroups').forward() if i.type == 'videoStill'])  # type: ignore


def get_video_stills_from_image_map(image_map: modo.Item) -> Union[modo.Item, None]:
    printd('get_video_still() function:')
    printd(f'{image_map.name=} {image_map}', 3)
    forwards: list[modo.Item] = [i for i in image_map.itemGraph('shadeLoc').forward()  # type: ignore
                                 if i.type == 'videoStill']
    printi(forwards, 'forwards:', 3)

    if forwards:
        return forwards[0]

    return None


def create_image_map(mask: modo.Item, video_still: modo.Item):
    lx.eval(f'select.subItem {{{mask.id}}} set textureLayer;light;render;environment')
    lx.eval(f'texture.new clip:{{{video_still.id}}}')
    lx.eval(f'texture.parent {{{mask.id}}} 1')
    lx.eval('item.editorColor red')


h3d = H3dDebug(enable=False, file=modo.Scene().name + '.log')
printd = h3d.print_debug
printi = h3d.print_items

if __name__ == '__main__':
    main()
