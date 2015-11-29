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

import bpy
from bpy.props import StringProperty, FloatProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper
from .panels import face_properties_panel, car_export_panel, world_export_panel, mesh_parameters_panel

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
        obj = decode.add_revolt_startpos(context.scene.revolt_world_parameters.scale)
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
    
def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)
    bpy.types.INFO_MT_add.append(menu_func_add)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    bpy.types.INFO_MT_add.remove(menu_func_add)

if __name__ == "__main__":
    register()