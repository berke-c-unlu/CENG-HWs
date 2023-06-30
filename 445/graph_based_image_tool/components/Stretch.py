from components.Component import Component
from PIL import Image


class Stretch(Component):
    """
    This component stretches an image to a given width and height.
    It has three inports and one outport.
    """

    def __init__(self):
        """
        Stretch constructor.
        Creates inports and outports.
        """

        self.inports_types = {
            "input" : Image.Image,
            "width" : int,
            "height" : int
        }

        self.outports_types = {
            "output" : Image.Image
        }

        self.inports = {
            "input" : None,
            "width" : None,
            "height" : None
        }

        self.outports = {
            "output" : None
        }
        super().__init__()

    def __repr__(self):
        """
        Stretch string representation.
        """
        return "Stretch component"

    def run(self):
        """
        Stretch run method.
        Gets inputs from inports and sends the result to outport.
        """

        # get inputs from inports via pipes
        img = self.inports["input"].recv()
        width = self.inports["width"].recv()
        height = self.inports["height"].recv()

        # create list of inputs
        inputs = [img,width,height]

        # execute component
        result = self.execute(inputs)

        # send result to outport via pipe
        self.outports["output"].send(result)
        

        
    def execute(self,inputs : list) -> Image.Image:
        """
        Stretch execute method.
        Stretches an image to a given width and height.
        Returns the stretched image.

        Args:
            inputs (list): [img,width,height]

        Returns:
            Image.Image: stretched image
        """
        # get inputs
        img,width,height = inputs

        # stretch image
        img = img.resize((width,height))

        return img