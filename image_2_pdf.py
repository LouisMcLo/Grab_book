import os   
from PIL import Image

def image_2_pdf(picfolder):
    file_list = os.listdir('./%s' %picfolder)
    pic_name = []
    im_list = []
    for x in file_list:
        if "jpg" in x or 'png' in x or 'jpeg' in x:
            pic_name.append(picfolder + "/" + x)
    pic_name.sort()
    # 合并为pdf
    im1 = Image.open(pic_name[0])
    pic_name.pop(0)
    for i in pic_name:
        img = Image.open(i)
        if img.mode != "RGB":
            img = img.convert('RGB')
            im_list.append(img)
        else:
            im_list.append(img)
    im1.save("{}.pdf".format(picfolder), "PDF", resolution=100.0, save_all=True, append_images=im_list)

image_2_pdf('243047561')