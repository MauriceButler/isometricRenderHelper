bl_info = {
    "name": "Isometric Render Helper",
    "author": "Maurice Butler",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "description": "Setups camera and performs isometric sprite rendering",
}

import bpy
import os
import math

class SetupCamera(bpy.types.Operator):   
    bl_idname = "irh.setup_camera"
    bl_label = "Setup"

    def execute(self, context):
        setupCamera(context)
        return {'FINISHED'}
    
def setupCamera(context):
    
    # empty cube
    bpy.ops.object.empty_add(type='CUBE', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    bpy.context.active_object.name = "irh_empty"
    irhEmpty = bpy.data.objects['irh_empty']  
    
    
    # camera
    bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(12, -12, 12), rotation=(0.991347, 0, 0.785398), scale=(1, 1, 1))
    bpy.context.active_object.name = "irh_camera"
    irhCamera = bpy.data.objects['irh_camera']
    irhCamera.data.type = 'ORTHO'
    irhCamera.data.ortho_scale = 1.8
    
    constraint = irhCamera.constraints.new(type='TRACK_TO')
    constraint.target = irhEmpty
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'

    bpy.ops.object.select_all(action='DESELECT')
    irhCamera.select_set(True)
    bpy.ops.object.visual_transform_apply()
    
    
    # circle
    bpy.ops.curve.primitive_bezier_circle_add(radius=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(8, 8, 8))
    bpy.context.active_object.name = "irh_circle"
    irhCircle = bpy.data.objects['irh_circle']
    
    irhCircle.data.path_duration = 1
    irhCircle.lock_location[0] = True
    irhCircle.lock_location[1] = True
    irhCircle.lock_location[2] = True
    irhCircle.lock_rotation[0] = True
    irhCircle.lock_rotation[1] = True
    irhCircle.lock_scale[0] = True
    irhCircle.lock_scale[1] = True
    irhCircle.lock_scale[2] = True
    irhCircle.rotation_euler[2] = 0.785398


    #setup parenting of camera and circle
    bpy.ops.object.select_all(action='DESELECT') 
    irhCircle.select_set(True)
    irhCamera.select_set(True)  

    bpy.context.view_layer.objects.active = irhCircle    # the active object will be the parent of all selected object
    bpy.ops.object.parent_set(type='FOLLOW')
    

    # output settings
    bpy.context.space_data.context = 'OUTPUT'
    bpy.context.scene.render.resolution_x = 300
    bpy.context.scene.render.resolution_y = 300
    bpy.context.scene.frame_step = 2
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.image_settings.color_mode = 'RGBA'


    # render settings
    bpy.context.space_data.context = 'RENDER'
    bpy.context.scene.render.film_transparent = True
    


class RemoveCamera(bpy.types.Operator):
    bl_idname = "irh.remove_camera"
    bl_label = "Remove"

    def execute(self, context):
        removeCamera(context)
        return {'FINISHED'}

def removeCamera(context):
    bpy.ops.object.select_all(action='DESELECT') 
    bpy.ops.object.select_pattern(pattern="irh_*", extend=False)
    bpy.ops.object.delete(use_global=False)
 


class CreateSpritesheet(bpy.types.Operator):
    bl_idname = "irh.create_spritesheet"
    bl_label = "Render Isometric Spritesheet"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        createSpritesheet(self, context)
        return {'FINISHED'}


def getFileCount(filepath):
    return len([name for name in os.listdir(filepath) if os.path.isfile(os.path.join(filepath, name))])

rotationMap = {
    "NW": 0.785398,
    "N": 1.5708,
    "NE": 2.35619,
    "E" : 3.14159,
    "SE": 3.92699,
    "S": 4.71239,
    "SW": 5.49779,
    "W": 6.28319
}

def renderAnimation(irhCircle, context, absAnimationOutputRoot, width, height, frameCount, animationName, direction):
    irhCircle.rotation_euler[2] = rotationMap[direction]
    context.scene.render.filepath = os.path.join(absAnimationOutputRoot, f"{direction}/")
    bpy.ops.render.opengl(animation=True, write_still=True)

    if frameCount is None:
        frameCount = getFileCount(bpy.path.abspath(context.scene.render.filepath))

    renderStrip(absAnimationOutputRoot, width, height, frameCount, animationName, direction)
    
    return frameCount

def renderStrip(absAnimationOutputRoot, width, height, frameCount, animationName, direction):
    command = f'montage {absAnimationOutputRoot}/{direction}/????.png -tile {frameCount}x1 -geometry {height}x{width}+0+0 -background transparent {absAnimationOutputRoot}/{animationName}_{direction}.png'
    os.system(command)


def renderSpriteSheet(absAnimationOutputRoot, width, height, animationName):
    command = f'montage {absAnimationOutputRoot}/{animationName}_?.png {absAnimationOutputRoot}/{animationName}_??.png -tile 1x8 -geometry {8 * height}x{width}+0+0 -background transparent {absAnimationOutputRoot}/{animationName}.png'
    print(command)
    os.system(command)


def createSpritesheet(self, context):
    outputRoot = context.scene.irh_settings.render_output_root
    animationName = ""

    if outputRoot == '':
        self.report({"WARNING"}, "Please set a render output root directory")
        return {"CANCELLED"}

    selection = bpy.context.selected_objects

    if selection:
        for obj in selection:
            anim = obj.animation_data
            if anim is not None and anim.action is not None:
                animationName = anim.action.name
                print(anim.action.frame_range)
                # TODO: find out how to get animation lengths better
                # context.scene.frame_start = anim.action.frame_range[0]
                # context.scene.frame_end = anim.action.frame_range[1]
                # context.scene.frame_step = 2
                # context.scene.render.fps = 60
    else:
        self.report({"WARNING"}, "Please select an object with animations")
        return {"CANCELLED"}

    if animationName == "":
        self.report({"WARNING"}, "Please select an animation")
        return {"CANCELLED"}
        

    animationOutputRoot = os.path.join(outputRoot, animationName)
    absAnimationOutputRoot = bpy.path.abspath(animationOutputRoot)
    width = bpy.context.scene.render.resolution_x 
    height = bpy.context.scene.render.resolution_y 

    irhCircle = bpy.data.objects['irh_circle']
    
    frameCount = renderAnimation(irhCircle, context, absAnimationOutputRoot, width, height, None, animationName, "NW")
    renderAnimation(irhCircle, context, absAnimationOutputRoot, width, height, None, animationName, "N")
    renderAnimation(irhCircle, context, absAnimationOutputRoot, width, height, None, animationName, "NE")
    renderAnimation(irhCircle, context, absAnimationOutputRoot, width, height, None, animationName, "E")
    renderAnimation(irhCircle, context, absAnimationOutputRoot, width, height, None, animationName, "SE")
    renderAnimation(irhCircle, context, absAnimationOutputRoot, width, height, None, animationName, "S")
    renderAnimation(irhCircle, context, absAnimationOutputRoot, width, height, None, animationName, "SW")
    renderAnimation(irhCircle, context, absAnimationOutputRoot, width, height, None, animationName, "W")
    
    renderSpriteSheet(absAnimationOutputRoot, width, height, animationName)
    
    context.scene.render.filepath = outputRoot

   
def menu_func(self, context):
    self.layout.separator()
    self.layout.operator(CreateSpritesheet.bl_idname)

class IsometricRenderHelperSettings(bpy.types.PropertyGroup):
    render_output_root: bpy.props.StringProperty(name="Animation Output Root",
                                        description="Animation Output Root",
                                        default="",
                                        maxlen=1024,
                                        subtype="FILE_PATH")
                                        
class IsometricRenderHelperPanel(bpy.types.Panel):
    bl_label = "Isometric Render Helper"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Camera:")
        row = layout.row()
        row.scale_y = 2.0
        row.operator(SetupCamera.bl_idname)
        row.operator(RemoveCamera.bl_idname)

        layout.label(text="Render Output Root:")
        row = layout.row()
        row.scale_y = 2.0
        row.prop(context.scene.irh_settings, "render_output_root")
        

def register():
    bpy.utils.register_class(IsometricRenderHelperPanel)
    bpy.utils.register_class(SetupCamera)
    bpy.utils.register_class(RemoveCamera)
    bpy.utils.register_class(CreateSpritesheet)
    bpy.utils.register_class(IsometricRenderHelperSettings)

    bpy.types.VIEW3D_MT_view.append(menu_func)
    
    bpy.types.Scene.irh_settings = bpy.props.PointerProperty(type=IsometricRenderHelperSettings)


def unregister():
    bpy.utils.unregister_class(IsometricRenderHelperPanel)
    bpy.utils.unregister_class(SetupCamera)
    bpy.utils.unregister_class(RemoveCamera)
    bpy.utils.unregister_class(CreateSpritesheet)
    bpy.utils.unregister_class(IsometricRenderHelperSettings)
    
    bpy.types.VIEW3D_MT_view.remove(menu_func)

    del bpy.types.Scene.irh_settings


if __name__ == "__main__":
    register()
