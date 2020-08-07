import bpy
import os
import MagicMergeRun



class magic_OT_merge(bpy.types.Operator):
    bl_idname = "magic.merge"
    bl_label = "Magic Merge"
    
    def execute(self, context): 
        self.no_vertices_to_delete=[]
        self.no_vertices_deleted=[]       
        self.no_vertices_to_delete, self.no_vertices_deleted = MagicMergeRun.run(self.no_vertices_to_delete, self.no_vertices_deleted)
        while int(sum(self.no_vertices_deleted)) != int(self.no_vertices_to_delete[0]):
            MagicMergeRun.run(self.no_vertices_to_delete, self.no_vertices_deleted)
        bpy.ops.mesh.bridge_edge_loops()
        bpy.ops.mesh.remove_doubles()
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.mesh.vertices_smooth(factor=0.5)
        return {'FINISHED'}

def draw(self, _context):
    layout = self.layout
    layout.operator("magic.merge", text="Magic Merge")

def register():
    bpy.utils.register_class(magic_OT_merge)
    bpy.types.VIEW3D_MT_edit_mesh_merge.prepend(draw)
def unregister() :
    bpy.types.VIEW3D_MT_edit_mesh_merge.remove(draw)
    
if __name__ == "__main__":
    register()