import unreal
from typing import List

class PutAssets:
    """
    Put assets to the editor world.
    Args:
        Contents:
        put_camera: Put a camera at the specified location and rotation.
        put_stereo_camera: Put a stereo camera at the specified location and rotation.
        put_spotlight: Put a spotlight at the specified location and rotation.
        put_camera_rig: Put a camera rig at the specified location and rotation.
        create_level_sequence: Create a level sequence.
    """
    def __init__(self):
        self.editor_world = unreal.EditorActorSubsystem()
        self.editor_level_lib = unreal.EditorLevelLibrary()
        self.asset_tools = unreal.AssetToolsHelpers.get_asset_tools() 


    def put_camera(self, 
                   location: unreal.Vector = unreal.Vector(0, 0, 0), 
                   rotation: unreal.Rotator = unreal.Rotator(0, 0, 0),
                   set_label: str = None,):
        """
        Put a camera at the specified location and rotation.
        Args:
            location (unreal.Vector): The location of the camera.
            rotation (unreal.Rotator): The rotation of the camera.
            set_label (str): Give a name to set the label of the camera.(Default: None)
        """
        try:
            camera = self.editor_level_lib.spawn_actor_from_class(unreal.CameraActor, 
                                                                  location=location, 
                                                                  rotation=rotation,)

            if set_label:
                camera.set_actor_label(set_label)


            return camera   
        except Exception as e:
            print(f"Put camera failed! Error: {e}")
            return None

    def put_stereo_camera(self, 
                         location: unreal.Vector = unreal.Vector(0, 0, 0), 
                         rotation: unreal.Rotator = unreal.Rotator(0, 0, 0),
                         base_line: float = 20.0,
                         set_label_left: str = "Left",
                         set_label_right: str = "Right",):
        """
        Put a stereo camera at the specified location and rotation.
        Args:
            location (unreal.Vector): The location of the base camera.
            rotation (unreal.Rotator): The rotation of the base camera.
            base_line (float): The base line of the stereo camera.
            set_label_left (str): Give a name to set the label of the left camera.(Default: "Left")
            set_label_right (str): Give a name to set the label of the right camera.(Default: "Right")
        """
        try:
            # 左右相机创建
            right_location = unreal.Vector( 0,
                                            base_line,  # 在Y轴方向添加基线偏移
                                            0)
            right_rotation = unreal.Rotator( 0,
                                             0,  
                                             0) 
            left_camera = self.put_camera(location=location, rotation=rotation, set_label=set_label_left)
            right_camera = self.put_camera(location=right_location, rotation=right_rotation, set_label=set_label_right)

            right_camera.attach_to_actor(left_camera, 
                                         unreal.Name("None"), 
                                    unreal.AttachmentRule.KEEP_RELATIVE, 
                                    unreal.AttachmentRule.KEEP_RELATIVE, 
                                    unreal.AttachmentRule.KEEP_RELATIVE)
            
            return left_camera, right_camera
        except Exception as e:
            print(f"Put stereo camera failed! Error: {e}")
            return None, None

    def put_spotlight(self, 
                     location: unreal.Vector = unreal.Vector(0, 0, 0), 
                     rotation: unreal.Rotator = unreal.Rotator(0, 0, 0),
                     movable: bool = True,
                     set_label: str = None,
                     intensity: float = 50.0,
                     light_color: unreal.LinearColor = unreal.LinearColor(1.0, 0.9, 0.8),
                     inner_cone_angle: float = 0,
                     outer_cone_angle: float = 45,
                     attenuation_radius: float = 1000,
                     is_set_volumetric_scattering_intensity: bool = True,
                     set_cast_shadows: float = 1.0,):
        """
        Put a spotlight at the specified location and rotation.
        Args:
            location (unreal.Vector): The location of the spotlight.
            rotation (unreal.Rotator): The rotation of the spotlight.
            movable (bool): Whether to make the spotlight movable.(Default: True)
            set_label (str): Give a name to set the label of the spotlight.(Default: None)
            intensity (float): The intensity of the camera.(Default: 160)
            light_color (unreal.LinearColor): The color of the camera's light.(Default: unreal.LinearColor(1.0, 0.9, 0.8))
            inner_cone_angle (float): The inner cone angle of the camera's light.(Default: 45)
            outer_cone_angle (float): The outer cone angle of the camera's light.(Default: 60)
            attenuation_radius (float): The attenuation radius of the camera's light.(Default: 1000)
            is_set_volumetric_scattering_intensity (bool): Whether to set the volumetric scattering intensity of the camera's light.(Default: True)
            is_set_cast_shadows (bool): Whether to set the cast shadows of the camera's light.(Default: True)
        """
        try:
            spot_light = unreal.EditorLevelLibrary.spawn_actor_from_class(
                                                                unreal.SpotLight,  # 聚光灯类       
                                                                location = location,     # 位置
                                                                rotation = rotation,      # 旋转
                                                                )    

            light_comp = spot_light.light_component
            spot_comp = spot_light.spot_light_component
            if movable:
                light_comp.set_editor_property("Mobility", unreal.ComponentMobility.MOVABLE)

            if set_label:
                spot_light.set_actor_label(set_label) 

            # 基础光照设置（光强，颜色）
            light_comp.set_intensity(intensity)
            light_comp.set_light_color(light_color)

            # 聚光灯特性设置（使用新版组件属性）
            spot_comp.set_editor_property("inner_cone_angle", inner_cone_angle)  # 内锥角
            spot_comp.set_editor_property("outer_cone_angle", outer_cone_angle)  # 外锥角
            spot_comp.set_editor_property("attenuation_radius", attenuation_radius)  # 影响范围

            # 高级设置
            spot_comp.set_cast_shadows(is_set_volumetric_scattering_intensity)  # 启用阴影
            # spot_comp.set_ies_brightness_scale(1.2)  # IES亮度缩放
            spot_comp.set_volumetric_scattering_intensity(set_cast_shadows)  # 体积雾强

            print("Put spotlight successfully!")
            return spot_light   
        except Exception as e:
            print(f"Put spotlight failed! Error: {e}")
            return None

    def put_camera_rig(self,
                      location: unreal.Vector = unreal.Vector(0, 0, 0),
                      rotation: unreal.Rotator = unreal.Rotator(0, 0, 0),
                      set_label: str = None,
                      is_lock_orientation_to_rail: bool = True,
                      is_visulize: bool = False,
                      spline_path_points: List[unreal.Vector] = [unreal.Vector(120, 0, 0)],
                      ):
        """
        Put a camera rig at the specified location and rotation.
        Args:
            location (unreal.Vector): The location of the camera rig.
            rotation (unreal.Rotator): The rotation of the camera rig.
            set_label (str): Give a name to set the label of the camera rig.(Default: None)
            is_lock_orientation_to_rail (bool): Whether to lock the orientation of the camera rig to the rail.(Default: True)
            spline_path_points (List[unreal.Vector]): The path of the camera rig rail.(Default: [unreal.Vector(120, 0, 0)])
        """
        try:
            camera_rig_rail = self.editor_level_lib.spawn_actor_from_class(unreal.CameraRig_Rail, 
                                                                           location,
                                                                           rotation)


            if set_label:
                camera_rig_rail.set_actor_label(set_label)

            if is_lock_orientation_to_rail:
                camera_rig_rail.set_editor_property("lock_orientation_to_rail", True) # 将绑定的相机朝向跟随rig

            if is_visulize is not True:
                camera_rig_rail.set_editor_property("show_rail_visualization", False)
            # 设置导轨路径
            spline_component = camera_rig_rail.get_component_by_class(unreal.SplineComponent.static_class())
            for index, location in enumerate(spline_path_points):
                spline_component.add_spline_point(location, unreal.SplineCoordinateSpace.LOCAL, update_spline=True)

            return camera_rig_rail
        except Exception as e:
            print(f"Put camera rig failed! Error: {e}")
            return None
        
    def put_cube(self,
                 location: unreal.Vector = unreal.Vector(0, 0, 0),
                 rotation: unreal.Rotator = unreal.Rotator(0, 0, 0),
                 scale: unreal.Vector = unreal.Vector(1, 1, 1),
                 set_label: str = None,
                 is_movable: bool = True,):
        """
        Put a cube at the specified location and rotation.
        Args:
            location (unreal.Vector): The location of the cube.
            rotation (unreal.Rotator): The rotation of the cube.
            scale (unreal.Vector): The scale of the cube.
            set_label (str): Give a name to set the label of the cube.(Default: None)
            is_movable (bool): Whether to make the cube movable.(Default: True)
        """
        try:
            cube = self.editor_level_lib.spawn_actor_from_class(unreal.StaticMeshActor.static_class(), 
                                                                location, 
                                                                rotation)
            static_mesh_component = cube.static_mesh_component
            if set_label:
                cube.set_actor_label(set_label)
            if is_movable:
                static_mesh_component.set_editor_property("Mobility", unreal.ComponentMobility.MOVABLE)
             # 设置立方体的静态网格（使用引擎默认的 Cube 模型）
            cube_mesh_path = "/Engine/BasicShapes/Cube"  # UE5 默认 Cube 的路径
            cube_mesh = unreal.load_asset(cube_mesh_path)
            static_mesh_component.set_static_mesh(cube_mesh) 
            static_mesh_component.set_relative_scale3d(scale)

            return cube
        except Exception as e:
            print(f"Put cube failed! Error: {e}")
            return None
    

    def create_level_sequence(self,  
                              asset_name: str = "NewLevelSequence", 
                              package_path: str = "/Game/LevelSequence/",
                              fps: int = 30,
                              playback_start: int = 0,
                              playback_end: int = 200,):
        """
        Create a level sequence.
        Args:
            asset_name (str): The name of the level sequence.(Default: "NewLevelSequence")
            package_path (str): The package path of the level sequence.(Default: "/Game/LevelSequence")
            fps (int): The frame rate of the level sequence.(Default: 30)
            playback_start (int): The start frame of the level sequence.(Default: 0)
            playback_end (int): The end frame of the level sequence.(Default: 200)
        """
        try:
            level_sequence = unreal.AssetTools.create_asset(self.asset_tools, 
                                                            asset_name = asset_name, 
                                                            package_path = package_path, 
                                                            asset_class = unreal.LevelSequence, 
                                                            factory = unreal.LevelSequenceFactoryNew())       
            # 设置帧率
            frame_rate = unreal.FrameRate(numerator = fps, denominator = 1) # 创建一个帧率对象并设置为所需的fps数值	
            level_sequence.set_display_rate(frame_rate) # 设置显示速率

            # 将播放范围设置
            level_sequence.set_playback_start(playback_start)
            level_sequence.set_playback_end(playback_end)
            return level_sequence
        except Exception as e:
            print(f"Create level sequence failed! Error: {e}")
            return None


if __name__ == '__main__':
    put_assets = PutAssets()
    # put_assets.put_camera(location=unreal.Vector(0, 0, 100), rotation=unreal.Rotator(0, 0, 0), set_label='camera1')
    # put_assets.put_stereo_camera(location=unreal.Vector(0, 0, 100), rotation=unreal.Rotator(0, 90, 0), base_line=20.0, set_label_left='left_camera', set_label_right='right_camera')
    # put_assets.put_spotlight(location=unreal.Vector(0, 0, 200), rotation=unreal.Rotator(0, 0, 0), set_label='spotlight1')
    # put_assets.put_camera_rig(location=unreal.Vector(0, 0, 300), rotation=unreal.Rotator(0, 0, 0), set_label='camera_rig1',spline_path_points=[unreal.Vector(1200, 0, 0),unreal.Vector(2000, 100, 0)])
    # put_assets.create_level_sequence(asset_name='LevelSequence1', package_path='/Game/LevelSequence', fps=30, playback_start=0, playback_end=200)

