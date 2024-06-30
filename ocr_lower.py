
import os
import cv2
import pytesseract

# Конфигурации для Tesseract
config_ocr_lower = '--oem 1 --psm 7 -c tessedit_char_whitelist=НГШПЭДКВОСТМабвгдезийклмнопрстухыья-№()./\ '

# Функция для предобработки изображения
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, 7, 21, 1)
    inverted = cv2.bitwise_not(denoised)
    contrast_enhanced = cv2.convertScaleAbs(inverted, alpha=2, beta=1.5)
    _, binary = cv2.threshold(inverted, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return binary

# Функция для сохранения текста из изображения
def save_text_from_image(image, output_file, lang, config):
    text = pytesseract.image_to_string(image, lang=lang, config=config)
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(text)

# Функция для выполнения OCR
def perform_ocr_lower(directory_path):
    for filename in os.listdir(directory_path):
        if filename.endswith('_lower.png'):
            image_path = os.path.join(directory_path, filename)
            image = cv2.imread(image_path)
            preprocessed_image = preprocess_image(image)
            text_filename = filename.replace('_lower.png', '_lower.txt')
            save_text_from_image(preprocessed_image, os.path.join(directory_path, text_filename), 'rus', config_ocr_lower)
