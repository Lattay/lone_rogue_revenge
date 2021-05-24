from pygame.sprite import groupcollide
from utils import dist2, Actor


def collide_circle(a, b):
    return a != b and (a.radius + b.radius) ** 2 > dist2(a.pos, b.pos)


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
                    collided=collide_circle,
                )
            )

        for t in c:
            Actor.send_to(t, "hit")
