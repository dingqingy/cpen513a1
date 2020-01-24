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
            solution = self.traceBack(source, target)
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
        if x < x_bound-1:
            self.expand_((x + 1, y), new_score)
        if y > 0:
            self.expand_((x, y - 1), new_score)
        if y < y_bound-1:
            self.expand_((x, y + 1), new_score)

    # low level expand
    def expand_(self, coordinate, score):
        if self.label[coordinate] == 0:
            self.label[coordinate] = score
            self.expansion_list.put((score, coordinate))

    # This only goes forward, need to have a way to go back
    def traceBack(self, source, target):
        result = []
        x, y = current_loc = target
        x_bound, y_bound = self.grid_size
        current_score = self.label[target]
        print('starting location', current_loc)
        print('starting score', current_score)

        while True:
            # how to enforce order?
            # based on different algorithm, new score can be calculated differently
            x, y = current_loc
            if current_loc == source:
                break
            elif x > 0 and self.label[x - 1, y] == current_score - 1:
                result.append((x - 1, y))
                current_loc = (x - 1, y)
                current_score -= 1
            elif x<x_bound-1 and self.label[x + 1, y] == current_score - 1:
                result.append((x + 1, y))
                current_loc = (x + 1, y)
                current_score -= 1
            elif y>0 and self.label[x, y - 1] == current_score - 1:
                result.append((x, y - 1))
                current_loc = (x, y - 1)
                current_score -= 1
            elif y<y_bound-1 and self.label[x, y + 1] == current_score - 1:
                result.append((x, y + 1))
                current_loc = (x, y + 1)
                current_score -= 1
            else:
                print('no way to trace back, something is wrong!')
                print('current result', result)
                assert False

            print('location updated to', current_loc)
            print('score updated to', current_score)
            # print(self.label[x, y - 1])
        return result


if __name__ == '__main__':
    router = Router('benchmarks/example.infile')
    router.shortestPath((10, 1), (2, 7))