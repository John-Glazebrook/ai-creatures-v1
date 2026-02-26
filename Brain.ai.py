import json
import math
import random

class Brain:
    def __init__(self, input_size=2, hidden_size=6, output_size=2):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.weights = self._random_weights()

    def _random_weights(self):
        return [
            [[random.gauss(0, 1) for _ in range(self.hidden_size)] for _ in range(self.input_size)],
            [[random.gauss(0, 1) for _ in range(self.output_size)] for _ in range(self.hidden_size)],
        ]

    def _tanh(self, x):
        return math.tanh(x)

    def _matmul(self, inputs, weights):
        return [
            sum(inputs[i] * weights[i][j] for i in range(len(inputs)))
            for j in range(len(weights[0]))
        ]

    def forward(self, inputs):
        hidden = [self._tanh(x) for x in self._matmul(inputs, self.weights[0])]
        output = [self._tanh(x) for x in self._matmul(hidden, self.weights[1])]
        return output  # [speed, turn_delta]

    def mutate(self, rate=0.1):
        child = Brain(self.input_size, self.hidden_size, self.output_size)
        child.weights = [
            [[w + random.gauss(0, rate) for w in row] for row in layer]
            for layer in self.weights
        ]
        return child

    def save(self, path):
        data = {
            "input_size": self.input_size,
            "hidden_size": self.hidden_size,
            "output_size": self.output_size,
            "weights": self.weights,
        }
        with open(path, "w") as f:
            json.dump(data, f)

    @classmethod
    def load(cls, path):
        with open(path) as f:
            data = json.load(f)
        brain = cls(data["input_size"], data["hidden_size"], data["output_size"])
        brain.weights = data["weights"]
        return brain