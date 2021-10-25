from sqlalchemy import exc
from orion import app
from flask import request, jsonify
from orion.models import Person, Phone, Email
from orion.data_validation import data_validation
from werkzeug.exceptions import BadRequest
import traceback

# В данном модуле описаны методы обработки запросов к API по сущностям Person, Phone и Email.


@app.errorhandler(404)
def page_not_found():
    """Обработчик неправильных URL"""
    return jsonify({'Ошибка URL адреса': 'URL в запросе не соответствует ни одному из маршрутов'})


# Методы для сущности Person
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
        validation = data_validation(request_data)
        if validation != 'Data is valid':
            return jsonify(validation)
        # Передаем данные в метод get_all_persons модели Person с данынми для сортировки
        all_persons = Person.get_all_persons(sorted_by=request_data['sorted_by'],
                                             order=request_data['order'])
        return jsonify(all_persons)
        # Ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})
    except KeyError as ke:
        return {'error': f'В полученных данных отсутствует обязательный аргумент - {ke}',
                'exception_name': ke.__class__.__name__, 'info': traceback.format_exc()}


@app.route('/api/get_person', methods=['POST'])
def get_person():
    """Функция принимает POST-запрос c person_id  в формате JSON и возвращает запись из таблицы persons в формате JSON"""
    try:
        # Из запроса получаем JSON c person_id
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = data_validation(request_data)
        if validation != 'Data is valid':
            return jsonify(validation)
        # Передаем person_id в метод get_person модели Person
        person = Person.get_person(person_id=request_data["person_id"])
        return jsonify(person)
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})


@app.route('/api/add_person', methods=['PUT'])
def add_person():
    """Функция, принимает данные из JSON в теле запроса в виде списка словарей, проверяет валидность данных с помощью
     модуля data_validation и сохраняет полученные данные в таблицу persons. Поддерживается возможность сохранения
    данных с related сущностями Phone и Email в связанные таблицы и добавление нескольких контактов в БД за один запрос."""
    try:
        # Из запроса получаем JSON c данными Person и related cущностей и сохраняем их в request_data
        request_data = request.get_json()
        # Проходим в цикле по списку контактов и роводим валидацию полученных атрибутов в модуле data_validation
        for item in request_data:
            validation = data_validation(item)
            if validation != 'Data is valid':
                return jsonify({f"Ошибка валидации данных контакта номер {request_data.index(item)+1}": validation})
        # Передаем данные в метод add_person сущности Person для добавления контактов в БД
        add_person_result = Person.add_person(request_data)
        return add_person_result
    except TypeError as te:
        return jsonify({'error': 'структура данных не соответствует ожидаемому формату. Ожидаеся список контактов',
                        'exception_name': te.__class__.__name__, 'info': traceback.format_exc()})
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})


@app.route('/api/update_person', methods=['PATCH'])
def update_person():
    """Функция принимает данные из JSON в теле запроса и обновляет данные в таблице persons по указанному person_id"""
    try:
        # Из запроса получаем JSON c данными Person
        request_data = request.get_json()
    # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = data_validation(request_data)
        if validation != 'Data is valid':
            return jsonify(validation)
    # Передаем атрибуты из request_data в метод update_person модели Person для изменения данных в БД
        update_result = Person.update_person(
                                      file_path=request_data['file_path'], full_name=request_data['full_name'],
                                      gender=request_data['gender'], birthday=request_data['birthday'],
                                      address=request_data['address'], person_id=request_data['person_id'])
        return jsonify(update_result)
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})


@app.route('/api/delete_person', methods=['DELETE'])
def delete_person():
    """Функция получает JSON и по указанному в нем person_id каскадно удаляет данные из таблицы persons и связанных
    таблиц"""
    try:
        # Из запроса получаем JSON c person_id
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = data_validation(request_data)
        if validation != 'Data is valid':
            return jsonify(validation)
        person_id = request_data['person_id']
        person_delete_result = Person.delete_person(person_id)
        return jsonify(person_delete_result)
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})


# Методы для сущности Phone
@app.route('/api/get_phones_list', methods=['POST'])
def get_phones_list():
    """Функция принимает POST-запрос с данными для сортировки и возвращает отсортированные
    записи из таблицы phones в формате JSON. Если данных для сортировки нет, возвращается несортированный список"""
    try:
        if not request.get_json():
            all_phones = Phone.get_all_phones()
            return jsonify(all_phones)
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation
        validation = data_validation(request_data)
        if validation != 'Data is valid':
            return jsonify(validation)
        # Передаем данные в метод get_all_phones модели Phones
        all_phones = Phone.get_all_phones(sorted_by=request_data['sorted_by'],
                                          order=request_data['order'])
        return jsonify(all_phones)
    # Ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})
    except KeyError as ke:
        return {'error': f'В полученных данных отсутствует обязательный аргумент - {ke}',
                'exception_name': ke.__class__.__name__, 'info': traceback.format_exc()}

@app.route('/api/get_phone', methods=['POST'])
def get_phone():
    """Функция принимает POST-запрос c person_id  в формате JSON и возвращает запись или записи из таблицы phones
    в формате JSON"""
    try:
        # Из запроса получаем JSON c person_id
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = data_validation(request_data)
        if validation != 'Data is valid':
            return jsonify(validation)
        person_id = request_data['person_id']
        # Отправляем person_id в метод get_phone и получаем все записи с соответствующим id
        phone = Phone.get_phone(person_id)
        return jsonify(phone)
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})


@app.route('/api/add_phone', methods=['PUT'])
def add_phone():
    """Функция получает из запроса person_id, phone_number и phone_type в формате JSON и добавляет запись в таблицу
    phones."""
    try:
        # Из запроса получаем JSON c данными
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = data_validation(request_data)
        if validation != 'Data is valid':
            return jsonify(validation)
        # Передаем атрибуты и person_id в метод модели Phone add_phone
        new_phone = Phone.add_phone(person_id=request_data["person_id"], phone_number=request_data["phone_number"],
                                    phone_type=request_data["phone_type"])
        return jsonify(new_phone)
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})
    # ловим ошибку нарушения уникальности по аттрибуту phone_number
    except exc.IntegrityError as ie:
        return jsonify({'error': f'Номер телефона {request_data["phone_number"]} уже есть в БД.',
                        'exception_name': ie.__class__.__name__, 'info': traceback.format_exc()})
    except KeyError as ke:
        return {'error': f'В полученных данных отсутствует обязательный аргумент - {ke}',
                'exception_name': ke.__class__.__name__, 'info': traceback.format_exc()}

@app.route('/api/update_phone', methods=['PATCH'])
def update_phone():
    """Функция принимает данные из JSON в теле запроса и обновляет данные в таблице phones по указанному person_id
    и old_phone_number"""
    # сохраняем данные из JSON в request_data
    try:
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = data_validation(request_data)
        if validation != 'Data is valid':
            return jsonify(validation)
        # Передаем атрибуты и person_id в метод модели Phone update_phone
        phones_update_result = Phone.update_phone(person_id=request_data["person_id"],
                                                  phone_number=request_data["phone_number"],
                                                  phone_type=request_data["phone_type"],
                                                  old_phone_number=request_data["old_phone_number"])
        return jsonify(phones_update_result)
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})
    # ловим ошибку нарушения уникальности по аттрибуту phone_number
    except exc.IntegrityError as ie:
        return jsonify({'error': f'Номер телефона {request_data["phone_number"]} уже есть в БД.',
                        'exception_name': ie.__class__.__name__, 'info': traceback.format_exc()})
    except KeyError as ke:
        return {'error': f'В полученных данных отсутствует обязательный аргумент - {ke}',
                'exception_name': ke.__class__.__name__, 'info': traceback.format_exc()}

@app.route('/api/delete_phone', methods=['DELETE'])
def delete_phone():
    """Функция получает JSON и по указанному в нем person_id и phone_number удаляет указанный телефон"""
    try:
        # Из запроса получаем JSON c person_id
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = data_validation(request_data)
        if validation != 'Data is valid':
            return jsonify(validation)
        # Передаем person_id и phone_number в метод delete_phone модели Phone
        phone_to_delete = Phone.delete_phone(person_id=request_data['person_id'],
                                             phone_number=request_data['phone_number'])
        return jsonify(phone_to_delete)
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})


# методы для сущности Email
@app.route('/api/get_emails_list', methods=['POST'])
def get_emails_list():
    """Функция принимает POST-запрос с данными для сортировки и возвращает отсортированные
    записи из таблицы emails в формате JSON. Если данных для сортировки нет, возвращается несортированный список"""
    try:
        if not request.get_json():
            all_emails = Email.get_all_emails()
            return jsonify(all_emails)
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation
        validation = data_validation(request_data)
        if validation != 'Data is valid':
            return jsonify(validation)
        # Передаем данные в метод get_all_emails модели Email
        all_emails = Email.get_all_emails(sorted_by=request_data['sorted_by'],
                                          order=request_data['order'])
        return jsonify(all_emails)
    # Ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})
    except KeyError as ke:
        return {'error': f'В полученных данных отсутствует обязательный аргумент - {ke}',
                'exception_name': ke.__class__.__name__, 'info': traceback.format_exc()}

@app.route('/api/get_email', methods=['POST'])
def get_email():
    """Функция принимает POST-запрос c person_id  в формате JSON и возвращает запись или записи из таблицы emails
    в формате JSON"""
    try:
        # Из запроса получаем JSON c person_id
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = data_validation(request_data)
        if validation != 'Data is valid':
            return jsonify(validation)
        person_id = request_data['person_id']
        # Отправляем person_id в метод get_email и получаем все записи с соответствующим id
        email = Email.get_email(person_id)
        return jsonify(email)
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})


@app.route('/api/add_email', methods=['PUT'])
def add_email():
    """Функция получает из запроса person_id, email_address и email_type в формате JSON и добавляет запись в таблицу
     emails."""
    try:
        # Из запроса получаем JSON c данными
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = data_validation(request_data)
        if validation != 'Data is valid':
            return jsonify(validation)
        new_email = Email.add_email(person_id=request_data["person_id"], email_address=request_data["email_address"],
                                    email_type=request_data["email_type"])
        return jsonify(new_email)
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})
    # ловим ошибку нарушения уникальности по аттрибуту email_address
    except exc.IntegrityError as ie:
        return jsonify({'error': f'email {request_data["email_address"]} уже есть в БД.',
                        'exception_name': ie.__class__.__name__, 'info': traceback.format_exc()})


@app.route('/api/update_email', methods=['PATCH'])
def update_email():
    """Функция принимает данные из JSON в теле запроса и обновляет данные в таблице emails по указанному person_id
    и old_email_address"""
    try:
        # сохраняем данные из JSON в request_data
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = data_validation(request_data)
        if validation != 'Data is valid':
            return jsonify(validation)
        # Передаем атрибуты и person_id в метод модели Email update_email
        emails_for_update = Email.update_email(person_id=request_data["person_id"],
                                               old_email_address=request_data["old_email_address"],
                                               email_address=request_data["email_address"],
                                               email_type=request_data["email_type"])
        return jsonify(emails_for_update)
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})
    # ловим ошибку нарушения уникальности по аттрибуту email_address
    except exc.IntegrityError as ie:
        return jsonify({'error': f'email {request_data["email_address"]} уже есть в БД.',
                        'exception_name': ie.__class__.__name__, 'info': traceback.format_exc()})


@app.route('/api/delete_email', methods=['DELETE'])
def delete_email():
    """Функция получает JSON и по указанному в нем person_id и email_address удаляет указанный email"""
    try:
        # Из запроса получаем JSON c person_id
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = data_validation(request_data)
        if validation != 'Data is valid':
            return jsonify(validation)
        # Передаем person_id и email_address в метод delete_email модели Email
        email_to_delete = Email.delete_email(person_id=request_data['person_id'],
                                             email_address=request_data['email_address'])
        return jsonify(email_to_delete)
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest as be:
        return jsonify({'error': 'Структура данных не соответсвует формату JSON', 'exception_name':
                        be.__class__.__name__, 'info': traceback.format_exc()})
