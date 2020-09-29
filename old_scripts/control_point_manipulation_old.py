from xml.etree import ElementTree
import numpy as np
"""
Vary cross section by expanding or collapsing control points radially
Process:
    Import original control points (obtained from SimVasc)
        This includes [center point, size point, outer0, outer1, ...]
    Translate control points into new plane represented by tangent vector and centered at center point
    Expand, collapse via specified method
    Translate back to old plane

Note: if simply expanding,collapsing, we don't need to translate plane.
Translating plane is useful for visualizing samples in matplotlib
"""

#======================================================================================================
# Read File
def extract_coords(point):
    coordinate_order = 'xyz'
    lookup_dict = point.attrib
    xyz =  [float(lookup_dict[j]) for j in coordinate_order]
    return xyz
def contour_control_points_from_xml(filename):
    """
    Input a Contour File Location (XXX.ctgr)
    Return 2 Lists: Normals; Control Points
    """
    
    tree = ElementTree.parse(filename)
    path_root = tree.getroot()	
    
    my_points = path_root[0]
    contour_control_points = []
    tan_points = []
    for child in my_points:
        if child.tag=='contour':
            for grandchild in child:
                if grandchild.tag=='control_points':
                    points = [extract_coords(point) for point in grandchild]
                elif grandchild.tag=='path_point':
                    tangent_point = extract_coords(grandchild[1])#Get tangent
            tan_points.append(tangent_point)
            contour_control_points.append(points)
    return tan_points,contour_control_points

#======================================================================================================
# Translating Axes
def convert_to_xy_plane(tangent,control_points):
    """
    Convert 3D points to xy plane centered at 0,0
    Returns only outer control points
    """
    tangent = np.array(tangent)
    control_points = np.array(control_points)
    new_axes,old_axes=get_new_and_old_axes(tangent,control_points)
    new_control_points = transform_coordinates(new_axes,old_axes,control_points)
    new_control_points -=  new_control_points[0]
    return new_control_points[2:]
def revert_to_original_plane(tangent,control_points,new_points):
    """
    Revert back to original 3D plane
    Returns only outer control points
    """
    tangent = np.array(tangent)
    control_points = np.array(control_points)
    new_axes,old_axes=get_new_and_old_axes(tangent,control_points)
    new_outer_points = transform_coordinates(old_axes,new_axes,new_points)
    new_outer_points += control_points[0]
    new_control_points = control_points.copy()
    new_control_points[2:]=new_outer_points
    new_control_points = [[c for c in b] for b in new_control_points]#to list
    return new_control_points
def normalize(vectors):
    return vectors / np.sqrt(np.sum(vectors**2,axis=-1))[...,np.newaxis]
def get_new_axes(tangent,control_points):
    center = control_points[0]
    first_point = control_points[2]
    new_xaxis = normalize(first_point-center)
    new_zaxis = tangent
    new_yaxis = -np.cross(new_xaxis,new_zaxis)
    new_axes  = np.array([new_xaxis, new_yaxis, new_zaxis])
    return new_axes
def get_old_axes():
    old_axes = np.array([[1, 0, 0],[0, 1, 0] , [0, 0, 1]], dtype=np.float32)
    return old_axes
def get_new_and_old_axes(tangent,control_points):
    new_axes = get_new_axes(tangent,control_points)
    old_axes = get_old_axes()
    return new_axes,old_axes
def transform_coordinates(new_axes,old_axes,points):
    transform_matrix = np.inner(new_axes,old_axes)
    return np.inner(points,transform_matrix)


#======================================================================================================
# Expanding/Collapsing in xy plane
def vary_points(outer_points,scale_factor):
    """
    Assumes centered at 0,0
    Expands contracts each control point by scale_factor
    (Scale factor is an array matching number of control points)
    Returns new points
    """
    dists,unit_vectors=get_dists_unit_vectors(outer_points)
    new_points = radial_expansion(outer_points,dists,unit_vectors,scale_factor)
    return new_points


def radial_expansion(new_outer_points,dists,unit_vectors,scale_factor):
    temp_outer_points = new_outer_points.copy()
    new_dists = dists * scale_factor
    new_points = unit_vectors * new_dists[...,np.newaxis]
    return new_points
    
def get_dists_unit_vectors(new_outer_points):
    dists = np.linalg.norm(new_outer_points,axis=-1)
    unit_vectors = new_outer_points/ dists[...,np.newaxis]
    return dists,unit_vectors


def vary_points_test(center,outer_points,scale_factor):
    dists,unit_vectors=get_dists_unit_vectors_test(center,outer_points)
    new_points = radial_expansion_test(center,outer_points,dists,unit_vectors,scale_factor)
    return new_points


def radial_expansion_test(center,new_outer_points,dists,unit_vectors,scale_factor):
    temp_outer_points = new_outer_points.copy()
    new_dists = dists * scale_factor
    new_points = unit_vectors * new_dists[...,np.newaxis] + center
    return new_points
def get_dists_unit_vectors_test(center,new_outer_points):
    dists = np.linalg.norm(new_outer_points-center,axis=-1)
    unit_vectors = (new_outer_points-center)/ dists[...,np.newaxis]
    return dists,unit_vectors
