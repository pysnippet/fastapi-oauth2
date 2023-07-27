from typing import Any
from typing import Callable
from typing import Union


class Claims(dict):
    """Claims configuration for a single provider."""

    display_name: Union[str, Callable[[dict], Any]]
    identity: Union[str, Callable[[dict], Any]]
    picture: Union[str, Callable[[dict], Any]]
    email: Union[str, Callable[[dict], Any]]

    def __init__(self, seq=None, **kwargs) -> None:
        super().__init__(seq or {}, **kwargs)
        self.display_name = self.get("display_name", "name")
        self.identity = self.get("identity", "sub")
        self.picture = self.get("picture", "picture")
        self.email = self.get("email", "email")

    # @property
    # def display_name(self) -> str:
    #     return self.get("display_name", "")
    #
    # @display_name.setter
    # def display_name(self, value: Union[Any, Callable[[dict], Any]]) -> None:
    #     self["display_name"] = self._get_value(value)
    #
    # @property
    # def identity(self) -> str:
    #     return self.get("identity", "")
    #
    # @identity.setter
    # def identity(self, value: Union[str, Callable[[dict], Any]]) -> None:
    #     self["identity"] = self._get_value(value)
    #
    # @property
    # def picture(self) -> str:
    #     return self.get("picture", "")
    #
    # @picture.setter
    # def picture(self, value: Union[str, Callable[[dict], Any]]) -> None:
    #     self["picture"] = self._get_value(value)
    #
    # @property
    # def email(self) -> str:
    #     return self.get("email", "")
    #
    # @email.setter
    # def email(self, value: Union[str, Callable[[dict], Any]]) -> None:
    #     self["email"] = self._get_value(value)

    def __getattr__(self, item):
        attr = super().get(item)
        if callable(attr):
            return attr(self)
        return self.get(attr)

    # def _get_value(self, value: Union[str, Callable[[dict], Any]]) -> Any:
    #     if callable(value):
    #         return value(self)
    #     return self.get(value, "")
