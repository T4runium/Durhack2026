import numpy as np

class NeuralNetwork:
    def __init__(self, input_size: int, hidden_size: int, output_size: int) -> None:
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        # Initialize weights and biases here (e.g., using random values)