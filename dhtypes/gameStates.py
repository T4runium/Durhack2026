from enum import Enum

class GameState(Enum):
    LOADING = 0
    MENU = 1
    DRUMMOVE = 2
    STICKDROP = 3
    STICKMOVE = 4
    POSTGAME = 5