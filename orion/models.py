from orion import db
from sqlalchemy import text

class Person(db.Model):
    __tablename__ = "persons"
    person_id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(30), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    address = db.Column(db.String, nullable=False)
    phones = db.relationship("Phone", backref="persons", passive_deletes=True, cascade='all, delete-orphan')
    emails = db.relationship("Email", backref="persons", passive_deletes=True, cascade='all, delete-orphan')

    def json(self):
        return {'person_id': self.person_id, 'file_path': self.file_path,
                'full_name': self.full_name, 'gender': self.gender,
                'birthday': self.birthday, 'address': self.address}


    def get_all_persons(sorted_by, order):
        if sorted_by and order:
            return [Person.json(person) for person in Person.query.order_by(text(sorted_by + ' ' + order)).all()]
        return [Person.json(person) for person in Person.query.all()]

    def get_person(person_id):
        return Person.query.filter_by(person_id=person_id).first()

    def add_person(file_path, full_name, gender, birthday, address, phones, emails):
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
        return new_person

    def update_person(person_id, file_path, full_name, gender, birthday, address):
        person_to_update = Person.query.filter_by(person_id=person_id).first()
        person_to_update.file_path = file_path
        person_to_update.full_name = full_name
        person_to_update.gender = gender
        person_to_update.birthday = birthday
        person_to_update.address = address
        db.session.commit()

    def delete_person(person_id):
        person_to_delete = Person.query.filter_by(person_id=person_id).first()
        db.session.delete(person_to_delete)
        db.session.commit()
        return person_to_delete


    def __repr__(self):
        return f'<Person {self.full_name}>'


class Phone(db.Model):
    __tablename__ = "phones"
    person_id = db.Column(db.Integer, db.ForeignKey('persons.person_id', ondelete="CASCADE"), nullable=False)
    phone_type = db.Column(db.String(30), nullable=False)
    phone_number = db.Column(db.String(30), nullable=False, primary_key=True)

    def json(self):
        return {'person_id': self.person_id, 'phone_type': self.phone_type, 'phone_number': self.phone_number}

    def get_all_phones(sorted_by, order):
        if sorted_by and order:
            return [Phone.json(phone) for phone in Phone.query.order_by(text(sorted_by + ' ' + order)).all()]
        return [Person.json(person) for person in Person.query.all()]

    def get_phone(person_id):
        return Phone.query.filter_by(person_id=person_id).first()

    def add_phone(person_id, phone_type, phone_number):
        new_phone = Phone(person_id=person_id, phone_type=phone_type, phone_number=phone_number)
        db.session.add(new_phone)
        db.session.commit()
        return new_phone

    def update_phone(person_id, phone_type, phone_number):
        phone_to_update = Phone.query.filter_by(person_id=person_id).first()
        phone_to_update.phone_type = phone_type
        phone_to_update.phone_number = phone_number
        db.session.commit()

    def delete_phone(person_id):
        phone_to_delete = Phone.query.filter_by(person_id=person_id).first()
        db.session.delete(phone_to_delete)
        db.session.commit()
        return phone_to_delete

    def __repr__(self):
        return f'<Phone {self.phone_number}>'


class Email(db.Model):
    __tablename__ = "emails"
    person_id = db.Column(db.Integer, db.ForeignKey('persons.person_id', ondelete="CASCADE"), nullable=False)
    email_type = db.Column(db.String(30), nullable=False)
    email_address = db.Column(db.String(254), nullable=False, primary_key=True)


    def json(self):
        return {'person_id': self.person_id, 'email_type': self.email_type, 'email_address': self.email_address}

    def get_all_emails(sorted_by, order):
        if sorted_by and order:
            return [Email.json(email) for email in Email.query.order_by(text(sorted_by + ' ' + order)).all()]
        return [Email.json(email) for email in Email.query.all()]

    def get_email(person_id):
        return Email.query.filter_by(person_id=person_id).first()

    def add_email(person_id, email_address, email_type):
        new_email = Email(person_id=person_id, email_address=email_address, email_type=email_type)
        db.session.add(new_email)
        db.session.commit()
        return new_email

    def update_email(person_id, email_address, email_type):
        email_to_update = Email.query.filter_by(person_id=person_id).first()
        email_to_update.email_type = email_type
        email_to_update.email_address = email_address
        db.session.commit()

    def delete_email(person_id):
        email_to_delete = Email.query.filter_by(person_id=person_id).first()
        db.session.delete(email_to_delete)
        db.session.commit()
        return email_to_delete

    def __repr__(self):
        return f'<Email {self.email_address}>'

db.create_all()
