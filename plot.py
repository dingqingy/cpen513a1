from tkinter import *
from tkinter import ttk
COLORS = ['black', 'red', 'yellow', 'azure4', 'orange', 'maroon', 'pink', 'lime green', 'dark violet', 'green']


def plot(canvas, grid_size, obstacles, wires):
    x_bound, y_bound = grid_size
    sizex = 1000 / x_bound
    sizey = 500 / y_bound

    for i in range(x_bound):
        for j in range(y_bound):
            if (i, j) in obstacles:
                canvas.create_rectangle(sizex * i, sizey * j, sizex * (i + 1), sizey * (j + 1), fill='blue')
            else:
                canvas.create_rectangle(sizex * i, sizey * j, sizex * (i + 1), sizey * (j + 1), fill='white')
            for k, wire in enumerate(wires):
                if (i, j) in wire:
                    canvas.create_rectangle(sizex * i, sizey * j, sizex * (i + 1), sizey * (j + 1), fill=COLORS[k + 1])
                    canvas.create_text(sizex * (i + 0.5), sizey * (j + 0.5), text=k + 1)


if __name__ == '__main__':
    root = Tk()
    frame = ttk.Frame(root, width=1000, height=500)
    frame.pack()
    c = Canvas(frame, bg='white', width=1000, height=500)
    c.pack()
    grid_size = (12, 9)
    obstacles = [(8, 2), (9, 2), (10, 2), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (6, 5), (9, 5), (6, 6), (9, 6), (6, 7), (9, 7), (2, 8), (3, 8), (4, 8), (9, 8)]
    wires = [[(10, 1), (2, 7)], [(8, 3), (7, 7), (10, 7)]]
    plot(c, grid_size, obstacles, wires)
    root.mainloop()
