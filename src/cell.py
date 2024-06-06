class Cell():
    def __init__(self, id, has_car, vector : tuple[int, int]) -> None:
        self.id = id
        self.has_car = has_car
        self.vector = vector
        
    def __eq__(self, value: object) -> bool:
        return isinstance(value, Cell) and value.id == self.id and value.vector == self.vector