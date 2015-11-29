import bpy, bmesh
from bpy.props import *

class RevoltFacePropertiesOperator(bpy.types.Operator):
    bl_label = "Apply"
    bl_idname = "mesh.apply_revolt_properties"
    
    test = StringProperty()
    
    def execute(self, context):
        return {'FINISHED'}

class RevoltFacePropertyGroup(bpy.types.PropertyGroup):
    index = IntProperty()
    type = IntProperty()

bpy.utils.register_class(RevoltFacePropertyGroup)
bpy.types.WindowManager.revolt_face_properties = PointerProperty(type = RevoltFacePropertyGroup)

class RevoltFacePropertiesPanel(bpy.types.Panel):
    bl_label = "Revolt Face Properties"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "mesh_edit"
    bl_category = "Re-Volt"
    
    bm = bmesh.new()
    
    @classmethod
    def poll(self, context):
        return context.object.type == "MESH"
    
    def draw(self, context):
        self.bm.clear()
        self.bm = bmesh.from_edit_mesh(context.object.data)
        selected_polygons = [face for face in self.bm.faces if face.select]
        layer = self.bm.faces.layers.int.get("revolt_type") or self.bm.faces.layers.int.new("revolt_type")
        
        # Exits if no polygon is selected
        if len(selected_polygons) == 0:
            return
        
        face_props = context.window_manager.revolt_face_properties
        
        # If face index has changed. Update index and fetch face data.
        if len(selected_polygons) == 1 and face_props.index != selected_polygons[0].index:
            face_props.index = selected_polygons[0].index
            face_props.type = selected_polygons[0][layer]
            
        selected_polygons[0][layer] = face_props.type
        
        self.layout.label("Polygon index: " + str(face_props.index))
        self.layout.prop(face_props, "type")