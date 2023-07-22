from stfed.model import Palette, ResourceType, UnitColors
import stfed.factories.pal
from stfed.repos.resources import resources_repo_instance as resources_repo


def substitute_unit_colors(pal: Palette, side1_color: UnitColors, side2_color: UnitColors, substitute_pal: Palette):
    data_copy = pal.data.copy()
    side1_src_colors_start = 192 + side1_color.value * 8
    side2_src_colors_start = 192 + side2_color.value * 8
    side1_dst_colors_start = 192
    side2_dst_colors_start = 192 + 8
    for i in range(8):
        data_copy[side1_dst_colors_start + i] = substitute_pal.data[side1_src_colors_start + i]
        data_copy[side2_dst_colors_start + i] = substitute_pal.data[side2_src_colors_start + i]
    return Palette(data_copy)
