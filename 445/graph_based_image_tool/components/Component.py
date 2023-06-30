from multiprocessing import Process

class Component(Process):
    """ Component class.
    Each operation is derived from this class.
    This class is inherits from Process class.
    """

    def __init__(self) -> None:
        super().__init__()

    def run(self) -> None:
        """ 
        This method is called when the component is executed.
        All the components must implement this method.
        """
        pass


    def execute(self,inputs : list) -> None:
        """ 
        This method is called when the component is executed.
        All the components must implement this method except interactive components.

        Args:
            inputs (list): List of inputs.
        """
        pass

    