"""
Tests for helper angle functions.

NOTE: run this file with pytest -s tests/test_angle_functions.py.
"""

import pytest
import numpy as np

def degrees_to_radians(angle):
    """
    Convert from degrees to radians.
    
    Args:
        angle: Float, angle in degrees.
    Return:
        Float, angle in radians.
    """
    return np.pi * angle / 180

def test_degrees_to_radians():
    assert degrees_to_radians(0) == 0
    assert degrees_to_radians(90) == np.pi / 2
    assert degrees_to_radians(-90) == -np.pi / 2
    assert degrees_to_radians(180) == np.pi
    assert degrees_to_radians(-180) == -np.pi
    assert np.allclose(degrees_to_radians(200), 3.49066, atol=1e-6)

def wrap_angle(angle):
    """
    Wrap an angle in radians to [-pi, pi].
    
    Args:
        angle: Float, angle in radians.
    Return:
        Float, angle in radians, clamped to [-pi, pi].
    """
    return np.arctan2(np.sin(angle), np.cos(angle))

def test_wrap_angle():
    assert np.allclose(wrap_angle(0), 0, atol=1e-6)
    assert np.allclose(wrap_angle(2 * np.pi), 0, atol=1e-6)
    assert np.allclose(wrap_angle(-2 * np.pi), 0, atol=1e-6)
    assert np.allclose(wrap_angle(3.5 * np.pi), -0.5 * np.pi, atol=1e-6)


def get_signed_angle_distance(source, target):
    """
    Given two angles between [-pi, pi], get the smallest signed angle d s.t.
    source + d = target.

    Args:
        source: Float, source angle in radians, in the range [-pi, pi].
        target: Float, target angle in radians, in the range [-pi, pi].
    Return:
        Float, the smallest signed angle from source to target.
    """
    assert -np.pi <= source <= np.pi
    assert -np.pi <= target <= np.pi
    a = target - source
    
    if a > np.pi:
        a = a - 2 * np.pi
    elif a < -np.pi:
        a = a + 2 * np.pi
    return a

def test_get_signed_angle_distance():
    assert np.allclose(get_signed_angle_distance(0, 0), 0, atol=1e-6)
    assert np.allclose(get_signed_angle_distance(0, 3/4 * np.pi), 3/4 * np.pi, atol=1e-6)
    assert np.allclose(get_signed_angle_distance(0, 3/4 * -np.pi), 3/4 * -np.pi, atol=1e-6)
    assert np.allclose(get_signed_angle_distance(-np.pi * 3/4, 3/4 * np.pi), -1/2 * np.pi, atol=1e-6)


def euler_angles_allclose(euler1, euler2, atol = 1e-6):
    """
    Compare two euler angles.

    Args:
        euler1: List, first euler angles in the form [yaw, pitch, roll] in degrees.
        euler2: List, second euler angles in the form [yaw, pitch, roll] in degrees.
        atol: Float, absolute tolerance, in degrees.

    Return:
        Bool, True if the two euler angles are close, False otherwise.
    """
    wrapped_angles1 = [wrap_angle(degrees_to_radians(a)) for a in euler1]
    wrapped_angles2 = [wrap_angle(degrees_to_radians(a)) for a in euler2]
    dists = [get_signed_angle_distance(a, b)
             for a, b in zip(wrapped_angles1, wrapped_angles2)]
    return np.allclose(dists, 0, atol=degrees_to_radians(atol))

def test_euler_angles_allclose():
    assert euler_angles_allclose([0, 0, 0], [0, 0, 0])
    assert not euler_angles_allclose([0, 0, 0], [0, 0, 90]) 
    assert not euler_angles_allclose([0, 0, 0], [0, 0, 180])
    assert euler_angles_allclose([0, 0, 0], [0, 360, 360])
    assert not euler_angles_allclose([0, 0, 250], [0, 250, 0])

    # Test close enough.
    assert euler_angles_allclose([0, 9, 0], [0, 10, 0], atol=10)
    assert euler_angles_allclose([0, 9, 0], [0, 18, 0], atol=10)
    assert euler_angles_allclose([0, 18, 0], [0, 9, 0], atol=10)
    assert euler_angles_allclose([0, 0, 0], [0, 355, 0], atol=10)
    assert euler_angles_allclose([0, 355, 0], [0, 4, 0], atol=10)

    # Test not close enough.
    assert not euler_angles_allclose([0, 9, 0], [0, 10, 0], atol=.1)
    assert not euler_angles_allclose([0, 90, 0], [0, 18, 0], atol=10)
    assert not euler_angles_allclose([0, 320, 0], [0, 4, 0], atol=10)
