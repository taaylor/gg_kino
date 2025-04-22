import typer
from commands import createsuperuser

app = typer.Typer()

app.add_typer(createsuperuser.app)
app.command()(createsuperuser.createsuperuser)

if __name__ == "__main__":
    app()
