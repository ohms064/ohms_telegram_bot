from datetime import datetime
from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass(order=True)
class Expenses:
    time: datetime
    quantity: float = 0
    reason: str = ""
    tag: str = ""

    def get_user_repr(self) -> str:
        time = self.time.strftime('%d/%m/%Y')
        result = f"Gasto: \n\t-Fecha: {time}\n\t-Cantidad: {self.quantity}"
        if self.tag:
            result += f"\n\t-Tag: {self.tag}"
        if self.reason:
            result += f"\n\t-Razón: {self.reason}"
        return result
