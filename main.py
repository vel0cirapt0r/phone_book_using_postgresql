import peewee
from database_manager import DatabaseManager
import local_settings

database_manager = DatabaseManager(
    database_name=local_settings.DATABASE['name'],
    user=local_settings.DATABASE['user'],
    password=local_settings.DATABASE['password'],
    host=local_settings.DATABASE['host'],
    port=local_settings.DATABASE['port'],
)


class Contact(peewee.Model):
    first_name = peewee.CharField(max_length=255)
    last_name = peewee.CharField(max_length=255)

    class Meta:
        database = database_manager.db


class Address(peewee.Model):
    contact = peewee.ForeignKeyField(Contact, backref='addresses')
    tag = peewee.CharField(max_length=50)  # Tag like 'home', 'office', etc.
    address = peewee.TextField()

    class Meta:
        database = database_manager.db


class PhoneNumber(peewee.Model):
    contact = peewee.ForeignKeyField(Contact, backref='phone_numbers')
    tag = peewee.CharField(max_length=50)  # Tag like 'home', 'work', etc.
    number = peewee.CharField(max_length=20)

    class Meta:
        database = database_manager.db


def is_valid_phone_number(number):
    # Check if the input is a string
    if not isinstance(number, str):
        return False

    # Check if the input consists of only digits
    if not number.isdigit():
        return False

    # Check if the length of the input is exactly 11 characters
    if len(number) != 11:
        return False

    return True


def is_valid_address(address):
    # Check if the input is a string
    if not isinstance(address, str):
        return False

    # Check if the input contains only alphanumeric characters
    if not address.isalnum():
        return False

    return True


def add_contact():
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    contact = Contact.create(first_name=first_name, last_name=last_name)

    while True:
        number = input("Enter phone number (leave blank to skip): ")
        if not number:
            break
        tag = input("Enter phone number tag (e.g., home, work): ")
        if is_valid_phone_number(number):
            PhoneNumber.create(contact=contact, tag=tag, number=number)
        else:
            print("Invalid phone number. Please enter a valid 11-digit integer.")

    while True:
        address = input("Enter address (leave blank to skip): ")
        if not address:
            break
        tag = input("Enter address tag (e.g., home, work): ")
        if is_valid_address(address):
            Address.create(contact=contact, tag=tag, address=address)
        else:
            print("Invalid address. Please enter a valid string without signs.")

    print(f"Contact '{first_name} {last_name}' added successfully!")


def display_contacts():
    print("All Contacts:")
    contacts = Contact.select()
    for contact in contacts:
        print(f"Name: {contact.first_name} {contact.last_name}")

        # Print phone numbers
        phone_numbers = PhoneNumber.select().where(PhoneNumber.contact == contact)
        for phone_number in phone_numbers:
            print(f"   {phone_number.tag}: {phone_number.number}")

        # Print addresses
        addresses = Address.select().where(Address.contact == contact)
        for address in addresses:
            print(f"   {address.tag}: {address.address}")
        print()


def search_contacts():
    keyword = input("Enter keyword to search: ")
    query = Contact.select().where(
        (Contact.first_name.contains(keyword)) | (Contact.last_name.contains(keyword))
    )
    if query.exists():
        print("Search Results:")
        for idx, contact in enumerate(query, start=1):
            print(f"{idx}. {contact.first_name} {contact.last_name}")

        while True:
            choice = input(
                "Enter the number of the contact to view details (or 'all' to show all results, or 'exit' to return "
                "to the main menu): ")
            if choice.lower() == 'exit':
                return
            elif choice.lower() == 'all':
                display_contacts()
                return
            elif choice.isdigit() and 1 <= int(choice) <= len(query):
                selected_contact = query[int(choice) - 1]

                # Print selected contact details
                print(f"\nDetails for {selected_contact.first_name} {selected_contact.last_name}:")

                # Print phone numbers
                phone_numbers = PhoneNumber.select().where(PhoneNumber.contact == selected_contact)
                print("   Phone Numbers:")
                for phone_number in phone_numbers:
                    print(f"      {phone_number.tag}: {phone_number.number}")

                # Print addresses
                addresses = Address.select().where(Address.contact == selected_contact)
                print("   Addresses:")
                for address in addresses:
                    print(f"      {address.tag}: {address.address}")

                return
            else:
                print("Invalid choice. Please try again.")
    else:
        print("No matching contacts found.")


if __name__ == "__main__":
    try:
        database_manager.create_tables(models=[Contact, PhoneNumber, Address])

        while True:
            print("\nMenu:")
            print("1. Add Contact")
            print("2. Display Contacts")
            print("3. Search Contacts")
            print("4. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":
                add_contact()
            elif choice == "2":
                display_contacts()
            elif choice == "3":
                search_contacts()
            elif choice == "4":
                break
            else:
                print("Invalid choice. Please try again.")

    except Exception as error:
        print("Error:", error)
    finally:
        # Close the database connection
        if database_manager.db:
            database_manager.db.close()
            print("Database connection is closed")
