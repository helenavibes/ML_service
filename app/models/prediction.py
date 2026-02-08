from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

from app.models.user import AuditableEntity
from app.models.enums import TaskStatus


class DataValidator(ABC):
    @abstractmethod
    def validate(self, data: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        pass


class SimpleDataValidator(DataValidator):
    def __init__(self, required_fields: List[str]):
        self._required_fields = required_fields

    def validate(self, data: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        valid_data = []
        invalid_data = []

        for item in data:
            if self._is_valid(item):
                valid_data.append(item)
            else:
                invalid_data.append(item)

        return valid_data, invalid_data

    def _is_valid(self, item: Dict[str, Any]) -> bool:
        for field in self._required_fields:
            if field not in item:
                return False
        return True


class PredictionTask(AuditableEntity):
    def __init__(
            self,
            user_id: str,
            model_id: str,
            input_data: List[Dict[str, Any]],
            status: TaskStatus = TaskStatus.PENDING,
            id: Optional[str] = None
    ):
        super().__init__(id)
        self._user_id = user_id
        self._model_id = model_id
        self._input_data = input_data
        self._status = status
        self._valid_data: List[Dict[str, Any]] = []
        self._invalid_data: List[Dict[str, Any]] = []
        self._result: Optional[List[Any]] = None
        self._total_cost: Optional[float] = None
        self._error_message: Optional[str] = None
        self._completed_at: Optional[datetime] = None

    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def model_id(self) -> str:
        return self._model_id

    @property
    def input_data(self) -> List[Dict[str, Any]]:
        return self._input_data

    @property
    def status(self) -> TaskStatus:
        return self._status

    @property
    def valid_data(self) -> List[Dict[str, Any]]:
        return self._valid_data

    @property
    def invalid_data(self) -> List[Dict[str, Any]]:
        return self._invalid_data

    @property
    def result(self) -> Optional[List[Any]]:
        return self._result

    @property
    def total_cost(self) -> Optional[float]:
        return self._total_cost

    @property
    def error_message(self) -> Optional[str]:
        return self._error_message

    @property
    def completed_at(self) -> Optional[datetime]:
        return self._completed_at

    def set_validated_data(
            self,
            valid_data: List[Dict[str, Any]],
            invalid_data: List[Dict[str, Any]]
    ) -> None:
        self._valid_data = valid_data
        self._invalid_data = invalid_data
        self.update_timestamp()

    def start_processing(self) -> None:
        self._status = TaskStatus.PROCESSING
        self.update_timestamp()

    def complete(
            self,
            result: List[Any],
            total_cost: float
    ) -> None:
        self._status = TaskStatus.COMPLETED
        self._result = result
        self._total_cost = total_cost
        self._completed_at = datetime.now()
        self.update_timestamp()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self._id,
            'user_id': self._user_id,
            'model_id': self._model_id,
            'input_data': self._input_data,
            'status': self._status.value,
            'valid_data': self._valid_data,
            'invalid_data': self._invalid_data,
            'result': self._result,
            'total_cost': self._total_cost,
            'error_message': self._error_message,
            'created_at': self._created_at.isoformat(),
            'updated_at': self._updated_at.isoformat(),
            'completed_at': self._completed_at.isoformat() if self._completed_at else None
        }