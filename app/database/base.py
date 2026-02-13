from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy"""
    
    def to_dict(self):
        """Преобразование объекта в словарь"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def __repr__(self):
        """Строковое представление"""
        columns = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return f"<{self.__class__.__name__}({columns})>"

# Для обратной совместимости
BaseModel = declarative_base(cls=Base)
