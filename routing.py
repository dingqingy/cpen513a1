from utils import *
from plot import *
import numpy as np
from queue import PriorityQueue as PQ


class Router:
    def __init__(self, infile):
        self.grid_size, self.obstacles, self.wires = parse_input(infile)

    # Fixme: source and target should be from wires, instead of input
    def shortestPath(self, source, target):
        self.label = np.zeros(self.grid_size)
        for obstacle in self.obstacles:
            self.label[obstacle] = np.Inf
        self.expansion_list = PQ()

        # we can have multiple sources
        self.label[source] = 1
        self.expansion_list.put((1, source))
        is_target_found = False
        while not self.expansion_list.empty():
            _, coordinate = self.expansion_list.get()
            if coordinate == target:
                print('target at {} found!'.format(coordinate))
                is_target_found = True
                break
            # expand all neighbours
            self.expand(coordinate)

        if(is_target_found):
            print('label map')
            print(self.label.T)
            solution = self.backTrack(target, source)
            print('routing solution: {}'.format(solution))
        else:
            print('not routable')

    def expand(self, source):
        # print('expand', source)
        x, y = source
        x_bound, y_bound = self.grid_size
        current_score = self.label[source]

        # based on different algorithm, new score can be calculated differently
        new_score = current_score + 1

        # make sure we don't go out of bounds
        if x > 0:
            self.expand_((x - 1, y), new_score)
        if x < x_bound - 1:
            self.expand_((x + 1, y), new_score)
        if y > 0:
            self.expand_((x, y - 1), new_score)
        if y < y_bound - 1:
            self.expand_((x, y + 1), new_score)

    # low level expand
    def expand_(self, coordinate, score):
        if self.label[coordinate] == 0:
            self.label[coordinate] = score
            self.expansion_list.put((score, coordinate))

    # This only goes forward, need to have a way to go back
    def backTrack(self, start, end):
        visited = np.zeros(self.grid_size, dtype=bool)
        result = []
        # print(visited.T)
        # print(start)
        # print(visited[start])
        if self.backTrack_(start, end, visited, result):
            return result
        else:
            print('backtrack failed')
            assert False

    def backTrack_(self, start, end, visited, result):
        if(start == end):
            # print('start hit end')
            result.append(start)
            # print(result)
            return True
        # explore neighbours
        visited[start] = True
        x, y = start
        current_score = self.label[start]
        # print('current position', start)
        # print('current score', current_score)
        x_bound, y_bound = self.grid_size
        if x > 0:
            new_start = (x - 1, y)
            if self.label[new_start] < current_score and not visited[new_start]:
                if self.backTrack_(new_start, end, visited, result):
                    result.append(start)
                    # print(result)
                    return True
        if y > 0:
            new_start = (x, y - 1)
            if self.label[new_start] < current_score and not visited[new_start]:
                if self.backTrack_(new_start, end, visited, result):
                    result.append(start)
                    # print(result)
                    return True
        if x + 1 < x_bound:
            new_start = (x + 1, y)
            if self.label[new_start] < current_score and not visited[new_start]:
                if self.backTrack_(new_start, end, visited, result):
                    result.append(start)
                    # print(result)
                    return True
        if y + 1 < y_bound:
            new_start = (x, y + 1)
            if self.label[new_start] < current_score and not visited[new_start]:
                if self.backTrack_(new_start, end, visited, result):
                    result.append(start)
                    # print(result)
                    return True
        return False


if __name__ == '__main__':
    router = Router('benchmarks/example.infile')
    router.shortestPath((10, 1), (2, 7))
