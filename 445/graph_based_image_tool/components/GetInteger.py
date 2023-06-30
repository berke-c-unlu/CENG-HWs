from components.Component import Component



class GetInteger(Component):
    """
    This component gets an integer from user and returns it.
    It is an interactive component.
    """
    
    
    def __init__(self) -> None:
        """
        GetInteger constructor.
        Creates only outports since it is an interactive component.
        It has no inports. However, it has a parameter.
        Parameter is the integer that user enters.
        """
        self.param = None
        self.outports_types = {
            "output" : int
        }

        self.outports = {
            "output" : None
        }
        super().__init__()

    def __repr__(self) -> str:
        """
        GetInteger string representation.
        """
        return "GetInteger component"

    def run(self) -> None:
        """
        GetInteger run method.
        Gets inputs from inports and sends the result to outport.
        """

        # execute component
        num = self.execute()

        # send result to outport via pipe
        self.outports["output"].send(num)
        
    def execute(self) -> int:
        """
        GetInteger execute method.
        It has no inputs.
        It gets an integer from user and returns it.

        Returns:
            int: User entered integer.
        """
        # get int
        return int(self.param)