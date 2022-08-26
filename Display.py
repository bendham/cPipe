from abc import ABC, abstractmethod
from typing import Dict
from PySimpleGUI import Window

class Display(ABC):
    @property
    @abstractmethod
    def events() -> Dict:
        pass
    
    @abstractmethod
    def getGUI() -> Window:
        pass
    
    @abstractmethod
    def startGUI() -> None:
        pass
    