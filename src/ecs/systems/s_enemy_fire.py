import esper
from src.create.prefab_creator import create_enemy_bullet
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from random import randrange


def system_enemy_fire(world: esper.World, bullet_info: dict):
    components_enemy = world.get_components(CSurface, CTransform, CTagEnemy)
    c_s: CSurface
    c_t: CTransform
    for _, (c_s, c_t, _) in components_enemy:
        shoot = randrange(1000)
        if shoot == 77:
            create_enemy_bullet(world, c_t.pos, c_s.area.size, bullet_info)