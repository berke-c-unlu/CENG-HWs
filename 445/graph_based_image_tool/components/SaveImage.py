from components.Component import Component
from PIL import Image


class SaveImage(Component):
    """
    This component saves an image to a file.
    It is an interactive component.
    It has one inport and no outports.
    It has one parameter which is the path of the file to save the image to.
    """


    def __init__(self) -> None:
        """
        SaveImage constructor.
        Creates only inports.
        """
        self.param = None
        self.inports_types = {
            "input" : Image.Image,
        }

        self.inports = {
            "input" : None,
        }
        super().__init__()

    def __repr__(self) -> str:
        """
        SaveImage string representation.
        """
        return "SaveImage component"

    def run(self) -> None:
        """
        SaveImage run method.
        Gets inputs from inport and saves the image to a file.
        File path is given by the parameter.
        """

        # get input image from inport via pipe
        img = self.inports["input"].recv()

        # create list of inputs
        inputs = [img]

        # execute component
        self.execute(inputs)
        
    def execute(self,inputs : list) -> None:     
        """
        SaveImage execute method.
        Saves an image to a file.
        File path is given by the parameter.

        Args:
            inputs (list): [img]
        """

        # get input image
        img = inputs[0]

        # save image
        img.save(self.param)
        