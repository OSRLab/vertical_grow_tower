import Part, PartGui
from FreeCAD import Base
import math

vec = Base.Vector


class GrowTower:
    """
    Store all the constants in here that you need to access for later steps.
    Compute a few, transfering logic in here it totally okay.
    """

    def __init__(self,
        dual=False,
        inner_tube_radius=24,
        tube_z_offset=4,
        tube_height=100,
        cham_len=0.5,
        bottom_cap_hole_ledge=5,
    ):
        self.main_thickness = 6.5
        self.inner_radius = 43.5
        self.outer_radius = self.inner_radius + self.main_thickness
        self.tower_height = 100
        self.tube_thickness = 6
        self.inner_tube_radius = inner_tube_radius
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
        self.tube_angle = 45
        self.tube_x_offset = 4
        self.tube_z_offset = tube_z_offset
        self.dual = dual
        self.cham_len = cham_len
        self.cap_thickness = 10
        self.bar_length = 100
        self.bar_width = 30
        self.hole_radius = 5
        self.hole_offset = 3
        self.bottom_cap_hole_ledge = bottom_cap_hole_ledge
        self.bottom_cap_hole_radius = self.inner_radius - self.bottom_cap_hole_ledge
        self.handle_radius = 5
        self.handle_width = 2

    def make_cap(self, bottom=True):
        """
        """
        cut_tower = self.make_it_all()
        outer_radius = self.outer_radius
        cap_thickness = self.cap_thickness
        bar_length = self.bar_length
        bar_width = self.bar_width
        hole_radius = self.hole_radius
        hole_offset = self.hole_offset
        bottom_cap_hole_radius = self.bottom_cap_hole_radius
        tower_height = self.tower_height
        handle_radius = self.handle_radius
        handle_width = self.handle_width

        # cut_tower = gt.make_it_all()
        # outer_radius = gt.outer_radius
        # cap_thickness = gt.cap_thickness
        # bar_length = gt.bar_length
        # bar_width = gt.bar_width
        # hole_radius = gt.hole_radius
        # hole_offset = gt.hole_offset
        # bottom_cap_hole_radius = gt.bottom_cap_hole_radius
        # tower_height = gt.tower_height
        # handle_radius = gt.handle_radius
        # handle_width = gt.handle_width

        # cap = Part.makeBox(bar_width, bar_length, cap_thickness,
        #                    vec(-bar_width/2, -bar_length/2, -cap_thickness/2))

        # end1 = Part.makeCylinder(bar_width/2, cap_thickness,
        #                    vec(0, -bar_length/2, -cap_thickness/2))

        # end2 = Part.makeCylinder(bar_width/2, cap_thickness,
        #                    vec(0, bar_length/2, -cap_thickness/2))

        cap_plate = Part.makeCylinder(outer_radius, cap_thickness,
                    vec(0,0,-cap_thickness/2))

        # cap = cap.fuse(end1).fuse(end2).fuse(cap_plate)
        if bottom:
            hole1 = Part.makeCylinder(hole_radius, cap_thickness,
                vec(0, -bar_length/3 - hole_offset, -cap_thickness/2))

            hole2 = Part.makeCylinder(hole_radius, cap_thickness,
                vec(0, bar_length/3 + hole_offset, -cap_thickness/2))
            bottom_cutout = Part.makeCylinder(30, 2*cap_thickness, vec(0,0,-cap_thickness/2) )

            holes = hole1.fuse(hole2)
            bottom_holes = holes.fuse(bottom_cutout)
            whole_thing = bottom_holes.fuse(cut_tower)
            cap = cap_plate.cut(whole_thing)
            # return cap
        else:
            # Make the viewing cap
            cap_cutout = Part.makeCylinder(20, cap_thickness, vec(0, 0, tower_height - cap_thickness/2))
            # Edge is Numero Tres
            edges = [3]
            radii = [5, 5]
            chammed_cut = self.chamfer_me_baby(cap_cutout, edges, radii)

            cap_plate.translate(vec(0, 0, tower_height))
            cut_plate = cap_plate.cut(chammed_cut)
            top_cutout = Part.makeCylinder(5, 2*cap_thickness, vec(0,0,tower_height-cap_thickness/2))
            chammed_holed_cut = chammed_cut.cut(top_cutout)

            hole1 = Part.makeCylinder(hole_radius, cap_thickness,
                vec(0, -bar_length/3 - hole_offset, tower_height-cap_thickness/2))

            hole2 = Part.makeCylinder(hole_radius, cap_thickness,
                vec(0, bar_length/3 + hole_offset, tower_height-cap_thickness/2))
            holes = hole1.fuse(hole2)
            whole_thing = holes.fuse(cut_tower)
            cap = cap_plate.cut(whole_thing)
            cut_cap = cap.cut(chammed_cut)
            return cut_cap, chammed_holed_cut            
        # if bottom:
        #     cap = cap.cut(cut_tower)
        #     bottom_cutout = Part.makeCylinder(bottom_cap_hole_radius, cap_thickness, vec(0,0,-cap_thickness/2) )
        #     cap = cap.cut(bottom_cutout)
        #     if chammed:
        #         # edges = [edge for edge in range(75,84)]
        #         edges = [16, 17, 53, 54, 55, 56, 57, 58, 50]
        #         cap = self.chamfer_me_baby(cap, edges, cham_lens=[2.3, 2.3])

        #     return cap
        # else:
        #     cap.translate(vec(0, 0, tower_height))
        #     cap = cap.cut(tower)
        #     viewhole_1 = Part.makeCylinder(25, cap_thickness/2, vec(0,0,tower_height))
        #     viewhole_2 = Part.makeCylinder(20, cap_thickness, vec(0,0, tower_height - cap_thickness/2))
        #     viewhole = viewhole_1.fuse(viewhole_2)
        #     cap = cap.cut(viewhole)
        #     handle = Part.makeCylinder(handle_radius,handle_width)
        #     handle.rotate(vec(0,0,handle_width/2), vec(0,1,0), 90)
        #     handle.translate(vec(0,0,tower_height+handle_radius/2))
        #     viewhole = viewhole.fuse(handle)
        #     return cap, viewhole


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


    def chamfer_me_baby(self, part, edges=[], cham_lens=[1.0,1.0]):
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
                myEdges.append((edge, cham_lens[0], cham_lens[1]))
        else:
            return None
        FreeCAD.ActiveDocument.myChamfer.Edges = myEdges
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.myPart.Visibility = False
        res = FreeCADGui.ActiveDocument.myChamfer.Object.Shape
        App.getDocument("Unnamed").removeObject("myChamfer")
        App.getDocument("Unnamed").removeObject("myPart")
        return res

    def fillet_me_baby(self, part, edges=[], fillet_lens=[1.0,1.0]):
        """
        Helper function to chamfer edges given their numbers and chamfer length.
        """
        myPart = FreeCAD.ActiveDocument.addObject("Part::Feature", "myPart")
        myPart.Shape = part
        fillet = FreeCAD.ActiveDocument.addObject("Part::Fillet", "myFillet")
        fillet.Base = FreeCAD.ActiveDocument.myPart
        myEdges = []
        if len(edges) > 0:
            for edge in edges:
                myEdges.append((edge, fillet_lens[0], fillet_lens[1]))
        else:
            return None
        FreeCAD.ActiveDocument.myFillet.Edges = myEdges
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.myPart.Visibility = False
        res = FreeCADGui.ActiveDocument.myFillet.Object.Shape
        App.getDocument("Unnamed").removeObject("myFillet")
        App.getDocument("Unnamed").removeObject("myPart")
        return res

    def chamfer_my_tube(self, tower):
        chamed_tube = self.chamfer_me_baby()


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
        #cham_pan = self.chamfer_me_baby(pan, [3], cham_lens=[cham_len, cham_len])
        cut_top = tower_shell.cut(pan)

        # CUT AROUND THE OUTER SURFACE ON BOTTOM. WATER GOES DOWN.
        # Make it in deeper by tolerance/2
        bottom_ring_radius = self.bottom_ring_radius
        bottom_cutaround_radius = self.bottom_cutaround_radius
        outer_ring = Part.makeCylinder(bottom_ring_radius, cutout_height)
        inner_volume = Part.makeCylinder(bottom_cutaround_radius, cutout_height)
        bottom_ring = outer_ring.cut(inner_volume)
        # chamfer Edge 4
        both_cut = cut_top.cut(bottom_ring)
        # both_cut_cham = self.chamfer_me_baby(both_cut, [35], cham_lens=[cham_len,cham_len])

        return both_cut


    def make_it_all(self):
        """
        make a raw tower, cut out rings, and notch.
        """

        raw_tower = self.make_raw_tower()
        cut_tower = self.make_em_stack(raw_tower)

        if not self.dual:
            edges = [5,7]
        else:
            edges = [6,14] # different designs, different edge numbers
        
        filleted_tower = self.chamfer_me_baby(
            cut_tower, edges=edges, cham_lens=[2.3, 2.3]
            )
        filleted_tower2 = filleted_tower.copy()
        filleted_tower2.translate(vec(0, 0, self.tower_height-self.cutout_height - 2.3))
        center = vec(0,0,0)
        rot_vec = vec(0,0,1)
        rot_angle = 30
        filleted_tower2.rotate(center, rot_vec, rot_angle)
        full_tower = filleted_tower.fuse(filleted_tower2)
        return full_tower


