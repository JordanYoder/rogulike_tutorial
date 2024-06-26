from __future__ import annotations
from typing import Iterator, List, Tuple, TYPE_CHECKING
import entity_factories
from game_map import GameMap
import tile_types
import random
import tcod

if TYPE_CHECKING:
    from engine import Engine


class RectangularRoom:
    def __init__(self, x: int, y: int, width: int, height: int):
        """
        Takes the x & y coordinates of the top left corner,
        then computes the bottom right corner based on the width and height
        """
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def center(self) -> Tuple[int, int]:
        """
        Center is a 'property' which essentially acts like a read only variable for our RectangularRoom class.
        It describes the x and y coordinates of the center of a room
        """
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y

    @property
    def inner(self) -> Tuple[slice, slice]:
        """
        Return the inner area of this room as a 2D array index

        This is the part we'll be 'digging out' for our room. It gives us an easy way to get the area to carve out.
        self.x1 and self.y1 have +1 as the zero index will be the start of the wall
        This is important to assure that if we draw two rectangles next to each other that they do not overlap; as they
        both will have walls

            0 1 2 3 4 5 6 7
         0  # # # # # # # #
         1  # . . . . . . #
         2  # . . . . . . #
         3  # . . . . . . #
         4  # . . . . . . #
         5  # . . . . . . #
         6  # . . . . . . #
         7  # # # # # # # #

        """
        return slice(self.x1 + 1, self.x2), slice(self.y1, self.y2)

    def intersects(self, other: RectangularRoom) -> bool:
        """Return True if this room overlaps with another RectangularRoom"""
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )


def place_entities(room: RectangularRoom, dungeon: GameMap, maximum_monsters: int) -> None:
    number_of_monsters = random.randint(0, maximum_monsters)

    # Randomly place up to two monsters
    for i in range(number_of_monsters):
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        # If there is no other entity at that location, place entity
        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            if random.random() < 0.8:
                entity_factories.orc.spawn(dungeon, x, y)
            else:
                entity_factories.troll.spawn(dungeon, x, y)


def tunnel_between(start: Tuple[int, int], end: Tuple[int, int]) -> Iterator[Tuple[int, int]]:
    """Return an L-shaped tunnel between these two points"""
    x1, y1 = start
    x2, y2 = end

    if random.random() < 0.5:
        # Move horizontally, then vertically
        corner_x, corner_y = x2, y1
    else:
        # Move vertically, then horizontally
        corner_x, corner_y = x1, y2

    # Generate the coordinates for this tunnel
    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
        yield x, y  # Yield expressions return the values but keep the local state, allow it to pick up where it left
    for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
        yield x, y  # Yield expressions return the values but keep the local state, allow it to pick up where it left


def generate_dungeon(
        max_rooms: int,
        room_min_size: int,
        room_max_size: int,
        map_width: int,
        map_height: int,
        max_monsters_per_room: int,
        engine: Engine,
) -> GameMap:
    """Generate a new dungeon map"""
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    # Running list of RectangularRoom rooms
    rooms: List[RectangularRoom] = []

    # Algorithm may or may not produce room based on location and intersection of other rooms
    for r in range(max_rooms):
        # Get a random sized room
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        # Get a random x,y coordinate where the room will fit within the dungeon
        x = random.randint(0, dungeon.width - room_width - 1)
        y = random.randint(0, dungeon.height - room_height - 1)

        # RectangularRoom class makes rectangles easier to work with
        new_room = RectangularRoom(x, y, room_width, room_height)

        # Run through the other rooms and see if they intersect with this one
        if any(new_room.intersects(other_room) for other_room in rooms):
            continue  # This room intersects, discard this iteration and go to the next attempt
        # If there are no intersections then the room is valid

        # Dig out this rooms inner area
        dungeon.tiles[new_room.inner] = tile_types.floor

        if len(rooms) == 0:
            # The first room, where the player starts
            player.place(*new_room.center, dungeon)
        else:
            # All rooms after the first
            # Dig out a tunnel between this room and the previous one.
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x, y] = tile_types.floor

        place_entities(new_room, dungeon, max_monsters_per_room)

        # Append the new room to the list
        rooms.append(new_room)

    return dungeon
