bl_info = {
    "name" : "Better Stats",
    "author" : "Sebastian Schneider",
    "description" : "Replacement for the original Statistics. Currently only works in Object Mode",
    "blender" : (3, 6, 0),
    'version': (0, 1, 0 ,2),
    "location" : "View3D",
    "warning" : "",
    "category" : "View3D",
    'wiki_url': 'https://github.com/ssnd292/BetterStats'
}

import bpy
import blf

from bpy.utils import register_class, unregister_class

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
                       AddonPreferences,
                       )

overlay = bpy.types.VIEW3D_PT_overlay

font_id = 0
overlay_position = (90,-150)
gap = 20
system = bpy.context.preferences.system


def update_betterstats(self, context):
    addon_prefs = context.preferences.addons[__package__].preferences
    if addon_prefs.betterstats_show:
        bpy.app.driver_namespace["BetterStats"] = BetterStatsHandler(context, None, context.object)
    else:        
        if "BetterStats" in bpy.app.driver_namespace:
            bpy.app.driver_namespace["BetterStats"].remove_handles()
            del bpy.app.driver_namespace["BetterStats"]

def update_betterstats_size_color(self, context):
    addon_prefs = context.preferences.addons[__package__].preferences
    bpy.app.driver_namespace["BetterStats"].font_size = addon_prefs.betterstats_font_size
    bpy.app.driver_namespace["BetterStats"].font_color = addon_prefs.betterstats_font_color
    bpy.app.driver_namespace["BetterStats"].gap = gap*(addon_prefs.betterstats_font_size/10)


class BetterStatsProps(AddonPreferences):
    bl_idname = __name__


    betterstats_show : BoolProperty(
        name = "Better Stats",
        default = False,
        update = update_betterstats
    )

    betterstats_font_size : IntProperty(
        name = "Font Size",
        default = 11,
        min = 1,
        max = 32,
        update = update_betterstats_size_color
    )

    betterstats_font_color : FloatVectorProperty(
        name = "Font Color",
        subtype = "COLOR",
        default = (1.0,1.0,1.0,1.0),
        size = 4,
        update = update_betterstats_size_color
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "betterstats_show")
        layout.prop(self, "betterstats_font_size")
        layout.prop(self, "betterstats_font_color")

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
        self.area_height = 0
        self.screen_position = (0,0)
        self.font_size = context.preferences.addons[__package__].preferences.betterstats_font_size
        self.font_color = context.preferences.addons[__package__].preferences.betterstats_font_color
        
        self.gap = 25
        self.draw_better_stats = bpy.types.SpaceView3D.draw_handler_add(self.draw_better_stats,(context,),'WINDOW', 'POST_PIXEL')
        self.depsgraph_handle = bpy.app.handlers.depsgraph_update_post.append(self.onDepsgraph)

    def onDepsgraph(self, scene, depsgraph):
        self.area_height = 0
        self.selected_objects = ""
        self.obj_count = 0
        self.total_obj_count = 0
        self.vtx_count = 0
        self.vtx_normal_count = 0
        self.uv_vtx_count = 0
        self.tri_count = 0

        selection = bpy.context.selected_objects     
        
        
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
        dpi = int(system.dpi * system.pixel_size)
        for bl_area in bpy.context.window.screen.areas:
            if bl_area.type == "VIEW_3D":
                self.area_height = bl_area.height
        
        self.screen_position = (0 + overlay_position[0], self.area_height + overlay_position[1])  
        blf.size(font_id,self.font_size, dpi)
        blf.color(font_id, self.font_color[0], self.font_color[1], self.font_color[2], 1)

        blf.position(font_id, self.screen_position[0], self.screen_position[1], 0)
        blf.draw(font_id, "Better Stats")

        blf.position(font_id, self.screen_position[0], self.screen_position[1]-self.gap, 0)
        if self.selected_objects == "":         
            blf.draw(font_id, "Stats for: Scene")
        else:
           blf.draw(font_id, "Stats for: %s" % self.selected_objects)            

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
    addon_prefs = context.preferences.addons[__package__].preferences

    layout.label(text="Better Stats")
    row = layout.row(align=True)
    row.prop(addon_prefs, 'betterstats_show')
    layout.separator()

    row = layout.row(align=True)
    row.prop(addon_prefs, "betterstats_font_size")
    row = layout.row(align=True)
    row.prop(addon_prefs, "betterstats_font_color")

    if addon_prefs.betterstats_show is True:
        bpy.context.space_data.overlay.show_stats = False

    if bpy.context.space_data.overlay.show_stats is True:
        addon_prefs.betterstats_show = False


    
def register():
    register_class(BetterStatsProps)

    overlay.append(draw_better_stats_overlay)

def unregister():

    overlay.remove(draw_better_stats_overlay)
    unregister_class(BetterStatsProps)
    
if __name__ == "__main__":
    register()