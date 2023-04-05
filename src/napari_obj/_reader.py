"""
This module is an example of a barebones numpy reader plugin for napari.

It implements the Reader specification, but your plugin may choose to
implement multiple readers or even other plugin contributions. see:
https://napari.org/stable/plugins/guides.html?#readers
"""
import numpy as np


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
    if not isinstance(path, str):
        # reader plugins may be handed single path, or a list of paths.
        # if it is a list, it is assumed to be an image stack...
        # so we are only going to look at the first file.
        return None

    # if we know we cannot read the file, we immediately return None.
    if not path.endswith(".obj"):
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
    # handle both a string and a list of strings
    data = obj_load(path)

    # optional kwargs for the corresponding viewer.add_* method
    add_kwargs = {
        "blending": "opaque",
        "shading": "smooth",
        "colormap": "twilight",
    }

    layer_type = "surface"  # optional, default is "image"
    return [(data, add_kwargs, layer_type)]
