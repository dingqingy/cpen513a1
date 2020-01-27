from utils import *
from plot import *
import numpy as np
from queue import PriorityQueue as PQ
import argparse


class Router:
    def __init__(self, infile):
        self.grid_size, self.obstacles, self.wires = parse_input(infile)
        self.routed_path = [[] for _ in range(len(self.wires))]
        # print('init routed path', self.routed_path)
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
        self.step_single = ttk.Button(self.frame, text="Single Step", command=self.visualSingleStep)
        self.step_single.pack()
        self.step_wire = ttk.Button(self.frame, text="Connect a Wire", command=self.visualSingleWire)
        self.step_wire.pack()

        # display final result
        self.step_all = ttk.Button(self.frame, text="Show Final Result", command=self.visualFinalSolution)
        self.step_all.pack()

        # reset 
        self.step_all = ttk.Button(self.frame, text="Reset", command=self.resetVisual)
        self.step_all.pack()
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
                    if (i, j) in self.routed_path[k]:
                        self.canvas.create_rectangle(sizex * i, sizey * j, sizex * (i + 1), sizey * (j + 1), fill=COLORS[k + 1])
                    if (i, j) in wire:
                        self.canvas.create_rectangle(sizex * i, sizey * j, sizex * (i + 1), sizey * (j + 1), fill=COLORS[k + 1])
                        self.canvas.create_text(sizex * (i + 0.5), sizey * (j + 0.5), text=k + 1)

    # have a global display state
    # detailed implementation later, start from final solution
    def visualSingleStep(self):
        print('single step a routing progress')

    def visualSingleWire(self):
        print('visualize single wire connection')

    def visualFinalSolution(self):
        self.routeAll()
        self.plot()
        print('visualize final solution')

    def resetVisual(self):
        # call reset method that clears all internal states
        self.reset()
        self.plot()
        print('reset')

    def reset(self):
        self.routed_path = [[] for _ in range(len(self.wires))]
        self.plot()
    
    def routeAll(self):
        for i in range(len(self.wires)):
            self.routed_path[i] = self.routeOneNet(self.wires[i])
        # TODO: show a final message on solved wires, pins etc

    # router
    def routeOneNet(self, wire):
        num_pins = len(wire)
        # TODO: init best result here
        for i in range(num_pins):
            routed = [wire[i]]
            targets = wire[:i] + wire[(i + 1):]
            print('start with {} source pin'.format(i))
            print('the whole wire', wire)
            print('current routed', routed)
            print('current targets', targets)
            while targets:
                result = self.shortestPath(routed, targets)
                if result is not None:
                    # update routed
                    for coordinate in result:
                        if not coordinate in routed:
                            routed.append(coordinate)
                    print('updated route:', routed)
                    # update target
                    for target in targets:
                        if target in result:
                            targets.remove(target)
                    print('updated target:', targets)
                else:
                    # routing for this net failed
                    # record how many pins we connect
                    # TODO: drop the current starting pin, attemps to route as many pins as possible when routing failed
                    pass

            # successfully route all pins when starting with a pin, also try start with another pin
            print('full route:', routed)
            return routed  # this only returns a valid solution, possibly not the best
        # fail to route this wire, provide the best routed result that connects most of the pins
        # return best result

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
                print('target at {} found!'.format(coordinate))
                print('label map')
                print(self.label.T)
                solution = self.backTrack(coordinate, sources)
                print('routing solution: {}'.format(solution))
                return solution
            # expand all neighbours
            self.expand(coordinate)
        print('Expansion list elements are drained. Not routable!')
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
    parser.add_argument('--infile', '-i', default='benchmarks/example.infile', help='input file') # yaml
    args = parser.parse_args()

    router = Router(args.infile)
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
