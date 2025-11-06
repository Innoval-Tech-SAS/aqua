class Repository:
    """
    Clase de ejemplo para un repositorio.
    """
    def __init__(self):
        self.data = ["item1", "item2", "item3"]

    def get_all(self):
        return self.data