import os
import numpy as np
from pdf2image import convert_from_path
import cv2
from PIL import Image, ImageEnhance, ImageFile
import warnings
import pytesseract
import re

pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
pytesseract.pytesseract.tessdata_dir_config = r'--tessdata-dir "/usr/local/share/tessdata"'
pdf_directory = '/home/abramovarto/OCR/pdf_files'
lang = 'rus'

class process_pdf:
    # Конфигурации для Tesseract
    Image.MAX_IMAGE_PIXELS = None
    warnings.simplefilter('error', Image.DecompressionBombWarning)
    configs = [
        """--oem 1 --psm 12 -c tessedit_char_whitelist='0123456789АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя-(),.:„;/\'""",
        """-c tessedit_use_gpu=1 tessedit_char_whitelist='0123456789АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя-(),.:„;/\'""",
        """--oem 1 --psm 6 -c tessedit_use_gpu=1 tessedit_char_whitelist='0123456789АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя-(),.:„;/\'""",
        """--oem 3 --psm 12 -c tessedit_use_gpu=1 tessedit_char_whitelist='0123456789АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя-(),.:„;/\'""",
        """--oem 3 --psm 6 -c tessedit_use_gpu=1 tessedit_char_whitelist='0123456789АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя-(),.:„;/\'"""
    ]

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    # Функция для предобработки изображений и их разделения на части
    def process_pdf(self):
        try:
            images = convert_from_path(self.pdf_path, first_page=1, last_page=1)
            image = np.array(images[0])
            preprocessed_image = self.preprocess_image(image)
            height = 11200
            upper_part = preprocessed_image[:int(height * 0.3), :]
            lower_part = preprocessed_image[int(height * 0.2):, :]

            # Создаем директорию, если она не существует
            image_result_directory = '/home/abramovarto/OCR/code/image_result1/'
            if not os.path.exists(image_result_directory):
                os.makedirs(image_result_directory)

            upper_filename = os.path.basename(self.pdf_path).replace('.pdf', '_upper.png').replace('.PDF', '_upper.png')
            lower_filename = os.path.basename(self.pdf_path).replace('.pdf', '_lower.png').replace('.PDF', '_lower.png')

            print(f"Сохранение верхней части: {upper_filename}")
            if cv2.imwrite(os.path.join(image_result_directory, upper_filename), upper_part):
                print(f"Верхняя часть изображения успешно сохранена: {upper_filename}")
            else:
                print(f"Ошибка сохранения верхней части изображения: {upper_filename}")
            
            print(f"Сохранение нижней части: {lower_filename}")
            if cv2.imwrite(os.path.join(image_result_directory, lower_filename), lower_part):
                print(f"Нижняя часть изображения успешно сохранена: {lower_filename}")
            else:
                print(f"Ошибка сохранения нижней части изображения: {lower_filename}")

            print(f"Изображения сохранены: {upper_filename}, {lower_filename}")

            text_result_directory = '/home/abramovarto/OCR/code/text_result1'
            if not os.path.exists(text_result_directory):
                os.makedirs(text_result_directory)

            self.save_text_from_image(upper_part, os.path.join(text_result_directory, upper_filename.replace('.png', '.txt')), lang=lang)

        except Exception as e:
            print(f"Ошибка при обработке файла {self.pdf_path}: {e}")
            return

    # Функция для предобработки изображения
    def preprocess_image(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray, None, 7, 21, 1)
        inverted = cv2.bitwise_not(denoised)
        inverted = cv2.bitwise_not(inverted)
        contrast_enhanced = cv2.convertScaleAbs(inverted, alpha=2, beta=1.5)
        _, binary = cv2.threshold(inverted, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        return binary

    # Функция для сохранения текста из изображения
    def save_text_from_image(self, image, output_file, lang='rus'):
        texts = []
        for config in self.configs:
            text = pytesseract.image_to_string(image, lang=lang, config=config)
            text = text.replace("\n", " ")
            text = re.sub(' *[^ А-Яа-я\d\w\/\\\.\-,:; ]+ *', '', text)
            texts.append(text)
        final_text = '\n\n'.join([f"Вариант {i+1}:\n{text}" for i, text in enumerate(texts)])
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(final_text)
        print(f"Текст успешно сохранен в файл: {output_file}")

for filename in os.listdir(pdf_directory):
    if filename.endswith('.pdf') or filename.endswith('.PDF'):
        pdf_path = os.path.join(pdf_directory, filename)
        pdf_processor = process_pdf(pdf_path)
        pdf_processor.process_pdf()
