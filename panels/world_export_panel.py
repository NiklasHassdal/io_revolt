import bpy, re, os
from bpy.props import *
from io_revolt.encode import export_world_full
from mathutils import Vector

def farclip_or_fogstart_changed(self, context):
    if self.fogstart > self.farclip:
        self.fogstart = self.farclip

class RevoltWorldParameters(bpy.types.PropertyGroup):
    path = StringProperty(name = "Path", subtype = "DIR_PATH")
    name = StringProperty(name = "Name")
    startpos_object = StringProperty(name = "Start position")
    farclip = FloatProperty(name = "Farclip", update = farclip_or_fogstart_changed, min = 0, step = 100)
    fogstart = FloatProperty(name = "Fogstart", update = farclip_or_fogstart_changed, min = 0, step = 100)
    fogcolor = FloatVectorProperty(name = "Fogcolor", subtype = "COLOR")
    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    
bpy.utils.register_class(RevoltWorldParameters)
bpy.types.Scene.revolt_world_parameters = PointerProperty(type = RevoltWorldParameters)

class WorldExportPanel(bpy.types.Panel):
    bl_label = "Re-Volt world export"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    
    def draw(self, context):
        world_parameters = context.scene.revolt_world_parameters
        
        self.layout.prop(world_parameters, "path")
        self.layout.prop(world_parameters, "name")
        self.layout.prop_search(world_parameters, "startpos_object", context.scene, "objects")
        self.layout.prop(world_parameters, "farclip")
        self.layout.prop(world_parameters, "fogstart")
        self.layout.prop(world_parameters, "fogcolor")
        self.layout.prop(world_parameters, "scale")
        
        self.layout.operator(WorldExportOperator.bl_idname)
        
class WorldExportOperator(bpy.types.Operator):
    bl_idname = "export_scene.revolt_world_complete"
    bl_label = "Export Re-Volt world"
    
    def execute(self, context):
        export_world_full()
        return {'FINISHED'}