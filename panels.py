import bpy, bmesh
from bpy.props import *
from io_revolt.encode import export_world_full

class RevoltFacePropertiesPanel(bpy.types.Panel):
    bl_label = "Revolt Face Properties"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "mesh_edit"
    bl_category = "Re-Volt"
    
    @classmethod
    def poll(self, context):
        return context.object.type == "MESH"
    
    def draw(self, context):
        self.layout.prop(context.object.data.revolt, "face_material")

class WorldExportPanel(bpy.types.Panel):
    bl_label = "Re-Volt world export"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    
    def draw(self, context):
        self.layout.prop(context.scene.revolt_world, "path")
        self.layout.prop(context.scene.revolt_world, "name")
        self.layout.prop_search(context.scene.revolt_world, "startpos_object", context.scene, "objects")
        self.layout.prop(context.scene.revolt_world, "farclip")
        self.layout.prop(context.scene.revolt_world, "fogstart")
        self.layout.prop(context.scene.revolt_world, "fogcolor")
        self.layout.prop(context.scene.revolt_world, "scale")
        
        self.layout.operator(WorldExportOperator.bl_idname)
        
class WorldExportOperator(bpy.types.Operator):
    bl_idname = "export_scene.revolt_world_complete"
    bl_label = "Export Re-Volt world"
    
    def execute(self, context):
        export_world_full()
        return {'FINISHED'}

class RevoltMeshPropertiesPanel(bpy.types.Panel):
    bl_label = "Re-Volt mesh properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    
    def draw(self, context):
        self.layout.prop(context.object.data.revolt, "export_as_prm")
        self.layout.prop(context.object.data.revolt, "export_as_ncp")
        self.layout.prop(context.object.data.revolt, "export_as_w")

class CarExportPanel(bpy.types.Panel):
    bl_label = "Re-Volt car export"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    
    def draw(self, context):
        car_parameters = context.scene.revolt_car
    
        self.layout.prop(car_parameters, "path")
        self.layout.prop(car_parameters, "name")
        self.layout.prop(car_parameters, "engine_class")
        self.layout.prop(car_parameters, "steer_rate")
        self.layout.prop_search(car_parameters, "body_object", context.scene, "objects")
        
        self.layout.separator()
        self.layout.label("Wheel configuration:")
        self.layout.prop(car_parameters, "current_wheel", expand = True)
        wheel = [car_parameters.wheel0, car_parameters.wheel1, car_parameters.wheel2, car_parameters.wheel3][int(car_parameters.current_wheel)]
        self.layout.prop_search(wheel, "object", context.scene, "objects")
        row = self.layout.row()
        row.column().prop(wheel, "is_present")
        row.column().prop(wheel, "is_powered")
        row.column().prop(wheel, "is_turnable")
        self.layout.prop(wheel, "steer_ratio")
        self.layout.prop(wheel, "engine_ratio")