from PIL import Image


def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i + 2], 16) for i in (0, 2, 4))


def change_color(image_path, hex_code):
    img = Image.open(image_path).convert("RGBA")
    rgb_new_color = hex_to_rgb(hex_code)

    data = img.load()

    for y in range(img.size[1]):
        for x in range(img.size[0]):
            r, g, b, a = data[x, y]

            if r == 0 and g == 0 and b == 0 and a == 255:
                data[x, y] = rgb_new_color + (a,)

    img.save('new_image.png')


change_color('image.png', '#72c22e')
