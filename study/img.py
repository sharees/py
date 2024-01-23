from PIL import Image
im = Image.open('img.jpg')
print(im.format,im.size,im.mode)