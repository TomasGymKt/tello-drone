from abc import ABC, abstractmethod

from utils.models import MouseData

class Element(ABC):
    @abstractmethod
    def handle_mouse(self, mouse: MouseData):
        ...
        
    @abstractmethod
    def render(self, frame):
        ...
    
    @abstractmethod
    def set_debug_render(self, enabled: bool):
        ...
    

    

