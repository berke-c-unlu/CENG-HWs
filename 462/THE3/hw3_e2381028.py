# function to copy array and return new array
def copy_array(arr : list):
    copied = []
    for i in arr:
        copied.append(i)
    return copied



# Each node has state, successors and utility value
# State : [a,b,c,...] where a,b,c are number of stones in each pile
# Successors : list of nodes which are successors of current node
# Utility : utility value of node (1 if MAX player wins, -1 if MIN player wins, 0 if game is not finished)
class Node:
    # Initialize node with state, successors and max_or_min value
    def __init__(self,state : list = [], successors : list = [], max_or_min : str = "MAX"):
        self.state = state
        self.successors = successors
        self.utility = self.set_utility(max_or_min)

    
    # function to check if node is terminal node
    def is_terminal_node(self) -> bool:
        if self.successors == [] and sum(self.state) == 0:
            return True
        return False


    # function to set utility of node at the beginning of construction of tree
    def set_utility(self,max_or_min : str) -> int:
        if self.is_terminal_node():
            if max_or_min == "MAX":
                return 1
            else:
                return -1
        else:
            return 0   


# Game tree stores root node
# Game tree has create_tree function to create game tree
# Game tree has create_successors function to create successors of node
# We can access every node from the root node
class GameTree:

    # Initialize game tree with root and max_or_min value
    def __init__(self, root : Node, max_or_min : str):
        self.root = Node(state=root,successors=[],max_or_min=max_or_min)
    
    # Recursive function to create game tree
    def create_tree(self,root : Node, max_or_min : str):
        # create successors of root
        successors = self.create_successors(root,max_or_min)
        # set successors of root
        root.successors = successors

        # for every successor create subtree with opposite max_or_min value
        for successor in successors:
            if max_or_min == "MAX":
                self.create_tree(successor,"MIN")
            else:
                self.create_tree(successor,"MAX")

    # Function to create successors of node
    # If node is terminal node return empty list
    def create_successors(self,node : Node, max_or_min : str) -> list:
        if node.is_terminal_node():
            return []
        # create successors of node
        successors = []

        # for every pile in state
        # start from 0 to current number of pile and insert

        # state : [a,b,c]
        for j in range(len(node.state)):
            # pile is a or b or c
            pile = node.state[j]
            for i in range(0,pile):
                # create new successor
                successor_state = copy_array(node.state[:j]) + [i] + copy_array(node.state[j+1:])

                # create new node
                new_node = Node(state = successor_state,successors=[],max_or_min=max_or_min)

                # add new node to successors
                successors.append(new_node)

        return successors



def minimax(root : Node,player_type : str):
    # count number of nodes
    count = 0
    return value(root,player_type,count)

def value(node : Node, player_type : str, count : int):
    # if node is terminal node return utility and number of nodes
    if node.is_terminal_node():
        return node.utility,count

    # if MAX player's turn return max_value
    # if MIN player's turn return min_value
    if player_type == "MAX":
        return max_value(node,count)
    else:
        return min_value(node,count)

def max_value(node : Node, count : int):
    # set v to -inf and count to 0 and total count to 0
    v = float("-inf")
    cnt = 0
    total_cnt = 0

    count += 1
    # for every successor
    for successor in node.successors:

        # get utility and count of successor by calling value function with MIN player
        util, cnt = value(successor,"MIN",count)

        # set v to max of v and current utility
        v = max(v,util)

        # increase total count by count
        total_cnt += cnt

        # set utility of successor to v
        successor.utility = v

    # return v and total count
    return v,total_cnt

def min_value(node : Node, count : int):
    # set v to inf and count to 0 and total count to 0
    v = float("inf")
    cnt = 0
    total_cnt = 0

    count += 1
    # for every successor
    for successor in node.successors:
        # increase count by 1

        # get utility and count of successor by calling value function with MAX player
        util, cnt = value(successor,"MAX",count)

        # set v to min of v and current utility
        v = min(v,util)

        # increase total count by count
        total_cnt += cnt

        # set utility of successor to v
        successor.utility = v
    
    # return v and total count
    return v,total_cnt

# alpha beta pruning function
def alpha_beta(node : Node, player_type : str):
    # set alpha to -inf and beta to inf and count to 0
    alpha = float("-inf")
    beta = float("inf")
    count = 0

    return value_alpha_beta(node,player_type,alpha,beta,count)

def value_alpha_beta(node : Node, player_type : str, alpha, beta, count : int):
    # if node is terminal node return utility and number of nodes
    if node.is_terminal_node():
        return node.utility,count

    # if MAX player's turn return max_alpha_beta
    # if MIN player's turn return min_alpha_beta
    if player_type == "MAX":
        return max_alpha_beta(node,alpha,beta,count)
    else:
        return min_alpha_beta(node,alpha,beta,count)



def max_alpha_beta(node : Node, alpha, beta, count : int):
    # set v to -inf and count to 0 and total count to 0
    v = float("-inf")
    cnt = 0
    total_cnt = 0

    count += 1
    # for every successor
    for successor in node.successors:

        # get utility and count of successor by calling value_alpha_beta function with MIN player
        util, cnt = value_alpha_beta(successor,"MIN",alpha,beta,count)

        # set v to max of v and current utility
        v = max(v,util)

        # increase total count by count
        total_cnt += cnt
        
        # if v >= beta return v and total count and set utility of successor to v
        if v >= beta:
            successor.utility = v
            return v,total_cnt
        
        # set alpha to max of alpha and v
        alpha = max(alpha,v)

        # set utility of successor to alpha
        successor.utility = alpha
    
    # return v and total count
    return v,total_cnt

def min_alpha_beta(node : Node, alpha, beta, count : int):
    
    # set v to inf and count to 0 and total count to 0
    v = float("inf")
    cnt = 0
    total_cnt = 0

    count += 1

    # for every successor
    for successor in node.successors:

        # get utility and count of successor by calling value_alpha_beta function with MAX player
        util, cnt = value_alpha_beta(successor,"MAX",alpha,beta,count)

        # set v to min of v and current utility
        v = min(v,util)

        # increase total count by count
        total_cnt += cnt

        # if v <= alpha return v and total count and set utility of successor to v
        if v <= alpha:
            successor.utility = v
            return v,total_cnt

        # set beta to min of beta and v
        beta = min(beta,v)

        # set utility of successor to beta
        successor.utility = beta
    
    # return v and total count
    return v,total_cnt

# function to print game tree
def print_tree(root : Node):
    print("ROOT")
    print(root.state, root.utility)
    print("SUCCESSORS")
    for successor in root.successors:
        print(successor.state,successor.utility, end= " ")
    print("\n")
    for successor in root.successors:
        print_tree(successor)


def SolveGame(method_name, problem_file_name, player_type):
    nimInput = None
    # read input file
    with open(problem_file_name) as inputFile:
        nimInput = inputFile.readline()
        nimInput = nimInput.strip('][').split(',')
        # convert to int
        for i in range(len(nimInput)):
            nimInput[i] = int(nimInput[i])

    # create game tree
    gameTree = GameTree(nimInput,player_type)
    gameTree.create_tree(gameTree.root,player_type)

    # print tree
    #print_tree(gameTree.root)
    


    if method_name == "Minimax":
        # find best move with minimax
        if player_type == 'MAX':
            # get max of all successors
            result = [(minimax(successor,"MIN"),successor.state) for successor in gameTree.root.successors]
            max_element = max(result, key= lambda x: x[0])
            ret_val = [tuple(max_element[1]),max_element[0][1]]
            return "(" + str(ret_val) + ")"
        else:
            # get min of all successors
            result = [(minimax(successor,"MAX"),successor.state) for successor in gameTree.root.successors]
            min_element = min(result, key= lambda x: x[0])
            ret_val = [tuple(min_element[1]),min_element[0][1]]
            return "(" + str(ret_val) + ")"
 
    elif method_name == "AlphaBeta":
        # find best move with alpha beta pruning
        if player_type == 'MAX':
            # get max of all successors
            result = [(alpha_beta(successor,"MIN"),successor.state) for successor in gameTree.root.successors]
            max_element = max(result, key= lambda x: x[0])
            ret_val = [tuple(max_element[1]),max_element[0][1]]
            return "(" + str(ret_val) + ")"
        else:
            # get min of all successors
            result = [(alpha_beta(successor,"MAX"),successor.state) for successor in gameTree.root.successors]
            min_element = min(result, key= lambda x: x[0])
            ret_val = [tuple(min_element[1]),min_element[0][1]]
            return "(" + str(ret_val) + ")"

