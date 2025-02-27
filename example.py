from ivy2 import Ivy2Printer
import image

PRINTER_MAC = "XX:XX:XX:XX:XX:XX"


def print_shrek():
    printer = Ivy2Printer()
    printer.connect(PRINTER_MAC)

    printer.print("./assets/test_image.jpg")

    printer.disconnect()


def preview_image(image_path, output_path="preview_image.jpeg"):
    """Get a preview of what the printed image will look like."""

    image_data = image.prepare_image(image_path, True, 100, True)

    with open(output_path, "wb") as file:
        file.write(image_data)


if __name__ == '__main__':
    print_shrek()

