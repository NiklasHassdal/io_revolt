# File specifications can be found here: http://www.perror.de/rv/rvstruct.html
# Re-Volt source code can be found here: http://revenant1.net/rvsource.rar

import bpy, struct, bmesh, mathutils, re, os, glob
from mathutils import Vector, Matrix, Color, Euler
from math import atan, pi

# Decodes a mesh and add decoded faces and vertices to supplied bmesh.
def decode_mesh(fh, bm, matrix, texture = None):
    # Split up path.
    path = fh.name.split(os.sep)
    is_world = os.path.splitext(fh.name)[1].upper() == ".W"
    
    # Gets/creates texture-, uv- and color layers.
    tex_lay = bm.faces.layers.tex.active or bm.faces.layers.tex.new("Texture")
    uv_lay = bm.loops.layers.uv.active or bm.loops.layers.uv.new("Uv")
    color_lay = bm.loops.layers.color.active or bm.loops.layers.color.new("Color")
    alpha_lay = bm.loops.layers.color.get("Alpha") or bm.loops.layers.color.new("Alpha")
    type_lay = bm.faces.layers.int.get("revolt_face_type") or bm.faces.layers.int.new("revolt_face_type")
    
    # Read some data from the file
    polygon_count, vertex_count = struct.unpack("<hh", fh.read(4))
    polygons = [struct.unpack("<hhhhhhBBBBBBBBBBBBBBBBffffffff", fh.read(60)) for x in range(polygon_count)]
    vertices = [bm.verts.new(Vector(struct.unpack("<ffffff", fh.read(24))[:3]) * matrix) for x in range(vertex_count)]
    
    # Loops through each polygon
    for data in polygons:
        vertex_indices = data[2:(5 if data[0] % 2 == 0 else 6)]
        if len(vertex_indices) == len(set(vertex_indices)) and bm.faces.get([vertices[i] for i in vertex_indices]) == None:
            polygon = bm.faces.new([vertices[i] for i in vertex_indices])
            polygon[type_lay] = data[0]
            
            if texture == None and data[1] >= 0:
                texture_name = path[-2].lower() + chr(97 + data[1]) + ".bmp"
                texture_path = os.sep.join(path[:-1]) + os.sep + texture_name
                
                image = bpy.data.images.get(texture_name)
                if image == None and os.path.isfile(texture_path):
                    image = bpy.data.images.load(texture_path)
                polygon[tex_lay].image = image
            else:
                polygon[tex_lay].image = texture
            
            for i in range(len(polygon.loops)):
                polygon.loops[i][uv_lay].uv = [data[22 + i * 2], 1 - data[23 + i * 2]]
                polygon.loops[i][color_lay] = Color(reversed([x / 255 for x in data[6 + i * 4:9 + i * 4]]))
                polygon.loops[i][alpha_lay] = Color([1 - (data[9 + i * 4]  / 255)] * 3)
            
            # The faces face the wrong way so the normal has to be flipped.
            polygon.normal_flip()

# Imports a mesh. (PRM-/M-file)
def get_mesh(filepath, matrix, texture_path = None):

    # Returns None if the file doesn't exist or if its filesize is 0 byte.
    if not os.path.isfile(filepath) or os.path.getsize(filepath) == 0:
        return None
    
    name = os.path.basename(filepath)
    
    # Returns already created mesh if there is one.
    if bpy.data.meshes.get(name):
        return bpy.data.meshes[name]
    
    # Creates mesh and decodes file.
    mesh = bpy.data.meshes.new(name)
    fh = open(filepath, "rb")
    bm = bmesh.new()
    decode_mesh(fh, bm, matrix, texture_path)
    fh.close()
    bm.to_mesh(mesh)
    return mesh

# Imports a model. (PRM-/M-file)
def import_model(filepath, matrix, texture_path = None):
    # Returns None if the file doesn't exist or if its filesize is 0 byte.
    if not os.path.isfile(filepath) or os.path.getsize(filepath) == 0:
        return None
        
    fh = open(filepath, "rb")
    bm = bmesh.new()
    decode_mesh(fh, bm, matrix, texture_path)
    fh.close()
    obj = bmesh_to_object(bm, os.path.basename(filepath))
    obj.data.revolt.export_as_prm = True
    return obj

# Imports a level/world. (W-file)
def import_world(filepath, matrix, include_models, include_objects, include_hitboxes, hide_hitboxes):
    # Exits if the file doesn't exist or if its filesize is 0 byte.
    if os.path.isfile(filepath) == False or os.path.getsize(filepath) == 0:
        return
    
    # Creates bmesh, opens the file and reads the number of meshes in the file
    bm = bmesh.new()
    fh = open(filepath, "rb")
    mesh_count = struct.unpack("<l", fh.read(4))[0]
    bpy.context.scene.revolt_world.path = os.path.dirname(fh.name)
    bpy.context.scene.revolt_world.matrix = matrix
    
    # Loops through each mesh.
    for i in range(mesh_count):
        fh.read(40)
        decode_mesh(fh, bm, matrix)
    
    # Reads FunnyBalls and unknown list.
    funnyball_count = struct.unpack("<l", fh.read(4))[0]
    for i in range(funnyball_count):
        fh.read(16)
        fh.read(4 * struct.unpack("<l", fh.read(4))[0])
    fh.read(4 * struct.unpack("<l", fh.read(4))[0])
    
    # Reads the EnvList. This is where the color for each face with EnvMapping is stored.
    envmapping_lay = bm.faces.layers.int.get("revolt_envmapping") or bm.faces.layers.int.new("revolt_envmapping")
    envmapping_color_lay = bm.faces.layers.int.get("revolt_envmapping_color") or bm.faces.layers.int.new("revolt_envmapping_color")
    
    # Closes file and create object form the bmesh.
    fh.close()
    world = bmesh_to_object(bm, os.path.basename(filepath))
    if world != None:
        world.data.revolt.export_as_w = True
    
    # Import objects if include_objects is True.
    if include_objects:
        import_world_objects(os.path.splitext(filepath)[0] + ".fob", matrix)
        
    # Import models if include_models is True.
    if include_models:
        import_world_models(os.path.splitext(filepath)[0] + ".fin", matrix, include_hitboxes)
        
    # Import hitbox if include_hitboxes is True.
    if include_hitboxes:
        hitbox = import_hitbox(os.path.splitext(filepath)[0] + ".ncp", matrix)
        if hitbox != None:
            hitbox.hide = hide_hitboxes
    
    # Imports startpos and some other stuff.
    inf_path = os.path.splitext(filepath)[0] + ".inf"
    if os.path.isfile(inf_path):
        fh = open(inf_path, "r")
        data = ParameterBlock(fh)
        bpy.context.scene.revolt_world.name = (data.get_parameter("NAME") or "  ")[1:-1]
        bpy.context.scene.revolt_world.farclip = float(data.get_parameter("FARCLIP") or "0") * min(matrix.to_scale())
        bpy.context.scene.revolt_world.fogstart = float(data.get_parameter("FOGSTART") or "0") * min(matrix.to_scale())
        fogcolor = [float(x) / 255 for x in data.get_parameters("FOGCOLOR") or []]
        if len(fogcolor) == 3:
            bpy.context.scene.revolt_world.fogcolor = Color(fogcolor)
        
        # Gets startpos and startrot.
        startpos = [float(x) for x in data.get_parameters("STARTPOS") or []]
        startrot = float(data.get_parameter("STARTROT") or "0")
        if len(startpos) == 3:
            obj = add_revolt_startpos(matrix)
            obj.location = Vector(startpos) * matrix
            obj.rotation_euler = Euler((0, 0, -startrot * pi * 2), "XYZ")
            bpy.context.scene.revolt_world.startpos_object = obj.name
        
        fh.close()

# Imports a hitbox. (NCP-file)
def import_hitbox(filepath, matrix):
    # Returns None if the file doesn't exist or if its filesize is 0 byte.
    if not os.path.isfile(filepath) or os.path.getsize(filepath) == 0:
        return None
        
    # Creates bmesh, opens file and reads the number of polyhedrons.
    bm = bmesh.new()
    fh = open(filepath, "rb")
    polyhedron_count = struct.unpack("<h", fh.read(2))[0]
    material_layer = bm.faces.layers.int.new("revolt_material")
    
    # Loops through each polyhedron.
    for i in range(polyhedron_count):
        type, surface = struct.unpack("<ll", fh.read(8))

        # Read some data.
        plane_data = [struct.unpack("<ffff", fh.read(16)) for n in range(5)]
        bbox = struct.unpack("<ffffff", fh.read(24))
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
                vert = bm.verts.new(Vector(pos) * matrix)
                vertices.insert(0, vert)
        
        # Creates a face if we've got 3 or more vertices.
        if len(vertices) >= 3:
            face = bm.faces.new(vertices)
            face[material_layer] = surface
            
    fh.close();
    
    obj = bmesh_to_object(bm, os.path.basename(filepath))
    obj.data.revolt.export_as_ncp = True
    return obj

# Imports world models. (FIN-file)
def import_world_models(filepath, matrix, include_hitboxes):
    if os.path.isfile(filepath) == False or os.path.getsize(filepath) == 0:
        return
    
    # Opens file, splits the path and reads the number of objects.
    fh = open(filepath, "rb")
    path = os.sep.join(fh.name.split(os.sep)[:-1]) + os.sep
    object_count = struct.unpack("<l", fh.read(4))[0]
    
    # Loops through each object.
    for i in range(object_count):
        
        # Reads some data.
        data = struct.unpack("<ccccccccccccLccccfffffffffffff", fh.read(72))

        # Decode the mesh name. For now expecing lowercase since it's the std for RVGL on Linux
        mesh_name = "".join([x.decode("ASCII").lower() for x in data[:9]]).split("\x00")[0]
        
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
                obj = import_model(mesh_path, matrix)
            else:
                obj = bpy.data.objects.new(mesh_name, mesh)
                bpy.context.scene.objects.link(obj)
            
            # If the object was created sucessfully. Set its matrix and location.
            if obj != None:
                v1 = Vector((data[21], data[24], data[27])) * matrix
                v2 = Vector((data[22], data[25], data[28])) * matrix
                v3 = Vector((data[23], data[26], data[29])) * matrix
                obj.matrix_local = Matrix((v1, v3, -v2)).to_4x4()
                obj.location = Vector(data[18:21]) * matrix
                obj.scale = Vector((1,1,1))
                
            # If we want to unclude hitboxes.
            if include_hitboxes:
                hitbox_name = os.path.splitext(mesh_name)[0] + ".ncp"
                hitbox = bpy.data.meshes.get(hitbox_name)
                
                # If the hitbox mesh hasn't been loaded, load it or else make an object using the existing hitbox mesh.
                if hitbox == None:
                    hitbox_obj = import_hitbox(path + hitbox_name, matrix)
                else:
                    hitbox_obj = bpy.data.objects.new(hitbox_name, hitbox)
                    bpy.context.scene.objects.link(hitbox_obj)
                
            # If the hitbox was created sucessfully. Hide it (because it's ugly!) and set its matrix + location.
            if hitbox_obj != None:
                hitbox_obj.hide = True
                hitbox_obj.matrix_local = obj.matrix_local
                hitbox_obj.location = Vector(data[18:21]) * matrix
            
    fh.close()

# Imports a car. (Parameters.txt)
def import_car(filepath, matrix):
    car_properties = bpy.context.scene.revolt_car
    fh = open(filepath, "r")
    
    # Split up path.
    path = fh.name.split(os.sep)
    revolt_path = os.sep.join(path[:-3]) + os.sep
    
    # Loops through each line until the first "{" is found.
    for line in fh:
        if "{" in line:
            break
    
    # Reads the paramater block.
    data = ParameterBlock(fh)
    
    # Sets some parameters.
    car_properties.path = os.sep.join(path[:-1]) + os.sep
    car_properties.name = (data.get_parameter("Name") or "  ")[1:-1]
    car_properties.engine_class = data.get_parameter("Class") or "0"
    car_properties.steer_rate = float(data.get_parameter("SteerRate") or "0")
    
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
                wheel_obj = import_model(model_path, matrix, texture)
            
            # If wheel was loaded successfully.
            if wheel_obj != None:
            
                # Sets some parameters.
                wheel_parameters = [car_properties.wheel0, car_properties.wheel1, car_properties.wheel2, car_properties.wheel3][i]
                wheel_parameters.object = wheel_obj.name
                wheel_parameters.is_present = wheel.get_parameter("IsPresent") == "TRUE"
                wheel_parameters.is_powered = wheel.get_parameter("IsPowered") == "TRUE"
                wheel_parameters.is_turnable = wheel.get_parameter("IsTurnable") == "TRUE"
                wheel_parameters.steer_ratio = float(wheel.get_parameter("SteerRatio") or "0")
                wheel_parameters.engine_ratio = float(wheel.get_parameter("EngineRatio") or "0")
                
                # Sets the location.
                location = wheel.get_parameters("Offset1")
                if location != None and len(location) == 3:
                    wheel_obj.location = Vector([float(re.sub("[^0-9\.\+-]", "", x)) for x in location]) * matrix
        
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
                    axle_obj = import_model(model_path, matrix, texture)
                
                # If axle was loaded successfully.
                if axle_obj != None:
                    
                    # Sets the location.
                    location = axle.get_parameters("Offset")
                    if location != None and len(location) == 3:
                        axle_obj.location = Vector([float(re.sub("[^0-9\.\+-]", "", x)) for x in location]) * matrix
                    
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
                    spring_obj = import_model(model_path, matrix, texture)
                
                # If spring was loaded successfully.
                if spring_obj != None:
                    
                    # Sets the location.
                    location = spring.get_parameters("Offset")
                    if location != None and len(location) == 3:
                        spring_obj.location = Vector([float(re.sub("[^0-9\.\+-]", "", x)) for x in location]) * matrix
                    
                    # Set the axle to track the wheel.
                    track_constraint = spring_obj.constraints.new(type = "TRACK_TO")
                    track_constraint.target = wheel_obj
                    track_constraint.track_axis = "TRACK_NEGATIVE_Z"
                    track_constraint.up_axis = "UP_Y"
            
                
    # Gets the body
    body = data.blocks.get("BODY")
    model_path = data.get_parameter("MODEL", body.get_parameter("ModelNum"))
    if body != None and model_path != None:
        obj = import_model(revolt_path + model_path[1:-1], matrix, texture)
        
        # If the body was loaded sucessfully.
        if obj != None:
            car_properties.body_object = obj.name
            
            # Sets the location.
            location = body.get_parameters("Offset")
            if location != None and len(location) == 3:
                obj.location = Vector([float(re.sub("[^0-9\.]", "", x)) for x in location]) * matrix
    
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

            # Also make all paths lowercase and replace \ with the local separator
            self.params.append([param.lower().replace('\\', os.sep) for param in params])
            
    # Supply the params that you know and this method will return the rest. For example, to get the offset use block.get_value("OFFSET")
    def get_parameters(self, *keys):
        matches = [p for p in self.params if len(p) > len(keys) and all([p[i].upper() == k.upper() for i, k in enumerate(keys)])]
        return matches[0][len(keys):] if len(matches) > 0 else None
        
    # Supply the params that you know and this method will return the following parameter. For example, to get the path to the first model use block.get_value("MODEL", "1")
    def get_parameter(self, *keys):
        matches = [p for p in self.params if len(p) > len(keys) and all([p[i].upper() == k.upper() for i, k in enumerate(keys)])]
        return matches[0][len(keys)] if len(matches) > 0 else None

# Imports world objects. (FOB-file)
def import_world_objects(filepath, matrix):
    
    # Returns None if the file doesn't exist or if its filesize is 0 byte.
    if not os.path.isfile(filepath) or os.path.getsize(filepath) == 0:
        return None
    
    # Model paths for planets.
    planet_models = [
        "models" + os.sep + "mercury.m",
        "models" + os.sep + "venus.m",
        "models" + os.sep + "earth.m",
        "models" + os.sep + "mars.m",
        "models" + os.sep + "jupiter.m",
        "models" + os.sep + "saturn.m",
        "models" + os.sep + "uranus.m",
        "models" + os.sep + "neptune.m",
        "models" + os.sep + "pluto.m",
        "models" + os.sep + "moon.m",
        "models" + os.sep + "rings.m"
        ]
        
    revolt_path = os.sep.join(filepath.split(os.sep)[:-3]) + os.sep
    object_types = [item[0] for item in bpy.types.RevoltObjectProperties.object_type[1]["items"]]
    
    fh = open(filepath, "rb")
    object_count = struct.unpack("<l", fh.read(4))[0]
    for i in range(object_count):
        data = struct.unpack("<lllllfffffffff", fh.read(56))
        if data[0] + 1 < len(object_types):
            up = (-Vector(data[8:11]) * matrix).normalized()
            forward = (Vector((data[11:14])) * matrix).normalized()
            right = forward.cross(up)
            obj_matrix = Matrix(((right.x, forward.x, up.x), (right.y, forward.y, up.y), (right.z, forward.z, up.z))).to_4x4()
            object_type = object_types[data[0] + 1]
            
            mesh = None
            
            if object_type == "OBJECT_TYPE_BARREL":
                mesh = get_mesh(revolt_path + "models" + os.sep + "barrel.m", matrix)
            
            elif object_type == "OBJECT_TYPE_FOOTBALL":
                mesh = get_mesh(revolt_path + "models" + os.sep + "football.m", matrix)
                
            elif object_type == "OBJECT_TYPE_BEACHBALL":
                mesh = get_mesh(revolt_path + "models" + os.sep + "beachball.m", matrix)
            
            elif object_type == "OBJECT_TYPE_PLANET" and data[1] != 11:
                mesh = get_mesh(revolt_path + planet_models[data[1]], matrix)

            elif object_type == "OBJECT_TYPE_PLANE":
                mesh = get_mesh(revolt_path + "models" + os.sep + "plane.m", matrix)
                
            elif object_type == "OBJECT_TYPE_COPTER":
                mesh = get_mesh(revolt_path + "models" + os.sep + "copter.m", matrix)
                
            elif object_type == "OBJECT_TYPE_DRAGON":
                mesh = get_mesh(revolt_path + "models" + os.sep + "dragon1.m", matrix)
                
            elif object_type == "OBJECT_TYPE_WATER":
                mesh = get_mesh(revolt_path + "models" + os.sep + "water.m", matrix)
                
            elif object_type == "OBJECT_TYPE_TROLLEY":
                mesh = get_mesh(revolt_path + "models" + os.sep + "trolley.m", matrix)
                
            elif object_type == "OBJECT_TYPE_BOAT":
                mesh = get_mesh(revolt_path + "models" + os.sep + "boat1.m", matrix)
                
            elif object_type == "OBJECT_TYPE_RADAR":
                mesh = get_mesh(revolt_path + "models" + os.sep + "radar.m", matrix)
                
            elif object_type == "OBJECT_TYPE_SPEEDUP":
                mesh = get_mesh(revolt_path + "models" + os.sep + "speedup.m", matrix)
                
            elif object_type == "OBJECT_TYPE_BALOON":
                mesh = get_mesh(revolt_path + "models" + os.sep + "baloon.m", matrix)
                
            elif object_type == "OBJECT_TYPE_HORSE":
                mesh = get_mesh(revolt_path + "models" + os.sep + "horse.m", matrix)
                
            elif object_type == "OBJECT_TYPE_TRAIN":
                mesh = get_mesh(revolt_path + "models" + os.sep + "train.m", matrix)
                
            elif object_type == "OBJECT_TYPE_STROBE":
                mesh = get_mesh(revolt_path + "models" + os.sep + "light1.m", matrix)
                
            elif object_type == "OBJECT_TYPE_SPACEMAN":
                mesh = get_mesh(revolt_path + "models" + os.sep + "spaceman.m", matrix)
                
            elif object_type == "OBJECT_TYPE_PICKUP":
                mesh = get_mesh(revolt_path + "models" + os.sep + "pickup.m", matrix)
                
            elif object_type == "OBJECT_TYPE_FLAP":
                mesh = get_mesh(revolt_path + "models" + os.sep + "flap.m", matrix)
                
            obj = bpy.data.objects.new(object_type, mesh)
            obj.empty_draw_type = "ARROWS"
            obj.matrix_local = obj_matrix
            obj.location = Vector(data[5:8]) * matrix
            obj.revolt.type = "OBJECT"
            obj.revolt.object_type = object_type
            obj.revolt.flag1_long = data[1]
            obj.revolt.flag2_long = data[2]
            obj.revolt.flag3_long = data[3]
            obj.revolt.flag4_long = data[4]
            bpy.context.scene.objects.link(obj)
            
    fh.close()

# Creates a Re-Volt start position used in levels.
def add_revolt_startpos(matrix):
    bm = bmesh.new()
    grid = [[-200, 0], [200, 0], [-200, -320], [200, -320], [-200, -640], [200, -640], [-200, -960], [200, -960]]
    mat = matrix.copy()
    mat.invert()
    for pos in grid:
        bmesh.ops.create_cube(bm, matrix = Matrix(((60, 0, 0, pos[0]), (0, 0, 110, pos[1]), (0, -30, 0, 15), (0, 0, 0, 1))) * matrix)
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