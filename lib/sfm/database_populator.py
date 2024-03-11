import math

from lib.sfm.database import COLMAPDatabase
import numpy as np
from math import radians, tan
from itertools import combinations
from os import listdir, path


def populate(db_path, input_directory, led_count=23, min_avg_points_per_view=100):

    cam_views = []

    total_keypoints = 0

    input_files = [
        f for f in listdir(input_directory) if path.isfile(input_directory / f)
    ]

    for input_file_name in input_files:

        with open(input_directory / input_file_name, "r") as csv_file:
            lines = csv_file.readlines()

        key_points = np.zeros((led_count, 2))

        for line in lines:
            led_id, u, v = line.split(",")

            key_points[int(led_id)][0] = float(u) * 2000
            key_points[int(led_id)][1] = float(v) * 2000

            total_keypoints += 1

        cam_views.append(key_points)

    avg_keypoints = total_keypoints / len(input_files)

    multiplier = math.ceil(min_avg_points_per_view / avg_keypoints)

    cam_views = [np.tile(k, (multiplier, 1)) for k in cam_views]

    db = COLMAPDatabase.connect(db_path)

    db.create_tables()

    # model=0 means that it's a "SIMPLE PINHOLE" with just 1 focal length parameter that I think should get optimised
    # the params here should be f, cx, cy

    width = 2000
    height = 2000
    fov = 60  # degrees, this gets optimised so doesn't //really// matter that much

    SIMPLE_PINHOLE = 0

    cx = width / 2
    cy = height / 2
    f = (width / 2.0) / tan(radians(fov / 2.0))

    camera_id = db.add_camera(
        model=SIMPLE_PINHOLE, width=width, height=height, params=(f, cx, cy)
    )

    # Create dummy images_all_the_same.

    image_ids = []
    for input_file in input_files:
        image_id = db.add_image(input_file, camera_id)
        image_ids.append(image_id)

    # Create some keypoints
    for i, keypoints in enumerate(cam_views):
        db.add_keypoints(image_ids[i], keypoints)

    for view_1_id, view_2_id in combinations(range(len(input_files)), 2):
        view_1_keypoints = cam_views[view_1_id]
        view_2_keypoints = cam_views[view_2_id]

        shared_led_ids = []

        for i in range(len(view_1_keypoints)):
            in_both = view_1_keypoints[i].any() and view_2_keypoints[i].any()
            if in_both:
                shared_led_ids.append([i, i])

        if shared_led_ids:
            db.add_two_view_geometry(
                image_ids[view_1_id], image_ids[view_2_id], np.array(shared_led_ids)
            )

    db.commit()
    db.close()
