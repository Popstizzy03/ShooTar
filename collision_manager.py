import pygame
import math
from config import *
from effects import Explosion, HitEffect, PowerUpEffect

class CollisionManager:
    def __init__(self, sound_manager=None, ui_manager=None):
        self.sound_manager = sound_manager
        self.ui_manager = ui_manager
        
        # Collision groups
        self.collision_groups = {
            'player': pygame.sprite.Group(),
            'enemies': pygame.sprite.Group(),
            'bosses': pygame.sprite.Group(),
            'player_bullets': pygame.sprite.Group(),
            'enemy_bullets': pygame.sprite.Group(),
            'powerups': pygame.sprite.Group(),
            'effects': pygame.sprite.Group()
        }
        
        # Collision statistics
        self.collision_stats = {
            'player_hits': 0,
            'enemy_hits': 0,
            'boss_hits': 0,
            'powerups_collected': 0,
            'total_damage_dealt': 0,
            'total_damage_taken': 0
        }
        
    def update_groups(self, **groups):
        """Update collision groups with new sprite groups"""
        for group_name, group in groups.items():
            if group_name in self.collision_groups:
                self.collision_groups[group_name] = group
                
    def check_all_collisions(self, player, score_callback=None):
        """Check all collision types and return results"""
        results = {
            'player_damaged': False,
            'enemies_killed': [],
            'bosses_killed': [],
            'powerups_collected': [],
            'effects_to_add': [],
            'score_gained': 0
        }
        
        # Player bullet vs enemies
        enemy_hits = self.check_player_bullets_vs_enemies()
        results['enemies_killed'].extend(enemy_hits['killed'])
        results['effects_to_add'].extend(enemy_hits['effects'])
        results['score_gained'] += enemy_hits['score']
        
        # Player bullet vs bosses
        boss_hits = self.check_player_bullets_vs_bosses()
        results['bosses_killed'].extend(boss_hits['killed'])
        results['effects_to_add'].extend(boss_hits['effects'])
        results['score_gained'] += boss_hits['score']
        
        # Enemy bullets vs player
        player_hit = self.check_enemy_bullets_vs_player(player)
        results['player_damaged'] = player_hit['damaged']
        results['effects_to_add'].extend(player_hit['effects'])
        
        # Enemies vs player
        enemy_collision = self.check_enemies_vs_player(player)
        results['player_damaged'] = results['player_damaged'] or enemy_collision['damaged']
        results['effects_to_add'].extend(enemy_collision['effects'])
        
        # Powerups vs player
        powerup_collection = self.check_powerups_vs_player(player)
        results['powerups_collected'].extend(powerup_collection['collected'])
        results['effects_to_add'].extend(powerup_collection['effects'])
        
        # Update statistics
        self.update_collision_stats(results)
        
        return results
        
    def check_player_bullets_vs_enemies(self):
        """Check collisions between player bullets and enemies"""
        result = {
            'killed': [],
            'effects': [],
            'score': 0
        }
        
        hits = pygame.sprite.groupcollide(
            self.collision_groups['enemies'],
            self.collision_groups['player_bullets'],
            False, True,
            collided=self.advanced_collision_detection
        )
        
        for enemy, bullet_list in hits.items():
            for bullet in bullet_list:
                # Apply damage
                damage = getattr(bullet, 'damage', 1)
                if enemy.damage(damage):
                    # Enemy killed
                    result['killed'].append(enemy)
                    result['score'] += enemy.score_value
                    
                    # Create explosion effect
                    explosion = Explosion(
                        enemy.rect.centerx,
                        enemy.rect.centery,
                        size=40
                    )
                    result['effects'].append(explosion)
                    
                    # Play sound
                    if self.sound_manager:
                        self.sound_manager.play_sound('explosion')
                        
                    # Screen shake
                    if self.ui_manager:
                        self.ui_manager.screen_shake(3, 200)
                        
                else:
                    # Enemy hit but not killed
                    hit_effect = HitEffect(
                        enemy.rect.centerx,
                        enemy.rect.centery,
                        color=WHITE
                    )
                    result['effects'].append(hit_effect)
                    
                    # Play hit sound
                    if self.sound_manager:
                        self.sound_manager.play_sound('hit', volume=0.3)
                        
                # Track damage dealt
                self.collision_stats['total_damage_dealt'] += damage
                
        return result
        
    def check_player_bullets_vs_bosses(self):
        """Check collisions between player bullets and bosses"""
        result = {
            'killed': [],
            'effects': [],
            'score': 0
        }
        
        hits = pygame.sprite.groupcollide(
            self.collision_groups['bosses'],
            self.collision_groups['player_bullets'],
            False, True,
            collided=self.advanced_collision_detection
        )
        
        for boss, bullet_list in hits.items():
            for bullet in bullet_list:
                # Apply damage
                damage = getattr(bullet, 'damage', 1)
                if boss.damage(damage):
                    # Boss killed
                    result['killed'].append(boss)
                    result['score'] += boss.get_score_value()
                    
                    # Create multiple explosion effects
                    for i in range(5):
                        explosion = Explosion(
                            boss.rect.centerx + (i - 2) * 20,
                            boss.rect.centery + (i - 2) * 15,
                            size=60
                        )
                        result['effects'].append(explosion)
                        
                    # Play boss explosion sound
                    if self.sound_manager:
                        self.sound_manager.play_sound('boss_explosion')
                        
                    # Intense screen shake
                    if self.ui_manager:
                        self.ui_manager.screen_shake(8, 500)
                        
                else:
                    # Boss hit but not killed
                    hit_effect = HitEffect(
                        boss.rect.centerx,
                        boss.rect.centery,
                        color=RED
                    )
                    result['effects'].append(hit_effect)
                    
                    # Play boss hit sound
                    if self.sound_manager:
                        self.sound_manager.play_sound('boss_hit', volume=0.5)
                        
                    # Small screen shake
                    if self.ui_manager:
                        self.ui_manager.screen_shake(2, 150)
                        
                # Track damage dealt
                self.collision_stats['total_damage_dealt'] += damage
                
        return result
        
    def check_enemy_bullets_vs_player(self, player):
        """Check collisions between enemy bullets and player"""
        result = {
            'damaged': False,
            'effects': []
        }
        
        hits = pygame.sprite.spritecollide(
            player,
            self.collision_groups['enemy_bullets'],
            True,
            collided=self.advanced_collision_detection
        )
        
        for bullet in hits:
            if not player.shield and not player.protected:
                damage = getattr(bullet, 'damage', 10)
                if player.damage(damage):
                    result['damaged'] = True
                    
                # Create hit effect
                hit_effect = HitEffect(
                    player.rect.centerx,
                    player.rect.centery,
                    color=RED
                )
                result['effects'].append(hit_effect)
                
                # Play hit sound
                if self.sound_manager:
                    self.sound_manager.play_sound('player_hit')
                    
                # Screen shake
                if self.ui_manager:
                    self.ui_manager.screen_shake(5, 300)
                    
                # Track damage taken
                self.collision_stats['total_damage_taken'] += damage
                
        return result
        
    def check_enemies_vs_player(self, player):
        """Check collisions between enemies and player"""
        result = {
            'damaged': False,
            'effects': []
        }
        
        hits = pygame.sprite.spritecollide(
            player,
            self.collision_groups['enemies'],
            True,
            collided=self.advanced_collision_detection
        )
        
        for enemy in hits:
            if not player.shield and not player.protected:
                damage = 25  # Collision damage
                if player.damage(damage):
                    result['damaged'] = True
                    
            # Create explosion effect
            explosion = Explosion(
                enemy.rect.centerx,
                enemy.rect.centery,
                size=35
            )
            result['effects'].append(explosion)
            
            # Play explosion sound
            if self.sound_manager:
                self.sound_manager.play_sound('explosion')
                
            # Screen shake
            if self.ui_manager:
                self.ui_manager.screen_shake(4, 250)
                
            # Track damage taken
            if not player.shield and not player.protected:
                self.collision_stats['total_damage_taken'] += damage
                
        return result
        
    def check_powerups_vs_player(self, player):
        """Check collisions between powerups and player"""
        result = {
            'collected': [],
            'effects': []
        }
        
        hits = pygame.sprite.spritecollide(
            player,
            self.collision_groups['powerups'],
            True,
            collided=self.advanced_collision_detection
        )
        
        for powerup in hits:
            result['collected'].append(powerup)
            
            # Create powerup effect
            powerup_effect = PowerUpEffect(
                powerup.rect.centerx,
                powerup.rect.centery,
                powerup.type
            )
            result['effects'].append(powerup_effect)
            
            # Apply powerup effect to player
            self.apply_powerup_to_player(player, powerup)
            
            # Play powerup sound
            if self.sound_manager:
                self.sound_manager.play_sound('powerup')
                
            # Track collection
            self.collision_stats['powerups_collected'] += 1
            
        return result
        
    def apply_powerup_to_player(self, player, powerup):
        """Apply powerup effects to player"""
        if powerup.type == PowerUpType.SHIELD:
            player.activate_shield(SHIELD_DURATION)
            
        elif powerup.type == PowerUpType.GUN_UPGRADE:
            if player.weapon_type == WeaponType.BASIC:
                player.upgrade_weapon(WeaponType.DOUBLE, GUN_UPGRADE_DURATION)
            elif player.weapon_type == WeaponType.DOUBLE:
                player.upgrade_weapon(WeaponType.TRIPLE, GUN_UPGRADE_DURATION)
            elif player.weapon_type == WeaponType.TRIPLE:
                player.upgrade_weapon(WeaponType.SPREAD, GUN_UPGRADE_DURATION)
            else:
                player.upgrade_weapon(WeaponType.SPREAD, GUN_UPGRADE_DURATION)
                
        elif powerup.type == PowerUpType.HEALTH:
            player.heal(25)
            
        elif powerup.type == PowerUpType.LIFE:
            player.add_life()
            
        elif powerup.type == PowerUpType.SPEED:
            player.speed_boost(1.5, 10000)
            
        elif powerup.type == PowerUpType.RAPID_FIRE:
            player.rapid_fire(8000)
            
        elif powerup.type == PowerUpType.ULTRAKILL:
            # Kill all enemies on screen
            for enemy in self.collision_groups['enemies']:
                explosion = Explosion(
                    enemy.rect.centerx,
                    enemy.rect.centery,
                    size=40
                )
                self.collision_groups['effects'].add(explosion)
                enemy.kill()
                
            # Play ultrakill sound
            if self.sound_manager:
                self.sound_manager.play_sound('ultrakill')
                
            # Big screen shake
            if self.ui_manager:
                self.ui_manager.screen_shake(10, 800)
                
        # Update player stats
        player.powerups_collected += 1
        
    def advanced_collision_detection(self, sprite1, sprite2):
        """More accurate collision detection using masks"""
        try:
            # Try to use mask collision for better accuracy
            if hasattr(sprite1, 'mask') and hasattr(sprite2, 'mask'):
                offset_x = sprite2.rect.x - sprite1.rect.x
                offset_y = sprite2.rect.y - sprite1.rect.y
                return sprite1.mask.overlap(sprite2.mask, (offset_x, offset_y)) is not None
            else:
                # Fallback to rect collision
                return sprite1.rect.colliderect(sprite2.rect)
        except:
            # Emergency fallback
            return sprite1.rect.colliderect(sprite2.rect)
            
    def circular_collision_detection(self, sprite1, sprite2):
        """Circular collision detection for more organic feel"""
        center1 = sprite1.rect.center
        center2 = sprite2.rect.center
        
        # Calculate distance between centers
        distance = math.sqrt(
            (center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2
        )
        
        # Calculate combined radius (average of width and height)
        radius1 = (sprite1.rect.width + sprite1.rect.height) / 4
        radius2 = (sprite2.rect.width + sprite2.rect.height) / 4
        
        return distance < (radius1 + radius2)
        
    def update_collision_stats(self, results):
        """Update collision statistics"""
        self.collision_stats['enemy_hits'] += len(results['enemies_killed'])
        self.collision_stats['boss_hits'] += len(results['bosses_killed'])
        self.collision_stats['powerups_collected'] += len(results['powerups_collected'])
        
        if results['player_damaged']:
            self.collision_stats['player_hits'] += 1
            
    def get_collision_stats(self):
        """Get current collision statistics"""
        return self.collision_stats.copy()
        
    def reset_stats(self):
        """Reset collision statistics"""
        self.collision_stats = {
            'player_hits': 0,
            'enemy_hits': 0,
            'boss_hits': 0,
            'powerups_collected': 0,
            'total_damage_dealt': 0,
            'total_damage_taken': 0
        }
        
    def check_bullet_boundaries(self):
        """Remove bullets that are off-screen"""
        for bullet in self.collision_groups['player_bullets']:
            if (bullet.rect.bottom < 0 or bullet.rect.top > SCREEN_HEIGHT or
                bullet.rect.right < 0 or bullet.rect.left > SCREEN_WIDTH):
                bullet.kill()
                
        for bullet in self.collision_groups['enemy_bullets']:
            if (bullet.rect.bottom < 0 or bullet.rect.top > SCREEN_HEIGHT or
                bullet.rect.right < 0 or bullet.rect.left > SCREEN_WIDTH):
                bullet.kill()
                
    def check_proximity_effects(self, player):
        """Check for proximity-based effects"""
        effects = []
        
        # Check for nearby enemies for tension effects
        nearby_enemies = 0
        for enemy in self.collision_groups['enemies']:
            distance = math.sqrt(
                (enemy.rect.centerx - player.rect.centerx) ** 2 +
                (enemy.rect.centery - player.rect.centery) ** 2
            )
            if distance < 100:  # Within 100 pixels
                nearby_enemies += 1
                
        # Apply tension effects based on nearby enemies
        if nearby_enemies >= 3:
            # High tension - more intense effects
            if self.ui_manager:
                self.ui_manager.screen_shake(1, 50)
                
        return effects
        
    def optimize_collision_detection(self):
        """Optimize collision detection by using spatial partitioning"""
        # Simple spatial partitioning - divide screen into grid
        grid_size = 100
        grid_width = SCREEN_WIDTH // grid_size + 1
        grid_height = SCREEN_HEIGHT // grid_size + 1
        
        # Create grid
        grid = [[[] for _ in range(grid_height)] for _ in range(grid_width)]
        
        # Place sprites in grid
        for group_name, group in self.collision_groups.items():
            for sprite in group:
                grid_x = min(sprite.rect.centerx // grid_size, grid_width - 1)
                grid_y = min(sprite.rect.centery // grid_size, grid_height - 1)
                grid[grid_x][grid_y].append((sprite, group_name))
                
        return grid
        
    def debug_draw_collision_boxes(self, surface):
        """Draw collision boxes for debugging"""
        for group_name, group in self.collision_groups.items():
            color = {
                'player': GREEN,
                'enemies': RED,
                'bosses': PURPLE,
                'player_bullets': BLUE,
                'enemy_bullets': ORANGE,
                'powerups': YELLOW
            }.get(group_name, WHITE)
            
            for sprite in group:
                pygame.draw.rect(surface, color, sprite.rect, 2)
                
        # Draw collision statistics
        font = pygame.font.Font(None, 24)
        stats_text = [
            f"Player Hits: {self.collision_stats['player_hits']}",
            f"Enemy Hits: {self.collision_stats['enemy_hits']}",
            f"Boss Hits: {self.collision_stats['boss_hits']}",
            f"Powerups: {self.collision_stats['powerups_collected']}"
        ]
        
        for i, text in enumerate(stats_text):
            text_surface = font.render(text, True, WHITE)
            surface.blit(text_surface, (10, 200 + i * 25))