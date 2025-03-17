import pytest
from pyrcareworld.attributes.base_attr import BaseAttr

# A dummy environment class to test BaseAttr methods.
class DummyEnv:
    def __init__(self):
        self.calls = []
        self.attrs = {}
        self.step_count = 0

    def _send_instance_data(self, id, message, *args):
        self.calls.append((id, message, args))

    def _step(self):
        self.step_count += 1

@pytest.fixture
def dummy_env():
    return DummyEnv()

@pytest.fixture
def base_attr_instance(dummy_env):
    # Set initial data with keys needed for WaitDo so it doesn't loop infinitely.
    return BaseAttr(dummy_env, id=1, data={'move_done': True, 'rotate_done': True})

# A dummy attribute type for testing SetType
class DummyAttr(BaseAttr):
    pass

# A dummy attribute type for testing SetType
class DummyAttr(BaseAttr):
    pass

def test_parse_message(base_attr_instance):
    test_data = {'name': 'TestObject', 'position': [1, 2, 3]}
    base_attr_instance.parse_message(test_data)
    assert base_attr_instance.data == test_data

def test_set_type(base_attr_instance, dummy_env):
    # Initially, the env should not contain the id.
    assert 1 not in dummy_env.attrs
    returned_attr = base_attr_instance.SetType(DummyAttr)
    # Check that the returned object is an instance of DummyAttr.
    assert isinstance(returned_attr, DummyAttr)
    # Check that the environment now has the attribute registered.
    assert 1 in dummy_env.attrs
    assert isinstance(dummy_env.attrs[1], DummyAttr)

def test_set_transform(base_attr_instance, dummy_env):
    dummy_env.calls.clear()
    pos = [1, 2, 3]
    rot = [10, 20, 30]
    scale = [1, 1, 1]
    is_world = False
    base_attr_instance.SetTransform(position=pos, rotation=rot, scale=scale, is_world=is_world)
    assert len(dummy_env.calls) == 1
    id_sent, message, args = dummy_env.calls[0]
    assert id_sent == 1
    assert message == "SetTransform"
    expected_args = ([float(i) for i in pos],
                     [float(i) for i in rot],
                     [float(i) for i in scale],
                     is_world)
    assert args == expected_args

def test_set_transform_invalid_length(base_attr_instance):
    with pytest.raises(AssertionError):
        base_attr_instance.SetTransform(position=[1, 2], rotation=[10, 20, 30], scale=[1, 1, 1])
    with pytest.raises(AssertionError):
        base_attr_instance.SetTransform(position=[1, 2, 3], rotation=[10, 20], scale=[1, 1, 1])
    with pytest.raises(AssertionError):
        base_attr_instance.SetTransform(position=[1, 2, 3], rotation=[10, 20, 30], scale=[1, 1])

def test_set_position(base_attr_instance, dummy_env):
    dummy_env.calls.clear()
    pos = [4, 5, 6]
    base_attr_instance.SetPosition(pos, is_world=True)
    assert len(dummy_env.calls) == 1
    id_sent, message, args = dummy_env.calls[0]
    assert id_sent == 1
    assert message == "SetPosition"
    expected_args = ([float(i) for i in pos], True)
    assert args == tuple(expected_args)
    
def test_set_position_invalid_length(base_attr_instance):
    with pytest.raises(AssertionError):
        base_attr_instance.SetPosition([1, 2])

def test_set_rotation(base_attr_instance, dummy_env):
    dummy_env.calls.clear()
    rot = [15, 30, 45]
    base_attr_instance.SetRotation(rot, is_world=False)
    assert len(dummy_env.calls) == 1
    id_sent, message, args = dummy_env.calls[0]
    assert message == "SetRotation"
    expected_args = ([float(i) for i in rot], False)
    assert args == tuple(expected_args)

def test_set_rotation_invalid_length(base_attr_instance):
    with pytest.raises(AssertionError):
        base_attr_instance.SetRotation([1, 2], is_world=True)

def test_set_rotation_quaternion(base_attr_instance, dummy_env):
    dummy_env.calls.clear()
    quat = [0, 0, 0, 1]
    base_attr_instance.SetRotationQuaternion(quat, is_world=True)
    assert len(dummy_env.calls) == 1
    id_sent, message, args = dummy_env.calls[0]
    assert message == "SetRotationQuaternion"
    expected_args = ([float(i) for i in quat], True)
    assert args == tuple(expected_args)

def test_set_rotation_quaternion_invalid_length(base_attr_instance):
    with pytest.raises(AssertionError):
        base_attr_instance.SetRotationQuaternion([0, 0, 1], is_world=True)

def test_set_scale(base_attr_instance, dummy_env):
    dummy_env.calls.clear()
    scale = [2, 2, 2]
    base_attr_instance.SetScale(scale)
    assert len(dummy_env.calls) == 1
    id_sent, message, args = dummy_env.calls[0]
    assert message == "SetScale"
    expected_args = ([float(i) for i in scale],)
    assert args == expected_args

def test_set_scale_invalid_length(base_attr_instance):
    with pytest.raises(AssertionError):
        base_attr_instance.SetScale([1, 2])

def test_translate(base_attr_instance, dummy_env):
    dummy_env.calls.clear()
    translation = [7, 8, 9]
    base_attr_instance.Translate(translation, is_world=False)
    assert len(dummy_env.calls) == 1
    id_sent, message, args = dummy_env.calls[0]
    assert message == "Translate"
    expected_args = ([float(i) for i in translation], False)
    assert args == tuple(expected_args)

def test_rotate(base_attr_instance, dummy_env):
    dummy_env.calls.clear()
    rot = [5, 10, 15]
    base_attr_instance.Rotate(rot, is_world=True)
    assert len(dummy_env.calls) == 1
    id_sent, message, args = dummy_env.calls[0]
    assert message == "Rotate"
    expected_args = ([float(i) for i in rot], True)
    assert args == tuple(expected_args)

def test_look_at(base_attr_instance, dummy_env):
    dummy_env.calls.clear()
    target = [1, 0, 0]
    world_up = [0, 1, 0]
    base_attr_instance.LookAt(target, world_up)
    assert len(dummy_env.calls) == 1
    id_sent, message, args = dummy_env.calls[0]
    assert message == "LookAt"
    expected_args = ([float(i) for i in target], [float(i) for i in world_up])
    assert args == tuple(expected_args)

def test_look_at_default_world_up(base_attr_instance, dummy_env):
    dummy_env.calls.clear()
    target = [1, 2, 3]
    base_attr_instance.LookAt(target)
    assert len(dummy_env.calls) == 1
    id_sent, message, args = dummy_env.calls[0]
    assert message == "LookAt"
    expected_args = ([float(i) for i in target], [0.0, 1.0, 0.0])
    assert args == tuple(expected_args)

def test_set_active(base_attr_instance, dummy_env):
    dummy_env.calls.clear()
    base_attr_instance.SetActive(True)
    assert len(dummy_env.calls) == 1
    id_sent, message, args = dummy_env.calls[0]
    assert message == "SetActive"
    expected_args = (True,)
    assert args == expected_args

def test_set_parent(base_attr_instance, dummy_env):
    dummy_env.calls.clear()
    parent_id = 10
    parent_name = "ParentObj"
    base_attr_instance.SetParent(parent_id, parent_name)
    assert len(dummy_env.calls) == 1
    id_sent, message, args = dummy_env.calls[0]
    assert message == "SetParent"
    expected_args = (parent_id, parent_name)
    assert args == expected_args

def test_set_layer(base_attr_instance, dummy_env):
    dummy_env.calls.clear()
    layer = 5
    base_attr_instance.SetLayer(layer)
    assert len(dummy_env.calls) == 1
    id_sent, message, args = dummy_env.calls[0]
    assert message == "SetLayer"
    expected_args = (layer,)
    assert args == expected_args

def test_copy_and_destroy(dummy_env):
    # Create a BaseAttr instance with id 2.
    base = BaseAttr(dummy_env, id=2, data={'key': 'value'})
    dummy_env.attrs[2] = base
    # Test Copy: duplicate to new id 3.
    new_id = 3
    dummy_env.calls.clear()
    copy_instance = base.Copy(new_id)
    assert len(dummy_env.calls) == 1
    id_sent, message, args = dummy_env.calls[0]
    assert message == "Copy"
    expected_args = (new_id,)
    assert args == expected_args
    # Verify the new instance is stored in env.attrs and has matching data.
    assert new_id in dummy_env.attrs
    assert dummy_env.attrs[new_id].data == base.data
    # Test Destroy: remove the original.
    dummy_env.calls.clear()
    base.Destroy()
    assert len(dummy_env.calls) == 1
    id_sent, message, args = dummy_env.calls[0]
    assert message == "Destroy"
    # Verify that the original instance has been removed.
    assert 2 not in dummy_env.attrs

def test_get_local_point_from_world(base_attr_instance, dummy_env):
    dummy_env.calls.clear()
    point = [3, 3, 3]
    base_attr_instance.GetLocalPointFromWorld(point)
    assert len(dummy_env.calls) == 1
    id_sent, message, args = dummy_env.calls[0]
    assert message == "GetLocalPointFromWorld"
    expected_args = ([float(i) for i in point],)
    assert args == expected_args

def test_get_world_point_from_local(base_attr_instance, dummy_env):
    dummy_env.calls.clear()
    point = [4, 5, 6]
    base_attr_instance.GetWorldPointFromLocal(point)
    assert len(dummy_env.calls) == 1
    id_sent, message, args = dummy_env.calls[0]
    assert message == "GetWorldPointFromLocal"
    expected_args = ([float(i) for i in point],)
    assert args == expected_args

def test_do_move(base_attr_instance, dummy_env):
    dummy_env.calls.clear()
    position = [1, 2, 3]
    duration = 5.0
    speed_based = False
    relative = True
    base_attr_instance.DoMove(position, duration, speed_based, relative)
    assert len(dummy_env.calls) == 1
    id_sent, message, args = dummy_env.calls[0]
    assert message == "DoMove"
    expected_args = ([float(i) for i in position], float(duration), speed_based, relative)
    assert args == tuple(expected_args)

def test_do_rotate(base_attr_instance, dummy_env):
    dummy_env.calls.clear()
    rotation = [10, 20, 30]
    duration = 3.0
    speed_based = True
    relative = False
    base_attr_instance.DoRotate(rotation, duration, speed_based, relative)
    assert len(dummy_env.calls) == 1
    id_sent, message, args = dummy_env.calls[0]
    assert message == "DoRotate"
    expected_args = ([float(i) for i in rotation], float(duration), speed_based, relative)
    assert args == tuple(expected_args)

def test_do_rotate_quaternion(base_attr_instance, dummy_env):
    dummy_env.calls.clear()
    quaternion = [0, 0, 0, 1]
    duration = 2.0
    speed_based = False
    relative = True
    base_attr_instance.DoRotateQuaternion(quaternion, duration, speed_based, relative)
    assert len(dummy_env.calls) == 1
    id_sent, message, args = dummy_env.calls[0]
    assert message == "DoRotateQuaternion"
    expected_args = ([float(i) for i in quaternion], float(duration), speed_based, relative)
    assert args == tuple(expected_args)

def test_do_complete(base_attr_instance, dummy_env):
    dummy_env.calls.clear()
    base_attr_instance.DoComplete()
    assert len(dummy_env.calls) == 1
    id_sent, message, args = dummy_env.calls[0]
    assert message == "DoComplete"
    assert args == ()

def test_do_kill(base_attr_instance, dummy_env):
    dummy_env.calls.clear()
    base_attr_instance.DoKill()
    assert len(dummy_env.calls) == 1
    id_sent, message, args = dummy_env.calls[0]
    assert message == "DoKill"
    assert args == ()

def test_wait_do(base_attr_instance, dummy_env):
    base_attr_instance.data["move_done"] = True
    base_attr_instance.data["rotate_done"] = True
    initial_steps = dummy_env.step_count
    base_attr_instance.WaitDo()
    assert dummy_env.step_count >= initial_steps
