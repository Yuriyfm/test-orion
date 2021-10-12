import re

#модуль валидации данных с помощью regex

def add_person_data_validation(request_data):
    '''Функция, с помощью regexp, проверяет валидность данных отправленных в обработчик add_person'''
    for num, item in enumerate(request_data):
        try:
            if not re.match("^\/([а-яА-Яa-zA-Z-_]+\/)+([а-яА-Яa-zA-Z-_]+)(\.)([a-zA-Z]{3,4})$", item['file_path']):
                return f'Неверный формат атрибута file_path в данных контакта {num+1}. Ожидается путь в подобном' \
                       f' формате - /media/profile_images/my_photo.jpg, было получено - {item["file_path"]}.'
            if not re.match("^[А-ЯЁ][а-яёА-ЯЁ\-]{0,}\s[А-ЯЁ][а-яёА-ЯЁ\-]{1,}(\s[А-ЯЁ][а-яёА-ЯЁ\-]{1,})?$",
                            item['full_name']):
                return f'Неверный формат атрибута full_name в элементе списка номер {num+1}. Ожидается ФИО в подобном' \
                       f' формате - Иванов Иван Иванович, было получено - {item["full_name"]}.'
            if not re.match("^(Мужской|Женский)$", item['gender']):
                return f'Неверный формат атрибута gender в элементе списка номер {num+1}. Ожидаются варианты - ' \
                       f'Мужской/Женский, было получено - {item["gender"]}.'
            if not re.match("^((?:19|20)\d\d)-(0[1-9]|1[012])-([12][0-9]|3[01]|0[1-9])$", item['birthday']):
                return f'Неверный формат атрибута birthday в элементе списка номер {num+1}. Ожидается дата в формате ' \
                       f'YYYY-MM-DD, было получено - {item["birthday"]}.'
            if not re.match("^([А-Я][а-яёА-Я\-]{1,})(?: +[А-Я][а-яёА-Я\-]{1,})?, +(?:\d+(?:-[яЯ])? +)?([А-Я][а-яёА-Я\-]"
                            "{1,})(?:( +[а-яёА-Я][а-яёА-Я\-]{1,})|( +[а-я]))*?( +\d+(\-)?[а-яёА-Я])?,"
                            " +д. +\d+[А-Я]{0,1}, +кв. +\d+$", item['address']):
                return f'Неверный формат атрибута address в элементе списка номер {num+1}. Ожидается адрес в  подобном' \
                       f' формате - Красноярск, Мира, д. 1, кв. 3 (элементы - "город", "улица", "дом", "квартира",' \
                       f' разделены запятой и пробелом, количество пробелов между элементами  и внутри них может быть' \
                       f' больше одного, названия улиц и городов начинаются с заглавной буквы), было получено - ' \
                       f'{item["address"]}.'
            for phone in item['phones']:
                if not re.match("^((8|\+7))(\(?\d{3}\)?)([\d]{7})$", phone['phone_number']):
                    return f'Неверный формат атрибута phone_number в элементе списка номер {num+1}. Ожидается номер в ' \
                           f'одном из форматов - +7хххххххххх/+7(ххх)ххххххх/8хххххххххх/8(ххх)ххххххх, было получено - ' \
                           f'{phone["phone_number"]}.)'
                if not re.match("^(Городской|Мобильный)$", phone['phone_type']):
                    return f'Неверный формат атрибута phone_type в элементе списка номер {num+1}. Ожидаются варианты - ' \
                           f'Городской/Мобильный, было получено - {phone["phone_type"]}.'
            for email in item['emails']:
                if not re.match("^((([0-9A-Za-z]{1}[-0-9A-z\.]{1,}[0-9A-Za-z]{1})|([0-9А-Яа-я]{1}[-0-9А-я\.]{1,}[0-9А-Яа-я]{1}))"
                                "@([-A-Za-z]{1,}\.){1,2}[-A-Za-z]{2,})$", email["email_address"]):
                    return f'Неверный формат атрибута email_address в элементе списка номер {num+1}. Ожидается адрес ' \
                           f'почты в подобном формате - ivanov1980@yahoo.com, было получено -  {email["email_address"]}.'
                if not re.match("^(Личная|Рабочая)$", email['email_type']):
                    return f'Неверный формат атрибута email_type в элементе списка номер {num+1}. Ожидаются варианты - ' \
                           f'Личная/Рабочая, было получено - {email["email_type"]}.'
        except TypeError:
            return ('Нет доступных данных для обработки или структура JSON не соответствует ожидаемой.')
        except KeyError as k:
            return f'неверно указано имя атрибута {k} в элементе списка номер {num+1}, или он отсутствует.'
    return 'Data is valid'


def update_person_data_validation(request_data):
    '''Функция, с помощью regexp, проверяет валидность данных отправленных в обработчик update_person'''
    try:
        if not re.match("^\/([а-яА-Яa-zA-Z-_]+\/)+([а-яА-Яa-zA-Z-_]+)(\.)([a-zA-Z]{3,4})$", request_data['file_path']):
            return f'Неверный формат атрибута file_path. Ожидается путь в подобном формате - ' \
                       f'/media/profile_images/my_photo.jpg, было получено - {request_data["file_path"]}.'
        if not re.match("^(\d+)$", request_data['person_id']):
            return f'Неверный формат атрибута person_id.'
        if not re.match("^^[А-ЯЁ][а-яёА-ЯЁ\-]{0,}\s[А-ЯЁ][а-яёА-ЯЁ\-]{1,}(\s[А-ЯЁ][а-яёА-ЯЁ\-]{1,})?$",
                        request_data['full_name']):
            return f'Неверный формат атрибута full_name. Ожидается ФИО в подобном формате - Иванов Иван Иванович,' \
                       f' было получено - {request_data["full_name"]}.'
        if not re.match("^Мужской|Женский$", request_data['gender']):
            return f'Неверный формат атрибута gender. Ожидаются варианты - Мужской/Женский, было получено - ' \
                   f'{request_data["gender"]}.'
        if not re.match("^((?:19|20)\d\d)-(0?[1-9]|1[012])-([12][0-9]|3[01]|0?[1-9])$", request_data['birthday']):
                return f'Неверный формат атрибута birthday. Ожидается дата в формате YYYY-MM-DD, было получено - ' \
                       f'{request_data["birthday"]}.'
        if not re.match("^([А-Я][а-яА-Я\-]{1,})(?: +[А-Я][а-яА-Я\-]{1,})?, +(?:\d+(?:-[яЯ])? +)?([А-Я][а-яА-Я\-]"
                        "{1,})(?:( +[а-яА-Я][а-яА-Я\-]{1,})|( +[а-я]))*?( +\d+\-[яЯ])?, +д. +\d+[А-Я]{0,1},"
                        " +кв. +\d+$", request_data['address']):
            return f'Неверный формат атрибута address в элементе списка номер {request_data + 1}. Ожидается адрес в  подобном' \
                   f' формате - Красноярск, Мира, д. 1, кв. 3 (элементы - "город", "улица", "дом", "квартира",' \
                   f' разделены запятой и пробелом, количество пробелов между элементами  и внутри них может быть' \
                   f' больше одного, названия улиц и городов начинаются с заглавной буквы), было получено - ' \
                   f'{request_data["address"]}.'
    except TypeError as tr:
        return ('Нет доступных данных для обработки или структура JSON не соответствует ожидаемой.')
    except KeyError as k:
        return f'неверно указано имя атрибута {k}, или он отсутствует'
    return 'Data is valid'


def add_phone_data_validation(request_data):
    '''Функция, с помощью regexp, проверяет валидность данных отправленных в обработчик add_phone'''
    try:
        if not re.match("^(\d+)$", request_data['person_id']):
            return f'Неверный формат атрибута person_id.'
        if not re.match("^((8|\+7))(\(?\d{3}\)?)([\d]{7})$", request_data['phone_number']):
            return f'Неверный формат атрибута phone_number. Ожидается номер в одном из форматов - ' \
                   f'+7хххххххххх/+7(ххх)ххххххх/8хххххххххх/8(ххх)ххххххх, было получено - {request_data["phone_number"]}.)'
        if not re.match("^(Городской|Мобильный)$", request_data['phone_type']):
            return f'Неверный формат атрибута phone_type. Ожидаются варианты - ' \
                   f'Городской/Мобильный, было получено - {request_data["phone_type"]}.'
    except TypeError as tr:
        return ('Нет доступных данных для обработки или формат данных не соответсвует ожидаемому')
    except KeyError as k:
        return f'неверно указано имя атрибута {k}, или он отсутствует'
    return 'Data is valid'


def add_email_data_validation(request_data):
    '''Функция, с помощью regexp, проверяет валидность данных отправленных в обработчик add_email'''
    try:
        if not re.match("^(\d+)$", request_data['person_id']):
            return f'Неверный формат атрибута person_id.'
        if not re.match(
                "^((([0-9A-Za-z]{1}[-0-9A-z\.]{1,}[0-9A-Za-z]{1})|([0-9А-Яа-я]{1}[-0-9А-я\.]{1,}[0-9А-Яа-я]{1}))"
                "@([-A-Za-z]{1,}\.){1,2}[-A-Za-z]{2,})$", request_data["email_address"]):
            return f'Неверный формат атрибута email_address. Ожидается адрес ' \
                   f'почты в подобном формате - ivanov1980@yahoo.com, было получено -  {request_data["email_address"]}.'
        if not re.match("^(Личная|Рабочая)$", request_data['email_type']):
            return f'Неверный формат атрибута email_type. Ожидаются варианты - ' \
                   f'Личная/Рабочая, было получено - {request_data["email_type"]}.'
    except TypeError as tr:
        return ('Нет доступных данных для обработки или формат данных не соответсвует ожидаемому')
    except KeyError as k:
        return f'неверно указано имя атрибута {k}, или он отсутствует'
    return 'Data is valid'


def id_validation(request_data):
    """Функция, с помощью regexp, проверяет валидность person_id в обработчиках удаления и изменения данных"""
    try:
        if not re.match("^(\d+)$", request_data['person_id']):
            return f'Неверный формат атрибута person_id.'
    except TypeError as tr:
        return ('Нет доступных данных для обработки или формат данных не соответсвует ожидаемому')
    except KeyError as k:
        return f'неверно указано имя атрибута {k}, или он отсутствует'
    return 'Data is valid'


def sort_data_persons(request_data):
    '''Функция проверяет валидность параметров сортировки отправленных в обработчик get_persons_list'''
    try:
        attributes = ['person_id', 'address', 'birthday', 'file_path', 'full_name', 'gender']
        order = ['desc', 'asc']
        if request_data['sorted_by'] not in attributes:
            return f'Неверный формат значения атрибута sorted_by. Ожидается один из следующих вариантов - {attributes}' \
                   f', было получено -  {request_data["sorted_by"]}'
        if request_data['order'] not in order:
            return f'Неверный формат значения атрибута order. Ожидается один из следующих вариантов {order}' \
                   f', было получено -  {request_data["order"]}'
    except TypeError as tr:
        return ('Нет доступных данных для обработки или формат данных не соответсвует ожидаемому')
    except KeyError as k:
        return f'неверно указано имя атрибута {k}, или он отсутствует'
    return 'Data is valid'

def sort_data_phones(request_data):
    '''Функция проверяет валидность параметров сортировки отправленных в обработчик get_phones_list'''
    try:
        attributes = ['person_id', 'phone_number', 'phone_type']
        order = ['desc', 'asc']
        if request_data['sorted_by'] not in attributes:
            return f'Неверный формат значения атрибута sorted_by. Ожидается один из следующих вариантов - {attributes}' \
                   f', было получено -  {request_data["sorted_by"]}'
        if request_data['order'] not in order:
            return f'Неверный формат значения атрибута order. Ожидается один из следующих вариантов {order}' \
                   f', было получено -  {request_data["order"]}'
    except TypeError as tr:
        return ('Нет доступных данных для обработки или формат данных не соответсвует ожидаемому')
    except KeyError as k:
        return f'неверно указано имя атрибута {k}, или он отсутствует'
    return 'Data is valid'

def sort_data_emails(request_data):
    '''Функция проверяет валидность параметров сортировки отправленных в обработчик get_emails_list'''
    try:
        attributes = ['person_id', 'email_address', 'email_type']
        order = ['desc', 'asc']
        if request_data['sorted_by'] not in attributes:
            return f'Неверный формат значения атрибута sorted_by. Ожидается один из следующих вариантов - {attributes},' \
                   f', было получено -  {request_data["sorted_by"]}'
        if request_data['order'] not in order:
            return f'Неверный формат значения атрибута order. Ожидается один из следующих вариантов {order}' \
                   f', было получено -  {request_data["order"]}'
    except TypeError as tr:
        return ('Нет доступных данных для обработки или формат данных не соответсвует ожидаемому')
    except KeyError as k:
        return f'неверно указано имя атрибута {k}, или он отсутствует'
    return 'Data is valid'