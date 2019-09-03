## BACKTRACKING WITH FORWARDCHECKING AND HEURISTICS ##
#######################################################
## To run this program, make sure it is in the same folder as an input file and run the following command
## in the terminal:
## python sudoku3.py 2.sd, where 2.sd is the name of the input file (it can be anything else)
#######################################################



import sys
import copy

class Cell:
	value = 0
	domain = []
sudokuGrid = []
assignmentCount = 0
listOfDomains = []

## Populate the sudoku grid with the values seen from the input
def preprocessing():
	global sudokuGrid
	inFile = sys.argv[1]
	file = open(inFile, "r")
	for line in file:
		lineGrid = []
		cellRow = []
		lineGrid = line.split(" ")
		k = len(lineGrid)-1
		j = 0
		lineGrid.remove('\n')
		while j < k:
			## Create a cell structure which holds the value and the domain of the current cell
			newCell = Cell()
			lineGrid[j] = int(lineGrid[j])
			newCell.value = lineGrid[j]
			## If the cell is unassigned, its domain is all possible values
			if (lineGrid[j] == 0):
				newCell.domain = [1, 2, 3, 4, 5, 6, 7, 8, 9]
			else:
				## If the value is already assigned, its domain can only be that value
				newCell.domain = [newCell.value]
			cellRow.append(newCell)
			j+=1
		sudokuGrid.append(cellRow)
	del sudokuGrid[-1]

## This function takes the grid, and returns a list of domains that each unassigned cell has
## The list returned is sorted in increasing order by the length of the domains
def minimumRepValue(sudokuGrid):
	global listOfDomains
	listOfDomains = []
	for i in range (9):
		for j in range (9):
			if (sudokuGrid[i][j].value == 0):
				listOfDomains.append((sudokuGrid[i][j].domain, (i,j)))
	return sorted(listOfDomains, key=lambda x: len(x[0]))

## A function that returns the degree of the current cell by checking how many unassigned cells 
## There are in the neighbouring cells of the current one we're looking at
def getDegree(sudokuGrid, row, col):
	degree = 0
	nodeTrav = sudokuGrid[row][col]
	for k in range (9):
		if (k == col):
			continue
		if sudokuGrid[row][k].value == 0:
			degree += len(sudokuGrid[row][k].domain)
	for z in range (9):
		if (z == row):
			continue
		if sudokuGrid[z][col].value == 0:
			degree += len(sudokuGrid[z][col].domain)
	newX = row - (row % 3)
	newY = col - (col % 3)
	for i in range (3):
		for j in range(3):
			if (i + newX == row) and (j + newY == col):
				continue
			if (sudokuGrid[newX + i][newY +j].value == 0):
				degree += len(sudokuGrid[newX + i][newY + j].domain)
		
	return degree

## A function that removes the assignment value from all the neighbouring domains of the cell we're currently
## looking at
def removeDomainValues(row, col, sudokuGrid):
	## Removes the value from the domains in the same row
	for j in range (9):
		if (j == col):
			continue
		if (sudokuGrid[row][j].domain.count(sudokuGrid[row][col].value) > 0):
			sudokuGrid[row][j].domain.remove(sudokuGrid[row][col].value)
	## Removes the value from the domains in the same column		
	for i in range (9):
		if (i == row):
			continue
		if (sudokuGrid[i][col].domain.count(sudokuGrid[row][col].value) > 0):
			sudokuGrid[i][col].domain.remove(sudokuGrid[row][col].value)
	newRow = row - (row % 3)
	newCol = col - (col % 3)
	## Removes the value from the domains in the 3x3 sub-grid that this cell is in
	for k in range (3):
		for z in range (3):
			if ((k + newRow == row) and (z + newCol == col)):
				continue
			if (sudokuGrid[newRow+k][newCol+z].domain.count(sudokuGrid[row][col].value)>0):
				sudokuGrid[newRow+k][newCol+z].domain.remove(sudokuGrid[row][col].value)

## Check if there are any values in the specific row that has the same value
## if so, return false
def rowConstraint(row, assign, sudokuGrid):
	for i in range (9):
		if sudokuGrid[row][i].value == assign:
			return False
	return True

## Check if there are any values in the specific column that has the same value
## if so, return false
def colConstraint(col, assign, sudokuGrid):
	for i in range (9):
		if sudokuGrid[i][col].value == assign:
			return False
	return True

## Check if the value you assigned is present in the 3x3 subgrid that this cell
## is constrained by. If you find a value, return false as this assignment is incorrect
def boxConstraint(row, col, assign, sudokuGrid):
	i = 0
	while (i < 3):
		j = 0
		while (j < 3):
			if (sudokuGrid[row+i][col+j].value == assign):
				return False
			j+=1
		i+=1
	return True

## Check if there are any cells that contain the value 0, if that is the case
## then this sudoku has not been solved yet, otherwise it has and return true
def solved():
	i = 0
	while ( i < 9):
		j = 0
		while (j < 9):
			if (sudokuGrid[i][j].value == 0):
				return False
			j+=1
		i+=1
	return True

## This function checks what values in the domain of the cell we're trying to populate appears the least
## in all neighbouring cells and returns a sorted list in increasing order of the counter, which represents
## how many times this value in the domain was present in neighbouring cells, and what the value associated with
## that counter was
def LRV(node, row, col):
	sortDomain = []
	for i in node.domain:
		counter = 0
		for j in range (9):
			if (j == col):
				continue
			## check if the value is present in the row
			if (sudokuGrid[row][j].value == i):
				counter+=1
		for z in range (9):
			if (z == row):
				continue
			## check if the value is present in the column
			if (sudokuGrid[z][col].value == i):
				counter+=1
		newCol = col - (col % 3)
		newRow = row - (row % 3)
		for a in range (3):
			for b in range (3):
				if ((a + newRow == row) and (b + newCol == col)):
					continue
				## check if the value is present in the 3x3 sub-grid
				if (sudokuGrid[a+newRow][b+newCol].value == i):
					counter += 1
		## append the pair (counter, i) which represents how many times this value was present and what the value
		## we were looking at was
		sortDomain.append((counter, i))
	## sort the list in increasing order by the counter	
	sortDomain = sorted(sortDomain, key=lambda x: x[0])
	newList = []
	## return a sorted domain that represents the least constraining value to the most
	for i in sortDomain:
		newList.append(i[1])
	return newList



def solveGrid():
	global sudokuGrid
	global assignmentCount
	if (solved()):
		print(assignmentCount)
		return True
	## Get the MRV
	LOD = minimumRepValue(sudokuGrid)
	## Get the x and y coordinate of the first item in the MRV, which is the minimum restraining value
	minX = LOD[0][1][0]
	minY = LOD[0][1][1]
	## Create an array of these cells if there are more than 1 MRV, this is in the case for a tie
	minRepSquares = []
	minNode = sudokuGrid[minX][minY]
	for i in LOD:
		x2 = i[1][0]
		y2 = i[1][1]
		minRep = sudokuGrid[x2][y2]
		## if there is another cell that has the same MRV, add it to the array
		if ((len(minNode.domain)) == (len(minRep.domain))):
			minRepSquares.append(i)
	## if there is only 1 thing in the array, that means there was no tie so this is the cell you want to
	## look at
 	if len(minRepSquares) == 1:
 		findNode = minRepSquares[0]
 		findX = findNode[1][0]
 		findY = findNode[1][1]
 		traverseNode = sudokuGrid[findX][findY]
 	else:
 		## otherwise, we want to find the maximumDegree now
 		degreeNodes = []
		for nodes in minRepSquares:
			x = nodes[1][0]
			y = nodes[1][1]
			deg = getDegree(sudokuGrid, x, y)
			## created a list of (Degree, (x,y)) pairs
			degreeNodes.append((deg, (x, y)))
		## sort the list of Degrees
		degreeNodes = sorted(degreeNodes, key=lambda x: x[0])
		## Just take the first one if there is a tie or not, it doesn't matter in this case
		findNode = degreeNodes[0]
		findX = findNode[1][0]
		findY = findNode[1][1]
		traverseNode = sudokuGrid[findX][findY]
	## Get the LRV of the cell you want to look at
	sortedDomain = copy.copy(traverseNode.domain)
	sortedDomain = LRV(traverseNode, findX, findY)
	## Look at values in the sorted domain and pick. These values are now sorted by LRV so we're guaranteed to try
	## the LRV first
	for assign in (sortedDomain):
		if (rowConstraint(findX, assign, sudokuGrid) and (colConstraint(findY, assign, sudokuGrid)) and (boxConstraint(findX - (findX%3), findY - (findY%3), assign, sudokuGrid))):
			## Get a deep copy of the current grid in the case that the assignment is wrong and you need to
			## revert back to old domains
			tempSGrid = copy.deepcopy(sudokuGrid)
			sudokuGrid[findX][findY].value = assign
			removeDomainValues(findX, findY, sudokuGrid)
			assignmentCount+=1
			if (assignmentCount == 10000):
				print (assignmentCount)
				sys.exit()
			if (solveGrid()):
				return True
			## Was not the right assignment, so we set the sudokuGrid back to what it was before changing domains
			sudokuGrid = tempSGrid
			sudokuGrid[findX][findY].domain.remove(assign)
		## Set the cell back to unassigned
		sudokuGrid[findX][findY].value = 0
	return False



	
preprocessing()
solveGrid()