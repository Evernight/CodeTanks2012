def process_shooting():
            targets = filter(ALIVE_ENEMY_TANK, world.tanks)

            if not targets:
                return

            def get_target_priority(tank, target):
                health_fraction = tank.crew_health / tank.crew_max_health
                angle_penalty_factor = (1 + (1 - health_fraction) * 1.5 -
                                        (1 - max(0, 150 - tank.remaining_reloading_time)/150) * 1)

                angle_degrees = fabs(tank.get_turret_angle_to_unit(target)) / PI * 180

                distance_penalty = tank.get_distance_to_unit(target) / 10
                angle_penalty = angle_penalty_factor * (angle_degrees**1.2)/2
                # Headshot ^_^
                if ((target.crew_health <= 20 or target.hull_durability <= 20) or
                    (tank.premium_shell_count > 0 and (target.crew_health <= 35 or target.hull_durability <= 35))):
                    finish_bonus = 30
                else:
                    finish_bonus = 0

                if self.physics.attacked_area(tank.x, tank.y, target, cache=self.EA_cache) > 0.5:
                    attacking_me_bonus = 20
                else:
                    attacking_me_bonus = 0

                # Last target priority
                last_target_bonus = 0
                if self.memory.last_turret_target_id:
                    if self.memory.last_turret_target_id == target.id:
                        last_target_bonus = 5

                result = 180 + finish_bonus + attacking_me_bonus + last_target_bonus - distance_penalty - angle_penalty
                self.debug('TARGET [%20s] (x=%8.2f, y=%8.2f, |v|=%8.2f) finish_B=%8.2f, AM_B=%8.2f, LT_B=%8.2f, D_P=%8.2f, A_P=%8.2f, APF=%8.2f, result=%8.2f' %
                           (target.player_name, target.x, target.y, hypot(target.speedX, target.speedY), finish_bonus, attacking_me_bonus, last_target_bonus,
                            distance_penalty, angle_penalty, angle_penalty_factor, result))
                return result

            if self.debug_mode:
                targets = sorted(targets, key=lambda t : t.player_name)
            targets_f = [(t, get_target_priority(tank, t)) for t in targets]

            cur_target = max(targets_f, key=operator.itemgetter(1))[0]
            self.memory.last_turret_target_id = cur_target.id

            est_pos = self.physics.estimate_target_position(cur_target, tank)

            def bonus_attacked():
                for bonus in world.bonuses:
                    if (self.physics.will_hit(tank, bonus, BONUS_FACTOR) and
                        tank.get_distance_to_unit(bonus) < tank.get_distance_to(*est_pos)):
                        return bonus
                return False

            def dead_tank_attacked():
                for obstacle in filter(filter_or(DEAD_TANK, ALLY_TANK(tank.id)), world.tanks):
                    next_position = self.physics.estimate_target_position(obstacle, tank)
                    next_unit = fictive_unit(obstacle, next_position[0], next_position[1])
                    if (self.physics.will_hit(tank, next_unit, DEAD_TANK_OBSTACLE_FACTOR) and
                        tank.get_distance_to_unit(obstacle) < tank.get_distance_to(*est_pos)):
                        return obstacle
                return False

            cur_angle = tank.get_turret_angle_to(*est_pos)
            if self.physics.will_hit(
                tank,
                fictive_unit(cur_target, est_pos[0], est_pos[1]),
                TARGETING_FACTOR
            ):
                if self.health_fraction > 0.8 and self.hull_fraction > 0.5 and tank.get_distance_to_unit(cur_target) > 400 and tank.premium_shell_count <= 2:
                    move.fire_type = FireType.REGULAR
                else:
                    move.fire_type = FireType.PREMIUM_PREFERRED
            else:
                move.fire_type = FireType.NONE

            if bonus_attacked() or dead_tank_attacked():
                self.debug('!!! Obstacle is attacked, don\'t shoot')
                move.fire_type = FireType.NONE

            if world.tick < 10 + tank.teammate_index * 10:
                move.fire_type = FireType.NONE

            if fabs(cur_angle) > PI/180 * 0.5:
                move.turret_turn = sign(cur_angle)