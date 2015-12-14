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
        self.layout.prop(context.object.data.revolt, "face_double_sided")
        self.layout.prop(context.object.data.revolt, "face_translucent")
        self.layout.prop(context.object.data.revolt, "face_mirror")
        self.layout.prop(context.object.data.revolt, "face_additive")
        self.layout.prop(context.object.data.revolt, "face_texture_animation")
        self.layout.prop(context.object.data.revolt, "face_no_envmapping")
        self.layout.prop(context.object.data.revolt, "face_envmapping")
        
class WorldExportPanel(bpy.types.Panel):
    bl_label = "Re-Volt world export"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    
    def draw(self, context):
        self.layout.prop(context.scene.revolt_world, "scale")
        self.layout.prop(context.scene.revolt_world, "up_axis")
        self.layout.prop(context.scene.revolt_world, "forward_axis")
        self.layout.prop(context.scene.revolt_world, "path")
        self.layout.prop(context.scene.revolt_world, "name")
        self.layout.prop_search(context.scene.revolt_world, "startpos_object", context.scene, "objects")
        self.layout.prop(context.scene.revolt_world, "farclip")
        self.layout.prop(context.scene.revolt_world, "fogstart")
        self.layout.prop(context.scene.revolt_world, "fogcolor")
        
        self.layout.operator(EXPORT_SCENE_OT_revolt_world_complete.bl_idname)
        
class EXPORT_SCENE_OT_revolt_world_complete(bpy.types.Operator):
    bl_idname = "export_scene.revolt_world_complete"
    bl_label = "Export Re-Volt world"
    
    def execute(self, context):
        export_world_full()
        return {'FINISHED'}

class DATA_PT_revolt_mesh(bpy.types.Panel):
    bl_label = "Re-Volt mesh properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    
    def draw(self, context):
        self.layout.prop(context.object.data.revolt, "export_as_prm")
        self.layout.prop(context.object.data.revolt, "export_as_ncp")
        self.layout.prop(context.object.data.revolt, "export_as_w")

class OBJECT_PT_revolt_object(bpy.types.Panel):
    bl_label = "Re-Volt object properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    
    def draw(self, context):
        self.layout.prop(context.object.revolt, "type")
        
        if context.object.revolt.type == "OBJECT":
            self.layout.prop(context.object.revolt, "object_type")
            self.layout.prop(context.object.revolt, "flag1_long")
            self.layout.prop(context.object.revolt, "flag2_long")
            self.layout.prop(context.object.revolt, "flag3_long")
            self.layout.prop(context.object.revolt, "flag4_long")

class RENDER_PT_revolt_car(bpy.types.Panel):
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
