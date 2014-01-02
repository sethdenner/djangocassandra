import math


def generate_sorl_crop_string(
    left,
    top,
    width,
    height
):
    if (
        left is not None and
        top is not None and
        width is not None and
        height is not None
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
