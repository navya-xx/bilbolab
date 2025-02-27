import copy
import dataclasses
import enum
import math
import pickle
import random
import time

import control
import matplotlib.pyplot as plt
import numpy as np
from numpy import nan

from extensions.simulation.src import core as core
from extensions.simulation.src.core import spaces as sp
from extensions.simulation.src.utils import lib_control
from extensions.simulation.src.utils.orientations import twiprToRotMat, twiprFromRotMat
from extensions.simulation.src.utils.babylon import setBabylonSettings


class BASE_ENVIRONMENT_ACTIONS(enum.StrEnum):
    INPUT = 'input'
    OBJECTS = 'objects'
    SENSORS = 'sensors'
    COMMUNICATION = 'communication'
    LOGIC = 'logic'
    DYNAMICS = 'dynamics'
    PHYSICS = 'physics'
    VISUALIZATION = 'visualization'
    OUTPUT = 'output'


class BaseEnvironment(core.environment.Environment):
    """
    A simple dynamic simulation world.
    It schedules various phases during each simulation cycle:
      - Input
      - Sensors
      - Communication
      - Logic
      - Dynamics
      - Physics Update
      - Collision
      - Additional Logic
      - Output
    """
    space = core.spaces.Space3D()
    # Ts = 0.02

    def __init__(self, Ts, run_mode, *args, **kwargs):
        super().__init__(Ts, run_mode, space=self.space, *args, **kwargs)
