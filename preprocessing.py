import os
import json
import numpy as np

BORDER_VALUE = 0
TRAINING_DATA_FOLDER_NAME = 'arcdata/evaluation';
fileNames = os.listdir(TRAINING_DATA_FOLDER_NAME);
fileNames = list(filter(lambda x: 'label' not in x, fileNames))

class Pixel:
    def getX(self):
        return self.coord[0]
    def getY(self):
        return self.coord[1]
    def __init__(self, color, coord):
        self.color = color
        self.coord = coord
        
class Grid:
    def getPixels(self):
        return self.pixels
    def __init__(self, raw_grid, pixels=[]):
        self.raw = raw_grid
        self.shape = raw_grid.shape
        self.sum = np.sum(raw_grid)
        self.size = len(np.nonzero(raw_grid!=0))
        if(pixels):
            self.pixels = pixels
        else:
            self.pixels = [Pixel(color, [i[0], i[1]]) for i, color in np.ndenumerate(raw_grid)]
        self.colors = np.unique(raw_grid)
        self.objects = find_objects(pp.add_border(raw_grid), np.asarray(raw_grid).size)

def evaluate_effectiveness_of_function(function):
    """
    The idea of this function is that a newly created library function can be tested directly on the evaluation data 
    (how many problems could be solved right away with this functionality).
    """
    solved_files = []
    for fileName in fileNames:
        with open(f'{TRAINING_DATA_FOLDER_NAME}/{fileName}', 'r') as file:
            data = json.loads(file.read())
            result = []
            #print(data)
            for i in data['train']:
                #print(i)
                result.append(np.array_equal(function(i['input']), np.array(i['output'])))
            if np.all(result):
                solved_files.append(fileName)
    return solved_files



def add_border(matrix):
    ''''Outline a grid so out of bounds exceptions can be minimized (nxm => n+2xm+2)'''
    return np.pad(matrix, 1, mode='constant', constant_values=BORDER_VALUE)

def matrix_per_color(matrix):
    """
    Extract all equal color pixels from a matrix and return one matrix per color
    :param matrix:
    :return: result_matrices
    """
    matrix = np.asarray(matrix).flatten()
    result_matrices = []
    for i in range(1, 9):
        matrix_copy = np.copy(matrix == i)
        matrix_result = np.zeros(matrix_copy.shape)
        if np.sum(matrix_copy == True) > 0:
            for j in range(matrix_copy.size):
                if matrix_copy[j]:
                    matrix_result[j] = i
            result_matrices.append(matrix_result)
    return result_matrices

def get_pixel_neighbours_recursive(matrix, pixel, seen_pos):
    if matrix[pixel[0], pixel[1]] == 0:
        return
    seen_pos.append(Pixel(matrix[pixel[0], pixel[1]], [pixel[0], pixel[1]]))
    for i in range(3):
        for j in range(3):
            d = Pixel(matrix[pixel[0]-1+i, pixel[1]-1+j], [pixel[0]-1+i, pixel[1]-1+j])
            if (all(obj.coord != d.coord for obj in seen_pos)) and d.color != 0:
                get_pixel_neighbours_recursive(matrix, d.coord, seen_pos)
    return seen_pos

#1. Suche erste Zahl, welche nicht 0 oder 10 ist
#2. Get Neighbours rekursiv bis alle neighbours schon im objekt oder 0 oder 10 sind
#3. suche nächste Zahl, welche in keinem objekt vorkommt und nicht 0 ist
def find_objects(matrix, size):
    #print(matrix)
    cluster = []
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            if matrix[i][j] == 0 or (cluster and any([i,j] == obj.coord for obj in np.concatenate(np.asarray(list(map(Grid.getPixels, cluster)), dtype=object)).ravel())):
                continue
            d = get_pixel_neighbours_recursive(matrix, [i, j], [])
            if math.ceil(np.asarray(d).size / 2) * 2 == size:
                return
            raw_child = normalize(d)
            cluster.append(Grid(raw_child, d))
    return cluster

def normalize(pixels):
    x = max(list(map(Pixel.getX, pixels))) - min(list(map(Pixel.getX, pixels)))
    y = max(list(map(Pixel.getY, pixels))) - min(list(map(Pixel.getY, pixels)))
    raw = np.zeros((x + 1,y + 1))
    
    for p in pixels:
        raw[(p.getX() - min(list(map(Pixel.getX, pixels))), p.getY() - min(list(map(Pixel.getY, pixels))))] = p.color
    return raw


"""
In dieser funktion wird preprocessing für alle matrizen durchgeführt.
Return value ist eine 2D array von input output Grid Objects
[[Grid_Input_1, Grid_Output_1],
 [Grid_Input_2, Grid_Output_2],
  [Grid_Input_3, Grid_Output_3]]
"""
def preprocess(matrices):
    return