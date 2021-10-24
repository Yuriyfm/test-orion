import re
import traceback
# модуль валидации данных с помощью regex

all_attributes = ['person_id', 'address', 'birthday', 'file_path', 'full_name', 'gender',
                  'phone_type', 'phone_number', 'email_type', 'email_address']

order_types = ['desc', 'asc']

gender_types = ['Мужской', 'Женский']

phone_types = ['Мобильный', 'Городской']

email_types = ['Личная', 'Рабочая']

# блок с регулярными выражениями для проверки валидности данных
file_path_validation_regexp = "^\\/([а-яА-Яa-zA-Z-_]+\\/)+([а-яА-Яa-zA-Z-_]+)(\\.)([a-zA-Z]{3,4})$"
full_name_validation_regexp = "^[А-ЯЁ][а-яёА-ЯЁ\\-]{0,}\\s[А-ЯЁ][а-яёА-ЯЁ\\-]{1,}(\\s[А-ЯЁ][а-яёА-ЯЁ\\-]{1,})?$"
gender_validation_regexp = f"^({'|'.join(gender_types)})$"
birthday_validation_regexp = "^((?:19|20)\\d\\d)-(0[1-9]|1[012])-([12][0-9]|3[01]|0[1-9])$"
address_validation_regexp = "^([А-Я][а-яёА-Я\\-]{1,})(?: +[А-Я][а-яёА-Я\\-]{1,})?, +(?:\\d+(?:-[яЯ])? +)?([А-Я]" \
                            "[а-яёА-Я\\-]{1,})(?:( +[а-яёА-Я][а-яёА-Я\\-]{1,})|( +[а-я]))*?( +\\d+(\\-)?[а-яёА-Я])?," \
                            " +д. +\\d+[А-Я]{0,1}, +кв. +\\d+$"
phone_type_validation_regexp = f"^({'|'.join(phone_types)})$"
phone_number_validation_regexp = '^((8|\\+7))(\\(?\\d{3}\\)?)([\\d]{7})$'
email_type_validation_regexp = f"^({'|'.join(email_types)})$"
email_address_validation_regexp = "^((([0-9A-Za-z]{1}[-0-9A-z\\.]{1,}[0-9A-Za-z]{1})|([0-9А-Яа-я]{1}[-0-9А-я\\.]{1,}" \
                                  "[0-9А-Яа-я]{1}))@([-A-Za-z]{1,}\\.){1,2}[-A-Za-z]{2,})$"
person_id_validation_regexp = "^(\\d+)$"
sorted_by_validation_regexp = f"^({'|'.join(all_attributes)})$"
order_validation_regexp = f"^({'|'.join(order_types)})$"

# словарь с названиями атрибутов, соответсвующими им regexp и сообщениями если данные не валидны.
validation_dict = {
    'file_path': {'regexp': file_path_validation_regexp,
                  'return_if_invalid': 'Неверный формат атрибута file_path. Ожидается путь в подобном формате - '
                                       '/media/profile_images/profile_photo.jpg.'},
    'full_name': {'regexp': full_name_validation_regexp,
                  'return_if_invalid': 'Неверный формат атрибута full_name. Ожидается ФИО в подобном формате - '
                                       'Иванов Иван Иванович.'},
    'gender': {'regexp': gender_validation_regexp,
               'return_if_invalid': f'Неверный формат атрибута gender. Ожидаются варианты - {", ".join(gender_types)}.'},
    'birthday': {'regexp': birthday_validation_regexp,
                 'return_if_invalid': 'Неверный формат атрибута birthday. Ожидается дата в формате YYYY-MM-DD.'},
    'address': {'regexp': address_validation_regexp,
                'return_if_invalid': 'Неверный формат атрибута address. Ожидается адрес в  подобном формате - '
                                     'Красноярск, Мира, д. 1, кв. 3 (элементы - "город", "улица", "дом", "квартира",'
                                     ' разделены запятой и пробелом, количество пробелов между элементами  и внутри'
                                     ' них может быть больше одного, названия улиц и городов начинаются с заглавной '
                                     'буквы).'},
    'phone_number': {'regexp': phone_number_validation_regexp,
                     'return_if_invalid': 'Неверный формат атрибута phone_number. Ожидается номер в одном из форматов -'
                                          ' +7хххххххххх/+7(ххх)ххххххх/8хххххххххх/8(ххх)ххххххх.'},
    'phone_type': {'regexp': phone_type_validation_regexp,
                   'return_if_invalid': f'Неверный формат атрибута phone_type. Ожидаются варианты - '
                                        f'{", ".join(phone_types)}.'},
    'email_type': {'regexp': email_type_validation_regexp,
                   'return_if_invalid': f'Неверный формат атрибута email_type. Ожидаются варианты - '
                                        f'{", ".join(email_types)}.'},
    'email_address': {'regexp': email_address_validation_regexp,
                      'return_if_invalid': 'Неверный формат атрибута email_address. Ожидается адрес '
                                           'почты в подобном формате - ivanov1980@yahoo.com.'},
    'person_id': {'regexp': person_id_validation_regexp,
                  'return_if_invalid': 'Неверный формат атрибута person_id. Ожидается числовое значение'},
    'sorted_by': {'regexp': sorted_by_validation_regexp,
                  'return_if_invalid': f'Неверный формат атрибута sorted_by. Ожидается один из атрибутов: '
                                       f'{", ".join(all_attributes)}.'},
    'order': {'regexp': order_validation_regexp,
              'return_if_invalid': f'Неверный формат атрибута order. Ожидается один из атрибутов:'
                                   f'{order_types}.'}
}


def data_validation(data):
    """Функция принимает аргументы пришедшие в обработчик в handlers и проверяет их по словарю validation_dict"""
    try:
        for attribute in data.items():
            # phones и emails обрабатываем отдельно, т.к. это списки
            if attribute[0] == 'phones' or attribute[0] == 'emails':
                for item in attribute[1]:
                    for i in item.items():
                        attribute_name = i[0]
                        attribute_value = i[1]
                        if not re.match(validation_dict[attribute_name]['regexp'], attribute_value):
                            return {'Ошибка валидации данных': validation_dict[attribute_name]['return_if_invalid'] +
                                    f' Было получено - {attribute_value}'}
            else:
                attribute_name = attribute[0]
                attribute_value = attribute[1]
                if not re.match(validation_dict[attribute_name]['regexp'], attribute_value):
                    return {'Ошибка валидации данных': validation_dict[attribute_name]['return_if_invalid'] +
                            f' Было получено - {attribute_value}'}
        return 'Data is valid'
    except KeyError as ke:
        return {'error': f'Неверно указано имя одного из атрибутов. Ожидаемые атрибуты'
                f' {", ".join(list(validation_dict.keys()))}. Было получено - {ke}', 'exception_name':
                ke.__class__.__name__, 'info': traceback.format_exc()}
    except AttributeError as ae:
        return {'error': 'Формат данных не соответствует ожидаемому', 'exception_name': ae.__class__.__name__,
                         'info': traceback.format_exc()}
