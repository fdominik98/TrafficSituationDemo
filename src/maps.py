
def rotate_lanes_90_degrees(lanes):
    rotated_lanes = []
    for lane in lanes:
        rotated_lane = []
        for point in lane:
            rotated_point = (-point[1], point[0])
            rotated_lane.append(rotated_point)
        rotated_lanes.append(tuple(rotated_lane))
    return rotated_lanes

def get_scenic_coord(cls, coord : tuple[float, float]):
    return f'{coord[0]} @ {coord[1]}' 

def inverse_rotate_coord(cls, coord : tuple[float, float]):
    coord = (coord[1], -coord[0])
    return get_scenic_coord(cls, coord)

map_town_01 = [
    ((3.86, -10), (3.93, -317.6),
     (0, -10), (0.08, -317.6)), 
    
    ((0, -10), (0.08, -317.6),
     (-0.13, -10), (-0.08, -317.6)),

    ((-0.13, -10), (-0.08, -317.6),
     (-4, -10), (-3.92, -317.6)),
]
map_town_01 = rotate_lanes_90_degrees(map_town_01)


map_town_06 = [
    ((128.5, -235.9), (599, -236),
     (128.5, -239.25), (599, -239.4)), 
    
    ((128.5, -239.25), (599, -239.4),
     (128.5, -239.38), (599, -239.54)),

    ((128.5, -239.38), (599, -239.54),
     (128.5, -242.75), (599, -242.9)),
    
    ((128.5, -242.75), (599, -242.9),
     (128.5, -242.9), (599, -243)),

    ((128.5, -242.9), (599, -243),
     (128.5, -246.25), (599, -246.4)) ,
    
    ((128.5, -246.25), (599, -246.4),
     (128.5, -246.4), (599, -246.55)),

    ((128.5, -246.4), (599, -246.55),
     (128.5, -249.75), (599, -249.9)),
    
    ((128.5, -249.75), (599, -249.9),
     (128.5, -249.9), (599, -250)) ,

    ((128.5, -249.9), (599, -250),
     (128.5, -253.25), (599, -253.4))
]

maps : dict = {'Town01' : [('road15', map_town_01, inverse_rotate_coord, [False, None, True])], 'Town06' : ['road40', map_town_06, get_scenic_coord, [True, None, True, None, True, None, True, None, True]]}


