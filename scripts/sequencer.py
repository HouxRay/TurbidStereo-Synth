import unreal
from typing import List,Union

class MySequencer:
    '''
    A class to operate a level sequencer.
    Contents:
        add_assets_to_sequence: Add assets to the sequence.
        add_camera_track: Add a new camera track to the sequence.
        add_camera_to_sequence: Add a new camera to the sequence.
        add_track_to_sequence: Add a new track to the sequence.
        add_key_to_track: Add a new key to the track.
        open_sequence_editor: Open the level sequence editor.(Staticmethod)
    '''
    def __init__(self, level_sequence: unreal.AssetTools = None):
        '''
        Args:
            level_sequence (unreal.AssetTools): The level sequence to use.
            If None, a new level sequence will be created with default settings.
        Default_settings:
            Name: MyLevelSequence
            Saving path: /Game/MySequence
        '''
        if level_sequence is None:
            pass
            print("Do not have level sequence, creating new level sequence, using default settings")
            asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
            asset_name = 'MyLevelSequence1'
            package_path = '/Game/MySequence' 	
            self.level_sequence = unreal.AssetTools.create_asset(asset_tools, 
                                                    asset_name = asset_name, 
                                                    package_path = package_path, 
                                                    asset_class = unreal.LevelSequence, 
                                                    factory = unreal.LevelSequenceFactoryNew())
        else:
            self.level_sequence = level_sequence
    
    def add_assets_to_sequence(self, asset):
        '''
        Add assets to the sequence.
        Args:
            asset : The asset to add to the sequence.
        Returns:
            asset_binding: The asset binding created by adding the assets to the sequence.
        '''
        try:
            asset_binding = self.level_sequence.add_possessable(asset)
            return asset_binding
        except:
            print("Assets should be a unreal.Object or a list of unreal.Object")
            return None
    

    def add_camera_cut_track(self,
                         level_sequence,
                         ):
        '''
        Add a new camera track to the sequence.
        Args:
            level_sequence (unreal.LevelSequence): The level sequence to add the camera track to.
        Returns:
            camera_track: The camera track created by adding the camera track to the sequence.
        '''        
        camera_cut_track = level_sequence.add_master_track(unreal.MovieSceneCameraCutTrack)
        return camera_cut_track
    
    def add_camera_to_sequence(self, 
                               camera_cut_track:unreal.MovieSceneCameraCutTrack,
                               camera_binding,
                               playback_start: int = 0,
                               playback_end: int = 100,):
        '''
        Add a new camera to the sequence.
        Args:
            camera_cut_track (unreal.MovieSceneCameraCutTrack): The camera cut track to add the camera to.
            camera_binding : The camera binding to add to the sequence.
            playback_start (int): The start frame of the camera. Defaults to 0.
            playback_end (int): The end frame of the camera. Defaults to 100.
        '''
        camera_section = camera_cut_track.add_section()
        camera_section.set_range(playback_start, playback_end)    
        camera_section.set_camera_binding_id(camera_binding.get_binding_id()) 
        
        
    def add_track_to_sequence(self, 
                              asset_binding: unreal.Object, 
                              property_name:str = None,
                               ):
        '''
        Add a new track to the sequence.
        Args:
            asset_binding (unreal.Object): The asset binding to add the track to.(Created by 'add_assets_to_sequence()')
            property_name (str, optional): Set the property name of the track. Defaults to None.(Warning: If choosing a property name, the property_name must be expoessed in the blueprint of the asset, or the property_name will not work.)
            total_frames (int, optional): The total frames of the track. Defaults to 100.
        '''
        try:
            track = asset_binding.add_track(unreal.MovieSceneFloatTrack)
            if property_name is not None:
                track.set_property_name_and_path(property_name, property_name)
                print(type(track))
            return track
        except:
            print("Asset binding should be a unreal.Object")
            return None, None

    def add_key_to_track(self, 
                         track,
                         total_frames: int = 100,
                         same_position_number: int = 1,
                         is_modify: bool = False,
                         frame: Union[unreal.FrameNumber, List[unreal.FrameNumber]] = unreal.FrameNumber(1),
                         current_position: Union[float, List[float]] = 0.0, ):
        '''
        Add a new key to the track. If is_modify is False, using linear division to create keys.
        Args:
            track (unreal.MovieSceneFloatTrack): The track to add the key to.
            total_frames (int, no need if is_modify is True): The total frames of the track. Defaults to 100.
            same_position_number (int, no need if is_modify is True): The number of frames to have the same position. Defaults to 1.
            is_modify (bool): Whether to modify the key. Defaults to False.
            frame (Union[unreal.FrameNumber, List[unreal.FrameNumber]], must if is_modify is True): The frame to add the key to. Defaults to None.
            current_position (Union[float, List[float]], must if is_modify is True): The current position of the key. Defaults to 0.0.
        '''
        
        current_position_section = track.add_section()
        current_position_section.set_range(0, total_frames)        
        channels = current_position_section.find_channels_by_type(unreal.MovieSceneScriptingFloatChannel)
        if is_modify:
            if type(frame) == list:
                if type(current_position) == list:
                    for i in len(current_position):
                        float_channel.add_key(frame[i], current_position[i])
                else:
                    float_channel.add_key(frame[i], current_position)
            elif type(frame) == unreal.FrameNumber or type(frame) == int:
                if type(current_position) == list:
                    for i in len(current_position):
                        float_channel.add_key(frame, current_position[i])
                else:
                    float_channel.add_key(frame, current_position)
            else:
                print("Frame should be a unreal.FrameNumber or a list of unreal.FrameNumber")
                return None
        
        else:
            if len(channels) > 0:
                float_channel = channels[0]
            else:
                float_channel = current_position_section.add_channel(unreal.MovieSceneScriptingFloatChannel)

            for frame in range(total_frames+1):
                if frame % same_position_number == 0:
                        current_position = frame / float(total_frames)
                float_channel.add_key(unreal.FrameNumber(frame), current_position)

        # float_channel.add_key(unreal.FrameNumber(frame), current_position)


    @staticmethod
    def open_sequence_editor(level_sequence: unreal.LevelSequence = None):
        '''
        Open the level sequence editor.

        Staticmethod
        Args:
            level_sequence (unreal.LevelSequence, optional): The level sequence to open. Defaults to None.
        '''
        unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(level_sequence)

if __name__ == '__main__':
    from put_assets import PutAssets
    my_level_sequence = PutAssets()
    level_sequence = my_level_sequence.create_level_sequence()
    camera = my_level_sequence.put_camera(location=(0,0,0), rotation=(0,0,0))
    cam_rig = my_level_sequence.put_camera_rig()

    sequencer = MySequencer(level_sequence)
    asset_binding = sequencer.add_assets_to_sequence(cam_rig)
    track = sequencer.add_track_to_sequence(asset_binding, property_name = "CurrentPositionOnRail")
    sequencer.add_key_to_track(track,same_position_number=2)
    MySequencer.open_sequence_editor(level_sequence)
    # unreal.EditorAssetLibrary.save_asset("/Game/Sequencer/MySequencer")
