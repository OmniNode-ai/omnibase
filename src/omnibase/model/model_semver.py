from pydantic import BaseModel, field_validator, ValidationError
from typing import Optional
import re

SEMVER_REGEX = re.compile(
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>[0-9A-Za-z-\.]+))?"
    r"(?:\+(?P<build>[0-9A-Za-z-\.]+))?$"
)

class SemVerModel(BaseModel):
    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    build: Optional[str] = None

    @classmethod
    def parse(cls, version_str: str) -> "SemVerModel":
        match = SEMVER_REGEX.match(version_str)
        if not match:
            raise ValidationError(f"Invalid semantic version: {version_str}")
        parts = match.groupdict()
        return cls(
            major=int(parts["major"]),
            minor=int(parts["minor"]),
            patch=int(parts["patch"]),
            prerelease=parts["prerelease"],
            build=parts["build"],
        )

    @field_validator("major", "minor", "patch")
    @classmethod
    def non_negative(cls, v):
        if v < 0:
            raise ValueError("Version numbers must be non-negative")
        return v

    def __str__(self):
        s = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            s += f"-{self.prerelease}"
        if self.build:
            s += f"+{self.build}"
        return s

    def __eq__(self, other):
        if not isinstance(other, SemVerModel):
            return NotImplemented
        return (
            self.major == other.major and
            self.minor == other.minor and
            self.patch == other.patch and
            self.prerelease == other.prerelease and
            self.build == other.build
        )

    def __lt__(self, other):
        if not isinstance(other, SemVerModel):
            return NotImplemented
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        if self.patch != other.patch:
            return self.patch < other.patch
        # Prerelease comparison: None > any prerelease
        if self.prerelease is None and other.prerelease is not None:
            return False
        if self.prerelease is not None and other.prerelease is None:
            return True
        if self.prerelease != other.prerelease:
            return (self.prerelease or "") < (other.prerelease or "")
        return False

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        return not self < other 