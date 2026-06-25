# db_requester/movies.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime
from .mixins import ToDictMixin  # Импортируем миксин

Base = declarative_base()


class MovieDBModel(Base, ToDictMixin):  # ← Добавляем миксин
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)
    description = Column(String)
    image_url = Column(String)
    location = Column(String)
    published = Column(Boolean)
    rating = Column(Integer)
    genre_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)

    # to_dict теперь берется из миксина — его можно удалить!

    def __repr__(self):
        return f"<Movie(id={self.id}, name='{self.name}', price={self.price}, rating={self.rating})>"