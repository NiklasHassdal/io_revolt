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

import bpy, bmesh
from bpy.props import *
from bpy_extras.io_utils import ImportHelper, ExportHelper
from . import panels

class IMPORT_OT_revolt_model(bpy.types.Operator, ImportHelper):
    bl_idname = "import_mesh.revolt_model"
    bl_label = "Import Re-Volt model"
    bl_options = {'UNDO'}

    filename_ext = ".prm"
    filter_glob = StringProperty(default="*.prm;*.m", options={'HIDDEN'})
    
    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    
    def execute(self, context):
        from . import decode
        decode.import_model(self.properties.filepath, self.scale)
        return {'FINISHED'}

class IMPORT_OT_revolt_world(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.revolt_world"
    bl_label = "Import Re-Volt world"
    bl_options = {'UNDO'}

    filename_ext = ".w"
    filter_glob = StringProperty(default="*.w", options={'HIDDEN'})
    
    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    include_objects = BoolProperty(default=True, name = "Include objects")
    include_hitboxes = BoolProperty(default=True, name = "Include hitboxes")
    hide_hitboxes = BoolProperty(default=True, name = "Hide hitboxes")
    
    def draw(self, context):
        self.layout.prop(self, "scale")
        self.layout.prop(self, "include_objects")
        self.layout.prop(self, "include_hitboxes")
        if self.include_hitboxes:
            self.layout.prop(self, "hide_hitboxes")
    
    def execute(self, context):
        from . import decode
        decode.import_world(self.properties.filepath, self.scale, self.include_objects, self.include_hitboxes, self.hide_hitboxes)
        return {'FINISHED'}
        
class IMPORT_OT_revolt_hitbox(bpy.types.Operator, ImportHelper):
    bl_idname = "import_mesh.revolt_hitbox"
    bl_label = "Import Re-Volt hitbox"
    bl_options = {'UNDO'}

    filename_ext = ".ncp"
    filter_glob = StringProperty(default="*.ncp", options={'HIDDEN'})
    
    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    
    def execute(self, context):
        from . import decode
        decode.import_hitbox(self.properties.filepath, self.scale)
        return {'FINISHED'}

class IMPORT_OT_revolt_car(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.revolt_car"
    bl_label = "Import Re-Volt car"
    bl_options = {'UNDO'}

    filename_ext = "Parameters.txt"
    filter_glob = StringProperty(default="Parameters.txt", options={'HIDDEN'})
    
    scale = FloatProperty(default=0.1, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    
    def execute(self, context):
        from . import decode
        decode.import_car(self.properties.filepath, self.scale)
        return {'FINISHED'}

class IMPORT_OT_revolt_convex_hull(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.revolt_convex_hull"
    bl_label = "Import Re-Volt convex hull"
    bl_options = {'UNDO'}

    filename_ext = ".hul"
    filter_glob = StringProperty(default="*.hul", options={'HIDDEN'})
    
    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    
    def execute(self, context):
        from . import decode
        decode.import_convex_hull(self.properties.filepath, self.scale)
        return {'FINISHED'}

class EXPORT_OT_revolt_model(bpy.types.Operator, ExportHelper):
    bl_idname = "export_mesh.revolt_model"
    bl_label = "Export Re-Volt model"
    bl_options = {'UNDO'}

    filename_ext = ".prm"
    filter_glob = StringProperty(default="*.prm;*.m", options={'HIDDEN'})
    
    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    include_texture = BoolProperty(default=True, name = "Include texture")
    
    def execute(self, context):
        from . import encode
        encode.export_model(self.properties.filepath, self.scale, self.include_texture)
        return {'FINISHED'}

class EXPORT_OT_revolt_world(bpy.types.Operator, ImportHelper):
    bl_idname = "export_scene.revolt_world"
    bl_label = "Export Re-Volt world"
    bl_options = {'UNDO'}

    filename_ext = ".w"
    filter_glob = StringProperty(default="*.w", options={'HIDDEN'})
    
    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    
    def execute(self, context):
        from . import encode
        encode.export_world(self.properties.filepath, self.scale)
        return {'FINISHED'}
        
class EXPORT_OT_revolt_hitbox(bpy.types.Operator, ImportHelper):
    bl_idname = "export_mesh.revolt_hitbox"
    bl_label = "Export Re-Volt hitbox"
    bl_options = {'UNDO'}

    filename_ext = ".ncp"
    filter_glob = StringProperty(default="*.ncp", options={'HIDDEN'})
    
    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    
    def execute(self, context):
        from . import encode
        encode.export_hitbox(self.properties.filepath, self.scale)
        return {'FINISHED'}

class EXPORT_OT_revolt_convex_hull(bpy.types.Operator, ImportHelper):
    bl_idname = "export_mesh.convex_hull"
    bl_label = "Export Re-Volt convex hull"
    bl_options = {'UNDO'}

    filename_ext = ".hul"
    filter_glob = StringProperty(default="*.hul", options={'HIDDEN'})
    
    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    
    def execute(self, context):
        from . import encode
        encode.export_convex_hull(self.properties.filepath, self.scale)
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
    
    def execute(self, context):
        from . import decode
        obj = decode.add_revolt_startpos(context.scene.revolt_world_scale)
        obj.location = bpy.context.scene.cursor_location
        obj.select = True
        bpy.context.scene.objects.active = obj
        return {'FINISHED'}
        
def menu_func_import(self, context):
    self.layout.operator(IMPORT_OT_revolt_model.bl_idname, text="Re-Volt model (.prm/.m)")
    self.layout.operator(IMPORT_OT_revolt_world.bl_idname, text="Re-Volt world (.w)")
    self.layout.operator(IMPORT_OT_revolt_hitbox.bl_idname, text="Re-Volt hitbox (.ncp)")
    self.layout.operator(IMPORT_OT_revolt_car.bl_idname, text="Re-Volt car (Parameters.txt)")
    self.layout.operator(IMPORT_OT_revolt_convex_hull.bl_idname, text="Re-Volt convex hull (.hul)")

def menu_func_export(self, context):
    self.layout.operator(EXPORT_OT_revolt_model.bl_idname, text="Re-Volt model (.prm/.m)")
    self.layout.operator(EXPORT_OT_revolt_world.bl_idname, text="Re-Volt world (.w)")
    self.layout.operator(EXPORT_OT_revolt_hitbox.bl_idname, text="Re-Volt hitbox (.ncp)")
    self.layout.operator(EXPORT_OT_revolt_convex_hull.bl_idname, text="Re-Volt convex hull (.hul)")

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
    selected_faces = [face for face in bm.faces if face.select]
    for face in selected_faces:
        face[layer] = value

class RevoltMeshProperties(bpy.types.PropertyGroup):
    face_material = EnumProperty(name = "Material", items = materials, get = get_face_material, set = set_face_material)
    export_as_prm = BoolProperty(name = "Export as mesh (.PRM)")
    export_as_ncp = BoolProperty(name = "Export as hitbox (.NCP)")
    export_as_w = BoolProperty(name = "Export as world (.W)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)
    bpy.types.INFO_MT_add.append(menu_func_add)
    
    bpy.types.Scene.revolt_world = PointerProperty(type = RevoltWorldProperties)
    bpy.types.Scene.revolt_car = PointerProperty(type = RevoltCarProperties)
    bpy.types.Mesh.revolt = PointerProperty(type = RevoltMeshProperties)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    bpy.types.INFO_MT_add.remove(menu_func_add)
    
    del bpy.types.Scene.revolt_world
    del bpy.types.Scene.revolt_car
    del bpy.types.Mesh.revolt

if __name__ == "__main__":
    register()