"""
This module is an example of a barebones numpy reader plugin for napari.

It implements the Reader specification, but your plugin may choose to
implement multiple readers or even other plugin contributions. see:
https://napari.org/stable/plugins/guides.html?#readers
"""
import numpy as np
import os


def napari_get_reader(path):
    """A basic implementation of a Reader contribution.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    if os.path.isdir(path):
        path = [os.path.join(path, p) for p in os.listdir(path)]
    if not (isinstance(path, str) or isinstance(path, list)):
        # reader plugins may be handed single path, or a list of paths.
        # if it is a list, it is assumed to be an image stack...
        # so we are only going to look at the first file.
        return None

    if isinstance(path, list) and not all([isinstance(p, str) for p in path]):
        return None
    
    # if we know we cannot read the file, we immediately return None.
    if isinstance(path, str) and not path.endswith(".obj"):
        return None

    # otherwise we return the *function* that can read ``path``.
    return obj_reader


def obj_load(path):
    with open(path, "r") as f:
        data = f.readlines()
    vertices = []
    faces = []
    values = []
    init_value = 0
    try:
        for line in data:
            if line[0] == "v":
                vertices.append([eval(v) for v in line.strip().split()[1:]])
                values.append(init_value)
            elif line[0] == "f":
                faces.append([eval(v) - 1 for v in line.strip().split()[1:]])
            else:
                init_value += 1
    except Exception as e:
        print(
            (
                "Could not read the '.obj' file because of the following error:\n"
                f"{e}\n"
                "The '.obj' files are expected as text files following the wavefront .obj files file format"
            )
        )
        return None

    vertices = np.array(vertices)
    faces = np.array(faces)
    values = np.array(values)
    faces -= np.min(faces)
    surface = (vertices, faces, values)
    return surface


#create a new function with which we can load multiple objects
#iterate through files and add time dimension to vertices

def obj_list_load(path):

    #use obj load to load individual objects and concatenate them all into one object plus time dimension (stored in vertices)
    time = 0
    for p in path:
        if p.endswith(".obj"):
            vertices, faces, values = obj_load(p)
            #pad vertices with time dimension
            vertices_4d = np.pad(vertices, ((0, 0), (1, 0)), constant_values=time)
            if time == 0:
                vertices_4d_concat = vertices_4d
                faces_4d_concat = faces
                values_4d_concat = values

            else:
                #increase ids by amount of vertices in all former rounds (not this one) and concat faces
                faces += vertices_4d_concat.shape[0]
                faces_4d_concat = np.concatenate((faces_4d_concat, faces))
                #concat vertices arrays
                vertices_4d_concat = np.concatenate((vertices_4d_concat, vertices_4d))
                #concat value arrays
                values_4d_concat = np.concatenate((values_4d_concat, values))
            time += 1   
    surface = (vertices_4d_concat, faces_4d_concat, values_4d_concat)
    return surface


def obj_reader(path):
    """Take a path or list of paths and return a list of LayerData tuples.

    Readers are expected to return data as a list of tuples, where each tuple
    is (data, [add_kwargs, [layer_type]]), "add_kwargs" and "layer_type" are
    both optional.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        (data, metadata, layer_type), where data is a numpy array, metadata is
        a dict of keyword arguments for the corresponding viewer.add_* method
        in napari, and layer_type is a lower-case string naming the type of
        layer. Both "meta", and "layer_type" are optional. napari will
        default to layer_type=="image" if not provided
    """
    # optional kwargs for the corresponding viewer.add_* method
    add_kwargs = {
        "blending": "opaque",
        "shading": "smooth",
        "colormap": "twilight",
    }
    layer_type = "surface"  # optional, default is "image"


    if os.path.isdir(path):
        path = [os.path.join(path, p) for p in os.listdir(path)]
    # handle a string
    if isinstance(path, str):
        data = obj_load(path)
        output = [(data, add_kwargs, layer_type)]

    # handles a folder with several obj files
    else:
        #call function that combines all objectes into one 
        data = obj_list_load(path)
        output = [(data, add_kwargs, layer_type)]
    return output
