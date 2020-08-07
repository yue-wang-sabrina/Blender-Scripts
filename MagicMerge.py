import bpy
import bmesh
import numpy

### Identify the 2 edgeloops selected
no_vertices_to_delete=[]
no_vertices_deleted=[]


def run():
    active_obj = bpy.context.active_object
    if bpy.context.mode == 'EDIT_MESH':
        bm = bmesh.from_edit_mesh(active_obj.data)
    else:
        bpy.ops.object.editmode_toggle()
        
    active_vertices=[i for i in bm.verts if i.select]

    loopdict={}

    for v in active_vertices:
        loopdict['{}'.format(v)]=[]
        for e in v.link_edges:
            v_other = e.other_vert(v)
            if v_other in active_vertices:
                loopdict['{}'.format(v)].append(v_other)

    loop1=[]
    continue_BOOL=True
    loop_sort=[active_vertices[0]]

    while continue_BOOL == True:
        loop_sort_new=[]
        for loop in loop_sort:
            loop1.append(loop)
            for item in loopdict['{}'.format(loop)]:
                loop_sort_new.append(item)
        loop_sort_new=list(set(loop_sort_new))
        
        remove_list=[]
        for item in loop_sort_new:
            if item in loop1:
                remove_list.append(item)
        remove_list=list(set(remove_list))
        loop_sort_new=[item for item in loop_sort_new if item not in remove_list]
        if len(loop_sort_new)!=0:
            loop_sort=loop_sort_new
            continue_BOOL=True
        else:
            continue_BOOL=False

    loop2=[vertex for vertex in active_vertices if vertex not in loop1]

    #print(len(loop1),len(loop2))

    ### decimate the edgeloop with more vertices
    loop_to_decimate = [len(loop1),len(loop2)].index(max([len(loop1),len(loop2)]))
    no_vertices_to_delete.append(int(abs(len(loop1)-len(loop2))))
    def magic_merge(loop1,loop2,direction):
        l_loop=loop1
        s_loop=loop2
        #Pair up vertices closest to each other from the 2 loops
        pairdict={}
        vertices_paired=[]
        for vertex1 in s_loop:
            distances=[]
            for vertex2 in l_loop:
                distances.append(numpy.linalg.norm(vertex1.co-vertex2.co))

            pairdict['{}'.format(vertex1)] = l_loop[distances.index(min(distances))]
    #        TODO: WRITE a while loop to make sure its a 1-1 connection?!
            vertices_paired.append(l_loop[distances.index(min(distances))])
        vertices_unpaired = [item for item in l_loop if item not in vertices_paired]
        assert len(vertices_unpaired)%2 == 0
        vertices_tomerge=[]
        edge_delete_vertices=[]

        for item in vertices_unpaired:
            connected_vertices = [e.other_vert(item) for e in item.link_edges]
            connected_vertices = list(set(connected_vertices).intersection(set(active_vertices)))
            connected_vertices_neighbour= [e.other_vert(connected_vertices[direction]) for e in connected_vertices[direction].link_edges]
            connected_vertices_neighbour = list(set(connected_vertices_neighbour).intersection(set(active_vertices)))
            if connected_vertices_neighbour[0] == item:
                third_vertex = connected_vertices_neighbour[1]
            elif connected_vertices_neighbour[1] == item:
                third_vertex = connected_vertices_neighbour[0]
            if item.index not in vertices_tomerge and third_vertex.index not in vertices_tomerge and connected_vertices[direction].index not in vertices_tomerge:
                if len(vertices_tomerge) < int(3*len(vertices_unpaired)/2):
                    vertices_tomerge.append(item.index)
                    vertices_tomerge.append(third_vertex.index)
                    vertices_tomerge.append(connected_vertices[direction].index)
                    edge_end_vertex=[e.other_vert(connected_vertices[direction]) for e in connected_vertices[direction].link_edges]
                    edge_end_vertex=[v_wanted for v_wanted in edge_end_vertex if v_wanted not in active_vertices]
                    assert len(edge_end_vertex)==1
                    edge_delete_vertices.append([connected_vertices[direction],edge_end_vertex[0]])
                    item.co += connected_vertices[direction].co - item.co
                    third_vertex.co += connected_vertices[direction].co - third_vertex.co 

        no_vertices_deleted.append(len(vertices_tomerge)*2/3)
        edges_vertex = [[i.verts[0],i.verts[1]] for i in bm.edges]
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        edges_delete=[]

        for pair in edge_delete_vertices:
           if pair in edges_vertex:
               index_del = edges_vertex.index(pair)
               edges_delete.append(bm.edges[index_del])
           elif pair[::-1] in edges_vertex:
               index_del=edges_vertex.index(pair[::-1])
               edges_delete.append(bm.edges[index_del])

        for item in edges_delete:
            bmesh.ops.dissolve_edges(bm,edges=[item])
            
        bpy.ops.mesh.remove_doubles()
        
    if loop_to_decimate == 0 :
        magic_merge(loop1,loop2,1)
        
    else:
        magic_merge(loop2,loop1,1)
        
#    bpy.ops.mesh.bridge_edge_loops()

run()
while int(sum(no_vertices_deleted)) != int(no_vertices_to_delete[0]):
        run()
bpy.ops.mesh.bridge_edge_loops()
bpy.ops.mesh.remove_doubles()
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.mesh.vertices_smooth(factor=0.5)