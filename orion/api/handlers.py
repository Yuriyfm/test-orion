from orion import app
from flask import request, jsonify
from orion.models import Person, Phone, Email
from werkzeug.exceptions import BadRequest
import traceback
from orion.data_validation import PersonData, SortedData, EmailData, PhoneData, IdData
from pydantic.error_wrappers import ValidationError as PydanticValilationError

# В данном модуле описаны методы обработки запросов к API по сущностям Person, Phone и Email.


@app.errorhandler(404)
def page_not_found():
    """Обработчик неправильных URL"""
    return jsonify({'Ошибка URL адреса': 'URL в запросе не соответствует ни одному из маршрутов'})


# Обработчики запросов к сущности Person
@app.route('/api/get_persons_list', methods=['POST'])
def get_persons_list():
    """Функция принимает POST-запрос с данными для сортировки и возвращает отсортированные
    записи из таблицы persons в формате JSON. Если данных для сортировки нет, возвращается несортированный список"""
    try:
        if not request.get_json():
            # Если данных для сортировки нет, то вызываем метод get_all_persons() модели Person без аргументов
            all_persons = Person.get_all_persons()
            return jsonify(all_persons)
        request_data = request.get_json()
        # Проводим валидацию полученных данных в модуле data_validation
        sorted_data = SortedData(**request_data)
        # Передаем данные в метод get_all_persons модели Person с данными для сортировки
        all_persons = Person.get_all_persons(sorted_data)
        return jsonify(all_persons)
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})
    except KeyError as ke:
        return jsonify({'error': f'В полученных данных отсутствует обязательный аргумент - {ke}',
                        'exception_name': ke.__class__.__name__, 'info': traceback.format_exc()})
    except PydanticValilationError as pve:
        return jsonify({'error': pve.errors(),
                        'exception_name': pve.__class__.__name__, 'info': traceback.format_exc()})


@app.route('/api/get_person', methods=['POST'])
def get_person():
    """Функция принимает POST-запрос c person_id  в формате JSON и возвращает соответствующую запись из таблицы persons"""
    try:
        # Из запроса получаем JSON c person_id
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation
        person_id_obj = IdData(**request_data)
        # Передаем person_id_obj в метод get_person модели Person
        person = Person.get_person(person_id_obj)
        return jsonify(person)
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})
    except TypeError as te:
        return jsonify({'error': f'Нет доступных данных для обработки',
                        'exception_name': te.__class__.__name__, 'info': traceback.format_exc()})
    except PydanticValilationError as pve:
        return jsonify({'error': pve.errors(),
                        'exception_name': pve.__class__.__name__, 'info': traceback.format_exc()})


@app.route('/api/add_person', methods=['PUT'])
def add_person():
    """Функция, принимает данные из JSON в теле запроса в виде списка словарей, проверяет валидность данных с помощью
     модуля data_validation и сохраняет полученные данные в таблицу persons. Поддерживается возможность сохранения
    данных с related сущностями Phone и Email в связанные таблицы и добавление нескольких контактов в БД за один запрос."""
    try:
        # Из запроса получаем JSON c данными Person и related cущностей и сохраняем их в request_data
        request_data = request.get_json()
        persons_list = []
        # Для каждого объекта в списоке контактов проводим валидацию и создаем объект person
        for item in request_data:
            person = PersonData(**item)
            persons_list.append(person)
        # Передаем список контактов в add_person сущности Person для добавления их в БД
        add_person_result = Person.add_person(persons_list)
        return add_person_result
    except TypeError as te:
        return jsonify({'error': 'структура данных не соответствует ожидаемому формату. Ожидаеся список контактов',
                        'exception_name': te.__class__.__name__, 'info': traceback.format_exc()})
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})
    except PydanticValilationError as pve:
        return jsonify({f'При валидации данных контакта номер {len(persons_list) + 1} произошла ошибка':
                        {'error': pve.errors(),
                         'exception_name': pve.__class__.__name__, 'info': traceback.format_exc()}})


@app.route('/api/update_person', methods=['PATCH'])
def update_person():
    """Функция принимает данные из JSON в теле запроса и обновляет данные в таблице persons по указанному person_id"""
    try:
        # Из запроса получаем JSON c данными Person
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation
        person_data = PersonData(**request_data)
        # Передаем атрибуты из request_data в метод update_person модели Person для изменения данных в БД
        update_result = Person.update_person(person_data)
        return jsonify(update_result)
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})
    except KeyError as ke:
        return {'error': f'В полученных данных отсутствует обязательный аргумент - {ke}',
                'exception_name': ke.__class__.__name__, 'info': traceback.format_exc()}
    except PydanticValilationError as pve:
        return jsonify({'error': pve.errors(),
                        'exception_name': pve.__class__.__name__, 'info': traceback.format_exc()})
    except TypeError as te:
        return jsonify({'error': f'Нет доступных данных для обработки',
                        'exception_name': te.__class__.__name__, 'info': traceback.format_exc()})


@app.route('/api/delete_person', methods=['DELETE'])
def delete_person():
    """Функция получает JSON и по указанному в нем person_id каскадно удаляет данные из таблицы persons и связанных
    таблиц"""
    try:
        # Из запроса получаем JSON c person_id
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        person_id_obj = IdData(**request_data)
        person_delete_result = Person.delete_person(person_id_obj)
        return jsonify(person_delete_result)
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})
    except KeyError as ke:
        return {'error': f'В полученных данных отсутствует обязательный аргумент - {ke}',
                'exception_name': ke.__class__.__name__, 'info': traceback.format_exc()}
    except PydanticValilationError as pve:
        return jsonify({'error': pve.errors(),
                        'exception_name': pve.__class__.__name__, 'info': traceback.format_exc()})
    except TypeError as te:
        return jsonify({'error': f'Нет доступных данных для обработки',
                        'exception_name': te.__class__.__name__, 'info': traceback.format_exc()})


# Обработчики запросов к сущности Phone
@app.route('/api/get_phones_list', methods=['POST'])
def get_phones_list():
    """Функция принимает POST-запрос с данными для сортировки и возвращает отсортированные
    записи из таблицы phones в формате JSON. Если данных для сортировки нет, возвращается несортированный список"""
    try:
        if not request.get_json():
            # Если данных для сортировки нет, то вызываем метод get_all_phones() модели Phone без аргументов
            all_phones = Phone.get_all_phones()
            return jsonify(all_phones)
        request_data = request.get_json()
        # Проводим валидацию полученных данных в модуле data_validation
        sorted_data = SortedData(**request_data)
        # Передаем данные в метод get_all_phones модели Phone с данными для сортировки
        all_phones = Phone.get_all_phones(sorted_data)
        return jsonify(all_phones)
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})
    except KeyError as ke:
        return {'error': f'В полученных данных отсутствует обязательный аргумент - {ke}',
                'exception_name': ke.__class__.__name__, 'info': traceback.format_exc()}
    except PydanticValilationError as pve:
        return jsonify({'error': pve.errors(),
                        'exception_name': pve.__class__.__name__, 'info': traceback.format_exc()})
    except TypeError as te:
        return jsonify({'error': f'Нет доступных данных для обработки',
                        'exception_name': te.__class__.__name__, 'info': traceback.format_exc()})


@app.route('/api/get_phone', methods=['POST'])
def get_phone():
    """Функция принимает POST-запрос c person_id  в формате JSON и возвращает запись или записи из таблицы phones
    в формате JSON"""
    try:
        # Из запроса получаем JSON c person_id
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation
        person_id_obj = IdData(**request_data)
        # Передаем person_id_obj в метод get_phone модели Phone
        phone = Phone.get_phone(person_id_obj)
        return jsonify(phone)
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})
    except KeyError as ke:
        return {'error': f'В полученных данных отсутствует обязательный аргумент - {ke}',
                'exception_name': ke.__class__.__name__, 'info': traceback.format_exc()}
    except PydanticValilationError as pve:
        return jsonify({'error': pve.errors(),
                        'exception_name': pve.__class__.__name__, 'info': traceback.format_exc()})
    except TypeError as te:
        return jsonify({'error': f'Нет доступных данных для обработки',
                        'exception_name': te.__class__.__name__, 'info': traceback.format_exc()})


@app.route('/api/add_phone', methods=['PUT'])
def add_phone():
    """Функция получает из запроса person_id, phone_number и phone_type в формате JSON и добавляет запись в таблицу
    phones."""
    try:
        # Из запроса получаем JSON c данными
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation
        phone_data = PhoneData(**request_data)
        # Передаем данные в метод модели Phone add_phone
        new_phone = Phone.add_phone(phone_data)
        return jsonify(new_phone)
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})
    except KeyError as ke:
        return {'error': f'В полученных данных отсутствует обязательный аргумент - {ke}',
                'exception_name': ke.__class__.__name__, 'info': traceback.format_exc()}
    except TypeError as te:
        return jsonify({'error': f'Нет доступных данных для обработки',
                        'exception_name': te.__class__.__name__, 'info': traceback.format_exc()})
    except PydanticValilationError as pve:
        return jsonify({'error': pve.errors(),
                        'exception_name': pve.__class__.__name__, 'info': traceback.format_exc()})


@app.route('/api/update_phone', methods=['PATCH'])
def update_phone():
    """Функция принимает данные из JSON в теле запроса и обновляет данные в таблице phones по указанному person_id
    и old_phone_number"""
    # сохраняем данные из JSON в request_data
    try:
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation
        phone_data = PhoneData(**request_data)
        # Передаем атрибуты и person_id в метод модели Phone update_phone
        phones_update_result = Phone.update_phone(phone_data)
        return jsonify(phones_update_result)
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})
    except KeyError as ke:
        return {'error': f'В полученных данных отсутствует обязательный аргумент - {ke}',
                'exception_name': ke.__class__.__name__, 'info': traceback.format_exc()}
    except TypeError as te:
        return jsonify({'error': f'Нет доступных данных для обработки',
                        'exception_name': te.__class__.__name__, 'info': traceback.format_exc()})
    except PydanticValilationError as pve:
        return jsonify({'error': pve.errors(),
                        'exception_name': pve.__class__.__name__, 'info': traceback.format_exc()})


@app.route('/api/delete_phone', methods=['DELETE'])
def delete_phone():
    """Функция получает JSON и по указанному в нем person_id и phone_number удаляет указанный телефон"""
    try:
        # Из запроса получаем JSON c person_id и номером телефона для удаления
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation
        phone_data = PhoneData(**request_data)
        # Передаем person_id и phone_number в метод delete_phone модели Phone
        phone_to_delete = Phone.delete_phone(phone_data)
        return jsonify(phone_to_delete)
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})
    except KeyError as ke:
        return {'error': f'В полученных данных отсутствует обязательный аргумент - {ke}',
                'exception_name': ke.__class__.__name__, 'info': traceback.format_exc()}
    except TypeError as te:
        return jsonify({'error': f'Нет доступных данных для обработки',
                        'exception_name': te.__class__.__name__, 'info': traceback.format_exc()})
    except PydanticValilationError as pve:
        return jsonify({'error': pve.errors(),
                        'exception_name': pve.__class__.__name__, 'info': traceback.format_exc()})


# Обработчики запросов к сущности Person
@app.route('/api/get_emails_list', methods=['POST'])
def get_emails_list():
    """Функция принимает POST-запрос с данными для сортировки и возвращает отсортированные записи из таблицы emails
    в формате JSON. Если данных для сортировки нет, возвращается несортированный список"""
    try:
        if not request.get_json():
            # Если данных для сортировки нет, то вызываем метод get_all_phones() модели Phone без аргументов
            all_emails = Email.get_all_emails()
            return jsonify(all_emails)
        request_data = request.get_json()
        # Проводим валидацию полученных данных в модуле data_validation
        sorted_data = SortedData(**request_data)
        # Передаем данные в метод get_all_phones модели Email с данными для сортировки
        all_emails = Email.get_all_emails(sorted_data)
        return jsonify(all_emails)
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON',
                        'exception_name': be.__class__.__name__, 'info': traceback.format_exc()})
    except KeyError as ke:
        return {'error': f'В полученных данных отсутствует обязательный аргумент - {ke}',
                'exception_name': ke.__class__.__name__, 'info': traceback.format_exc()}
    except PydanticValilationError as pve:
        return jsonify({'error': pve.errors(),
                        'exception_name': pve.__class__.__name__, 'info': traceback.format_exc()})
    except TypeError as te:
        return jsonify({'error': f'Нет доступных данных для обработки',
                        'exception_name': te.__class__.__name__, 'info': traceback.format_exc()})


@app.route('/api/get_email', methods=['POST'])
def get_email():
    """Функция принимает POST-запрос c person_id  в формате JSON и возвращает запись или записи из таблицы emails
    в формате JSON"""
    try:
        # Из запроса получаем JSON c person_id
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation
        person_id_obj = IdData(**request_data)
        # Передаем person_id_obj в метод get_phone модели Phone
        email = Email.get_email(person_id_obj)
        return jsonify(email)
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})
    except KeyError as ke:
        return {'error': f'В полученных данных отсутствует обязательный аргумент - {ke}',
                'exception_name': ke.__class__.__name__, 'info': traceback.format_exc()}
    except PydanticValilationError as pve:
        return jsonify({'error': pve.errors(),
                        'exception_name': pve.__class__.__name__, 'info': traceback.format_exc()})
    except TypeError as te:
        return jsonify({'error': f'Нет доступных данных для обработки',
                        'exception_name': te.__class__.__name__, 'info': traceback.format_exc()})


@app.route('/api/add_email', methods=['PUT'])
def add_email():
    """Функция получает из запроса person_id, email_address и email_type в формате JSON и добавляет запись в таблицу
     emails."""
    try:
        # Из запроса получаем JSON c данными
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation
        email_data = EmailData(**request_data)
        # Передаем данные в метод модели Email add_email
        new_email = Email.add_email(email_data)
        return jsonify(new_email)
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})
    except KeyError as ke:
        return {'error': f'В полученных данных отсутствует обязательный аргумент - {ke}',
                'exception_name': ke.__class__.__name__, 'info': traceback.format_exc()}
    except TypeError as te:
        return jsonify({'error': f'Нет доступных данных для обработки',
                        'exception_name': te.__class__.__name__, 'info': traceback.format_exc()})
    except PydanticValilationError as pve:
        return jsonify({'error': pve.errors(),
                        'exception_name': pve.__class__.__name__, 'info': traceback.format_exc()})


@app.route('/api/update_email', methods=['PATCH'])
def update_email():
    """Функция принимает данные из JSON в теле запроса и обновляет данные в таблице emails по указанному person_id
    и old_email_address"""
    try:
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation
        email_data = EmailData(**request_data)
        # Передаем атрибуты и person_id в метод модели Email update_email
        emails_update_result = Email.update_email(email_data)
        return jsonify(emails_update_result)
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})
    except KeyError as ke:
        return {'error': f'В полученных данных отсутствует обязательный аргумент - {ke}',
                'exception_name': ke.__class__.__name__, 'info': traceback.format_exc()}
    except TypeError as te:
        return jsonify({'error': f'Нет доступных данных для обработки',
                        'exception_name': te.__class__.__name__, 'info': traceback.format_exc()})
    except PydanticValilationError as pve:
        return jsonify({'error': pve.errors(),
                        'exception_name': pve.__class__.__name__, 'info': traceback.format_exc()})


@app.route('/api/delete_email', methods=['DELETE'])
def delete_email():
    """Функция получает JSON и по указанному в нем person_id и email_address удаляет указанный email"""
    try:
        # Из запроса получаем JSON c person_id и номером телефона для удаления
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation
        email_data = EmailData(**request_data)
        # Передаем данные в метод delete_email модели Email
        email_to_delete = Email.delete_email(email_data)
        return jsonify(email_to_delete)
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})
    except KeyError as ke:
        return {'error': f'В полученных данных отсутствует обязательный аргумент - {ke}',
                'exception_name': ke.__class__.__name__, 'info': traceback.format_exc()}
    except TypeError as te:
        return jsonify({'error': f'Нет доступных данных для обработки',
                        'exception_name': te.__class__.__name__, 'info': traceback.format_exc()})
    except PydanticValilationError as pve:
        return jsonify({'error': pve.errors(),
                        'exception_name': pve.__class__.__name__, 'info': traceback.format_exc()})
