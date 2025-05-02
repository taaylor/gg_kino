import typer
from db.postgres import sync_session_maker
from models.models import DictRoles, RolesPermissions, User, UserCred
from models.models_types import PermissionEnum
from utils.key_manager import pwd_context

MAX_ATTEMPTS = 3

app = typer.Typer()


def check_common_passwords(password):
    with open("commands/common-passwords.txt", "r", encoding="utf-8") as f:
        common_passwords_ls = list(filter(bool, f.read().split("\n")))
        validate_password = password.isalpha() or password.isdigit() or len(password) < 8
        return (password in common_passwords_ls) or validate_password


def prompt_passwords_with_confirmation() -> str:
    for attempt in range(1, MAX_ATTEMPTS + 1):
        password = typer.prompt("Введите пароль", hide_input=True)
        password2 = typer.prompt("Повторите пароль для подтверждения", hide_input=True)

        if password == password2 and len(password) > 0:
            return password
        else:
            typer.echo(f"Пароли не совпадают. Попытка {attempt}/{MAX_ATTEMPTS}\n")
    typer.echo("Превышено количество попыток.")
    raise typer.Exit(code=1)


def createsuperuser():
    username = typer.prompt("username")
    email = typer.prompt("email")
    password = prompt_passwords_with_confirmation()
    if check_common_passwords(password):
        confirmation = typer.prompt(
            "Пароль слишком простой, вы уверены что хотите продолжить (y/n)?"
        )
        if confirmation.lower() != "y":
            raise typer.Exit(code=1)

    create(username, email, password)


def create(username: str, email: str, password: str):
    with sync_session_maker() as session:
        role = session.get(DictRoles, "ADMIN")
        if not role:
            role = DictRoles(
                role="ADMIN",
                descriptions="CRUD над контентом.",
            )
            session.add(role)
            # ! -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
            # ! временный код для создания всех ролей
            role_description_ls = (
                ("SUB_USER", "Пользователь с подпиской"),
                ("UNSUB_USER", "Пользователь без подписки"),
                ("ANONYMOUS", "Аноним"),
            )
            bulk_data_roles = [
                DictRoles(
                    role=role_,
                    descriptions=desc,
                )
                for role_, desc in role_description_ls
            ]
            session.add_all(bulk_data_roles)
            # ! -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
            action_description_ls = (
                (PermissionEnum.CRUD_ROLE.value, "CRUD над ролями"),
                (PermissionEnum.ASSIGN_ROLE.value, "Назначать роль"),
            )
            bulk_data = [
                RolesPermissions(
                    permission=action,
                    descriptions=desc,
                    role=role,
                )
                for action, desc in action_description_ls
            ]
            session.add_all(bulk_data)

        user = User(
            username=username,
            role=role,
        )
        session.add(user)

        user_cred = UserCred(
            user=user,
            email=email,
            # argon2 считается лучше чем pbkdf2_sha256, bcrypt, и scrypt.
            # https://passlib.readthedocs.io/en/stable/lib/passlib.hash.argon2.html?highlight=argon2#passlib.hash.argon2
            password=pwd_context.hash(password),
        )
        session.add(user_cred)
        session.commit()

        typer.echo(f"Суперпользователь создан: {username}")
