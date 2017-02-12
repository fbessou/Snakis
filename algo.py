import numpy as np

# Give the strongly connected components in a matrix with given 'size'
# the function 'grp(i, j)' must return the group value at index (i, j)
# -> adjacent tiles with same group value are in the same component
# -> group 0 is ignored
# Return tuple (
#   array of component descriptor: {"index":(x,y), "size":size, "grp":grp(x,y)},
#   full matrix of component ownership
# )
def connectedComponent(size, grp):
    count = 0
    comp = []
    group = np.zeros(size, dtype='int')
    for x in range(size[0]):
        for y in range(size[1]):
            if groupe[x][y] == 0:
                g = grp(x, y)
                if g != 0:
                    count += 1
                    fill = dfsFill(group, count, lambda i,j:grp(i, j)==g)
                    comp.append({"index":(x,y), "size":fill, "grp":g})

    return (comp, group)

# Fill a matrix with the given 'value',
# start at position (i,j) and recursively fill adjencent square (DFS: depth first search)
# if they respect the constraint defined by the function 'allow(i,j)'
# Return the number the number of filled squares
def dfsFill(matrix, i, j, value, allow):
    count = 0

    if 0 <= i < matrix.size()[0] and 0 <= j < matrix.size()[1]:
        if matrix[i][j] != value and allow(i,j):
            matrix[i][j] = value
            count += 1

            count += dfsFill(matrix, i+1, j+0, value, allow)
            count += dfsFill(matrix, i-1, j+0, value, allow)
            count += dfsFill(matrix, i+0, j+1, value, allow)
            count += dfsFill(matrix, i+0, j-1, value, allow)
    
    return count

# Indicate whether at least one item collide with the map with given 'size'.
# 'blocks' is the position of each item to test,
# 'collision(i, j)': it defines if collision occurs when an item is at index (i, j),
# 'items_shift': offset to apply to blocks before testing,
# 'allow_out_of_bounds': can allow item index (i, j) to be either (i<0, i>=size[0], j<0, j>=size[1]).
# If an item is out side and it is allowed the method 'collision' will not be called.
def collide(size, blocks, collision, items_shift=(0,0), allow_out_of_bounds=(False, False, False, False)):
    for pos in blocks:
        i = pos[0]+items_shift[0]
        j = pos[1]+items_shift[1]
        if i < 0:
            if not allow_out_of_bounds[0]:
                return True
            continue
        if i >= size[0]:
            if not allow_out_of_bounds[1]:
                return True
            continue
        if j < 0:
            if not allow_out_of_bounds[2]:
                return True
            continue
        if j >= size[1]:
            if not allow_out_of_bounds[3]:
                return True
            continue
        if collision(i, j):
            return True

    return False


# Build items fall dependencies.
# items: for each item, an array of position of blocks
# fallingDirection: direction in which the items will fall, norm should be 1
# Return the matrix of boolean: isAboveMatrix[i][j] means that item i is just above item j
def fallingDependencies(items, fallingDirection = (0, -1)):
    isAboveMatrix = np.zeros(len(items), len(items), dtype=bool)
    for i in range(len(items)):
        for j in range(len(items)):
            for ip in items[i]:
                for jp in items[j]:
                    # i is above j
                    if (ip[0]+fallingDirection[0], ip[1]+fallingDirection[1]) == jp:
                        isAboveMatrix[i][j] = True
                    # j is above i
                    if (jp[0]+fallingDirection[0], jp[1]+fallingDirection[1]) == ip:
                        isAboveMatrix[j][i] = True
    return isAboveMatrix

# Indicate which items can fall using collision detection and item relative position.
# items: for each item, an array of position of blocks
# fallingDirection: direction in which the items will fall, norm should be 1
# size: playground size
# collision(i, j): it defines if collision occurs when an item is at index (i, j),
# allow_out_of_bounds: can allow item index (i, j) to be either (i<0, i>=size[0], j<0, j>=size[1]).
# Return an array of boolean that indicates for each item if it can fall
def canFall(items, fallDirection, size, collision, allow_out_of_bounds=(False, False, False, False)):
    isLocked = [False] * len(items)
    # check for each item individually if it can fall or it is locked
    for i in range(len(items)):
        if collide(size, items[i], collision, fallDirection, allow_out_of_bounds):
            isLocked[i] = True
    
    isAboveMatrix = fallingDependencies(items, fallingDirection)
    
    # spread the lockness using 'isAboveMatrix'
    def spread(item_index):
        for i in range(len(items)):
            if isAboveMatrix[i][item_index] and not isLocked[i]:
                isLocked[i] = True
                spread(i)

    for i in range(len(items)):
        if isLocked[i]:
            spread(i)

    return [not b for b in isLocked]


# Move all items in the given direction if they can.
# items: for each item, an array of position of blocks
# canFall: array of boolean to allow or not each item to fall
# fallDirection: direction in which the items fall
def fall(items, canFall, fallDirection=(0,-1)):
    for i in range(len(items)):
        if canFall[i]:
            items[i][0] += fallDirection[0]
            items[i][1] += fallDirection[1]

# Clear playground tiles that belong to the given connected component, also remove extra adjacent tiles.
# component: the ID if the connected component to clear
# playgroundSize: the size of the playground
# clearPlayground(i,j): the function that will perform the removal at index (i,j)
# componentOwnershipMatrix: result of connectedComponent
# extraRemoval: additional tiles to remove, given relatively to a component's tile
def removeConnectedComponent(component, playgroundSize, clearPlayground, componentOwnershipMatrix, extraRemoval=[(1,0), (-1,0), (0,1), (0,-1)]):
    for i in range(size[0]):
        for j in range(size[1]):
            if componentOwnershipMatrix[i][j] == component:
                clearPlayground(i,j)
                for e in extraRemoval:
                    ei, ej = i + e[0], j + e[1]
                    if 0 <= ei < size[0] and 0 <= ej < size[1] and componentOwnershipMatrix(ei, ej) != component:
                        clearPlayground(ei, ej)
