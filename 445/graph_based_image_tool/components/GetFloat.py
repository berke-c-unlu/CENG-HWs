from components.Component import Component


class GetFloat(Component):
    """
    This component gets a float from the user.
    It has no inports and one outport.
    It is an interactive component.
    It has a parameter that user can set.
    """
    
    
    def __init__(self) -> None:
        """
        GetFloat constructor.
        Creates only one outport.
        """
        super().__init__()
        self.param = None
        self.outports_types = {
            "output" : float
        }

        self.outports = {
            "output" : None
        }

    def __repr__(self) -> str:
        """
        GetFloat string representation.
        """
        return "GetFloat component"
    
    
    def run(self) -> None:
        """
        GetFloat run method.
        Gets a float from the user and sends it to outport.
        """

        # execute component
        num = self.execute()

        # send result to outport via pipe
        self.outports["output"].send(num)
        
    def execute(self) -> float:
        """
        GetFloat execute method.
        Returns a float from the user.

        Returns:
            float: float from the user
        """
        return float(self.param)
        
