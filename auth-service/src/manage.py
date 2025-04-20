import typer
from commands import example_command
from commands.createsuperuser import createsuperuser

app = typer.Typer()

# Регистрируем подкоманды
app.add_typer(example_command.app, name="example-command")
app.command()(createsuperuser)

if __name__ == "__main__":
    app()
