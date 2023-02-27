class Graph():
    def __init__(self,graphGrid,rows,cols):
        # Grid with adjacency list, stored in dictionary
        self.Grid = {}

        # key : name of the node
        # val 1 : row number
        # val 2 : column number
        self.importantPoints = []

        # Since the customers represented as "C" in the file, change their names as X1,X2 etc.
        # To change their names, store a counter variable
        self.__customerCounter = 1

        # Traverse the matrix representation of the graph.
        # And find the location of start,finish and customers
        
        for i in range(rows):
            for j in range(cols):
                if graphGrid[i][j] == "S":
                    self.importantPoints.append(["S",i,j])
                elif graphGrid[i][j] == "C":
                    self.importantPoints.append([("X"+str(self.__customerCounter)),i,j])
                    self.__customerCounter += 1
                elif graphGrid[i][j] == "F":
                    self.importantPoints.append(["F",i,j])
        

        
        # Create adjacency list representation of the grid
        for i in range(len(self.importantPoints)):
            currentPoint = self.importantPoints[i]

            # if current point is F do not create a adj list since F is final destination
            if(currentPoint[0] == "F"):
                continue

            self.Grid[currentPoint[0]] = []
            
            for j in range(len(self.importantPoints)):
                # do not add the node itself to adjacency list
                if(i == j):
                    continue
                
                currentAdjacentPoint = self.importantPoints[j]
                
                # do not add the final node to adj list since the result always ended up with it
                if(currentAdjacentPoint[0] == "F"):
                    continue

                # currentPoint name is the key, adj points name and coordinates are values
                self.Grid[currentPoint[0]].append([currentAdjacentPoint[0],currentAdjacentPoint[1],currentAdjacentPoint[2]])
                
            
        







def BFS(grid, visited, minCustomerNum):
    
    # result list
    result = []

    # keep track of the remaining customers
    remainingCustomers = minCustomerNum

    # this fringe is a FIFO due to BFS
    fringe = []

    # find start coordinates
    startCoord = findCoordinate(grid.importantPoints,"S")

    # firstly append start node to the fringe
    fringe.append(["S"]+startCoord)

    # mark it as visited
    visited["S"] = True

    # append start coordinates to the result
    result.append(startCoord)
    
    
    # if fringe is empty or there is no remaining customers stop
    while True:
        if(len(fringe) == 0):
            return None
        if(remainingCustomers == 0):
            break
        # pop first item
        poppedItem = fringe[0]
        fringe.pop(0)


        adjList = grid.Grid[poppedItem[0]]

        # for every adjacent node of the current node, iterate and mark them visited if it's not visited
        for point in adjList:
            if(visited[point[0]] == False):
                
                fringe.append(point)
                visited[point[0]] = True
                result.append(point[1:])

                remainingCustomers -= 1

                # if there is no remaining customers break the loop
                if(remainingCustomers == 0):
                    break

    # find coordinates of final destination and append to the end of the list
    finalCoord = findCoordinate(grid.importantPoints,"F")
    result.append(finalCoord)

    if(remainingCustomers > 0):
        return None

    return result

def DFS(grid, visited, minCustomerNum):
    # result list
    result = []

    # keep track of the remaining customers
    remainingCustomers = minCustomerNum

    # this fringe is a LIFO
    fringe = []

    # find start coordinates
    startCoord = findCoordinate(grid.importantPoints,"S")

    # firstly append start node to the fringe
    fringe.append(["S"]+startCoord)

    # mark it as visited
    visited["S"] = True

    # append start node to the result array
    result.append(startCoord)

    while True:
        # if fringe is empty, failure
        if(len(fringe) == 0):
            return None
        if(remainingCustomers == 0):
            break

        # pop the top of the stack
        poppedItem = fringe[-1]
        fringe.pop(-1)

        # if not visited, append to the list and mark it as visited
        if(visited[poppedItem[0]] == False):
            remainingCustomers -= 1

            visited[poppedItem[0]] = True
            result.append(poppedItem[1:])
            

            if(remainingCustomers == 0):
                break

        adjList = grid.Grid[poppedItem[0]]

        # traverse through the children of the current node and push item
        for node in adjList:
            if(visited[node[0]] == False):
                fringe.append(node)

    # find coordinates of final destination and append to the end of the list
    finalCoord = findCoordinate(grid.importantPoints,"F")
    result.append(finalCoord)

    if(remainingCustomers > 0):
        return None
    return result



def UCS(grid, visited, minCustomerNum):

    # result path
    result = []

    remaining = minCustomerNum

    allNodes = grid.importantPoints

    # in order to track remaining customers, we need to see Final node in the fringe
    # In BFS and DFS I did not need F node in the adjacency list
    for node in allNodes:
        f = findCoordinate(allNodes,"F")
        if(node[0] != "F"):
            grid.Grid[node[0]].append(["F",f[0],f[1]])

    # to find all paths
    path = {}

    # priority queue
    fringe = []

    # preprocess for path dictionary
    for node in allNodes:
        name = node[0]
        path[name] = []


    # push start node
    fringe.append([0,"S"])
    currentCost = 0


    while True:
        # if priority queue is empty break
        if(len(fringe) == 0):
            break

        # sort the fringe by cost
        fringe.sort()

        # current least cost node
        currentNode = fringe[0]
        currentNodeName = currentNode[1]
        currentPoint = findCoordinate(allNodes,currentNodeName)
        currentCost = currentNode[0]

        # pop the least cost node
        fringe.pop(0)

        # increase the all costs by current cost
        for item in fringe:
            item[0] += currentCost

        # this part is crucial for path
        # maybe a node was visited before but not in the path of Final node
        # therefore, we may need to revisit it, so mark it as unvisited
        for n in allNodes:
                if n[0] not in path["F"]:
                    visited[n[0]] = False
        
        
        # if remaining == 0 program exitst from the loop below (children loop)
        # however, remaining become -1
        # in order to stop check the -1 condition
        if(remaining == -1):
            break
        # F does not have adjacency list, therefore continue
        elif(currentNodeName == "F"):
            continue
        
        # mark the current node as visited
        visited[currentNodeName] = True

        children = grid.Grid[currentNodeName]

        # check all child nodes in the adjacency list of current node
        for child in children:
            # find child point's coordinate
            childPoint = findCoordinate(allNodes,child[0])
            
            # find the manhattan distance between current and child point
            dist = calculateManhattanDist(childPoint,currentPoint)

            # calculate total cost
            totalCost = dist + currentCost

            # check whether or not the child node is in the fringe
            contains = checkFringe(child[0],fringe)

            # if child node is not visited and is not in fringe
            # append it to the fringe
            # if child node is Final node, decrease remaining nodes since we must visit a node now
            if(visited[child[0]] == False and contains == -1):
                fringe.append([totalCost,child[0]])
                path[child[0]] += [currentNodeName]
                if(child[0] == "F"):
                    remaining -=1
                if(child[0] == "F" and remaining == 0):
                    break
            
            # if child node is in the fringe and new cost is lest than the old cost
            # change the cost of the child node in the fringe
            # if child node is Final node, decrease remaining nodes since we must visit a node now
            elif(contains != -1 and fringe[contains][0] > totalCost):
                fringe[contains][0] = totalCost
                path[child[0]] +=  [currentNodeName]
                if(child[0] == "F"):
                    remaining -=1
                if(child[0] == "F" and remaining == 0):
                    break
   
   # now we have all nodes that in the path of Final node
   # find their coordinate and create the result array
    for name in path["F"]:
        result.append(findCoordinate(allNodes,name))

    # finally append the final nodes coordinates
    result.append(findCoordinate(allNodes,"F"))

    if minCustomerNum > len(result) - 2:
        return None
    return result
    
# checks whether or not the given name in the fringe
# returns the index if it is present, else returns -1
def checkFringe(name,fringe):
    for i in range(len(fringe)):
        if name == fringe[i][1]:
            return i
    return -1

# calculates manhattan distance between two nodes
def calculateManhattanDist(current,next):
    return abs(current[0]-next[0]) + abs(current[1]-next[1])



def UnInformedSearch(method_name , problem_file_name):
    minCustomerNumber = 0
    matrixRepOfGrid = []

    # Open the problem file and read 
    with open(problem_file_name) as inputFile:
        inp = eval(inputFile.readline())
        minCustomerNumber = inp["min"]
        gridInStringFormat = inp["env"]

        matrixRepOfGrid = parseGridFromStr(gridInStringFormat)
        
        
    rows = len(matrixRepOfGrid)
    cols = len(matrixRepOfGrid[0])

    GridEnvironment = Graph(matrixRepOfGrid,rows,cols)    


    lenOfPoints = len(GridEnvironment.importantPoints)
    
    if method_name == "BFS":
        
        visited = {}
        for i in range(lenOfPoints):
            visited[GridEnvironment.importantPoints[i][0]] = False
        return BFS(GridEnvironment,visited,minCustomerNumber)


    elif method_name == "DFS":

        visited = {}
        for i in range(lenOfPoints):
            visited[GridEnvironment.importantPoints[i][0]] = False
        return DFS(GridEnvironment,visited,minCustomerNumber)


    elif method_name == "UCS":
        visited = {}
        for i in range(lenOfPoints):
            visited[GridEnvironment.importantPoints[i][0]] = False
        return UCS(GridEnvironment,visited,minCustomerNumber)

    return None

# Finds min value 
def findMin(minStr):
    parsed = minStr.split(" ")

    minNumber = int(parsed[-1])

    return minNumber

# Parses Input string to construct a matrix for graph representation
def parseGridFromStr(gridList):
    grid = []
    for gridStr in gridList:
        currentRow = []
        for char in gridStr:
            if char == "." or char == "C" or char == "S" or char == "F":
                currentRow.append(char)
        grid.append(currentRow)

    return grid

# returns coordinate of the given node
def findCoordinate(pointList,name):
    for point in pointList:
        if(name == point[0]):
            return point[1:]
    return None


