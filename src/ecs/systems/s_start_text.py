import pygame
import esper
from src.ecs.components.c_surface import CSurface
from src.engine.service_locator import ServiceLocator


def system_start_text(world: esper.World, text_entity: int, time: float, start_cfg: dict, logo_entity: int):
    start_surface = world.component_for_entity(text_entity, CSurface)
    start_surface.count += time
    if start_surface.count >= start_cfg["display_time"]:
        font = ServiceLocator.fonts_service.get(start_cfg['font'], start_cfg["font_size"])
        text = ''
        start_surface.surf = font.render(text, False, pygame.Color(0, 0, 0))
        start_surface.area = start_surface.surf.get_rect()
        logo_surface = world.component_for_entity(logo_entity, CSurface)
        logo_surface.area.size = (0, 0)



