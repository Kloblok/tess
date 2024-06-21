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

print(pytesseract.get_tesseract_version())
print(os.path.exists('/usr/share/tesseract/tessdata'))
print(os.access('/usr/share/tesseract/tessdata', os.R_OK))

config = '--tessdata-dir "/usr/share/tesseract/tessdata"'
os.environ['TESSDATA_PREFIX'] = '/usr/share/tesseract/tessdata/'
warnings.simplefilter('ignore', DecompressionBombWarning)
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

lang_up = 'rus'
lang_low = 'rus+eng'

def save_text_from_image(image, output_file, lang):
    texts = []
    for config in ['--oem 3 --psm 12 tessedit_use_gpu=1', '', '--oem 3 --psm 6 tessedit_use_gpu=1', '--oem 2 --psm 12 tessedit_use_gpu=1', '--oem 2 --psm 6 tessedit_use_gpu=1']:
        text = pytesseract.image_to_string(image, lang=lang, config=config)
        text = text.replace("\n", " ")
        text = re.sub(' *[^ $$$$А-Яа-я\d\w\/\\\.\-,:; ]+ *', ' ', text)
        texts.append(text)
    final_text = '\n\n'.join([f"Вариант {i+1}:\n{text}" for i, text in enumerate(texts)])
    with open(output_file, 'w') as file:
        file.write(final_text)

def crop_text(image):
    # Применение пороговой обработки
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)    
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    # Нахождение контуров текста
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Определение границ текста
    x, y, w, h = cv2.boundingRect(contours[0])
    for contour in contours:
        x_, y_, w_, h_ = cv2.boundingRect(contour)
        x = min(x, x_)
        y = min(y, y_)
        w = max(w, w_)
        h = max(h, h_)
    # Обрезка изображения по границам текста
    cropped_image = image[y:y+h, x:x+w]
    return cropped_image

def crop_text_negativ(image):
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            x, y, w, h = cv2.boundingRect(contours[0])
            for contour in contours:
                x_, y_, w_, h_ = cv2.boundingRect(contour)
                x = min(x, x_)
                y = min(y, y_)
                w = max(w, w_)
                h = max(h, h_)
            cropped_image = image[y:y+h, x:x+w]
            return cropped_image
        else:
            return image
    except Exception as e:
        print(f"Ошибка при обрезке негативного изображения: {e}")
        return image

def preprocess_image_negativ(image):
    # Изменение размера изображения, если необходимо
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=30)
    inverted = cv2.bitwise_not(denoised)
    _, binary = cv2.threshold(inverted, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return binary

def preprocess_image(image):
    # Изменение  если необходимо
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray)
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

    filename = os.path.basename(pdf_path).replace('.PDF', '.png')
    cv2.imwrite(os.path.join('image_result9', filename), image, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    preprocessed_image = preprocess_image(image)

    height = 11200
    parts = [
        (image, 'upper'),
        (image[int(height * 0.2):, :], 'lower'),
        (preprocessed_image[:int(height * 0.3), :], 'negativ_upper'),
        (preprocessed_image[:int(height * 0.3):, :], 'negativ_lower'),
    ]

    for part, name in parts:
        if name.startswith('negativ'):
            part = crop_text_negativ(part)
            part = cv2.bitwise_not(part)
        else:
            part = crop_text(part)
        filename = os.path.basename(pdf_path).replace('.PDF', f'_{name}.png')
        cv2.imwrite(os.path.join('image_result9', filename), part, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        filename = os.path.basename(pdf_path).replace('.PDF', f'_{name}.txt')
        save_text_from_image(part, os.path.join('text_result9', filename), lang_up if name.startswith('upper') or name.startswith('negativ_upper') else lang_low)

if not os.path.exists('text_result9'):
    os.makedirs('text_result9')
if not os.path.exists('image_result9'):
    os.makedirs('image_result9')

for filename in os.listdir('ecn'):
    if filename.endswith('.pdf') or filename.endswith('.PDF'):
        pdf_path = os.path.join('ecn', filename)
        if os.path.isfile(pdf_path):
            process_pdf(pdf_path)
        else:
            print(f"Файл не найден: {pdf_path}")


