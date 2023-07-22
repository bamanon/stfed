from PySide6 import QtWidgets

from stfed.model import ResourceType
from stfed.view import (
    DefaultResourcePreview,
    WavResourcePreview,
    PalResourcePreview,
    TlbResourcePreview,
    AniResourcePreview,
    SqbResourcePreview,
    FonResourcePreview,
    MifResourcePreview
)

def get_widget_for_resource_type(rt: ResourceType) -> QtWidgets.QWidget:
    if rt == ResourceType.ANI:
        return AniResourcePreview()
    if rt == ResourceType.FON:
        return FonResourcePreview()
    if rt == ResourceType.MIF:
        return MifResourcePreview()
    if rt == ResourceType.PAL:
        return PalResourcePreview()
    if rt == ResourceType.SQB:
        return SqbResourcePreview()
    if rt == ResourceType.TLB:
        return TlbResourcePreview()
    if rt == ResourceType.WAV:
        return WavResourcePreview()
    else:
        return DefaultResourcePreview()