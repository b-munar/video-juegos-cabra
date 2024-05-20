import esper
from src.ecs.components.c_animation import CAnimation, set_animation
from src.ecs.components.c_player_state import CPlayerState, PlayerState
from src.ecs.components.c_velocity import CVelocity

def system_player_state(world: esper.World):
    components = world.get_components(CVelocity, CAnimation, CPlayerState)
    for _, (c_v, c_a, c_pst) in components:
        if c_pst.state == PlayerState.IDLE:
            _do_idle_state(c_v, c_a, c_pst)
        if c_pst.state == PlayerState.MOVE:
            _do_move_state(c_v, c_a, c_pst)

def _do_idle_state(c_v:CVelocity, c_a:CAnimation, c_pst:CPlayerState):
    set_animation(c_a, 1)
    if c_v.vel.magnitude_squared()>0:
        c_pst.state=PlayerState.MOVE

def _do_move_state(c_v:CVelocity, c_a:CAnimation, c_pst:CPlayerState):
    set_animation(c_a, 0)
    if c_v.vel.magnitude_squared()<=0:
        c_pst.state=PlayerState.IDLE

