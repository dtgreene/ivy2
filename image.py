from PIL import Image
from io import BytesIO

PRINT_START_WIDTH = 1280
PRINT_START_HEIGHT = 1920

PRINT_FINAL_WIDTH = 640
PRINT_FINAL_HEIGHT = 1616


def prepare_image(path, quality=100, preview=False):
    image = Image.open(path, "r")
    width, height = image.size
    ratio = height / width

    scaled_width = width
    scaled_height = height

    if scaled_width < PRINT_START_WIDTH:
        scaled_width = PRINT_START_WIDTH
        scaled_height = int(scaled_width * ratio)

    if scaled_height < PRINT_START_HEIGHT:
        scaled_height = PRINT_START_HEIGHT
        scaled_width = int(scaled_height / ratio)

    if scaled_width != width or scaled_height != height:
        image = image.resize(
            (scaled_width, scaled_height), Image.LANCZOS
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
            Image.LANCZOS
        )
        out_image = out_image.rotate(180.0)

    # debug
    # out_image.save("out.jpeg", format="JPEG", quality=quality)

    with BytesIO() as out_stream:
        out_image.save(out_stream, format="JPEG", quality=quality)
        return out_stream.getvalue()
