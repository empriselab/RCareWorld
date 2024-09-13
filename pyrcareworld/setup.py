from setuptools import setup
from setuptools import find_packages
import pyrcareworld

VERSION = pyrcareworld.__version__

setup(
    name="pyrcareworld",
    version=VERSION,
    description="rcareworld python interface",
    url="https://github.com/empriselab/RCareWorld",
    author="RCareWorld",
    install_requires=[
        "numpy>=1.14.1",
        "opencv-contrib-python",
        "requests"
    ],
    entry_points={
        'console_scripts': [
            'pyrcareworld=pyrcareworld.entry_points:pyrcareworld_entry_points',
        ]
    }
)
