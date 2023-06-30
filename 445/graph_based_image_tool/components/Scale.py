from components.Component import Component
from PIL import Image

class Scale(Component):
    """
    This component scales an image by a given factor.
    It has two inports and one outport.
    """


    def __init__(self) -> None:
        """
        Scale constructor.
        Creates inports and outports.
        """
        self.inports_types = {
            "input" : Image.Image,
            "scale" : float
        }

        self.outports_types = {
            "output" : Image.Image
        }

        self.inports = {
            "input" : None,
            "scale" : None
        }

        self.outports = {
            "output" : None
        }
        super().__init__()

    def __repr__(self) -> str:
        """
        Scale string representation.
        """
        return "Scale component"

    def run(self) -> None:
        """
        Scale run method.
        Gets inputs from inports and sends the result to outport.
        """

        # get input image from inports via pipes
        img = self.inports["input"].recv()
        scale = self.inports["scale"].recv()

        # create list of inputs
        inputs = [img,scale]
        
        # execute component
        result = self.execute(inputs)

        # send results to outport via pipe
        self.outports["output"].send(result)
        
        
    def execute(self,inputs : list) -> Image.Image:
        """
        Scale execute method.
        Scales an image by a given factor.
        Returns the scaled image.

        Args:
            inputs (list): [img,scale]

        Returns:
            Image.Image: scaled image
        """

        # get inputs
        img,scale = inputs

        # scale image
        width, height = img.size
        width = int(width*scale)
        height = int(height*scale)
        img = img.resize((width,height))

        return img

        
