from __future__ import annotations
from typing import TYPE_CHECKING, Any

from settings.Manager import SettingsManager

if TYPE_CHECKING:
    from utils.models import ValidationPreset


class SharedSettings():
    """Typed accessors for shared settings that do not belong to a profile."""

    def __init__(self, manager: SettingsManager):
        """Create shared-setting accessors backed by a settings manager.

        Args:
            manager: Manager used to read and write shared storage.
        """
        self._manager = manager
    
    
    # Validation presets
    
    def get_validation_presets(self):
        """Load all saved validation presets.

        Returns:
            Mapping from preset name to typed validation preset.
        """
        from utils.models import ValidationPreset
        presets: dict[str, Any] = self._manager.get_shared("validation_presets")
        return {
            name: ValidationPreset(**data)
            for name, data in presets.items()
        }
    
    def save_validation_preset(self, name: str, preset: ValidationPreset):
        """Save or replace a named validation preset.

        Args:
            name: Preset name to save.
            preset: Typed validation thresholds to persist.
        """
        presets = self._manager.get_shared("validation_presets")
        presets[name] = preset.to_dict()
        self._manager.set_shared("validation_presets", presets)
