import dataclasses
import enum


class Severity(enum.Enum):
    Warning = enum.auto()
    Critical = enum.auto()


@dataclasses.dataclass
class ImportIssue:
    severity: Severity
    text: str

