import struct

class World:
    def __init__(self):

        self.mesh_count = 0
        self.meshes = []

        self.bigcube_count = 0
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
        return ("====   WORLD   ====\n"
                "Mesh count: {}\n"
                "Meshes:\n{}\n"
                "==== WORLD END ====\n"
               ).format(self.mesh_count, '\n'.join([str(mesh) for mesh in self.meshes]))

# Meshes found in .w files
class Mesh:
    def __init__(self, fh=None):

        self.bound_ball_center = None
        self.bound_ball_radius = None

        self.bbox = None

        self.polygon_count = None
        self.vertex_count = None

        self.polygons = []
        self.vertices = []

        if fh:
            self.read(fh)

    def read(self, fh):
        
        self.bound_ball_center = struct.unpack("=fff", fh.read(12))
        self.bound_ball_radius = struct.unpack("=f", fh.read(4))[0]
        self.bbox = BoundingBox(fh)
        self.polygon_count = struct.unpack("=h", fh.read(2))[0]
        self.vertex_count = struct.unpack("=h", fh.read(2))[0]

        for polygon in range(self.polygon_count):
            self.polygons.append(Polygon(fh))

        for vertex in range(self.vertex_count):
            self.vertices.append(Vertex(fh))

    def __str__(self):
        return ("====   MESH   ====\n"
                "Bounding Ball Center: {}\n"
                "Bounding Ball Radius: {}\n"
                "Bounding Box:\n{}\n"
                "Polygon Count: {}\n"
                "Vertex Count: {}\n"
                "Polygons:\n{}"
                "Vertices:\n{}"
                "==== MESH END ====\n"
               ).format(self.bound_ball_center,
                        self.bound_ball_radius,
                        self.bbox,
                        self.polygon_count,
                        self.vertex_count,
                        '\n'.join([str(polygon) for polygon in self.polygons]),
                        '\n'.join([str(vertex) for vertex in self.vertices]))

class BoundingBox:

    bformat = "=ffffff"
    bsize = 24

    def __init__(self, fh=None):
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

    def __init__(self, fh=None, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

        if fh:
            self.read(fh)

    def read(self, fh):
        # read rvfloats
        vec = struct.unpack("=fff", fh.read(12))
        self.x, self.y, self.z = vec

    def __str__(self):
        return "({}, {}, {})".format(self.x, self.y, self.z)

class Polygon:
    def __init__(self, fh=None):

        self.type = None    # rvshort
        self.texture = None # rvshort

        self.vertex_indices = [] # 4 rvshorts
        self.colors = []    # 4 unsigned rvlongs

        self.uv = []

        if fh:
            self.read(fh)

    def read(self, fh):
        
        self.type = struct.unpack("=h", fh.read(2))
        self.texture = struct.unpack("=h", fh.read(2))

        self.vertex_indices = struct.unpack("=hhhh", fh.read(8))
        self.colors = struct.unpack("=LLLL", fh.read(16))

        for x in range(4):
            self.uv.append(UV(fh))

    def __str__(self):
        return ("====   POLYGON   ====\n"
                "Type: {}\n"
                "Texture: {}\n"
                "Vertex Indices: {}\n"
                "Colors: {}\n"
                "UV: {}\n"
                "==== POLYGON END ====\n"
               ).format(self.type,
                        self.texture,
                        self.vertex_indices,
                        self.colors,
                        '\n'.join([str(uv) for uv in self.uv]))


class Vertex:
    def __init__(self, fh=None):

        self.position = None # Vector
        self.normal = None # Vector (normalized, length 1)

        if fh:
            self.read(fh)

    def read(self, fh):
        self.position = struct.unpack("=fff", fh.read(12))
        self.normal = struct.unpack("=fff", fh.read(12))
        # self.position = Vector(fh)
        # self.normal = Vector(fh)

    def __str__(self):
        return ("====   VERTEX   ====\n"
                "Position: {}\n"
                "Normal: {}\n"
                "==== VERTEX END ====\n"
                ).format(self.position, self.normal)

class UV:
    def __init__(self, fh=None):

        self.u = 0
        self.v = 0

        if fh:
            self.read(fh)

    def read(self, fh):

        self.u = struct.unpack("=f", fh.read(4))
        self.v = struct.unpack("=f", fh.read(4))

    def __str__(self):
        return "({}, {})".format(self.u, self.v)

testw = World()

fh = open("/home/yethiel/Applications/RVGL/levels/muse1/muse1.w", "rb")
testw.read(fh)
print(testw)

fh.close()