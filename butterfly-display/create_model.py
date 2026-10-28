import bpy, math, os, struct, zipfile
from mathutils import Vector
from xml.sax.saxutils import escape

OUT=os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
groups={'Black':[], 'White':[]}
def add(o, color):
    groups[color].append(o); return o
def ball(p,r,color,scale=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=r,location=p)
    o=bpy.context.object
    if scale: o.scale=scale
    return add(o,color)
def tube(points,r,color):
    c=bpy.data.curves.new('rounded detail','CURVE'); c.dimensions='3D'; c.resolution_u=12
    c.bevel_depth=r; c.bevel_resolution=3; c.use_fill_caps=True
    s=c.splines.new('POLY'); s.points.add(len(points)-1)
    for v,p in zip(s.points,points): v.co=(*p,1)
    o=bpy.data.objects.new('detail',c); bpy.context.collection.objects.link(o); return add(o,color)
def cylinder(r,depth,z,color):
    bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=r,depth=depth,location=(0,0,z)); return add(bpy.context.object,color)
def petal(center, direction, length, width, depth, color):
    # Closed ellipsoid, with its long axis oriented in the butterfly plane.
    o=ball(center,1,color,(width,depth,length))
    o.rotation_euler[1]=direction
    return o

# Dimensions are millimeters. The display lies in X/Z, facing negative Y.
cylinder(5,7.4,3.7,'Black'); cylinder(31.75,3,1.5,'Black'); cylinder(31.75,1.2,3.6,'White'); cylinder(31.75,3.2,5.8,'Black')
# Stem and scrolls support the body and both lower wings.
tube([(0,2,6),(0,2,17),(0,1,27),(0,0,43)],2.4,'Black')
for side in [-1,1]:
    pts=[]
    for i in range(101):
        t=i/100; a=-math.pi/2+t*math.pi*3.0; r=11*(1-t)+1
        pts.append((side*(12+r*math.cos(a)),1,17+r*math.sin(a)))
    tube(pts,1.25,'Black')
    tube([(side*12,1,6),(side*19,1,13),(side*23,1,24),(side*19,0,29)],1.4,'Black')

# Petal-shaped wing cells: white centers surrounded by black structural ribs.
# Each wing is curved in depth and has a continuous perimeter.
def wing(side, upper):
    root=Vector((side*2,0,43 if upper else 40))
    tip=Vector((side*(35 if upper else 26),4 if upper else 2,72 if upper else 24))
    # Fan of closed cells creates a scalloped silhouette with solid 1.4 mm ribs.
    endpoints=[]
    for i in range(7 if upper else 6):
        t=i/(6 if upper else 5)
        if upper:
            end=Vector((side*(12+23*math.sin(t*math.pi*0.7)),3+3*t,65+14*math.sin(math.pi*t)-21*t))
        else:
            end=Vector((side*(27-17*t),2+2*t,36-15*math.sin(t*math.pi/2)))
        endpoints.append(end)
        axis=end-root; length=axis.length
        u=axis.normalized(); v=Vector((u.z,0,-u.x)).normalized()
        width=(3.0 if upper else 3.2)*(0.85+0.15*math.sin(math.pi*t))
        # A tapered loop with rounded, thick printed edges.
        loop=[]
        for j in range(65):
            a=2*math.pi*j/64
            along=(1-math.cos(a))/2
            p=root+axis*along+v*(width*math.sin(a)*math.sin(math.pi*along)**0.35)
            loop.append(tuple(p))
        tube(loop,0.85,'Black')
        # Solid white inset, a triangulated lens, 1.2 mm deep.
        verts=[]
        for dy in [-0.65,0.65]:
            for p in loop[:-1]: verts.append((p[0],p[1]+dy,p[2]))
        n=64; faces=[]
        faces.append(tuple(range(n-1,-1,-1))); faces.append(tuple(range(n,2*n)))
        for j in range(n): faces.append((j,(j+1)%n,(j+1)%n+n,j+n))
        mesh=bpy.data.meshes.new('wing inset'); mesh.from_pydata(verts,[],faces); mesh.update()
        o=bpy.data.objects.new('ivory wing cell',mesh); bpy.context.collection.objects.link(o); add(o,'White')
        # Border beads sit outside the cell and overlap its black rim.
        if i>0: ball(tuple(end+Vector((0,-0.6,0))),1.1,'White')
    # Rounded perimeter joins fan cells into a continuous butterfly wing.
    nodes=[root]+endpoints+[root]
    outline=[]
    for k in range(len(nodes)-1):
        p0=nodes[max(0,k-1)]; p1=nodes[k]; p2=nodes[k+1]; p3=nodes[min(len(nodes)-1,k+2)]
        for j in range(12):
            t=j/12
            q=0.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)
            outline.append(tuple(q))
    outline.append(tuple(root)); tube(outline,1.05,'Black')

for side in [-1,1]:
    wing(side,True); wing(side,False)

petal((0,-1,40),0,11,2.6,2.6,'Black')
ball((0,-1,52),3,'Black')
for z in range(32,49,3):
    ball((0,-1.1,z),1,'Black',(2.7,2.7,1.2))
for side in [-1,1]:
    tube([(side*(1.2+5.5*t),-1,54+12*t-2*t*t) for t in [i/32 for i in range(33)]],0.7,'Black')
    ball((side*6.7,-1,64),1.1,'White')
    ball((side*1.5,-3.5,52.7),0.7,'Black')

# Sculpted roses: solid cupped petals, joined into a printable bloom.
def rose(x,y,z,r):
    ball((x,y+1,z),r*0.63,'Black',(1,0.6,0.75))
    for layer,count in [(0,7),(1,6),(2,5),(3,3)]:
        radius=r*(0.72-0.17*layer)
        for j in range(count):
            a=2*math.pi*j/count+layer*0.7
            # Curved, thick rose petals, cupped toward the front of the display.
            verts=[]; faces=[]; nu=16; nv=8
            outer=r*(1.0-0.22*layer)
            for thickness in [-0.5,0.5]:
                for iv in range(nv+1):
                    v=iv/nv
                    for iu in range(nu+1):
                        u=iu/nu; theta=a+(u-0.5)*(1.45 if layer<2 else 2.1)+0.30*v
                        radial=outer*(0.20+0.80*v)*(0.88+0.12*math.sin(math.pi*u))
                        yy=y-0.8*layer-2.8*v*v+0.9*math.sin(math.pi*u)*math.sin(math.pi*v)+thickness
                        verts.append((x+radial*math.cos(theta),yy,z+radial*math.sin(theta)))
            n=(nu+1)*(nv+1)
            for k in [0,1]:
                for iv in range(nv):
                    for iu in range(nu):
                        q=k*n+iv*(nu+1)+iu
                        f=(q,q+1,q+nu+2,q+nu+1)
                        faces.append(f if k==0 else tuple(reversed(f)))
            border=list(range(nu+1))+[iv*(nu+1)+nu for iv in range(1,nv+1)]+[nv*(nu+1)+iu for iu in range(nu-1,-1,-1)]+[iv*(nu+1) for iv in range(nv-1,0,-1)]
            for k,q in enumerate(border):
                q2=border[(k+1)%len(border)]; faces.append((q,q+n,q2+n,q2))
            mesh=bpy.data.meshes.new('cupped rose petal'); mesh.from_pydata(verts,[],faces); mesh.update()
            o=bpy.data.objects.new('rose petal',mesh); bpy.context.collection.objects.link(o); add(o,'Black')

    ball((x,y-2.5,z),r*0.17,'Black')
rose(0,-11,15,8.4); rose(-15,-8,11,5.8); rose(15,-11,10,6)
for side in [-1,1]:
    for j in range(3):
        o=petal((side*(10+j*5),-6,8+j*1.5),side*(0.8+j*0.3),4.7,1.8,1,'Black')

# Fuse every color independently, retaining white inserts as separately assignable parts.
final={}
for color,objects in groups.items():
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects: o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.object.convert(target='MESH'); bpy.ops.object.join()
    o=bpy.context.object; o.name=color
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    rem=o.modifiers.new('Fuse printable solids','REMESH'); rem.mode='VOXEL'; rem.voxel_size=0.25; rem.use_smooth_shade=True
    bpy.ops.object.modifier_apply(modifier=rem.name)
    final[color]=o

# Remove tiny disconnected voxel debris from each material.
import bmesh
def clean_small_islands(o):
    bm=bmesh.new(); bm.from_mesh(o.data); unseen=set(bm.verts); discard=[]
    while unseen:
        v=unseen.pop(); stack=[v]; component=[v]
        while stack:
            v=stack.pop()
            for e in v.link_edges:
                w=e.other_vert(v)
                if w in unseen: unseen.remove(w); stack.append(w); component.append(w)
        if len(component)<100: discard.extend(component)
    bmesh.ops.delete(bm,geom=discard,context='VERTS'); bm.to_mesh(o.data); bm.free()
for o in final.values(): clean_small_islands(o)

# Remove the black/white overlap from white so slicers see exclusive material volumes.
white=final['White']; black=final['Black']
bpy.context.view_layer.objects.active=white
mod=white.modifiers.new('Material interface','BOOLEAN'); mod.operation='DIFFERENCE'; mod.solver='EXACT'; mod.object=black
bpy.ops.object.modifier_apply(modifier=mod.name)
clean_small_islands(white)

materials={}
for color,rgb in [('Black',(0.018,0.018,0.022,1)),('White',(0.92,0.89,0.80,1))]:
    m=bpy.data.materials.new(color); m.diffuse_color=rgb; m.use_nodes=True
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=rgb
    m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=0.32
    final[color].data.materials.clear(); final[color].data.materials.append(m)
    o=final[color]; mesh=o.data; mesh.calc_loop_triangles()
    with open(os.path.join(OUT,color.lower()+'.stl'),'wb') as f:
        f.write(b'Butterfly display - millimeters'.ljust(80,b' ')); f.write(struct.pack('<I',len(mesh.loop_triangles)))
        for tri in mesh.loop_triangles:
            pts=[o.matrix_world@mesh.vertices[i].co for i in tri.vertices]
            normal=(pts[1]-pts[0]).cross(pts[2]-pts[0]).normalized()
            f.write(struct.pack('<12fH',*normal,*pts[0],*pts[1],*pts[2],0))

# Portable multi-part 3MF; Orca can assign the two objects to U1 tools.
xml=['<?xml version="1.0" encoding="UTF-8"?>','<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources>','<basematerials id="1"><base name="Black PLA" displaycolor="#080809FF"/><base name="Ivory PLA" displaycolor="#EBE3CCFF"/></basematerials>']
for idx,(color,o) in enumerate(final.items()):
    mesh=o.data; mesh.calc_loop_triangles()
    xml.append(f'<object id="{idx+2}" name="{color}" type="model" pid="1" pindex="{idx}"><mesh><vertices>')
    for v in mesh.vertices:
        p=o.matrix_world@v.co; xml.append(f'<vertex x="{p.x:.5f}" y="{p.y:.5f}" z="{p.z:.5f}"/>')
    xml.append('</vertices><triangles>')
    for t in mesh.loop_triangles: xml.append(f'<triangle v1="{t.vertices[0]}" v2="{t.vertices[1]}" v3="{t.vertices[2]}"/>')
    xml.append('</triangles></mesh></object>')
xml.append('<object id="4" type="model" name="Butterfly and roses"><components><component objectid="2"/><component objectid="3"/></components></object></resources><build><item objectid="4"/></build></model>')
with zipfile.ZipFile(os.path.join(OUT,'butterfly-display.3mf'),'w',zipfile.ZIP_DEFLATED) as f:
    f.writestr('[Content_Types].xml','<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    f.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    f.writestr('3D/3dmodel.model',''.join(xml))

# Report actual topology rather than inferring validity from file export.
import bmesh, json
report={}
for color,o in final.items():
    bm=bmesh.new(); bm.from_mesh(o.data)
    report[color]={'vertices':len(bm.verts),'faces':len(bm.faces),'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_mm3':abs(bm.calc_volume())}
    bm.free()
points=[o.matrix_world@Vector(c) for o in final.values() for c in o.bound_box]
report['dimensions_mm']=[max(p[i] for p in points)-min(p[i] for p in points) for i in range(3)]
with open(os.path.join(OUT,'validation.json'),'w') as f: json.dump(report,f,indent=2)
print(report,flush=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'butterfly-display.blend'))

# Render an honest preview of the exported geometry.
world=bpy.context.scene.world; world.color=(0.3,0.3,0.3)
bpy.ops.object.camera_add(location=(105,-170,100)); cam=bpy.context.object
cam.rotation_euler=(Vector((0,0,37))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=95
scene=bpy.context.scene; scene.camera=cam
for loc,power,size in [((30,-80,120),180000,70),((-70,-30,70),100000,60),((0,60,90),150000,50)]:
    bpy.ops.object.light_add(type='AREA',location=loc); light=bpy.context.object; light.data.energy=power; light.data.shape='DISK'; light.data.size=size
    light.rotation_euler=(Vector((0,0,35))-light.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='CYCLES'; scene.cycles.samples=32; scene.cycles.use_denoising=False
scene.render.resolution_x=900; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.render.filepath=os.path.join(OUT,'preview.png'); bpy.ops.render.render(write_still=True)
