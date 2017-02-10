
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
# start at position (i,j) and recursively fill adjencent cases (DFS: depth first search)
# if they respect the constraint defined by the function 'allow(i,j)'
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

# Indicate whether at least one item collide with the map with given 'size'
# 'items_pos' is the position of each item to test,
# 'collision(i, j)': it defines if collision occurs when an item is at index (i, j),
# 'items_shift': offset to apply to items_pos before testing,
# 'allow_out_of_bounds': can allow item index (i, j) to be either (i<0, i>=size[0], j<0, j>=size[1]).
# If an item is out side and it is allowed the method 'collision' will not be called.
def collide(size, items_pos, collision, items_shift=(0,0), allow_out_of_bounds=(False, False, False, False)):
    for pos in items_pos:
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
