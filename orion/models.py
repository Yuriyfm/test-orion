from orion import db
from sqlalchemy import text, exc
# В данном модуле находятся классы моделей таблиц и их методы обработки данных


class Person(db.Model):
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
    def get_all_persons(sorted_by=None, order=None):
        """"Метод принимает на вход параметры сортировки (если они есть) и возвращает список всех записей из
        таблицы persons"""
        if sorted_by and order:
            return [Person.json(person) for person in Person.query.order_by(text(sorted_by + ' ' + order)).all()]
        return [Person.json(person) for person in Person.query.all()]

    @staticmethod
    def get_person(person_id):
        """"Метод принимает на вход person_id и возвращает соотвествующую запись из таблицы persons"""
        return Person.query.filter_by(person_id=person_id).first()

    @staticmethod
    def add_person(file_path, full_name, gender, birthday, address, phones, emails):
        """Метод принимает на вход атрибуты сущности Person и related сущностей (если они есть) и добавляет записи в
        соответствующие таблицы"""
        try:
            new_person = Person(file_path=file_path, full_name=full_name,
                                gender=gender, birthday=birthday, address=address)
            db.session.add(new_person)
            db.session.commit()
            for phone in phones:
                new_person_phone = Phone(person_id=new_person.person_id, phone_type=phone['phone_type'],
                                         phone_number=phone['phone_number'])
                db.session.add(new_person_phone)
            for email in emails:
                new_person_email = Email(person_id=new_person.person_id, email_type=email['email_type'],
                                         email_address=email['email_address'])
                db.session.add(new_person_email)
            db.session.commit()
            return f'Контакт {full_name} успешно добавлен в БД c person_id = {new_person.person_id}\n\n'
        # ловим ошибку нарушения уникальности по столбцам email_address и phone_number, делаем session rollback
        # и возвращаем ошибку
        except exc.IntegrityError as i:
            db.session.rollback()
            return(f'При добавлении данных контакта {full_name} произошла ошибка нарушения уникальности, '
                   f'по одному из столбцов - email_address, phone_number. {i.args}.\n\n')

    @staticmethod
    def update_person(person_id, file_path, full_name, gender, birthday, address):
        """"Метод принимает на вход значения атрибутов сущности Person и обновляет данные в соответсвии с указанным
         person_id"""
        person_to_update = Person.query.filter_by(person_id=person_id).first()
        if not person_to_update:
            return f'person_id {person_id} не найден в БД'
        person_to_update.file_path = file_path
        person_to_update.full_name = full_name
        person_to_update.gender = gender
        person_to_update.birthday = birthday
        person_to_update.address = address
        db.session.commit()
        return f'Данные контакта с person_id = {person_id} изменены'

    @staticmethod
    def delete_person(person_id):
        """"Метод принимает на вход person_id и удаляет соответствующую запись из таблицы person и дочерних таблиц"""
        person_to_delete = Person.query.filter_by(person_id=person_id).first()
        if not person_to_delete:
            return f'person_id {person_id} не найден в БД'
        db.session.delete(person_to_delete)
        db.session.commit()
        return f"Все данные контакта с person_id = {person_id} были удалены"

    def __repr__(self):
        return f'<Person {self.full_name}>'


class Phone(db.Model):
    __tablename__ = "phones"
    __table_args__ = {'extend_existing': True}
    person_id = db.Column(db.Integer, db.ForeignKey('persons.person_id', ondelete="CASCADE"), nullable=False)
    phone_type = db.Column(db.String(30), nullable=False)
    phone_number = db.Column(db.String(30), nullable=False, primary_key=True)

    def json(self):
        """Метод сериализует данные полученные из БД в формат JSON"""
        return {'person_id': self.person_id, 'phone_type': self.phone_type, 'phone_number': self.phone_number}

    @staticmethod
    def get_all_phones(sorted_by=None, order=None):
        """"Метод принимает на вход параметры сортировки (если они есть) и возвращает список всех записей из
        таблицы phones"""
        if sorted_by and order:
            return [Phone.json(phone) for phone in Phone.query.order_by(text(sorted_by + ' ' + order)).all()]
        return [Phone.json(person) for person in Phone.query.all()]

    @staticmethod
    def get_phone(person_id):
        """"Метод принимает на вход person_id и возвращает соотвествующую запись из таблицы phones"""
        return [Phone.json(phone) for phone in Phone.query.filter(Phone.person_id == person_id).all()]

    @staticmethod
    def add_phone(person_id, phone_type, phone_number):
        """Метод принимает на вход атрибуты сущности Phone и добавляет запись в таблицу phones в соответствии с person_id"""
        person = Person.query.filter_by(person_id=person_id).first()
        if not person:
            return f'person_id = {person_id} не был найден в БД'
        new_phone = Phone(person_id=person_id, phone_type=phone_type, phone_number=phone_number)
        db.session.add(new_phone)
        db.session.commit()
        return f'Номер телефона {phone_number} был добавлен'

    @staticmethod
    def update_phone(person_id, new_phone_type, new_phone_number, old_phone_number):
        """Метод принимает person_id, существующий номер телефона и новый номер для замены и заменяет
        данные указанного номера"""
        phones_by_id = Phone.query.filter(Phone.person_id == person_id).all()
        phone_for_update = [phone for phone in phones_by_id if phone.phone_number == old_phone_number]
        if len(phone_for_update) == 0:
            return f'Номер телефона {old_phone_number} не был найден среди номеров контакта с person_id = ' \
                   f'{person_id}. Для замены выберите один из существующих номеров: {phones_by_id}'
        phone_for_update[0].phone_type = new_phone_type
        phone_for_update[0].phone_number = new_phone_number
        db.session.commit()
        return f'Номер телефона {old_phone_number} был заменен на {new_phone_number}'

    @staticmethod
    def delete_phone(person_id, phone_number):
        """Метод принимает на вход person_id и номер который нужно удалить  и удаляет соответствующую запись
        из таблицы phones"""
        phones_by_id = Phone.query.filter(Phone.person_id == person_id).all()
        if not phones_by_id:
            return f'person_id = {person_id} не был найден в БД'
        phone_to_delete = [phone for phone in phones_by_id if phone.phone_number == phone_number]
        if len(phone_to_delete) == 0:
            return f'Номер телефона {phone_number} не был найден среди номеров контакта с person_id = ' \
                   f'{person_id}. Для удаления выберите один из существующих номеров: {phones_by_id}'
        db.session.delete(phone_to_delete[0])
        db.session.commit()
        return f'Номер телефона {phone_number} был удален'

    def __repr__(self):
        return f'<Phone {self.phone_number}>'


class Email(db.Model):
    __tablename__ = "emails"
    __table_args__ = {'extend_existing': True}
    person_id = db.Column(db.Integer, db.ForeignKey('persons.person_id', ondelete="CASCADE"), nullable=False)
    email_type = db.Column(db.String(30), nullable=False)
    email_address = db.Column(db.String(254), nullable=False, primary_key=True)

    def json(self):
        """Метод сериализует данные полученные из БД в формат JSON"""
        return {'person_id': self.person_id, 'email_type': self.email_type, 'email_address': self.email_address}

    @staticmethod
    def get_all_emails(sorted_by=None, order=None):
        """Метод принимает на вход параметры сортировки (если они есть) и возвращает список всех записей из
        таблицы emails"""
        if sorted_by and order:
            return [Email.json(email) for email in Email.query.order_by(text(sorted_by + ' ' + order)).all()]
        return [Email.json(email) for email in Email.query.all()]

    @staticmethod
    def get_email(person_id):
        """"Метод принимает на вход person_id и возвращает соотвествующую запись или записи из таблицы emails"""
        return [Email.json(email) for email in Email.query.filter(Email.person_id == person_id).all()]

    @staticmethod
    def add_email(person_id, email_address, email_type):
        """Метод принимает на вход атрибуты сущности Email и добавляет запись в таблицу emails в соответствии с person_id"""
        person = Person.query.filter_by(person_id=person_id).first()
        if not person:
            return f'person_id = {person_id} не был найден в БД'
        new_email = Email(person_id=person_id, email_type=email_type, email_address=email_address)
        db.session.add(new_email)
        db.session.commit()
        return f'Адрес почты {email_address} был добавлен'

    @staticmethod
    def update_email(person_id, old_email_address, new_email_address, new_email_type):
        """"Метод принимает person_id, существующий адрес почты и новый адрес для замены и заменяет
        данные указанной почты."""
        emails_by_id = Email.query.filter(Email.person_id == person_id).all()
        email_for_update = [email for email in emails_by_id if email.email_address == old_email_address]
        if len(email_for_update) == 0:
            return f'адрес почты {old_email_address} не был найден среди адресов контакта с person_id = ' \
                   f'{person_id}. Для замены выберите один из существующих адресов почты: {emails_by_id}'
        email_for_update[0].email_type = new_email_type
        email_for_update[0].email_address = new_email_address
        db.session.commit()
        return f'Адрес почты {old_email_address} был заменен на {new_email_address}'

    @staticmethod
    def delete_email(person_id, email_address):
        """Метод принимает на вход person_id и email который нужно удалить  и удаляет соответствующую запись
        из таблицы emails"""
        emails_by_id = Email.query.filter(Email.person_id == person_id).all()
        if not emails_by_id:
            return f'person_id = {person_id} не был найден в БД'
        email_to_delete = [email for email in emails_by_id if email.email_address == email_address]
        if len(email_to_delete) == 0:
            return f'email {email_address} не был найден среди адресов контакта с person_id = ' \
                   f'{person_id}. Для удаления выберите один из существующих адресов: {emails_by_id}'
        db.session.delete(email_to_delete[0])
        db.session.commit()
        return f'Адрес почты {email_address} был удален'

    def __repr__(self):
        return f'<Email {self.email_address}>'
