from cloudbot.util.database import metadata, base


def test_database():
    assert metadata is None
    assert base is None
