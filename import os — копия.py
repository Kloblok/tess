import os
from pdf2image import convert_from_path
import cv2
import pytesseract
import numpy as np
from PIL import Image, ImageEnhance
from PIL.Image import DecompressionBombWarning
import re
import warnings
from img2table.ocr import TesseractOCR
from img2table.document import Image

print(os.path.exists('/usr/share/tesseract-ocr/5/tessdata'))
print(os.access('/usr/share/tesseract-ocr/5/tessdata', os.R_OK))

config = '--tessdata-dir "/usr/share/tesseract-ocr/5/tessdata"'
os.environ['TESSDATA_PREFIX'] = '/usr/share/tesseract-ocr/5/tessdata'
warnings.simplefilter('ignore', DecompressionBombWarning)
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

lang_up = 'rus'
lang_low = 'rus'

print(pytesseract.get_tesseract_version())
print(pytesseract.get_languages(config=''))
print(cv2.cuda.getCudaEnabledDeviceCount())

def save_text_from_image(image, output_file, lang):
    texts = []
    for config in ['--oem 3 --psm 12 -c tessedit_use_gpu=1' , '-c tessedit_use_gpu=1', '--oem 3 --psm 6 -c tessedit_use_gpu=1', '--oem 3 --psm 12 -c tessedit_use_gpu=1', '--oem 3 --psm 6 -c tessedit_use_gpu=1']:
        text = pytesseract.image_to_string(image, lang=lang, config=config)
        text = text.replace("\n", " ")
        text = re.sub(' *[^ $$$$А-Яа-я\d\w\/\\\.\-,:; ]+ *', ' ', text)
        texts.append(text)
    final_text = '\n\n'.join([f"Вариант {i+1}:\n{text}" for i, text in enumerate(texts)])
    with open(output_file, 'w') as file:
        file.write(final_text)

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, 7, 21, 1)
    inverted = cv2.bitwise_not(denoised)
    contrast_enhanced = cv2.convertScaleAbs(inverted, alpha=2, beta=1.5)
    _, binary = cv2.threshold(inverted, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    
    return binary

def process_pdf(pdf_path):
    try:
        images = convert_from_path(pdf_path, first_page=1, last_page=1)
        image = np.array(images[0])
    except Exception as e:
        print(f"Ошибка при обработке файла {pdf_path}: {e}")
        return
        print(cv2.cuda.getCudaEnabledDeviceCount())

    filename = os.path.basename(pdf_path).replace('.PDF', '.png')
    cv2.imwrite(os.path.join('image_result1', filename), image, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    preprocessed_image = preprocess_image(image)

    height = 11200
    parts = [
        (image[:int(height * 0.3), :], 'upper'),
        (preprocessed_image[:int(height * 0.3), :], 'negativ_upper'),
        (image[int(height * 0.2):, :], 'lower'),
    ]

    for part, name in parts:
        if name.startswith('upper'):
            part = (part)
        else:
            part = part

        filename = os.path.basename(pdf_path).replace('.PDF', f'_{name}.png')
        cv2.imwrite(os.path.join('image_result1', filename), part, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        filename = os.path.basename(pdf_path).replace('.PDF', f'_{name}.txt')
        save_text_from_image(part, os.path.join('text_result1', filename), lang_up if name.startswith('upper') or name.startswith('negativ_upper') else lang_low)

if not os.path.exists('text_result1'):
    os.makedirs('text_result1')
if not os.path.exists('image_result1'):
    os.makedirs('image_result1')

for filename in os.listdir('ecn'):
    if filename.endswith('.pdf') or filename.endswith('.PDF'):
        pdf_path = os.path.join('ecn', filename)
        if os.path.isfile(pdf_path):
            process_pdf(pdf_path)
        else:
            print(f"Файл не найден: {pdf_path}")



