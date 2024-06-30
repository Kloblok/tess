import os
import cv2
import pytesseract
import numpy as np
import re
import pandas as pd

# Конфигурации для Tesseract
configs = [
    '--oem 3 --psm 6',
    '--oem 3 --psm 11',
    '--oem 3 --psm 12',
    '--oem 1 --psm 3'
]

# Функция для предобработки изображения
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, 7, 21, 1)
    inverted = cv2.bitwise_not(denoised)
    contrast_enhanced = cv2.convertScaleAbs(inverted, alpha=2, beta=1.5)
    _, binary = cv2.threshold(inverted, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return binary

# Функция для обработки изображений таблиц
def process_table_image(image_path):
    print(f"Начало обработки таблицы: {image_path}")
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel)
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 20))
    vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel)

    table_lines = cv2.add(horizontal_lines, vertical_lines)

    contours, _ = cv2.findContours(table_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    table_contour = max(contours, key=cv2.contourArea)

    epsilon = 0.1 * cv2.arcLength(table_contour, True)
    approx = cv2.approxPolyDP(table_contour, epsilon, True)

    if len(approx) == 4:
        pts = approx.reshape(4, 2)
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        (tl, tr, br, bl) = rect

        widthA = np.linalg.norm(br - bl)
        widthB = np.linalg.norm(tr - tl)
        maxWidth = max(int(widthA), int(widthB))
        heightA = np.linalg.norm(tr - br)
        heightB = np.linalg.norm(tl - bl)
        maxHeight = max(int(heightA), int(heightB))

        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")

        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

        warped_gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        _, warped_thresh = cv2.threshold(warped_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        kernel = np.ones((3, 3), np.uint8)
        warped_thresh = cv2.morphologyEx(warped_thresh, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(warped_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        cells = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > (maxWidth // 28) and h > (maxHeight // 24):
                cells.append((x, y, w, h))

        cells.sort(key=lambda c: (c[1], c[0]))
        print(f"Обработка таблицы завершена: {image_path}")
        return warped, cells
    else:
        print(f"Не удалось обнаружить таблицу: {image_path}")
        return None, []

# Функция для выполнения OCR и сохранения результата
def ocr_table_image(image, cells, output_dir):
    results = []
    for (x, y, w, h) in cells:
        cell_img = image[y:y + h, x:x + w]
        cell_text = ""
        for config in configs:
            text = pytesseract.image_to_string(cell_img, config=config, lang='rus').strip()
            if text:
                cell_text = text
                break
        if not cell_text:
            cell_text = "Не распознано"
        results.append(cell_text)

        cell_img_path = os.path.join(output_dir, f'cell_{x}_{y}.png')
        cv2.imwrite(cell_img_path, cell_img)
    return results

# Функция для выполнения OCR
def perform_ocr_lower(directory_path):
    print("Начало OCR для нижней части изображений")
    output_dir = os.path.join(directory_path, 'cells')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(directory_path):
        if filename.endswith('_lower.png'):
            image_path = os.path.join(directory_path, filename)
            print(f"Обработка изображения: {image_path}")
            processed_image, cells = process_table_image(image_path)
            if processed_image is not None:
                text_filename = filename.replace('_lower.png', '_lower.txt')
                results = ocr_table_image(processed_image, cells, output_dir)
                with open(os.path.join(directory_path, text_filename), 'w', encoding='utf-8') as file:
                    for result in results:
                        file.write(result + "\n")
                print(f"Текст успешно сохранен: {text_filename}")
    print("OCR для нижней части изображений завершен")

# Класс для парсинга результатов OCR
class ParserLower:
    def __init__(self):
        self.pattern = re.compile(r'ваш_шаблон_для_парсинга')  # Измените на нужный вам шаблон

    def run(self, directory_path):
        results = {}
        files = list(filter(lambda filename: filename.endswith("lower.txt"), os.listdir(directory_path)))
        df = pd.DataFrame(index=files)
        for filename in files:
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r', encoding='UTF-8') as file:
                text = file.read()
            variants = list(filter(lambda variant: len(variant) != 0, text.split('Вариант')))
            for i, variant in enumerate(variants, start=1):
                results = self.parse_words(filename, variant, df, results, i)
        df.to_csv('results_lower.csv')
        df.sort_index(axis=1, ascending=True).to_excel('results_lower.xlsx')
        with open('results_lower.txt', 'w') as output_file:
            for word, value in results.items():
                output_file.write(f"{word}: {value}\n")

    def parse_words(self, filename, text, df, results, i):
        matches = self.pattern.findall(text)
        for name, value in matches:
            df.loc[filename, f'{name.lower()}-{i}'] = value
            results[name] = value
        return results