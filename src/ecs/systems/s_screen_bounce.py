

import esper
import pygame

from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_surface import CSurface
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_player import CTagPlayer

def system_screen_bounce(world:esper.World, screen:pygame.Surface, player_entity: int):
    screen_rect = screen.get_rect()
    components = world.get_components(CTransform, CVelocity, CSurface, CTagEnemy)

    c_t:CTransform
    c_v:CVelocity
    c_s:CSurface
    for _, (c_t, c_v, c_s, c_e) in components:
        cuad_rect = CSurface.get_area_relative(c_s.area, c_t.pos)
        if c_e.enemy_type == "Bouncer":
            if cuad_rect.left < 15 or cuad_rect.right > screen_rect.width - 15:
                for _, (c_t2, c_v2, c_s2, c_e2) in components:
                    c_v2.vel.x *= -1
    if len(components) == 0 and world.get_component(CEnemySpawner)[0][1].current_time > 4:
        world.component_for_entity(player_entity, CTagPlayer).win = True
