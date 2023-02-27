
# creates initial visited dictionary for every node
def create_visited_dict(graphKeys):
    visited = {}
    for key in graphKeys:
        visited[key] = False

    return visited

# creates a pair with cost value and coordinates of the node
def create_cost_and_coord_pair(cost,coordinate):
    return [cost,coordinate]

# checks whether or not the fringe contains given node
# returns index, if does not exist, returns -1
def fringe_contains(node,fringe):
    size = len(fringe)
    for i in range(size):
        if(fringe[i][1:] == node[1:]):
            return i
    return -1

# creates parent dictionary
def create_parent_dict(graphKeys):
    parents = {}
    for key in graphKeys:
        parents[key] = None
    return parents

def UCS(graph,start,end):
    # result list
    result = []

    # to create result path, save the parents of the nodes
    parents = create_parent_dict(graph.keys())

    ## create visited dict for every node
    visited = create_visited_dict(graph.keys())

    # priority queue
    fringe = []

    # start node with 0 cost
    # Format : startNode = [0,[x,y]]
    startNode = create_cost_and_coord_pair(0,start)

    # append start node
    fringe.append(startNode)

    while True:

        # if fringe is no solution
        if(len(fringe) == 0):
            return None

        # sort the fringe by cost values
        fringe.sort(key = lambda x: x[0])

        # pop maximum priority node
        currentNode = fringe[0]
        fringe.pop(0)

        # if goal state break and return path
        if(currentNode[1] == end):
            break

        # increase costs of nodes in the fringe
        for item in fringe:
            item[0] += 1


        # mark current node as visited
        visited[(currentNode[1][0],currentNode[1][1])] = True

        # adjacency list of current node
        children = graph[(currentNode[1][0],currentNode[1][1])]

        for child in children:

            # index of the item if it is in fringe, else -1
            fringe_index = fringe_contains(child,fringe)

            # boolean var indicates if the child node visited
            is_visited = visited[(child[0],child[1])]

            # calculate total cost
            totalCost = calculate_manhattan_dist(child,currentNode[1]) + currentNode[0]

            # if child node is not in fringe and not visited
            # mark its parent as current node
            # append it to the fringe
            if fringe_index == -1 and is_visited == False:
                childNode = create_cost_and_coord_pair(currentNode[0] + 1, child)
                parents[(child[0],child[1])] = currentNode[1]
                fringe.append(childNode)

            # if child node is in the fringe and the calculated cost less than the fringe version of it
            # change the cost of the child node
            # mark its parent as current node
            elif fringe_index != -1 and fringe[fringe_index][0] > totalCost:
                fringe[fringe_index][0] = totalCost
                parents[(child[0],child[1])] = currentNode[1]

    # iterate from end to start
    # create result path
    it = end
    while it != None:
        tupleIndex = (it[0],it[1])
        result.append(tupleIndex)
        it = parents[(it[0],it[1])]

    return result

    

def AStar(graph, heuristic_values,start,end):
    # result list
    result = []

    # to create result path, save the parents of the nodes
    parents = create_parent_dict(graph.keys())

    # create visited dict for every node
    visited = create_visited_dict(graph.keys())

    # priority queue
    fringe = []

    # start node with 0 cost
    startNode = create_cost_and_coord_pair(0,start)

    # push it to fringe
    fringe.append(startNode)

    while True:

        # if fringe is empty return no solution
        if(len(fringe) == 0):
            return None

        # sort fringe by cost values of nodes
        fringe.sort(key = lambda x: x[0])

        # pop max priority node from the fringe
        currentNode = fringe[0]
        fringe.pop(0)

        # if current node is end, break and return result
        if(currentNode[1] == end):
            break

        # mark the current node as visited
        visited[(currentNode[1][0],currentNode[1][1])] = True

        # adjacency list of the current node
        children = graph[(currentNode[1][0],currentNode[1][1])]

        for child in children:

            # index of the item if it is in fringe, else -1
            fringe_index = fringe_contains(child,fringe)

            # boolean var indicates if the child node visited
            is_visited = visited[(child[0],child[1])]

            # find heuristic value from grid
            value = heuristic_values[child[1]][child[0]]

            # if value is 'S' or 'E' make it 0 since these are start and end points
            # else take the value
            h = value if value != 'S' and value != 'E' else 0

            # calculate manhattan distance and add it with heuristic value
            # f = g + h
            totalCost = calculate_manhattan_dist(currentNode[1],child) + h       
            
            # if child node is not in fringe and not visited
            # mark its parent as current node
            # append it to the fringe
            if fringe_index == -1 and is_visited == False:
                childNode = create_cost_and_coord_pair(totalCost, child)
                parents[(child[0],child[1])] = currentNode[1]
                fringe.append(childNode)

            # if child node is in the fringe and the calculated cost less than the fringe version of it
            # change the cost of the child node
            # mark its parent as current node
            elif fringe_index != -1 and fringe[fringe_index][0] > totalCost:
                fringe[fringe_index][0] = totalCost
                parents[(child[0],child[1])] = currentNode[1]


    # iterate from end to start
    # create result path
    it = end
    while it != None:
        tupleIndex = (it[0],it[1])
        result.append(tupleIndex)
        it = parents[(it[0],it[1])]

    return result

# Finds start and end coordinates
def find_start_and_end_points(grid):
    start = None
    end = None
    size = len(grid)
    for i in range(size):
        for j in range(size):
            if(grid[i][j] == 'S'):
                start = [j,i]
            elif(grid[i][j] == 'E'):
                end = [j,i]
    return start,end

# calculates manhattan distance between two nodes
def calculate_manhattan_dist(current,next):
    return abs(current[0]-next[0]) + abs(current[1]-next[1])

# create graph with adjacency list representation
def create_graph(grid):
    graph = {}

    ### GRID IS A SQUARE MATRIX ###
    size = len(grid)

    # for each col
    for i in range(size):
        # for each row
        for j in range(size):
            if(grid[i][j] != '#'):
                graph[(j,i)] = []

    # row index is vertical
    # column index is horizontal

    for i in range(size):
        for j in range(size):
            currentPoint = grid[i][j]

            if currentPoint != '#':

                left = [j-1,i]

                right = [j+1,i]

                top = [j,i-1]

                bot = [j,i+1]

                if j - 1 >= 0:
                    if(grid[i][j-1] != '#'):
                        graph[(j,i)].append(left)

                if i - 1 >= 0:
                    if(grid[i-1][j] != '#'):
                        graph[(j,i)].append(top)

                if j + 1 < size:
                    if(grid[i][j+1] != '#'):
                        graph[(j,i)].append(right)


                if i + 1 < size:
                    if(grid[i+1][j] != '#'):
                        graph[(j,i)].append(bot)    

    return graph

# create heuristic grid
def create_heuristic_grid(grid):
    heuristic_grid = []

    for i in range(len(grid)):
        row = []
        for j in range(len(grid)):
            currentEntry = grid[i][j]
            if(currentEntry != 'E' and currentEntry != 'S' and currentEntry != '#'):
                row.append(int(currentEntry))
            else:
                row.append(currentEntry)
        heuristic_grid.append(row)
            
    return heuristic_grid



def InformedSearch(method_name, problem_file_name):

    Grid = []
    Graph = {}

    # read the file and parse it
    with open(problem_file_name) as inputFile:
        inp = inputFile.readlines()

        for line in inp:
            Grid += [line.split()]
    
    # Find start and end coordinates
    startPoint,endPoint = find_start_and_end_points(Grid)



    if(method_name == "UCS"):
        # create Graph for UCS
        Graph = create_graph(Grid)

        return UCS(Graph,startPoint,endPoint)

    elif(method_name == "AStar"):
        # create Graph for A*
        Graph = create_graph(Grid)

        # create Heuristic value Graph for A*
        heuristicValues = create_heuristic_grid(Grid)

        return AStar(Graph,heuristicValues,startPoint,endPoint)