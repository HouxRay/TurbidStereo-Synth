import unreal

# 获取编辑器世界
editor_world = unreal.EditorActorSubsystem()
editor_level_lib = unreal.EditorLevelLibrary()


#cube

# 定义立方体的位置、旋转和缩放
cube_location = (0, 0, 0)   # 位置（世界坐标）
cube_rotation = (0, 0, 0)  # 旋转
cube_scale = (0.01, 0.01, 0.01)  # 缩放（默认 1.0）

# 生成立方体（StaticMeshActor）
cube_actor = editor_level_lib.spawn_actor_from_class(
    unreal.StaticMeshActor.static_class(),  # 使用 StaticMeshActor 类
    cube_location,
    cube_rotation
)
cube_actor.set_actor_label("cube")

if cube_actor:
    # 获取立方体的静态网格组件
    static_mesh_component = cube_actor.static_mesh_component
    static_mesh_component.set_editor_property("Mobility", unreal.ComponentMobility.MOVABLE)
    
    # 设置立方体的静态网格（使用引擎默认的 Cube 模型）
    cube_mesh_path = "/Engine/BasicShapes/Cube"  # UE5 默认 Cube 的路径
    cube_mesh = unreal.load_asset(cube_mesh_path)
    static_mesh_component.set_static_mesh(cube_mesh)
    
    # 设置缩放
    static_mesh_component.set_world_scale3d(cube_scale)
    
    # 可选：设置材质
    # material_path = "/Game/MyMaterials/MyMaterial"
    # material = unreal.load_asset(material_path)
    # static_mesh_component.set_material(0, material)
    
    print(f"立方体生成成功！位置: {cube_location}")
else:
    print("立方体生成失败！")


# camera
location = unreal.Vector(0, 0, 0) 
rotation = unreal.Rotator(0, -30, 90)
camera = editor_level_lib.spawn_actor_from_class(unreal.CameraActor, 
                                                location=location, 
                                                rotation=rotation,)
camera.set_actor_label("cam")

camera.attach_to_actor(cube_actor, 
                        unreal.Name("None"), 
                        unreal.AttachmentRule.KEEP_RELATIVE, 
                        unreal.AttachmentRule.KEEP_RELATIVE, 
                        unreal.AttachmentRule.KEEP_RELATIVE)


# rig
camera_rig_rail = editor_level_lib.spawn_actor_from_class(unreal.CameraRig_Rail, 
                                                        unreal.Vector(0, 100, 200),
                                                        unreal.Rotator(0, 0, 0))
camera_rig_rail.set_editor_property("lock_orientation_to_rail", True)
camera_rig_rail.set_editor_property("show_rail_visualization", False)
spline_component = camera_rig_rail.get_component_by_class(unreal.SplineComponent.static_class())

spline_points = [
    unreal.Vector(1500, 0, 0),  # 第二个点
]


for index, location in enumerate(spline_points):
    spline_component.add_spline_point(location, unreal.SplineCoordinateSpace.LOCAL, update_spline=True)


# sequencer
asset_tools = unreal.AssetToolsHelpers.get_asset_tools() 
level_sequence = asset_tools.create_asset( 
                                                asset_name = 'test_python', 
                                                package_path = '/Game/TestPython', 
                                                asset_class = unreal.LevelSequence, 
                                                factory = unreal.LevelSequenceFactoryNew())   
frame_rate = unreal.FrameRate(numerator = 30, denominator = 1) # 创建一个帧率对象并设置为所需的fps数值	
level_sequence.set_display_rate(frame_rate) # 设置显示
# 将播放范围设置
level_sequence.set_playback_start(0)
level_sequence.set_playback_end(20)

# create camera cut track
camera_binding = level_sequence.add_possessable(camera)
cube_binding = level_sequence.add_possessable(cube_actor)
rig_binding = level_sequence.add_possessable(camera_rig_rail)
camera_cut_track = level_sequence.add_master_track(unreal.MovieSceneCameraCutTrack)

camera_section = camera_cut_track.add_section()
camera_section.set_range(0, 20)
camera_section.set_camera_binding_id(camera_binding.get_binding_id())
# rig_root_component = camera_rig_rail.root_component

property_track = rig_binding.add_track(unreal.MovieSceneFloatTrack)
property_track.set_property_name_and_path("CurrentPositionOnRail", "CurrentPositionOnRail") # 添加CurrentPositionOnRail属性，注：path必须在蓝图中被exposed，否则无法实现
current_position_section = property_track.add_section()
current_position_section.set_range(0, 20)  # 设置轨道范围
channels = current_position_section.find_channels_by_type(unreal.MovieSceneScriptingFloatChannel)
if len(channels) > 0:
    float_channel = channels[0]
else:
    float_channel = current_position_section.add_channel(unreal.MovieSceneScriptingFloatChannel)
# 在每一帧添加关键帧
for frame in range(20+1):
    if frame % 2 == 0:
        # 计算Current Position的值
        current_position = frame / float(20)
    # 添加关键帧
    float_channel.add_key(unreal.FrameNumber(frame), current_position)


path_track = cube_binding.add_track(unreal.MovieScene3DAttachTrack)
path_section = path_track.add_section()
path_section.set_range(0, 20)
path_section.set_constraint_binding_id(level_sequence.make_binding_id(rig_binding, unreal.MovieSceneObjectBindingSpace.LOCAL))
# rig_id = level_sequence.make_binding_id(rig_binding, unreal.MovieSceneObjectBindingSpace.LOCAL)
# path_section.set_constraint_binding_id(rig_id)
# path_section.add_actor_component_key(unreal.SequencerBindingProxy(rig_id), rig_root_component)




# attach_binding_id = sequence.make_binding_id(guid_of_cube_1, unreal.MovieSceneObjectBindingSpace.LOCAL)
# attach_settings.set_constraint_binding_id(attach_binding_id)

# 假设已获取 cube_binding 和 level_sequence
# 添加 3D 变换轨道
transform_track = camera_binding.add_track(unreal.MovieScene3DTransformTrack)
transform_section = transform_track.add_section()

# 设置时间范围（0-20帧）
transform_section.set_start_frame(0)
transform_section.set_end_frame(20)

# 获取所有通道（顺序：位置X/Y/Z，旋转Roll/Pitch/Yaw，缩放X/Y/Z）
channels = transform_section.get_channels()
# 
# 设置关键帧 ---------------------------------------------------
# 位置Y轴（第1通道）
position_x = channels[1]

for frame in range(20+1):
    if frame % 2 == 0:
        # 计算Current Position的值
        current_position = frame / float(20)
    # 添加关键帧
        position_x.add_key(unreal.FrameNumber(frame),0.0)  # 初始位置
    else:
        position_x.add_key(unreal.FrameNumber(frame),300.0)

# position_x.add_key(unreal.FrameNumber(0),0.0)  # 初始位置
# position_x.add_key(unreal.FrameNumber(20), 500.0)  # 20帧时X=500
