import pickle
from collections import UserDict
from datetime import datetime


class Field:
    def __init__(self, value):
        self._value = None
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class Name(Field):
    pass


class Phone(Field):

    @Field.value.setter
    def value(self, value):
        if not value.isnumeric():
            raise ValueError(f'Wrong phone format {value}')
        self._value = value
        print(self._value)


class Birthday(Field):

    @Field.value.setter
    def value(self, value):
        birth_date = datetime.strptime(value, '%Y-%m-%d').date()
        today = datetime.now().date()
        birth_date = datetime.strptime(value, '%Y-%m-%d').date()
        if birth_date > today:
            raise ValueError("Birthday cannot be in the future")
        self._value = birth_date


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def get_info(self):
        phones_info = ''
        for phone in self.phones:
            print(phone.value)
            phones_info += f'{phone.value}, '
        if self.birthday:
            return f'{self.name.value} : {phones_info[:-2]} Birthday: {self.birthday.value}'
        else:
            return f'{self.name.value} : {phones_info[:-2]}'

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def delete_phone(self, phone):
        for record_phone in self.phones:
            if record_phone.value == phone:
                self.phones.remove(record_phone)
                return True
        return False

    def change_phones(self, phones):
        for phone in phones:
            if not self.delete_phone(phone):
                self.add_phone(phone)

    def add_birthday(self, date):
        self.birthday = Birthday(date)

    def get_days_to_next_birthday(self):
        if not self.birthday:
            raise ValueError("Contact doesn't have birthday value")
        now = datetime.now().date()
        birthday = datetime.strptime(self.birthday.value, '%Y-%m-%d').date()
        this_year = now.year
        if now.month >= birthday.month and now.day > birthday.day:
            this_year += 1
        next_birthday = datetime(
            year=this_year,
            month=birthday.month,
            day=birthday.day
        )
        return (next_birthday.date() - now).days


class AddressBook(UserDict):

    def __init__(self):
        super().__init__()
        self.load_data_from_file()

    def add_record(self, record):
        self.data[record.name.value] = record

    def get_all_record(self):
        return self.data

    def has_record(self, name):
        return bool(self.data.get(name))

    def get_record(self, name):
        return self.data.get(name)

    def remove_record(self, name):
        del self.data[name]

    def search(self, value):
        result = []
        if self.has_record(value):
            result = [self.get_record(value)]
        for record in self.get_all_record().values():
            for phone in record.phones:
                if phone.value == value:
                    result.append(record)
        if result:
            return result
        raise ValueError(f"Contact with this value '{value}' does not exist")


    def iterator(self, count = 2):
        page = []
        i = 0
        for record in self.data.values():
            page.append(record)
            i += 1
            if i == count:
                yield page
                page = []
                i = 0
        if page:
            yield page

    def save_data_to_file(self):
        with open('AddressBook.dat', 'wb') as file:
            pickle.dump(self.data, file)

    def load_data_from_file(self):
        try:
            with open('AddressBook.dat', 'rb') as file:
                self.data = pickle.load(file)
        except FileNotFoundError:
            pass


contacts = AddressBook()


def input_error(function):
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except KeyError:
            return 'Wrong name'
        except ValueError as exception:
            return exception.args[0]
        except IndexError:
            return 'Enter: name and number'
        except TypeError:
            return 'Wrong command'
    return wrapper


@input_error
def hello_func():
    return 'How can I help you?'


@input_error
def exit_func():
    return 'Good bye!'


@input_error
def add_func(data):
    name, phone = pars_params(data)
    if name in contacts:
        raise ValueError(f'Contact {name} exist. ''name'' should be unique')
    record = Record(name)
    record.add_phone(phone)
    contacts.add_record(record)
    return f'New contact: {name} {phone} was added'


@input_error
def change_func(data):
    name, phone = pars_params(data)
    if name in contacts:
        contacts[name] = phone
        return f'You changed number to {phone} for {name}'
    return f'Contact {name} was not found'


@input_error
def search_func(name):
    search_result = ''
    records = contacts.search(name.strip())
    for record in records:
        search_result += f"{record.get_info()}\n"
    return f'Contacts:\n {search_result}'


@input_error
def show_all_func():
    contacts_result = ''
    page_number = 1
    for page in contacts.iterator(3):
        contacts_result += f'Page № {page_number}\n'
        for record in page:
            contacts_result += f'{record.get_info()}\n'
        page_number += 1
    return contacts_result


@input_error
def birthday_func(data):
    name, date = pars_params(data)
    record = contacts.get_record(name)
    record.add_birthday(date)
    return f"{name}'s birthday {date} was added"


@input_error
def next_birthday_func(name):
    name = name.strip()
    record = contacts[name]
    return f"Days to next {name}'s birthday is {record.get_days_to_next_birthday()}"


commands = {
    'hello': hello_func,
    'add': add_func,
    'change': change_func,
    'show all': show_all_func,
    'phone': search_func,
    'exit': exit_func,
    'close': exit_func,
    'good bye': exit_func,
    'birthday': birthday_func,
    'days to birthday': next_birthday_func
}


def process_input_data(user_input):
    new_input = user_input
    data = ''
    for key in commands:
        if user_input.strip().lower().startswith(key):
            new_input = key
            data = user_input[len(new_input):]
            break
    if data:
        return process_func(new_input)(data)
    return process_func(new_input)()


def process_func(command_name):
    return commands.get(command_name, unknown_func)


def pars_params(data):
    name, phone = data.strip().split(" ")
    return name, phone


def unknown_func():
    return 'Unknown command name'


def main():
    try:
        while True:
            user_input = input('Enter command: ')
            result = process_input_data(user_input)
            print(result)
            if result == 'Good bye!':
                break
    finally:
        contacts.save_data_to_file()


if __name__ == '__main__':
    main()
