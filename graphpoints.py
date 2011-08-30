import math

from matplotlib import pyplot, axes
from mpl_toolkits.mplot3d import axes3d
import numpy

from sys import argv

if __name__ == '__main__':

    fig = pyplot.figure()
    axes = pyplot.subplot(111, projection='3d')

    points = [( 0.07826526, -0.8631922 , -0.49877228),
              (-0.02999477, -0.96742597, -0.25137087), 
              ( 0.06420691, -0.9818318 , -0.17856034), 
              ( 0.16057571, -0.95586931, -0.24602703), 
              ( 0.24508727, -0.95988891, -0.13618192), 
              ( 0.40681028, -0.88751077, -0.21640245), 
              ( 0.44190865, -0.81611357, -0.37239145), 
              ( 0.47401636, -0.79000325, -0.38884876),
              ( 0.07826526, -0.8631922 , -0.49877228)]

    axes.plot(*[[p[i] for p in points] for i in range(3)], color='r')

    query = (0.29210493879571187, -0.8867057671346513, -0.35836794954530027)

    axes.scatter(*[[query[i]] for i in range(3)], color='g')

    ext = (-0.21032302, 0.93088621, 0.29868896)

    axes.scatter(*[[ext[i]] for i in range(3)], color='g')

    for span in [[(0.47401636, -0.79000325, -0.38884876), (0.07826526, -0.8631922, -0.49877228)],
        [(-0.02999477, -0.96742597, -0.25137087), (0.06420691, -0.9818318, -0.17856034)]]:
        axes.plot(*[[p[i] for p in span] for i in range(3)], color='b')

    axes.set_xlim3d(-1,1)
    axes.set_ylim3d(-1,1)
    axes.set_zlim3d(-1,1)

    pyplot.show()
