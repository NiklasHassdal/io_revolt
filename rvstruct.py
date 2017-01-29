import struct


class World:
    """
    Reads a .w file and stores all sub-structures
    All contained objects are of a similar structure.
    """
    def __init__(self, fh=None):

        self.mesh_count = 0             # rvlong, amount of Mesh objects
        self.meshes = []                # sequence of Mesh structures

        self.bigcube_count = 0          # rvlong, amount of BigCubes
        self.bigcubes = []              # sequence of BigCubes

        self.animation_count = 0        # rvlong, amount of Texture Animations
        self.animations = []            # sequence of TexAnimation structures

        self.env_count = 0              # amount of faces with env enabled
        self.env_list = None            # an EnvList structure

        # Immediately starts reading it if an opened file is supplied
        if fh:
            self.read(fh)

    def read(self, fh):

        # Reads the mesh count (one rvlong)
        self.mesh_count = struct.unpack("<l", fh.read(4))[0]

        # Reads the meshes
        for mesh in range(self.mesh_count):
            self.meshes.append(Mesh(fh, self))

        # Reads the amount of bigcubes
        self.bigcube_count = struct.unpack("<l", fh.read(4))[0]

        # Reads all BigCubes
        for bcube in range(self.bigcube_count):
            self.bigcubes.append(BigCube(fh))

        # Reads texture animation count
        self.animation_count = struct.unpack("<l", fh.read(4))[0]

        # Reads all animations
        for anim in range(self.animation_count):
            self.animations.append(TexAnimation(fh))

        # Reads the environment colors
        self.env_list = EnvList(fh, self)
        
    # Uses the to-string for dumping the whole .w structure
    def __str__(self):
        return ("====   WORLD   ====\n"
                "Mesh count: {}\n"
                "Meshes:\n{}\n"
                "BigCube count: {}\n"
                "BigCubes:\n{}\n"
                "Animation Count: {}\n"
                "Animations:\n{}\n"
                "ENV Count: {}\n"
                "EnvList:\n{}\n"
                "==== WORLD END ====\n"
               ).format(self.mesh_count, 
               '\n'.join([str(mesh) for mesh in self.meshes]),
               self.bigcube_count,
               '\n'.join([str(bcube) for bcube in self.bigcubes]),
               self.animation_count,
               '\n'.join([str(anim) for anim in self.animations]),
               self.env_count,
               self.env_list)


class Mesh:
    """
    Reads the Meshes found in .w files from an opened file
    These are different from PRM meshes since they also contain
    bounding boxes.
    """
    def __init__(self, fh=None, w=None):
        self.w = w                      # World it belongs to

        self.bound_ball_center = None   # Vector
        self.bound_ball_radius = None   # rvfloat

        self.bbox = None                # BoundingBox

        self.polygon_count = None       # rvlong
        self.vertex_count = None        # rvlong

        self.polygons = []              # Sequence of Polygon objects
        self.vertices = []              # Sequence of Vertex objects

        if fh:
            self.read(fh)

    def read(self, fh):
        
        # Reads bounding "ball" center and the radius
        self.bound_ball_center = Vector(fh)
        self.bound_ball_radius = struct.unpack("<f", fh.read(4))[0]

        self.bbox = BoundingBox(fh)

        # Reads amount of polygons/vertices and the structures themselves
        self.polygon_count = struct.unpack("<h", fh.read(2))[0]
        self.vertex_count = struct.unpack("<h", fh.read(2))[0]

        # Also give the polygon a reference to w so it can report if env is on
        for polygon in range(self.polygon_count):
            self.polygons.append(Polygon(fh, self.w))

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
    """
    Reads and stores bounding boxes found in .w meshes
    They are probably used for culling optimization, similar to BigCube
    """
    def __init__(self, fh=None):
        # Lower and higher boundaries for each axis
        self.xlo = 0
        self.xhi = 0
        self.ylo = 0
        self.yhi = 0
        self.zlo = 0
        self.zhi = 0

        if fh:
            self.read(fh)

    def read(self, fh):
        # Reads boundaries
        self.xlo, self.xhi = struct.unpack("<ff", fh.read(8))
        self.ylo, self.yhi = struct.unpack("<ff", fh.read(8))
        self.zlo, self.zhi = struct.unpack("<ff", fh.read(8))

    def __str__(self):
        return (
                "xlo {}\n"
                "xhi {}\n"
                "ylo {}\n"
                "yhi {}\n"
                "zlo {}\n"
                "zhi {}\n"
               ).format(self.xlo, self.xhi, self.ylo, 
                        self.yhi, self.zlo, self.zhi)

    def __iter__(self):
        return [self.xlo, self.xhi, self.ylo, self.yhi, self.zlo, self.zhi]

class Vector:
    """
    A very simple vector class
    """
    def __init__(self, fh=None, x=0, y=0, z=0):
        self.x = x    # rvfloat
        self.y = y    # rvfloat
        self.z = z    # rvfloat

        if fh:
            self.read(fh)

    def read(self, fh):
        # Reads the coordinates
        vec = struct.unpack("<fff", fh.read(12))
        self.x, self.y, self.z = vec

    def __iter__(self):
        return (x, y, z)


    def __str__(self):
        return "({}, {}, {})".format(self.x, self.y, self.z)

class Polygon:
    """
    Reads a Polygon structure and stores it
    """
    def __init__(self, fh=None, w=None):
        self.w = w                  # World it belongs to

        self.type = None            # rvshort
        self.texture = None         # rvshort

        self.vertex_indices = []    # 4 rvshorts
        self.colors = []            # 4 unsigned rvlongs

        self.uv = []                # UV structures (4)

        if fh:
            self.read(fh)

    def read(self, fh):
        # Reads the type bitfield and the texture index
        self.type = struct.unpack("<h", fh.read(2))[0]
        self.texture = struct.unpack("<h", fh.read(2))[0]

        # Reads indices of the polygon's vertices and their vertex colors
        self.vertex_indices = struct.unpack("<hhhh", fh.read(8))
        self.colors = struct.unpack("<LLLL", fh.read(16))

        # Reads the UV mapping
        for x in range(4):
            self.uv.append(UV(fh))

        # Tells the .w if bit 11 (environment map) is enabled for this
        if self.w:
            if self.type & 2048: 
                self.w.env_count += 1
                print(self.type)

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
    """
    Reads a Polygon structure and stores it
    """
    def __init__(self, fh=None):
        self.position = None    # Vector
        self.normal = None      # Vector (normalized, length 1)

        if fh:
            self.read(fh)

    def read(self, fh):
        # Stores position and normal as a vector
        self.position = Vector(fh)
        self.normal = Vector(fh)

    def __str__(self):
        return ("====   VERTEX   ====\n"
                "Position: {}\n"
                "Normal: {}\n"
                "==== VERTEX END ====\n"
                ).format(self.position, self.normal)

class UV:
    """
    Reads UV-map structure and stores it
    """
    def __init__(self, fh=None):
        self.u = 0      # rvfloat
        self.v = 0      # rvfloat

        if fh:
            self.read(fh)

    def read(self, fh):
        # Read the uv coordinates
        self.u = struct.unpack("<f", fh.read(4))[0]
        self.v = struct.unpack("<f", fh.read(4))[0]

    def __iter__(self):
        return (x, y)

    def __str__(self):
        return "({}, {})".format(self.u, self.v)

class BigCube:
    """
    Reads a BigCube structure and stores it
    BigCubes are used for in-game optimization (culling)
    """
    def __init__(self, fh=None):
        self.center = None      # center/position of the cube, Vector
        self.size = 0           # rvfloat, size of the cube

        self.mesh_count = 0     # rvlong, amount of meshes
        self.mesh_indices = []  # indices of meshes that belong to the cube

        if fh:
            self.read(fh)

    def read(self, fh):
        # Reads center and size of the cube
        self.center = Vector(fh)
        self.size = struct.unpack("<f", fh.read(4))[0]

        # Reads amount of meshes and then the indices of the meshes
        self.mesh_count = struct.unpack("<l", fh.read(4))[0]
        for mesh in range(self.mesh_count):
            self.mesh_indices.append(struct.unpack("<l", fh.read(4))[0])

    def __str__(self):
        return ("====   BIGCUBE   ====\n"
                "Center: {}\n"
                "Size: {}\n"
                "Mesh Count: {}\n"
                "Mesh Indices: {}\n"
                "==== BIGCUBE END ====\n"
                ).format(self.center,
                         self.size,
                         self.mesh_count,
                         self.mesh_indices)


class TexAnimation:
    """
    Reads and stores a texture animation of a .w file
    """
    def __init__(self, fh=None):

        self.frame_count = 0    # rvlong, amount of frames
        self.frames = []        # Frame objects

        if fh:
            self.read(fh)

    def read(self, fh):
        # Reads the amount of frames
        self.frame_count = struct.unpack("<l", fh.read(4))[0]

        # Reads the frames themselves
        for frame in range(self.frame_count):
            self.frames.append(Frame(fh))

    def __str__(self):
        return ("====   ANIMATION   ====\n"
                "Frame Count: {}\n"
                "Frames\n{}"
                "==== ANIMATION END ====\n"
                ).format(self.frame_count,
                         '\n'.join([str(frame) for frame in self.frames]))

class Frame:
    """
    Reads and stores exactly one texture animation frame
    """
    def __init__(self, fh=None):

        self.texture = 0    # texture id of the animated texture
        self.delay = 0      # delay in milliseconds
        self.uv = []        # list of 4 UV coordinates

        if fh:
            self.read(fh)

    def read(self, fh):
        # Reads the texture id
        self.texture = struct.unpack("<l", fh.read(4))[0]
        # Reads the delay
        self.delay = struct.unpack("<f", fh.read(4))[0]

        # Reads the UV coordinates for this frame
        for uv in range(4):
            self.uv.append(UV(fh))

    def __str__(self):
        return ("====   FRAME   ====\n"
                "Texture: {}\n"
                "Delay: {}\n"
                "UV:\n{}\n"
                "==== FRAME END ====\n"
                ).format(self.texture,
                         self.delay,
                         '\n'.join([str(uv) for uv in self.uv]))

class EnvList:
    """
    Reads and stores the list of environment vertex colors of a .w file
    """
    def __init__(self, fh=None, w=None):
        self.w = w              # World it belongs to

        # list with length of the number of bit-11 polys
        self.env_colors = []    # unsigned rvlongs

        if fh:
            self.read(fh)

    def read(self, fh):
        # Reads the colors times the amount of env-enabled polygons
        for col in range(self.w.env_count):
            self.env_colors.append(struct.unpack("<L", fh.read(4))[0])

    def __iter__(self):
        return self.env_colors

    def __str__(self):
        return str(self.env_colors)


# Test
testw = World()

fh = open("/home/yethiel/Applications/RVGL/levels/muse2/muse2.w", "rb")
testw.read(fh)
print(testw)

fh.close()

