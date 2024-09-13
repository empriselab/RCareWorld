import random
import subprocess
from abc import ABC
import socket
import numpy as np
import pyrcareworld
import pyrcareworld.attributes as attr
from pyrcareworld.side_channel import IncomingMessage, OutgoingMessage
from pyrcareworld.utils.rfuniverse_communicator import RFUniverseCommunicator
import os


class RCareWorld(ABC):
    """
    RCareWorld base environment class.

    :param executable_file: Str, the absolute path of the Unity executable file. Use None to use config.json; use "@editor" to use Unity Editor.
    :param scene_file: Str, the absolute path of the Unity scene JSON file. All JSON files are located at `<PlayerName>_Data/StreamingAssets/SceneData` by default. This is located in the build for the executable files.
    :param assets: List, the list of pre-loaded assets. All assets in the list will be pre-loaded in Unity when the environment is initialized, saving time during instantiation.
    :param graphics: Bool, True for showing the GUI and False for headless mode.
    :param port: Int, the port for communication.
    :param proc_id: Int, the process ID for the Unity environment. 0 for the first process, 1 for the second process, and so on.
    :param log_level: Int, the log level for the Unity environment. 0 for no log, 1 for error logs, 2 for warnings and errors, 3 for all logs.
    :param ext_attr: List, the list of extended attributes. All extended attributes will be added to the environment. (Deprecated in RCareWorld 1.5.0)
    :param check_version: Bool, True for checking the version of the Unity environment and the pyrcareworld library, False for not checking the version.
    """


    metadata = {"render.modes": ["human", "rgb_array"]}

    def __init__(
            self,
            executable_file: str = None,
            scene_file: str = None,
            assets: list = [],
            graphics: bool = True,
            port: int = 5004,
            proc_id=0,
            log_level=0,
            ext_attr: list = [],
            check_version: bool = False
    ):
        """
        Initialize the RCareWorld base environment class.

        :param executable_file: Str, the absolute path of the Unity executable file. Use None to use config.json; use "@editor" to use Unity Editor.
        :param scene_file: Str, the absolute path of the Unity scene JSON file. All JSON files are located at `<PlayerName>_Data/StreamingAssets/SceneData` by default. This is located in the build for the executable files.
        :param assets: List, the list of pre-loaded assets. All assets in the list will be pre-loaded in Unity when the environment is initialized, saving time during instantiation.
        :param graphics: Bool, True for showing the GUI and False for headless mode.
        :param port: Int, the port for communication.
        :param proc_id: Int, the process ID for the Unity environment. 0 for the first process, 1 for the second process, and so on.
        :param log_level: Int, the log level for the Unity environment. 0 for no log, 1 for error logs, 2 for warnings and errors, 3 for all logs.
        :param ext_attr: List, the list of extended attributes. All extended attributes will be added to the environment. (Deprecated in RCareWorld 1.5.0)
        :param check_version: Bool, True for checking the version of the Unity environment and the pyrcareworld library, False for not checking the version.
        """
        # time step
        self.t = 0
        self.graphics = graphics
        self.process = None
        self.attrs = {}
        self.data = {}
        self.listen_messages = {}
        self.listen_object = {}
        self.port = port
        self.check_version = check_version
        for i in ext_attr:
            if i.__name__ in attr.attrs:
                raise ValueError(f"ext_attr {i.__name__} already exists")
            attr.attrs[i.__name__] = i

        self.log_level = log_level

        self.log_map = {"Log": 3, "Warning": 2, "Error": 1, "Exception": 1, "Assert": 1}

        if executable_file is None:
            executable_file = pyrcareworld.executable_file

        if executable_file == "" or executable_file == "@editor":  # editor
            assert proc_id == 0, "proc_id must be 0 when using editor"
            print("Waiting for UnityEditor play...")
            PROC_TYPE = "editor"
        elif os.path.exists(executable_file):  # release
            PROC_TYPE = "release"
            self.port = self.port + 1 + proc_id  # default release port
        else:  # error
            raise ValueError(f"Executable file {executable_file} does not exist")

        self.communicator = RFUniverseCommunicator(
            port=self.port,
            receive_data_callback=self._receive_data,
            proc_type=PROC_TYPE,
        )
        self.port = self.communicator.port  # update port
        if PROC_TYPE == "release":
            self.process = self._start_unity_env(executable_file, self.port)
        self.communicator.online()
        self.WaitSceneInit()
        if len(assets) > 0:
            self.PreLoadAssetsAsync(assets, True)
        if scene_file is not None:
            self.LoadSceneAsync(scene_file, True)

    def __del__(self):
        self.close()

    def _get_port(self) -> int:
        executable_port = self.port + 1
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                s.bind(("localhost", executable_port))
                s.close()
                return executable_port
            except OSError:
                executable_port += 1
                continue

    def _start_unity_env(self, executable_file: str, port: int) -> subprocess.Popen:
        arg = [executable_file]
        if not self.graphics:
            arg.extend(["-nographics", "-batchmode"])
        if self.log_level == 0:
            proc_out = subprocess.DEVNULL
        else:
            proc_out = None
        arg.append(f"-port:{port}")
        return subprocess.Popen(arg, stdout=proc_out, stderr=proc_out)

    def _receive_data(self, objs: list) -> None:
        msg = objs[0]
        objs = objs[1:]
        if msg == "Env":
            self._parse_env_data(objs)
        elif msg == "Instance":
            self._parse_instance_data(objs)
        elif msg == "Debug":
            self._parse_debug_data(objs)
        elif msg == "Message":
            self._parse_message_data(objs)
        elif msg == "Object":
            self._parse_object_data(objs)
        return

    def _parse_env_data(self, objs: dict) -> None:
        self.data = objs[0]
        if "close" in self.data:
            self.close()

    def _parse_instance_data(self, objs: list) -> None:
        this_object_id = objs[0]
        this_object_type = objs[1]
        this_object_data = objs[2]

        try:
            attr_type = attr.attrs[this_object_type]
        except Exception as e:
            print(f"An error occurred: {e}")
            return

        if this_object_id not in self.attrs:
            self.attrs[this_object_id] = attr_type(self, this_object_id)
        elif type(self.attrs[this_object_id]) != attr_type:
            self.attrs[this_object_id] = attr_type(
                self, this_object_id, self.attrs[this_object_id].data
            )

        self.attrs[this_object_id].parse_message(this_object_data)

    def _parse_debug_data(self, objs: list) -> None:
        msg = objs[0]
        objs = objs[1:]
        if msg == "Log":
            if self.log_map[objs[0]] <= self.log_level:
                print(
                    f"Unity Env Log Type:{objs[0]}\nCondition:{objs[1]}\nStackTrace:{objs[2]}"
                )
        else:
            print(f"unknown debug data type: {msg}")
        return

    def _parse_message_data(self, objs: list) -> None:
        msg = objs[0]
        objs = objs[1:]
        if msg in self.listen_messages:
            self.listen_messages[msg](IncomingMessage(objs[0]))

    def _parse_object_data(self, objs: list) -> None:
        head = objs[0]
        objs = objs[1:]
        if head in self.listen_object:
            self.listen_object[head](objs)
        # else:
        # warnings.warn(f"unknown object data type: {head}")

    def _send_env_data(self, *args) -> None:
        self.communicator.send_object("Env", *args)

    def _send_physics_scene_data(self, *args) -> None:
        self.communicator.send_object("PhysicsScene", *args)

    def _send_instance_data(self, *args) -> None:
        self.communicator.send_object("Instance", *args)

    def _send_debug_data(self, *args) -> None:
        self.communicator.send_object("Debug", *args)

    def _send_message_data(self, *args) -> None:
        self.communicator.send_object("Message", *args)

    def _send_object_data(self, *args) -> None:
        self.communicator.send_object("Object", *args)

    def _step(self, count: int = 1, simulate: bool = True, collect: bool = True):
        """
        Send the messages of called functions to Unity and simulate for a step, then accept the data from Unity.

        :param count: Int, the number of steps for executing Unity simulation.
        :param simulate: Bool, True to simulate physics, False otherwise.
        :param collect: Bool, True to collect data, False otherwise.
        :raises Exception: If the Unity environment is not connected.
        """
        if not self.communicator.connected:
            raise Exception("Unity Env not connected")
        if count < 1:
            count = 1
        for i in range(count):
            if simulate:
                self.Simulate()
            if collect and i == count - 1:
                self.Collect()
            self.communicator.sync_step()


    def step(self, count: int = 1, simulate: bool = True, collect: bool = True):
        """
        Send the messages of called functions to Unity and simulate for a step, then accept the data from Unity.
        The difference of this function with `_step` is that this function is designed to be overwritten if there is a new class inherited from `RCareWorld`.

        :param count: Int, the number of steps for executing Unity simulation.
        :param simulate: Bool, True to simulate physics, False otherwise.
        :param collect: Bool, True to collect data, False otherwise.
        :raises Exception: If the Unity environment is not connected.
        """
        self._step(count, simulate, collect)

    def close(self):
        """
        Close the environment
        """
        if hasattr(self, "process") and self.process is not None:
            self.process.kill()
        if hasattr(self, "communicator") and self.communicator is not None:
            self.communicator.close()


    def Simulate(self, time_step: float = -1, count: int = 1):
        """
        Physics simulation.

        :param time_step: Float, the delta time of simulation per step. Default is -1.
        :param count: Int, the number of simulation steps. Default is 1.
        """
        self._send_env_data("Simulate", float(time_step), int(count))


    def Collect(self):
        """
        Collect environment data.
        """
        self._send_env_data("Collect")

    def GetAttr(self, id: int):
        """
        Get the attribute instance by object ID.

        :param id: Int, object ID.
        :return: pyrcareworld.attributes.BaseAttr, an instance of the attribute.
        :raises AssertionError: If the ID does not exist.
        """
        assert id in self.attrs, f"this ID: {id} does not exist"
        return self.attrs[id]

    # Env API
    def PreLoadAssetsAsync(self, names: list, auto_wait: bool = False) -> None:
        """
        Pre-load the assets.

        :param names: List, the names of assets.
        :param auto_wait: Bool, if True, this function will not return until the loading is done.
        """
        self._send_env_data("PreLoadAssetsAsync", names)

        if auto_wait:
            self.WaitLoadDone()

    def LoadSceneAsync(self, file: str, auto_wait: bool = False) -> None:
        """
        Load the scene asynchronously.

        :param file: Str, the scene JSON file. If it's a relative path, it will load from `StreamingAssets`.
        :param auto_wait: Bool, if True, this function will not return until the loading is done.
        """
        self._send_env_data("LoadSceneAsync", file)

        if auto_wait:
            self.WaitLoadDone()

    def SwitchSceneAsync(self, name: str, auto_wait: bool = False) -> None:
        """
        Switch the scene asynchronously.

        :param name: Str, the scene name.
        :param auto_wait: Bool, if True, this function will not return until the loading is done.
        """
        self._send_env_data("SwitchSceneAsync", name)

        if auto_wait:
            self.WaitSceneInit()

    def WaitSceneInit(self) -> None:
        """
        Wait for the scene initialization to be done.
        """
        while "scene_init" not in self.data:
            self._step(simulate=False)
        self.data.pop("scene_init")
        self._send_debug_data("SetPythonVersion", pyrcareworld.__version__)

    def WaitLoadDone(self) -> None:
        """
        Wait for the loading to be done.
        """
        while "load_done" not in self.data:
            self._step(simulate=False)
        self.data.pop("load_done")

    def Pend(self, simulate: bool = True, collect: bool = True) -> None:
        """
        Pend the program until the `EndPend` button in `UnityPlayer` is clicked.

        :param simulate: Bool, if True, simulate physics.
        :param collect: Bool, if True, collect data.
        """
        self._send_env_data("Pend")
        while "pend_done" not in self.data:
            self._step(simulate=simulate, collect=collect)
        self.data.pop("pend_done")

    def SendMessage(self, message: str, *args) -> None:
        """
        Send a message to Unity.

        :param message: Str, the message head.
        :param *args: List, the list of parameters. We support str, bool, int, float, and List[float] types.
        """
        msg = OutgoingMessage()
        for i in args:
            if isinstance(i, str):
                msg.write_string(i)
            elif isinstance(i, bool):
                msg.write_bool(i)
            elif isinstance(i, int):
                msg.write_int32(i)
            elif isinstance(i, (float, np.float32, np.float64)):
                msg.write_float32(float(i))
            elif isinstance(i, list) and isinstance(i[0], float):
                msg.write_float32_list(i)
            else:
                print(f"Don't support this data type: {type(i)}")
        self._send_message_data(message, msg.buffer)

    def SendObject(self, head: str, *args) -> None:
        """
        Send an object to Unity.

        :param head: Str, the message head.
        :param *args: List, the list of parameters. We support str, bool, int, float, and List[float] types.
        """
        self._send_object_data(head, *args)

    def AddListener(self, message: str, fun):
        """
        Add a listener.

        :param message: Str, the message head.
        :param fun: Callable, the callback function.
        """
        self.listen_messages[message] = fun

    def RemoveListener(self, message: str, fun):
        """
        Remove a listener.

        :param message: Str, the message head.
        :param fun: Callable, the callback function.
        """
        self.listen_messages.pop(message)

    def AddListenerObject(self, head: str, fun):
        """
        Add an object listener.

        :param head: Str, the message head.
        :param fun: Callable, the callback function.
        """
        self.listen_object[head] = fun

    def RemoveListenerObject(self, type: str):
        """
        Remove an object listener.

        :param type: Str, the message head.
        """
        self.listen_object.pop(type)

    def InstanceObject(self, name: str, id: int = None, attr_type: type = attr.BaseAttr):
        """
        Instantiate an object.

        Built-in assets:

        BaseAttr:
            - "Empty"

        GameObjectAttr:
            Basic Objects:
                - "GameObject_Box"
                - "GameObject_Capsule"
                - "GameObject_Cylinder"
                - "GameObject_Sphere"
                - "GameObject_Quad"
            IGbison Meshes:
                - "Hainesburg_mesh_texture"
                - "Halfway_mesh_texture"
                - "Hallettsville_mesh_texture"
                - "Hambleton_mesh_texture"
                - "Hammon_mesh_texture"
                - "Hatfield_mesh_texture"
                - "Haxtun_mesh_texture"
                - "Haymarket_mesh_texture"
                - "Hendrix_mesh_texture"
                - "Hercules_mesh_texture"
                - "Highspire_mesh_texture"
                - "Hitchland_mesh_texture"

        ColliderAttr:
            - "Collider_Box"
            - "Collider_ObiBox"
            - "Collider_Capsule"
            - "Collider_Cylinder"
            - "Collider_Sphere"
            - "Collider_Quad"

        RigidbodyAttr:
            Basic Objects:
                - "Rigidbody_Box"
                - "GameObject_Capsule"
                - "Rigidbody_Cylinder"
                - "Rigidbody_Sphere"
            YCB dataset:
                - 77 models in YCB dataset. See YCB Object and Model Set for detail: https://rse-lab.cs.washington.edu/projects/posecnn/

        ControllerAttr:
            Gripper:
                - "allegro_hand_right"
                - "bhand"
                - "svh"
                - "robotiq_arg2f_85_model"
                - "dh_robotics_ag95_gripper"
                - "shadowhand"
            Robot arm:
                - "kinova_gen3"
                - "ur5"
                - "flexivArm"
                - "tobor_r300"
            Robot arm and gripper:
                - "franka_panda"
                - "kinova_gen3_robotiq85"
                - "ur5_robotiq85"
                - "tobor_r300_ag95_ag95"
                - "tobor_r300_robotiq85_robotiq85"
                - "flexivArm_ag95"
                - "yumi"

        CameraAttr:
            - "Camera"

        LightAttr:
            - "Light"

        PointCloudAttr:
            - "PointCloud"

        :param name: Str, object name. Please check the above `built-in assets` list for names.
        :param id: Int, object id.
        :param attr_type: type, the attribute type. This parameter helps the editor identify types/completion codes.
        :return: type(attr_type), the object attribute instance.
        :rtype: attr_type
        """
        assert id not in self.attrs, f"ID:{id} already exists"

        while id is None or id in self.attrs:
            id = random.randint(100000, 999999)

        self._send_env_data("InstanceObject", name, id)

        self.attrs[id] = attr_type(self, id)
        return self.attrs[id]


    def LoadURDF(self, path: str, id: int = None, native_ik: bool = False, axis: str = "y") -> attr.ControllerAttr:
        """
        Load a model from a URDF file.

        :param path: Str, the URDF file path.
        :param id: Int, object id.
        :param native_ik: Bool, True for enabling native IK; False for using custom IK. When True, use the IKTargetDo*** interface for end pose; when False, use the SetJoint*** interface for joint movement.
        :param axis: Str, import axis. This can be 'z' or 'y', depending on the URDF file.
        :return: pyrcareworld.attributes.ControllerAttr, the object attribute instance.
        """
        assert id not in self.attrs, "this ID exists"

        while id is None or id in self.attrs:
            id = random.randint(100000, 999999)

        self._send_env_data("LoadURDF", id, path, native_ik, axis)

        self.attrs[id] = attr.ControllerAttr(self, id)
        return self.attrs[id]

    def LoadMesh(self, path: str, id: int = None, collider_mode: str = "VHACD") -> attr.RigidbodyAttr:
        """
        Load a model from a Mesh file.

        :param path: Str, the Mesh file path.
        :param id: Int, object id.
        :param collider_mode: Str, how to generate collisions for the model. Can be "VHACD"/"CoACD"/"Convex"/Any other is None Collider.
        :return: pyrcareworld.attributes.RigidbodyAttr, the object attribute instance.
        """
        assert id not in self.attrs, "this ID exists"

        while id is None or id in self.attrs:
            id = random.randint(100000, 999999)

        self._send_env_data("LoadMesh", id, path, True, collider_mode)

        self.attrs[id] = attr.RigidbodyAttr(self, id)
        return self.attrs[id]

    def IgnoreLayerCollision(self, layer1: int, layer2: int, ignore: bool) -> None:
        """
        Ignore or enable the collision between two layers.

        :param layer1: Int, the layer number of the first layer.
        :param layer2: Int, the layer number of the second layer.
        :param ignore: Bool, True for ignoring collision between two layers; False for enabling collision between two layers.
        """
        self._send_env_data("IgnoreLayerCollision", layer1, layer2, ignore)

    def GetCurrentCollisionPairs(self) -> None:
        """
        Get the collision pairs of current collisions. After calling this method and stepping once, the result will be saved in env.data['CurrentCollisionPairs'].
        """
        self._send_env_data("GetCurrentCollisionPairs")

    def GetRFMoveColliders(self) -> None:
        """
        Get the RFMove colliders. After calling this method and stepping once, the result will be saved in env.data['RFMoveColliders'].
        """
        self._send_env_data("GetRFMoveColliders")

    def SetGravity(self, x: float, y: float, z: float) -> None:
        """
        Set the gravity of the environment.

        :param x: Float, gravity on the global x-axis (right).
        :param y: Float, gravity on the global y-axis (up).
        :param z: Float, gravity on the global z-axis (forward).
        """
        self._send_env_data("SetGravity", [float(x), float(y), float(z)])

    def SetGroundActive(self, active: bool) -> None:
        """
        Set the ground to be active or inactive.

        :param active: Bool, active or inactive the ground.
        """
        self._send_env_data("SetGroundActive", active)

    def SetGroundPhysicMaterial(self, bounciness: float, dynamic_friction: float, static_friction: float, friction_combine: int, bounce_combine: int) -> None:
        """
        Set the physics material of the ground in the environment.

        :param bounciness: Float, the bounciness.
        :param dynamic_friction: Float, the dynamic friction coefficient (0-1).
        :param static_friction: Float, the static friction coefficient (0-1).
        :param friction_combine: Int, how friction of two colliding objects is combined. 0 for Average, 1 for Minimum, 2 for Maximum and 3 for Multiply. See https://docs.unity3d.com/Manual/class-PhysicMaterial.html for more details.
        :param bounce_combine: Int, how bounciness of two colliding objects is combined. The value representation is the same as `friction_combine`.
        """
        self._send_env_data(
            "SetGroundPhysicMaterial",
            float(bounciness),
            float(dynamic_friction),
            float(static_friction),
            friction_combine,
            bounce_combine,
        )

    def SetTimeStep(self, delta_time: float) -> None:
        """
        Set the time for a step in Unity.

        :param delta_time: Float, the time for a step in Unity.
        """
        self._send_env_data("SetTimeStep", float(delta_time))

    def SetTimeScale(self, time_scale: float) -> None:
        """
        Set the time scale in Unity.

        :param time_scale: Float, the time scale in Unity.
        """
        self._send_env_data("SetTimeScale", float(time_scale))

    def SetResolution(self, resolution_x: int, resolution_y: int) -> None:
        """
        Set the resolution of the windowed GUI.

        :param resolution_x: Int, window width.
        :param resolution_y: Int, window height.
        """
        self._send_env_data("SetResolution", resolution_x, resolution_y)

    def ExportOBJ(self, items_id: list, save_path: str) -> None:
        """
        Export the specified object list to an OBJ file. For native bundle models, the `Read/Write` must be checked in Unity Editor.

        :param items_id: List, the object ids.
        :param save_path: Str, the path to save the OBJ files.
        """
        self._send_env_data("ExportOBJ", items_id, save_path)

    def SetShadowDistance(self, distance: float) -> None:
        """
        Set the shadow distance for rendering in the environment.

        :param distance: Float, the shadow distance measured in meters.
        """
        self._send_env_data("SetShadowDistance", float(distance))

    def SaveScene(self, file: str) -> None:
        """
        Save the current scene.

        :param file: Str, the file path to save the current scene. Default saving to the `StreamingAssets` folder.
        """
        self._send_env_data("SaveScene", file)

    def ClearScene(self) -> None:
        """
        Clear the current scene.
        """
        self._send_env_data("ClearScene")

    def AlignCamera(self, camera_id: int) -> None:
        """
        Align the current GUI view to a given camera.

        :param camera_id: Int, camera id.
        """
        self._send_env_data("AlignCamera", camera_id)

    def SetViewTransform(self, position: list = None, rotation: list = None) -> None:
        """
        Set the GUI view.

        :param position: A list of length 3, representing the position of the GUI view.
        :param rotation: A list of length 3, representing the rotation of the GUI view.
        """
        if position is not None:
            assert type(position) == list and len(position) == 3, "Argument position must be a 3-d list."
            position = [float(i) for i in position]
        if rotation is not None:
            assert type(rotation) == list and len(rotation) == 3, "Argument rotation must be a 3-d list."
            rotation = [float(i) for i in rotation]

        self._send_env_data("SetViewTransform", position, rotation)

    def GetViewTransform(self) -> None:
        """
        Get the GUI view transform.

        After calling this method and stepping once, the result will be saved in env.data['view_position'] / env.data['view_rotation'] / env.data['view_quaternion'].
        """
        self._send_env_data("GetViewTransform")

    def ViewLookAt(self, target: list, world_up: list = None) -> None:
        """
        Rotate the transform so the forward vector points at the target's current position.

        :param target: A list of length 3, target to point towards.
        :param world_up: A list of length 3, vector specifying the upward direction.
        """
        if world_up is None:
            world_up = [0.0, 1.0, 0.0]
        assert len(target) == 3, "target length must be 3"
        target = [float(i) for i in target]
        assert len(world_up) == 3, "world_up length must be 3"
        world_up = [float(i) for i in world_up]

        self._send_env_data("ViewLookAt", target, world_up)

    def SetViewBackGround(self, color: list = None) -> None:
        """
        Set the GUI view background.

        :param color: A list of length 3, background color of the GUI view. None: default skybox.
        """
        if color is not None:
            assert type(color) == list and len(color) == 3, "color length must be 3"
            color = [float(i) for i in color]

        self._send_env_data("SetViewBackGround", color)

    def LoadCloth(self, path: str, id: int = None) -> attr.ClothAttr:
        """
        Load a mesh to Cloth.

        :param path: Str, the Mesh file path.
        :param id: Int, object id.
        :return: pyrcareworld.attributes.ClothAttr, the cloth attribute instance.
        """
        assert id not in self.attrs, "this ID exists"

        while id is None or id in self.attrs:
            id = random.randint(100000, 999999)

        self._send_env_data("LoadCloth", path, int(id))

        self.attrs[id] = attr.ClothAttr(self, id)
        return self.attrs[id]

    def EnabledGroundObiCollider(self, enabled: bool) -> None:
        """
        Enable or disable the Ground ObiCollider.

        :param enabled: Bool, the Ground ObiCollider enabled.
        """
        self._send_env_data("EnabledGroundObiCollider", enabled)

    # Debug API
    def DebugGraspPoint(self, enabled: bool = True) -> None:
        """
        Show or hide the end effector of the robot arm for debugging.

        :param enabled: Bool, True for showing and False for hiding.
        """
        self._send_debug_data("DebugGraspPoint", enabled)

    def DebugObjectPose(self, enabled: bool = True) -> None:
        """
        Show or hide the object base point for debugging.

        :param enabled: Bool, True for showing and False for hiding.
        """
        self._send_debug_data("DebugObjectPose", enabled)

    def DebugCollisionPair(self, enabled: bool = True) -> None:
        """
        Show or hide collision pairs for debugging.

        :param enabled: Bool, True for showing and False for hiding.
        """
        self._send_debug_data("DebugCollisionPair", enabled)

    def DebugColliderBound(self, enabled: bool = True) -> None:
        """
        Show or hide the collider bounding box for debugging.

        :param enabled: Bool, True for showing and False for hiding.
        """
        self._send_debug_data("DebugColliderBound", enabled)

    def DebugObjectID(self, enabled: bool = True) -> None:
        """
        Show or hide the object ID for debugging.

        :param enabled: Bool, True for showing and False for hiding.
        """
        self._send_debug_data("DebugObjectID", enabled)

    def Debug3DBBox(self, enabled: bool = True) -> None:
        """
        Show or hide the 3D bounding box of objects for debugging.

        :param enabled: Bool, True for showing and False for hiding.
        """
        self._send_debug_data("Debug3DBBox", enabled)

    def Debug2DBBox(self, enabled: bool = True) -> None:
        """
        Show or hide the 2D bounding box of objects for debugging.

        :param enabled: Bool, True for showing and False for hiding.
        """
        self._send_debug_data("Debug2DBBox", enabled)

    def DebugJointLink(self, enabled: bool = True) -> None:
        """
        Show or hide joint information of articulation for debugging.

        :param enabled: Bool, True for showing and False for hiding.
        """
        self._send_debug_data("DebugJointLink", enabled)

    def SendLog(self, log: str) -> None:
        """
        Send a log message and show it on the Unity GUI window.

        :param log: Str, log message.
        """
        self._send_debug_data("SendLog", log)

    def ShowArticulationParameter(self, controller_id: int) -> None:
        """
        Show Articulation Parameter on the Unity GUI window.

        :param controller_id: int, controller_attr id.
        """
        self._send_debug_data("ShowArticulationParameter", int(controller_id))

    def NewPhysicsScene(self, physics_scene_id: int) -> None:
        """
        Place all current scene objects into the new physics scene, and all objects are prefixed with the ID of the physical scene.

        :param physics_scene_id: int, physics scene id.
        """
        self._send_physics_scene_data("NewPhysicsScene", int(physics_scene_id))

    def CopyPhysicsScene(self, new_id: int, copy_id: int) -> None:
        """
        Copy a physics scene.

        :param new_id: int, new physics scene id.
        :param copy_id: int, copy physics scene id.
        """
        self._send_physics_scene_data("CopyPhysicsScene", int(new_id), int(copy_id))

    def SimulatePhysicsScene(self, physics_scene_id: int, time_step: float = -1, count: int = 1) -> None:
        """
        Physics scene simulation.

        :param physics_scene_id: int, physics scene id.
        :param time_step: Float, delta time of simulation per step.
        :param count: Int, count of simulations.
        """
        self._send_physics_scene_data("SimulatePhysicsScene", int(physics_scene_id), float(time_step), int(count))
