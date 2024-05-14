from typing import Optional  # Optional denotes something can be set to None
import tcod.event            # We don't need all tcod, we just need event
from actions import Action, EscapeAction, MovementAction


# Superclass EventDispatch allows us to send an event to its proper method based on what type of event it is
class EventHandler(tcod.event.EventDispatch[Action]):
    """The EventHandler class take an Action class event and performs an action"""

    # Event quit
    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()

    # When a key is pressed down
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        # This variable holds whatever subclass of Action we end up assigning to it. If no valid key, set to None
        action: Optional[Action] = None

        # The key pressed with no modifiers
        key = event.sym

        # Uses MovementAction to move the player
        if key == tcod.event.K_UP:
            action = MovementAction(dx=0, dy=-1)
        elif key == tcod.event.K_DOWN:
            action = MovementAction(dx=0, dy=1)
        elif key == tcod.event.K_LEFT:
            action = MovementAction(dx=-1, dy=0)
        elif key == tcod.event.K_RIGHT:
            action = MovementAction(dx=1, dy=0)

        elif key == tcod.event.K_ESCAPE:
            action = EscapeAction()

        # No valid key was pressed
        return action
