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
        height is not None and
        width != 0 and
        height != 0
    ):
        return unicode(', '.join([
            str(int(math.floor(left))),
            str(int(math.floor(top))),
            str(int(math.floor(left + width))),
            str(int(math.floor(top + height))),
        ]))

    else:
        return unicode('')  # sorl-thumbnail checks "if not" for noop.


def transform_crop_aspect_ratio(
    new_ratio,
    old_left,
    old_top,
    old_width,
    old_height
):
    if (
        None is old_left or
        None is old_top or
        None is old_width or
        None is old_height
    ):
        return (
            None,
            None,
            None,
            None
        )

    old_ratio = (old_width + 0.) / old_height
    if new_ratio > old_ratio:
        new_height = int(old_width / new_ratio)
        new_width = old_width

    else:
        new_width = int(old_height * new_ratio)
        new_height = old_height

    width_delta = new_width - old_width
    grow_left = (width_delta / 2)
    new_left = old_left - grow_left
    if new_left < 0:
        new_left = 0

    height_delta = new_height - old_height
    grow_top = (height_delta / 2)
    new_top = old_top - grow_top
    if new_top < 0:
        new_top = 0

    return (
        new_left,
        new_top,
        new_width,
        new_height
    )
