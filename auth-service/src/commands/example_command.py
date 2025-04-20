import typer

app = typer.Typer()

@app.command()
def example(parametr: str = "Some-command"):
    typer.echo(f"Command: {parametr}")
