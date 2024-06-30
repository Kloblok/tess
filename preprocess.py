import os
import numpy as np
from pdf2image import convert_from_path
import cv2
from PIL import Image, ImageEnhance, ImageFile
import warnings

# Увеличиваем лимит размера изображения
Image.MAX_IMAGE_PIXELS = None

warnings.simplefilter('error', Image.DecompressionBombWarning)

# Функция для предобработки изображения
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, 7, 21, 1)
    inverted = cv2.bitwise_not(denoised)
    contrast_enhanced = cv2.convertScaleAbs(inverted, alpha=2, beta=1.5)
    _, binary = cv2.threshold(inverted, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return binary

# Функция для предобработки изображений и их разделения на части
def preprocess_pdf(pdf_path):
    try:
        print(f"Конвертация PDF: {pdf_path}")
        images = convert_from_path(pdf_path, first_page=1, last_page=1, poppler_path=r'C:\\Program Files\\poppler-24.02.0\\Library\\bin')
        image = np.array(images[0])
    except Exception as e:
        print(f"Ошибка при обработке файла {pdf_path}: {e}")
        return

    # Создаем директорию, если она не существует
    if not os.path.exists('image_result'):
        os.makedirs('image_result')

    height = image.shape[0]
    upper_part = image[:int(height * 0.3), :]
    lower_part = image[int(height * 0.2):, :]

    upper_filename = os.path.basename(pdf_path).replace('.pdf', '_upper.png').replace('.PDF', '_upper.png')
    lower_filename = os.path.basename(pdf_path).replace('.pdf', '_lower.png').replace('.PDF', '_lower.png')

    print(f"Сохранение верхней части: {upper_filename}")
    if cv2.imwrite(os.path.join('image_result', upper_filename), upper_part):
        print(f"Верхняя часть изображения успешно сохранена: {upper_filename}")
    else:
        print(f"Ошибка сохранения верхней части изображения: {upper_filename}")
    
    print(f"Сохранение нижней части: {lower_filename}")
    if cv2.imwrite(os.path.join('image_result', lower_filename), lower_part):
        print(f"Нижняя часть изображения успешно сохранена: {lower_filename}")
    else:
        print(f"Ошибка сохранения нижней части изображения: {lower_filename}")

    print(f"Изображения сохранены: {upper_filename}, {lower_filename}")
