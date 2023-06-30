from components.Component import Component
from PIL import Image

class HStack(Component):
    """
    This component stacks two images horizontally.
    It has two inports and one outport.
    """


    def __init__(self) -> None:
        """
        HStack constructor.
        Creates inports and outports.
        """
        
        self.inports_types = {
            "input1" : Image.Image,
            "input2" : Image.Image
        }

        self.outports_types = {
            "output" : Image.Image
        }

        self.inports = {
            "input1" : None,
            "input2" : None
        }

        self.outports = {
            "output" : None
        }
        super().__init__()

    def __repr__(self) -> str:
        """
        HStack string representation.
        """
        return "HStack component"

    def run(self) -> None:
        """
        HStack run method.
        Gets inputs from inports and sends the result to outport.
        """

        # get input images from inports via pipes
        img1 = self.inports["input1"].recv()
        img2 = self.inports["input2"].recv()

        # create list of inputs
        inputs = [img1,img2]

        # execute component
        result = self.execute(inputs)

        # send result to outport via pipe
        self.outports["output"].send(result)
        
    def execute(self,inputs : list) -> Image.Image:
        """
        HStack execute method.
        Stacks two images horizontally.
        Returns the stacked image.

        Args:
            inputs (list): [img1,img2]

        Returns:
            Image.Image: Horizontal stacked image
        """

        # get inputs
        img1,img2 = inputs

        # get dimensions
        width1, height1 = img1.size
        width2, height2 = img2.size

        # create new image
        new_width = width1 + width2
        new_height = max(height1,height2)
        new_image = Image.new("RGB",(new_width,new_height))

        # paste images
        new_image.paste(img1,(0,0))
        new_image.paste(img2,(width1,0))

        return new_image