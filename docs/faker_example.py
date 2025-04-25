from faker import Faker


def generate_fake_user():
    fake = Faker('ru_RU')

    return {
        'name': fake.name(),
        'address': fake.address(),
        'email': fake.email(),
        'phone_number': fake.phone_number(),
        'birth_date': fake.date_of_birth(),
        'company': fake.company(),
        'job': fake.job()
    }

result = generate_fake_user()
print(result)

