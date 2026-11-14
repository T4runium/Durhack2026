import numpy as np

class Layer:
    def __init__(self, num, next_num):
        scale = 0.1
        self.nodes = [0 for i in range(num)]
        self.weights = np.random.rand(num, next_num) * scale
        self.biases = [0 for i in range(next_num)]

class Network:
    def __init__(self, shape):
        self.shape = shape
        self.length = len(shape)
        self.network = []
        for  i in range(self.length - 1):
            self.network.append(Layer(self.shape[i], self.shape[i + 1]))
        self.network.append([0 for i in range(shape[-1])])
    def relu(self, x):
        return np.maximum(0, x)
    
    def d_relu(self, x):
        return (x > 0).astype.float

    def forward(self, inputs):
        self.network[0].nodes = inputs
        for i in range(self.length - 2):
            self.network[i + 1].nodes = self.relu(np.dot(self.network[i].nodes, self.network[i].weights) + self.network[i].biases)
        self.network[-1] = np.dot(self.network[-2].nodes, self.network[-2].weights) + self.network[-2].biases
        print(self.network[-1])

test = Network([2, 8, 8, 2])
test.forward([5, 5])