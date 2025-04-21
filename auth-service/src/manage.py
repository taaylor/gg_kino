import typer
from commands import createsuperuser
from db import postgres


def main():
    try:
        postgres.init_database()
        app = typer.Typer()
        app.add_typer(createsuperuser.app)
        app.command()(createsuperuser.createsuperuser)
        app()
    finally:
        postgres.engine.dispose()


if __name__ == "__main__":
    main()
