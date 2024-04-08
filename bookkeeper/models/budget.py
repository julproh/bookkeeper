"""
Модель бюджета
"""

from dataclasses import dataclass

ALLOWED_PERIODS = ['День', 'Неделя', 'Месяц']


@dataclass(slots=True)
class Budget:
    """
    Модель бюджета
    interval -  "День"/"Неделя"/"Месяц",
    amount - сумму затрат
    limit - ограничение по затратам на выбранный период
    """

    amount: int
    period: str
    pk: int = 0
