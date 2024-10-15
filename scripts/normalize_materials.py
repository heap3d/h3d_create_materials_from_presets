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


import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_debug import H3dDebug
from h3d_utilites.scripts.h3d_utils import get_ptag


def main():
    masks = get_material_masks()


def get_material_masks() -> tuple[modo.Item]:
    masks = modo.Scene().items(itype=c.MASK_TYPE)
    masks = [m for m in masks if get_ptag(m)]
    return tuple(masks)


h3d = H3dDebug(enable=True, file=modo.Scene().name + '.log')
printd = h3d.print_debug
printi = h3d.print_items

if __name__ == '__main__':
    main()
