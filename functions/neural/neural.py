import numpy as np

class Layer:
    def __init__(self, num, next_num):
        scale = 0.1
        self.nodes = [0 for i in range(num)]
        self.weights = np.random.randn(num, next_num) * scale
        self.biases = np.zeros(next_num)

class Network:
    def __init__(self, shape):
        self.z = []
        self.learningRate = 0.01
        self.shape = shape
        self.length = len(shape)
        self.network = []
        for  i in range(self.length - 1):
            self.network.append(Layer(self.shape[i], self.shape[i + 1]))
        self.network.append([0 for i in range(shape[-1])])
    def relu(self, x):
        return np.maximum(0, x)
    
    def d_relu(self, x):
        return (x > 0).astype(float)

    def contrastive(self, e1, e2, y, margin=1.0):
        e1, e2, y = np.atleast_2d(e1), np.atleast_2d(e2), np.atleast_1d(y)
        d = np.linalg.norm(e1 - e2, axis=1)
        loss = y * d**2 + (1 - y) * np.maximum(0, margin - d)**2
        return 0.5 * loss.mean()

    def d_contrastive(self, e1, e2, y, margin=1.0):
        e1, e2, y = np.atleast_2d(e1), np.atleast_2d(e2), np.atleast_1d(y)
        diff = e1 - e2
        d = np.linalg.norm(diff, axis=1, keepdims=True) + 1e-8
        y = y[:, None]
        grad_e1 = (y * diff - (1 - y) * np.maximum(0, margin - d) * diff / d) / len(y)
        return grad_e1, -grad_e1

    def forward(self, inputs):
        # Returns (output, acts, zs). acts[i] is the input to weight layer i; zs[i] is the pre-ReLU of acts[i + 1]
        self.z = []
        acts = [np.array(inputs, dtype=float)]
        self.network[0].nodes = acts[0]
        for i in range(self.length - 2):
            z = np.dot(acts[i], self.network[i].weights) + self.network[i].biases
            self.z.append(z)
            acts.append(self.relu(z))
            self.network[i + 1].nodes = acts[-1]
        out = np.dot(acts[-1], self.network[-2].weights) + self.network[-2].biases
        self.network[-1] = out
        return out, acts, self.z

    def chainRule(self, delta, a_prev, W, z_prev = None):
        delta, a_prev = np.atleast_2d(delta), np.atleast_2d(a_prev)
        dW = np.dot(a_prev.T, delta)
        db = delta.sum(axis=0)
        d_prev = np.dot(delta, W.T)
        if z_prev is not None:
            d_prev *= self.d_relu(z_prev)
        return dW, db, d_prev
    
    def backward(self, grad_out, acts, zs):
        delta = grad_out
        dW = [None] * (self.length - 1)
        db = [None] * (self.length - 1)
        for i in reversed(range(self.length - 1)):
            z_prev = zs[i - 1] if i > 0 else None
            dW[i], db[i], delta = self.chainRule(delta, acts[i], self.network[i].weights, z_prev)
        return dW, db

    def update(self, dW, db):
        for i in range(self.length - 1):
            self.network[i].weights -= self.learningRate * dW[i]
            self.network[i].biases -= self.learningRate * db[i]

    def train_step(self, x1, x2, y, margin=1.0):
        e1, acts1, zs1 = self.forward(x1)
        e2, acts2, zs2 = self.forward(x2)
        loss = self.contrastive(e1, e2, y, margin)
        g1, g2 = self.d_contrastive(e1, e2, y, margin)
        dW1, db1 = self.backward(g1, acts1, zs1)
        dW2, db2 = self.backward(g2, acts2, zs2)
        self.update([a + b for a, b in zip(dW1, dW2)], [a + b for a, b in zip(db1, db2)])
        return loss

