import dataclasses


@dataclasses.dataclass(frozen=True)
class UserPreferences:
    lookup_paths: list[str]
    recent_files: list [str]
    double_width_image_preview: bool
    double_width_image_export: bool
