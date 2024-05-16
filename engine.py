from typing import Set, Iterable, Any

from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov

from entity import Entity
from input_handlers import EventHandler
from game_map import GameMap


class Engine:
    def __init__(self, event_handler: EventHandler, game_map: GameMap, player: Entity):
        """
        Takes a set of entities (a Set is kind of like a list that enforces uniqueness
        An event handler to handle our events
        And a player that we keep outside the entities set for ease of access
        """
        self.event_handler = event_handler
        self.game_map = game_map
        self.player = player
        self.update_fov()

    def handle_enemy_turns(self) -> None:
        for entity in self.game_map.entities - self.player:
            print(f'The {entity.name} wonders when it will get to take a real turn.')

    def handle_events(self, events: Iterable[Any]) -> None:
        """We pass any events and iterate through them"""
        for event in events:
            action = self.event_handler.dispatch(event)

            if action is None:
                continue

            action.perform(self, self.player)
            self.handle_enemy_turns()

            self.update_fov()  # Update the FOV before the player's next action

    def update_fov(self) -> None:
        """Recompute the visible area based on the player's point of view"""
        # Setting the game_map's visible tiles to equal the result of compute_fov
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],   # Transparency is 2d numpy array and considers != 0 as transparent
            (self.player.x, self.player.y),  # The origin point of the FOV, which is a 2d index of x,y coordinates
            radius=8                              # How far the FOV extends
        )

        # If a tile is visible it should be added to explored
        self.game_map.explored |= self.game_map.visible

    def render(self, console: Console, context: Context) -> None:
        """We iterate through our entities and print them to their proper locations"""
        self.game_map.render(console)

        context.present(console)
        console.clear()
