from PIL import Image


def make_background_transparent(img_path, tolerance=10):
    img = Image.open(img_path)
    img = img.convert("RGBA")

    datas = img.getdata()

    new_data = []
    for item in datas:
        if all([abs(n - 255) < tolerance for n in item[:3]]):
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)

    img.putdata(new_data)
    img.save("img_bg_removed.png", "PNG")


make_background_transparent("test_image.png")
