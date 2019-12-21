import re
import math


import logging
logger = logging.getLogger("moon_simulator")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class Moon:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.vx = 0
        self.vy = 0
        self.vz = 0

    def __repr__(self):
        return "pos=<x={: }, y={: }, z={: }>, vel=<x={: }, y={: }, z={: }>".format(
            self.x, self.y, self.z,
            self.vx, self.vy, self.vz
        )

    def pos(self, axis):
        if axis == 0:
            return self.x
        elif axis == 1:
            return self.y
        elif axis == 2:
            return self.z
        else:
            assert axis >= 0 and axis <= 2, "Axis can't be {}".format(axis)

    def set_pos(self, axis, value):
        if axis == 0:
            self.x = value
        elif axis == 1:
            self.y = value
        elif axis == 2:
            self.z = value
        else:
            assert axis >= 0 and axis <= 2, "Axis can't be {}".format(axis)

    def vel(self, axis):
        if axis == 0:
            return self.vx
        elif axis == 1:
            return self.vy
        elif axis == 2:
            return self.vz
        else:
            assert axis >= 0 and axis <= 2, "Axis can't be {}".format(axis)

    def set_vel(self, axis, value):
        if axis == 0:
            self.vx = value
        elif axis == 1:
            self.vy = value
        elif axis == 2:
            self.vz = value
        else:
            assert axis >= 0 and axis <= 2, "Axis can't be {}".format(axis)

    def potential_energy(self):
        e = abs(self.x) + abs(self.y) + abs(self.z)
        logger.debug("pot: {} + {} + {} = {}".format(abs(self.x), abs(self.y), abs(self.z), e))
        return e

    def kinetic_energy(self):
        e = abs(self.vx) + abs(self.vy) + abs(self.vz)
        logger.debug("kin: {} + {} + {} = {}".format(abs(self.vx), abs(self.vy), abs(self.vz), e))
        return e

    def total_energy(self):
        pe = self.potential_energy()
        ke = self.kinetic_energy()
        e = pe * ke
        logger.debug("total: {} * {} = {}".format(pe, ke, e))
        return e


def load_moons(filename):
    moons = []
    with open(filename) as f:
        moon_line = f.readline().strip()
        while moon_line:
            moon = parse_moon(moon_line)
            logger.debug(moon)
            moons.append(moon)
            moon_line = f.readline().strip()
    return moons


def parse_moon(line):
    # <x=-1, y=0, z=2>
    m = re.match(r'<x=(-?\d+), y=(-?\d+), z=(-?\d+)>', line)
    x = int(m.group(1))
    y = int(m.group(2))
    z = int(m.group(3))
    return Moon(x, y, z)


class MoonSimulator:
    def __init__(self, moons):
        self.moons = moons
        self.step_count = 0

    def step(self, do_debug = False):
        self.step_count += 1
        self.apply_gravity()
        self.apply_velocity()
        if do_debug:
            logger.debug("\nAfter {} step(s):".format(self.step_count))
            logger.debug(self)

    def step_axis(self, axis, do_debug = False):
        assert axis >= 0 and axis <= 2
        self.step_count += 1
        self.apply_gravity_axis(axis)
        self.apply_velocity_axis(axis)
        if do_debug:
            logger.debug("\nAfter {} step(s):".format(self.step_count))
            logger.debug(self)

    def apply_gravity(self):
        for i in range(0, len(self.moons) - 1):
            for j in range(i+1, len(self.moons)):
                m1 = self.moons[i]
                m2 = self.moons[j]
                for a in range(0,3):
                    if m1.pos(a) > m2.pos(a):
                        m1.set_vel(a, m1.vel(a) - 1)
                        m2.set_vel(a, m2.vel(a) + 1)
                    elif m1.pos(a) < m2.pos(a):
                        m1.set_vel(a, m1.vel(a) + 1)
                        m2.set_vel(a, m2.vel(a) - 1)

    def apply_velocity(self):
        for m in self.moons:
            for a in range(0,3):
                m.set_pos(a, m.pos(a) + m.vel(a))

    def apply_gravity_axis(self, a):
        assert a >= 0 and a <= 2
        for i in range(0, len(self.moons) - 1):
            for j in range(i+1, len(self.moons)):
                m1 = self.moons[i]
                m2 = self.moons[j]
                if m1.pos(a) > m2.pos(a):
                    m1.set_vel(a, m1.vel(a) - 1)
                    m2.set_vel(a, m2.vel(a) + 1)
                elif m1.pos(a) < m2.pos(a):
                    m1.set_vel(a, m1.vel(a) + 1)
                    m2.set_vel(a, m2.vel(a) - 1)

    def apply_velocity_axis(self, a):
        assert a >= 0 and a <= 2
        for m in self.moons:
            m.set_pos(a, m.pos(a) + m.vel(a))

    def __repr__(self):
        r = ""
        for m in self.moons:
            r += str(m) + "\n"
        return r

    def energy(self):
        logger.debug("\nAfter {} step(s):".format(self.step_count))
        logger.debug(self)
        e = 0
        for m in self.moons:
            me = m.total_energy()
            logger.debug("Energy: {}".format(me))
            e += me
        logger.debug("Total energy: {}".format(e))
        return e

    def reset_steps(self):
        self.step_count = 0

    def axis_key(self, a):
        keys = []
        for m in self.moons:
            keys.append("({},{})".format(m.pos(a), m.vel(a)))
        return ",".join(keys)

    def get_axis_period(self, axis):
        self.reset_steps()
        seen = [self.axis_key(axis)]
        self.step_axis(axis)
        key = self.axis_key(axis)
        while key not in seen:
            self.step_axis(axis)
            key = self.axis_key(axis)
        return self.step_count

    def get_period(self):
        periods = []
        for a in range(0, 3):
            periods.append(self.get_axis_period(a))
        # Lowest common multiple of the three axis periods is the period where all three axis
        # will repeat
        # lcm = (x*y)/gcd(x,y)
        lcm1 = int((periods[0] * periods[1]) / math.gcd(periods[0], periods[1]))
        lcm2 = int((lcm1 * periods[2]) / math.gcd(lcm1, periods[2]))
        return lcm2
