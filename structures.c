struct PRM_Mesh {

  rvshort polygon_count;
  rvshort vertex_count;

  Polygon polygons[polygon_count];
  Vertex  vertices[vertex_count];
};

struct World {

  rvlong       mesh_count;
  Mesh         meshes[mesh_count];
  
  rvlong       bigcube_count;
  BigCube      bcube[bigcube_count];

  rvlong       animation_count; 
  TexAnimation anim[animation_count]

  EnvList   env_list;
};

struct Mesh {
    
  Vector       bound_ball_center;
  rvfloat      bound_ball_radius;

  BoundingBox  bbox;

  rvshort      polygon_count;
  rvshort      vertex_count;

  Polygon      polygons[polygon_count];
  Vertex       vertices[vertex_count];
};

struct TexAnimation {

  rvlong frame_count; // the number of frames per animation
  Frame  frames[animation_count]
};

struct Frame {

  rvlong  texture;
  rvfloat delay; // in microseconds
  UV      uv[4];
};

struct Polygon {

           rvshort  type;

           rvshort  texture;

           rvshort  vertex_indices[4];
  unsigned rvlong   colors[4];

           UV       texcoord[4];
};


struct Vertex {

  Vector position;
  Vector normal;
};

struct Vector {

  rvfloat x;
  rvfloat y;
  rvfloat z;
};

struct UV {

  rvfloat u;
  rvfloat v;
};

struct BigCube {

  Vector  center;
  rvfloat radius;

  rvlong  mesh_count;
  rvlong  mesh_indices[mesh_count];
};

struct WorldNCP {

  rvshort    polyhedron_count;
  Polyhedron polyhedra[polyhedron_count];

  LookupGrid lookup;
};

struct Polyhedron {

  rvlong      type;
  rvlong      surface;

  Plane       plane[5];

  BoundingBox bbox;
};

struct Plane {

  Vector  normal;
  rvfloat distance;
};

struct LookupGrid {

  rvfloat    x0;
  rvfloat    z0;

  rvfloat    x_size;
  rvfloat    z_size;

  rvfloat    raster_size;

  LookupList lists[z_size][x_size];
};

struct LookupList {

  rvlong length;
  rvlong polyhedron_indices[length];
};

struct EnvList {

  unsigned rvlong env_color[number of bit-11-polys in file];
};


struct BoundingBox {

  rvfloat xlo, xhi;
  rvfloat ylo, yhi;
  rvfloat zlo, zhi;
};

struct POR_File {

  rvlong    entry_count;
  POR_Entry entries[entry_count];
};

struct POR_Entry {

  rvulong  type;
  rvulong  id[2];
  Vector   center;
  rvfloat  rotation_matrix[3][3];
  Vector   size;

  rvfloat  zeroes[4];
};

struct RIM_File {

  rvshort   entry_count;

  RIM_Entry entries[entry_count];
};

struct RIM_Entry {
  rvulong     flags;

  Vector      plane_normal;
  rvfloat     plane_distance;

  BoundingBox bbox;

  Vector      vertices[4];
};
