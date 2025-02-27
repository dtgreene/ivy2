from PIL import Image
from io import BytesIO

PRINT_START_WIDTH = 1280
PRINT_START_HEIGHT = 1920

PRINT_FINAL_WIDTH = 640
PRINT_FINAL_HEIGHT = 1616


def prepare_image(path, auto_crop=True, quality=100, preview=False):
    image = Image.open(path, "r")
    width, height = image.size

    # determine the scale needed to reach the target dimensions
    if auto_crop:
        scale_factor = max(PRINT_START_WIDTH / width, PRINT_START_HEIGHT / height)
    else:
        scale_factor = min(PRINT_START_WIDTH / width, PRINT_START_HEIGHT / height)

    scaled_width = int(width * scale_factor)
    scaled_height = int(height * scale_factor)

    if scaled_width != width or scaled_height != height:
        image = image.resize(
            (scaled_width, scaled_height), Image.Resampling.LANCZOS
        )

    offset = (
        (PRINT_START_WIDTH - scaled_width) // 2,
        (PRINT_START_HEIGHT - scaled_height) // 2
    )

    out_image = Image.new("RGB", (PRINT_START_WIDTH, PRINT_START_HEIGHT))
    out_image.paste(image, offset)

    # skip the final transformation for preview mode
    if not preview:
        out_image = out_image.resize(
            (PRINT_FINAL_WIDTH, PRINT_FINAL_HEIGHT), 
            Image.Resampling.LANCZOS
        )
        out_image = out_image.rotate(180.0)

    with BytesIO() as out_stream:
        out_image.save(out_stream, format="JPEG", quality=quality)
        return out_stream.getvalue()
