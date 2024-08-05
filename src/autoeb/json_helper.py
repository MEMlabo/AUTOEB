from json import dumps, loads
from typing import Any


def serialize(value: Any) -> str:
    """jsonでシリアライズを行います。

    Args:
        value (Any): シリアライズするオブジェクト

    Returns:
        str: json文字列
    """
    fields: dict[str, Any] = __get_dict(value)
    return dumps(fields, indent=2)


def __get_dict(value: Any) -> dict[str, Any]:
    """オブジェクトのフィールドを取得します。

    Args:
        value (Any): 対象オブジェクト

    Returns:
        dict[str, Any]: フィールド一覧
    """
    type_name: str = type(value).__name__
    offset: int = len(type_name) + 3
    result = dict[str, Any]()
    for key in value.__dict__:
        field: Any = value.__dict__[key]
        name: str = key[offset:]
        result[name] = field
    return result


def deserialize(json: str, tp: type) -> Any:
    """jsonでデシリアライズを行います。

    Args:
        json (str): json文字列
        tp (type): 復元するオブジェクトの型

    Returns:
        Any: デシリアライズされたオブジェクト
    """
    fields: dict[str, Any] = loads(json)
    result: Any = tp()
    __set_dict(result, fields)
    return result


def __set_dict(value: Any, fields: dict[str, Any]) -> None:
    """オブジェクトのフィールドを設定します。

    Args:
        value (Any): 対象オブジェクト
        fields (dict[str, Any]): フィールド一覧
    """
    prefix: str = f"_{type(value).__name__}__"
    for name in fields:
        field: Any = fields[name]
        setattr(value, prefix + name, field)
