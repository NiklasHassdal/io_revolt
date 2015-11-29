import bpy
from bpy.props import *

class RevoltMeshParameters(bpy.types.PropertyGroup):
    export_as_prm = BoolProperty(name = "Export as mesh (.PRM)")
    export_as_ncp = BoolProperty(name = "Export as hitbox (.NCP)")
    export_as_w = BoolProperty(name = "Export as world (.W)")

bpy.utils.register_class(RevoltMeshParameters)
bpy.types.Mesh.revolt = PointerProperty(type = RevoltMeshParameters)

class RevoltMeshParametersPanel(bpy.types.Panel):
    bl_label = "Re-Volt mesh properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    
    def draw(self, context):
        self.layout.prop(context.object.data.revolt, "export_as_prm")
        self.layout.prop(context.object.data.revolt, "export_as_ncp")
        self.layout.prop(context.object.data.revolt, "export_as_w")
        