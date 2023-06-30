from components.Component import Component
from PIL import Image

class Crop(Component):
    """
    This component crops an image.
    Gets an image and four parameters (left, top, width, height) and returns a cropped image.
    """

    def __init__(self) -> None:
        """
        Crop constructor.
        Creates inports and outports.
        """
        super().__init__()
        self.inports_types = {
            "input" : Image.Image,
            "left" : int,
            "top" : int,
            "width" : int,
            "height" : int
        }

        self.outports_types = {
            "output" : Image.Image
        }

        self.inports = {
            "input" : None,
            "left" : None,
            "top" : None,
            "width" : None,
            "height" : None
        }

        self.outports = {
            "output" : None
        }

    def __repr__(self) -> str:
        """
        Crop string representation.
        """
        return "Crop component"


    def run(self) -> None:
        """
        Crop run method.
        Gets inputs from inports and sends the result to outport.
        """

        print(self.inports)

        # get inputs from inports via pipes
        img = self.inports["input"].recv()
        left = self.inports["left"].recv()
        top = self.inports["top"].recv()
        width = self.inports["width"].recv()
        height = self.inports["height"].recv()

        # create list of inputs
        inputs = [img,left,top,width,height]

        # execute component
        result = self.execute(inputs)

        # send result to outport via pipe
        self.outports["output"].send(result)


    def execute(self,inputs : list) -> Image.Image:
        """
        Crop execute method.
        Gets inputs from inports and returns the result.

        Args:
            inputs (list): [image, left, top, width, height]

        Returns:
            Image.Image: cropped image
        """
        # get inputs
        img, left, top, width, height = inputs
        
        # calculate right and bottom
        right = left + width
        bottom = top + height

        # crop image
        img = img.crop((left,top,right,bottom))

        return img


