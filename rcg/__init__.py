"""
RCG (RCareWorld Code Generation) Package
=========================================

This package contains test environments and utilities for RCareWorld development.

Main Components:
    - KinovaTestEnv: Test environment for Kinova robot with Unity Editor
    - create_test_env: Convenience function for quick environment setup

Example:
    from rcg.env import KinovaTestEnv

    env = KinovaTestEnv()
    env.step(100)
"""

from rcg.env import KinovaTestEnv, create_test_env

__all__ = ["KinovaTestEnv", "create_test_env"]
__version__ = "0.1.0"
