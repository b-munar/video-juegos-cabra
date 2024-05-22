import pygame
import esper
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_star import CTagStar


def system_star_blink(world: esper.World, window_cfg: dict, delta: float):
    components = world.get_components(CTransform, CSurface, CTagStar)

    c_t: CTransform
    c_s: CSurface
    c_t_s: CTagStar
    for _, (c_t, c_s, c_t_s) in components:
        star_rect = CSurface.get_area_relative(c_s.area, c_t.pos)
        if star_rect.top > window_cfg['size']['h']:
            c_t.pos.y = 0
        c_s.count += delta
        if c_s.count <= c_t_s.blink_rate:
            c_s.surf.fill(c_t_s.color)
        elif c_s.count <= c_t_s.blink_rate * 2:
            c_s.surf.fill(pygame.Color(0, 0, 0))
        else:
            c_s.count = 0