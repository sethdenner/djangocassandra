import math


def generate_sorl_crop_string(
    left,
    top,
    width,
    height
):
    if (
        left and
        top and
        width and
        height
    ):
        return ''.join([
            str(int(math.floor(left))),
            'px ',
            str(int(math.floor(top))),
            'px ',
            str(int(math.floor(width))),
            'px ',
            str(int(math.floor(height))),
            'px'
        ])

    else:
        return 'noop'
