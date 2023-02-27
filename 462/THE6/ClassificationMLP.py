import numpy as np


class Network:
    # Create Directed Acyclic Network of given number layers.
    def __init__(self, layers):
        
        # e.g. layers = [4,3,3]
        self.layers = layers

        # count of layers
        self.num_layers = len(layers)

        # Initialize weights
        self.weights = self.initialize_weights()

        # Create empty dictionary to store activations and z values
        self.activations = {}
        self.zs = {}

    def print_net(self):
        print("Network:")
        for i in range(0,self.num_layers-1):
            print("Layer: ", i)
            print("Weights: ", self.weights[i])
            print("Activations: ", self.activations) if len(self.activations) != 0 else print("Activations: None")
            print("")

    def initialize_weights(self):
        # Initialize weights with random values between -0.5 and 0.5
        # Store them in a dictionary
        # Each key is the index of the previous layer
        # Each value is a matrix of weights
        weights = {}
        for i in range(1,self.num_layers):
            # each weight has shape (output_size, input_size)

            # For w01 the input_size is 4 and output_size is 3
            # For w12 the input_size is 3 and output_size is 3
            input_size = self.layers[i-1]
            output_size = self.layers[i]

            # Initialize weights with random values between -0.5 and 0.5
            weights[i-1] = np.random.uniform(-0.5, 0.5, (output_size, input_size))

        return weights

    def sigmoid(self, z):
        # Sigmoid activation function
        return 1/(1+np.exp(-z))
    
    def sigmoid_derivative(self, z):
        # Derivative of sigmoid activation function
        sig = self.sigmoid(z)
        return sig*(1-sig)

    def mse(self, y, y_hat):
        # Mean squared error
        return ((y-y_hat)**2)

    def forward_pass(self, example):
        # Forward pass through the network

        # Return the activations of the output layer

        # Convert example to (1,x) vector
        example = np.array(example).reshape(-1,1)

        # Set the activations of the input layer to the example
        self.activations = {}
        self.activations[0] = example

        # Calculate the activation of each node in the layer using previous layer's activations
        for i in range(1,self.num_layers):

            # Get weights between current layer and previous layer
            W = self.weights[i-1]

            # Get activations of previous layer
            A_prev = self.activations[i-1]

            # Calculate the activation of each node in the current layer
            self.zs[i] = np.dot(W,A_prev)
            self.activations[i] = self.sigmoid(self.zs[i])

        # Return the activations of the output layer
        return self.activations[self.num_layers-1]
    

    def backward_pass(self, y, y_hat):
        # Backward pass through the network
        # Return the errors of each layer
        deltas = {}

        # Calculate the error of the output layer
        y_diff = y-y_hat
        deltas[self.num_layers-1] = y_diff*self.sigmoid_derivative(self.zs[self.num_layers-1])

        # Calculate the error of each hidden layer
        for i in reversed(range(1,self.num_layers-1)):
            # Calculate the error of the current layer using the error of the previous layer
            deltas[i] = np.dot(self.weights[i].T, deltas[i+1])*self.sigmoid_derivative(self.zs[i])
        
        return deltas
        

    def update_weights(self, deltas, learning_rate):
        # Update the weights of the network by the given learning rate and errors
        for i in range(1,self.num_layers):
            self.weights[i-1] += learning_rate * np.dot(deltas[i], self.activations[i-1].T)
        
        return self.weights
        
    


def BackPropagationLearner(X,Y, net : Network, learning_rate, epochs):
    # initialize each weight with the values min_value=-0.5, max_value=0.5,

    for epoch in range(epochs):
		# Iterate over each example
        for x,y in zip(X,Y):
            x = np.array(x).reshape(-1,1)

            # Convert y to one-hot vector
            if y == 0:
                y = np.array([1,0,0]).reshape(-1,1)
            elif y == 1:
                y = np.array([0,1,0]).reshape(-1,1)
            elif y == 2:
                y = np.array([0,0,1]).reshape(-1,1)
            
            # forward pass
            y_hat = net.forward_pass(x)
            # backward pass
            deltas = net.backward_pass(y,y_hat)

            # update weights
            net.update_weights(deltas, learning_rate)

    return net



def NeuralNetLearner(X,y, hidden_layer_sizes=None, learning_rate=0.01, epochs=100):
    """
    Layered feed-forward network.
    hidden_layer_sizes: List of number of hidden units per hidden layer if None set 3
    learning_rate: Learning rate of gradient descent
    epochs: Number of passes over the dataset
    activation:sigmoid 
	"""

    
    # Find input and output layer sizes
    input_layer_size = len(X[0])
    output_layer_size = len(np.unique(y))

    # If hidden_layer_sizes is None set it to [3] else it is like [n1, n2, n3, ...]
    if hidden_layer_sizes is None:
        hidden_layer_sizes = [3]

    # Create a list of layers
    layers = []

    # Add input layer, hidden layers and output layer to the list
    # e.g layers = [4,3,3]
    layers.append(input_layer_size)
    for i in hidden_layer_sizes:
        layers.append(i)
    layers.append(output_layer_size)

    # construct a raw network and call BackPropagationLearner
    net = Network(layers)
    net = BackPropagationLearner(X,y, net, learning_rate, epochs)

    def predict(example):
        prediction = None

        # activate input layer
        example = np.array(example).reshape(-1,1)

        # forward pass
        y_hat = net.forward_pass(example)

        # find the max node from output nodes and return the index
        prediction = np.argmax(y_hat)
        return prediction

    return predict
	
from sklearn import datasets

# Set random seed as 0
np.random.seed(0)

iris = datasets.load_iris()
X = iris.data  
y = iris.target

nNL = NeuralNetLearner(X,y)
print(nNL([4.6, 3.1, 1.5, 0.2])) #0
print(nNL([6.5, 3. , 5.2, 2. ])) #2