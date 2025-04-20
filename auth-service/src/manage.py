import typer
from commands.createsuperuser import createsuperuser


app = typer.Typer()

app.command()(createsuperuser)

if __name__ == "__main__":
    app()
