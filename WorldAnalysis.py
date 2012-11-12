from collections import defaultdict
import pickle
from Geometry import Vector

class PhysicsAnalyser:
    def __init__(self, enabled):
        self.shell_velocity = defaultdict(list)
        self.last_target_time_init_values = None
        self.targets = []
        self.enabled = enabled

    def store_shell_velocity(self, world):
        if not self.enabled:
            return
        for shell in world.shells:
            self.shell_velocity[shell.id].append(Vector(shell.speedX, shell.speedY).length())
        if world.tick % 100 == 0:
            pickle.dump(self.shell_velocity, open('shells.dump', 'wb'))

    def save_target_init_values(self, tank, x, y):
        if not self.enabled:
            return

        dist = tank.get_distance_to(x, y)
        vt = Vector(tank.speedX, tank.speedY)

        tank_v = Vector(tank.x, tank.y)
        pt_v = Vector(x, y)
        d = pt_v - tank_v

        tank_d_v = Vector(1, 0).rotate(tank.angle)

        if vt.is_zero():
            vd_angle = 0
        else:
            vd_angle = vt.angle(d)

        if d.is_zero():
            self.last_target_time_init_values = (0, 0, 0, 0, 0, 0)

        self.last_target_time_init_values = (
            tank_d_v.angle(d),
            dist,
            vd_angle,
            vt.length(),
            tank.angular_speed,
            tank.crew_health/tank.crew_max_health
        )