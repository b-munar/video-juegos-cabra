import pygame
import esper
from src.ecs.components.c_surface import CSurface
from src.engine.service_locator import ServiceLocator


def system_pause_text(ecs_world: esper.World, pause_text_entity: int, pause: bool, pause_cfg: dict, color: dict, delta: float):
    pause_surface = ecs_world.component_for_entity(pause_text_entity, CSurface)
    text = ''
    if pause:
        pause_surface.count += delta
        if pause_surface.count <= pause_cfg['display_time'] / 2:
            text = pause_cfg['text']
        elif pause_surface.count <= pause_cfg['display_time']:
            text = ''
        else:
            pause_surface.count = 0
    else:
        pause_surface.count = 0
    font = ServiceLocator.fonts_service.get(pause_cfg['font'], pause_cfg["font_size"])
    pause_surface.surf = font.render(text, False, pygame.Color(color["r"], color["g"], color["b"]))
    pause_surface.area = pause_surface.surf.get_rect()