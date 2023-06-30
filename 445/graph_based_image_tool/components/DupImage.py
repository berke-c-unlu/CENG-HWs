from components.Component import Component
from PIL import Image

class DupImage(Component):
    """
    This component duplicates an image
    It has one input port and two output ports
    Gets an image from input port and duplicates it and sends two copies to output ports
    """

    def __init__(self) -> None:
        """
        DupImage constructor.
        Creates inports and outports.
        """
        self.inports_types = {
        "input" : Image.Image
        }

        self.outports_types = {
            "output1" : Image.Image,
            "output2" : Image.Image
        }

        self.inports = {
            "input" : None
        }

        self.outports = {
            "output1" : None,
            "output2" : None
        }
        super().__init__()

    def __repr__(self) -> str:
        """
        DupImage string representation.
        """
        return "DupImage component"

    def run(self) -> None:
        """
        DupImage run method.
        Gets inputs from inports and sends the result to outports.
        """

        # get input image from inport
        img = self.inports["input"].recv()

        inputs = [img]

        # execute component
        res1, res2 = self.execute(inputs)

        #send results to outports
        self.outports["output1"].send(res1)
        self.outports["output2"].send(res2)
        
    def execute(self,inputs : list) -> Image.Image:
        """
        DupImage execute method.
        Duplicates an image.
        Returns two copies of the image.

        Args:
            inputs (list): [img]

        Returns:
            Image.Image: [img,img]
        """

        # get input image
        inp = inputs[0]
        
        # duplicate image
        img2 = inp.copy()

        return inp,img2
        