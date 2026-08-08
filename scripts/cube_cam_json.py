import unreal
from put_assets import PutAssets
from binding import Binding
from sequencer import MySequencer
from SequencerBinding import SequencerBinding
import json

def read_json(json_file_path:str)->dict:
    with open(json_file_path, 'r', encoding='utf-8') as f:
        json_data = f.read()
    return json.loads(json_data)

def main(json_data:dict)->None:
    epoch = json_data['epoch']
    camera_info = json_data['camera']
    spotlight_info = json_data['spotlight']
    camera_rig_info = json_data['camera_rig']
    cube_info = json_data['cube']
    sequencer_name = json_data['sequencer_name']
    sequencer_path = json_data['sequencer_save_path']
    playback_end = json_data['playback_end']
    playback_start = json_data['playback_start']
    total_frames = playback_end - playback_start

    assets_builder = PutAssets()
    binding_builder = Binding()

    cube = assets_builder.put_cube(location = eval(cube_info['location']), 
                                   rotation = eval(cube_info['rotation']),
                                   scale = eval(cube_info['scale']),
                                   set_label = f"cube",
                                   is_movable = True,)
    
    camera = assets_builder.put_camera(location = eval(camera_info['location']), 
                                       rotation = eval(camera_info['rotation']),
                                       set_label = f"camera",)
    
    left_spotlight = assets_builder.put_spotlight(location = eval(spotlight_info['location'][0]), 
                                                      rotation = eval(spotlight_info['rotation']), 
                                                      set_label = f"Left Spotlight",
                                                      intensity=spotlight_info['intensity'],
                                                      attenuation_radius=3000)

    right_spotlight = assets_builder.put_spotlight(location = eval(spotlight_info['location'][1]), 
                                                       rotation = eval(spotlight_info['rotation']), 
                                                       set_label = f"Right Spotlight",
                                                       intensity=spotlight_info['intensity'],
                                                       attenuation_radius=3000) 
    
    binding_builder.bind(parent = cube, child = left_spotlight, attach_method = "relative")
    binding_builder.bind(parent = cube, child = right_spotlight, attach_method = "relative")
    
    for i in range(epoch):
        # i = 3

        # 创建相机 rig
        camera_rig = assets_builder.put_camera_rig(location = eval(camera_rig_info['location']), 
                                               spline_path_points=[eval(k) for k in camera_rig_info['spline_path_points']],
                                               set_label = f"Camera_Rig_{i}",)
        
        # 创建序列
        level_sequence = assets_builder.create_level_sequence(asset_name = sequencer_name + f"_{i}", 
                                                              package_path = sequencer_path,
                                                              playback_end=playback_end)    
        sequencer_controller = MySequencer(level_sequence)
        
        # 获取绑定
        camera_binding = sequencer_controller.add_assets_to_sequence(camera)
        cube_binding = sequencer_controller.add_assets_to_sequence(cube)
        camera_rig_binding = sequencer_controller.add_assets_to_sequence(camera_rig)
        camera_cut_track = sequencer_controller.add_camera_cut_track(level_sequence)

        # 添加相机轨道
        sequencer_controller.add_camera_to_sequence(camera_cut_track = camera_cut_track, 
                                                    camera_binding = camera_binding, 
                                                    playback_start = playback_start,
                                                    playback_end = playback_end)

        # 添加绑定轨道
        camera_path_section =  SequencerBinding.bind_in_sequencer(sequencer=level_sequence,
                                                                parent_binding=cube_binding,
                                                                child_binding=camera_binding,
                                                                playback_start=playback_start,
                                                                 playback_end=playback_end)
        _ =  SequencerBinding.bind_in_sequencer(sequencer=level_sequence,
                                                parent_binding=camera_rig_binding,
                                                child_binding=cube_binding,
                                                playback_start=playback_start,
                                                playback_end=playback_end)

        # 添加相机变换轨道
        camera_transform_section = SequencerBinding.transform_in_sequencer(actor_binding=camera_binding,
                                                                          playback_start=playback_start,
                                                                          playback_end=playback_end)
        cube_transform_section = SequencerBinding.transform_in_sequencer(actor_binding=cube_binding,
                                                                         playback_start=playback_start,
                                                                         playback_end=playback_end)
        cam_y_channel = SequencerBinding.get_transform_channel(transform_section=camera_transform_section,
                                                              transform_axis='Y')
        cube_rz_channel = SequencerBinding.get_transform_channel(transform_section=cube_transform_section,
                                                               transform_axis='RZ')
        SequencerBinding.add_key_to_transform_channel(transform_channel=cam_y_channel,
                                                      total_frames=total_frames,
                                                      trans_value = 50,
                                                      trans = "trans")
        SequencerBinding.add_key_to_transform_channel(transform_channel=cube_rz_channel,
                                                      total_frames=total_frames,
                                                      trans_value = 90,
                                                      trans = "rot")

        # 添加相机轨道
        rig_track = sequencer_controller.add_track_to_sequence(camera_rig_binding, property_name = "CurrentPositionOnRail")
        sequencer_controller.add_key_to_track(track = rig_track, 
                                              total_frames = total_frames,
                                              same_position_number = 2)

if __name__ == '__main__':
    json_file_path = r'D:\\UE5\\python\\config.json'
    json_data = read_json(json_file_path)
    main(json_data)
