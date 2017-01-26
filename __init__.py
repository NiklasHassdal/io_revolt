bl_info = {
    "name": "Re-Volt Import/Export",
    "author": "Niklas Hassdal",
    "version": (1, 0, 0),
    "blender": (2, 76, 0),
    "location": "File > Import-Export",
    "description": "This plugin will let you import/export models, levels and some other things used in the game Re-Volt.",
    "category": "Import-Export",
}

if "bpy" in locals():
    import importlib
    if "decode" in locals():
        importlib.reload(decode)
    if "encode" in locals():
        importlib.reload(encode)

import bpy, bmesh, struct
from bpy.props import *
from bpy_extras.io_utils import ImportHelper, ExportHelper, axis_conversion
from . import panels
from mathutils import Matrix

class IMPORT_MESH_OT_revolt_model(bpy.types.Operator, ImportHelper):
    bl_idname = "import_mesh.revolt_model"
    bl_label = "Import Re-Volt model"
    bl_options = {'UNDO'}

    filename_ext = ".prm"
    filter_glob = StringProperty(default="*.prm;*.m", options={'HIDDEN'})
    
    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    up_axis = EnumProperty(default = "-Y", name = "Up axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    forward_axis = EnumProperty(default = "Z", name = "Forward axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    
    def execute(self, context):
        from . import decode
        decode.import_model(self.properties.filepath, axis_conversion(to_up = self.up_axis, to_forward = self.forward_axis).to_4x4() * self.scale)
        return {'FINISHED'}

class IMPORT_SCENE_OT_revolt_world(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.revolt_world"
    bl_label = "Import Re-Volt world"
    bl_options = {'UNDO'}

    filename_ext = ".w"
    filter_glob = StringProperty(default="*.w", options={'HIDDEN'})
    
    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    up_axis = EnumProperty(default = "-Y", name = "Up axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    forward_axis = EnumProperty(default = "Z", name = "Forward axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    include_models = BoolProperty(default = True, name = "Include objects")
    include_objects = BoolProperty(default = True, name = "Include pickups")
    include_hitboxes = BoolProperty(default = True, name = "Include hitboxes")
    hide_hitboxes = BoolProperty(default = True, name = "Hide hitboxes")
    
    def draw(self, context):
        self.layout.prop(self, "scale")
        self.layout.prop(self, "up_axis")
        self.layout.prop(self, "forward_axis")
        self.layout.prop(self, "include_models")
        self.layout.prop(self, "include_objects")
        self.layout.prop(self, "include_hitboxes")
        if self.include_hitboxes:
            self.layout.prop(self, "hide_hitboxes")
    
    def execute(self, context):
        from . import decode
        decode.import_world(self.properties.filepath, axis_conversion(to_up = self.up_axis, to_forward = self.forward_axis).to_4x4() * self.scale, self.include_objects, self.include_models, self.include_hitboxes, self.hide_hitboxes)
        context.scene.revolt_world.scale = self.scale
        context.scene.revolt_world.up_axis = self.up_axis
        context.scene.revolt_world.forward_axis = self.forward_axis
        return {'FINISHED'}
        
class IMPORT_MESH_OT_revolt_hitbox(bpy.types.Operator, ImportHelper):
    bl_idname = "import_mesh.revolt_hitbox"
    bl_label = "Import Re-Volt hitbox"
    bl_options = {'UNDO'}

    filename_ext = ".ncp"
    filter_glob = StringProperty(default="*.ncp", options={'HIDDEN'})
    
    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    up_axis = EnumProperty(default = "-Y", name = "Up axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    forward_axis = EnumProperty(default = "Z", name = "Forward axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    
    def execute(self, context):
        from . import decode
        decode.import_hitbox(self.properties.filepath, axis_conversion(to_up = self.up_axis, to_forward = self.forward_axis).to_4x4() * self.scale)
        return {'FINISHED'}

class IMPORT_SCENE_OT_revolt_car(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.revolt_car"
    bl_label = "Import Re-Volt car"
    bl_options = {'UNDO'}

    filename_ext = "Parameters.txt"
    filter_glob = StringProperty(default="Parameters.txt", options={'HIDDEN'})
    
    scale = FloatProperty(default=0.1, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    up_axis = EnumProperty(default = "-Y", name = "Up axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    forward_axis = EnumProperty(default = "Z", name = "Forward axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    
    def execute(self, context):
        from . import decode
        decode.import_car(self.properties.filepath, axis_conversion(to_up = self.up_axis, to_forward = self.forward_axis).to_4x4() * self.scale)
        return {'FINISHED'}

class EXPORT_MESH_OT_revolt_model(bpy.types.Operator, ExportHelper):
    bl_idname = "export_mesh.revolt_model"
    bl_label = "Export Re-Volt model"
    bl_options = {'UNDO'}

    filename_ext = ".prm"
    filter_glob = StringProperty(default="*.prm;*.m", options={'HIDDEN'})
    
    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    up_axis = EnumProperty(default = "-Y", name = "Up axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    forward_axis = EnumProperty(default = "Z", name = "Forward axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    include_texture = BoolProperty(default=True, name = "Include texture")
    
    def execute(self, context):
        from . import encode
        encode.export_model(self.properties.filepath, axis_conversion(from_up = self.up_axis, from_forward = self.forward_axis).to_4x4() * (1 / self.scale), self.include_texture)
        return {'FINISHED'}

class EXPORT_SCENE_OT_revolt_world(bpy.types.Operator, ImportHelper):
    bl_idname = "export_scene.revolt_world"
    bl_label = "Export Re-Volt world"
    bl_options = {'UNDO'}

    filename_ext = ".w"
    filter_glob = StringProperty(default="*.w", options={'HIDDEN'})
    
    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    up_axis = EnumProperty(default = "-Y", name = "Up axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    forward_axis = EnumProperty(default = "Z", name = "Forward axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    
    def execute(self, context):
        from . import encode
        encode.export_world(self.properties.filepath, axis_conversion(from_up = self.up_axis, from_forward = self.forward_axis).to_4x4() * (1 / self.scale))
        return {'FINISHED'}
        
class EXPORT_MESH_OT_revolt_hitbox(bpy.types.Operator, ImportHelper):
    bl_idname = "export_mesh.revolt_hitbox"
    bl_label = "Export Re-Volt hitbox"
    bl_options = {'UNDO'}

    filename_ext = ".ncp"
    filter_glob = StringProperty(default="*.ncp", options={'HIDDEN'})
    
    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    up_axis = EnumProperty(default = "-Y", name = "Up axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    forward_axis = EnumProperty(default = "Z", name = "Forward axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    
    def execute(self, context):
        from . import encode
        encode.export_hitbox(self.properties.filepath, axis_conversion(from_up = self.up_axis, from_forward = self.forward_axis).to_4x4() * (1 / self.scale))
        return {'FINISHED'}

class EXPORT_MESH_OT_revolt_convex_hull(bpy.types.Operator, ImportHelper):
    bl_idname = "export_mesh.convex_hull"
    bl_label = "Export Re-Volt convex hull"
    bl_options = {'UNDO'}

    filename_ext = ".hul"
    filter_glob = StringProperty(default="*.hul", options={'HIDDEN'})
    
    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    up_axis = EnumProperty(default = "-Y", name = "Up axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    forward_axis = EnumProperty(default = "Z", name = "Forward axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    
    def execute(self, context):
        from . import encode
        encode.export_convex_hull(self.properties.filepath, axis_conversion(from_up = self.up_axis, from_forward = self.forward_axis).to_4x4() * (1 / self.scale))
        return {'FINISHED'}

class INFO_MT_revolt_add(bpy.types.Menu):
    bl_idname = "INFO_MT_revolt_add"
    bl_label = "Re-Volt"
    
    def draw(self, context):
        self.layout.operator("object.add_revolt_startpos")

class OBJECT_OT_add_revolt_startpos(bpy.types.Operator):
    bl_idname = "object.add_revolt_startpos"
    bl_label = "Re-Volt start position"
    bl_options = {'UNDO'}
    
    matrix = FloatVectorProperty(subtype = "MATRIX", size = 16, default = (0.01, 0, 0, 0, 0, 0, -0.01, 0, 0, 0.01, 0, 0, 0, 0, 0, 0.01))
    
    def execute(self, context):
        from . import decode
        obj = decode.add_revolt_startpos(self.matrix)
        obj.location = bpy.context.scene.cursor_location
        obj.select = True
        bpy.context.scene.objects.active = obj
        return {'FINISHED'}
        
def menu_func_import(self, context):
    self.layout.operator(IMPORT_MESH_OT_revolt_model.bl_idname, text="Re-Volt model (.prm/.m)")
    self.layout.operator(IMPORT_SCENE_OT_revolt_world.bl_idname, text="Re-Volt world (.w)")
    self.layout.operator(IMPORT_MESH_OT_revolt_hitbox.bl_idname, text="Re-Volt hitbox (.ncp)")
    self.layout.operator(IMPORT_SCENE_OT_revolt_car.bl_idname, text="Re-Volt car (Parameters.txt)")

def menu_func_export(self, context):
    self.layout.operator(EXPORT_MESH_OT_revolt_model.bl_idname, text="Re-Volt model (.prm/.m)")
    self.layout.operator(EXPORT_SCENE_OT_revolt_world.bl_idname, text="Re-Volt world (.w)")
    self.layout.operator(EXPORT_MESH_OT_revolt_hitbox.bl_idname, text="Re-Volt hitbox (.ncp)")
    self.layout.operator(EXPORT_MESH_OT_revolt_convex_hull.bl_idname, text="Re-Volt convex hull (.hul)")

def menu_func_add(self, context):
    self.layout.separator()
    self.layout.menu(INFO_MT_revolt_add.bl_idname, icon = "GAME")

def limit_farclip(self, context):
    if self.farclip < self.fogstart:
        self.farclip = self.fogstart

def limit_fogstart(self, context):
    if self.farclip < self.fogstart:
        self.fogstart = self.farclip

class RevoltWorldProperties(bpy.types.PropertyGroup):
    path = StringProperty(name = "Path", subtype = "DIR_PATH")
    name = StringProperty(name = "Name")
    startpos_object = StringProperty(name = "Start position")
    farclip = FloatProperty(name = "Farclip", update = limit_fogstart, min = 0, step = 100)
    fogstart = FloatProperty(name = "Fogstart", update = limit_farclip, min = 0, step = 100)
    fogcolor = FloatVectorProperty(name = "Fogcolor", subtype = "COLOR")
    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    up_axis = EnumProperty(default = "-Y", name = "Up axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    forward_axis = EnumProperty(default = "Z", name = "Forward axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    position_node_start = StringProperty()

class RevoltWheelProperties(bpy.types.PropertyGroup):
    object = StringProperty(name = "Object")
    is_present = BoolProperty(name = "Present", default = True)
    is_powered = BoolProperty(name = "Powered")
    is_turnable = BoolProperty(name = "Turnable")
    steer_ratio = FloatProperty(name = "Steer ratio")
    engine_ratio = FloatProperty(name = "Engine ratio")

class RevoltCarProperties(bpy.types.PropertyGroup):
    path = StringProperty(name = "Path", subtype = "DIR_PATH")
    name = StringProperty(name = "Car name")
    engine_class = EnumProperty(name = "Engine class", items = [("0", "Electric", "Electric"), ("1", "Glow", "Glow"), ("2", "Other", "Other")])
    steer_rate = FloatProperty(name = "Steer rate", default = 3)
    body_object = StringProperty(name = "Body object")
    wheel0 = PointerProperty(type = RevoltWheelProperties)
    wheel1 = PointerProperty(type = RevoltWheelProperties)
    wheel2 = PointerProperty(type = RevoltWheelProperties)
    wheel3 = PointerProperty(type = RevoltWheelProperties)
    current_wheel = EnumProperty(items = [("0", "0", "0"), ("1", "1", "1"), ("2", "2", "2"), ("3", "3", "3")])

materials = [
    ("MATERIAL_NONE", "None", "None", "", -1),
    ("MATERIAL_DEFAULT", "Default", "None", "", 0),
    ("MATERIAL_MARBLE", "Marble", "None", "", 1),
    ("MATERIAL_STONE", "Stone", "None", "", 2),
    ("MATERIAL_WOOD", "Wood", "None", "", 3),
    ("MATERIAL_SAND", "Sand", "None", "", 4),
    ("MATERIAL_PLASTIC", "Plastic", "None", "", 5),
    ("MATERIAL_CARPETTILE", "Carpet tile", "None", "", 6),
    ("MATERIAL_CARPETSHAG", "Carpet shag", "None", "", 7),
    ("MATERIAL_BOUNDARY", "Boundary", "None", "", 8),
    ("MATERIAL_GLASS", "Glass", "None", "", 9),
    ("MATERIAL_ICE1", "Ice 1", "None", "", 10),
    ("MATERIAL_METAL", "Metal", "None", "", 11),
    ("MATERIAL_GRASS", "Grass", "None", "", 12),
    ("MATERIAL_BUMPMETAL", "Bump metal", "None", "", 13),
    ("MATERIAL_PEBBLES", "Pebbles", "None", "", 14),
    ("MATERIAL_GRAVEL", "Gravel", "None", "", 15),
    ("MATERIAL_CONVEYOR1", "Conveyor 1", "None", "", 16),
    ("MATERIAL_CONVEYOR2", "Conveyor 2", "None", "", 17),
    ("MATERIAL_DIRT1", "Dirt 1", "None", "", 18),
    ("MATERIAL_DIRT2", "Dirt 2", "None", "", 19),
    ("MATERIAL_DIRT3", "Dirt 3", "None", "", 20),
    ("MATERIAL_ICE2", "Ice 2", "None", "", 21),
    ("MATERIAL_ICE3", "Ice 3", "None", "", 22)
    ]

def get_face_material(self):
    bm = bmesh.from_edit_mesh(bpy.context.object.data)
    layer = bm.faces.layers.int.get("revolt_material") or bm.faces.layers.int.new("revolt_material")
    selected_faces = [face for face in bm.faces if face.select]
    if len(selected_faces) == 0 or any([face[layer] != selected_faces[0][layer] for face in selected_faces]):
        return -1
    else:
        return selected_faces[0][layer]

def set_face_material(self, value):
    bm = bmesh.from_edit_mesh(bpy.context.object.data)
    layer = bm.faces.layers.int.get("revolt_material") or bm.faces.layers.int.new("revolt_material")
    for face in bm.faces:
        if face.select:
            face[layer] = value

def get_face_property(self):
    bm = bmesh.from_edit_mesh(bpy.context.object.data)
    layer = bm.faces.layers.int.get("revolt_face_type") or bm.faces.layers.int.new("revolt_face_type")
    selected_faces = [face for face in bm.faces if face.select]
    if len(selected_faces) == 0:
        return 0
    output = selected_faces[0][layer]
    for face in selected_faces:
        output = output & face[layer]
    print(self)
    return output
            
def set_face_property(self, value, mask):
    bm = bmesh.from_edit_mesh(bpy.context.object.data)
    layer = bm.faces.layers.int.get("revolt_face_type") or bm.faces.layers.int.new("revolt_face_type")
    for face in bm.faces:
        if face.select:
            for arg in args:
                face[layer] = face[layer] | mask if value else face[layer] & ~mask

class RevoltMeshProperties(bpy.types.PropertyGroup):
    face_material = EnumProperty(name = "Material", items = materials, get = get_face_material, set = set_face_material)
    face_double_sided = BoolProperty(name = "Double sided", get = lambda s: bool(get_face_property(s) & 2), set = lambda s,v: set_face_property(s, v, 2))
    face_translucent = BoolProperty(name = "Translucent", get = lambda s: bool(get_face_property(s) & 4), set = lambda s,v: set_face_property(s, v, 4))
    face_mirror = BoolProperty(name = "Mirror", get = lambda s: bool(get_face_property(s) & 128), set = lambda s,v: set_face_property(s, v, 128))
    face_additive = BoolProperty(name = "Additive blending", get = lambda s: bool(get_face_property(s) & 256), set = lambda s,v: set_face_property(s, v, 256))
    face_texture_animation = BoolProperty(name = "Texture animation", get = lambda s: bool(get_face_property(s) & 512), set = lambda s,v: set_face_property(s, v, 512))
    face_no_envmapping = BoolProperty(name = "No EnvMapping (.PRM)", get = lambda s: bool(get_face_property(s) & 1024), set = lambda s,v: set_face_property(s, v, 1024))
    face_envmapping = BoolProperty(name = "EnvMapping (.W)", get = lambda s: bool(get_face_property(s) & 2048), set = lambda s,v: set_face_property(s, v, 2048))
    export_as_prm = BoolProperty(name = "Export as mesh (.PRM)")
    export_as_ncp = BoolProperty(name = "Export as hitbox (.NCP)")
    export_as_w = BoolProperty(name = "Export as world (.W)")

object_types = [
    ("OBJECT_TYPE_CAR", "Car", "Car", "", -1),
    ("OBJECT_TYPE_BARREL", "Barrel", "Barrel", "", 1),
    ("OBJECT_TYPE_BEACHBALL", "Beachball", "Beachball", "", 2),
    ("OBJECT_TYPE_PLANET", "Planet", "Planet", "", 3),
    ("OBJECT_TYPE_PLANE", "Plane", "Plane", "", 4),
    ("OBJECT_TYPE_COPTER", "Copter", "Copter", "", 5),
    ("OBJECT_TYPE_DRAGON", "Dragon", "Dragon", "", 6),
    ("OBJECT_TYPE_WATER", "Water", "Water", "", 7),
    ("OBJECT_TYPE_TROLLEY", "Trolley", "Trolley", "", 8),
    ("OBJECT_TYPE_BOAT", "Boat", "Boat", "", 9),
    ("OBJECT_TYPE_SPEEDUP", "Speedup", "Speedup", "", 10),
    ("OBJECT_TYPE_RADAR", "Radar", "Radar", "", 11),
    ("OBJECT_TYPE_BALLOON", "Balloon", "Balloon", "", 12),
    ("OBJECT_TYPE_HORSE", "Horse", "Horse", "", 13),
    ("OBJECT_TYPE_TRAIN", "Train", "Train", "", 14),
    ("OBJECT_TYPE_STROBE", "Strobe", "Strobe", "", 15),
    ("OBJECT_TYPE_FOOTBALL", "Football", "Football", "", 16),
    ("OBJECT_TYPE_SPARKGEN", "Sparkgen", "Sparkgen", "", 17),
    ("OBJECT_TYPE_SPACEMAN", "Spaceman", "Spaceman", "", 18),
    ("OBJECT_TYPE_SHOCKWAVE", "Shockwave", "Shockwave", "", 19),
    ("OBJECT_TYPE_FIREWORK", "Firework", "Firework", "", 20),
    ("OBJECT_TYPE_PUTTYBOMB", "Puttybomb", "Puttybomb", "", 21),
    ("OBJECT_TYPE_WATERBOMB", "Waterbomb", "Waterbomb", "", 22),
    ("OBJECT_TYPE_ELECTROPULSE", "Electropulse", "Electropulse", "", 23),
    ("OBJECT_TYPE_OILSLICK", "Oilslick", "Oilslick", "", 24),
    ("OBJECT_TYPE_OILSLICK_DROPPER", "Oilslick dropper", "Oilslick dropper", "", 25),
    ("OBJECT_TYPE_CHROMEBALL", "Chromeball", "Chromeball", "", 26),
    ("OBJECT_TYPE_CLONE", "Clone", "Clone", "", 27),
    ("OBJECT_TYPE_TURBO", "Turbo", "Turbo", "", 28),
    ("OBJECT_TYPE_ELECTROZAPPED", "Electrozapped", "Electrozapped", "", 29),
    ("OBJECT_TYPE_SPRING", "Spring", "Spring", "", 30),
    ("OBJECT_TYPE_PICKUP", "Pickup", "Pickup", "", 31),
    ("OBJECT_TYPE_DISSOLVEMODEL", "Dissolve model", "Dissolve model", "", 32),
    ("OBJECT_TYPE_FLAP", "Flap", "Flap", "", 33),
    ("OBJECT_TYPE_LASER", "Laser", "Laser", "", 34),
    ("OBJECT_TYPE_SPLASH", "Splash", "Splash", "", 35),
    ("OBJECT_TYPE_BOMBGLOW", "Bombglow", "Bombglow", "", 36),
    ("OBJECT_TYPE_MAX", "Max", "Max", "", 37),
    ]

def get_flag_long(self, start):
    return struct.unpack("=l", bytes(self.flags[start:start + 4]))[0]

def set_flag_long(self, value, start):
    for i,b in enumerate(struct.pack("=l", value), start):
        self.flags[i] = b

def get_first_node(self):
    return bpy.context.object.name == bpy.context.scene.revolt_world.position_node_start

def set_first_node(self, value):
    bpy.context.scene.revolt_world.position_node_start = bpy.context.object.name if value else ""

class RevoltObjectProperties(bpy.types.PropertyGroup):
    type = EnumProperty(name = "Type", items = (("NONE", "None", "None"), ("OBJECT", "Object", "Object"), ("TRIGGER", "Trigger", "Trigger")))
    object_type = EnumProperty(name = "Object type", items = object_types)
    flags = IntVectorProperty(name = "Flags", size = 16)
    flag1_long = IntProperty(get = lambda s: get_flag_long(s, 0), set = lambda s,v: set_flag_long(s, v, 0))
    flag2_long = IntProperty(get = lambda s: get_flag_long(s, 4), set = lambda s,v: set_flag_long(s, v, 4))
    flag3_long = IntProperty(get = lambda s: get_flag_long(s, 8), set = lambda s,v: set_flag_long(s, v, 8))
    flag4_long = IntProperty(get = lambda s: get_flag_long(s, 12), set = lambda s,v: set_flag_long(s, v, 12))

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)
    bpy.types.INFO_MT_add.append(menu_func_add)
    
    bpy.types.Scene.revolt_world = PointerProperty(type = RevoltWorldProperties)
    bpy.types.Scene.revolt_car = PointerProperty(type = RevoltCarProperties)
    bpy.types.Mesh.revolt = PointerProperty(type = RevoltMeshProperties)
    bpy.types.Object.revolt = PointerProperty(type = RevoltObjectProperties)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    bpy.types.INFO_MT_add.remove(menu_func_add)
    
    del bpy.types.Scene.revolt_world
    del bpy.types.Scene.revolt_car
    del bpy.types.Mesh.revolt
    del bpy.types.Object.revolt

if __name__ == "__main__":
    register()