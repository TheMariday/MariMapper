import cv2
from lib.utils import cprint, Col
from lib.led_map_2d import LEDDetection


class LedFinder:

    def __init__(self, threshold=128):
        self.threshold = threshold

    def find_led(self, image):

        _, image_thresh = cv2.threshold(image, self.threshold, 255, cv2.THRESH_TOZERO)

        contours, _ = cv2.findContours(
            image_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )

        led_response_count = len(contours)
        if led_response_count == 0:
            return None
        elif led_response_count > 1:
            pass
            #cprint(
            #    f"Warning! More than 1 light source found, found {led_response_count} light sources",
            #    format=Col.WARNING,
            #)

        moments = cv2.moments(image_thresh)

        if moments["m00"] == 0:
            return None

        img_height = image.shape[0]
        img_width = image.shape[1]

        center_u = moments["m10"] / moments["m00"]
        center_v = moments["m01"] / moments["m00"]

        center_u = center_u / img_width
        v_offset = (img_width - img_height) / 2.0
        center_v = (center_v + v_offset) / img_width

        return LEDDetection(center_u, center_v, contours)

    @staticmethod
    def draw_results(image, results):

        render_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        img_height = render_image.shape[0]
        img_width = render_image.shape[1]

        if results:
            cv2.drawContours(render_image, results.contours, -1, (255, 0, 0), 1)

            u_abs = int(results.u * img_width)

            v_offset = (img_width - img_height) / 2.0

            v_abs = int(results.v * img_width - v_offset)

            cv2.drawMarker(
                render_image,
                (u_abs, v_abs),
                (0, 255, 0),
                markerSize=100,
            )

        return render_image
