import cv2
import pytesseract
import numpy as np
import os
from PIL import Image
import conftess
import confpars
from confpars import pars2


config = '--tessdata-dir "/usr/share/tesseract/tessdata"'
os.environ['TESSDATA_PREFIX'] = '/usr/share/tesseract/tessdata/'
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

# Список файлов для чтения
files_to_read = [f for f in os.listdir('/home/master2/prj/image_result11') if not f.endswith('.py') and not f.endswith('env') and not f.endswith('__pycache__')]


def read_and_recognize_text(file_path):
    image_path = file_path
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold( blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2 )

    # Применение морфологической операции для выделения горизонтальных и вертикальных линий
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel)
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 20))
    vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel)

    # Объединение горизонтальных и вертикальных линий
    table_lines = cv2.add(horizontal_lines, vertical_lines)

    # Поиск контуров таблицы
    contours, hierarchy = cv2.findContours(table_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    table_contour = max(contours, key=cv2.contourArea)  # Tаблица - самый крупный контур

    # Поиск углов таблицы с помощью метода минимального ограничивающего многоугольника
    epsilon = 0.1 * cv2.arcLength(table_contour, True)
    approx = cv2.approxPolyDP(table_contour, epsilon, True)

    # Предполагаем, что таблица имеет форму четырехугольника
    if len(approx) == 4:
        pts = approx.reshape(4, 2)

        # Сортировка углов по порядку: верхний левый, верхний правый, нижний правый, нижний левый
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        (tl, tr, br, bl) = rect
        print(tl, tr, br, bl)

        # Ширина и высота новой выровненной таблицы
        widthA = np.linalg.norm(br - bl)
        widthB = np.linalg.norm(tr - tl)
        maxWidth = max(int(widthA), int(widthB))
        heightA = np.linalg.norm(tr - br)
        heightB = np.linalg.norm(tl - bl)
        maxHeight = max(int(heightA), int(heightB))

        # Координаты новой выровненной таблицы
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")
        print(dst)

        # Преобразование перспективы
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

        # Преобразование выровненного изображения в оттенки серого
        warped_gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        warped_gray = clahe.apply(warped_gray)
        warped_thresh = cv2.adaptiveThreshold( warped_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2 )


        # Применение морфологического замыкания для усиления линий ячеек
        kernel = np.ones((3, 3), np.uint8)
        #warped_thresh = cv2.morphologyEx(warped_thresh, cv2.MORPH_CLOSE, kernel)

        # Поиск контуров ячеек в выровненной таблице
        contours, hierarchy = cv2.findContours(warped_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Фильтрация и сортировка контуров, чтобы получить ячейки таблицы
        cells = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > (maxWidth//28) and h > (maxHeight//24):  
                cells.append((x, y, w, h))

        # Сортировка ячеек по координате x, затем по координате y
        cells.sort(key=lambda c: (c[0], c[1]))
        row_header_cells = [cell for cell in cells if cell[0] < maxWidth // 15  and cell[1] >= maxHeight // 15]  # Первый столбец, исключая первую строку
        print(maxWidth)
        print(maxHeight)

        def clean_text(text):
            return text.replace("\n", " ").replace("\r", " ").strip()

        row_headers = []
        for i, (x, y, w, h) in enumerate(row_header_cells):
            header_img = warped[y:y + h, x:x + w]
            #header_img = cv2.bitwise_not(header_img) 
            header_text = pytesseract.image_to_string(header_img, config=conftess.config_ocr_name, lang='rus')
            if not header_text.strip():  # если текст пустой 
                header_text = pytesseract.image_to_string(header_img, config=conftess.config_ocr_name_1, lang='rus')
                if not header_text.strip():  # если текст пустой 
                    header_text = pytesseract.image_to_string(header_img, config=conftess.config_ocr_name_2, lang='rus')

            row_headers.append((y, y + h - 30, clean_text(header_text)))  # Сохраняем начальную и конечную координаты y заголовка

            # Сохранение изображения заголовка строки
            row_header_img_path = f'/home/master2/prj/foto2/col_header_{x}_{y}.png'
            cv2.imwrite(row_header_img_path, header_img)
            print(f"Сохранено изображение заголовка строки: {row_header_img_path}")
        
        row_headers.sort(key=lambda c: (c[0], c[1]))
        print("\nЗаголовки строк:")
        for start_y, end_y, header in row_headers:
            print(f"({start_y}, {end_y}): {header}")

        # Открытие файла для записи результатов
        with open(os.path.join('/home/master2/prj/results2', os.path.basename(file) + '.txt'), 'w', encoding='utf-8') as f:
            # Группировка ячеек по строкам с учетом небольших отклонений в координатах y
            grouped_cells = {}
            tolerance = 30  # Допуск для группировки по y координате
            for x, y, w, h in cells:
                if y > maxHeight // 10 and x > maxWidth // 10:
                    found = False
                    for key in grouped_cells.keys():
                        if abs(y - key) < tolerance:
                            grouped_cells[key].append((x, y, w, h))
                            found = True
                            break
                    if not found:
                        grouped_cells[y] = [(x, y, w, h)]

            # Обработка и запись ячеек по строкам
            for row in sorted(grouped_cells.keys()):
                # Сортировка ячеек в строке по координате x
                grouped_cells[row].sort(key=lambda c: c[0])
                row_values = []
                row_texts = []
                for x, y, w, h in grouped_cells[row]:
                    cell_img = warped[y:y + h, x:x + w]
                    #cell_img = cv2.bitwise_not(cell_img)
                    text = pytesseract.image_to_string(cell_img, config=conftess.config_ocr, lang='rus')
                    text = clean_text(text)
                    pars2_instance = pars2(text)
                    if pars2_instance.validate() or not text.strip():  # если текст пустой 
                        text = pytesseract.image_to_string(cell_img, config=conftess.config_ocr_1, lang='rus')
                        text = clean_text(text)
                        pars2_instance = pars2(text)
                        if pars2_instance.validate() or not text.strip():
                            text = pytesseract.image_to_string(cell_img, config=conftess.config_ocr_2, lang='rus')
                            text = clean_text(text)
                        else:
                            text = "Пустая ячейка"


                    row_texts.append(text)
                row_values.append(' '.join(row_texts))

                # Поиск заголовка строки
                row_header = []
                for start_y, end_y, header in row_headers:
                    if start_y-10 <= y < end_y+10:
                        row_header.append(header)
                if len(row_header) == 1:
                    row_header = row_header[0]

                if text == "":
                    text = "Пустая ячейка"

                row_header_str = row_header

                result = f"{row_header}: {'; '.join(row_texts)}\n"
                print(result)
                f.write(result)

                    # Сохранение изображения ячейки
                cell_img_path = f'/home/master2/prj/foto2/cell_{x}_{y}.png'
                cv2.imwrite(cell_img_path, cell_img)
                print(f"Сохранено изображение ячейки: {cell_img_path}")

# Чтение и распознавание текста для каждого файла
for file in files_to_read:
    print(f"Reading file: {file}")
    read_and_recognize_text(file)
    print("Text recognized and saved to file")


# Отображение изображений с выделенными ячейками
#for (x, y, w, h) in cells:
#    cv2.rectangle(warped, (x, y), (x + w, y + h), (0, 255, 0), 2)

#cv2.imshow('Table Cells', warped)
#cv2.waitKey(0)
#cv2.destroyAllWindows()

#

#def check(*args):
#    if not True:
#        return None
#    if not False:
#        return None
#    if 5 == 5:
#        return True



#if True:
#    pass
#    if False:
#        pass
#        if 5==5:
#            pass
