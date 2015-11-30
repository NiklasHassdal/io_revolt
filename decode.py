# File specifications can be found here: http://www.perror.de/rv/rvstruct.html
# Re-Volt source code can be found here: http://revenant1.net/rvsource.rar

import bpy, struct, bmesh, mathutils, re, os, glob
from mathutils import Vector, Matrix, Color, Euler
from math import atan, pi

# Decodes a mesh and add decoded faces and vertices to supplied bmesh.
def decode_mesh(fh, bm, scale, texture = None):
    # Split up path.
    path = re.split("[/\\\\]", fh.name)
    
    # Gets/creates texture-, uv- and color layers.
    tex_lay = bm.faces.layers.tex.active or bm.faces.layers.tex.new("Texture")
    uv_lay = bm.loops.layers.uv.active or bm.loops.layers.uv.new("Uv")
    color_lay = bm.loops.layers.color.active or bm.loops.layers.color.new("Color")
    alpha_lay = bm.loops.layers.color.get("Alpha") or bm.loops.layers.color.new("Alpha")
    
    # Read some data from the file
    polygon_count, vertex_count = struct.unpack("hh", fh.read(4))
    polygons = [struct.unpack("hhhhhhBBBBBBBBBBBBBBBBffffffff", fh.read(60)) for x in range(polygon_count)]
    vertices = [bm.verts.new(revolt_fix(struct.unpack("ffffff", fh.read(24))[:3], scale)) for x in range(vertex_count)]
    
    # Loops through each polygon
    for data in polygons:
        vertex_indices = data[2:(5 if data[0] % 2 == 0 else 6)]
        if len(vertex_indices) == len(set(vertex_indices)) and bm.faces.get([vertices[i] for i in vertex_indices]) == None:
            polygon = bm.faces.new([vertices[i] for i in vertex_indices])
            
            if texture == None and data[1] >= 0:
                texture_name = path[-2].lower() + chr(97 + data[1]) + ".bmp"
                texture_path = "\\".join(path[:-1]) + "\\" + texture_name
                
                image = bpy.data.images.get(texture_name)
                if image == None and os.path.isfile(texture_path):
                    image = bpy.data.images.load(texture_path)
                polygon[tex_lay].image = image
            else:
                polygon[tex_lay].image = texture
            
            for i in range(len(polygon.loops)):
                polygon.loops[i][uv_lay].uv = [data[22 + i * 2], 1 - data[23 + i * 2]]
                polygon.loops[i][color_lay] = Color([x / 255 for x in data[6 + i * 4:9 + i * 4]])
                polygon.loops[i][alpha_lay] = Color([1 - (data[9 + i * 4]  / 255)] * 3)
            
            # The faces face the wrong way so the normal has to be flipped.
            polygon.normal_flip()

# Imports a model. (PRM-/M-file)
def import_model(filepath, scale, texture_path = None):
    # Returns None if the file doesn't exist or if its filesize is 0 byte.
    if not os.path.isfile(filepath) or os.path.getsize(filepath) == 0:
        return None
        
    fh = open(filepath, "rb")
    bm = bmesh.new()
    decode_mesh(fh, bm, scale, texture_path)
    fh.close()
    obj = bmesh_to_object(bm, os.path.basename(filepath))
    obj.data.revolt.export_as_prm = True
    return obj

# Imports a level/world. (W-file)
def import_world(filepath, scale, include_objects, include_hitboxes, hide_hitboxes):
    # Exits if the file doesn't exist or if its filesize is 0 byte.
    if os.path.isfile(filepath) == False or os.path.getsize(filepath) == 0:
        return
    
    # Creates bmesh, opens the file and reads the number of meshes in the file
    bm = bmesh.new()
    fh = open(filepath, "rb")
    mesh_count = struct.unpack("l", fh.read(4))[0]
    bpy.context.scene.revolt_world_parameters.path = os.path.dirname(fh.name)
    bpy.context.scene.revolt_world_parameters.scale = scale
    
    # Loops through each mesh
    for i in range(mesh_count):
        fh.read(40)
        decode_mesh(fh, bm, scale)
        
    # Closes file and create object form the bmesh.
    fh.close()
    world = bmesh_to_object(bm, os.path.basename(filepath))
    if world != None:
        world.data.revolt.export_as_w = True
    
    # Import hitbox if include_hitboxes is True.
    if include_hitboxes:
        hitbox = import_hitbox(os.path.splitext(filepath)[0] + ".ncp", scale)
        if hitbox != None:
            hitbox.hide = hide_hitboxes
            bpy.context.scene.revolt_world_parameters.hitbox_object = hitbox.name
    
    # Import objects if include_objects is True.
    if include_objects:
        import_objects(os.path.splitext(filepath)[0] + ".fin", scale, include_hitboxes)
    
    # Imports startpos and some other stuff.
    inf_path = os.path.splitext(filepath)[0] + ".inf"
    if os.path.isfile(inf_path):
        fh = open(inf_path, "r")
        data = ParameterBlock(fh)
        bpy.context.scene.revolt_world_parameters.name = (data.get_parameter("NAME") or "  ")[1:-1]
        bpy.context.scene.revolt_world_parameters.farclip = float(data.get_parameter("FARCLIP") or "0") * scale
        bpy.context.scene.revolt_world_parameters.fogstart = float(data.get_parameter("FOGSTART") or "0") * scale
        fogcolor = [float(x) / 255 for x in data.get_parameters("FOGCOLOR") or []]
        if len(fogcolor) == 3:
            bpy.context.scene.revolt_world_parameters.fogcolor = Color(fogcolor)
        
        # Gets startpos and startrot.
        startpos = [float(x) for x in data.get_parameters("STARTPOS") or []]
        startrot = float(data.get_parameter("STARTROT") or "0")
        if len(startpos) == 3:
            obj = add_revolt_startpos(bpy.context.scene.revolt_world_parameters.scale)
            obj.location = revolt_fix(startpos, scale)
            obj.rotation_euler = Euler((0, 0, -startrot * pi * 2), "XYZ")
            bpy.context.scene.revolt_world_parameters.startpos_object = obj.name
        
        fh.close()

# Imports a hitbox. (NCP-file)
def import_hitbox(filepath, scale):
    # Returns None if the file doesn't exist or if its filesize is 0 byte.
    if not os.path.isfile(filepath) or os.path.getsize(filepath) == 0:
        return None
        
    # Creates bmesh, opens file and reads the number of polyhedrons.
    bm = bmesh.new()
    fh = open(filepath, "rb")
    polyhedron_count = struct.unpack("h", fh.read(2))[0]
    material_layer = bm.faces.layers.int.new("revolt_material")
    
    # Loops through each polyhedron.
    for i in range(polyhedron_count):
        type, surface = struct.unpack("ll", fh.read(8))

        # Read some data.
        plane_data = [struct.unpack("ffff", fh.read(16)) for n in range(5)]
        bbox = struct.unpack("ffffff", fh.read(24))
        v = [Vector(plane[0:3]) for plane in plane_data]
        d = [plane[3] for plane in plane_data]
        
        # If first bit in type is 0 it's a tris otherwise it's a quad.
        plane_count = 3 if type % 2 == 0 else 4
        
        # Loops through each plane.
        vertices = []
        for n in range(plane_count):
            a = n + 1
            b = (n + 1) % plane_count + 1
            
            # Calculating plane-plane intersection. http://mathworld.wolfram.com/Plane-PlaneIntersection.html
            determinant = Matrix([v[0], v[a], v[b]]).determinant()
            if determinant != 0:
                pos = determinant**-1 * (-d[0] * v[a].cross(v[b]) + -d[a] * v[b].cross(v[0]) + -d[b] * v[0].cross(v[a]))
                vert = bm.verts.new(revolt_fix(pos, scale))
                vertices.insert(0, vert)
        
        # Creates a face if we've got 3 or more vertices.
        if len(vertices) >= 3:
            face = bm.faces.new(vertices)
            face[material_layer] = surface
            
    fh.close();
    
    obj = bmesh_to_object(bm, os.path.basename(filepath))
    obj.data.revolt.export_as_ncp = True
    return obj

# Imports world objects. (FIN-file)
def import_objects(filepath, scale, include_hitboxes):
    if os.path.isfile(filepath) == False or os.path.getsize(filepath) == 0:
        return
    
    # Opens file, splits the path and reads the number of objects.
    fh = open(filepath, "rb")
    path = "\\".join(re.split("[/\\\\]", fh.name)[:-1]) + "\\"
    object_count = struct.unpack("l", fh.read(4))[0]
    
    # Loops through each object.
    for i in range(object_count):
        
        # Reads som data.
        data = struct.unpack("ccccccccccccLccccfffffffffffff", fh.read(72))
        mesh_name = "".join([x.decode("ASCII") for x in data[:9]]).split("\x00")[0]
        
        # The path is incomplete sometimes due to limitations in the FIN-file format. Let's fix this!
        if os.path.isfile(path + mesh_name + ".prm"):
            mesh_path = path + mesh_name + ".prm"
        else:
            found_paths = glob.glob(path + mesh_name + "*.prm")
            mesh_path = found_paths[0] if len(found_paths) == 1 else None
        
        # If exactly one mesh matched the pattern.
        if mesh_path != None:
            mesh_name = bpy.path.basename(mesh_path)
            
            # If the mesh hasn't been loaded, load it or else make an object using the existing mesh.
            mesh = bpy.data.meshes.get(mesh_name)
            if mesh == None:
                obj = import_model(mesh_path, scale)
            else:
                obj = bpy.data.objects.new(mesh_name, mesh)
                bpy.context.scene.objects.link(obj)
            
            # Reads the matrix. Let's call revolt_fix to fix the coordinates.
            matrix = revolt_fix(Matrix(((data[21], data[24], data[27]), (data[22], data[25], data[28]), (data[23], data[26], data[29])))).to_4x4()
            
            # If the object was created sucessfully. Set its matrix and location.
            if obj != None:
                obj.matrix_local = matrix
                obj.location = revolt_fix(data[18:21], scale)
                
            # If we want to unclude hitboxes.
            if include_hitboxes:
                hitbox_name = os.path.splitext(mesh_name)[0] + ".ncp"
                hitbox = bpy.data.meshes.get(hitbox_name)
                
                # If the hitbox mesh hasn't been loaded, load it or else make an object using the existing hitbox mesh.
                if hitbox == None:
                    obj = import_hitbox(path + hitbox_name, scale)
                else:
                    obj = bpy.data.objects.new(hitbox_name, hitbox)
                    bpy.context.scene.objects.link(obj)
                
            # If the hitbox was created sucessfully. Hide it (because it's ugly!) and set its matrix + location.
            if obj != None:
                obj.hide = True
                obj.matrix_local = matrix
                obj.location = revolt_fix(data[18:21], scale)
            
    fh.close()

# Imports a car. (Parameters.txt)
def import_car(filepath, scale):
    car_parameters = bpy.context.scene.revolt_car_parameters
    fh = open(filepath, "r")
    
    # Split up path.
    path = re.split("[/\\\\]", fh.name)
    revolt_path = "\\".join(path[:-3]) + "\\"
    
    # Loops through each line until the first "{" is found.
    for line in fh:
        if "{" in line:
            break
    
    # Reads the paramater block.
    data = ParameterBlock(fh)
    
    # Sets some parameters.
    car_parameters.path = "\\".join(path[:-1]) + "\\"
    car_parameters.name = (data.get_parameter("Name") or "  ")[1:-1]
    car_parameters.engine_class = data.get_parameter("Class") or "0"
    car_parameters.steer_rate = float(data.get_parameter("SteerRate") or "0")
    
    # Loads the texture if it exists.
    texture_path = revolt_path + (data.get_parameter("TPAGE") or "  ")[1:-1]
    texture = bpy.data.images.load(texture_path) if os.path.isfile(texture_path) else None
    
    # Loops through each wheel and axle.
    for i in range(4):
        # Gets the wheel info. Continue with the next one if it wasn't found.
        wheel = data.blocks.get("WHEEL " + str(i))
        if wheel == None:
            continue
            
        model_path = data.get_parameter("MODEL", wheel.get_parameter("ModelNum"))
        
        # If the model path is defined.
        if model_path != None:
            model_path = revolt_path + model_path[1:-1]
            model_name = os.path.basename(model_path)
            
            # If a mesh with the same name is already loaded, then use it or else import the mesh.
            if bpy.data.meshes.get(model_name) != None:
                wheel_obj = bpy.data.objects.new(model_name, bpy.data.meshes[model_name])
                bpy.context.scene.objects.link(wheel_obj)
            else:
                wheel_obj = import_model(model_path, scale, texture)
            
            # If wheel was loaded successfully.
            if wheel_obj != None:
                # Sets the wheel name.
                wheel_obj.name = "WHEEL " + str(i)
                
                # Sets some parameters.
                wheel_parameters = car_parameters.get_wheel(i)
                wheel_parameters.object = wheel_obj.name
                wheel_parameters.is_present = wheel.get_parameter("IsPresent") == "TRUE"
                wheel_parameters.is_powered = wheel.get_parameter("IsPowered") == "TRUE"
                wheel_parameters.is_turnable = wheel.get_parameter("IsTurnable") == "TRUE"
                wheel_parameters.steer_ratio = float(wheel.get_parameter("SteerRatio") or "0")
                wheel_parameters.engine_ratio = float(wheel.get_parameter("EngineRatio") or "0")
                
                # Sets the location.
                location = wheel.get_parameters("Offset1")
                if location != None and len(location) == 3:
                    wheel_obj.location = revolt_fix([float(re.sub("[^0-9\.\+-]", "", x)) for x in location], scale)
        
        # Gets the axle info.
        axle = data.blocks.get("AXLE " + str(i))
        if axle != None:
            model_path = data.get_parameter("MODEL", axle.get_parameter("ModelNum"))
            
            # If the model path is defined.
            if model_path != None:
                model_path = revolt_path + model_path[1:-1]
                model_name = os.path.basename(model_path)
                
                # If a mesh with the same name is already loaded, then use it or else import the mesh.
                if bpy.data.meshes.get(model_name) != None:
                    axle_obj = bpy.data.objects.new(model_name, bpy.data.meshes[model_name])
                    bpy.context.scene.objects.link(axle_obj)
                else:
                    axle_obj = import_model(model_path, scale, texture)
                
                # If axle was loaded successfully.
                if axle_obj != None:
                    
                    # Sets the axle name.
                    axle_obj.name = "AXLE " + str(i)
                    
                    # Sets the location.
                    location = axle.get_parameters("Offset")
                    if location != None and len(location) == 3:
                        axle_obj.location = revolt_fix([float(re.sub("[^0-9\.\+-]", "", x)) for x in location], scale)
                    
                    # Set the axle to track the wheel.
                    track_constraint = axle_obj.constraints.new(type = "TRACK_TO")
                    track_constraint.target = wheel_obj
                    track_constraint.track_axis = "TRACK_NEGATIVE_Z"
                    track_constraint.up_axis = "UP_Y"
                    stretch_constraint = axle_obj.constraints.new(type = "STRETCH_TO")
                    stretch_constraint.target = wheel_obj
                    stretch_constraint.rest_length = 1
                    stretch_constraint.volume = "NO_VOLUME"
        
        # Gets the spring info.
        spring = data.blocks.get("SPRING " + str(i))
        if spring != None:
            model_path = data.get_parameter("MODEL", spring.get_parameter("ModelNum"))
            
            # If the model path is defined.
            if model_path != None:
                model_path = revolt_path + model_path[1:-1]
                model_name = os.path.basename(model_path)
                
                # If a mesh with the same name is already loaded, then use it or else import the mesh.
                if bpy.data.meshes.get(model_name) != None:
                    spring_obj = bpy.data.objects.new(model_name, bpy.data.meshes[model_name])
                    bpy.context.scene.objects.link(spring_obj)
                else:
                    spring_obj = import_model(model_path, scale, texture)
                
                # If spring was loaded successfully.
                if spring_obj != None:
                    
                    # Sets the spring name.
                    spring_obj.name = "SPRING " + str(i)
                    
                    # Sets the location.
                    location = spring.get_parameters("Offset")
                    if location != None and len(location) == 3:
                        spring_obj.location = revolt_fix([float(re.sub("[^0-9\.\+-]", "", x)) for x in location], scale)
                    
                    # Set the axle to track the wheel.
                    track_constraint = spring_obj.constraints.new(type = "TRACK_TO")
                    track_constraint.target = wheel_obj
                    track_constraint.track_axis = "TRACK_NEGATIVE_Z"
                    track_constraint.up_axis = "UP_Y"
            
                
    # Gets the body
    body = data.blocks.get("BODY")
    model_path = data.get_parameter("MODEL", body.get_parameter("ModelNum"))
    if body != None and model_path != None:
        obj = import_model(revolt_path + model_path[1:-1], scale, texture)
        
        # If the body was loaded sucessfully.
        if obj != None:
            obj.name = "BODY"
            car_parameters.body_object = obj.name
            
            # Sets the location.
            location = body.get_parameters("Offset")
            if location != None and len(location) == 3:
                obj.location = revolt_fix([float(re.sub("[^0-9\.]", "", x)) for x in location], scale)
    
    fh.close()

# Class used for reading a block from car parameters.
class ParameterBlock:
    def __init__(self, fh):
        self.blocks = {}
        self.params = []
    
        # Loops through each line.
        for line in fh:
        
            # Removes comment and strips additional spaces.
            line = line.split(";")[0].rstrip()
            if len(line) == 0:
                continue
            
            # Reads another block if the line contains a "{".
            if "{" in line:
                self.blocks[line[:line.index("{")].rstrip()] = ParameterBlock(fh)
                continue
            
            # Ends the block if the line contains a "}".
            if "}" in line:
                break
            
            # Parameters are split by one or more spaces.
            params = re.findall("(['\\\"].+['\\\"]|[^\s]+)", line)
            self.params.append(params)
            
    # Supply the params that you know and this method will return the rest. For example, to get the offset use block.get_value("OFFSET")
    def get_parameters(self, *keys):
        matches = [p for p in self.params if len(p) > len(keys) and all([p[i] == k for i, k in enumerate(keys)])]
        return matches[0][len(keys):] if len(matches) > 0 else None
        
    # Supply the params that you know and this method will return the following parameter. For example, to get the path to the first model use block.get_value("MODEL", "1")
    def get_parameter(self, *keys):
        matches = [p for p in self.params if len(p) > len(keys) and all([p[i] == k for i, k in enumerate(keys)])]
        return matches[0][len(keys)] if len(matches) > 0 else None

# Imports a convex hull. (HUL-file)
def import_convex_hull(filepath, scale):
    # Returns None if the file doesn't exist or if its filesize is 0 byte.
    if not os.path.isfile(filepath) or os.path.getsize(filepath) == 0:
        return None
        
    # Opens file and creates bmesh.
    fh = open(filepath, "rb")
    bm = bmesh.new()
    
    # Reads number of convex hulls.
    chull_count = struct.unpack("h", fh.read(2))[0]
    
    # Loops through each convex hull.
    for i in range(chull_count):
        vertex_count, edge_count, face_count = struct.unpack("hhh", fh.read(6))
        fh.read(36)
        
        # Loops through each vertex.
        for n in range(vertex_count):
            co = struct.unpack("fff", fh.read(12))
            bm.verts.new(revolt_fix(co, scale))
        
        bm.verts.ensure_lookup_table()
        
        # Loops through each edge.
        for n in range(edge_count):
            verts = [bm.verts[x] for x in struct.unpack("hh", fh.read(4))]
            if bm.edges.get(verts) == None:
                bm.edges.new(verts)
        
        # Loops through each face.
        for n in range(face_count):
            fh.read(16)
        
        sphere_count = struct.unpack("h", fh.read(2))[0]
        
        # Loops through each sphere.
        for n in range(sphere_count):
            sphere = struct.unpack("ffff", fh.read(16))
            location = revolt_fix(sphere[:3], scale)
            radius = sphere[-1] * scale
            bpy.ops.mesh.primitive_uv_sphere_add(location = location, size = radius)
    
    fh.close()
    return bmesh_to_object(bm, os.path.basename(filepath))

# Creates a Re-Volt start position used in levels.
def add_revolt_startpos(scale):
    bm = bmesh.new()
    grid = [[-200, 0], [200, 0], [-200, -320], [200, -320], [-200, -640], [200, -640], [-200, -960], [200, -960]]
    for pos in grid:
        bmesh.ops.create_cube(bm, matrix = Matrix(((60 * scale, 0, 0, pos[0] * scale), (0, 110 * scale, 0, pos[1] * scale), (0, 0, 30 * scale, 15 * scale), (0, 0, 0, 1))))
    return bmesh_to_object(bm, "Startpos")

# Creates a new object from supplied bmesh and links it to the current scene.
def bmesh_to_object(bm, name):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bm.to_mesh(mesh)
    bm.free()
    bpy.context.scene.objects.link(obj)
    return obj

# This function is used to get a complete path even though supplied path may be incomplete. Model names stored in FIN-files are limited to 9 characters so we need to find the best match.
def filepath_fix(filepath):
    if os.path.isfile(filepath):
        return filepath
    path, ext = os.path.splitext(filepath)
    found_files = glob.glob(path + "*" + ext)
    return found_files[0] if len(found_files) > 0 else None

# Rescales any kind of input to the supplied scale. This method also fixes the axes. (In Re-Volt the Y-axis is up and inverted. In Blender the Z-axis is up.)
def revolt_fix(input, scale = 1):
    t = type(input)
    if t in (Vector, list, tuple) and len(input) == 3:
        return Vector((input[0], input[2], -input[1])) * scale
    if t in (float, int):
        return input * scale
    if t is Matrix and len(input) >= 3:
        return Matrix(((input[0][0], input[0][2], -input[0][1]), (input[2][0], input[2][2], -input[2][1]), (-input[1][0], -input[1][2], input[1][1])))
        