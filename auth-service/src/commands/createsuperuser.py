from passlib.hash import argon2
import asyncio
import typer

from db.postgres import async_session_maker
from models.models import User, UserCred


MAX_ATTEMPTS = 3


def check_common_passwords(password):
    with open('commands/common-passwords.txt', "r", encoding="utf-8") as f:
        common_passwords_ls = list(filter(bool, f.read().split('\n')))
        return password in common_passwords_ls


def prompt_passwords_with_confirmation() -> str:
    for attempt in range(1, MAX_ATTEMPTS + 1):
        password = typer.prompt("Введите пароль", hide_input=True)
        password2 = typer.prompt(
            "Повторите пароль для подтверждения", hide_input=True)

        if password == password2 and len(password) > 0:
            return password
        else:
            typer.echo(
                f"Пароли не совпадают. Попытка {attempt}/{MAX_ATTEMPTS}\n")
    typer.echo("Превышено количество попыток.")
    raise typer.Exit(code=1)


def createsuperuser():
    username = typer.prompt("username")
    first_name = typer.prompt("имя")
    password = prompt_passwords_with_confirmation()
    if check_common_passwords(password):
        confirmation = typer.prompt(
            "Пароль слишком простой, вы уверены что хотите продолжить (y/n)?")
        if confirmation.lower() != 'y':
            raise typer.Exit(code=1)

    async def create():
        async with async_session_maker() as session:
            user = User(
                username=username,
                first_name=first_name
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)

            user_cred = UserCred(
                user_id=user.id,
                # argon2 считается лучше чем pbkdf2_sha256, bcrypt, и scrypt.
                # https://passlib.readthedocs.io/en/stable/lib/passlib.hash.argon2.html?highlight=argon2#passlib.hash.argon2
                password=argon2.hash(password)
            )
            session.add(user_cred)
            await session.commit()

            typer.echo(f"Суперпользователь создан: {username}")

    asyncio.run(create())
