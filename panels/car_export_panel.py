import bpy
from bpy.props import *

class RevoltWheelParameters(bpy.types.PropertyGroup):
    object = StringProperty(name = "Object")
    is_present = BoolProperty(name = "Present", default = True)
    is_powered = BoolProperty(name = "Powered")
    is_turnable = BoolProperty(name = "Turnable")
    steer_ratio = FloatProperty(name = "Steer ratio")
    engine_ratio = FloatProperty(name = "Engine ratio")

bpy.utils.register_class(RevoltWheelParameters)

class RevoltCarParameters(bpy.types.PropertyGroup):
    path = StringProperty(name = "Path", subtype = "DIR_PATH")
    name = StringProperty(name = "Car name")
    engine_class = EnumProperty(name = "Engine class", items = [("0", "Electric", "Electric"), ("1", "Glow", "Glow"), ("2", "Other", "Other")])
    steer_rate = FloatProperty(name = "Steer rate", default = 3)
    body_object = StringProperty(name = "Body object")
    wheel0 = PointerProperty(type = RevoltWheelParameters)
    wheel1 = PointerProperty(type = RevoltWheelParameters)
    wheel2 = PointerProperty(type = RevoltWheelParameters)
    wheel3 = PointerProperty(type = RevoltWheelParameters)
    current_wheel = EnumProperty(items = [("0", "0", "0"), ("1", "1", "1"), ("2", "2", "2"), ("3", "3", "3")])
    
    def get_wheel(self, nr):
        return [self.wheel0, self.wheel1, self.wheel2, self.wheel3][nr]
    
    def get_selected_wheel(self):
        return self.get_wheel(int(self.current_wheel))

bpy.utils.register_class(RevoltCarParameters)
bpy.types.Scene.revolt_car_parameters = PointerProperty(type = RevoltCarParameters)

class CarExportPanel(bpy.types.Panel):
    bl_label = "Re-Volt car export"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    
    def draw(self, context):
        car_parameters = context.scene.revolt_car_parameters
    
        self.layout.prop(car_parameters, "path")
        self.layout.prop(car_parameters, "name")
        self.layout.prop(car_parameters, "engine_class")
        self.layout.prop(car_parameters, "steer_rate")
        self.layout.prop_search(car_parameters, "body_object", context.scene, "objects")
        
        self.layout.separator()
        self.layout.label("Wheel configuration:")
        self.layout.prop(car_parameters, "current_wheel", expand = True)
        wheel = car_parameters.get_selected_wheel()
        self.layout.prop_search(wheel, "object", context.scene, "objects")
        row = self.layout.row()
        row.column().prop(wheel, "is_present")
        row.column().prop(wheel, "is_powered")
        row.column().prop(wheel, "is_turnable")
        self.layout.prop(wheel, "steer_ratio")
        self.layout.prop(wheel, "engine_ratio")
