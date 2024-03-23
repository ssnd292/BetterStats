bl_info = {
    "name" : "Better Stats",
    "author" : "Sebastian Schneider",
    "description" : "Replacement for the original Statistics. Currently only works in Object Mode",
    "blender" : (3, 6, 0),
    'version': (0, 1, 0 ,1),
    "location" : "View3D",
    "warning" : "",
    "category" : "View3D",
    'wiki_url': 'https://github.com/ssnd292/BetterStats'
}

import bpy
import blf

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )

winman = bpy.types.WindowManager
overlay = bpy.types.VIEW3D_PT_overlay

font_id = 0

position_1920px = (0.045,0.75)
position_2560px = (0.0342,0.81)
position_3840px = (0.0234,0.872)
position = (0,0)

gap = 22
system = bpy.context.preferences.system
dpi = int(system.dpi * system.pixel_size)



class BetterStatsHandler:
    def __init__(self, context, prop, obj):
        self.obj = obj
        self.selected_objects = ""
        self.obj_count = 0
        self.total_obj_count = 0
        self.vtx_count = 0
        self.vtx_normal_count = 0
        self.uv_vtx_count = 0
        self.tri_count = 0
        self.screen_width = 0
        self.screen_height = 0
        self.screen_position = (0,0)
        self.font_size = context.window_manager.betterstats_font_size
        self.font_color = context.window_manager.betterstats_font_color
        
        self.gap = 25
        self.draw_better_stats = bpy.types.SpaceView3D.draw_handler_add(self.draw_better_stats,(context,),'WINDOW', 'POST_PIXEL')
        self.depsgraph_handle = bpy.app.handlers.depsgraph_update_post.append(self.onDepsgraph)

    def onDepsgraph(self, scene, depsgraph):
        self.screen_width = 0
        self.screen_height = 0
        self.selected_objects = ""
        self.obj_count = 0
        self.total_obj_count = 0
        self.vtx_count = 0
        self.vtx_normal_count = 0
        self.uv_vtx_count = 0
        self.tri_count = 0

        selection = bpy.context.selected_objects

        # Get Window Size

        for window in bpy.context.window_manager.windows:
            self.screen_width = window.width
            self.screen_height = window.height

        if self.screen_width > 2160:
            for window in bpy.context.window_manager.windows:
                self.screen_width = window.width
                self.screen_height = window.height
            self.screen_position = (self.screen_width * position_3840px[0], self.screen_height * position_3840px[1])
        if self.screen_width < 3840 and self.screen_width > 1920:
            for window in bpy.context.window_manager.windows:
                self.screen_width = window.width
                self.screen_height = window.height
            self.screen_position = (self.screen_width * position_2560px[0], self.screen_height * position_2560px[1])
        if self.screen_width == 1920:
            for window in bpy.context.window_manager.windows:
                self.screen_width = window.width
                self.screen_height = window.height
            self.screen_position = (self.screen_width * position_1920px[0], self.screen_height * position_1920px[1])        

        print ("Screen Position is:" +str(self.screen_position))
        
        if len(selection) == 0:
            obj_to_count = [ob for ob in bpy.context.view_layer.objects if ob.visible_get()]
        else: 
            obj_to_count = selection
            self.selected_objects = [obj.name for obj in selection]

        
        for obj in obj_to_count:
            if obj.type == 'MESH':
                self.obj_count = len(obj_to_count)
                self.total_obj_count = len(bpy.context.view_layer.objects)
                self.vtx_count += len(obj.evaluated_get(depsgraph).data.vertices)
                self.vtx_normal_count += self.get_normal_count(obj.evaluated_get(depsgraph).data)
                self.uv_vtx_count += self.get_uv_vtx_count(obj.evaluated_get(depsgraph).data)
                self.tri_count += len(obj.evaluated_get(depsgraph).data.loop_triangles)
    

    def get_uv_vtx_count(self,mesh):
        # Based on https://blender.stackexchange.com/a/44896

        uvs = []
        for loop in mesh.loops:
            uv_indices = mesh.uv_layers.active.data[loop.index].uv
            uvs.append(tuple(map(lambda x: round(x,3), uv_indices[:])))
        return len(set(uvs))   


    def get_normal_count(self, mesh):
        #With Help from CarrotKing Marko "Fuxna" Tatalovic
        mesh.calc_normals_split()
        unique_i_to_ns = []
        seen = set()

        for loop in mesh.loops:
            vertex_index = loop.vertex_index
            index_to_normal = { 'index': vertex_index, 'normals' : tuple(loop.normal)}            
            unique_id = (vertex_index, tuple(loop.normal))
            
            if unique_id not in seen:
                seen.add(unique_id)
                unique_i_to_ns.append(index_to_normal)            
        return len(unique_i_to_ns)
    

    def draw_better_stats(self, context):
        blf.size(font_id,self.font_size, dpi)
        blf.color(font_id, self.font_color[0], self.font_color[1], self.font_color[2], 1)

        blf.position(font_id, self.screen_position[0], self.screen_position[1], 0)
        if self.selected_objects == "":         
            blf.draw(font_id, "Better Stats: All")
        else:
            blf.draw(font_id, "Better Stats: %s" % self.selected_objects)

        blf.position(font_id, self.screen_position[0], self.screen_position[1]-self.gap, 0)        
        blf.draw(font_id, "Stats for:")

        blf.position(font_id, self.screen_position[0], self.screen_position[1]-self.gap*2, 0)
        blf.draw(font_id, "Objects:             %d/%d" % (self.obj_count, self.total_obj_count)) 

        blf.position(font_id, self.screen_position[0], self.screen_position[1]-self.gap*3, 0)
        blf.draw(font_id, "Vertices:            %d" % self.vtx_count)

        blf.position(font_id, self.screen_position[0], self.screen_position[1]-self.gap*4, 0)
        blf.draw(font_id, "Vertex Normals:      %d" % self.vtx_normal_count)

        blf.position(font_id, self.screen_position[0], self.screen_position[1]-self.gap*5, 0)
        blf.draw(font_id, "UV Vertices:         %d" % self.uv_vtx_count)

        blf.position(font_id, self.screen_position[0], self.screen_position[1]-self.gap*6, 0)
        blf.draw(font_id, "Triangles:           %d" % self.tri_count)

    def remove_handles(self):
        bpy.app.handlers.depsgraph_update_post.remove(self.onDepsgraph)
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_better_stats, 'WINDOW')



def draw_better_stats_overlay(self, context):
    layout = self.layout
    winman = context.window_manager

    layout.label(text="Better Stats")
    row = layout.row(align=True)
    row.prop(winman, 'betterstats_show')
    layout.separator()

    row = layout.row(align=True)
    row.prop(winman, "betterstats_font_size")
    row = layout.row(align=True)
    row.prop(winman, "betterstats_font_color")

    if winman.betterstats_show is True:
        bpy.context.space_data.overlay.show_stats = False

    if bpy.context.space_data.overlay.show_stats is True:
        winman.betterstats_show = False


def update_betterstats(self, context):
    if self.betterstats_show:
        bpy.app.driver_namespace["BetterStats"] = BetterStatsHandler(context, None, context.object)
    else:        
        if "BetterStats" in bpy.app.driver_namespace:
            bpy.app.driver_namespace["BetterStats"].remove_handles()
            del bpy.app.driver_namespace["BetterStats"]


def update_betterstats_size_color(self, context):
    winman = context.window_manager
    bpy.app.driver_namespace["BetterStats"].font_size = winman.betterstats_font_size
    bpy.app.driver_namespace["BetterStats"].font_color = winman.betterstats_font_color
    bpy.app.driver_namespace["BetterStats"].gap = gap*(winman.betterstats_font_size/10)



def register():
    winman.betterstats_show = BoolProperty(
        name = "Better Stats",
        default = False,
        update = update_betterstats
    )

    winman.betterstats_font_size = IntProperty(
        name = "Font Size",
        default = 11,
        min = 1,
        max = 32,
        update = update_betterstats_size_color
    )

    winman.betterstats_font_color = FloatVectorProperty(
        name = "Font Color",
        subtype = "COLOR",
        default = (1.0,1.0,1.0,1.0),
        size = 4,
        update = update_betterstats_size_color
    )

    overlay.append(draw_better_stats_overlay)

def unregister():
    overlay.remove(draw_better_stats_overlay)
    del winman.betterstats_show
    del winman.betterstats_font_size
    del winman.betterstats_font_color

if __name__ == "__main__":
    register()