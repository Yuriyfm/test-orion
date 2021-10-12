from sqlalchemy import exc
from sqlalchemy.orm.exc import UnmappedInstanceError
from orion import app, db
from flask import request, jsonify, Response
from orion.models import Person, Phone, Email
from orion.data_validation import add_person_data_validation, update_person_data_validation, add_phone_data_validation, \
    add_email_data_validation, id_validation, sort_data_persons, sort_data_phones, sort_data_emails
from werkzeug.exceptions import BadRequest

# В данном модуле описаны методы обработки запросов к API по сущностям Person, Phone и Email.


@app.errorhandler(404)
def page_not_found(e):
    return ('Неверный URL адрес')


# Методы для сущности Person
@app.route('/api/get_persons_list', methods=['POST'])
def get_persons_list():
    '''Функция принимает POST-запрос с данными для сортировки и возвращает отсортированные
    записи из таблицы persons в формате JSON. Если данных для сортировки нет, возвращается несортированный список'''
    try:
        if not request.get_json():
            all_persons = Person.get_all_persons()
            return jsonify(all_persons)
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation
        validation = sort_data_persons(request_data)
        if validation != 'Data is valid':
            return validation
        # Передаем данные в метод get_all_persons модели Person
        all_persons = Person.get_all_persons(sorted_by=request_data['sorted_by'],
                                             order=request_data['order'])
        return jsonify(all_persons)
        # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest:
        return ('структура данных не соответствует формату JSON')

@app.route('/api/get_person', methods=['POST'])
def get_person():
    '''Функция принимает POST-запрос c person_id  в формате JSON и возвращает запись из таблицы persons в формате JSON'''
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
        return ({'Persons': person.json()})
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest:
        return ('структура данных не соответствует формату JSON')
    # ловим ошибку на отсутсвие person_id в БД
    except AttributeError as atr:
        return ('Контакт с указанным person_id не найден')


@app.route('/api/add_person', methods=['PUT'])
def add_person():
    '''Функция, принимает данные из JSON в теле запроса в виде списка словарей, проверяет валидность данных с помощью
     модуля data_validation и сохраняет полученные данные в таблицу persons. Поддерживается возможность сохранения
    данных с related сущностями Phone и Email в связанные таблицы и добавление нескольких контактов в БД за один запрос.'''
    try:
        # Из запроса получаем JSON c данными Person и related cущностей и сохраняем их в request_data
        request_data = request.get_json()
        logging_upload_process = []
        # Проводим валидацию полученных атрибутов в модуле data_validation с помощью regex
        validation = add_person_data_validation(request_data)
        if validation != 'Data is valid':
            return validation
        for item in request_data:
            try:
                # Передаем атрибуты из item в метод add_person модели Person для добавления данных в БД
                new_person = Person.add_person(
                    file_path=item['file_path'], full_name=item['full_name'],
                    gender=item['gender'], birthday=item['birthday'],
                    address=item['address'], phones=item['phones'], emails=item['emails'])
                logging_upload_process.append(f'Контакт {item["full_name"]} успешно добавлен в БД c person_id '
                                              f'= {new_person.person_id}\n\n')
            # ловим ошибку нарушения уникальности по столбцам email_address и phone_number и делаем session rollback
            except exc.IntegrityError as int:
                logging_upload_process.append(f'При добавлении данных контакта {item["full_name"]} произошла ошибка'
                                              f' нарушения уникальности, по одному из столбцов - email_address, phone_number.'
                                              f' {int.args}.   \n\n')
                db.session.rollback()

        logging_upload_process.append(f'Всего обработано {len(request_data)} контактов')
        return Response(logging_upload_process)
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest:
        return ('структура данных не соответствует формату JSON')


@app.route('/api/update_person', methods=['PATCH'])
def update_person():
    '''Функция принимает данные из JSON в теле запроса и обновляет данные в таблице persons по указанному person_id '''
    try:
        # Из запроса получаем JSON c данными Person
        request_data = request.get_json()
    # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = update_person_data_validation(request_data)
        if validation != 'Data is valid':
            return validation
    # Передаем атрибуты из request_data в метод update_person модели Person для изменения данных в БД
        Person.update_person(
            file_path=request_data['file_path'], full_name=request_data['full_name'],
            gender=request_data['gender'], birthday=request_data['birthday'],
            address=request_data['address'], person_id=request_data['person_id'])
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest as bad:
        return ('структура данных не соответствует формату JSON')
    # ловим ошибку на отсутсвие person_id в БД
    except AttributeError as atr:
        return ('Контакт с указанным person_id не найден')
    return (f"Данные контакта {request_data['full_name']} обновлены")


@app.route('/api/delete_person', methods=['DELETE'])
def remove_person():
    '''Функция получает JSON и по указанному в нем person_id каскадно удаляет данные из таблицы persons и связанных таблиц'''
    try:
        # Из запроса получаем JSON c person_id
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = id_validation(request_data)
        if validation != 'Data is valid':
            return validation
        person_id = request_data['person_id']
        Person.delete_person(person_id)
    # ловим ошибку на отсутствие контакта в БД
    except UnmappedInstanceError:
        return (f'Контакт с person_id = {person_id} не найден в БД')
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest as bad:
        return ('структура данных не соответствует формату JSON')
    return (f"Данные контакта с person_id = {person_id} удалены вместе с данными из связанных таблиц")


# Методы для сущности Phone
@app.route('/api/get_phones_list', methods=['POST'])
def get_phones_list():
    '''Функция принимает POST-запрос с данными для сортировки и возвращает отсортированные
    записи из таблицы phones в формате JSON. Если данных для сортировки нет, возвращается несортированный список'''
    try:
        if not request.get_json():
            all_phones = Phone.get_all_phones()
            return jsonify(all_phones)
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation
        validation = sort_data_phones(request_data)
        if validation != 'Data is valid':
            return validation
        # Передаем данные в метод get_all_phones модели Phones
        all_phones = Phone.get_all_phones(sorted_by=request_data['sorted_by'],
                                             order=request_data['order'])
        return jsonify(all_phones)
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest:
        return ('структура данных не соответствует формату JSON')


@app.route('/api/get_phone', methods=['POST'])
def get_phone():
    '''Функция принимает POST-запрос c person_id  в формате JSON и возвращает запись из таблицы phones в формате JSON'''
    try:
        # Из запроса получаем JSON c person_id
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = id_validation(request_data)
        if validation != 'Data is valid':
            return validation
        person_id = request_data['person_id']
        phone = Phone.get_phone(person_id)
        return ({'Phone': phone.json()})
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest:
        return ('структура данных не соответствует формату JSON')
    # ловим ошибку на отсутсвие person_id в БД
    except AttributeError as atr:
        return ('Контакт с указанным person_id не найден')


@app.route('/api/add_phone', methods=['PUT'])
def add_phone():
    '''Функция получает из запроса person_id, phone_number и phone_type в формате JSON и добавляет запись в таблицу phones.'''
    try:
        # Из запроса получаем JSON c данными
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = add_phone_data_validation(request_data)
        if validation != 'Data is valid':
            return validation
        # Передаем атрибуты и person_id в метод модели Phone add_phone
        Phone.add_phone(person_id=request_data["person_id"], phone_number=request_data["phone_number"],
                                    phone_type=request_data["phone_type"])
        return (
            f"Новый номер телефона - {request_data['phone_number']} добавлен в контакт с person_id = {request_data['person_id']}")
        # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest:
        return ('структура данных не соответствует формату JSON')
    # ловим ошибку нарушения уникальности по столбцу phone_number или отсутствие person_id в БД
    except exc.IntegrityError as int:
        return (f'При добавлении номера телефона в контакт с person_id = {request_data["person_id"]} произошла ошибка.'
                f'{int.args}')


@app.route('/api/update_phone', methods=['PATCH'])
def update_phone():
    '''Функция принимает данные из JSON в теле запроса и обновляет данные в таблице phones по указанному person_id '''
    # сохраняем данные из JSON в request_data
    try:
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = add_phone_data_validation(request_data)
        if validation != 'Data is valid':
            return validation
        # Передаем атрибуты и person_id в метод модели Phone update_phone
        Phone.update_phone(person_id=request_data["person_id"], phone_number=request_data["phone_number"],
                           phone_type=request_data["phone_type"])
        return (f"Данные телефона контакта c person_id = {request_data['person_id']} обновлены")
    # ловим ошибку нарушения уникальности по столбцу phone_number
    except exc.IntegrityError as int:
        return (f'При добавлении номера телефона в контакт с person_id = {request_data["person_id"]} произошла ошибка.'
                f'{int.args}')
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest as bad:
        return ('структура данных не соответствует формату JSON')
    # ловим ошибку на отсутсвие person_id в БД
    except AttributeError as atr:
        return ('Контакт с указанным person_id не найден')


@app.route('/api/delete_phone', methods=['DELETE'])
def remove_phone():
    '''Функция получает JSON и по указанному в нем person_id удаляет данные из таблицы phones'''
    try:
        # Из запроса получаем JSON c person_id
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = id_validation(request_data)
        if validation != 'Data is valid':
            return validation
        person_id = request_data['person_id']
        # Передаем person_id в метод модели Phone delete_phone
        delete_phone = Phone.delete_phone(person_id)
        return (f"Номер телефона - {delete_phone.phone_number} контакта с person_id = {person_id} удален.")
    # ловим ошибку на отсутствие контакта в БД
    except UnmappedInstanceError:
        return (f'Контакт с person_id = {person_id} не найден в БД')
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest as bad:
        return ('структура данных не соответствует формату JSON')
    # ловим ошибку на отсутсвие person_id в БД
    except AttributeError as atr:
        return ('Контакт с указанным person_id не найден')


# методы для сущности Email
@app.route('/api/get_emails_list', methods=['POST'])
def get_emails_list():
    '''Функция принимает POST-запрос с данными для сортировки и возвращает отсортированные
    записи из таблицы emails в формате JSON. Если данных для сортировки нет, возвращается несортированный список'''
    try:
        if not request.get_json():
            all_emails = Email.get_all_emails()
            return jsonify(all_emails)
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation
        validation = sort_data_emails(request_data)
        if validation != 'Data is valid':
            return validation
        # Передаем данные в метод get_all_emails модели Email
        all_emails = Email.get_all_emails(sorted_by=request_data['sorted_by'],
                                             order=request_data['order'])
        return jsonify(all_emails)
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest:
        return ('структура данных не соответствует формату JSON')


@app.route('/api/get_email', methods=['POST'])
def get_email():
    '''Функция принимает POST-запрос c person_id  в формате JSON и возвращает запись из таблицы emails в формате JSON'''
    try:
        # Из запроса получаем JSON c person_id
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = id_validation(request_data)
        if validation != 'Data is valid':
            return validation
        person_id = request_data['person_id']
        email = Email.get_email(person_id)
        return ({'Email': email.json()})
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest:
        return ('структура данных не соответствует формату JSON')
    # ловим ошибку на отсутсвие person_id в БД
    except AttributeError as atr:
        return ('Контакт с указанным person_id не найден')


@app.route('/api/add_email', methods=['PUT'])
def add_email():
    '''Функция получает из запроса person_id, email_address и email_type в формате JSON и добавляет запись в таблицу emails.'''
    try:
        # Из запроса получаем JSON c данными
        request_data = request.get_json()
        # ловим ошибку на несоответсвие входящих данных структуре JSON
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = add_email_data_validation(request_data)
        if validation != 'Data is valid':
            return validation
        new_email = Email.add_email(person_id=request_data["person_id"], email_address=request_data["email_address"],
                                    email_type=request_data["email_type"])
        # ловим ошибку нарушения уникальности по столбцу email_address
        return (f"Новый адрес электронной почты - {request_data['email_address']} добавлен в контакт с person_id = "
                f"{request_data['person_id']}")
        # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest:
        return ('структура данных не соответствует формату JSON')
    # ловим ошибку нарушения уникальности по столбцу email_address или отсутствие person_id в БД
    except exc.IntegrityError as int:
        return (f'При добавлении номера телефона в контакт с person_id = {request_data["person_id"]} произошла ошибка.'
                f'{int.args}')


@app.route('/api/update_email', methods=['PATCH'])
def update_email():
    '''Функция принимает данные из JSON в теле запроса и обновляет данные в таблице emails по указанному person_id '''
    try:
        # сохраняем данные из JSON в request_data
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = add_email_data_validation(request_data)
        if validation != 'Data is valid':
            return validation
        # Передаем атрибуты и person_id в метод модели Email update_email
        Email.update_email(person_id=request_data["person_id"], email_address=request_data["email_address"],
                           email_type=request_data["email_type"])
        return (f"Данные электронной почты контакта c person_id = {request_data['person_id']} обновлены")
    # ловим ошибку нарушения уникальности по столбцу email_address
    except exc.IntegrityError as int:
        return (f'При добавлении номера телефона в контакт с person_id = {request_data["person_id"]} произошла ошибка.'
                f'{int.args}')
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest as bad:
        return ('структура данных не соответствует формату JSON')
    # ловим ошибку на отсутсвие person_id в БД
    except AttributeError as atr:
        return ('Контакт с указанным person_id не найден')


@app.route('/api/delete_email', methods=['DELETE'])
def remove_email():
    '''Функция получает JSON и по указанному в нем person_id удаляет данные из таблицы emails'''
    try:
        # Из запроса получаем JSON c person_id
        request_data = request.get_json()
        # Проводим валидацию полученных арибутов в модуле data_validation с помощью regex
        validation = id_validation(request_data)
        if validation != 'Data is valid':
            return validation
        person_id = request_data['person_id']
        # передаем person_id в метод модели Email delete_email
        delete_email = Email.delete_email(person_id)
        return (f"Адрес электронной почты - {delete_email.email_address} контакта с person_id = {person_id} удален.")
    # ловим ошибку на отсутствие контакта в БД
    except UnmappedInstanceError:
        return (f'Контакт с person_id = {person_id} не найден в БД')
    # ловим ошибку на несоответсвие входящих данных структуре JSON
    except BadRequest as bad:
        return ('структура данных не соответствует формату JSON')
    # ловим ошибку на отсутсвие person_id в БД
    except AttributeError as atr:
        return ('Контакт с указанным person_id не найден')
