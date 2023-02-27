import copy
import random


class Node:
    def __init__(self, parents : list , name : str):
        self.parents = parents
        self.children = []
        self.name = name
        self.conditional_probabilities = {}
        self.probability = 0

    def print_node(self):
        print("Name: ",self.name)
        print("Parents: ",[parent.name for parent in self.parents])
        print("Children: ",[child.name for child in self.children])
        print("Conditional Probabilities: ",self.conditional_probabilities)
        print("Probability: ", self.probability)
        print('-----------------')

class BayesNet:
    def __init__(self):
        self.Nodes = []
        self.query_key = ''
        self.Query = {}

    # Parse Nodes
    def parse_nodes(self, startIndex : int , endIndex : int , all_lines : list):
        for i in range(startIndex, endIndex):
            self.Nodes.append(Node([], all_lines[i].strip()))
        
    # find given node using node name
    def find_node(self, name : str) -> Node or None:
        for node in self.Nodes:
            if node.name == name:
                return node
        return None

    # parse paths
    def parse_paths(self, startIndex : int , endIndex : int , all_lines : list):
        for i in range(startIndex, endIndex):
            parents,child = eval(all_lines[i].strip())
            childNode = self.find_node(child)
            for parent in parents:
                parentNode = self.find_node(parent)
                if parentNode != None:
                    childNode.parents.append(parentNode)
                parentNode.children.append(childNode)

    # parse probability table
    def parse_probability_table(self, startIndex : int , endIndex : int , all_lines : list):
        for i in range(startIndex, endIndex):
            node, parents, probabilities = eval(all_lines[i].strip())
            current_node = self.find_node(node)
            if(len(probabilities) == 1):
                if current_node != None:
                    current_node.probability = probabilities.pop()
            else:
                if current_node != None:
                    parents_tuple = tuple(parents)
                    current_node.conditional_probabilities[parents_tuple] = probabilities

    # parse query
    def parse_query(self, startIndex : int , all_lines : list):
        query = eval(all_lines[startIndex + 1])
        self.Query[query[0]] = query[1]
        self.query_key = query[0]

    # Enumeration ask algorithm
    def enumeration_ask(self, X : str , e : dict):
        # qx, a vector of probabilities for each value of X , initially empty
        qx = []
        # for each value xi of X
        for xi in [True, False]:
            # extend e with {X = xi}
            ex = copy.deepcopy(e)
            ex[X] = xi
            # add ENUMERATION-ALL(bn.VARS, e) to qx
            qx.append(self.enumeration_all(self.Nodes, ex))
        
        # return NORMALIZE(qx)
        qx = self.normalize_probabilities(qx)
        return qx

    # Enumeration all algorithm    
    def enumeration_all(self, vars : list, e : dict) -> float:
        
        # if VARS is empty then return 1.0
        if len(vars) == 0:
            return 1.0

        # pick first variable Y in VARS
        Y = vars[0]

        # if Y is in e
        if Y.name in e.keys():
            # return P(Y | e) * ENUMERATION-ALL(VARS - {Y}, e)
            return self.get_probability(Y, e) * self.enumeration_all(vars[1:], e)
        
        else:
            # create a new vector of probabilities for Y
            probabilities = []
            
            ey = copy.deepcopy(e)

            # for each value yi of Y
            for yi in [True, False]:
                # extend e with {Y = yi}
                ey[Y.name] = yi
                # add P(Y = yi | e) * ENUMERATION-ALL(VARS - {Y}, e) to the vector
                probabilities.append(self.get_probability(Y, ey) * self.enumeration_all(vars[1:], ey))

            # return the sum of the vector
            return sum(probabilities)
    
    # Normalize probabilities
    def normalize_probabilities(self, qx : list) -> tuple:
        # copy qx
        q = copy.deepcopy(qx)
        # sum all elements of qx
        q_sum = sum(q)

        # for each element of qx
        for i in range(len(q)):
            # divide by sum and round to 3 decimal places
            q[i] = round(q[i] / q_sum,3)
        
        # return tuple of qx
        q = tuple(q)
        return q
        
    # Get probability of a node given evidence
    def get_probability(self, Y : Node , e : dict):
        # if Y has no parents
        if len(Y.parents) == 0:
            # return probability of Y if Y is in e else return 1 - probability of Y
            return Y.probability if e[Y.name] else 1.0 - Y.probability

        # if Y has one parent
        elif len(Y.parents) == 1:
            # create a tuple of parent name
            parent = tuple([Y.parents[0].name])
            # get parent condition
            parent_condition = e[Y.parents[0].name]
            # return conditional probability of Y given parent condition
            return Y.conditional_probabilities[parent][parent_condition] if e[Y.name] else 1.0 - Y.conditional_probabilities[parent][parent_condition]

        # if Y has more than one parent
        else:
            # create a tuple of parent names
            condition_tuple = tuple([e[parent.name] for parent in Y.parents])
            # create a tuple of parent names
            parents_tuple = tuple([parent.name for parent in Y.parents])
            # return conditional probability of Y given parent conditions
            return Y.conditional_probabilities[parents_tuple][condition_tuple] if e[Y.name] else 1.0 - Y.conditional_probabilities[parents_tuple][condition_tuple]
    
    # Gibbs Ask algorithm
    def gibbs_ask(self, X : str , e : dict, Iteration : int):
        # N, a vector of counts for each value of X , initially zero
        # Z, the nonevidence variables in bn
        # x, the current state of the network, initially copied from e

        random.seed(10)

        N = [0,0]
        Z = {}
        x = copy.deepcopy(e)

        # choose a random value for each variable in Z
        for node in self.Nodes:
            if node.name not in x.keys():
                Z[node.name] = random.choice([True, False])
        
        # initialize x with random values for each variable in Z
        for zi in Z.keys():
            x[zi] = Z[zi]

        

        # for i = 1 to Iteration do
        for _ in range(Iteration):
            # for each variable zi in Z do
            for zi in Z.keys():
                # Create Markov Blanket for zi
                markov_blanket = self.create_markov_blanket(self.find_node(zi))
                # set zi to a value from P(zi | mb(zi))
                x[zi] = self.gibbs_sample(zi, x, markov_blanket)
                if x[X]:
                    N[0] += 1
                else:
                    N[1] += 1

        N = self.normalize_probabilities(N)
        return N

    def gibbs_sample(self, var : str, x : dict, MarkovBlanket : dict) -> bool:

        # get parent evidence list of var
        parent_evidence = {}
        for parent in MarkovBlanket['parents']:
            parent_evidence[parent.name] = x[parent.name]
        
        # P(x : True | parent evidence)
        parent_evidence[var] = True
        probability_true = self.get_probability(self.find_node(var), parent_evidence)

        # P(x : False | parent evidence)
        parent_evidence[var] = False
        probability_false = self.get_probability(self.find_node(var), parent_evidence)

        
        # get probability of children given parent evidence
        for child in MarkovBlanket['children']:
            child_evidence = {}
            for parent in MarkovBlanket['parents_of_children'][child.name]:
                child_evidence[parent.name] = x[parent.name]

            # append child to the evidence list to get probability
            child_evidence[child.name] = x[child.name]
            
            # Set X : True since we are calculating probability of X : True
            child_evidence[var] = True
            probability_true *= self.get_probability(child, child_evidence)

            # Set X : False since we are calculating probability of X : False
            child_evidence[var] = False
            probability_false *= self.get_probability(child, child_evidence)

        # Sum P(x : True | parent evidence) and P(x : False | parent evidence)
        prob_total = probability_true + probability_false

        # Normalize probabilities
        probability_true = probability_true / prob_total
        probability_false = probability_false / prob_total

        # return True if random number is less than probability of True else return False
        return random.random() < probability_true 



        

    def create_markov_blanket(self, node : Node) -> dict:
        # create a dictionary to store markov blanket
        markov_blanket = {}

        # create a list to store parents of node
        parent_list = []
        # create a list to store children of node
        child_list = []
        # create a dictionary to store parents of children of node
        # key is the name of child and value is a list of parents of child
        parent_of_child_list = {}
        
        for parent in node.parents:
            parent_list.append(parent)
        for child in node.children:
            child_list.append(child)
            parent_of_child_list[child.name] = []
            for parent in child.parents:
                parent_of_child_list[child.name].append(parent)

        markov_blanket['parents'] = parent_list
        markov_blanket['children'] = child_list
        markov_blanket['parents_of_children'] = parent_of_child_list
        return markov_blanket
        
    


def DoInference(method_name : str, problem_file_name : str, num_iteration : int):
    # create bayes net
    bayes_net = BayesNet()

    with open(problem_file_name, 'r') as f:
        
        # read all lines
        all_lines = f.readlines()
        # find the index of each section in the file
        node_loc = all_lines.index('[BayesNetNodes]\n')
        path_loc = all_lines.index('[Paths]\n')
        prob_loc = all_lines.index('[ProbabilityTable]\n')
        query_loc = all_lines.index('[Query]\n')

        # parse each section
        bayes_net.parse_nodes(node_loc + 1, path_loc, all_lines)
        bayes_net.parse_paths(path_loc + 1, prob_loc, all_lines)
        bayes_net.parse_probability_table(prob_loc + 1, query_loc, all_lines)
        bayes_net.parse_query(query_loc, all_lines)


    # run bayes net inference method based on the method name    
    if method_name == 'ENUMERATION':
        return bayes_net.enumeration_ask(bayes_net.query_key, bayes_net.Query[bayes_net.query_key])
    
    elif method_name == 'GIBBS':
        return bayes_net.gibbs_ask(bayes_net.query_key, bayes_net.Query[bayes_net.query_key], num_iteration)
            