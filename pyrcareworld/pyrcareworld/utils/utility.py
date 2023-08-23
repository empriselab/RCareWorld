import math
import numpy as np


def EncodeIDAsColor(instance_id: int):
    """
    Encode the object id to a color.

    Args:
        instance_id: Int, the id of the object.

    Return:
        List: The encoded color in [r, g, b, 255] format.
    """
    r = (instance_id * 16807 + 187) % 256
    g = (instance_id * 48271 + 79) % 256
    b = (instance_id * 95849 + 233) % 256
    return [r, g, b, 255]


def UnityEularToQuaternion(eular: list) -> list:
    """
    Transform euler angle to quaternion in Unity.

    Args:
        eular: List of length 3, representing euler angle in [x, y, z]
        order and measured in degree.

    Return:
        List: The transformed quaternion in [x, y, z, w] format.
    """
    xx = math.radians(eular[0])
    yy = math.radians(eular[1])
    zz = math.radians(eular[2])
    x = math.cos(yy / 2) * math.sin(xx / 2) * math.cos(zz / 2) + math.sin(
        yy / 2
    ) * math.cos(xx / 2) * math.sin(zz / 2)
    y = math.sin(yy / 2) * math.cos(xx / 2) * math.cos(zz / 2) - math.cos(
        yy / 2
    ) * math.sin(xx / 2) * math.sin(zz / 2)
    z = math.cos(yy / 2) * math.cos(xx / 2) * math.sin(zz / 2) - math.sin(
        yy / 2
    ) * math.sin(xx / 2) * math.cos(zz / 2)
    w = math.cos(yy / 2) * math.cos(xx / 2) * math.cos(zz / 2) + math.sin(
        yy / 2
    ) * math.sin(xx / 2) * math.sin(zz / 2)
    return [x, y, z, w]


def UnityQuaternionToEular(quaternion: list) -> list:
    """
    Transform quaternion to euler angle in Unity.

    Args:
        quaternion: List of length 4, representing quaternion in [x, y, z, w]
        order.

    Return:
        List: The transformed euler angle in [x, y, z] order and measured in degree.
    """
    xx = quaternion[0]
    yy = quaternion[1]
    zz = quaternion[2]
    ww = quaternion[3]
    x = math.asin(2 * ww * xx - 2 * yy * zz)
    y = math.atan2(2 * ww * yy + 2 * xx * zz, 1 - 2 * xx * xx - 2 * yy * yy)
    z = math.atan2(2 * ww * zz + 2 * xx * yy, 1 - 2 * xx * xx - 2 * zz * zz)
    x = math.degrees(x)
    y = math.degrees(y)
    z = math.degrees(z)
    return [x, y, z]


def CheckKwargs(kwargs: dict, compulsory_params: list):
    legal = True
    for param in compulsory_params:
        if param not in kwargs.keys():
            legal = False
            assert legal, "Parameters illegal, parameter <%s> missing." % param


def GetMatrix(pos, quat) -> np.ndarray:
    """
    Transform the position and quaternion into a transformation matrix.

    Args:
        pos: List of length 3, representing the [x, y, z] position.
        quat: List of length 4, representing the [x, y, z, w] quaternion.

    Return:
        numpy.ndarray: the transformation matrix.
    """
    q = quat.copy()
    n = np.dot(q, q)
    if n < np.finfo(q.dtype).eps:
        return np.identity(4)
    q = q * np.sqrt(2.0 / n)
    q = np.outer(q, q)
    # rot_matrix = np.array(
    #     [[1.0 - q[2, 2] - q[3, 3], q[1, 2] + q[3, 0], q[1, 3] - q[2, 0], pos[0]],
    #      [q[1, 2] - q[3, 0], 1.0 - q[1, 1] - q[3, 3], q[2, 3] + q[1, 0], pos[1]],
    #      [q[1, 3] + q[2, 0], q[2, 3] - q[1, 0], 1.0 - q[1, 1] - q[2, 2], pos[2]],
    #      [0, 0, 0, 1.0]], dtype=q.dtype)
    matrix = np.array(
        [
            [1.0 - q[1, 1] - q[2, 2], -(q[2, 3] - q[1, 0]), q[1, 3] + q[2, 0], pos[0]],
            [q[2, 3] + q[1, 0], -(1.0 - q[1, 1] - q[3, 3]), q[1, 2] - q[3, 0], pos[1]],
            [
                -(q[1, 3] - q[2, 0]),
                q[1, 2] + q[3, 0],
                -(1.0 - q[2, 2] - q[3, 3]),
                pos[2],
            ],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=float,
    )
    return matrix
