import esper
from src.create.prefab_creator import create_player_explosion
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_enemy_bullet import CTagEnemyBullet
from src.ecs.components.tags.c_tag_player import CTagPlayer


def system_collision_player_bullet(world: esper.World, player_entity: int, explosion_info: dict):
    components_bullet = world.get_components(CSurface, CTransform, CTagEnemyBullet)
    pl_t = world.component_for_entity(player_entity, CTransform)
    pl_s = world.component_for_entity(player_entity, CSurface)
    pl_tag = world.component_for_entity(player_entity, CTagPlayer)
    pl_rect = CSurface.get_area_relative(pl_s.area, pl_t.pos)

    for bullet_entity, (c_s, c_t, _) in components_bullet:
        bullet_rect = CSurface.get_area_relative(c_s.area, c_t.pos)
        if bullet_rect.colliderect(pl_rect):
            world.delete_entity(bullet_entity)
            pl_tag.dead = True
            create_player_explosion(world, pl_t.pos, pl_s.area.size, explosion_info)
