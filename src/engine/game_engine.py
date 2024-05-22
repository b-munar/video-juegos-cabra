import asyncio
import json
import time
import pygame
import esper

from src.create.prefab_creator import create_bullet, create_enemy_spawner, create_input_player, create_player_square, create_sprite, create_square, create_starfield, create_text
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_player import CTagPlayer
from src.ecs.systems.s_animation import system_animatiom
from src.ecs.systems.s_collision_enemy_bullet import system_collision_enemy_bullet
from src.ecs.systems.s_collision_player_bullet import system_collision_player_bullet
from src.ecs.systems.s_collision_player_enemy import systmen_collision_player_enemy
from src.ecs.systems.s_enemy_fire import system_enemy_fire
from src.ecs.systems.s_enemy_hunter_state import system_enemy_hunter_state
from src.ecs.systems.s_enemy_spawner import system_enemy_spawner
from src.ecs.systems.s_explosion_kill import system_explosion_kill
from src.ecs.systems.s_input_player import system_input_player
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_pause_text import system_pause_text
from src.ecs.systems.s_player_state import system_player_state
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.systems.s_score_text import system_score_text
from src.ecs.systems.s_screen_bounce import system_screen_bounce
from src.ecs.systems.s_screen_bullet import system_screen_bullet
from src.ecs.systems.s_screen_player import system_screen_player
from src.ecs.systems.s_star_blink import system_star_blink
from src.ecs.systems.s_start_text import system_start_text
from src.engine.service_locator import ServiceLocator

class GameEngine:
    def __init__(self) -> None:
        self._load_config_files()

        pygame.init()
        pygame.display.set_caption(self.window_cfg["title"])
        self.screen = pygame.display.set_mode(
            (self.window_cfg["size"]["w"], self.window_cfg["size"]["h"]))

        self.clock = pygame.time.Clock()
        self.is_running = False
        self.framerate = self.window_cfg["framerate"]
        self.delta_time = 0
        self.pause = False
        self.reset = False
        self.score = 0

        self.bg_color = pygame.Color(self.window_cfg["bg_color"]["r"],
                                     self.window_cfg["bg_color"]["g"],
                                     self.window_cfg["bg_color"]["b"])
        self.ecs_world = esper.World()

        # Original framerate = 0
        # Original bg_color (0, 200, 128)

    def _load_config_files(self):
        with open("assets/cfg/window.json", encoding="utf-8") as window_file:
            self.window_cfg = json.load(window_file)
        with open("assets/cfg/enemies.json") as enemies_file:
            self.enemies_cfg = json.load(enemies_file)
        with open("assets/cfg/level_01.json") as level_01_file:
            self.level_01_cfg = json.load(level_01_file)
        with open("assets/cfg/player.json") as player_file:
            self.player_cfg = json.load(player_file)
        with open("assets/cfg/bullet.json") as bullet_file:
            self.bullet_cfg = json.load(bullet_file)
        with open("assets/cfg/explosion.json") as explosion_file:
            self.explosion_cfg = json.load(explosion_file)
        with open("assets/cfg/interface.json") as interface_file:
            self.interface_cfg = json.load(interface_file)
        with open("assets/cfg/starfield.json") as starfield_file:
            self.starfield_cfg = json.load(starfield_file)

    async def run(self) -> None:
        self._create()
        self.is_running = True
        while self.is_running:
            self._calculate_time()
            self._process_events()
            self._update()
            self._draw()
            await asyncio.sleep(0)
        self._clean()

    def _create(self):
        create_starfield(self.ecs_world, self.starfield_cfg, self.window_cfg)
        self._player_entity = create_player_square(self.ecs_world, self.player_cfg, self.level_01_cfg["player_spawn"])
        self._player_c_v = self.ecs_world.component_for_entity(self._player_entity, CVelocity)
        self._player_c_t = self.ecs_world.component_for_entity(self._player_entity, CTransform)
        self._player_c_s = self.ecs_world.component_for_entity(self._player_entity, CSurface)
        create_enemy_spawner(self.ecs_world, self.level_01_cfg)
        self.pause_text_entity = create_text(self.ecs_world, self.interface_cfg["pause"], self.interface_cfg["black"])
        if not self.reset:
            self.start_text_entity = create_text(self.ecs_world, self.interface_cfg["start"], self.interface_cfg["normal_text_color"])
            
            self.logo =create_sprite(self.ecs_world, 
                                     pygame.Vector2(self.interface_cfg['logo']['position']['x'], self.interface_cfg['logo']['position']['y']),
                                     pygame.Vector2(0, 0), ServiceLocator.images_services.get(self.interface_cfg['logo']['image']) )
        else:
            self.start_text_entity = create_text(self.ecs_world, self.interface_cfg["ready"], self.interface_cfg["normal_text_color"])
        create_text(self.ecs_world, self.interface_cfg["up"], self.interface_cfg["title_text_color"])
        self.interface_cfg["score"]['text'] = str(self.score)
        self.score_text_entity = create_text(self.ecs_world, self.interface_cfg["score"], self.interface_cfg["normal_text_color"])
        self.ecs_world.component_for_entity(self.score_text_entity, CSurface).count = self.score
        create_input_player(self.ecs_world)
        if not self.reset:
            ServiceLocator.sounds_service.play(self.level_01_cfg["start_game_sound"])

    def _calculate_time(self):
        self.clock.tick(self.framerate)
        self.delta_time = self.clock.get_time() / 1000.0
    
    def _process_events(self):
        for event in pygame.event.get():
            system_input_player(self.ecs_world, event, self._do_action)
            if event.type == pygame.QUIT:
                self.is_running = False

    def _update(self):
        system_pause_text(self.ecs_world, self.pause_text_entity, self.pause, self.interface_cfg["pause"], self.interface_cfg["title_text_color"], self.delta_time)
        if not self.pause:
            system_enemy_spawner(self.ecs_world, self.enemies_cfg, self.delta_time)
            system_movement(self.ecs_world, self.delta_time)
            system_star_blink(self.ecs_world, self.window_cfg, self.delta_time)
            system_screen_bounce(self.ecs_world, self.screen, self._player_entity)
            system_screen_player(self.ecs_world, self.screen)
            system_screen_bullet(self.ecs_world, self.screen)
            system_explosion_kill(self.ecs_world)
            system_collision_enemy_bullet(self.ecs_world, self.explosion_cfg, self.score_text_entity)
            system_enemy_fire(self.ecs_world, self.bullet_cfg)
            system_collision_player_bullet(self.ecs_world, self._player_entity, self.explosion_cfg)
            system_start_text(self.ecs_world, self.start_text_entity, self.delta_time, self.interface_cfg["start"], self.logo)
            system_score_text(self.ecs_world, self.score_text_entity, self.interface_cfg["score"], self.interface_cfg["normal_text_color"])
            system_animatiom(self.ecs_world, self.delta_time)
            self.ecs_world._clear_dead_entities()
            self.num_bullets = len(self.ecs_world.get_component(CTagBullet))
            if(self.ecs_world.component_for_entity(self._player_entity, CTagPlayer).dead):
                    self.score = 0
                    self.ecs_world.clear_database()
                    self.reset = True
                    self._create()
            if(self.ecs_world.component_for_entity(self._player_entity, CTagPlayer).win):
                    self.score += self.ecs_world.component_for_entity(self.score_text_entity, CSurface).count
                    self.ecs_world.clear_database()
                    self.reset = True
                    self._create()

    def _draw(self):
        self.screen.fill(self.bg_color)
        system_rendering(self.ecs_world, self.screen)
        pygame.display.flip()

    def _clean(self):
        self.ecs_world.clear_database()
        pygame.quit()

    def _do_action(self, c_input:CInputCommand):

        print(c_input.name + " " + str(c_input.phase))
        if c_input.name == "PLAYER_LEFT":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.x -= self.player_cfg["input_velocity"]
                c_input.prev = CommandPhase.START
            if c_input.phase == CommandPhase.END:
                if c_input.prev != CommandPhase.START:
                    self._player_c_v.vel.x = 0
                else:
                    self._player_c_v.vel.x += self.player_cfg["input_velocity"]
                c_input.prev = CommandPhase.NA


        if c_input.name == "PLAYER_RIGHT":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.x += self.player_cfg["input_velocity"]
                c_input.prev = CommandPhase.START
            if c_input.phase == CommandPhase.END:
                if c_input.prev != CommandPhase.START:
                    self._player_c_v.vel.x = 0
                else:
                    self._player_c_v.vel.x -= self.player_cfg["input_velocity"]
                c_input.prev = CommandPhase.NA

        if c_input.name == "PAUSE":
            if c_input.phase == CommandPhase.START:
                self.pause = not self.pause

        if c_input.name == "PLAYER_FIRE" and self.num_bullets < self.level_01_cfg["player_spawn"]["max_bullets"] and not self.pause and len(self.ecs_world.get_component(CTagEnemy)) > 0:
            create_bullet(self.ecs_world, self._player_c_t.pos, self._player_c_s.area.size, self.bullet_cfg)