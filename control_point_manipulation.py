
import numpy as np


def to_numpy(lists):
    return [np.array(one_list,dtype=np.float32) for one_list in lists]
def to_lists_2d(arr):
    return [[float(c) for c in b] for b in arr]
def vary_points_test(center,outer_points,scale_factor):
    center,outer_points = to_numpy([center,outer_points])
    dists,unit_vectors=get_dists_unit_vectors_test(center,outer_points)
    new_points = radial_expansion_test(center,outer_points,dists,unit_vectors,scale_factor)
    new_points = to_lists_2d(new_points)
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


