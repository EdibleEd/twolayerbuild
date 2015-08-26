# -*- coding: utf-8 -*-
"""
@author: Kotarou
"""

from entity import System
from util import Vector
from components.CollisionComponent import CollisionComponent
from components.MeshComponent import MeshComponent
import time
import numpy as np
import math

class CollisionSystem(System):

    def __init__(self):
        super().__init__()

    def update(self, _):
        # First, update for changes in SVA
        for e, c in self.eman.pairsForType(CollisionComponent):
            if c.AABB:
                self.newAABB(c, e)

        for e0, c0 in self.eman.pairsForType(CollisionComponent):
            if c0.active:
                for e1, c1 in self.eman.pairsForType(CollisionComponent):
                    if e0 is not e1 and c1.active:
                        if c0.AABB and c1.AABB:
                            bCollides = self.collidesWithAABB(c0, c1)
                            #bCollides = self.collidesWithTriangles(c0, c1)
                        else:
                            # Triangle intersections, baby!
                            bCollides = self.collidesWithTriangles(c0, c1)
                        if bCollides:
                            print(e0, " collides with ", e1)
                            print(int(round(time.time() * 1000)))

    def newAABB(self, obj, owner):
        obj.tl = Vector(99999, -9999, -999999)
        obj.br = Vector(-99999, 9999, 999999)
        for mesh in owner.getComponentsByType(MeshComponent):
            for triangle in mesh.triangles:
                for vertex in triangle:
                    obj.tl.x = min(vertex[0], obj.tl.x)
                    obj.tl.y = max(vertex[1], obj.tl.y)
                    obj.tl.z = max(vertex[2], obj.tl.z)

                    obj.br.x = max(vertex[0], obj.br.x)
                    obj.br.y = min(vertex[1], obj.br.y)
                    obj.br.z = min(vertex[2], obj.br.z)

    def collidesWithAABB(self, obj1, obj2):
        x = (obj1.br.x >= obj2.tl.x and obj1.tl.x<= obj2.br.x)
        y = (obj1.tl.y >= obj2.br.y and obj1.br.y<= obj2.tl.y)
        z = (obj1.tl.z >= obj2.br.z and obj1.br.z<= obj2.tl.z)
        return x and y and z

    def collidesWithTriangles(self, obj1, obj2):
        #raise Exception("Triangle - triangle collsions are not currently supported")
        tri0 = obj1.owner.getSingleComponentByType(MeshComponent).triangles
        tri1 = obj2.owner.getSingleComponentByType(MeshComponent).triangles
        #print(tri0)
        for t0 in tri0:
            for t1 in tri1:
                if self.ttCollision(t0, t1):
                    return True
        return False

    def pointInTriangle(self, a, b, c, q):
        # This assumes the point p is coplanar with the triangle (a,b,c)
        u = b - a
        v = c - a
        w = q - a

        vcw = np.cross(v, w)
        vcu = np.cross(v, u)

        # Sign of r
        if vcw.dot(vcu) < 0:
            return False

        ucw = np.cross(u, w)
        ucv = np.cross(u, v)

        # Sign of t
        if ucw.dot(ucv) < 0:
            return False

        # Both r and t > 0.
        # Given this, as long as their sum <= 1, both are <= 1

        denom = np.sqrt(ucv.dot(ucv))
        r = np.sqrt(vcw.dot(vcw)) / denom
        t = np.sqrt(ucw.dot(ucw)) / denom

        return r + t <= 1

    def normalize(self, a):
        l = np.sqrt(a.dot(a))
        return a / l

    def ttCollision(self, t0, t1):
        # TODO: Make this use my vectors eventually
        # TODO: Make this check edges rather than just verticies
        # TODO: Remove coplanar assumption

        # Assume that component triangles are sufficiently large compared to their velocities
        # Thus, for any triangle-triangle intersection
        # A vertex wil always intersect before an edge will
        # Note that this only works for coplaner objects

        # The verticies of triangle0
        p00 = np.array(t0[0])
        p01 = np.array(t0[1])
        p02 = np.array(t0[2])
        # The verticies of triangle1
        p10 = np.array(t1[0])
        p11 = np.array(t1[1])
        p12 = np.array(t1[2])

        # Do any of triangle1's verticies intersect triangle0?
        a = self.pointInTriangle(p00, p01, p02, p10)
        b = self.pointInTriangle(p00, p01, p02, p11)
        c = self.pointInTriangle(p00, p01, p02, p12)
        # Do any of triangle0's verticies intersect triangle1?
        d = self.pointInTriangle(p10, p11, p12, p00)
        e = self.pointInTriangle(p10, p11, p12, p01)
        f = self.pointInTriangle(p10, p11, p12, p02)

        return a or b or c or d or e or f
