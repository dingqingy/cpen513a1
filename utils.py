import argparse
from itertools import combinations

def parse_input(infile):
    with open(infile, 'r') as f:
        grid_size = tuple([int(x) for x in f.readline().rstrip('\n').split(' ')])

        num_obstacles = int(f.readline())
        obstacles = []
        for _ in range(num_obstacles):
            # read obstacles coordinates
            obstacles.append(tuple([int(x) for x in f.readline().rstrip('\n').split(' ')]))

        num_wires = int(f.readline())
        wires = []
        for _ in range(num_wires):
            # read source and sink coordinates
            wire = f.readline().rstrip('\n').split(' ')
            num_pins = int(wire[0])
            pins = []
            for i in range(num_pins):
                pin = int(wire[2 * i + 1]), int(wire[2 * i + 2])
                pins.append(pin)
            wires.append(pins)

    return grid_size, obstacles, wires

def totalL1Distance(pins):
    sum = 0
    for pin_a, pin_b in combinations(pins, 2):
        x_a, y_a = pin_a
        x_b, y_b = pin_b
        sum += abs(x_a - x_b) + abs(y_a - y_b)
    return sum

def averageL1Distance(pins):
    sum = 0
    count = 0
    for pin_a, pin_b in combinations(pins, 2):
        x_a, y_a = pin_a
        x_b, y_b = pin_b
        count += 1
        sum += abs(x_a - x_b) + abs(y_a - y_b)
    return sum/count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Timeloop')
    parser.add_argument('--infile', '-i', default='benchmarks/example.infile', help='input file') # yaml
    args = parser.parse_args()
    grid_size, obstacles, wires = parse_input(args.infile)
    print('grid size: ', grid_size)
    print('obstacles: ', obstacles)
    print('wires: ', wires)

    print('total L1', totalL1Distance([(3, 4), (1, 2), (5, 6)]))
