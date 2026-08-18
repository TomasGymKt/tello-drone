import json
import re

from dataclasses import asdict
from pathlib import Path

from settings.Settings import Settings, ScanMethod


class SettingsManager:
    def __init__(self):
        self._settings = Settings()

        self._profiles_path = Path(__file__).parent / "profiles"
        self._profiles_path.mkdir(exist_ok=True)

        self._default_profile_path = self._profiles_path / "default.json"

        self._create_default_profile()
        self.load_default_profile()

    @property
    def settings(self) -> Settings:
        return self._settings

    def reset_to_factory_defaults(self):
        self._settings = Settings()

    def save_profile(self, name: str):
        self._validate_profile_name(name)

        path = self._get_profile_path(name)

        with path.open("w", encoding="utf-8") as file:
            json.dump(asdict(self._settings), file, indent=2, ensure_ascii=False)

    def load_profile(self, name: str):
        self._validate_profile_name(name)

        path = self._get_profile_path(name)

        if not path.exists():
            raise FileNotFoundError(f"Profile '{name}' does not exist")

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if "scan_method_order" in data:
            data["scan_method_order"] = [
                ScanMethod(method)
                for method in data["scan_method_order"]
            ]

        self._settings = Settings(**data)

    def delete_profile(self, name: str):
        self._validate_profile_name(name)

        if name == "default":
            raise ValueError("The default profile cannot be deleted")

        path = self._get_profile_path(name)

        if not path.exists():
            raise FileNotFoundError(f"Profile '{name}' does not exist")

        path.unlink()

        if self._get_default_profile() == name:
            self._set_default_profile(None)

    def rename_profile(self, old_name: str, new_name: str):
        self._validate_profile_name(old_name)
        self._validate_profile_name(new_name)

        if old_name == "default" or new_name == "default":
            raise ValueError("The profile name 'default' is reserved")

        old_path = self._get_profile_path(old_name)
        new_path = self._get_profile_path(new_name)

        if not old_path.exists():
            raise FileNotFoundError(f"Profile '{old_name}' does not exist")

        if new_path.exists():
            raise FileExistsError(f"Profile '{new_name}' already exists")

        old_path.rename(new_path)

        if self._get_default_profile() == old_name:
            self._set_default_profile(new_name)

    def set_default_profile(self, name: str | None):
        if name is not None:
            self._validate_profile_name(name)

            if not self.profile_exists(name):
                raise FileNotFoundError(f"Profile '{name}' does not exist")

        self._set_default_profile(name)

    def load_default_profile(self):
        name = self._get_default_profile()

        if name is None:
            self.reset_to_factory_defaults()
            return

        if not self.profile_exists(name):
            self.reset_to_factory_defaults()
            self._set_default_profile(None)
            return

        self.load_profile(name)

    def profile_exists(self, name: str) -> bool:
        self._validate_profile_name(name)
        return self._get_profile_path(name).is_file()

    def get_profiles(self) -> list[str]:
        return sorted(
            path.stem
            for path in self._profiles_path.glob("*.json")
            if path.name != "default.json"
        )

    def get_default_profile(self) -> str | None:
        return self._get_default_profile()

    def _create_default_profile(self):
        if self._default_profile_path.exists():
            return

        self._set_default_profile(None)

    def _get_default_profile(self) -> str | None:
        with self._default_profile_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return data.get("default")

    def _set_default_profile(self, name: str | None):
        with self._default_profile_path.open("w", encoding="utf-8") as file:
            json.dump({"default": name}, file, indent=2)

    def _get_profile_path(self, name: str) -> Path:
        return self._profiles_path / f"{name}.json"

    def _validate_profile_name(self, name: str):
        if not name:
            raise ValueError("Profile name cannot be empty")

        if name == "default":
            raise ValueError("The profile name 'default' is reserved")

        if not re.fullmatch(r"[a-zA-Z0-9_-]+", name):
            raise ValueError(
                "Profile name can only contain letters, numbers, '_' and '-'."
            )