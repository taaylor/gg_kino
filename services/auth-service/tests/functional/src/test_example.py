def test_example():
    assert True


def test_postgres_connection(postgres_test):
    result = postgres_test("SELECT 1")
    assert result == [(1,)], "PostgreSQL должен вернуть [(1,)]"


def test_postgres_insert_and_select(postgres_test):
    postgres_test("CREATE TABLE IF NOT EXISTS some_table (name TEXT)")
    postgres_test("INSERT INTO some_table (name) VALUES (%s)", ("some-data",))
    result = postgres_test("SELECT name FROM some_table WHERE name = %s", ("some-data",))
    assert result == [("some-data",)], "Должна быть одна строка с именем 'some-data'"
