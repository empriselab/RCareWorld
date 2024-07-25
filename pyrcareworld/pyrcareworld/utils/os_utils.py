import os


def make_sb3_model_dir(model_dir):
    while str(model_dir).endswith("/"):
        model_dir = model_dir[:-1]
    version = 1
    model_dir_name = model_dir + "_V" + str(version)
    while os.path.exists(model_dir_name):
        version += 1
        model_dir_name = model_dir + "_V" + str(version)

    os.makedirs(model_dir_name)

    return model_dir_name


def get_eval_file_name(model_dir, eval_file_prefix):
    eval_full_path_prefix = os.path.join(model_dir, eval_file_prefix)
    version = 1
    eval_file_name = eval_full_path_prefix + "_V" + str(version) + ".json"
    while os.path.exists(eval_file_name):
        version += 1
        eval_file_name = eval_full_path_prefix + "_V" + str(version) + ".json"

    return eval_file_name
