from components.Component import Component
from PIL import Image

class LoadImage(Component):
    """
    This component loads an image.
    It is an interactive component, so it has no inports.
    It has one outport, which sends the loaded image.
    It has a parameter, which is the path of the image.

    """

    def __init__(self) -> None:
        """
        LoadImage constructor.
        Creates only outports since it is an interactive component.
        It has no inports. However, it has a parameter.
        Parameter is the path of the image.
        """
        self.param = None
        self.outports_types = {
            "output" : Image.Image
        }

        self.outports = {
            "output" : None
        }
        super().__init__()

    def __repr__(self) -> str:
        """
        LoadImage string representation.
        """
        return "LoadImage component"

    def run(self) -> None:
        """
        LoadImage run method.
        Gets inputs from user and sends the result to outport.
        """

        # execute component
        img = self.execute()

        # send result to outport via pipe
        self.outports["output"].send(img)
        
    def execute(self) -> Image.Image:
        """
        LoadImage execute method.
        It has no inputs.
        It loads an image from the path given by the parameter.
        It returns the loaded image.

        Returns:
            Image.Image: Loaded image.
        """
        
        return self.param