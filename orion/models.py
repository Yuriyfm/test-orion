from orion import db
from sqlalchemy import text, exc
import traceback


# В данном модуле находятся классы моделей таблиц и их методы обработки данных


class Person(db.Model):
    """Класс содержит модель таблицы persons и ее методы обработки данных"""
    __tablename__ = "persons"
    __table_args__ = {'extend_existing': True}
    person_id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(30), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    address = db.Column(db.String, nullable=False)
    phones = db.relationship("Phone", backref="persons", passive_deletes=True, cascade='all, delete-orphan')
    emails = db.relationship("Email", backref="persons", passive_deletes=True, cascade='all, delete-orphan')

    def json(self):
        """Метод сериализует данные полученные из БД в формат JSON"""
        return {'person_id': self.person_id, 'file_path': self.file_path,
                'full_name': self.full_name, 'gender': self.gender,
                'birthday': self.birthday, 'address': self.address}

    @staticmethod
    def get_all_persons(sorted_data=None):
        """"Метод принимает на вход параметры сортировки (если они есть) и возвращает список всех записей из
        таблицы persons"""
        try:
            if sorted_data:
                return {'response':
                        [Person.json(person) for person in Person.query.order_by(text(
                         sorted_data.sorted_by + ' ' + sorted_data.order)).all()]}
            return {'response': [Person.json(person) for person in Person.query.all()]}
        except exc.ProgrammingError as pe:
            return {
                'error': f'аттрибута {sorted_data.sorted_by} нет в таблице persons. Выберите один из следующих атрибутов - '
                         f'{", ".join([m.key for m in Person.__table__.columns])}',
                         'exception_name': pe.__class__.__name__,
                         'info': traceback.format_exc()}
        except exc.OperationalError as oe:
            return {'error': f'Не удалось подключиться к БД {db.engine.url.database}.',
                    'exception_name': oe.__class__.__name__, 'info': traceback.format_exc()}

    @staticmethod
    def get_person(person_id_obj):
        """"Метод принимает на вход person_id и возвращает соотвествующую запись из таблицы persons"""
        try:
            if not person_id_obj.person_id:
                return {'response': 'Запрос должен содержать обязательный атрибут person_id'}
            person = Person.query.filter_by(person_id=person_id_obj.person_id).first().json()
            if not person:
                return {'response': 'Контакт с указанным person_id не найден в БД'}
            return {'response': person}
        except exc.OperationalError as oe:
            return {'error': f'Не удалось подключиться к БД {db.engine.url.database}.',
                    'exception_name': oe.__class__.__name__, 'info': traceback.format_exc()}
        except KeyError as ke:
            return {'error': f'В полученных данных отсутствует обязательный аргумент - {ke}',
                    'exception_name': ke.__class__.__name__, 'info': traceback.format_exc()}
        except AttributeError as ae:
            return {'error': 'Контакт с указанным person_id не найден', 'exception_name': ae.__class__.__name__,
                    'info': traceback.format_exc()}

    @staticmethod
    def add_person(data):
        """Метод принимает на вход атрибуты сущности Person и related сущностей (если они есть) и добавляет записи в
        соответствующие таблицы"""
        # В цикле добавляем в базу контакты из списка. Если все контакты были добавлены делаем commit, если была ошибка
        # при добавлении хотя бы одного из контактов отменяем всё.
        for ind, item in enumerate(data):
            try:
                new_person = Person(file_path=item.file_path, full_name=item.full_name,
                                    gender=item.gender, birthday=item.birthday, address=item.address)
                db.session.add(new_person)
                db.session.flush()
                for phone in item.phones:
                    new_person_phone = Phone(person_id=new_person.person_id, phone_type=phone.phone_type,
                                             phone_number=phone.phone_number)
                    db.session.add(new_person_phone)
                    db.session.flush()
                for email in item.emails:
                    new_person_email = Email(person_id=new_person.person_id, email_type=email.email_type,
                                             email_address=email.email_address)
                    db.session.add(new_person_email)
                    db.session.flush()
            # ловим ошибку нарушения уникальности по столбцам email_address и phone_number
            except exc.IntegrityError as ie:
                db.session.rollback()
                return {
                    'error': f'При добавлении данных контакта {item["full_name"]} произошла ошибка нарушения уникальности, '
                             f'по одному из столбцов - email_address, phone_number.',
                    'exception_name': ie.__class__.__name__,
                    'info': traceback.format_exc()}
            except exc.OperationalError as oe:
                return {'error': f'Не удалось подключиться к БД {db.engine.url.database}.',
                        'exception_name': oe.__class__.__name__, 'info': traceback.format_exc()}
            except KeyError as ke:
                db.session.rollback()
                return {
                    'error': f'В полученных данных контакта номер {ind + 1} отсутствует обязательный аргумент - {ke}',
                    'exception_name': ke.__class__.__name__, 'info': traceback.format_exc()}
        db.session.commit()
        return {'response': f'{len(data)} контактов было добавлено в БД'}

    @staticmethod
    def update_person(person_data):
        """"Метод принимает на вход значения атрибутов сущности Person и обновляет данные в соответсвии с указанным
         person_id"""
        try:
            person_to_update = Person.query.filter_by(person_id=person_data.person_id).first()
            if not person_to_update:
                return {'response': f'Контакт с person_id = {person_data.person_id} не найден в БД'}
            person_to_update.file_path = person_data.file_path
            person_to_update.full_name = person_data.full_name
            person_to_update.gender = person_data.gender
            person_to_update.birthday = person_data.birthday
            person_to_update.address = person_data.address
            db.session.commit()
            return {'response': f'Данные контакта с person_id = {person_data.person_id} были изменены'}
        except exc.OperationalError as oe:
            return {'error': f'Не удалось подключиться к БД {db.engine.url.database}.',
                    'exception_name': oe.__class__.__name__, 'info': traceback.format_exc()}

    @staticmethod
    def delete_person(person_id_obj):
        """"Метод принимает на вход person_id и удаляет соответствующую запись из таблицы person и дочерних таблиц"""
        try:
            person_to_delete = Person.query.filter_by(person_id=person_id_obj.person_id).first()
            if not person_to_delete:
                return {'response': f'Контакт с person_id = {person_id_obj.person_id} не найден в БД'}
            db.session.delete(person_to_delete)
            db.session.commit()
            return {'response': f"Все данные контакта с person_id = {person_id_obj.person_id} были удалены"}
        except exc.OperationalError as oe:
            return {'error': f'Не удалось подключиться к БД {db.engine.url.database}.',
                    'exception_name': oe.__class__.__name__, 'info': traceback.format_exc()}
        except KeyError as ke:
            return {'error': f'В полученных данных отсутствует обязательный аргумент - {ke}',
                    'exception_name': ke.__class__.__name__, 'info': traceback.format_exc()}

    def __repr__(self):
        return f'<Person {self.full_name}>'


class Phone(db.Model):
    """Класс содержит модель таблицы phones и ее методы обработки данных"""
    __tablename__ = "phones"
    __table_args__ = {'extend_existing': True}
    person_id = db.Column(db.Integer, db.ForeignKey('persons.person_id', ondelete="CASCADE"), nullable=False)
    phone_type = db.Column(db.String(30), nullable=False)
    phone_number = db.Column(db.String(30), nullable=False, primary_key=True)

    def json(self):
        """Метод сериализует данные полученные из БД в формат JSON"""
        return {'person_id': self.person_id, 'phone_type': self.phone_type, 'phone_number': self.phone_number}

    @staticmethod
    def get_all_phones(sorted_data=None):
        """"Метод принимает на вход параметры сортировки (если они есть) и возвращает список всех записей из
        таблицы phones"""
        try:
            if sorted_data:
                return {'response':
                        [Phone.json(phone) for phone in Phone.query.order_by(text(sorted_data.sorted_by + ' '
                         + sorted_data.order)).all()]}
            return {'response': [Phone.json(phone) for phone in Phone.query.all()]}
        except exc.ProgrammingError as pe:
            return {'error': f'аттрибута {sorted_data.sorted_by} нет в таблице phones. Выберите один из следующих'
                             f'  атрибутов - {", ".join([m.key for m in Phone.__table__.columns])}',
                    'exception_name': pe.__class__.__name__,
                    'info': traceback.format_exc()}
        except exc.OperationalError as oe:
            return {'error': f'Не удалось подключиться к БД {db.engine.url.database}.',
                    'exception_name': oe.__class__.__name__, 'info': traceback.format_exc()}

    @staticmethod
    def get_phone(person_id_obj):
        """"Метод принимает на вход person_id и возвращает соотвествующую запись из таблицы phones"""
        try:
            person = Person.query.filter_by(person_id=person_id_obj.person_id).first()
            if not person:
                return {'response': f'Контакт с person_id = {person_id_obj.person_id} не найден в БД'}
            phone = [Phone.json(phone) for phone in Phone.query.filter(Phone.person_id == person_id_obj.person_id).all()]
            return {'response': phone}
        except exc.OperationalError as oe:
            return {'error': f'Не удалось подключиться к БД {db.engine.url.database}.',
                    'exception_name': oe.__class__.__name__, 'info': traceback.format_exc()}

    @staticmethod
    def add_phone(phone_data):
        """Метод принимает на вход атрибуты сущности Phone и добавляет запись в таблицу phones в соответствии с person_id"""
        try:
            person = Person.query.filter_by(person_id=phone_data.person_id).first()
            if not person:
                return {'response': f'Контакт с person_id = {phone_data.person_id} не найден в БД'}
            new_phone = Phone(person_id=phone_data.person_id, phone_type=phone_data.phone_type,
                              phone_number=phone_data.phone_number)
            db.session.add(new_phone)
            db.session.commit()
            return {'response': f'Номер телефона {phone_data.phone_number} был добавлен в контакт с person_id = '
                                f'{phone_data.person_id}'}
        except exc.OperationalError as oe:
            return {'error': f'Не удалось подключиться к БД {db.engine.url.database}.',
                    'exception_name': oe.__class__.__name__, 'info': traceback.format_exc()}
        except exc.IntegrityError as ie:
            return {'error': f'Номер телефона {phone_data.phone_number} уже есть в БД.',
                             'exception_name': ie.__class__.__name__, 'info': traceback.format_exc()}

    @staticmethod
    def update_phone(phone_data):
        """Метод принимает person_id, существующий номер телефона и новый номер для замены и заменяет
        данные указанного номера"""
        try:
            phones_by_id = Phone.query.filter(Phone.person_id == phone_data.person_id).all()
            phone_for_update = [phone for phone in phones_by_id if phone.phone_number == phone_data.old_phone_number]
            if len(phone_for_update) == 0:
                return {'response':
                        f'Номер телефона {phone_data.old_phone_number} не был найден среди номеров контакта с person_id = '
                        f'{phone_data.person_id}. Для замены выберите один из существующих номеров: {phones_by_id}'}
            phone_for_update[0].phone_type = phone_data.phone_type
            phone_for_update[0].phone_number = phone_data.phone_number
            db.session.commit()
            return {'response': f'Номер телефона {phone_data.old_phone_number} был заменен на {phone_data.phone_number}'}
        except exc.OperationalError as oe:
            return {'error': f'Не удалось подключиться к БД {db.engine.url.database}.',
                    'exception_name': oe.__class__.__name__, 'info': traceback.format_exc()}
        except exc.IntegrityError as ie:
            return {'error': f'Номер телефона {phone_data.phone_number} уже есть в БД.',
                             'exception_name': ie.__class__.__name__, 'info': traceback.format_exc()}

    @staticmethod
    def delete_phone(phone_data):
        """Метод принимает на вход person_id и номер который нужно удалить  и удаляет соответствующую запись
        из таблицы phones"""
        try:
            phones_by_id = Phone.query.filter(Phone.person_id == phone_data.person_id).all()
            if not phones_by_id:
                return {'response': f'Контакт с person_id = {phone_data.person_id} не найден в БД'}
            phone_to_delete = [phone for phone in phones_by_id if phone.phone_number == phone_data.phone_number and
                               phone.phone_type == phone_data.phone_type]
            if len(phone_to_delete) == 0:
                return {'response':
                        f'Номер телефона - {phone_data.phone_number} с указанным типом - {phone_data.phone_type} '
                        f'не был найден среди номеров контакта с person_id = {phone_data.person_id}. Для удаления '
                        f'выберите один из существующих номеров: {phones_by_id} и проверьте соответствие phone_type'}
            db.session.delete(phone_to_delete[0])
            db.session.commit()
            return {'response': f'Номер телефона {phone_data.phone_number} был удален'}
        except exc.OperationalError as oe:
            return {'error': f'Не удалось подключиться к БД {db.engine.url.database}.',
                    'exception_name': oe.__class__.__name__, 'info': traceback.format_exc()}

    def __repr__(self):
        return f'<Phone {self.phone_number}, {self.phone_type}>'


class Email(db.Model):
    """Класс содержит модель таблицы emails и ее методы обработки данных"""
    __tablename__ = "emails"
    __table_args__ = {'extend_existing': True}
    person_id = db.Column(db.Integer, db.ForeignKey('persons.person_id', ondelete="CASCADE"), nullable=False)
    email_type = db.Column(db.String(30), nullable=False)
    email_address = db.Column(db.String(254), nullable=False, primary_key=True)

    def json(self):
        """Метод сериализует данные полученные из БД в формат JSON"""
        return {'person_id': self.person_id, 'email_type': self.email_type, 'email_address': self.email_address}

    @staticmethod
    def get_all_emails(sorted_data=None):
        """Метод принимает на вход параметры сортировки (если они есть) и возвращает список всех записей из
        таблицы emails"""
        try:
            if sorted_data:
                return {'response':
                        [Email.json(email) for email in Email.query.order_by(text(sorted_data.sorted_by + ' '
                                                                             + sorted_data.order)).all()]}
            return {'response': [Email.json(email) for email in Email.query.all()]}
        except exc.ProgrammingError as pe:
            return {'error': f'аттрибута {sorted_data.sorted_by} нет в таблице emails. Выберите один из следующих '
                             f'атрибутов - {", ".join([m.key for m in Email.__table__.columns])}',
                    'exception_name': pe.__class__.__name__, 'info': traceback.format_exc()}
        except exc.OperationalError as oe:
            return {'error': f'Не удалось подключиться к БД {db.engine.url.database}.',
                    'exception_name': oe.__class__.__name__, 'info': traceback.format_exc()}

    @staticmethod
    def get_email(person_id_obj):
        """"Метод принимает на вход person_id и возвращает соотвествующую запись или записи из таблицы emails"""
        try:
            person = Person.query.filter_by(person_id=person_id_obj.person_id).first()
            if not person:
                return {'response': f'Контакт с person_id = {person_id_obj.person_id} не найден в БД'}
            email = [Email.json(email) for email in Email.query.filter(Email.person_id == person_id_obj.person_id).all()]
            return {'response': email}
        except exc.OperationalError as oe:
            return {'error': f'Не удалось подключиться к БД {db.engine.url.database}.',
                    'exception_name': oe.__class__.__name__, 'info': traceback.format_exc()}

    @staticmethod
    def add_email(email_data):
        """Метод принимает на вход атрибуты сущности Email и добавляет запись в таблицу emails в соответствии с person_id"""
        try:
            person = Person.query.filter_by(person_id=email_data.person_id).first()
            if not person:
                return {'response': f'Контакт с person_id = {email_data.person_id} не найден в БД'}
            new_email = Email(person_id=email_data.person_id, email_type=email_data.email_type,
                              email_address=email_data.email_address)
            db.session.add(new_email)
            db.session.commit()
            return {'response': f'Адрес почты {email_data.email_address} был добавлен'}
        except exc.OperationalError as oe:
            return {'error': f'Не удалось подключиться к БД {db.engine.url.database}.',
                    'exception_name': oe.__class__.__name__, 'info': traceback.format_exc()}
        except exc.IntegrityError as ie:
            return {'error': f'Email {email_data.email_address} уже есть в БД.',
                    'exception_name': ie.__class__.__name__, 'info': traceback.format_exc()}

    @staticmethod
    def update_email(email_data):
        """"Метод принимает person_id, существующий адрес почты и новый адрес для замены и заменяет
        данные указанной почты."""
        try:
            emails_by_id = Email.query.filter(Email.person_id == email_data.person_id).all()
            email_for_update = [email for email in emails_by_id if email.email_address == email_data.old_email_address]
            if len(email_for_update) == 0:
                return {'response':
                        f'Email {email_data.old_email_address} не был найден среди адресов контакта с person_id = '
                        f'{email_data.person_id}. Для замены выберите один из существующих адресов: {emails_by_id}'}
            email_for_update[0].email_type = email_data.email_type
            email_for_update[0].email_address = email_data.email_address
            db.session.commit()
            return {'response': f'Адрес почты  {email_data.old_email_address} был заменен на {email_data.email_address}'}
        except exc.OperationalError as oe:
            return {'error': f'Не удалось подключиться к БД {db.engine.url.database}.',
                    'exception_name': oe.__class__.__name__, 'info': traceback.format_exc()}
        except exc.IntegrityError as ie:
            return {'error': f'Номер телефона {email_data.email_address} уже есть в БД.',
                             'exception_name': ie.__class__.__name__, 'info': traceback.format_exc()}

    @staticmethod
    def delete_email(email_data):
        """Метод принимает на вход person_id и данные email которые нужно удалить  и удаляет соответствующую запись
        из таблицы emails"""
        try:
            emails_by_id = Email.query.filter(Email.person_id == email_data.person_id).all()
            if not emails_by_id:
                return {'response': f'Контакт с person_id = {email_data.person_id} не найден в БД'}
            email_to_delete = [email for email in emails_by_id if email.email_address == email_data.email_address and
                               email.email_type == email_data.email_type]
            if len(email_to_delete) == 0:
                return {'response':
                        f'Email - {email_data.email_address} с указанным типом - {email_data.email_type} '
                        f'не был найден среди адресов контакта с person_id = {email_data.person_id}. Для удаления '
                        f'выберите один из существующих адресов: {emails_by_id} и проверьте соответствие email_type'}
            db.session.delete(email_to_delete[0])
            db.session.commit()
            return {'response': f'адрес {email_data.email_address} был удален'}
        except exc.OperationalError as oe:
            return {'error': f'Не удалось подключиться к БД {db.engine.url.database}.',
                    'exception_name': oe.__class__.__name__, 'info': traceback.format_exc()}

    def __repr__(self):
        return f'<Email {self.email_address}, {self.email_type}>'
