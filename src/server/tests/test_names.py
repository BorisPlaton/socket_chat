def test_get_name_return_first_name(name_class):
    for _ in range(5):
        name = name_class.get_name()
        assert isinstance(name, str)
        assert ' ' not in name


def test_name_uniqueness(name_class):
    names_list = set()
    for _ in range(600):
        name = name_class.get_name()
        assert name not in names_list
        names_list.add(name)


def test_name_deletion(name_class):
    name = name_class.get_name()
    assert name in name_class._registered_names
    name_class.delete_name(name)
    assert name not in name_class._registered_names
