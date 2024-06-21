import os  
import re

def parse_line_type1(line):
    parts = line.split(': ')
    key = parts[0].strip()
    values = parts[1].split('; ')
    if len(values) >= 8:
        first_value = values[0].strip()  
        second_value = (re.sub(r'\D', '', values[1].strip()))  
        third_value = (re.sub(r'\D', '', values[2].strip()))   
        fourth_value = (re.sub(r'\D', '', values[3].strip())) 
        fifth_value = re.sub(r'^\D+', '', values[4].strip())  
        #seventh_value = re.sub(r'[^НОВРЕМ]+', '', values[6]).strip()
        seventh_value = (re.sub(r'(?:(?!НОВ|РЕМ).)*', '', values[6]).strip())
        eighth_value = values[7].strip() 
        return (key, first_value, second_value, third_value, fourth_value, fifth_value, seventh_value, eighth_value)   
    else:
        return None

def parse_line_type2(line):
    parts = line.split(': ')
    key = parts[0].strip()
    values = parts[1].split('; ')
    if len(values) >=5:
        first_value = values[0].strip() 
        second_value = (re.sub(r'\D', '', values[1].strip()))  
        third_value = (re.sub(r'\D+', '', values[2].strip())) 
        #fourth_value = re.sub(r'[^НОВРЕМ]+', '', values[3]).strip()
        fourth_value = (re.sub(r'(?:(?!НОВ|РЕМ).)*', '', values[3]).strip())  
        fifth_value = values[4].strip()  
        return (key, second_value, third_value, fourth_value, fifth_value)
    else:
        return None

def parse_line_type3(line):

    # Разделяем строку по ": " и "; "
    parts = line.split(': ')
    key = parts[0].strip()
    values = parts[1].split('; ')
    if len(values) >=5:
        # Извлекаем значения по описанным правилам  
        first_value = values[0].strip()
        second_value = (re.sub(r'\D+', '', values[1].strip()))
        #fourth_value = re.sub(r'[^НОВРЕМ]+', '', values[3]).strip()
        fourth_value = (re.sub(r'(?:(?!НОВ|РЕМ).)*', '', values[3]).strip())
        fifth_value = values[4].strip() 
        return (key, first_value, second_value, fourth_value, fifth_value)
    else:
        return None

def parse_line_type4(line):
    parts = line.split(': ')
    key = parts[0].strip()
    values = parts[1].split('; ')
    if len(values) >=4:
        first_value = values[0].strip()
        second_value = (re.sub(r'\D+', '', values[1].strip()))
        #fourth_value = re.sub(r'[^НОВРЕМ]+', '', values[3]).strip()
        third_value = (re.sub(r'(?:(?!НОВ|РЕМ).)*', '', values[2]).strip())
        fourth_value = values[3].strip()
        return (key, first_value, second_value, third_value, fourth_value)
    else:
        return None

def parse_line_type5(line):
    parts = line.split(': ')
    key = parts[0].strip()
    values = parts[1].split('; ')
    if len(values) >=6:
        first_value = values[0].strip()
        second_value = values[1].strip()  
        #fourth_value = re.sub(r'[^НОВРЕМ]+', '', values[3]).strip()
        fourth_value = (re.sub(r'\D+', '', values[3].strip())) 
        fifth_value = (re.sub(r'(?:(?!НОВ|РЕМ).)*', '', values[4]).strip())
        sixth_value = values[5].strip() 
        return (key, first_value, second_value, fourth_value, fifth_value, sixth_value)
    else:
        return None

def parse_line_type6(line):
    parts = line.split(': ')
    key = parts[0].strip()
    values = parts[1].split('; ')
    if len(values) >= 8:
        first_value = values[0].strip()  
        second_value = values[1].strip()   
        third_value = (re.sub(r'\D', '', values[2].strip()))   
        fourth_value = (re.sub(r'\D', '', values[3].strip())) 
        fifth_value = (re.sub(r'(?:(?!НОВ|РЕМ).)*', '', values[4]).strip())
        #sixth_value = re.sub(r'[^НОВРЕМ]+', '', values[5]).strip()
        sixth_value = (re.sub(r'(?:(?!НОВ|РЕМ).)*', '', values[5]).strip()) 
        seventh_value = values[6].strip()
        eighth_value = values[7].strip()
        return (key, first_value, second_value, third_value, fourth_value, fifth_value, seventh_value, eighth_value)   
    else:
        return None  


def process_files(directory):

    txt_files = [f for f in os.listdir(directory) if f.endswith('.txt')]
    all_data = []

    for file_name in txt_files:
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                parsed_data = None
                if line.startswith('ПЭД'):
                    parsed_data = parse_line_type1(line)

                elif line.startswith('Насос'):
                    parsed_data = parse_line_type2(line)

                elif line.startswith('Протекор'):
                    parsed_data = parse_line_type3(line)

                elif line.startswith('Компенсатор') or line.startswith('Газосепаратор') or line.startswith('Вход. модуль') or line.startswith('Кабель-удлинитель') or line.startswith('ТМС'):
                    parsed_data = parse_line_type4(line)

                elif line.startswith('Кабель/№ каб.барабана'):
                    parsed_data = parse_line_type5(line)

                elif line.startswith('Обратные клапана') or line.startswith('КС/Шламоуловитель'):
                    parsed_data = parse_line_type6(line)

                if parsed_data:
                    all_data.append(parsed_data)
    
    return all_data

directory_path = '/home/master2/prj/results2/'
parsed_data = process_files(directory_path)

for data in parsed_data:
    print(data)




