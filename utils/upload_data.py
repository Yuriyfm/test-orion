from orion.models import Person, Phone, Email
from orion import db
from utils.data_generator import get_random_person, genders
from random import choice
import sys
import os

# модуль для наполнения БД данными сгеренированными в модуле data_generator

def data_uploader():
    """Функция для наполнения БД данными сгеренированными в модуле data_generator. Данные соответсвуют критериям
    валидации описанным в модуле data_validation"""
    for i in range(100):
        try:
            data = get_random_person(choice(genders))
            new_person = Person(file_path=data['file_path'], full_name=data['full_name'], gender=data['gender'],
                            birthday=data['birthday'], address=data['address'])
            db.session.add(new_person)
            db.session.commit()
            for phone in data['phones']:
                new_phone = Phone(phone_type=phone['phone_type'], phone_number=phone['phone_number'], person_id=new_person.person_id)
                db.session.add(new_phone)
                db.session.commit()
            for email in data['emails']:
                new_email = Email(email_type=email['email_type'], email_address=email['email_address'], person_id=new_person.person_id)
                db.session.add(new_email)
                db.session.commit()
            print(f'Контакт {data["full_name"]} добавлен в БД')
        except Exception as e:
            print(f'При добавлении контакта в БД произошла ошибка {e}')

data_uploader()
