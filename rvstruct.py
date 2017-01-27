import struct

class World:
    def __init__(self):

        self.mesh_count = 0
        self.meshes = []

        self.bigcube_count =0
        self.bigcubes = []

        self.animation_count = 0
        self.animations = []

        self.env_list = None

    def read(self, fh):

        # Read the mesh count (one rvlong)
        self.mesh_count = struct.unpack("=l", fh.read(4))[0]

        # Read the meshes
        for mesh in range(self.mesh_count):
            self.meshes.append(Mesh(fh))
        

    def __str__(self):
        return ("Mesh count: {}\n"
                "Meshes:\n{}\n"
               ).format(self.mesh_count, *[str(mesh) for mesh in self.meshes])

# Meshes found in .w files
class Mesh:
    def __init__(self, fh = None):

        self.bound_ball_center = None
        self.bound_ball_radius = 0

        self.bbox = None

        self.polygon_count = 0
        self.vertex_count = 0

        self.polygons = []
        self.vertices = []

        if fh:
            self.read(fh)

    def read(self, fh):
        
        self.bound_ball_center = Vector(fh)
        self.bound_ball_radius = struct.unpack("=f", fh.read(4))[0]
        self.bbox = BoundingBox(fh)

    def __str__(self):
        return ("Bounding Ball Center: {}\n"
                "Bounding Ball Radius: {}\n"
                "Bounding Box:\n{}"
               ).format(self.bound_ball_center,
                        self.bound_ball_radius,
                        self.bbox)

class BoundingBox:

    bformat = "=ffffff"
    bsize = 24

    def __init__(self, fh = None):
        self.xlo = 0
        self.xhi = 0
        self.ylo = 0
        self.yhi = 0
        self.zlo = 0
        self.zhi = 0

        if fh:
            self.read(fh)

    def read(self, fh):

        # Read 6 rvfloats
        self.xlo, self.xhi, self.ylo, self.yhi, self.zlo, self.zhi = struct.unpack(BoundingBox.bformat, fh.read(BoundingBox.bsize))

    def __str__(self):
        return (
                "xlo {}\n"
                "xhi {}\n"
                "ylo {}\n"
                "yhi {}\n"
                "zlo {}\n"
                "zhi {}\n"
               ).format(self.xlo, self.xhi, self.ylo, self.yhi, self.zlo, self.zhi)

class Vector:

    bformat = "=fff"
    bsize = 12

    def __init__(self, fh=None, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

        if fh:
            self.read(fh)

    def read(self, fh):
        # read rvfloats
        self.x, self.y, self.z = struct.unpack(Vector.bformat, fh.read(Vector.bsize))

    def __str__(self):
        return "({}, {}, {})".format(self.x, self.y, self.z)

testw = World()

fh = open("/home/yethiel/test.w", "rb")
testw.read(fh)
print(testw)

fh.close()