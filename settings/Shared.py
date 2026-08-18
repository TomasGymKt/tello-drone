from typing import TYPE_CHECKING, Any

from settings.Manager import SettingsManager

if TYPE_CHECKING:
    from utils.models import ValidationPreset


class SharedSettings():
    def __init__(self, manager: SettingsManager):
        self._manager = manager
    
    
    # Validation presets
    
    def get_validation_presets(self):
        from utils.models import ValidationPreset
        presets: dict[str, Any] = self._manager.get_shared("validation_presets")
        return {
            name: ValidationPreset(**data)
            for name, data in presets.items()
        }
    
    def save_validation_preset(self, name: str, preset: ValidationPreset):
        presets = self._manager.get_shared("validation_presets")
        presets[name] = preset.to_dict()
        self._manager.set_shared("validation_presets", presets)