from ivy2 import Ivy2Printer
import image

PRINTER_MAC = "04:7F:0E:B7:46:0B"


def main():
    printer = Ivy2Printer()
    printer.connect(PRINTER_MAC)

    printer.print("./assets/test_image.png")

    printer.disconnect()


def preview_image(image_path, output_path="preview_image.jpeg"):
    """Get a preview of what the printed image will look like."""

    image_data = image.prepare_image(image_path, 100, True)

    with open(output_path, "wb") as file:
        file.write(image_data)


main()
