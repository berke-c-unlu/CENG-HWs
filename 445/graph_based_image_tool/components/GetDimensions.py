from components.Component import Component
from PIL import Image

class GetDimensions(Component):
    """
    This component gets the dimensions of an image.
    It has one inport and two outports.
    Returns the width and height of the image.
    """
    
    def __init__(self) -> None:
        """
        GetDimensions constructor.
        Creates inports and outports.
        """
        self.inports_types = {
            "input" : Image.Image
        }

        self.outports_types = {
            "width" : int,
            "height" : int
        }

        self.inports = {
            "input" : None
        }

        self.outports = {
            "width" : None,
            "height" : None
        }
        super().__init__()

    def __repr__(self) -> str:
        """
        GetDimensions string representation.
        """
        description = self.__class__.__name__
        return description

    def run(self) -> None:
        """
        GetDimensions run method.
        Gets inputs from inports and sends the result to outports.
        """

        # get input image from inport via pipe
        img = self.inports["input"].recv()

        inputs = [img]

        # execute component
        width,height = self.execute(inputs)

        # send results to outports via pipe
        self.outports["width"].send(width)
        self.outports["height"].send(height)
        
    def execute(self,inputs: list) -> tuple:
        """
        GetDimensions execute method.
        Gets the dimensions of an image.
        Returns the width and height of the image.

        Args:
            inputs (list): [img]

        Returns:
            tuple: [width,height]
        """

        # get input image
        img = inputs[0]

        # get dimensions
        width, height = img.size

        return width,height