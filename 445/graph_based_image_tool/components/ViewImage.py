from components.Component import Component
from PIL import Image

class ViewImage(Component):
    """
    This component shows an image.
    It has one inport and no outports.
    """

    def __init__(self) -> None:
        """
        ViewImage constructor.
        Creates only one inport.
        """
        self.inports_types = {
            "input" : Image.Image
        }

        self.inports = {
            "input" : None
        }
        super().__init__()

    def __repr__(self) -> str:
        """
        ViewImage string representation.
        """
        return "ViewImage component"

    def run(self) -> None:
        """
        ViewImage run method.
        Gets input from inport and shows the image.
        """

        # get input image from inport via pipe
        img = self.inports["input"].recv()

        # create list of inputs
        inputs = [img]

        # execute component
        self.execute(inputs)
        
    def execute(self,inputs : list) -> None:
        """
        ViewImage execute method.
        Shows an image.

        Args:
            inputs (list): [img]
        """
        
        # get input image
        img = inputs[0]

        # show image
        img.show(title="Image")

