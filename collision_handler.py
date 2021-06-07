from pygame.sprite import groupcollide
from utils import dist2
from enemies import Shield


def collide(a, b):
    if a == b:
        return False
    c = dist2(a.pos, b.pos) < (a.radius + b.radius)**2
    if c:
        if isinstance(b, Shield):
            return b.collides(a)
        elif isinstance(a, Shield):
            return a.collides(b)
        else:
            return True
    else:
        return False


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

        all_collided = set()
        for t, collection in c.items():
            first, *_ = collection
            first.send(t, "hit")
            for o in set(collection).difference(all_collided):
                t.send(o, "hit")
            all_collided.update(collection)
