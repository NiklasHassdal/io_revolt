# File specifications can be found here: http://www.perror.de/rv/rvstruct.html
# Re-Volt source code can be found here: http://revenant1.net/rvsource.rar

import bpy, bmesh, struct, os, re
from mathutils import Color, Vector, Matrix
from math import sqrt, pow, ceil, floor, pi
from bpy_extras.io_utils import axis_conversion

# This method is used to encode a bmesh. If you want to you can define which faces and verts to use. We do this when encoding W-files for example.
def encode_mesh(fh, bm, matrix, include_textures, faces = None, verts = None):
    if faces == None or verts == None:
        faces = list(bm.faces)
        verts = list(bm.verts)
    
    # Writes number of polygons and vertices.
    fh.write(struct.pack("hh", len(faces), len(verts)))
    
    # Gets active texture-, uv- and color layers.
    tex_lay = bm.faces.layers.tex.active
    uv_lay = bm.loops.layers.uv.active
    color_lay = bm.loops.layers.color.active
    alpha_lay = bm.loops.layers.color.get("Alpha")
    type_lay = bm.faces.layers.int.get("revolt_face_type")
    
    # Loops through each polygon.
    for face in faces:
        
        # The texture is stored as an integer where 0 means ...a.bmp, 1 means ...b.bmp etc. Let's figure out what number to write!
        if include_textures and tex_lay != None and face[tex_lay].image != None:
            texture = ord(os.path.splitext(face[tex_lay].image.name)[0][-1:].lower()) - 97
        else:
            texture = 0
        

        # Sets the polygon's bit-field
        is_quad = 1 if len(face.verts) > 3 else 1
        type = face[type_lay] & ~1 + is_quad


        # Writes type and texture.
        fh.write(struct.pack("hh", type, texture))
        looping = [2, 1, 0, 3] if len(face.verts) < 4 else [3, 2, 1, 0]
        
        # Writes vertex indices.
        vertex_indices = [verts.index(face.verts[i]) if i < len(face.verts) else 0 for i in looping]
        fh.write(struct.pack("hhhh", vertex_indices[0], vertex_indices[1], vertex_indices[2], vertex_indices[3]))
        
        # Writes color and alpha.
        for i in looping:
            color = face.loops[i][color_lay] if i < len(face.loops) and color_lay != None else Color((1, 1, 1))
            alpha = face.loops[i][alpha_lay] if i < len(face.loops) and alpha_lay != None else Color((1, 1, 1))
            fh.write(struct.pack("BBBB", int(color.r * 255), int(color.g * 255), int(color.b * 255), int(alpha.v * 255)))
        
        # Writes UV.
        for i in looping:
            uv = face.loops[i][uv_lay].uv if i < len(face.loops) and uv_lay != None else [0, 0]
            fh.write(struct.pack("ff", uv[0], 1 - uv[1]))
    
    # Loops through each vertex
    for vertex in verts:
        co = Vector(vertex.co) * matrix
        normal = revolt_fix(vertex.normal, 1)
        fh.write(struct.pack("fff", co[0], co[1], co[2]))
        fh.write(struct.pack("fff", normal[0], normal[1], normal[2]))
        
# Exports a model. (PRM-/M-file)
def export_model(filepath, matrix, include_textures, mesh = None):
    bm = bmesh.new()
    bm.from_mesh(mesh or bpy.context.object.data)
    fh = open(filepath, "wb")
    encode_mesh(fh, bm, matrix, include_textures)
    fh.close()
    bm.free()

# Exports a level/world. (W-file)
def export_world(filepath, matrix, mesh = None):
    bm = bmesh.new()
    bm.from_mesh(mesh or bpy.context.object.data)
    fh = open(filepath, "wb")
    fh.write(struct.pack("l", len(bm.faces)))
    
    # Loops through each face.
    for face in bm.faces:
        c = Vector(face.calc_center_bounds()) * matrix
        r = max([get_distance(Vector(v.co) * matrix, c) for v in face.verts])
        fh.write(struct.pack("ffff", c[0], c[1], c[2], r))
        p1 = Vector([min([v.co.x for v in face.verts]), min([v.co.y for v in face.verts]), min([v.co.z for v in face.verts])]) * matrix
        p2 = Vector([max([v.co.x for v in face.verts]), max([v.co.y for v in face.verts]), max([v.co.z for v in face.verts])]) * matrix
        fh.write(struct.pack("ffffff", p1[0], p1[1], p1[2], p2[0], p2[1], p2[2]))
        encode_mesh(fh, bm, matrix, True, [face], list(face.verts))
    
    # Writes a "FunnyBall" surrounding the whole level
    p1 = Vector([min([v.co.x for v in bm.verts]), min([v.co.y for v in bm.verts]), min([v.co.z for v in bm.verts])]) * matrix
    p2 = Vector([max([v.co.x for v in bm.verts]), max([v.co.y for v in bm.verts]), max([v.co.z for v in bm.verts])]) * matrix
    fh.write(struct.pack("lffff", 1, (p1.x + p2.x) / 2, (p1.y + p2.y) / 2, (p1.z + p2.z) / 2, get_distance(p1, p2) / 2))
    fh.write(struct.pack("l", len(bm.faces)))
    for i in range(len(bm.faces)):
        fh.write(struct.pack("l", i))
    
    # Writes an "UnknownList" with length 0.
    fh.write(struct.pack("l", 0))
    
    fh.close()
    bm.free()

# Exports a level/world according to the settings in the "Re-Volt world export" panel.
def export_world_full():
    world_parameters = bpy.context.scene.revolt_world
    full_path = world_parameters.path
    path = [x for x in re.split("[/\\\\]", full_path) if x != ""]
    matrix = axis_conversion(from_up = world_parameters.up_axis, from_forward = world_parameters.forward_axis).to_4x4() * (1 / world_parameters.scale)
    
    # Exits if the directory doesn't exist.
    if not os.path.isdir(full_path):
        return
    
    # Loops through each mesh.
    for mesh in bpy.data.meshes:
    
        # Exports to a W-file.
        if mesh.revolt.export_as_w:
            export_world(full_path + bpy.path.ensure_ext(mesh.name, ".w"), matrix, mesh)
            
        # Exports to a PRM-file.
        if mesh.revolt.export_as_prm:
            export_model(full_path + bpy.path.ensure_ext(mesh.name, ".prm"), matrix, True, mesh)
            
        # Exports to a NCP-file.
        if mesh.revolt.export_as_ncp:
            export_hitbox(full_path + bpy.path.ensure_ext(mesh.name, ".ncp"), matrix, mesh)
            
    # Exports each texture.
    bpy.context.scene.render.image_settings.file_format = "BMP"
    for image in bpy.data.images:
        temp_image = image.copy()
        temp_image.scale(256, 256)
        temp_image.save_render("\\".join(path) + "\\" + path[-1] + os.path.splitext(image.name)[0][-1] + ".bmp")
        bpy.data.images.remove(temp_image)
    
    # Exports world models. (FIN-file)
    export_world_models("\\".join(path) + "\\" + path[-1] + ".fin", matrix, [obj for obj in bpy.context.scene.objects if obj.type == "MESH" and obj.data.revolt.export_as_prm])
    
    # Exports world objects. (FOB-file)
    export_world_objects("\\".join(path) + "\\" + path[-1] + ".fob", matrix, [obj for obj in bpy.data.objects if obj.revolt.type == "OBJECT"])
    
    # Exports the INF-file.
    fh = open("\\".join(path) + "\\" + path[-1] + ".inf", "w")
    startpos_object = bpy.context.scene.objects.get(world_parameters.startpos_object)
    params = {}
    params["NAME"] = "'" + world_parameters.name + "'"
    if startpos_object == None:
        params["STARTPOS"] =  "0 0 0"
        params["STARTROT"] = "0"
    else:
        params["STARTPOS"] = " ".join([str(x) for x in Vector(startpos_object.location) * matrix])
        params["STARTROT"] = str((-startpos_object.rotation_euler.z % (pi * 2)) / (pi * 2))
    params["FARCLIP"] = str(world_parameters.farclip * min(matrix.to_scale()))
    params["FOGSTART"] = str(world_parameters.fogstart * min(matrix.to_scale()))
    params["FOGCOLOR"] = " ".join([str(int(x * 255)) for x in world_parameters.fogcolor])
    char_count = max([len(x) for x in params]) + 5
    fh.writelines([p.ljust(char_count) + params[p] + "\n" for p in params])
    fh.close()

# Exports a hitbox. (NCP-file)
def export_hitbox(filepath, matrix, mesh = None):
    bm = bmesh.new()
    bm.from_mesh(mesh or bpy.context.object.data)
    fh = open(filepath, "wb")
    fh.write(struct.pack("h", len(bm.faces)))
    material_layer = bm.faces.layers.int.get("revolt_material") or bm.faces.layers.int.new("revolt_material")
    
    print(fh.name)
    
    # Loops through each face.
    for face in bm.faces:
        # Writes face type (tris / quad) and material. (see panels/face_properties_panel.py for available material types)
        fh.write(struct.pack("ll", 0 if len(face.verts) < 4 else 1, face[material_layer]))
        
        # Writes the floor plane
        normal = face.normal * matrix
        normal.length = 1
        point = face.verts[0].co * matrix
        distance = -point.x * normal.x - point.y * normal.y - point.z * normal.z
        fh.write(struct.pack("ffff", normal[0], normal[1], normal[2], distance))
        
        # Writes each cutting plane.
        vertex_count = len(face.verts[:4])
        for i in range(vertex_count - 1, -1, -1):
            a = face.verts[i].co * matrix
            b = face.verts[(i + 1) % vertex_count].co * matrix
            normal2 = normal.cross(a - b)
            normal2.length = 1
            distance = -a.x * normal2.x - a.y * normal2.y - a.z * normal2.z
            fh.write(struct.pack("ffff", normal2[0], normal2[1], normal2[2], distance))
            
        # Writes the rest of the cutting planes if the number of edges is lower than four.
        for i in range(4 - vertex_count):
            fh.write(struct.pack("ffff", 0, 0, 0, 0))
        
        # Writes bounding box.
        verts = [v.co * matrix for v in face.verts]
        min_point = [min([v.x for v in verts]), min([v.y for v in verts]), min([v.z for v in verts])]
        max_point = [max([v.x for v in verts]), max([v.y for v in verts]), max([v.z for v in verts])]
        fh.write(struct.pack("ffffff", min_point[0], max_point[0], min_point[1], max_point[1], min_point[2], max_point[2]))
        
    # Writes the lookup grid.
    raster_size = 1024
    x_coords = [(v.co * matrix).x for v in bm.verts]
    z_coords = [(v.co * matrix).z for v in bm.verts]
    min_x = min(x_coords)
    max_x = max(x_coords)
    min_z = min(z_coords)
    max_z = max(z_coords)
    x_size = ceil((max_x - min_x) / raster_size)
    z_size = ceil((max_z - min_z) / raster_size)
    lookup_table = [[] for n in range(x_size * z_size)]
    
    for face in bm.faces:
        verts = [v.co * matrix for v in face.verts]
        from_x = floor((min([v.x for v in verts]) - min_x) / raster_size)
        to_x = ceil((max([v.x for v in verts]) - min_x) / raster_size)
        from_z = floor((min([v.z for v in verts]) - min_z) / raster_size)
        to_z = ceil((max([v.z for v in verts]) - min_z) / raster_size)
        for x in range(from_x, to_x):
            for z in range(from_z, to_z):
                lookup_table[x + z * x_size].append(face.index)
    
    fh.write(struct.pack("fffff", min_x, min_z, x_size, z_size, raster_size))
    for list in lookup_table:
        fh.write(struct.pack("l", len(list)))
        for index in list:
            fh.write(struct.pack("l", index))
        
    fh.close()
    bm.free()

# Exports world objects. (FIN-file)
def export_world_models(filepath, matrix, objects):
    fh = open(filepath, "wb")
    
    # Writes the number of objects.
    fh.write(struct.pack("l", len(objects)))
    
    # Loops through each object.
    for obj in objects:
        mesh_name = bpy.path.ensure_ext(obj.data.name, ".PRM").upper().replace(".", "\x00")[:8].ljust(8, "\x00")
        fh.write(bytes(mesh_name, "ASCII"))
        v1 = Vector((obj.matrix_local[0].x, obj.matrix_local[1].x, obj.matrix_local[2].x)) * matrix.normalized()
        v2 = -Vector((obj.matrix_local[0].z, obj.matrix_local[1].z, obj.matrix_local[2].z)) * matrix.normalized()
        v3 = Vector((obj.matrix_local[0].y, obj.matrix_local[1].y, obj.matrix_local[2].y)) * matrix.normalized()
        location = obj.location * matrix
        fh.write(struct.pack("BBBLBBBBfffffffffffff", 0, 0, 0, 0, 0, 0, 0, 0, 0, location.x, location.y, location.z, v1.x, v1.y, v1.z, v2.x, v2.y, v2.z, v3.x, v3.y, v3.z))
        
    fh.close()
    
# Exports a convex hull. (HUL-file)
def export_convex_hull(filepath, scale, mesh = None):
    bm = bmesh.new();
    bm.from_mesh(mesh or bpy.context.object.data)
    fh = open(filepath, "wb")
    
    # Fetches the hull data. I find it strange that the method convex_hull returns verts, edges and faces in the same sequence but it does so we've got to separate them.
    data = bmesh.ops.convex_hull(bm, input = bm.verts)
    verts = [x for x in data["geom"] if type(x) is bmesh.types.BMVert]
    edges = [x for x in data["geom"] if type(x) is bmesh.types.BMEdge]
    faces = [x for x in data["geom"] if type(x) is bmesh.types.BMFace]
    
    # Let's write the hull. I don't see the point in using multiple hulls so we're just gonna go with one.
    fh.write(struct.pack("hhhh", 1, len(verts), len(edges), len(faces)))
    
    # Writes the bounding box.
    co = [revolt_fix(v.co, scale) for v in verts]
    fh.write(struct.pack("ffffff", min([v.x for v in co]), max([v.x for v in co]), min([v.y for v in co]), max([v.y for v in co]), min([v.z for v in co]), max([v.z for v in co])))
    fh.write(struct.pack("fff", 0, 0, 0))
    
    # Loops through each vertex.
    for vert in verts:
        co = revolt_fix(vert.co, scale)
        fh.write(struct.pack("fff", co.x, co.y, co.z))
    
    # Loops through each edge.
    for edge in edges:
        fh.write(struct.pack("hh", verts.index(edge.verts[0]), verts.index(edge.verts[1])))
    
    # Loops through each face.
    for face in faces:
        point = revolt_fix(face.verts[0].co, scale)
        normal = revolt_fix(face.normal, 1)
        normal.length = 1
        
        # The faces are stored in the file as planes so we need to get the distance from the origin.
        distance = -point.x * normal.x - point.y * normal.y - point.z * normal.z
        fh.write(struct.pack("ffff", normal.x, normal.y, normal.z, revolt_fix(distance, scale)))
    
    # So the convex hull is filled with spheres so let's try to fill it. First of, we need to find suitable locations for each sphere so we need a grid basically.
    count_x, count_y, count_z = 5, 5, 5
    min_x, min_y, min_z = [min([v.co.x for v in verts]), min([v.co.y for v in verts]), min([v.co.z for v in verts])]
    step_x, step_y, step_z = [(max([v.co.x for v in verts]) - min_x) / count_x, (max([v.co.y for v in verts]) - min_y) / count_y, (max([v.co.z for v in verts]) - min_z) / count_z]
    spheres_locations = []
    
    # Loops through the grid.
    for x in range(count_x):
        for y in range(count_y):
            for z in range(count_z):
                
                # Calculates the sphere location. All spheres will be evenly distributed within the convex hull.
                sphere = Vector([min_x + step_x / 2 + step_x * x, min_y + step_y / 2 + step_y * y, min_z + step_z / 2 + step_z * z])
                
                # Gets the distance from the origin for each face and the sphere center (using the face normal). This is partly used in order to determine the radius of the sphere but also to check if the sphere is inside the convex hull.
                distances = [[-face.verts[0].co.x * face.normal.x - face.verts[0].co.y * face.normal.y - face.verts[0].co.z * face.normal.z, -sphere.x * face.normal.x - sphere.y * face.normal.y - sphere.z * face.normal.z] for face in faces]
                
                # Let's add the sphere to spheres_locations if the sphere is inside of the convex hull.
                if all([distance[0] < distance[1] for distance in distances]):
                    spheres_locations.append([sphere, min([distance[1] - distance[0] for distance in distances])])
                    
    # Writes the number of spheres.
    fh.write(struct.pack("h", len(spheres_locations)))
    
    # Writes each sphere.
    for sphere in spheres_locations:
        co = revolt_fix(sphere[0], scale)
        fh.write(struct.pack("ffff", co.x, co.y, co.z, revolt_fix(sphere[1], scale)))
    
    fh.close()
    bm.free()

# Exports world objects. (FOB-file)
def export_world_objects(filepath, matrix, objects):
    object_types = {item[0] : i - 1 for i,item in enumerate(bpy.types.RevoltObjectProperties.object_type[1]["items"])}
    
    fh = open(filepath, "wb")
    fh.write(struct.pack("l", len(objects)))
    for obj in objects:
        object_type = object_types[obj.revolt.object_type]
        up = (-Vector((obj.matrix_local[0].z, obj.matrix_local[1].z, obj.matrix_local[2].z)) * matrix).normalized()
        forward = (Vector((obj.matrix_local[0].y, obj.matrix_local[1].y, obj.matrix_local[2].y)) * matrix).normalized()
        location = obj.location * matrix
        fh.write(struct.pack("lllllfffffffff", object_type, obj.revolt.flag1_long, obj.revolt.flag2_long, obj.revolt.flag3_long, obj.revolt.flag4_long, location.x, location.y, location.z, up.x, up.y, up.z, forward.x, forward.y, forward.z))
    fh.close()

# This method converts a Blender coordinate to a Re-Volt coordinate. In Re-Volt the Y-axis is up and inverted. In Blender the Z-axis is up.
def revolt_fix(input, scale = 1):
    t = type(input)
    if t in (Vector, list, tuple) and len(input) == 3:
        return Vector((input[0], -input[2], input[1])) / scale
    if t in (float, int):
        return input / scale
    if t is Matrix and len(input) >= 3:
        return Matrix(((input[0][0], -input[0][2], input[0][1]), (-input[2][0], input[2][2], -input[2][1]), (input[1][0], -input[1][2], input[1][1])))

# Returns the distance between two points.
def get_distance(v1, v2):
    return sqrt(pow(v1.x - v2.x, 2) + pow(v1.y - v2.y, 2) + pow(v1.z - v2.z, 2))