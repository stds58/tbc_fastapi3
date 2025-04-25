# Группировка списка словарей по ключу

from collections import defaultdict
from datetime import date
from typing import List, Dict, Any


def group_dicts_by_key(data_list_dict: List[Dict[str, Any]], key_group: str) -> dict:
    """
    Функция для группировки списка словарей по указанному ключу.

    Args:
    data_list_dict (list): Исходный список словарей.
    key_group (str): Ключ для группировки.

    Returns:
    dict: Словарь со сгрупированными значениями.
    """
    grouped_dict = defaultdict(list)

    for item in data_list_dict:
        order = item[key_group]
        grouped_dict[order].append(item)

    return dict(grouped_dict)


if __name__ == "__main__":
    data = [
        {'art': '123da', 'order_number_1': 472931549},
        {'art': 'dasdw', 'order_number_1': 472931549},
        {'art': 'cxzcz', 'order_number_1': 474269428},
        {'art': 'wezsa', 'order_number_1': 474286312},
        {'art': 'fasqw', 'order_number_1': 474286313}
    ]

    result_dict = group_dicts_by_key(data, 'order_number_1')
    print(result_dict)

