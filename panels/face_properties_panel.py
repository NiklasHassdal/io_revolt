import bpy, bmesh
from bpy.props import *

# Gets the current face type for the selected faces. It'll return "none" if no faces are selected or if the selected faces doesn't have the same type.
def get_face_material(mesh):
    bm = bmesh.from_edit_mesh(mesh)
    layer = bm.faces.layers.int.get("revolt_material") or bm.faces.layers.int.new("revolt_material")
    selected_faces = [face for face in bm.faces if face.select]
    if len(selected_faces) == 0 or any([face[layer] != selected_faces[0][layer] for face in selected_faces]):
        return -1
    else:
        return selected_faces[0][layer]

# Sets the face type for all selected faces.
def set_face_material(mesh, value):
    bm = bmesh.from_edit_mesh(mesh)
    layer = bm.faces.layers.int.get("revolt_material") or bm.faces.layers.int.new("revolt_material")
    selected_faces = [face for face in bm.faces if face.select]
    for face in selected_faces:
        face[layer] = value

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

bpy.types.Mesh.revolt_face_material = EnumProperty(name = "Material (NCP only)", items = materials, get = get_face_material, set = set_face_material)

# Class used for drawing the panel.
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
        self.layout.prop(context.object.data, "revolt_face_material")