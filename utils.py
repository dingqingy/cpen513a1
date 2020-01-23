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


if __name__ == "__main__":
    grid_size, obstacles, wires = parse_input('benchmarks/example.infile')
    print(grid_size)
    print(obstacles)
    print(wires)
