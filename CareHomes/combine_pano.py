import numpy as np

def im2sphere(im, im_hori_fov, sphere_w, sphere_h, x, y):
    

def combineViews(imgs, width, height):
    img_shape = imgs[0]["img"].shape
    panoout = np.zeros((height, width, img_shape[0], img_shape[1], 3))
    panowei = np.zeros((height, width, img_shape[0], img_shape[1], 3))
    imgNum = len(imgs.keys())
    for i in range(imgNum):
        sphere_img, valid_map = im2sphere(imgs[i]["img"], imgs[i]["fov"], width, height, imgs[i]["vx"], imgs[i]["vy"])
        invalid_map = 1-valid_map
        sphere_img[invalid_map] = 0
        panoout = panoout + sphere_img
        panowei = panowei + valid_map
    
    panoout[panowei==0] = 0
    panowei[panowei==0] = 1
    panoout = panoout / (1.0 * panowei)
    return panoout

def stitch_a_skybox(name):
    sep_img = {}
    vx = np.array([-np.pi/2, -np.pi/2, 0, np.pi/2, np.pi, -np.pi/2])
    vy = np.array([np.pi/2, 0, 0, 0, 0, -np.pi/2])

    for i in range(6):
        sep_img[i]["img"] = 
        sep_img[i]["vx"] = vx[i]
        sep_img[i]["vy"] = vy[i]
        sep_img[i]["fov"] = np.pi/2+0.001
        sep_img[i]["sz"] = sep_img[i]["img"].shape
    
    panoskybox = combineViews(sep_img, 2048, 1024)
    return panoskybox


if __name__ == "__main__":
    house_name = "1LXtFkjw3qL"
    skybox_path = house_name+"/"+house_name+"/matterport_skybox_images"

    # skybox does not need camera intrinsics
    #camera_intri_path = house_name+"/"+house_name+"/matterport_camera_intrinsics"