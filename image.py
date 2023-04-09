from PIL import Image
from io import BytesIO

PRINT_OUT_WIDTH = 1280
PRINT_OUT_HEIGHT = 1920

def prepare_image(path, quality=100):
    image = Image.open(path, "r")
    width, height = image.size
    ratio = height / width

    scaled_width = width
    scaled_height = height

    if scaled_width < PRINT_OUT_WIDTH:
        scaled_width = PRINT_OUT_WIDTH
        scaled_height = int(scaled_width * ratio)

    if scaled_height < PRINT_OUT_HEIGHT:
        scaled_height = PRINT_OUT_HEIGHT
        scaled_width = int(scaled_height / ratio)

    if scaled_width != width or scaled_height != height:
        image = image.resize(
            (scaled_width, scaled_height), Image.LANCZOS
        )

    offset = (
        (PRINT_OUT_WIDTH - scaled_width) // 2,
        (PRINT_OUT_HEIGHT - scaled_height) // 2
    )

    out_image = Image.new("RGB", (PRINT_OUT_WIDTH, PRINT_OUT_HEIGHT))
    out_image.paste(image, offset)

    # debug
    # out_image.save("out.jpeg", format="JPEG", quality=90)

    with BytesIO() as out_stream:
        out_image.save(out_stream, format="JPEG", quality=quality)
        return out_stream.getvalue()
