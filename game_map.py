import numpy as np  # type: ignore
from tcod.console import Console
import tile_types


class GameMap:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")

        # Tiles that the player can currently see
        self.visible = np.full((width, height), fill_value=False, order="F")
        # Tiles that the player has seen before
        self.explored = np.full((width, height), fill_value=False, order="F")

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside the bounds of this map"""
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        """
        Render the entire map. Faster than using the console.print method we used for individual entities

        If a tile is in the 'visible' array, then draw it with the 'light' colors.
        If it isn't, but it's in the 'explored array, then draw it with the 'dark' colors.
        Otherwise, the default is 'SHROUD'
        """

        # np.select allows us to conditionally draw the tiles we want, based on what's specified in 'condlist'
        # If it's visible it uses the first value in 'choicelist', if it's not visible but explored then it uses the
        # second value in 'choicelist'. If neither are true, it instead uses the value in SHROUD
        console.tiles_rgb[0:self.width, 0:self.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=tile_types.SHROUD
        )
