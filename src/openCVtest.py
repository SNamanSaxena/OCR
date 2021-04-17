import numpy as np 
import cv2
import pytesseract
import re
import io
from PIL import Image
from io import BytesIO
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import base64
from S3Test import s3Creds as s3
import webbrowser

from flask import Flask, render_template, request, jsonify

app = Flask(__name__,template_folder='/template_folder')

###########################
def plot_gray(input_image, output_image):
#"""
#Converts an image from BGR to RGB and plots
#"""
# change color channels order for matplotlib
    fig, ax = plt.subplots(nrows=1, ncols=2)
    ax[0].imshow(input_image, cmap='gray')
    ax[0].set_title('Input Image')
    ax[0].axis('on')
    ax[1].imshow(output_image, cmap='gray')
    ax[1].set_title('Histogram Equalized ')
    ax[1].axis('on')
#    plt.savefig('histogram_equalized.png')
    plt.show()

###########################
def plot_img(input_image, obj):
    plt.imshow(input_image,cmap=obj)
    
###########################
def text_processing(text):
    panNumber = 0
    adhaarNumber = 0
    text1 = []
    data = {}
    
    lines = text.split('\n')
    for lin in lines:
        s = lin.strip()
        s = s.rstrip()
        s = s.lstrip()
        text1.append(s)
        
    pan_card_regex = r'\b[A-Z]{5}\d{4}[A-Z]{1}\b'
    adhaar_card_regex = r'\b\d{4}\s\d{4}\s\d{4}\b'
        
    text1 = list(filter(None, text1))
    
    for wordline in text1:
#        xx = wordline.split()
#        if ([w for w in xx if re.findall(pan_card_regex, w)]):
        if re.search(pan_card_regex, wordline):
            panNumber = re.findall(pan_card_regex, wordline).pop()
#            panline = text1.index(wordline)
            break
        if re.search(adhaar_card_regex, wordline):
            adhaarNumber = re.findall(adhaar_card_regex, wordline).pop()
            break

    if(panNumber != 0):
#        panNumber = text1[panline]
        data['Category'] = 'Pan Card'
        data['Pan Number'] = panNumber
#                print(data)
#                print("Category ->     Pan Card ")
#                print("Pan Number ->    "+ panNumber + '\n\n\n')
    elif(adhaarNumber != 0):
        data['Category'] = 'Adhaar Card'
        data['Adhaar Number'] = adhaarNumber
#                print(data)
#                print("Category ->     Adhaar Card ")
#                print("Adhaar Number ->    "+ adhaarNumber + '\n\n\n')  
#                break
    else:
        data['Category'] = 'NA'
#        print("Not able to read")
#                break
    return data

###########################
def imageProcessing(img):
#    img = img.convert('RGBA')
    
    gray = cv2.cvtColor(np.float32(img), cv2.COLOR_BGR2GRAY)
    plot_img(np.uint8(gray),plt.cm.gray)
    
    #CLAHE (Contrast Limited Adaptive Histogram Equalization)
    #clahe = cv2.createCLAHE(clipLimit=3.5, tileGridSize=(10,10))
    #claheFiltered = clahe.apply(np.uint8(gray))
    proc = gray
    plot_img(proc,plt.cm.gray)
    # following function performs equalization on input image
    equ = cv2.equalizeHist(np.uint8(cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX,cv2.CV_32F)))
    # for visualizing input and output side by side
    plot_gray(gray, equ)
    ret,th1 = cv2.threshold(equ,20,250,cv2.THRESH_BINARY)
#    plot_img(th1,plt.cm.gray)

    cv2.imwrite('filterImg.png',th1)
    
#    filter_img = Image.open('filterImg.png')
    
    
#    if th1.mode in ("RGBA", "P"):
#        filter_img = th1.convert("RGB")
#    filter_img.save('temp.jpg')
    
    # extracting text from image using tesseract
    text = pytesseract.image_to_string(th1)
#    print(text)
    return text

###########################
@app.route("/onBrowseCardClassifier",methods=["POST"])
def Browse():
    if request.method == 'POST':
#        print(request.form['data'])
        base64encoded = str(request.form['data'])
        encodedString = base64encoded.split(',')[1]
        decodedString = base64.b64decode(encodedString)
        input_image = Image.open(io.BytesIO(decodedString))

#    rootdir = '/home/pristyncare/Downloads/OCR/PAN-Card-OCR-test`1/test'
#    for subdir, dirs, files in os.walk(rootdir):
#        for file in files:
#            print('Current File -> '+os.path.join(subdir, file)+'\n')
#            
#            input_image = Image.open(os.path.join(subdir, file))
    
#    bucket = s3()
#
#    url = 'InsApp/4.jpg-Wed%20Jan%2029%2013%3A40%3A17%20UTC%202020'
#    url = url.replace('%20',' ')
#    url = url.replace('%3A',':')
#    object = bucket.Object(url)
#    input_image = mpimg.imread(BytesIO(object.get()['Body'].read()),'jpg')
    
    text = imageProcessing(input_image)
    response = text_processing(text)
            
#    response[file] = data
    return jsonify(isError= False,
                    message= "Success",
                    statusCode= 200,
                    data= response), 200
###########################
    
@app.route("/onDropCardClassifier",methods=["POST"])
def DropDown():
    if request.method == 'POST':
#        print(request.form['data'])
        url = request.form['data']

#    rootdir = '/home/pristyncare/Downloads/OCR/PAN-Card-OCR-test`1/test'
#    for subdir, dirs, files in os.walk(rootdir):
#        for file in files:
#            print('Current File -> '+os.path.join(subdir, file)+'\n')
#            
#            input_image = Image.open(os.path.join(subdir, file))
    
#
#    url = 'panCard/2qTRpREuYI-1578927310102.jpg'
#    print(url)
#    input_image = Image.open('13.jpg')

    app.logger.info(url)
    url = url.replace('%20',' ')
    url = url.replace('%3A',':')
    object = bucket.Object(url)
    input_image = mpimg.imread(BytesIO(object.get()['Body'].read()),'jpg')
    
    text = imageProcessing(input_image)
    response = text_processing(text)
    app.logger.info(response)
    redirecturl = 'https://example.s3.ap-south-1.amazonaws.com/' + url
    webbrowser.open(redirecturl, new=2)


#    response[file] = data
    return jsonify(isError= False,
                    message= "Success",
                    statusCode= 200,
                    data= response), 200
                   
###########################
def dropdownlist():
#    bucket = s3()
    list = []
    for obj in bucket.objects.all():
        list.append(obj.key)    
    return list

###########################
@app.route("/")
def homepage():
    droplist = dropdownlist()
    return render_template('dummy.html', droplist = droplist)

###########################
if __name__ == '__main__':
    bucket = s3()
    app.run(debug = True,use_reloader = True)