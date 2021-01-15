bl_info = {
    "name": "Isometric Render Helper",
    "author": "Maurice Butler",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "description": "Setups camera and performs isometric sprite rendering",
}

import bpy
import os
    
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

def createSpritesheet(self, context):
    outputRoot = context.scene.irh_settings.render_output_root

    if outputRoot == '':
        self.report({"WARNING"}, "Please set a render output root directory")
        return {"CANCELLED"}

    irhCircle = bpy.data.objects['irh_circle']
    
    irhCircle.rotation_euler[2] = 0.785398
    context.scene.render.filepath = os.path.join(outputRoot, "NW/")
    bpy.ops.render.opengl(animation=True, write_still=True)
    
    irhCircle.rotation_euler[2] = 1.5708
    context.scene.render.filepath = os.path.join(outputRoot, "N/")
    bpy.ops.render.opengl(animation=True, write_still=True)

    irhCircle.rotation_euler[2] = 2.35619
    context.scene.render.filepath = os.path.join(outputRoot, "NE/")
    bpy.ops.render.opengl(animation=True, write_still=True)

    irhCircle.rotation_euler[2] = 3.14159
    context.scene.render.filepath = os.path.join(outputRoot, "E/")
    bpy.ops.render.opengl(animation=True, write_still=True)

    irhCircle.rotation_euler[2] = 3.92699
    context.scene.render.filepath = os.path.join(outputRoot, "SE/")
    bpy.ops.render.opengl(animation=True, write_still=True)

    irhCircle.rotation_euler[2] = 4.71239
    context.scene.render.filepath = os.path.join(outputRoot, "S/")
    bpy.ops.render.opengl(animation=True, write_still=True)

    irhCircle.rotation_euler[2] = 5.49779
    context.scene.render.filepath = os.path.join(outputRoot, "SW/")
    bpy.ops.render.opengl(animation=True, write_still=True)

    irhCircle.rotation_euler[2] = 6.28319
    context.scene.render.filepath = os.path.join(outputRoot, "W/")
    bpy.ops.render.opengl(animation=True, write_still=True)
    
    

   
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
