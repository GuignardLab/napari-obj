import numpy as np

from napari_obj import napari_get_reader


# tmp_path is a pytest fixture
def test_reader(tmp_path):
    """An example of how you might test your plugin."""

    # write some fake data using your supported file format
    my_test_file = str(tmp_path / "myfile.obj")
    vertices = np.array([[0, 0], [0, 20], [10, 0], [10, 10]])
    faces = np.array([[0, 1, 2], [1, 2, 3]])
    values = [
        0,
    ] * len(vertices)
    init_data = (vertices, faces, values)
    with open(my_test_file, "w") as file:
        for v in vertices:
            file.write(f"v {v[0]} {v[1]}\n")
        for f in faces:
            file.write(f"f {f[0]} {f[1]} {f[2]}\n")

    # try to read it back in
    reader = napari_get_reader(my_test_file)
    assert callable(reader)

    # make sure we're delivering the right format
    layer_data_list = reader(my_test_file)
    assert isinstance(layer_data_list, list) and len(layer_data_list) > 0
    layer_data_tuple = layer_data_list[0]
    assert isinstance(layer_data_tuple, tuple) and len(layer_data_tuple) > 0

    # make sure it's the same as it started
    np.testing.assert_allclose(init_data[0], layer_data_tuple[0][0])
    np.testing.assert_allclose(init_data[1], layer_data_tuple[0][1])
    np.testing.assert_allclose(init_data[2], layer_data_tuple[0][2])


def test_reader2(tmp_path):
    """An example of how you might test your plugin."""

    # write some fake data using your supported file format
    my_test_file = str(tmp_path / "myfile.obj")
    vertices = np.array([[0, 0], [0, 20], [10, 0], [10, 10]])
    faces = np.array([[1, 2, 3], [2, 3, 4]])
    values = [
        0,
    ] * len(vertices)
    init_data = (vertices, faces, values)
    with open(my_test_file, "w") as file:
        for v in vertices:
            file.write(f"v {v[0]} {v[1]}\n")
        for f in faces:
            file.write(f"f {f[0]} {f[1]} {f[2]}\n")

    # try to read it back in
    reader = napari_get_reader(my_test_file)
    assert callable(reader)

    # make sure we're delivering the right format
    layer_data_list = reader(my_test_file)
    assert isinstance(layer_data_list, list) and len(layer_data_list) > 0
    layer_data_tuple = layer_data_list[0]
    assert isinstance(layer_data_tuple, tuple) and len(layer_data_tuple) > 0

    # make sure it's the same as it started
    np.testing.assert_allclose(init_data[0], layer_data_tuple[0][0])
    np.testing.assert_allclose(init_data[1] - 1, layer_data_tuple[0][1])
    np.testing.assert_allclose(init_data[2], layer_data_tuple[0][2])


def test_get_reader_pass():
    reader = napari_get_reader("fake.file")
    assert reader is None
