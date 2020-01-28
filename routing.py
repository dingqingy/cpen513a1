from utils import *
# from plot import *
import numpy as np
from queue import PriorityQueue as PQ
import copy
import argparse
from tkinter import *
from tkinter import ttk
COLORS = ['black', 'red', 'yellow', 'azure4', 'orange', 'maroon', 'pink', 'lime green', 'dark violet', 'green']


class Router:
    def __init__(self, infile, verbose=False):
        self.verbose = verbose
        self.grid_size, self.obstacles, self.wires = parse_input(infile)
        self.total_possible_segments = 0
        for wire in self.wires:
            self.total_possible_segments += len(wire) - 1
        # print('Total possible segments:', self.total_possible_segments)
        self.resetAll()
        self.startGUI()
        self.plot()

    # GUI
    def startGUI(self, width=1000, height=500, background_color='white'):
        '''
        set up GUI
        '''
        self.root = Tk()
        self.frame = ttk.Frame(self.root, width=width, height=height)
        self.frame.pack()
        self.canvas = Canvas(self.frame, bg=background_color, width=width, height=height)
        self.canvas.pack()
        # self.step_single = ttk.Button(self.frame, text="Single Step", command=self.visualSingleStep)
        # self.step_single.pack()
        # self.step_wire = ttk.Button(self.frame, text="Connect a Wire", command=self.visualSingleWire)
        # self.step_wire.pack()

        # display final result
        self.step_all = ttk.Button(self.frame, text="Show Final Result", command=self.visualFinalSolution)
        self.step_all.pack()

        # reset button
        self.reset_button = ttk.Button(self.frame, text="Reset", command=self.resetVisual)
        self.reset_button.pack()

        # debug
        # self.debug_button = ttk.Button(self.frame, text="Debug Plot", command=self.plot)
        # self.debug_button.pack()
        # self.root.mainloop()

    # modify for generic plotting function
    def plot(self, width=1000, height=500):
        x_bound, y_bound = self.grid_size
        sizex = width / x_bound
        sizey = height / y_bound

        for i in range(x_bound):
            for j in range(y_bound):
                # draw obstacles
                if (i, j) in self.obstacles:
                    self.canvas.create_rectangle(sizex * i, sizey * j, sizex * (i + 1), sizey * (j + 1), fill='blue')
                else:
                    self.canvas.create_rectangle(sizex * i, sizey * j, sizex * (i + 1), sizey * (j + 1), fill='white')
                # draw wires
                for k, wire in enumerate(self.wires):
                    if (i, j) in self.best_routed_path[k]:
                        self.canvas.create_rectangle(sizex * i, sizey * j, sizex * (i + 1), sizey * (j + 1), fill=COLORS[k + 1])
                    if (i, j) in wire:
                        self.canvas.create_rectangle(sizex * i, sizey * j, sizex * (i + 1), sizey * (j + 1), fill=COLORS[k + 1])
                        self.canvas.create_text(sizex * (i + 0.5), sizey * (j + 0.5), text=k + 1)

    # have a global display state
    # detailed implementation later, start from final solution
    # def visualSingleStep(self):
    #     print('single step a routing progress')

    # def visualSingleWire(self):
    #     print('visualize single wire connection')

    def visualFinalSolution(self):
        ''' Display the final routing solution in the GUI'''
        self.routeAll()
        self.plot()
        print('visualize final solution')

    def resetVisual(self):
        ''' Reset the GUI to initial state'''
        self.resetAll()
        self.plot()
        print('reset')

    def resetAll(self):
        ''' Reset all members'''
        self.resetInternalState()
        # reset global state
        self.best_routed_path = [[] for _ in range(len(self.wires))]
        self.best_total_segments = 0

    def resetInternalState(self):
        ''' Reset members for the current state'''
        self.routed_path = [[] for _ in range(len(self.wires))]
        self.label = np.zeros(self.grid_size)
        self.expansion_list = PQ()
        self.net_ordering = PQ()

    # Router functionality
    def routeAll(self):
        self.best_total_segments = 0

        # # traverse nets in linear order
        # total_segments = self.linearOrder()
        # if total_segments > self.best_total_segments:
        #     self.best_total_segments = total_segments
        #     self.best_routed_path = copy.deepcopy(self.routed_path)

        # # solve simple nets (less pin and distance)
        # total_segments = self.solveSimpleFirst()
        # if total_segments > self.best_total_segments:
        #     self.best_total_segments = total_segments
        #     self.best_routed_path = copy.deepcopy(self.routed_path)

        # solve simple nets previously failed nets first
        self.solveSimpleFirstIterative()
        # maybe we will do

    def linearOrder(self):
        '''
        naive approach that attempts to connect wires/segments in input order
        '''
        self.resetInternalState()
        total_segments = 0
        for i in range(len(self.wires)):
            routed_segments, self.routed_path[i] = self.routeOneNet(self.wires[i])
            total_segments += routed_segments
        # TODO: show a final message on solved wires, pins etc
        if total_segments == self.total_possible_segments:
            if self.verbose:
                print('Linear Order Success, Route {} / {} segments'.format(total_segments, self.total_possible_segments))
        else:
            if self.verbose:
                print('Linear Order Failed, Route {} / {} segments'.format(total_segments, self.total_possible_segments))
        return total_segments

    def solveSimpleFirst(self):
        '''
        Heristic: connect simple wires first
        simple is defined based on L1 distance between all pins within a wire
        '''
        self.resetInternalState()
        total_segments = 0

        # detemine simple by evaluating total L1 distance
        for wire_id, wire in enumerate(self.wires):
            # self.net_ordering.put((totalL1Distance(wire), wire_id))
            self.net_ordering.put((totalL1Distance(wire), wire_id))

        while not self.net_ordering.empty():
            _, i = self.net_ordering.get()
            routed_segments, self.routed_path[i] = self.routeOneNet(self.wires[i])
            total_segments += routed_segments
        # TODO: show a final message on solved wires, pins etc
        if total_segments == self.total_possible_segments:
            if self.verbose:
                print('Simple First Success, Route {} / {} segments'.format(total_segments, self.total_possible_segments))
        else:
            if self.verbose:
                print('Simple First Failed, Route {} / {} segments'.format(total_segments, self.total_possible_segments))
        return total_segments

    def solveSimpleFirstIterative(self, iter=5):
        '''
        Heristic: connect simple & failed wires first
        simple is defined based on L1 distance between all pins within a wire
        At the same time, iteratively increase the prioiry of failed wires
        '''
        cost = np.zeros(len(self.wires))
        for i in range(iter):
            self.resetInternalState()
            total_segments = 0

            # detemine simple by evaluating total L1 distance
            for wire_id, wire in enumerate(self.wires):
                # self.net_ordering.put((totalL1Distance(wire), wire_id))
                self.net_ordering.put((averageL1Distance(wire) - cost[wire_id], wire_id))  # lower score, higher priority

            while not self.net_ordering.empty():
                _, wire_id = self.net_ordering.get()
                routed_segments, self.routed_path[wire_id] = self.routeOneNet(self.wires[wire_id])
                possible_segments = len(self.wires[wire_id]) - 1

                # if we are not able to route this wire, we increase the cost
                if routed_segments < possible_segments:
                    cost[wire_id] += 10

                total_segments += routed_segments
            # TODO: show a final message on solved wires, pins etc
            if total_segments == self.total_possible_segments:
                if self.verbose:
                    print('Iter {}, simple first success, route {} / {} segments'.format(i, total_segments, self.total_possible_segments))
            else:
                if self.verbose:
                    print('Iter {}, simple first fail, route {} / {} segments'.format(i, total_segments, self.total_possible_segments))
            if self.best_total_segments < total_segments:
                self.best_total_segments = total_segments
                self.best_routed_path = copy.deepcopy(self.routed_path)

    # greedy that tries to connect as many pins as possible
    def routeOneNet(self, wire):
        num_pins = len(wire)
        max_segments = 0
        best_routed = []
        # TODO: init best result here
        for i in range(num_pins):
            num_segments = 0
            routed = [wire[i]]  # this is the staring pin
            targets = wire[:i] + wire[(i + 1):]  # every other pin is the target
            # print('start with {} source pin'.format(i))
            # print('the whole wire', wire)
            # print('current routed', routed)
            # print('current targets', targets)
            while targets:
                result = self.shortestPath(routed, targets)
                if result is not None:
                    # update routed
                    for coordinate in result:
                        if not coordinate in routed:
                            routed.append(coordinate)
                    # print('updated route:', routed)
                    # remove found target
                    for target in targets:
                        if target in result:
                            targets.remove(target)
                    # print('updated target:', targets)
                    num_segments += 1
                else:
                    # print('we are not able to connect further, the current # of segments is', num_segments)
                    break

            if num_segments > max_segments:
                max_segments = num_segments
                best_routed = copy.deepcopy(routed)

        # print('best route:', best_routed)
        # print('max segments / potential segments: {} / {}'.format(max_segments, num_pins-1))
        return max_segments, best_routed
        # fail to route this wire, provide the best routed result that connects most of the pins
        # return best result

    # greedy that tries to maximize # wires get connected
    def routeClosest(self):
        pass

    def shortestPath(self, sources, targets):
        '''
        Perform Lee-Moore Shortest Path Algorithm
        sources are a list for source pin(s)
        targets are a list of target pin(s)
        '''
        self.label = np.zeros(self.grid_size)
        for obstacle in self.obstacles:
            self.label[obstacle] = np.Inf
        # FIXME: routed paths are obstacles too!
        for path in self.routed_path:
            for coordinate in path:
                self.label[coordinate] = np.Inf

        # unrouted pins are obstacles too
        for wire in self.wires:
            for pin in wire:
                if not pin in targets:
                    self.label[pin] = np.Inf
        self.expansion_list = PQ()

        # we can have multiple sources
        for source in sources:
            self.label[source] = 1
            self.expansion_list.put((1, source))
        while not self.expansion_list.empty():
            _, coordinate = self.expansion_list.get()
            if coordinate in targets:
                # print('target at {} found!'.format(coordinate))
                # print('label map')
                # print(self.label.T)
                solution = self.backTrack(coordinate, sources)
                # print('routing solution: {}'.format(solution))
                return solution
            # expand all neighbours
            self.expand(coordinate)
        # print('Expansion list elements are drained. Not routable!')
        return

    def expand(self, coordinate):
        '''
        Expand arond a grid coordinate
        '''
        x, y = coordinate
        x_bound, y_bound = self.grid_size
        current_score = self.label[coordinate]

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

    def expand_(self, coordinate, score):
        ''' Low level expand method '''
        if self.label[coordinate] == 0:
            self.label[coordinate] = score
            self.expansion_list.put((score, coordinate))

    def backTrack(self, start, ends):
        '''
        high level backTrack wrapper
        '''
        visited = np.zeros(self.grid_size, dtype=bool)
        result = []
        # print(visited.T)
        # print(start)
        # print(visited[start])
        if self.backTrack_(start, ends, visited, result):
            return result
        else:
            print('backtrack failed')
            assert False

    def backTrack_(self, start, ends, visited, result):
        ''' Recursive backtrack method '''
        if start in ends:
            # print('start hit an s position', start)
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

        # TODO: how to decide backtrack order?
        # prefer not change direction etc...?
        if x > 0:
            new_start = (x - 1, y)
            if self.label[new_start] < current_score and not visited[new_start]:
                if self.backTrack_(new_start, ends, visited, result):
                    result.append(start)
                    # print(result)
                    return True
        if y > 0:
            new_start = (x, y - 1)
            if self.label[new_start] < current_score and not visited[new_start]:
                if self.backTrack_(new_start, ends, visited, result):
                    result.append(start)
                    # print(result)
                    return True
        if x + 1 < x_bound:
            new_start = (x + 1, y)
            if self.label[new_start] < current_score and not visited[new_start]:
                if self.backTrack_(new_start, ends, visited, result):
                    result.append(start)
                    # print(result)
                    return True
        if y + 1 < y_bound:
            new_start = (x, y + 1)
            if self.label[new_start] < current_score and not visited[new_start]:
                if self.backTrack_(new_start, ends, visited, result):
                    result.append(start)
                    # print(result)
                    return True
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Timeloop')
    parser.add_argument('--infile', '-i', default='benchmarks/example.infile', help='input file')  # yaml
    args = parser.parse_args()

    router = Router(args.infile, verbose=True)

    # test Lee Moore on single source and target
    # router.shortestPath([(10, 1)], [(2, 7)])
    # test Lee Moore on single source and multiple target
    # router.shortestPath([(8, 3)], [(7, 7), (10, 7)])
    # test Lee Moore on multiple source and single target
    # router.shortestPath([(8, 3), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7)], [(10, 7)])
    # test visualization
    # router.start_gui()
    # router.plot_init()
    # for i in range(len(router.wires)):
    #     print('test net', i)
    #     router.routeOneNet(router.wires[i])
    #     print('')
    router.root.mainloop()
