from .Manager import SettingsManager
from .Settings import ScanMethod
from .Shared import SharedSettings

settings_manager = SettingsManager()
settings = settings_manager.settings
shared = SharedSettings(settings_manager)