import stfed.factories.pal as pal
import stfed.factories.fon as fon
from stfed.model import ResourceType
from stfed.repos.user_preferences import repo as user_preferences_repo


def get_export_formats_for_resource(rt: ResourceType):
    ext = rt.name.upper()
    default_formats = []

    if rt not in [ResourceType.WAV, ResourceType.BNK, ResourceType.HMP]:
        default_formats = [
            (
                f"Raw {ext} file *.{ext} (*.{ext})",
                lambda resource: resource.data()
            ),
            (
                f"Raw {ext} file with header *.{ext} (*.{ext})",
                lambda resource: resource.data()
            ),
        ]

    if rt == ResourceType.WAV:
        return [(
            f"Waveform Audio File *.WAV (*.WAV)",
            lambda resource: resource.data()
        )]
    
    if rt == ResourceType.BNK:
        return [(
            f"AdLib Instrument Bank version 0.0 for Human Machine Interfaces *.BNK (*.BNK)",
            lambda resource: resource.data()
        )]
    
    if rt == ResourceType.HMP:
        return [(
            f"Human Machine Interfaces MIDI *.HMP (*.HMP)",
            lambda resource: resource.data()\
    )]
    
    extra_formats = []
    if rt == ResourceType.PAL:
        extra_formats = [
            (
                "PCX file *.PCX (*.PCX)",
                lambda resource: pal.export_as_pcx(pal.parse(resource.data()))
            ),
            (
                "HTML file *.html (*.html)",
                lambda resource: pal.export_as_html(pal.parse(resource.data()).encode('utf-8'))
            ),
        ]

    if rt == ResourceType.FON:
        extra_formats = [(
            "PNG file *.PNG (*.PNG)",
            lambda resource: fon.export_as_png(
                fon.parse(resource),
                user_preferences_repo.get().double_width_image_export)
        )]

    return default_formats + extra_formats
