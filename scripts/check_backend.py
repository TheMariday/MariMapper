import argparse
import sys
import time

sys.path.append("./")

from lib import utils
from lib import logging

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Tests a particular backend by making a reference led blink"
    )

    utils.add_backend_args(parser)

    parser.add_argument(
        "--reference_led",
        type=int,
        help="This is the index of the LED should be visible from the camera",
        default=0,
    )

    args = parser.parse_args()

    logging.info(f"Loading {args.backend} backend")

    led_count = args.reference_led + 1

    led_backend = utils.get_backend(args.backend, args.server)

    logging.info("Press ctrl-c to cancel")

    while True:
        time.sleep(1)

        logging.info(f"Turning on LED {args.reference_led}")
        led_backend.set_led(args.reference_led, True)

        time.sleep(1)

        logging.info(f"Turning off LED {args.reference_led}")
        led_backend.set_led(args.reference_led, False)
