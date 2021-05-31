from pygame.sprite import groupcollide
from utils import dist2
from enemies import Shield


def collide(a, b):
    if a == b:
        return False
    if isinstance(b, Shield):
        return b.collides(a)
    elif isinstance(a, Shield):
        return a.collides(b)
    else:
        return dist2(a.pos, b.pos) < (a.radius + b.radius)**2


class CollisionHandler:
    def __init__(self, target, *groups):
        self.target = target
        self.groups = groups

    def handle_collisions(self):
        c = {}
        for g in self.groups:
            c.update(
                groupcollide(
                    self.target,
                    g,
                    False,
                    False,
                    collided=collide,
                )
            )

        for t in c:
            first, *_ = c[t]
            first.send(t, "hit")
