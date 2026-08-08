import unreal

def build_stereocam():

    '''-----------------基础参数设置----------------------'''
    playback_start = 0
    playback_end = 30
    numberator = 30  # fps
    # 设置总帧宽度
    total_frames = playback_end - playback_start

    # name与path
    asst_name = "un_stereocam4"
    package_path = "/Game/"

    # 基础位置
    start_x = -2000
    start_y = -1000
    start_z = 800

    # 添加多个 Spline 点并设置位置(rig设置)
    spline_points = [
        # unreal.Vector(100, 0, 0),    # 第一个点
        unreal.Vector(1500, 0, 0),  # 第二个点
        # unreal.Vector(1200, 200, 0),# 第三个点
        # unreal.Vector(1500, 100, 0),   # 第四个点
        # unreal.Vector(2000, -100, 0),
        # unreal.Vector(2500, -100, 0),
        # unreal.Vector(2500, 1000, 0),
        # unreal.Vector(1700, 1000, 0),
        # unreal.Vector(1350, 500, 0),
        # unreal.Vector(1000, 1000, 0),
        # unreal.Vector(500, 1000, 0),
        # unreal.Vector(0, 700, 0),
        # unreal.Vector(0, 0, 0),
    ]

    editor_level_lib = unreal.EditorLevelLibrary()
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools() 	
    # 在根内容文件夹中创建一个名为LevelSequenceName的关卡序列	
    level_sequence = unreal.AssetTools.create_asset(asset_tools, 
                                                    asset_name = asst_name, 
                                                    package_path = package_path, 
                                                    asset_class = unreal.LevelSequence, 
                                                    factory = unreal.LevelSequenceFactoryNew())
    # 创建一个帧率对象并设置为所需的fps数值	
    frame_rate = unreal.FrameRate(numerator = numberator, denominator = 1) 	
    # 设置显示速率	
    level_sequence.set_display_rate(frame_rate)
    # 将播放范围设置
    level_sequence.set_playback_start(playback_start)
    level_sequence.set_playback_end(playback_end)

    '''--------------------------------Camera-------------------------------------'''
    # 创建相机Actor
    camera_left = editor_level_lib.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(start_x, start_y, start_z), unreal.Rotator(0, -30, 90))
    camera_right = editor_level_lib.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(start_x + 20, start_y, start_z), unreal.Rotator(0, -30, 90))

    # 设置相机Actor的标签
    camera_left.set_actor_label("left_cam")
    camera_right.set_actor_label("right_cam")

    # 将相机添加到Sequencer
    camera_left_binding = level_sequence.add_possessable(camera_left)
    camera_right_binding = level_sequence.add_possessable(camera_right)

    # 添加相机切换轨道
    camera_cut_track = level_sequence.add_master_track(unreal.MovieSceneCameraCutTrack)


    for i in range(total_frames):
        if i % 2 == 0:
            # 单数帧添加左相机
            left_camera_section = camera_cut_track.add_section()
            left_camera_section.set_range(i, i+1)
            left_camera_section.set_camera_binding_id(camera_left_binding.get_binding_id())
        if i % 2 == 1:
            # 双数帧添加右相机
            right_camera_section = camera_cut_track.add_section()
            right_camera_section.set_range(i, i+1)
            right_camera_section.set_camera_binding_id(camera_right_binding.get_binding_id())


    '''--------------------------------Rig------------------------------------'''
    # 创建相机导轨（Camera Rail）
    camera_rig_rail = editor_level_lib.spawn_actor_from_class(unreal.CameraRig_Rail, unreal.Vector(start_x, start_y, start_z), unreal.Rotator(0, -0, 0))
    camera_rig_rail.set_actor_label("CameraRail")
    camera_rig_rail.set_editor_property("lock_orientation_to_rail", True) # 将绑定的相机朝向跟随rig

    # 将camera绑定到rig
    camera_left.attach_to_actor(camera_rig_rail, 
                                 unreal.Name("None"), 
                                 unreal.AttachmentRule.KEEP_WORLD, 
                                 unreal.AttachmentRule.KEEP_WORLD, 
                                 unreal.AttachmentRule.KEEP_WORLD)
    camera_right.attach_to_actor(camera_left, 
                                 unreal.Name("None"), 
                                 unreal.AttachmentRule.KEEP_WORLD, 
                                 unreal.AttachmentRule.KEEP_WORLD, 
                                 unreal.AttachmentRule.KEEP_WORLD)


    # 将导轨添加到Sequencer
    camera_rail_binding = level_sequence.add_possessable(camera_rig_rail)

    # 设置 Camera Rig Rail 的 Spline 路径
    spline_component = camera_rig_rail.get_component_by_class(unreal.SplineComponent.static_class())

    for index, location in enumerate(spline_points):
        spline_component.add_spline_point(location, unreal.SplineCoordinateSpace.LOCAL, update_spline=True)

    property_track = camera_rail_binding.add_track(unreal.MovieSceneFloatTrack)
    property_track.set_property_name_and_path("CurrentPositionOnRail", "CurrentPositionOnRail") # 添加CurrentPositionOnRail属性，注：path必须在蓝图中被exposed，否则无法实现
    current_position_section = property_track.add_section()
    current_position_section.set_range(0, total_frames)  # 设置轨道范围
    channels = current_position_section.find_channels_by_type(unreal.MovieSceneScriptingFloatChannel)
    if len(channels) > 0:
        float_channel = channels[0]
    else:
        float_channel = current_position_section.add_channel(unreal.MovieSceneScriptingFloatChannel)
    # 在每一帧添加关键帧
    for frame in range(total_frames+1):
        if frame % 2 == 0:
            # 计算Current Position的值
            current_position = frame / float(total_frames)

        # 添加关键帧
        float_channel.add_key(unreal.FrameNumber(frame), current_position)
    # 保存 Sequencer 资产
    unreal.EditorAssetLibrary.save_asset("/Game/Sequencer/MySequencer")

    # 打开Sequencer
    unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(level_sequence)

    # 打印成功信息
    print("Sequencer created successfully with CameraRig_Rail and Current Position track!")

    # 刷新以直观地查看添加的新绑定
    unreal.LevelSequenceEditorBlueprintLibrary.refresh_current_level_sequence()

if __name__ == "__main__":
    build_stereocam()