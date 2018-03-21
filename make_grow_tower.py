import Part, PartGui
from FreeCAD import Base
import math

vec = Base.Vector

class Config:
    """
    Store all the constants in here that you need to access for later steps.
    Compute a few, transfering logic in here it totally okay.
    """
    def __init__(self):
        self.outer_radius = 50
        self.inner_radius = 44
        self.tower_height = 100
        self.outer_tube_radius = 28
        self.inner_tube_radius = 22
        self.tube_height = self.tower_height
        self.destructor_radius = self.outer_tube_radius
        self.destructor_height = 18.3
        self.tolerance = 0.001 # one micron
        self.cutout_thickness = 3
        self.cutout_height = 5
        self.bottom_ring_radius = 55
        self.move_up = self.tower_height - self.cutout_height
        self.top_cutout_radius = self.inner_radius + \
                                 self.cutout_thickness + \
                                 self.tolerance/2
        self.bottom_cutaround_radius = self.outer_radius - \
                                       self.cutout_thickness - \
                                       self.tolerance/2
        self.angle = math.pi/3


def move_tube(part):
    """
    move parts into position for the tube that holds net cup.
    """
    part.rotate(vec(0, 0, 0), vec(0, 1, 0), 40)
    part.translate(vec(10, 0, 4))

def make_raw_tower(config):
    """
    Base design. Add / Subtract from this rough model to create finished 
    product.
    """
    # Make main tower components inner and outer.
    outer_radius = config.outer_radius
    inner_radius = config.inner_radius
    main_height = config.tower_height
    outer_main = Part.makeCylinder(outer_radius, main_height)
    inner_main = Part.makeCylinder(inner_radius, main_height)

    # Construct inner and outer tube
    outer_tube_radius = config.outer_tube_radius
    inner_tube_radius = config.inner_tube_radius
    tube_height = config.tower_height
    outer_tube = Part.makeCylinder(outer_tube_radius, tube_height)
    inner_tube = Part.makeCylinder(inner_tube_radius, tube_height)
    
    # Move them into position
    move_tube(outer_tube)
    move_tube(inner_tube)

    # Create an outer cylinder to clean up the mess
    destructor_radius = config.destructor_radius
    destructor_height = config.destructor_height
    tube_destructor = Part.makeCylinder(destructor_radius, destructor_height)
    move_tube(tube_destructor)

    # Create an outer and an inner main
    outer_shell = outer_main.fuse(outer_tube)
    inner_volume = inner_main.fuse(inner_tube)

    # Cut the volume out and leave only shell
    tower_shell_dirty = outer_shell.cut(inner_volume)

    # Cut away model hanging below
    tower_shell = tower_shell_dirty.cut(tube_destructor)

    return tower_shell


def make_em_stack(tower_shell, config):
    """
    Cut out rings on top and bottom to allow planter units to stack.
    """
    tolerance = config.tolerance
    cutout_thickness = config.cutout_thickness
    outer_radius = config.outer_radius
    inner_radius = config.inner_radius
    cutout_height = config.cutout_height
    tower_height = config.tower_height
    bottom_ring_radius = config.bottom_ring_radius
    
    # CUT INSIDE OUT ON TOP. WATER GOES DOWN.
    # Move the shell up to the top before cutting out.
    move_up = config.move_up
    
    # Make it cut out wider by tolerance/2
    top_cutout_radius = config.top_cutout_radius
    pan = Part.makeCylinder(top_cutout_radius, cutout_height)
    pan.translate(vec(0, 0, move_up))
    cut_top = tower_shell.cut(pan)
    
    # CUT AROUND THE OUTER SURFACE ON BOTTOM. WATER GOES DOWN.
    # Make it in deeper by tolerance/2
    bottom_cutaround_radius = config.bottom_cutaround_radius
    outer_ring = Part.makeCylinder(bottom_ring_radius, cutout_height)
    inner_volume = Part.makeCylinder(bottom_cutaround_radius, cutout_height)
    bottom_ring = outer_ring.cut(inner_volume)
    both_cut = cut_top.cut(bottom_ring)
    return both_cut

def notch_it(tower_shell, config):
    """
    Using small spheres, create notches and notch cutouts to lock towers
    into a repeatable configuration. Keep them from sliding around z-axis.
    """
    bottom_radius = config.bottom_cutaround_radius
    cutout_height = config.cutout_height
    bottom_notch_radius = 1 - config.tolerance / 2
    bottom_notch = Part.makeSphere(bottom_notch_radius,
                                   vec(bottom_radius, 0, cutout_height))

    # The notches on the top need some elementary trig to calculate their position.
    top_radius = config.top_cutout_radius
    top_notch_radius = 1 + config.tolerance / 2
    angle = config.angle
    x_coord_1 = top_radius * math.cos(angle)
    x_coord_2 = top_radius * math.cos(-angle)
    y_coord_1 = top_radius * math.sin(angle)
    y_coord_2 = top_radius * math.sin(-angle)
    z_coord = config.tower_height
    top_notch_1 = Part.makeSphere(top_notch_radius,
                                  vec(x_coord_1, y_coord_1, z_coord))
    top_notch_2 = Part.makeSphere(top_notch_radius,
                                  vec(x_coord_2, y_coord_2, z_coord))

    # Now add the bottom notch.
    tower_shell_1 = tower_shell.fuse(bottom_notch)

    # Cut out notches on top.
    tower_shell_2 = tower_shell_1.cut(top_notch_1)
    tower_shell_final = tower_shell_2.cut(top_notch_2)
    return tower_shell_final

def make_it_all(config):
    """
    make a raw tower, cut out rings, and notch.
    """
    raw_tower = make_raw_tower(config)
    cut_tower = make_em_stack(raw_tower, config)
    finished_tower = notch_it(cut_tower, config)
    return finished_tower

if __name__ == "__main__":
    config = Config()
    grow_tower = make_it_all(config)
