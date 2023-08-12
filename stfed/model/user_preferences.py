import dataclasses
import typing


@dataclasses.dataclass(frozen=True)
class UserPreferences:
    lookup_paths: typing.List[str]
    recent_files: typing.List[str]
    double_width_image_preview: bool
    double_width_image_export: bool
