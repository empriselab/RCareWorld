import base64
import cv2
import numpy as np

import pyrcareworld.attributes as attr
import pyrcareworld.utils.active_depth_generate as active_depth
import pyrcareworld.utils.utility as utility
from pyrcareworld.side_channel.side_channel import (
    IncomingMessage,
    OutgoingMessage,
)


main_intrinsic_matrix = np.array([[1380, 0, 800], [0, 1380, 450], [0, 0, 1]])
ir_intrinsic_matrix = np.array([[920, 0, 640], [0, 920, 360], [0, 0, 1]])


def parse_message(msg: IncomingMessage) -> dict:
    this_object_data = attr.camera_attr.parse_message(msg)
    if msg.read_bool() is True:
        this_object_data["ir_left"] = base64.b64decode(msg.read_string())
        this_object_data["ir_right"] = base64.b64decode(msg.read_string())

        image_left = np.frombuffer(this_object_data["ir_left"], dtype=np.uint8)
        image_left = cv2.imdecode(image_left, cv2.IMREAD_COLOR)[..., 2]
        image_right = np.frombuffer(this_object_data["ir_right"], dtype=np.uint8)
        image_right = cv2.imdecode(image_right, cv2.IMREAD_COLOR)[..., 2]
        left_extrinsic_matrix = np.array(
            [
                [0.0, -1.0, 0.0, -0.0175],
                [0.0, 0.0, -1.0, 0.0],
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )
        right_extrinsic_matrix = np.array(
            [
                [0.0, -1.0, 0.0, -0.072],
                [0.0, 0.0, -1.0, 0.0],
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )
        main_extrinsic_matrix = np.array(
            [
                [0.0, -1.0, 0.0, 0.0],
                [0.0, 0.0, -1.0, 0.0],
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )
        this_object_data[
            "active_depth"
        ] = active_depth.calc_main_depth_from_left_right_ir(
            image_left,
            image_right,
            left_extrinsic_matrix,
            right_extrinsic_matrix,
            main_extrinsic_matrix,
            ir_intrinsic_matrix,
            ir_intrinsic_matrix,
            main_intrinsic_matrix,
            lr_consistency=False,
            main_cam_size=(
                main_intrinsic_matrix[0, 2] * 2,
                main_intrinsic_matrix[1, 2] * 2,
            ),
            ndisp=128,
            use_census=True,
            register_depth=True,
            census_wsize=7,
            use_noise=False,
        )
        this_object_data["active_depth"][this_object_data["active_depth"] > 8.0] = 0
        this_object_data["active_depth"][this_object_data["active_depth"] < 0.1] = 0
    return this_object_data


def GetActiveDepth(kwargs: dict) -> OutgoingMessage:
    compulsory_params = ["id", "main_intrinsic_matrix", "ir_intrinsic_matrix"]
    optional_params = []
    utility.CheckKwargs(kwargs, compulsory_params)
    msg = OutgoingMessage()

    msg.write_int32(kwargs["id"])
    msg.write_string("GetActiveDepth")
    global main_intrinsic_matrix
    global ir_intrinsic_matrix
    main_intrinsic_matrix = np.reshape(kwargs["main_intrinsic_matrix"], [3, 3]).T
    ir_intrinsic_matrix = np.reshape(kwargs["ir_intrinsic_matrix"], [3, 3]).T
    msg.write_float32_list(ir_intrinsic_matrix.T.reshape([-1]).tolist())

    return msg
