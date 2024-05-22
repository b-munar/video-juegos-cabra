
import esper
import pygame
import random

from src.ecs.components.c_enemy_hunter_state import CEnemyHunterState
from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_animation import CAnimation
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_enemy_bullet import CTagEnemyBullet
from src.ecs.components.tags.c_tag_explosion import CTagExplosion
from src.ecs.components.tags.c_tag_player import CTagPlayer
from src.ecs.components.tags.c_tag_star import CTagStar
from src.engine.service_locator import ServiceLocator

def create_square(ecs_world: esper.World, size: pygame.Vector2, pos: pygame.Vector2, vel: pygame.Vector2, col: pygame.Color) -> int:
    cuad_entity = ecs_world.create_entity()
    ecs_world.add_component(cuad_entity,
                CSurface(size, col))
    ecs_world.add_component(cuad_entity,
                CTransform(pos))
    ecs_world.add_component(cuad_entity, 
                CVelocity(vel))
    return cuad_entity

def create_sprite(world: esper.World, pos:pygame.Vector2, vel:pygame.Vector2, surface: pygame.Surface)->int:
    sprite_entity = world.create_entity()
    world.add_component(sprite_entity, CTransform(pos))
    world.add_component(sprite_entity, CVelocity(vel))
    world.add_component(sprite_entity, CSurface.from_surface(surface))
    return sprite_entity



def create_enemy_square(world: esper.World, pos: pygame.Vector2, enemy_info: dict):
    enemy_surface = ServiceLocator.images_services.get(enemy_info["image"])
    vel = enemy_info["velocity"]
    velocity = pygame.Vector2(vel, 0)
    enemy_entity = create_sprite(world, pos, velocity, enemy_surface)
    world.add_component(enemy_entity, CTagEnemy("Bouncer", enemy_info["points"]))
    world.add_component(enemy_entity, CAnimation(enemy_info["animations"]))

def create_enemy_hunter(world: esper.World, pos: pygame.Vector2, enemy_info: dict):
    enemy_surface = ServiceLocator.images_services.get(enemy_info["image"])
    velocity = pygame.Vector2(0, 0)
    enemy_entity = create_sprite(world, pos, velocity, enemy_surface)
    world.add_component(enemy_entity, CEnemyHunterState(pos))
    world.add_component(enemy_entity, CAnimation(enemy_info["animations"]))
    world.add_component(enemy_entity, CTagEnemy("Hunter"))

def create_player_square(world: esper.World, player_info: dict, player_lcl_info: dict) -> int:
    player_sprite = ServiceLocator.images_services.get(player_info["image"])
    size = player_sprite.get_rect().size
    pos = pygame.Vector2(player_lcl_info["position"]["x"] - (size[0]/2), player_lcl_info["position"]["y"] - (size[1]/2))
    vel = pygame.Vector2(0, 0)
    player_entity = create_sprite(world, pos, vel, player_sprite)
    world.add_component(player_entity, CTagPlayer())
    return player_entity

def create_enemy_spawner(world:esper.World, level_data: dict):
    spawner_entity = world.create_entity()
    world.add_component(spawner_entity, CEnemySpawner(level_data["enemy_spawn_events"]))


def create_input_player(world:esper.World):
    input_left  = world.create_entity()
    input_right  = world.create_entity()

    world.add_component(input_left, CInputCommand("PLAYER_LEFT", pygame.K_a))
    world.add_component(input_right, CInputCommand("PLAYER_RIGHT", pygame.K_d))
    input_pause = world.create_entity()
    world.add_component(input_pause, CInputCommand("PAUSE", pygame.K_p))
    
    input_fire= world.create_entity()

    world.add_component(input_fire, CInputCommand("PLAYER_FIRE", pygame.K_SPACE))

def create_bullet(world: esper.World, player_pos: pygame.Vector2, player_size: pygame.Vector2, bullet_info: dict):
    pos = pygame.Vector2(player_pos.x + player_size[0]/2 - (bullet_info["size"]["x"]/2), player_pos.y + player_size[1]/2-(bullet_info["size"]["y"]/2))
    vel = pygame.Vector2(0, -bullet_info["velocity"])
    bullet_entity = create_square(world, 
                                  pygame.Vector2(bullet_info["size"]["x"], bullet_info["size"]["y"]), 
                                  pos, vel, 
                                  pygame.Color(bullet_info["color"]["r"], bullet_info["color"]["g"], bullet_info["color"]["b"]))
    world.add_component(bullet_entity, CTagBullet())
    ServiceLocator.sounds_service.play(bullet_info["sound"])

def create_enemy_bullet(world: esper.World, enemy_pos: pygame.Vector2, enemy_size: pygame.Vector2, bullet_info: dict):
    pos = pygame.Vector2(enemy_pos.x + enemy_size[0]/2 - (bullet_info["enemy_size"]["x"]/2), enemy_pos.y + enemy_size[1]/2-(bullet_info["enemy_size"]["y"]/2))
    vel = pygame.Vector2(0, bullet_info["enemy_velocity"])
    bullet_entity = create_square(world, 
                                  pygame.Vector2(bullet_info["enemy_size"]["x"], bullet_info["enemy_size"]["y"]), 
                                  pos, vel, 
                                  pygame.Color(bullet_info["enemy_color"]["r"], bullet_info["enemy_color"]["g"], bullet_info["enemy_color"]["b"]))
    world.add_component(bullet_entity, CTagEnemyBullet())

def create_explosion(world: esper.World, pos: pygame.Vector2, explosion_info: dict):
    explosion_surface = ServiceLocator.images_services.get(explosion_info["enemy_image"])
    vel = pygame.Vector2(0, 0)
    explosion_entity = create_sprite(world, pos, vel, explosion_surface)
    world.add_component(explosion_entity, CTagExplosion())
    world.add_component(explosion_entity, CAnimation(explosion_info["animations"]))
    ServiceLocator.sounds_service.play(explosion_info["enemy_sound"])
    return explosion_entity

def create_player_explosion(world: esper.World, pos: pygame.Vector2, size: tuple, explosion_info: dict):
    explosion_surface = ServiceLocator.images_services.get(explosion_info["player_image"])
    vel = pygame.Vector2(0, 0)
    explosion_entity = create_sprite(world, pygame.Vector2(pos.x - size[0]/2, pos.y - size[1]/2), vel, explosion_surface)
    world.add_component(explosion_entity, CTagExplosion())
    world.add_component(explosion_entity, CAnimation(explosion_info["animations"]))
    ServiceLocator.sounds_service.play(explosion_info["player_sound"])
    return explosion_entity

def create_text(ecs_world: esper.World, text_info: dict, color: dict):
    font = ServiceLocator.fonts_service.get(text_info["font"], text_info["font_size"])
    pos = text_info["position"]
    text_surface = font.render(text_info["text"], False, pygame.Color(color["r"], color["g"], color["b"]))
    text_entity = ecs_world.create_entity()
    ecs_world.add_component(text_entity, CSurface.from_text(text_surface))
    ecs_world.add_component(text_entity,
                    CTransform(pygame.Vector2(pos["x"], pos["y"])))
    return text_entity

def create_star(world: esper.World, starfield_cfg: dict, window_cfg: dict):
    size = pygame.Vector2(1, 1)
    pos = pygame.Vector2(random.randint(0, window_cfg['size']['w']-1), 0)
    vel = pygame.Vector2(0, random.randint(starfield_cfg['vertical_speed']['min'], starfield_cfg['vertical_speed']['max']))
    col_dict = starfield_cfg['star_colors'][random.randint(0, 2)]
    color = pygame.Color(col_dict['r'], col_dict['g'], col_dict['b'])
    star_entity = create_square(world, size, pos, vel, color)
    world.add_component(star_entity, CTagStar(random.uniform(starfield_cfg['blink_rate']['min'], starfield_cfg['blink_rate']['max']), color))

def create_starfield(world: esper.World, starfield_cfg: dict, window_cfg: dict):
    for i in range(starfield_cfg['number_of_stars']):
        create_star(world, starfield_cfg, window_cfg)