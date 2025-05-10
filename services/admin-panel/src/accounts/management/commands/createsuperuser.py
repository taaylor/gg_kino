from getpass import getpass

from django.contrib.auth import get_user_model
from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError

User = get_user_model()


class Command(createsuperuser.Command):
    help = "Создание суперпользователя"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        username_field = User.USERNAME_FIELD
        try:
            username = self._get_input_data(username_field, f"{username_field}: ", input_type=str)
            if not username:
                raise CommandError(f"{username_field} must be set")

            email = self._get_input_data("email", "email: ", input_type=str)
            if not email:
                raise CommandError("Email must be set")

            password = self._get_input_data("password", "password: ", input_type=str, hidden=True)
            password2 = self._get_input_data(
                "password (again)", "password (again): ", input_type=str, hidden=True
            )
            if password != password2:
                raise CommandError("Пароли не совпадают")

            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS("Суперпользователь создан"))
        except KeyboardInterrupt:
            self.stderr.write(self.style.ERROR("Операция прервана"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error: {str(e)}"))
            raise

    def _get_input_data(self, field_name, message, input_type=str, hidden=False):
        """Вспомогательный метод для получения ввода"""
        while True:
            if hidden:
                value = input_hidden(message)
            else:
                value = input(message).strip()
            if value:
                try:
                    return input_type(value)
                except (TypeError, ValueError):
                    self.stderr.write(self.style.ERROR(f"Некорректный ввод {field_name}"))
            else:
                self.stderr.write(self.style.ERROR(f"{field_name} не может быть пустым"))


def input_hidden(message):
    return getpass(message)
