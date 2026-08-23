import json
import re

from dataclasses import asdict
from pathlib import Path

from settings.Settings import Settings, ScanMethod, LongTermValidationSettings


class SettingsManager:
    """Persist application settings in named profiles and shared storage."""

    def __init__(self):
        """Initialize storage paths and load the configured default profile."""
        self._settings = Settings()

        self._profiles_path = Path(__file__).parent / "profiles"
        self._profiles_path.mkdir(exist_ok=True)

        self._shared_path = Path(__file__).parent / "shared.json"

        self._create_shared()
        self._load_shared()
        self.load_default_profile()

    @property
    def settings(self) -> Settings:
        """Return the active settings object.

        Returns:
            Mutable settings currently used by the application.
        """
        return self._settings

    # ==================== Settings ====================

    def reset_to_factory_defaults(self):
        """Replace active settings with fresh default values."""
        self._settings = Settings()

    # ==================== Profiles ====================

    def save_profile(self, name: str):
        """Serialize active settings into a named profile.

        Args:
            name: Valid profile name to create or overwrite.

        Raises:
            ValueError: If the profile name is invalid.
        """
        self._validate_profile_name(name)

        path = self._get_profile_path(name)

        with path.open("w", encoding="utf-8") as file:
            json.dump(asdict(self._settings), file, indent=2, ensure_ascii=False)

    def load_profile(self, name: str):
        """Load a named profile as the active settings.

        Args:
            name: Valid profile name to load.

        Raises:
            ValueError: If the profile name is invalid.
            FileNotFoundError: If the profile does not exist.
        """
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
        
        if "long_term_validation_settings" in data:
            data["long_term_validation_settings"] = LongTermValidationSettings(**data["long_term_validation_settings"])

        self._settings = Settings(**data)

    def delete_profile(self, name: str):
        """Delete a named profile and clear it as default when necessary.

        Args:
            name: Valid profile name to delete.

        Raises:
            ValueError: If the profile name is invalid.
            FileNotFoundError: If the profile does not exist.
        """
        self._validate_profile_name(name)

        path = self._get_profile_path(name)

        if not path.exists():
            raise FileNotFoundError(f"Profile '{name}' does not exist")

        path.unlink()

        if self.get_default_profile() == name:
            self.set_default_profile(None)

    def rename_profile(self, old_name: str, new_name: str):
        """Rename a profile and preserve its default-profile status.

        Args:
            old_name: Existing valid profile name.
            new_name: New valid profile name.

        Raises:
            ValueError: If either profile name is invalid.
            FileNotFoundError: If the old profile does not exist.
            FileExistsError: If the new profile already exists.
        """
        self._validate_profile_name(old_name)
        self._validate_profile_name(new_name)

        old_path = self._get_profile_path(old_name)
        new_path = self._get_profile_path(new_name)

        if not old_path.exists():
            raise FileNotFoundError(f"Profile '{old_name}' does not exist")

        if new_path.exists():
            raise FileExistsError(f"Profile '{new_name}' already exists")

        old_path.rename(new_path)

        if self.get_default_profile() == old_name:
            self.set_default_profile(new_name)

    def profile_exists(self, name: str) -> bool:
        """Check whether a valid profile exists.

        Args:
            name: Profile name to check.

        Returns:
            True when the profile JSON file exists.

        Raises:
            ValueError: If the profile name is invalid.
        """
        self._validate_profile_name(name)
        return self._get_profile_path(name).is_file()

    def get_profiles(self) -> list[str]:
        """Return profile names in sorted order.

        Returns:
            Sorted profile names without their JSON extension.
        """
        return sorted(
            path.stem
            for path in self._profiles_path.glob("*.json")
        )

    # ==================== Default profile ====================

    def set_default_profile(self, name: str | None):
        """Set the profile loaded at startup, or clear the default.

        Args:
            name: Existing profile name, or None to use factory defaults.

        Raises:
            ValueError: If the profile name is invalid.
            FileNotFoundError: If the named profile does not exist.
        """
        if name is not None:
            self._validate_profile_name(name)

            if not self.profile_exists(name):
                raise FileNotFoundError(f"Profile '{name}' does not exist")

        self._set_shared("default_profile", name)

    def get_default_profile(self) -> str | None:
        """Return the profile selected for startup.

        Returns:
            Default profile name, or None when defaults should be used.
        """
        return self._shared["default_profile"]

    def load_default_profile(self):
        """Load the configured default profile or fall back to factory defaults."""
        name = self.get_default_profile()

        if name is None:
            self.reset_to_factory_defaults()
            return

        if not self.profile_exists(name):
            self.reset_to_factory_defaults()
            self.set_default_profile(None)
            return

        self.load_profile(name)

    # ==================== Shared ====================

    def get_shared(self, key: str):
        """Read a value from shared persistent storage.

        Args:
            key: Shared-storage key to read.

        Returns:
            Stored value for the key.

        Raises:
            KeyError: If the key does not exist.
        """
        return self._shared[key]

    def set_shared(self, key: str, value):
        """Write a shared value and persist the storage file.

        Args:
            key: Shared-storage key to set.
            value: JSON-serializable value to persist.
        """
        self._shared[key] = value
        self._save_shared()

    def delete_shared(self, key: str):
        """Delete a non-reserved shared-storage key.

        Args:
            key: Existing non-reserved key to delete.

        Raises:
            ValueError: If the reserved default_profile key is requested.
            KeyError: If the key does not exist.
        """
        if key == "default_profile":
            raise ValueError("The default_profile key cannot be deleted")

        del self._shared[key]
        self._save_shared()

    def shared_exists(self, key: str) -> bool:
        """Check whether a shared-storage key exists.

        Args:
            key: Shared-storage key to check.

        Returns:
            True when the key exists.
        """
        return key in self._shared

    # ==================== Shared internals ====================

    def _create_shared(self):
        """Create the shared-storage file when it does not exist."""
        if self._shared_path.exists():
            return

        with self._shared_path.open("w", encoding="utf-8") as file:
            json.dump({"default_profile": None}, file, indent=2)

    def _load_shared(self):
        """Load shared storage and ensure required default keys exist."""
        with self._shared_path.open("r", encoding="utf-8") as file:
            self._shared = json.load(file)

        if "default_profile" not in self._shared:
            self._shared["default_profile"] = None
            self._save_shared()

    def _set_shared(self, key: str, value):
        """Set a shared value without public validation.

        Args:
            key: Shared-storage key to set.
            value: JSON-serializable value to persist.
        """
        self._shared[key] = value
        self._save_shared()

    def _save_shared(self):
        """Write the current shared-storage mapping to disk."""
        with self._shared_path.open("w", encoding="utf-8") as file:
            json.dump(self._shared, file, indent=2, ensure_ascii=False)

    # ==================== Helpers ====================

    def _get_profile_path(self, name: str) -> Path:
        """Build the JSON path for a validated profile name.

        Args:
            name: Profile name to convert into a path.

        Returns:
            Profile JSON path within the profiles directory.
        """
        return self._profiles_path / f"{name}.json"

    def _validate_profile_name(self, name: str):
        """Validate the restricted profile-name format.

        Args:
            name: Profile name to validate.

        Raises:
            ValueError: If the name is empty, reserved, or contains invalid characters.
        """
        if not name:
            raise ValueError("Profile name cannot be empty")

        if name == "default":
            raise ValueError("The profile name 'default' is reserved")

        if not re.fullmatch(r"[a-zA-Z0-9_-]+", name):
            raise ValueError(
                "Profile name can only contain letters, numbers, '_' and '-'."
            )
