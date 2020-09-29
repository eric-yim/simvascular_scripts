"""
Takes in segmentation file (XXX.ctgr)
Allows for programmatic manipulation of contour control points
Creates files for svpre steps

script will output the following file structure

sims/
  name/
    inflow.flow
    MyModel.svpre
    solver.inp
    mesh-complete/
      mesh-complete.mesh.vtu
      mesh-complete.exterior.vtp
      walls-combined.vtp
      mesh-surfaces/
        1.vtp
        2.vtp
        3.vtp
"""
#Name of Main Directory
mdir = "/home/ericyim/Desktop/sv_script/new-py-proj02/"
#Name of new simulation
name = 'sim02/'
import sv
import sys
import vtk
import os
import numpy as np
from shutil import copyfile
sys.path.append(mdir)
import graphics as gr
import control_point_manipulation as manip

newdir = mdir+'sims/' + name


list_of_scales = np.load(mdir+'raw_data/keypoints.npy')
#print(list_of_scales)
# list_of_scales = np.array([
#     [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
#     [1.475, 1.475, 1.475, 1.475, 1.,    1.025, 1.025, 1.025, 1.025, 1.025],
#     [1.45, 1.45, 1.45, 1.45, 1.,   1.05 ,1.05 ,1.05 ,1.05 ,1.05]

# ])
#=========================================================================================
# File Structure
def make_dirs():
    """
    Make file structure:
    sims/NAME/mesh-complete/mesh-surfaces
    """
    def makedir(path):
        if not os.path.exists(path):
            os.mkdir(path)

    dir_complete='mesh-complete/'
    dir_surf = "mesh-surfaces/"
    makedir(newdir)
    makedir(newdir+dir_complete)
    makedir(newdir+dir_complete+dir_surf)
def copyfiles():
    files = ['inflow.flow','MyModel.svpre','solver.inp']
    fromfiles = [mdir+'raw_data/'+f for f in files]
    tofiles = [newdir+f for f in files]
    for f0,f1 in zip(fromfiles,tofiles):
        copyfile(f0,f1)
#=========================================================================================
# Segmentation
 
def set_spline(control_points):
    # .ctgr includes center and distance control points, followed by outer control points
    # this function takes outer control points only
    seg = sv.segmentation.SplinePolygon(control_points=control_points)
    seg.set_subdivision_params(type=sv.segmentation.SubdivisionType.CONSTANT_SPACING)
    return seg
def set_splines(control_points_list):
    segs = [set_spline(control_points) for control_points in control_points_list]
    return segs

def read_contours(file_name):
    print("Read SV ctgr file: {0:s}".format(file_name))
    contour_group = sv.segmentation.Series(file_name)
    num_conts = contour_group.get_num_segmentations()
    contours = []

    for i in range(num_conts):
        cont = contour_group.get_segmentation(i)
        contours.append(cont)

    print("Number of contours: {0:d}".format(num_conts))
    return contours

# Manipulation of Contour
def get_center_outer(contour):
    return contour.get_center(),contour.get_control_points()
def manipulate_contour(contour,scale_factor):
    """
    Radially expand or contract given contour
    scale_factor is a np.array of same length as contour. values >1 is expansion, values <1 is contraction
    """
    center,outer = get_center_outer(contour)
    new_outer = manip.vary_points_test(center,outer,scale_factor=scale_factor)
    contour = set_spline(new_outer)
    return contour
def manipulate_contour_test(center,outer,scale_factor):
    """
    Radially expand or contract given contour
    scale_factor is a np.array of same length as contour. values >1 is expansion, values <1 is contraction
    """
    
    new_outer = manip.vary_points_test(center,outer,scale_factor=scale_factor)
    contour = set_spline(new_outer)
    return contour
#=========================================================================================
# Modeling
def get_profile_contour(contours, cid, npts):
    cont = contours[cid]
    cont_pd = cont.get_polydata()
    cont_ipd = sv.geometry.interpolate_closed_curve(polydata=cont_pd, number_of_points=npts)
    return cont_ipd
def loft(contours):
    num_contours = len(contours)
    num_profile_points = 50# what does this do?
    use_distance = True
    contour_list = []
    start_cid = 0
    end_cid = num_contours
    for cid in range(start_cid,end_cid):
        cont_ipd = get_profile_contour(contours, cid, num_profile_points)
        if cid == start_cid:
            cont_align = cont_ipd
        else:
            cont_align = sv.geometry.align_profile(last_cont_align, cont_ipd, use_distance)
        contour_list.append(cont_align)
        last_cont_align = cont_align
    options = sv.geometry.LoftNurbsOptions()
    loft_surf = sv.geometry.loft_nurbs(polydata_list=contour_list, loft_options=options)#, num_divisions=12
    loft_capped = sv.vmtk.cap(surface=loft_surf, use_center=False)

    # We dont need to save the ugly_file, it will be remeshed
    # ugly_file = mdir+"temp/"+"capped-loft-surface.vtp"
    # writer = vtk.vtkXMLPolyDataWriter()
    # writer.SetFileName(ugly_file)
    # writer.SetInputData(loft_capped)
    # writer.Update()
    # writer.Write()
    return loft_capped
def remesh(loft_capped):
    remesh_file = mdir+"temp/"+"loft_nurb_model"
    modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)
    model = sv.modeling.PolyData()
    model.set_surface(surface=loft_capped)
    model.compute_boundary_faces(angle=60.0)
    remesh_model = sv.mesh_utils.remesh(model.get_polydata(), hmin=0.1, hmax=0.1)
    model.set_surface(surface=remesh_model)
    model.compute_boundary_faces(angle=60.0)
    
    model.write(remesh_file, format="vtp")
    polydata = model.get_polydata()
    print("Model: ")
    print("  Number of points: " + str(polydata.GetNumberOfPoints()))
    print("  Number of cells: " + str(polydata.GetNumberOfCells()))
    return remesh_file + '.vtp',polydata
#=========================================================================================
# Meshing  
# see https://github.com/SimVascular/SimVascular-Tests/blob/master/new-api-tests/meshing/tetgen-options.py
def do_mesh(file_name):
    dir_complete='mesh-complete/'
    dir_surf = "mesh-surfaces/"
    mesher = sv.meshing.create_mesher(sv.meshing.Kernel.TETGEN)
    options = sv.meshing.TetGenOptions(global_edge_size=0.05, surface_mesh_flag=True, volume_mesh_flag=True) 
    mesher.load_model(file_name)

    ## Set the face IDs for model walls.
    wall_face_ids = [1]
    mesher.set_walls(wall_face_ids)

    ## Compute model boundary faces.
    mesher.compute_model_boundary_faces(angle=50.0)
    face_ids = mesher.get_model_face_ids()
    print("Mesh face ids: " + str(face_ids))

    ## Set boundary layer meshing options
    print("Set boundary layer meshing options ... ")
    mesher.set_boundary_layer_options(number_of_layers=2, edge_size_fraction=0.5, layer_decreasing_ratio=0.8, constant_thickness=False)
    options.no_bisect = False

    ## Print options.
    #print("Options values: ")
    #[ print("  {0:s}:{1:s}".format(key,str(value))) for (key, value) in sorted(options.get_values().items()) ]

    ## Generate the mesh. 
    mesher.generate_mesh(options)
    
    ## Get the mesh as a vtkUnstructuredGrid. 
    mesh = mesher.get_mesh()
    
    print("Mesh:")
    print("  Number of nodes: {0:d}".format(mesh.GetNumberOfPoints()))
    print("  Number of elements: {0:d}".format(mesh.GetNumberOfCells()))

    ## Write the mesh.
    mesher.write_mesh(file_name=newdir+dir_complete+'mesh-complete.mesh.vtu')

    ## Export the mesh-complete files
    for i in range(4):#complete exterior and 3 faces
        if i==0:
            temp_name = newdir+dir_complete+'mesh-complete.exterior.vtp'
            surf_mesh = mesher.get_surface()
        else:
            temp_name = newdir+dir_complete+dir_surf + str(i) + ".vtp"
            surf_mesh = mesher.get_face_polydata(i)
        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetFileName(temp_name)
        writer.SetInputData(surf_mesh)
        writer.Update()
        writer.Write()
        #Main wall
        if i==1:
            temp_name2 = newdir+dir_complete+'walls_combined.vtp'
            copyfile(temp_name,temp_name2)
#=========================================================================================
# Graphics
def draw_solid(polydata):
    win_width = 500
    win_height = 500
    renderer, renderer_window = gr.init_graphics(win_width, win_height)
    gr.add_geometry(renderer, polydata, color=[0.0, 1.0, 0.0], wire=False, edges=True)
    gr.display(renderer_window)

def draw_segmentations(contours):
    num_segs = len(contours)

    ## Create renderer and graphics window.
    win_width = 500
    win_height = 500
    renderer, renderer_window = gr.init_graphics(win_width, win_height)
    ## Show contours.
    for sid in range(num_segs):
        seg = contours[sid]
        control_points = seg.get_control_points()
        gr.create_segmentation_geometry(renderer, seg)

    # Display window.
    gr.display(renderer_window)

#=========================================================================================

def main():
    make_dirs()
    file_name = mdir+'raw_data/simple_coronary.ctgr'
    contours=read_contours(file_name)

    
    center,outer = get_center_outer(contours[2])
    # any of the contours can be manipulated
    for scale_factor in list_of_scales:
        
        try:
            contours[2]=manipulate_contour_test(center,outer,scale_factor)
            #draw_segmentations(contours)
            loft_capped=loft(contours)
            remesh_file,polydata=remesh(loft_capped)
            draw_solid(polydata)
        except:
            print("bad:",scale_factor)
            pass

    #do_mesh(remesh_file)
    #copyfiles()

    
main()
