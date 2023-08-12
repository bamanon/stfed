import stfed.factories.ani as ani
import stfed.factories.fon as fon
import stfed.factories.hmp as hmp
import stfed.factories.pal as pal
import stfed.factories.sqb as sqb
import stfed.factories.tlb as tlb
from stfed.model import ResourceType
from stfed.repos.user_preferences import repo as user_preferences_repo
from stfed.repos.resources import save_single_file_resource

def get_export_formats_for_resource(rt: ResourceType):
    ext = rt.name.upper()
    default_formats = []

    if rt not in [ResourceType.WAV, ResourceType.BNK, ResourceType.HMP]:
        default_formats = [
            (
                f"Raw {ext} file *.{ext} (*.{ext})",
                save_single_file_resource,
                []
            ),
        ]

    if rt == ResourceType.WAV:
        return [(
            "Waveform Audio File *.WAV (*.WAV)",
            save_single_file_resource,
            []
        )]
    
    if rt == ResourceType.BNK:
        return [(
            "AdLib Instrument Bank version 0.0 for Human Machine Interfaces *.BNK (*.BNK)",
            save_single_file_resource,
            []
        )]
    
    if rt == ResourceType.HMP:
        return [
            (
                "MIDI file *.mid (*.mid)",
                lambda resource: hmp.export_as_smf(resource.data()),
                []
            ),
            (
                "Human Machine Interfaces MIDI file *.HMP (*.HMP)",
                save_single_file_resource,
                []
            ),
        ]
    
    extra_formats = []
    if rt == ResourceType.PAL:
        extra_formats = [
            (
                "PCX file *.PCX (*.PCX)",
                lambda resource: pal.export_as_pcx(pal.parse(resource.data())),
                []
            ),
            (
                "HTML file *.html (*.html)",
                lambda resource: pal.export_as_html(pal.parse(resource.data()).encode('utf-8')),
                []
            ),
        ]

    if rt == ResourceType.FON:
        extra_formats = [(
            "PNG file *.PNG (*.PNG)",
            lambda resource: fon.export_as_png(
                fon.parse(resource),
                user_preferences_repo.get().double_width_image_export),
            []
        )]

    if rt == ResourceType.ANI:
        extra_formats = [(
            "PNG file *.PNG (*.PNG)",
            lambda ani_resource, pal_resource: ani.export_spritemap(
                ani.parse(ani_resource),
                pal.parse(pal_resource.data()),
                user_preferences_repo.get().double_width_image_export),
            ['pal']
        )]

    if rt == ResourceType.TLB:
        extra_formats = [(
            "PNG file *.PNG (*.PNG)",
            lambda tlb_resource, pal_resource: tlb.export_spritemap(
                tlb.parse_tile_library(tlb_resource.data()),
                pal.parse(pal_resource.data()),
                user_preferences_repo.get().double_width_image_export),
            ['pal']
        )]

    if rt == ResourceType.SQB:
        extra_formats = [(
            "JSON file *.json (*.json)",
            lambda resource: sqb.export_as_json(resource).encode('utf-8'),
            []
        )]

    return extra_formats + default_formats
