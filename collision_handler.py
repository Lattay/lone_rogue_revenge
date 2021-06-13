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
        a = {
            e for e in self.target
            if e.on_screen()
        }
        b = set()
        for g in self.groups:
            b.update({
                e for e in g
                if e.on_screen()
            })

        all_collided = set()
        for t in a:
            colliding = {
                e for e in b
                if collide(t, e)
            }

            if colliding:
                for o in colliding.difference(all_collided):
                    t.send(o, "hit")

                first, *_ = colliding
                first.send(t, "hit")
                all_collided.update(colliding)
                all_collided.add(t)
