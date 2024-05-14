#!/usr/bin/env python3
import tcod
from engine import Engine
from entity import Entity
from input_handlers import EventHandler
from procgen import generate_dungeon


def main() -> None:
    # The screen size
    screen_width = 80
    screen_height = 50

    # The map size
    map_width = 80
    map_height = 45

    # Boundaries for size/number of rooms
    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    # Load the font, a 32x8 tile font with Libtcod's old character layout
    tileset = tcod.tileset.load_tilesheet(
        "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    # Create our event handler
    event_handler = EventHandler()

    # Create our initial two entities
    player = Entity(x=int(screen_width / 2), y=int(screen_height / 2), char="@", color=(255, 255, 255))
    npc = Entity(x=int(screen_width / 2 - 5), y=int(screen_height / 2), char="@", color=(255, 255, 0))
    entities = {player, npc}

    # Create our map object
    game_map = generate_dungeon(
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
        player=player
    )

    # Passes entities and event_handler to the engine
    engine = Engine(entities=entities, event_handler=event_handler, game_map=game_map, player=player)

    # Create a window based on this console and tileset
    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset=tileset,
        title="Yet Another Roguelike Tutorial",
        vsync=True,
    ) as context:
        root_console = tcod.Console(screen_width, screen_height, order="F")  # Numpy access 2D arrays in [y,x] order

        # Main loop
        while True:
            # Draw the entities on the screen
            engine.render(console=root_console, context=context)

            # Get event
            events = tcod.event.wait()
            engine.handle_events(events)


if __name__ == "__main__":
    main()
