import unreal

class SequencerBinding:
    def __init__(self):
        pass

    @staticmethod
    def bind_in_sequencer(
                          sequencer,
                          parent_binding,
                          child_binding,
                          playback_start: float = None,
                          playback_end: float = None,):
        """
        Binds the child binding to the parent binding using a 3D attach section.

        :param sequencer: The sequencer which is used to create the attach section.
        :param parent_binding: The parent binding to attach to.
        :param child_binding: The child binding to attach.
        :param playback_start: The start time of the child binding in the parent binding's time range.
        :param playback_end: The end time of the child binding in the parent binding's time range.

        Example usage:
            If you want to let a cube follow a path, parent_binding is the path, child_binding is the cube.

        """
        
        path_track = child_binding.add_track(unreal.MovieScene3DAttachTrack)
        path_section = path_track.add_section()
        path_section.set_constraint_binding_id(sequencer.make_binding_id(parent_binding, unreal.MovieSceneObjectBindingSpace.LOCAL))
        if playback_start is not None and playback_end is not None:
            path_section.set_range(playback_start, playback_end)

        return path_section

    
    @staticmethod
    def transform_in_sequencer(
                               actor_binding,
                               playback_start: float = None,
                               playback_end: float = None,):
        
        transform_track = actor_binding.add_track(unreal.MovieScene3DTransformTrack)
        transform_section = transform_track.add_section()
        if playback_start is not None and playback_end is not None:
            transform_section.set_range(playback_start, playback_end)

        return transform_section
    
    @staticmethod
    def get_transform_channel(
                               transform_section,
                               transform_axis: str,):
        
        channels = transform_section.get_channels()
        if transform_axis == "x" or transform_axis == "X":
            position_x = channels[0]
            return position_x
        elif transform_axis == "y" or transform_axis == "Y":
            position_y = channels[1]
            return position_y
        elif transform_axis == "z" or transform_axis == "Z":
            position_z = channels[2]
            return position_z
        elif transform_axis == "rx" or transform_axis == "RX":
            rotation_x = channels[3]
            return rotation_x
        elif transform_axis == "ry" or transform_axis == "RY":
            rotation_y = channels[4]
            return rotation_y
        elif transform_axis == "rz" or transform_axis == "RZ":
            rotation_z = channels[5]
            return rotation_z
        else:
            return None
        
    @staticmethod
    def add_key_to_transform_channel(
                                     transform_channel,
                                     total_frames: int = 100,
                                     trans_value: int = 1,
                                     trans: str = "trans",):
        """
        This is a customized func for user's convenience.
        """
        
        if trans == "trans":
            for frame in range(total_frames +1):
                if frame % 2 == 0:
                    # 计算Current Position的值
                    # current_position = frame / float(20)
                # 添加关键帧
                    transform_channel.add_key(unreal.FrameNumber(frame),0.0)  # 初始位置
                else:
                    transform_channel.add_key(unreal.FrameNumber(frame),trans_value)
        elif trans == "rot":
            transform_channel.add_key(unreal.FrameNumber(0),90.0)
            transform_channel.add_key(unreal.FrameNumber(total_frames),90.0)
