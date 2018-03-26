import Part, PartGui
from FreeCAD import Base
import math

vec = Base.Vector


class GrowTower:
    """
    Store all the constants in here that you need to access for later steps.
    Compute a few, transfering logic in here it totally okay.
    """

    def __init__(self, dual=False, inner_radius=22, tube_z_offset=4, tube_height=100, cham_len=0.5):
        self.main_thickness = 6.5
        self.inner_radius = 43.5
        self.outer_radius = self.inner_radius + self.main_thickness
        self.tower_height = 100
        self.tube_thickness = 6
        self.inner_tube_radius = inner_radius
        self.outer_tube_radius = self.inner_tube_radius + self.tube_thickness
        self.tube_height = tube_height
        self.destructor_radius = self.outer_tube_radius + 20
        self.destructor_height = 200
        self.tolerance = 0.001 # one micron
        self.cutout_thickness = self.main_thickness / 2
        self.cutout_height = 5
        self.bottom_ring_radius = 55
        self.move_up = self.tower_height - self.cutout_height
        self.top_cutout_radius = self.inner_radius + \
                                 self.cutout_thickness + \
                                 self.tolerance/2
        self.bottom_cutaround_radius = self.outer_radius - \
                                       self.cutout_thickness - \
                                       self.tolerance/2
        self.notch_angle = math.pi/3
        self.tube_angle = 40
        self.tube_x_offset = 10
        self.tube_z_offset = tube_z_offset
        self.dual = dual
        self.cham_len = cham_len


    def move_tube(self, part, flip=False):
        """
        move parts into position for the tube that holds net cup.
        """
        center = vec(0,0,0)
        axis = vec(0,1,0)
        angle = self.tube_angle
        x_offset = self.tube_x_offset
        z_offset = self.tube_z_offset
        trans_vec = vec(x_offset,0,z_offset)
        if not flip:
            part.rotate(center, axis, angle)
            part.translate(trans_vec)
        else:
            opposite_trans_vec = vec(-x_offset, 0, z_offset)
            part.rotate(center, axis, -angle)
            part.translate(opposite_trans_vec)


    def make_tube(self, flip=False):
        """
        Make a planting site AKA a tube sticking out the side.
        """
        # Construct inner and outer tube
        outer_tube_radius = self.outer_tube_radius
        inner_tube_radius = self.inner_tube_radius
        tube_height = self.tube_height
        outer_tube = Part.makeCylinder(outer_tube_radius, tube_height)
        inner_tube = Part.makeCylinder(inner_tube_radius, tube_height)

        # Move them into position
        self.move_tube(outer_tube, flip=flip)
        self.move_tube(inner_tube, flip=flip)
        return outer_tube, inner_tube


    def make_destructor(self):
        """
        Make a big cylinder that sits under the planter to clean up debris.
        """
        # Create an outer cylinder to clean up the mess
        destructor_radius = self.destructor_radius
        destructor_height = self.destructor_height
        tube_destructor = Part.makeCylinder(destructor_radius, destructor_height)
        tube_destructor.translate(vec(0,0,-destructor_height))
        return tube_destructor


    def chamfer_me_baby(self, part, edges=[], cham_len=1.0):
        """
        Helper function to chamfer edges given their numbers and chamfer length.
        """
        myPart = FreeCAD.ActiveDocument.addObject("Part::Feature", "myPart")
        myPart.Shape = part
        chmfr = FreeCAD.ActiveDocument.addObject("Part::Chamfer", "myChamfer")
        chmfr.Base = FreeCAD.ActiveDocument.myPart
        myEdges = []
        if len(edges) > 0:
            for edge in edges:
                myEdges.append((edge, cham_len, cham_len))
        else:
            return None
        FreeCAD.ActiveDocument.myChamfer.Edges = myEdges
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.myPart.Visibility = False
        res = FreeCADGui.ActiveDocument.myChamfer.Object.Shape
        App.getDocument("Unnamed").removeObject("myChamfer")
        App.getDocument("Unnamed").removeObject("myPart")
        return res


    def make_raw_tower(self):
        """
        Base design. Add / Subtract from this rough model to create finished
        product.
        """
        # Make main tower components inner and outer.
        outer_radius = self.outer_radius
        inner_radius = self.inner_radius
        main_height = self.tower_height
        outer_main = Part.makeCylinder(outer_radius, main_height)
        inner_main = Part.makeCylinder(inner_radius, main_height)

        # Use self.make_tube to create outer and inner tube cylinders.
        outer_tube, inner_tube = self.make_tube(flip=False)

        tube_destructor = self.make_destructor()

        if not self.dual:
            # Create an outer and an inner main
            outer_shell = outer_main.fuse(outer_tube)
            inner_volume = inner_main.fuse(inner_tube)
        else:
            outer_tube_back, inner_tube_back = self.make_tube(flip=True)
            outer_shell = outer_main.fuse(outer_tube)
            outer_shell = outer_shell.fuse(outer_tube_back)
            inner_volume = inner_main.fuse(inner_tube)
            inner_volume = inner_volume.fuse(inner_tube_back)


        # Cut the volume out and leave only shell
        tower_shell_dirty = outer_shell.cut(inner_volume)

        # Cut away model hanging below
        tower_shell = tower_shell_dirty.cut(tube_destructor)

        return tower_shell


    def make_em_stack(self, tower_shell):
        """
        Cut out rings on top and bottom to allow planter units to stack.
        Put a chamfer on the bottom and top so they more easily fit together.
        """
        cutout_height = self.cutout_height
        move_up = self.move_up
        top_cutout_radius = self.top_cutout_radius
        cham_len = self.cham_len

        # CUT INSIDE OUT ON TOP. WATER GOES DOWN.
        pan = Part.makeCylinder(top_cutout_radius, cutout_height)
        pan.translate(vec(0, 0, move_up))
        # chamfer Edge 3.
        cham_pan = self.chamfer_me_baby(pan, [3], cham_len=cham_len)
        cut_top = tower_shell.cut(cham_pan)

        # CUT AROUND THE OUTER SURFACE ON BOTTOM. WATER GOES DOWN.
        # Make it in deeper by tolerance/2
        bottom_ring_radius = self.bottom_ring_radius
        bottom_cutaround_radius = self.bottom_cutaround_radius
        outer_ring = Part.makeCylinder(bottom_ring_radius, cutout_height)
        inner_volume = Part.makeCylinder(bottom_cutaround_radius, cutout_height)
        bottom_ring = outer_ring.cut(inner_volume)
        # chamfer Edge 4
        both_cut = cut_top.cut(bottom_ring)
        both_cut_cham = self.chamfer_me_baby(both_cut, [35], cham_len=cham_len)

        return both_cut_cham


    def notch_it(self, tower_shell):
        """
        Using small spheres, create notches and notch cutouts to lock towers
        into a repeatable configuration. Keep them from sliding around z-axis.
        """
        bottom_radius = self.bottom_cutaround_radius
        cutout_height = self.cutout_height
        bottom_notch_radius = 1 - self.tolerance / 2
        bottom_notch = Part.makeSphere(bottom_notch_radius,
                                       vec(bottom_radius, 0, cutout_height))

        # The notches on the top need some elementary trig to calculate their position.
        top_radius = self.top_cutout_radius
        top_notch_radius = 1 + self.tolerance / 2
        angle = self.notch_angle
        x_coord_1 = top_radius * math.cos(angle)
        x_coord_2 = top_radius * math.cos(-angle)
        y_coord_1 = top_radius * math.sin(angle)
        y_coord_2 = top_radius * math.sin(-angle)
        z_coord = self.tower_height
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


    def make_it_all(self):
        """
        make a raw tower, cut out rings, and notch.
        """
        raw_tower = self.make_raw_tower()
        cut_tower = self.make_em_stack(raw_tower)
        # chammed = self.chamfer_me_baby(cut_tower)
        # finished_tower = cut_tower
        finished_tower = self.notch_it(cut_tower)
        self.finished_tower = finished_tower
        return finished_tower
