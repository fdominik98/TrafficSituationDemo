class State():
    def __init__(self, name : str, parameters : list[str], variable_names : list[str]) -> None:
        self.name : str = name
        self.paramaters = parameters
        self.variable_names = variable_names
        
    def __str__(self) -> str:
        return f"{self.name}{self.paramaters}"