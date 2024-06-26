from __future__ import annotations
from typing import Optional, TYPE_CHECKING  # Optional denotes something can be set to None
import tcod.event
from actions import Action, EscapeAction, BumpAction

if TYPE_CHECKING:
    from engine import Engine


# Superclass EventDispatch allows us to send an event to its proper method based on what type of event it is
class EventHandler(tcod.event.EventDispatch[Action]):
    """The EventHandler class take an Action class event and performs an action"""
    def __init__(self, engine: Engine):
        self.engine = engine

    def handle_events(self) -> None:
        for event in tcod.event.wait():
            action = self.dispatch(event)

            if action is None:
                continue

            action.perform()
            self.engine.handle_enemy_turns()
            self.engine.update_fov()

    # Event quit
    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()

    # When a key is pressed down
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        # This variable holds whatever subclass of Action we end up assigning to it. If no valid key, set to None
        action: Optional[Action] = None

        # The key pressed with no modifiers
        key = event.sym

        player = self.engine.player

        # Uses MovementAction to move the player
        if key == tcod.event.K_UP:
            action = BumpAction(player, dx=0, dy=-1)
        elif key == tcod.event.K_DOWN:
            action = BumpAction(player, dx=0, dy=1)
        elif key == tcod.event.K_LEFT:
            action = BumpAction(player, dx=-1, dy=0)
        elif key == tcod.event.K_RIGHT:
            action = BumpAction(player, dx=1, dy=0)

        elif key == tcod.event.K_ESCAPE:
            action = EscapeAction(player)

        # No valid key was pressed
        return action
