import os
import cv2
import pytesseract
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# Конфигурации для Tesseract
configs = [
    '--oem 3 --psm 12 -c tessedit_use_gpu=1',
    '-c tessedit_use_gpu=1',
    '--oem 3 --psm 6 -c tessedit_use_gpu=1',
    '--oem 3 --psm 12 -c tessedit_use_gpu=1',
    '--oem 3 --psm 6 -c tessedit_use_gpu=1'
]

# Функция для предобработки изображения
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, 7, 21, 1)
    inverted = cv2.bitwise_not(denoised)
    contrast_enhanced = cv2.convertScaleAbs(inverted, alpha=2, beta=1.5)
    _, binary = cv2.threshold(inverted, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return binary

# Функция для сохранения текста из изображения
def save_text_from_image(image, output_file, lang='rus'):
    texts = []
    for config in configs:
        text = pytesseract.image_to_string(image, lang=lang, config=config)
        text = text.replace("\n", " ")
        text = re.sub(' *[^ $$$$А-Яа-я\d\w\/\\\.\-,:; ]+ *', ' ', text)
        texts.append(text)
    final_text = '\n\n'.join([f"Вариант {i+1}:\n{text}" for i, text in enumerate(texts)])
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(final_text)
    print(f"Текст успешно сохранен в файл: {output_file}")

# Функция для выполнения OCR верхней части
def perform_ocr_upper(directory_path):
    print("Начало OCR для верхней части изображений")
    for filename in os.listdir(directory_path):
        if filename.endswith('_upper.png'):
            image_path = os.path.join(directory_path, filename)
            print(f"Обработка изображения: {image_path}")
            image = cv2.imread(image_path)
            preprocessed_image = preprocess_image(image)
            text_filename = filename.replace('_upper.png', '_upper.txt')
            save_text_from_image(preprocessed_image, os.path.join(directory_path, text_filename))
    print("OCR для верхней части изображений завершен")