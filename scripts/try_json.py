import unreal
from put_assets import PutAssets
from binding import Binding
from sequencer import MySequencer
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
    sequencer_name = json_data['sequencer_name']
    sequencer_path = json_data['sequencer_save_path']
    playback_end = json_data['playback_end']
    playback_start = json_data['playback_start']
    total_frames = playback_end - playback_start

    assets_builder = PutAssets()
    binding_builder = Binding()


    # print(epoch)
    # print(camera_info)
    # print(spotlight_info)
    # print(camera_rig_info)
    # print(sequencer_name)
    # print(sequencer_path)
    # print(eval(camera_info['rotation']))

    for i in range(epoch):
        # i= i+10
        
        left_camera, right_camera = assets_builder.put_stereo_camera(base_line = camera_info['base_line'], 
                                                                     set_label_left = f"Left_{i}", 
                                                                     set_label_right = f"Right_{i}",
                                                                     rotation=eval(camera_info['rotation']))

        camera_rig = assets_builder.put_camera_rig(set_label = f"Camera_Rig_{i}",
                                                   spline_path_points=[eval(k) for k in camera_rig_info['spline_path_points']],
                                                    location=eval(camera_rig_info['location']), )

        left_spotlight = assets_builder.put_spotlight(location = eval(spotlight_info['location'][1]), 
                                                      rotation = eval(spotlight_info['rotation']), 
                                                      set_label = f"Left Spotlight_{i}")

        right_spotlight = assets_builder.put_spotlight(location = eval(spotlight_info['location'][0]), 
                                                       rotation = eval(spotlight_info['rotation']), 
                                                       set_label = f"Right Spotlight_{i}") 

        binding_builder.bind(parent=camera_rig, child=left_camera, attach_method="relative")
        binding_builder.bind(parent=left_camera, child=left_spotlight, attach_method="relative")
        binding_builder.bind(parent=right_camera, child=right_spotlight, attach_method="relative")   

        level_sequence = assets_builder.create_level_sequence(asset_name = sequencer_name + f"_{i}", 
                                                              package_path = sequencer_path,
                                                              playback_end=playback_end) 

        sequencer_controller = MySequencer(level_sequence)
        camera_left_binding = sequencer_controller.add_assets_to_sequence(left_camera)
        camera_right_binding = sequencer_controller.add_assets_to_sequence(right_camera)
        camera_rig_binding = sequencer_controller.add_assets_to_sequence(camera_rig)
        camera_cut_track = sequencer_controller.add_camera_cut_track(level_sequence) 

        for i in range(total_frames):
            if i % 2 == 0:
                sequencer_controller.add_camera_to_sequence(camera_cut_track = camera_cut_track, 
                                                            camera_binding = camera_left_binding, 
                                                            playback_start = i, 
                                                            playback_end = i+1)
            else:
                sequencer_controller.add_camera_to_sequence(camera_cut_track = camera_cut_track,
                                                            camera_binding = camera_right_binding,
                                                            playback_start = i,
                                                            playback_end = i+1)

        rig_track = sequencer_controller.add_track_to_sequence(camera_rig_binding, property_name = "CurrentPositionOnRail")
        sequencer_controller.add_key_to_track(track = rig_track, 
                                              total_frames = total_frames,
                                              same_position_number = 2)

        # unreal.EditorAssetLibrary.save_asset(sequencer_path + sequencer_name + f"_{i}")
        # MySequencer.open_sequence_editor(level_sequence)



if __name__ == '__main__':
    json_file_path = r'./config.json'
    json_data = read_json(json_file_path)
    print(json_data)
    main(json_data)