'''
PBR texture multi baker v. 0.1 Beta (06/28/2018)

Developed by:

	Cavicchini Davide
	De Bianchi Giacomo
	Giaretta Leonardo
	Ricci Francesco

'''


bl_info = {
    "name": "PBR Texture Multi Baker",
    'description': 'This addon can bake more than one texture simultaneously',
    'author': '',
    'license': 'GPL',
    'deps': 'UE4 Shader node',
    'version': (0 , 1),
    'blender': (2, 7, 9),
    'location': 'Properties > Render > PBR Texture Multi Baker',
    'warning': 'While baking blender will freeze',
    'wiki_url': 'https://github.com/ASLGalileiVerona/PBR-texture-baker',
    'tracker_url': 'https://github.com/ASLGalileiVerona/PBR-texture-baker/issues',
    'link': 'https://github.com/ASLGalileiVerona/PBR-texture-baker',
    'support': 'COMMUNITY',
    "category": "Material"
}


import bpy
import os

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )
def cr(self, context):
        bpy.context.scene.my_tool.xresolution = int(bpy.context.scene.my_tool.Presets)
        bpy.context.scene.my_tool.yresolution = int(bpy.context.scene.my_tool.Presets)
        return None

def cd(self, context):
    if (bpy.context.scene.my_tool.cd8):
        bpy.context.scene.render.image_settings.color_depth = '8'
        bpy.context.scene.my_tool.cd16 = False
    if (not bpy.context.scene.my_tool.cd8 and not bpy.context.scene.my_tool.cd16):
        bpy.context.scene.render.image_settings.color_depth = '16'
        bpy.context.scene.my_tool.cd16 = True
    return None

def cde(self, context):
    if (bpy.context.scene.my_tool.cd16):
        bpy.context.scene.render.image_settings.color_depth = '16'
        bpy.context.scene.my_tool.cd8 = False
    if (not bpy.context.scene.my_tool.cd8 and not bpy.context.scene.my_tool.cd16):
        bpy.context.scene.render.image_settings.color_depth = '8'
        bpy.context.scene.my_tool.cd8 = True
    return None
    
def main(context):
    bpy.context.active_object.data.uv_textures.active = bpy.context.active_object.data.uv_textures[bpy.context.scene.my_tool.UV_selection]
    filepath = bpy.data.filepath
    filedir = os.path.dirname(filepath)
    BakeResolutionx = bpy.context.scene.my_tool.xresolution
    BakeResolutiony = bpy.context.scene.my_tool.yresolution
    BakeDir = bpy.path.abspath(bpy.context.scene.my_tool.filedir)
    BakeChannel = [[bpy.context.scene.my_tool.Base_color,bpy.context.scene.my_tool.Base_Suffix,'Base Color'],
    [bpy.context.scene.my_tool.Metallic,bpy.context.scene.my_tool.Metal_Suffix,'Metallic'],
    [bpy.context.scene.my_tool.Specular,bpy.context.scene.my_tool.Spec_Suffix,'Specular'],
    [bpy.context.scene.my_tool.Roughness,bpy.context.scene.my_tool.Rough_Suffix,'Roughness'],
    [bpy.context.scene.my_tool.Emissive,bpy.context.scene.my_tool.Emit_Suffix,'Emissive Color'],
    [bpy.context.scene.my_tool.Normal,bpy.context.scene.my_tool.Norm_Suffix,'Normal (Non-Color)'],
    [bpy.context.scene.my_tool.Alfa,bpy.context.scene.my_tool.Alfa_Suffix,'Opacity']]


    # Get the Active Object.
    ActObj = bpy.context.active_object


    # Get the first Active Object Material.
    ActMat = ActObj.active_material
    print ('Active Material: ' + ActMat.name) #for debug.

    # Change its parameters - example viewport diffuse color.

    # Duplicate Active Object Material to create a new temp material and link it to the Active Object.
    TempMat = ActMat.copy()
    TempMat.name = 'Temp Material'
    ActObj.data.materials[0] = TempMat
    print ('Temp Material: ' + TempMat.name) #for debug.
        
    # Get the nodes.
    nodes = TempMat.node_tree.nodes
    print ('Nodes: ' + str(nodes)) #for debug.

    # Get some specific node:
    # Returns None if the node does not exist.
    MatOut = nodes.get('Material Output')
    print (MatOut) #for debug

    # Go look for node named "UE4 Opaque".
    MainShader = [node for node in bpy.data.materials['Temp Material'].node_tree.nodes if node.type=='GROUP' and node.node_tree==bpy.data.node_groups['UE4']]
    print ('Main Shader ' + str(MainShader)) #for debug


    # Select correct Node Slot.
    Sampling_op= bpy.context.scene.cycles.samples
    Bake_op=[
            bpy.context.scene.cycles.bake_type,
            bpy.context.scene.render.bake.margin,
            ]
    Lights_Paths_op = [
             bpy.context.scene.cycles.transparent_max_bounces,
             bpy.context.scene.cycles.transparent_min_bounces,
             bpy.context.scene.cycles.max_bounces, 
             bpy.context.scene.cycles.min_bounces,
             bpy.context.scene.cycles.caustics_reflective,
             bpy.context.scene.cycles.caustics_refractive, 
             ]
    bpy.context.scene.cycles.samples = 1
    bpy.context.scene.cycles.transparent_max_bounces = 1
    bpy.context.scene.cycles.transparent_min_bounces = 1
    bpy.context.scene.cycles.max_bounces = 1
    bpy.context.scene.cycles.min_bounces = 1
    bpy.context.scene.cycles.caustics_reflective = False
    bpy.context.scene.cycles.caustics_refractive = False
    media = (bpy.context.scene.my_tool.xresolution + bpy.context.scene.my_tool.yresolution) // 2
    if(media<=512):
        bpy.context.scene.render.bake.margin = 0
    elif(media>=4096):
        bpy.context.scene.render.bake.margin = 16
    else:
        bpy.context.scene.render.bake.margin = media // 256
    for i in range(0,7,1):
        if(BakeChannel[i][0]):
            CurrentSlot = 0 
            print ('Baking: ' + BakeChannel[i][2])
            for k in range(len(MainShader[0].outputs)):    
                print(MainShader[0].outputs[k].name)
                if MainShader[0].outputs[k].name == BakeChannel[i][2]:
                    CurrentSlot = k
                    print('Gotcha! Slot N. ' + str(CurrentSlot))
                    break
                else:
                    print ('No object found.')
            # Link nodes.
            TempMat.node_tree.links.new(MainShader[0].outputs[CurrentSlot], MatOut.inputs[0])


            # Create the correct resolution Image Node.
            BakeNode = TempMat.node_tree.nodes.new('ShaderNodeTexImage')
            format_list = [["PNG","png"],
            ["TIFF","tiff"],
            ["OPEN_EXR","exr"],
            ["DPX","dpx"],
            ["CINEON","cin"],
            ["TARGA","tga"],
            ["JPEG2000","jp2"],
            ["BMP","bmp"],
            ["IRIS","rgb"],
            ["JPEG","jpeg"]]
            for p in range(0,10,1):
                if (p==int(bpy.context.scene.my_tool.FileType)):
                    BakeFilename = bpy.context.scene.my_tool.Base_Name + BakeChannel[i][1] + '.' + format_list[p][1]
            BakeNode.image = bpy.data.images.new(BakeFilename,BakeResolutionx,BakeResolutiony,alpha=False)
            for p in range(0,10,1):
                if (p==int(bpy.context.scene.my_tool.FileType)):
                    BakeNode.image.file_format = format_list[p][0]
                    
            # Non Color for Normal
            if (i == 5):
                BakeNode.image.colorspace_settings.name = 'Non-Color'
                print ('Setting Non-Color for Normal Bake')
                
            # Non Color for Roughness.
            if (i == 3):
                BakeNode.image.colorspace_settings.name = 'Non-Color'
                print ('Setting Non-Color for Roughness Bake')
                
            # Non Color for Opacity.
            if (i == 6):
                BakeNode.image.colorspace_settings.name = 'Non-Color'
                print ('Setting Non-Color for Roughness Bake')

            # Make the BakeNode Active.
            BakeNode.select = True
            TempMat.node_tree.nodes.active = BakeNode
            
            # Set bake options.
            bpy.context.scene.render.bake.use_selected_to_active = 0
            bpy.context.scene.render.bake.use_clear = 0

            # Baking.
            print ('Baking ' + str(BakeChannel[i][2]) + ' Texture at ' + str(BakeResolutionx) + ' x '+ str(BakeResolutiony) + ' pixel...')
            bpy.ops.object.bake(type='EMIT')

            # Save the texture with the correct filename.
            if not os.path.exists(BakeDir):
                os.makedirs(BakeDir)
            print ('Saving ' + str(BakeChannel[i][2]) + ' Texture as: ' + str(BakeFilename))
            BakeNode.image.save_render(BakeDir + BakeFilename)


            # Back to the original Shader.
            bpy.data.images.remove(bpy.data.images[BakeFilename])

    bpy.data.materials.remove(TempMat)
    ActObj.data.materials[0] = ActMat
    
    bpy.context.scene.cycles.samples = Sampling_op
    
    bpy.context.scene.cycles.bake_type = Bake_op[0]
    bpy.context.scene.render.bake.margin = Bake_op[1]
    
    bpy.context.scene.cycles.transparent_max_bounces = Lights_Paths_op[0]
    bpy.context.scene.cycles.transparent_min_bounces = Lights_Paths_op[1]
    bpy.context.scene.cycles.max_bounces = Lights_Paths_op[2]
    bpy.context.scene.cycles.min_bounces = Lights_Paths_op[3]
    bpy.context.scene.cycles.caustics_reflective = Lights_Paths_op[4]
    bpy.context.scene.cycles.caustics_refractive = Lights_Paths_op[5]
    
class SimpleOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.simple_operator"
    bl_label = "Simple Object Operator"
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        if(len(bpy.context.active_object.material_slots.items())==1):
            if(len(bpy.context.active_object.data.uv_layers.items())>1):
                self.report({'INFO'},'more than one uv_layers were detected baking '+bpy.context.active_object.data.uv_layers.active.name)
            main(context)
            return {'FINISHED'} 
        else:
            self.report({'ERROR'},'More than one material slots were detected')
            return {'CANCELLED'}

def item_cb(self, context):
    return[(uv.name,uv.name,"")for uv in bpy.context.active_object.data.uv_layers]

def active_UV(self, context):
    bpy.context.active_object.data.uv_textures.active = bpy.context.active_object.data.uv_textures[bpy.context.scene.my_tool.UV_selection]
    print(bpy.context.active_object.data.uv_layers.active)
    return None

class MySettings(PropertyGroup):
    
    UV_selection = EnumProperty(
        name = 'UVs',
        items = item_cb,
        update = active_UV
    )
    
    Base_color = BoolProperty(
        name="base color",
        description="Select if you want to bake it",
        )
    Metallic = BoolProperty(
        name="metallic",
        description="Select if you want to bake it",
        )
    Specular = BoolProperty(
        name="specular",
        description="Select if you want to bake it",
        )
    Roughness = BoolProperty(
        name="roughness",
        description="Select if you want to bake it",
        )
    Emissive = BoolProperty(
        name="emissive",
        description="Select if you want to bake it",
        )
    Normal = BoolProperty(
        name="normal",
        description="Select if you want to bake it",
        )
    Alfa = BoolProperty(
        name="alfa",
        description="Select if you want to bake it",
        )
    cd8 = BoolProperty(
        name="cd8",
        description="Select the color depth",
        default = True,
        update = cd
        )
    cd16 = BoolProperty(
        name="cd16",
        description="Select the color depth",
        default = False,
        update = cde
        )
    Custom = BoolProperty(
        name="custom",
        description="Select if you want to choose different resolutions",
        update = cr
        )
    Base_Suffix = StringProperty(
        default = "_COL"
        )
    Metal_Suffix = StringProperty(
        default = "_MET"
        )
    Spec_Suffix = StringProperty(
        default = "_SPE"
        )
    Rough_Suffix = StringProperty(
        default = "_ROU"
        )
    Emit_Suffix = StringProperty(
        default = "_EMI"
        )
    Norm_Suffix = StringProperty(
        default = "_NOR"
        )
    Alfa_Suffix = StringProperty(
        default = "_ALFA"
        )
    Base_Name = StringProperty(
        default = "bake"
    )
    filedir = StringProperty(
        name="",
        description="choose a directory",
        default="",
        subtype='DIR_PATH'
    )
    xresolution = IntProperty(
        name = "x",
        description="",
        default = 512,
        min = 2,
        max = 16384
        )
    yresolution = IntProperty(
        name = "y",
        description="",
        default = 512,
        min = 2,
        max = 16384
        )
    Presets = EnumProperty(
        name = 'Presets',
        items = [('512', '512 x 512', ""),
                 ('1024', '1024 x 1024', ""),
                 ('2048', '2048 x 2048', ""),
                 ('4096', '4096 x 4096', ""),
                 ('8192', '8192 x 8192', ""),
                 ],
        update = cr
    )
    FileType = EnumProperty(
        name = 'FileType',
        items = [('0', 'PNG', ""),
                 ('9', 'JPG', ""),
                 ('8', 'Iris', ""),
                 ('7', 'BMP', ""),
                 ('6', 'JPEG 2000', ""),
                 ('5', 'Targa', ""),
                 ('4', 'Cineon', ""),
                 ('3', 'DPX', ""),
                 ('2', 'OpenEXR', ""),
                 ('1', 'Tiff', "")
                 ]
    )
    
class LayoutDemoPanel(bpy.types.Panel): 
    """Creates a Panel in the scene context of the properties editor""" 
    bl_label = 'PBR Texture Multi Baker' 
    bl_idname = "SCENE_PT_layout" 
    bl_space_type = 'PROPERTIES' 
    bl_region_type= 'WINDOW' 
    bl_context = 'render' 
    def draw(self, context): 
        layout = self.layout 

        scene = context.scene 
        rd = scene.render
        split = layout.split() 
        
        # Resolution selection.
        
        layout.label(text = "Resolution :")
        row = layout.row() 

        row.prop(scene.my_tool, "Presets", text="")
        
        row = layout.row() 
        row = layout.row() 
        row = layout.row() 
        row.prop(scene.my_tool, "Custom", text = "Custom")
        
        if (bpy.context.scene.my_tool.Custom):
            row = layout.row() 
            row = layout.row() 
            row = layout.row() 
            row.prop(scene.my_tool, "xresolution", text="X custom")
            row.prop(scene.my_tool, "yresolution", text="Y custom")
        row = layout.row() 
        row = layout.row() 
        
        # Bake directory.
        
        split = layout.split()
        col = split.column()
        col.label(text = "Bake dir:")
        col = split.column()
        col.prop(scene.my_tool, "filedir", text="")
        row = layout.row() 
        
        # Base name.
        
        split = layout.split()
        col = split.column()
        col.label(text = "Base name:")
        col = split.column()
        col.prop(scene.my_tool, "Base_Name", text = "")
        row = layout.row() 
        
        # File type.
        
        split = layout.split()
        col = split.column()
        col.label(text = "File type:")
        col = split.column()
        col.prop(scene.my_tool, "FileType", text="", icon = "IMAGE_DATA")
        row = layout.row() 
        
        # Color Depth.
        
        split = layout.split()
        col = split.column()
        col.label(text = "Color depth:")
        col = split.column()
        col = split.column()
        col.prop(scene.my_tool, "cd8", text = "8 bit")
        col = split.column()
        col.prop(scene.my_tool, "cd16", text = "16 bit")
        row = layout.row() 
        row = layout.row() 
        
        # UV selection.
        
        split = layout.split()
        me = context.mesh
        col = split.column()
        col.label(text = "UV selection:")
        col = split.column()
        col.prop(scene.my_tool, "UV_selection", text="")
        row = layout.row() 

        # Texture selection.
        
        split = layout.split()
        col = split.column()
        col.label(text="Texture:")
        col.prop(scene.my_tool, "Base_color", text = "Base color")
        col.prop(scene.my_tool, "Metallic", text = "Metallic")
        col.prop(scene.my_tool, "Specular", text = "Specular")
        col.prop(scene.my_tool, "Roughness", text = "Roughness")
        col.prop(scene.my_tool, "Emissive", text = "Emissive")
        col.prop(scene.my_tool, "Alfa", text = "Opacity")
        col.prop(scene.my_tool, "Normal", text = "Normal")
        
        # Suffix selection.
        
        col = split.column()
        col.label(text="Suffix:")
        col.prop(scene.my_tool, "Base_Suffix", text = "")
        col.prop(scene.my_tool, "Metal_Suffix", text = "")
        col.prop(scene.my_tool, "Spec_Suffix", text = "")
        col.prop(scene.my_tool, "Rough_Suffix", text = "")
        col.prop(scene.my_tool, "Emit_Suffix", text = "")
        col.prop(scene.my_tool, "Alfa_Suffix", text = "")
        col.prop(scene.my_tool, "Norm_Suffix", text = "")
        
        # Bake button.
        
        row = layout.row() 
        row = layout.row() 
        row = layout.row() 
        row.operator("object.simple_operator",text = "Multi Bake", icon='RENDER_STILL') 


def register(): 
    bpy.utils.register_class(LayoutDemoPanel)
    bpy.utils.register_class(SimpleOperator)
    bpy.utils.register_module(__name__)
    bpy.types.Scene.my_tool = PointerProperty(type=MySettings)



def unregister(): 
    bpy.utils.unregister_class(LayoutDemoPanel)
    bpy.utils.unregister_class(SimpleOperator)
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.my_tool

if __name__ == "__main__":
    register()
