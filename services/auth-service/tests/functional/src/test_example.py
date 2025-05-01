from sqlalchemy import delete
from tests.functional.plugins.testdata import DictRoles


def test_example():
    assert True


async def test_postgres_example(pg_session):
    role = DictRoles(role="some-role", descriptions="test role")
    pg_session.add(role)
    # pg_session.flush() вместо pg_session.commit()
    # алхимия отправит INSERT’ы в базу, но не зафиксирует их.
    # а в фикстуре pg_session rollback() откатит всё.
    await pg_session.flush()
    assert role.role == "some-role"
    result = await pg_session.execute(
        delete(DictRoles).where(DictRoles.role == "some-role").returning(DictRoles.role)
    )
    assert result.scalar_one() == "some-role"
