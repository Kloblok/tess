
import os
import re
import cv2
import pytesseract
import numpy as np
import pandas as pd
from PIL import Image, ImageEnhance, DecompressionBombWarning
from img2table.ocr import TesseractOCR
from img2table.document import Image

# Configuration for Tesseract
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
os.environ['TESSDATA_PREFIX'] = '/usr/share/tesseract-ocr/5/tessdata'
warnings.simplefilter('ignore', DecompressionBombWarning)

# OCR configurations
config_ocr_upper = '--oem 1 --psm 7 -c tessedit_char_whitelist=0123456789АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯабвгдеёжзийклмнопрстухыьэюя-(),.:„;/\ '
config_ocr_name = '--oem 1 --psm 7 -c tessedit_char_whitelist=НГШПЭДКВОСТМабвгдезийклмнопрстухыья-№()./\ '

# Function to preprocess the image
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, 7, 21, 1)
    inverted = cv2.bitwise_not(denoised)
    contrast_enhanced = cv2.convertScaleAbs(inverted, alpha=2, beta=1.5)
    _, binary = cv2.threshold(inverted, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return binary

# Function to save text from image
def save_text_from_image(image, output_file, lang, config):
    text = pytesseract.image_to_string(image, lang=lang, config=config)
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(text)

# Function to process PDF
def process_pdf(pdf_path):
    try:
        images = convert_from_path(pdf_path, first_page=1, last_page=1)
        image = np.array(images[0])
    except Exception as e:
        print(f"Error processing file {pdf_path}: {e}")
        return

    height = image.shape[0]
    upper_part = image[:int(height * 0.3), :]
    lower_part = image[int(height * 0.2):, :]

    upper_preprocessed = preprocess_image(upper_part)
    lower_preprocessed = preprocess_image(lower_part)

    upper_filename = os.path.basename(pdf_path).replace('.PDF', '_upper.txt')
    lower_filename = os.path.basename(pdf_path).replace('.PDF', '_lower.txt')

    save_text_from_image(upper_preprocessed, os.path.join('text_result', upper_filename), 'rus', config_ocr_upper)
    save_text_from_image(lower_preprocessed, os.path.join('text_result', lower_filename), 'rus', config_ocr_name)

# Create directories if they do not exist
if not os.path.exists('text_result'):
    os.makedirs('text_result')
if not os.path.exists('image_result'):
    os.makedirs('image_result')

# Process all PDF files in the 'ecn' directory
for filename in os.listdir('ecn'):
    if filename.lower().endswith('.pdf'):
        pdf_path = os.path.join('ecn', filename)
        if os.path.isfile(pdf_path):
            process_pdf(pdf_path)
        else:
            print(f"File not found: {pdf_path}")

# Additional code for parsing and recognizing text from images
class ParserUpper:
    def __init__(self, directory_path):
        self.pattern = '|'.join(re.escape(word) for word in ['Куст:', 'Скважина', 'Месторождение', 'ЦДНГ', 'ЦИТС', 'УЭЦН:'])
        self.pattern = rf'(?P<name>{"|".join([re.escape(word) for word in self.words_to_find])})\s+(?P<value>(?:\w|\d)+)'
        self.directory_path = directory_path

    def run(self):
        results = {}
        files = list(filter(lambda filename: filename.endswith("upper.txt"), os.listdir(self.directory_path)))
        df = pd.DataFrame(index=files)
        for filename in files:
            file_path = os.path.join(self.directory_path, filename)
            with open(file_path, 'r', encoding='UTF-8') as file:
                text = file.read()
            variants = list(filter(lambda variant: len(variant) != 0, text.split('Вариант')))
            for i, variant in enumerate(variants, start=1):
                results = self.parse_words(pattern=self.pattern, filename=filename, text=variant, df=df, results=results, i=i)
        df.to_csv('results_kust.csv')
        df.sort_index(axis=1, ascending=True).to_excel('results_kust.xlsx')
        with open('results.txt', 'w') as output_file:
            for word, value in results.items():
                output_file.write(f"{word}: {value}\n")

    def parse_words(self, pattern, filename, text, df, results, i):
        matches = re.findall(pattern, text, re.IGNORECASE)
        for name, value in matches:
            df.loc[filename, f'{name.lower()}-{i}'] = value
            results[name] = value
        return results

class ParserLower:
    def parse_line_type1(self, line):
        parts = line.split(': ')
        key = parts[0].strip()
        values = parts[1].split('; ')
        if len(values) >= 8:
            first_value = values[0].strip()
            second_value = re.sub(r'\D', '', values[1].strip())
            third_value = re.sub(r'\D', '', values[2].strip())
            fourth_value = re.sub(r'\D', '', values[3].strip())
            fifth_value = re.sub(r'^\D+', '', values[4].strip())
            seventh_value = re.sub(r'(?:(?!НОВ|РЕМ).)*', '', values[6]).strip()
            eighth_value = values[7].strip()
            return (key, first_value, second_value, third_value, fourth_value, fifth_value, seventh_value, eighth_value)
        else:
            return None

    def process_files(self, directory):
        txt_files = [f for f in os.listdir(directory) if f.endswith('.txt')]
        all_data = []
        for file_name in txt_files:
            file_path = os.path.join(directory, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    parsed_data = None
                    if line.startswith('ПЭД'):
                        parsed_data = self.parse_line_type1(line)
                    if parsed_data:
                        all_data.append(parsed_data)
        return all_data

    def run(self, directory_path):
        parsed_data = self.process_files(directory_path)
        for data in parsed_data:
            print(data)

if __name__ == '__main__':
    upper_parser = ParserUpper('text_result')
    upper_parser.run()

    lower_parser = ParserLower()
    lower_parser.run('text_result')
