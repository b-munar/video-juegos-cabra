import pygame
import esper
from src.ecs.components.c_surface import CSurface
from src.engine.service_locator import ServiceLocator


def system_score_text(world: esper.World, text_entity: int, score_cfg: dict, color: dict):
    score_surface = world.component_for_entity(text_entity, CSurface)
    font = ServiceLocator.fonts_service.get(score_cfg['font'], score_cfg["font_size"])
    text = '00' if score_surface.count == 0 else str(score_surface.count)
    score_surface.surf = font.render(text, False, pygame.Color(color["r"], color["g"], color["b"]))
    score_surface.area = score_surface.surf.get_rect()

