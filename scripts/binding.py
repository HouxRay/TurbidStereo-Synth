import unreal

class Binding:
    """
    A class for binding objects in Unreal Engine 5.
    """
    def __init__(self):
        pass
    
    def bind(self, parent, child, attach_method: str= "world"):
        """
        Create a binding between father and child.
        Args:
            parent: the parent of child
            child: the child of parent
            attach_method: "world" or "relative" or "snap"(Default: "world")
            AttachMethod:
                world: base on the world coordinate system

                relative: base on the parent's relative coordinate system
                
                snap: snap to the target
        """
        if attach_method == "world":
            attach_rule = unreal.AttachmentRule.KEEP_WORLD
        elif attach_method == "relative":
            attach_rule = unreal.AttachmentRule.KEEP_RELATIVE
        elif attach_method == "snap":
            attach_rule = unreal.AttachmentRule.SNAP_TO_TARGET
        else:
            print("Invalid attach method")
            return 0
    
        child.attach_to_actor(parent, 
                                  unreal.Name("None"), 
                                  attach_rule, 
                                  attach_rule, 
                                  attach_rule)
