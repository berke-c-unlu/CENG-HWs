from components.Component import Component
from PIL import Image


class Rotate(Component):
    """
    This component rotates an image.
    Gets an image and an angle and returns a rotated image.
    """
    
    def __init__(self) -> None:
        """
        Rotate constructor.
        Creates inports and outports.
        """
        
        self.inports_types = {
            "input" : Image.Image,
            "angle" : int
        }

        self.outports_types = {
            "output" : Image.Image
        }

        self.inports = {
            "input" : None,
            "angle" : None
        }

        self.outports = {
            "output" : None
        }
        super().__init__()

    def __repr__(self) -> str:
        """
        Rotate string representation.
        """
        return "Rotate component"

    def run(self) -> None:
        """
        Rotate run method.
        Gets inputs from inports and sends the result to outport.
        """

        # get inputs from inports via pipes
        img = self.inports["input"].recv()
        angle = self.inports["angle"].recv()

        # create list of inputs
        inputs = [img,angle]

        # execute component
        result = self.execute(inputs)

        # send result to outport via pipe
        self.outports["output"].send(result)
        
    def execute(self,inputs : list) -> Image.Image:
        """
        Rotate execute method.
        Gets inputs and returns the result.

        Args:
            inputs (list): [img,angle]

        Returns:
            Image.Image: rotated image
        """
        
        # get inputs
        img, angle = inputs

        # rotate image
        img = img.rotate(angle)

        return img
        