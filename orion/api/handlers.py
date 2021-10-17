from sqlalchemy import exc
from sqlalchemy.orm.exc import UnmappedInstanceError
from orion import app
from flask import request, jsonify, Response
from orion.models import Person, Phone, Email
from orion.data_validation import add_person_data_validation, id_validation, sort_list_data_validation, \
    add_data_validation, update_data_validation, delete_validation
from werkzeug.exceptions import BadRequest

# В данном модуле описаны методы обработки запросов к API по сущностям Person, Phone и Email.


@app.errorhandler(404)
def page_not_found():
    return 'Неверный URL адрес'


# Методы для сущности Person
@app.route('/api/get_persons_list', methods=['POST'])
def get_persons_list():
    """Функция принимает POST-запрос с данными для сортировки и возвращает отсортированные
    записи из таблицы persons в формате JSON. Если данных для сортировки нет, возвращается несортированный список"""
    func_name = 'get_persons_list'
    try:
        if not request.get_json():
            all_persons = Person.get_all_persons()
            return jsonify({'persons_list': all_persons})
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation
        validation = sort_list_data_validation(request_data, func_name)
        if validation != 'Data is valid':
            return validation
        # Передаем данные в метод get_all_persons модели Person
        all_persons = Person.get_all_persons(sorted_by=request_data['sorted_by'],
                                             order=request_data['order'])
        return jsonify({'persons list': all_persons})
        # Ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest:
        return 'структура данных не соответствует формату JSON'


@app.route('/api/get_person', methods=['POST'])
def get_person():
    """Функция принимает POST-запрос c person_id  в формате JSON и возвращает запись из таблицы persons в формате JSON"""
    try:
        # Из запроса получаем JSON c person_id
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = id_validation(request_data)
        if validation != 'Data is valid':
            return validation
        person_id = request_data['person_id']
        # Передаем person_id в метод get_person модели Person
        person = Person.get_person(person_id)
        return {'Person': person.json()}
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest:
        return 'структура данных не соответствует формату JSON'
    # ловим ошибку на отсутсвие person_id в БД
    except AttributeError:
        return 'Контакт с указанным person_id не найден'


@app.route('/api/add_person', methods=['PUT'])
def add_person():
    """Функция, принимает данные из JSON в теле запроса в виде списка словарей, проверяет валидность данных с помощью
     модуля data_validation и сохраняет полученные данные в таблицу persons. Поддерживается возможность сохранения
    данных с related сущностями Phone и Email в связанные таблицы и добавление нескольких контактов в БД за один запрос."""
    try:
        # Из запроса получаем JSON c данными Person и related cущностей и сохраняем их в request_data
        request_data = request.get_json()
        logging_upload_process = []
        # Проводим валидацию полученных атрибутов в модуле data_validation с помощью regex
        validation = add_person_data_validation(request_data)
        if validation != 'Data is valid':
            return validation
        for item in request_data:
            # Передаем атрибуты из item в метод add_person модели Person для добавления данных в БД
            add_person_result = Person.add_person(
                file_path=item['file_path'], full_name=item['full_name'],
                gender=item['gender'], birthday=item['birthday'],
                address=item['address'], phones=item['phones'], emails=item['emails'])
            logging_upload_process.append(add_person_result)
        logging_upload_process.append(f'Всего обработано {len(request_data)} контактов')
        return Response(logging_upload_process)
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest:
        return 'структура данных не соответствует формату JSON'


@app.route('/api/update_person', methods=['PATCH'])
def update_person():
    """Функция принимает данные из JSON в теле запроса и обновляет данные в таблице persons по указанному person_id"""
    func_name = 'update_person'
    try:
        # Из запроса получаем JSON c данными Person
        request_data = request.get_json()
    # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = update_data_validation(request_data, func_name)
        if validation != 'Data is valid':
            return validation
    # Передаем атрибуты из request_data в метод update_person модели Person для изменения данных в БД
        update_result = Person.update_person(
                                      file_path=request_data['file_path'], full_name=request_data['full_name'],
                                      gender=request_data['gender'], birthday=request_data['birthday'],
                                      address=request_data['address'], person_id=request_data['person_id'])
        return update_result
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest:
        return 'структура данных не соответствует формату JSON'
    # ловим ошибку на отсутсвие person_id в БД
    except AttributeError:
        return 'Контакт с указанным person_id не найден'


@app.route('/api/delete_person', methods=['DELETE'])
def delete_person():
    """Функция получает JSON и по указанному в нем person_id каскадно удаляет данные из таблицы persons и связанных
    таблиц"""
    try:
        # Из запроса получаем JSON c person_id
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = id_validation(request_data)
        if validation != 'Data is valid':
            return validation
        person_id = request_data['person_id']
        person_delete_result = Person.delete_person(person_id)
        return person_delete_result
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest:
        return 'структура данных не соответствует формату JSON'


# Методы для сущности Phone
@app.route('/api/get_phones_list', methods=['POST'])
def get_phones_list():
    """Функция принимает POST-запрос с данными для сортировки и возвращает отсортированные
    записи из таблицы phones в формате JSON. Если данных для сортировки нет, возвращается несортированный список"""
    func_name = 'get_phones_list'
    try:
        if not request.get_json():
            all_phones = Phone.get_all_phones()
            return jsonify({'phones_list': all_phones})
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation
        validation = sort_list_data_validation(request_data, func_name)
        if validation != 'Data is valid':
            return validation
        # Передаем данные в метод get_all_phones модели Phones
        all_phones = Phone.get_all_phones(sorted_by=request_data['sorted_by'],
                                          order=request_data['order'])
        return jsonify({'phones_list': all_phones})
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest:
        return 'структура данных не соответствует формату JSON'


@app.route('/api/get_phone', methods=['POST'])
def get_phone():
    """Функция принимает POST-запрос c person_id  в формате JSON и возвращает запись или записи из таблицы phones
    в формате JSON"""
    try:
        # Из запроса получаем JSON c person_id
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = id_validation(request_data)
        if validation != 'Data is valid':
            return validation
        person_id = request_data['person_id']
        # Отправляем person_id в метод get_phone и получаем все записи с соответствующим id
        phone = Phone.get_phone(person_id)
        return {'Phone': phone}
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest:
        return 'структура данных не соответствует формату JSON'
    # ловим ошибку на отсутсвие person_id в БД
    except AttributeError:
        return 'Контакт с указанным person_id не найден'


@app.route('/api/add_phone', methods=['PUT'])
def add_phone():
    """Функция получает из запроса person_id, phone_number и phone_type в формате JSON и добавляет запись в таблицу
    phones."""
    func_name = 'add_phone'
    try:
        # Из запроса получаем JSON c данными
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = add_data_validation(request_data, func_name)
        if validation != 'Data is valid':
            return validation
        # Передаем атрибуты и person_id в метод модели Phone add_phone
        new_phone = Phone.add_phone(person_id=request_data["person_id"], phone_number=request_data["phone_number"],
                                    phone_type=request_data["phone_type"])
        return new_phone
        # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest:
        return 'структура данных не соответствует формату JSON'
    # ловим ошибку нарушения уникальности по столбцу phone_number
    except exc.IntegrityError as i:
        return (f'При добавлении номера телефона в контакт с person_id = {request_data["person_id"]} произошла ошибка.'
                f'{i.args}')


@app.route('/api/update_phone', methods=['PATCH'])
def update_phone():
    """Функция принимает данные из JSON в теле запроса и обновляет данные в таблице phones по указанному person_id
    и old_phone_number"""
    func_name = 'update_phone'
    # сохраняем данные из JSON в request_data
    try:
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = update_data_validation(request_data, func_name)
        if validation != 'Data is valid':
            return validation
        # Передаем атрибуты и person_id в метод модели Phone update_phone
        phones_update_result = Phone.update_phone(person_id=request_data["person_id"],
                                                  new_phone_number=request_data["new_phone_number"],
                                                  new_phone_type=request_data["new_phone_type"],
                                                  old_phone_number=request_data["old_phone_number"])
        return phones_update_result
    # ловим ошибку нарушения уникальности по столбцу phone_number
    except exc.IntegrityError as i:
        return (f'При добавлении номера телефона в контакт с person_id = {request_data["person_id"]} произошла ошибка.'
                f'{i.args}')
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest:
        return 'структура данных не соответствует формату JSON'
    # ловим ошибку на отсутсвие person_id в БД
    except AttributeError:
        return 'Контакт с указанным person_id не найден'


@app.route('/api/delete_phone', methods=['DELETE'])
def delete_phone():
    """Функция получает JSON и по указанному в нем person_id и phone_number удаляет указанный телефон"""
    func_name = 'delete_phone'
    try:
        # Из запроса получаем JSON c person_id
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = delete_validation(request_data, func_name)
        if validation != 'Data is valid':
            return validation
        # Передаем person_id и phone_number в метод delete_phone модели Phone
        phone_to_delete = Phone.delete_phone(person_id=request_data['person_id'],
                                             phone_number=request_data['phone_number'])
        return phone_to_delete
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest:
        return 'структура данных не соответствует формату JSON'


# методы для сущности Email
@app.route('/api/get_emails_list', methods=['POST'])
def get_emails_list():
    """Функция принимает POST-запрос с данными для сортировки и возвращает отсортированные
    записи из таблицы emails в формате JSON. Если данных для сортировки нет, возвращается несортированный список"""
    func_name = 'get_emails_list'
    try:
        if not request.get_json():
            all_emails = Email.get_all_emails()
            return jsonify({'emails_list': all_emails})
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation
        validation = sort_list_data_validation(request_data, func_name)
        if validation != 'Data is valid':
            return validation
        # Передаем данные в метод get_all_emails модели Email
        all_emails = Email.get_all_emails(sorted_by=request_data['sorted_by'],
                                          order=request_data['order'])
        return jsonify({'emails_list': all_emails})
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest:
        return 'структура данных не соответствует формату JSON'


@app.route('/api/get_email', methods=['POST'])
def get_email():
    """Функция принимает POST-запрос c person_id  в формате JSON и возвращает запись или записи из таблицы emails
    в формате JSON"""
    try:
        # Из запроса получаем JSON c person_id
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = id_validation(request_data)
        if validation != 'Data is valid':
            return validation
        person_id = request_data['person_id']
        # Отправляем person_id в метод get_email и получаем все записи с соответствующим id
        email = Email.get_email(person_id)
        return jsonify({'Email': email})
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest:
        return 'структура данных не соответствует формату JSON'
    # ловим ошибку на отсутсвие person_id в БД
    except AttributeError:
        return 'Контакт с указанным person_id не найден'


@app.route('/api/add_email', methods=['PUT'])
def add_email():
    """Функция получает из запроса person_id, email_address и email_type в формате JSON и добавляет запись в таблицу
     emails."""
    func_name = 'add_email'
    try:
        # Из запроса получаем JSON c данными
        request_data = request.get_json()
        # ловим ошибку на несоответсвие входящих данных структуре JSON
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = add_data_validation(request_data, func_name)
        if validation != 'Data is valid':
            return validation
        new_email = Email.add_email(person_id=request_data["person_id"], email_address=request_data["email_address"],
                                    email_type=request_data["email_type"])
        return new_email
        # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest:
        return 'структура данных не соответствует формату JSON'
    # ловим ошибку нарушения уникальности по столбцу email_address
    except exc.IntegrityError as i:
        return f'При добавлении номера телефона в контакт с person_id = {new_email.person_id} произошла ошибка. {i.args}'


@app.route('/api/update_email', methods=['PATCH'])
def update_email():
    """Функция принимает данные из JSON в теле запроса и обновляет данные в таблице emails по указанному person_id
    и old_email_address"""
    func_name = 'update_email'
    try:
        # сохраняем данные из JSON в request_data
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = update_data_validation(request_data, func_name)
        if validation != 'Data is valid':
            return validation
        # Передаем атрибуты и person_id в метод модели Email update_email
        emails_for_update = Email.update_email(person_id=request_data["person_id"],
                                               old_email_address=request_data["old_email_address"],
                                               new_email_address=request_data["new_email_address"],
                                               new_email_type=request_data["new_email_type"])
        return emails_for_update
    # ловим ошибку нарушения уникальности по столбцу email_address
    except exc.IntegrityError as i:
        return f'При добавлении номера телефона в контакт с person_id = {request_data["person_id"]} произошла ошибка.' \
               f' {i.args}'
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest:
        return 'структура данных не соответствует формату JSON'
    # ловим ошибку на отсутсвие person_id в БД
    except AttributeError:
        return 'Контакт с указанным person_id не найден'


@app.route('/api/delete_email', methods=['DELETE'])
def delete_email():
    """Функция получает JSON и по указанному в нем person_id и email_address удаляет указанный email"""
    func_name = 'delete_email'
    try:
        # Из запроса получаем JSON c person_id
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = delete_validation(request_data, func_name)
        if validation != 'Data is valid':
            return validation
        # Передаем person_id и email_address в метод delete_email модели Email
        email_to_delete = Email.delete_email(person_id=request_data['person_id'],
                                             email_address=request_data['email_address'])
        return email_to_delete
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest:
        return 'структура данных не соответствует формату JSON'
