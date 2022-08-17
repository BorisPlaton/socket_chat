from faker import Faker


class Names:
    """Класс, что выдает случайные имена."""

    def get_name(self) -> str:
        """
        Возвращает случайное имя, которое ещё
        не использовалось.
        """
        while True:
            name = self.faker.first_name()
            if name not in self._registered_names:
                self._registered_names.add(name)
                break
        return name

    def delete_name(self, name) -> bool:
        """
        Удаляет имя из множества уже использованных
        имён. Если имя там было, вернет `True`, иначе -
        False.
        """
        try:
            self._registered_names.remove(name)
        except KeyError:
            return False
        return True

    def __init__(self):
        self.faker = Faker()
        self._registered_names = set()
