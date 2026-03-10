import math
import random

# lerp
def scale(value, from_range, to_range):
    from_min, from_max = from_range
    to_min, to_max = to_range
    return (value - from_min) / (from_max - from_min) * (to_max - to_min) + to_min


class Neuron:
    def __init__(self, num_inputs):
        # Initialize random weights
        self.weights = [random_weight() for _ in range(num_inputs)]
        self.bias = random_weight()

    def activate(self, inputs):
        # sigmoid activation function to the weighted sum of the inputs.
        weighted_sum = sum(input * weight for input, weight in zip(inputs, self.weights)) + self.bias
        return 1 / (1 + math.exp(-weighted_sum))

class Layer:
    # A layer of neurons in the neural network.
    def __init__(self, num_neurons, num_inputs):
        self.neurons = [Neuron(num_inputs) for _ in range(num_neurons)]

    def forward(self, inputs):
        # Pass the inputs through the layer, returning the outputs.
        return [neuron.activate(inputs) for neuron in self.neurons]

class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        # self.input_layer = Layer(input_size, 2)  # 2 inputs: angle and distance
        self.hidden_layer = Layer(hidden_size, input_size)
        self.output_layer = Layer(output_size, hidden_size)


    def normalize_angle(self, angle):
        # Normalize angle from [-180, 180] to [-1, 1]
        #return angle / 180.0
        return scale(angle, (-180, 180), (-1, 1))


    def normalize_distance(self, distance):
        # Normalize distance from [0, 1024] to [0, 1]
        #return distance / 1024.0
        return scale(distance, (0, 1024), (0, 1))


    def denormalize_angle_delta(self, sigmoid_output):
        #tmp = (sigmoid_output * 2) - 1 # [0 to 1] -> [-1 to 1]
        #return tmp * 3.1
        return scale(sigmoid_output, (0, 1), (-3.1, 3.1))


    def denormalize_speed(self, sigmoid_output):
        #return sigmoid_output * 4.0
        return scale(sigmoid_output, (0, 1), (-1.5, 4.0))


    def forward(self, angle, distance):
        # Pass the inputs through the network, returning the outputs.

        # Normalize inputs
        norm_angle = self.normalize_angle(angle)
        norm_distance = self.normalize_distance(distance)

        inputs = [norm_angle, norm_distance]
        hidden_outputs = self.hidden_layer.forward(inputs)
        outputs = self.output_layer.forward(hidden_outputs)

        angle_delta = self.denormalize_angle_delta(outputs[0])
        speed = self.denormalize_speed(outputs[1])
        
        return angle_delta, speed
    

    def get_dna(self):
        # Extract the weights and biases of the network as a "DNA" string.
        dna = []
        for layer in (self.hidden_layer, self.output_layer):
            for neuron in layer.neurons:
                dna.extend(neuron.weights)
                dna.append(neuron.bias)
        return dna

    def set_dna(self, dna):
        # Import the weights and biases from a "DNA" string.
        start = 0
        for layer in (self.hidden_layer, self.output_layer):
            for neuron in layer.neurons:
                neuron.weights = dna[start:start+len(neuron.weights)]
                neuron.bias = dna[start+len(neuron.weights)]
                start += len(neuron.weights) + 1

    @staticmethod
    def breed(parent1, parent2, mutation_rate=0.1, mutation_range=0.2):
        # Create a new neural network by combining DNA from two parents
        # with optional mutation
        dna1 = parent1.get_dna()
        dna2 = parent2.get_dna()
        
        # Create child with same structure as parents
        child = NeuralNetwork(
            input_size=2,
            hidden_size=len(parent1.hidden_layer.neurons),
            output_size=2
        )
        
        # Combine DNA
        child_dna = []
        for gene1, gene2 in zip(dna1, dna2):
            # Randomly choose from either parent
            gene = gene1 if random.random() < 0.5 else gene2
            
            # Possibly mutate
            if random.random() < mutation_rate:
                mutation = (random.random() * 2 - 1) * mutation_range
                gene += mutation
            
            child_dna.append(gene)
        
        child.set_dna(child_dna)
        return child

    def mutate(self, mutation_rate=0.1, mutation_range=0.2):
        # Add random mutations to the network
        # mutation_rate: Probability of each weight/bias being mutated
        # mutation_range: Maximum amount of mutation
        dna = self.get_dna()
        
        for i in range(len(dna)):
            if random.random() < mutation_rate:
                mutation = (random.random() * 2 - 1) * mutation_range
                dna[i] += mutation
        
        self.set_dna(dna)


def random_weight():
    # random weight between -1 and 1.
    # random.gauss(0, 1)
    return (random.random() * 2) - 1