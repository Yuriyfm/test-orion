import re
# модуль валидации данных с помощью regex


file_path_validation_regexp = "^\\/([а-яА-Яa-zA-Z-_]+\\/)+([а-яА-Яa-zA-Z-_]+)(\\.)([a-zA-Z]{3,4})$"
full_name_validation_regexp = "^[А-ЯЁ][а-яёА-ЯЁ\\-]{0,}\\s[А-ЯЁ][а-яёА-ЯЁ\\-]{1,}(\\s[А-ЯЁ][а-яёА-ЯЁ\\-]{1,})?$"
gender_validation_regexp = "^(Мужской|Женский)$"
birthday_validation_regexp = "^((?:19|20)\\d\\d)-(0[1-9]|1[012])-([12][0-9]|3[01]|0[1-9])$"
address_validation_regexp = "^([А-Я][а-яёА-Я\\-]{1,})(?: +[А-Я][а-яёА-Я\\-]{1,})?, +(?:\\d+(?:-[яЯ])? +)?([А-Я]" \
                            "[а-яёА-Я\\-]{1,})(?:( +[а-яёА-Я][а-яёА-Я\\-]{1,})|( +[а-я]))*?( +\\d+(\\-)?[а-яёА-Я])?," \
                            " +д. +\\d+[А-Я]{0,1}, +кв. +\\d+$"
phone_type_validation_regexp = '^(Городской|Мобильный)$'
phone_number_validation_regexp = '^((8|\\+7))(\\(?\\d{3}\\)?)([\\d]{7})$'
email_type_validation_regexp = "^(Личная|Рабочая)$"
email_address_validation_regexp = "^((([0-9A-Za-z]{1}[-0-9A-z\\.]{1,}[0-9A-Za-z]{1})|([0-9А-Яа-я]{1}[-0-9А-я\\.]{1,}" \
                                  "[0-9А-Яа-я]{1}))@([-A-Za-z]{1,}\\.){1,2}[-A-Za-z]{2,})$"
person_id_validation_regexp = "^(\\d+)$"

attributes_for_sort_persons_list = ['person_id', 'address', 'birthday', 'file_path', 'full_name', 'gender']
attributes_for_sort_phones_list = ['person_id', 'phone_type', 'phone_number']
attributes_for_sort_emails_list = ['person_id', 'email_type', 'email_address']
order = ['desc', 'asc']


def add_person_data_validation(request_data):
    """Функция, с помощью regexp, проверяет валидность данных отправленных в обработчик add_person"""
    for num, item in enumerate(request_data):
        try:
            if not re.match(file_path_validation_regexp, item['file_path']):
                return f'Неверный формат атрибута file_path в данных контакта {num+1}. Ожидается путь в подобном' \
                       f' формате - /media/profile_images/my_photo.jpg, было получено - {item["file_path"]}.'
            if not re.match(full_name_validation_regexp, item['full_name']):
                return f'Неверный формат атрибута full_name в элементе списка номер {num+1}. Ожидается ФИО в подобном' \
                       f' формате - Иванов Иван Иванович, было получено - {item["full_name"]}.'
            if not re.match(gender_validation_regexp, item['gender']):
                return f'Неверный формат атрибута gender в элементе списка номер {num+1}. Ожидаются варианты - ' \
                       f'Мужской/Женский, было получено - {item["gender"]}.'
            if not re.match(birthday_validation_regexp, item['birthday']):
                return f'Неверный формат атрибута birthday в элементе списка номер {num+1}. Ожидается дата в формате ' \
                       f'YYYY-MM-DD, было получено - {item["birthday"]}.'
            if not re.match(address_validation_regexp, item['address']):
                return f'Неверный формат атрибута address в элементе списка номер {num+1}. Ожидается адрес в  подобном' \
                       f' формате - Красноярск, Мира, д. 1, кв. 3 (элементы - "город", "улица", "дом", "квартира",' \
                       f' разделены запятой и пробелом, количество пробелов между элементами  и внутри них может быть' \
                       f' больше одного, названия улиц и городов начинаются с заглавной буквы), было получено - ' \
                       f'{item["address"]}.'
            for phone in item['phones']:
                if not re.match(phone_number_validation_regexp, phone['phone_number']):
                    return f'Неверный формат атрибута phone_number в элементе списка номер {num+1}. Ожидается номер в ' \
                           f'одном из форматов - +7хххххххххх/+7(ххх)ххххххх/8хххххххххх/8(ххх)ххххххх, было получено - ' \
                           f'{phone["phone_number"]}.)'
                if not re.match(phone_type_validation_regexp, phone['phone_type']):
                    return f'Неверный формат атрибута phone_type в элементе списка номер {num+1}. Ожидаются варианты - ' \
                           f'Городской/Мобильный, было получено - {phone["phone_type"]}.'
            for email in item['emails']:
                if not re.match(email_address_validation_regexp, email["email_address"]):
                    return f'Неверный формат атрибута email_address в элементе списка номер {num+1}. Ожидается адрес ' \
                           f'почты в подобном формате - ivanov1980@yahoo.com, было получено -  {email["email_address"]}.'
                if not re.match(email_type_validation_regexp, email['email_type']):
                    return f'Неверный формат атрибута email_type в элементе списка номер {num+1}. Ожидаются варианты - ' \
                           f'Личная/Рабочая, было получено - {email["email_type"]}.'
        except TypeError:
            return ('Нет доступных данных для обработки или структура JSON не соответствует ожидаемой. '
                    'Ожидается список словарей')
        except KeyError as k:
            return f'неверно указано имя атрибута {k} в элементе списка номер {num+1}, или он отсутствует.'
    return 'Data is valid'


def add_data_validation(request_data, func_name):
    """Функция, с помощью regexp, проверяет валидность данных отправленных в обработчики добавления данных add_phone и
    add_email"""
    try:
        if func_name == 'add_phone':
            if not re.match(person_id_validation_regexp, request_data['person_id']):
                return f'Неверный формат атрибута person_id.'
            if not re.match(person_id_validation_regexp, request_data['person_id']):
                return f'Неверный формат атрибута person_id.'
            if not re.match(phone_number_validation_regexp, request_data['phone_number']):
                return f'Неверный формат атрибута phone_number. Ожидается номер в одном из форматов - ' \
                       f'+7хххххххххх/+7(ххх)ххххххх/8хххххххххх/8(ххх)ххххххх, было получено - ' \
                       f'{request_data["phone_number"]}.)'
            if not re.match(phone_type_validation_regexp, request_data['phone_type']):
                return f'Неверный формат атрибута phone_type. Ожидаются варианты - ' \
                       f'Городской/Мобильный, было получено - {request_data["phone_type"]}.'
        if func_name == 'add_email':
            if not re.match(person_id_validation_regexp, request_data['person_id']):
                return f'Неверный формат атрибута person_id.'
            if not re.match(person_id_validation_regexp, request_data['person_id']):
                return f'Неверный формат атрибута person_id.'
            if not re.match(email_address_validation_regexp, request_data["email_address"]):
                return f'Неверный формат атрибута email_address. Ожидается адрес ' \
                       f'почты в подобном формате - ivanov1980@yahoo.com, было получено -  ' \
                       f'{request_data["email_address"]}.'
            if not re.match(email_type_validation_regexp, request_data['email_type']):
                return f'Неверный формат атрибута email_type. Ожидаются варианты - ' \
                       f'Личная/Рабочая, было получено - {request_data["email_type"]}.'
    except TypeError:
        return 'Нет доступных данных для обработки или структура JSON не соответствует ожидаемой.'
    except KeyError as k:
        return f'неверно указано имя атрибута {k}, или он отсутствует'
    return 'Data is valid'


def update_data_validation(request_data, func_name):
    """Функция, с помощью regexp, проверяет валидность данных отправленных в обработчики update_person, update_phone,
    update_email"""
    try:
        if func_name == 'update_person':
            if not re.match(file_path_validation_regexp, request_data['file_path']):
                return f'Неверный формат атрибута file_path. Ожидается путь в подобном формате - ' \
                           f'/media/profile_images/my_photo.jpg, было получено - {request_data["file_path"]}.'
            if not re.match(person_id_validation_regexp, request_data['person_id']):
                return f'Неверный формат атрибута person_id.'
            if not re.match(full_name_validation_regexp, request_data['full_name']):
                return f'Неверный формат атрибута full_name. Ожидается ФИО в подобном формате - Иванов Иван Иванович,' \
                           f' было получено - {request_data["full_name"]}.'
            if not re.match(gender_validation_regexp, request_data['gender']):
                return f'Неверный формат атрибута gender. Ожидаются варианты - Мужской/Женский, было получено - ' \
                       f'{request_data["gender"]}.'
            if not re.match(birthday_validation_regexp, request_data['birthday']):
                return f'Неверный формат атрибута birthday. Ожидается дата в формате YYYY-MM-DD, было получено - ' \
                           f'{request_data["birthday"]}.'
            if not re.match(address_validation_regexp, request_data['address']):
                return f'Неверный формат атрибута address. Ожидается адрес в  подобном' \
                       f' формате - Красноярск, Мира, д. 1, кв. 3 (элементы - "город", "улица", "дом", "квартира",' \
                       f' разделены запятой и пробелом, количество пробелов между элементами  и внутри них может быть' \
                       f' больше одного, названия улиц и городов начинаются с заглавной буквы), было получено - ' \
                       f'{request_data["address"]}.'
        if func_name == 'update_phone':
            if not re.match(person_id_validation_regexp, request_data['person_id']):
                return f'Неверный формат атрибута person_id.'
            if not re.match(phone_number_validation_regexp, request_data['old_phone_number']):
                return f'Неверный формат атрибута old_phone_number. Ожидается номер в одном из форматов - ' \
                       f'+7хххххххххх/+7(ххх)ххххххх/8хххххххххх/8(ххх)ххххххх, было получено - ' \
                       f'{request_data["old_phone_number"]}.'
            if not re.match(phone_number_validation_regexp, request_data['new_phone_number']):
                return f'Неверный формат атрибута new_phone_number. Ожидается номер в одном из форматов - ' \
                       f'+7хххххххххх/+7(ххх)ххххххх/8хххххххххх/8(ххх)ххххххх, было получено - ' \
                       f'{request_data["new_phone_number"]}.'
            if not re.match(phone_type_validation_regexp, request_data['new_phone_type']):
                return f'Неверный формат атрибута phone_type. Ожидаются варианты - ' \
                       f'Городской/Мобильный, было получено - {request_data["new_phone_type"]}.'
        if func_name == 'update_email':
            if not re.match(person_id_validation_regexp, request_data['person_id']):
                return f'Неверный формат атрибута person_id.'
            if not re.match(email_address_validation_regexp, request_data["old_email_address"]):
                return f'Неверный формат атрибута old_email_address. Ожидается адрес ' \
                       f'почты в подобном формате - ivanov1980@yahoo.com, было получено -  ' \
                       f'{request_data["old_email_address"]}.'
            if not re.match(email_address_validation_regexp, request_data["new_email_address"]):
                return f'Неверный формат атрибута new_email_address. Ожидается адрес ' \
                       f'почты в подобном формате - ivanov1980@yahoo.com, было получено -  ' \
                       f'{request_data["new_email_address"]}.'
            if not re.match(email_type_validation_regexp, request_data['new_email_type']):
                return f'Неверный формат атрибута new_email_type. Ожидаются варианты - ' \
                       f'Личная/Рабочая, было получено - {request_data["new_email_type"]}.'
    except TypeError:
        return 'Нет доступных данных для обработки или структура JSON не соответствует ожидаемой.'
    except KeyError as k:
        return f'неверно указано имя атрибута {k}, или он отсутствует'
    return 'Data is valid'


def id_validation(request_data):
    """Функция, с помощью regexp, проверяет валидность person_id в обработчиках удаления и получения данных по id"""
    try:
        if not re.match(person_id_validation_regexp, request_data['person_id']):
            return f'Неверный формат атрибута person_id.'
    except TypeError:
        return 'Нет доступных данных для обработки или формат данных не соответсвует ожидаемому'
    except KeyError as k:
        return f'неверно указано имя атрибута {k}, или он отсутствует'
    return 'Data is valid'


def sort_list_data_validation(request_data, func_name):
    """Функция проверяет валидность параметров сортировки отправленных в обработчики получения списков записей"""
    try:
        if func_name == 'get_persons_list' and request_data['sorted_by'] not in attributes_for_sort_persons_list:
            return f'Неверный формат значения атрибута sorted_by. Ожидается один из следующих вариантов -' \
                   f' {attributes_for_sort_persons_list}, было получено -  {request_data["sorted_by"]}'
        elif func_name == 'get_phones_list' and request_data['sorted_by'] not in attributes_for_sort_phones_list:
            return f'Неверный формат значения атрибута sorted_by. Ожидается один из следующих вариантов -' \
                   f' {attributes_for_sort_phones_list}, было получено -  {request_data["sorted_by"]}'
        elif func_name == 'get_emails_list' and request_data['sorted_by'] not in attributes_for_sort_emails_list:
            return f'Неверный формат значения атрибута sorted_by. Ожидается один из следующих вариантов -' \
                   f' {attributes_for_sort_emails_list}, было получено -  {request_data["sorted_by"]}'

        if  request_data["order"] not in order:
            return f'Неверный формат значения атрибута order. Ожидается один из следующих вариантов -' \
                   f' {order}, было получено -  {request_data["order"]}'
    except TypeError:
        return 'Нет доступных данных для обработки или формат данных не соответсвует ожидаемому'
    except KeyError as k:
        return f'неверно указано имя атрибута {k}, или он отсутствует'
    return 'Data is valid'


def delete_validation(request_data, func_name):
    """Функция проверяет валидность значений отправленных в обработчики удаления записей из phones и emails"""
    try:
        if func_name == 'delete_phone':
            if not re.match(phone_number_validation_regexp, request_data['phone_number']):
                return f'Неверный формат атрибута phone_number. Ожидается номер в одном из форматов - ' \
                       f'+7хххххххххх/+7(ххх)ххххххх/8хххххххххх/8(ххх)ххххххх, было получено - ' \
                       f'{request_data["phone_number"]}.)'
            if not re.match(person_id_validation_regexp, request_data['person_id']):
                return f'Неверный формат атрибута person_id.'
        if func_name == 'delete_email':
            if not re.match(email_address_validation_regexp, request_data["email_address"]):
                return f'Неверный формат атрибута email_address. Ожидается адрес почты в подобном формате' \
                       f' - ivanov1980@yahoo.com, было получено -  {request_data["email_address"]}.'
            if not re.match(person_id_validation_regexp, request_data['person_id']):
                return f'Неверный формат атрибута person_id.'
    except TypeError:
        return 'Нет доступных данных для обработки или формат данных не соответсвует ожидаемому'
    except KeyError as k:
        return f'неверно указано имя атрибута {k}, или он отсутствует'
    return 'Data is valid'
