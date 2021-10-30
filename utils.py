from PIL import Image
from io import BytesIO


# to convert any image to our required aspect ratio and size, 450 x 600 pixels
def resize_image(img):
    img = Image.open(BytesIO(img))
    img_ratio = img.size[0] / img.size[1]

    ratio = 3.0/4.0 # Set image ratio here

    if ratio > img_ratio:
        box = (0, (img.size[1] - img.size[0]/ratio) / 2, img.size[0], (img.size[1] + img.size[0]/ratio) / 2)
        img = img.crop(box)

    elif ratio < img_ratio:
        box = ((img.size[0] - img.size[1] * ratio) / 2, 0, ((img.size[0] + img.size[1] * ratio)) / 2, img.size[1])
        img = img.crop(box)

    img = img.resize((450,600))

    imgBlob = BytesIO()
    img.save(imgBlob, format='jpeg')
    imgBlob = imgBlob.getvalue()

    return imgBlob
