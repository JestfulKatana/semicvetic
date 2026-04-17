from __future__ import annotations

import json
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class AdminUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class SiteSetting(db.Model):
    key = db.Column(db.String(120), primary_key=True)
    value = db.Column(db.Text, nullable=False, default="")

    @classmethod
    def get_map(cls) -> dict[str, str]:
        return {row.key: row.value for row in cls.query.order_by(cls.key).all()}


class Page(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    meta_title = db.Column(db.String(255), nullable=True)
    meta_description = db.Column(db.Text, nullable=True)
    hero_subtitle = db.Column(db.Text, nullable=True)
    content_json = db.Column(db.Text, nullable=False, default="[]")
    is_published = db.Column(db.Boolean, default=True, nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)

    @property
    def blocks(self) -> list[dict]:
        return json.loads(self.content_json or "[]")

    @blocks.setter
    def blocks(self, value: list[dict]) -> None:
        self.content_json = json.dumps(value, ensure_ascii=False, indent=2)


class Teacher(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(200), nullable=False)
    specialization = db.Column(db.Text, nullable=True)
    bio = db.Column(db.Text, nullable=True)
    photo_url = db.Column(db.String(255), nullable=True)
    emoji = db.Column(db.String(20), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    sort_order = db.Column(db.Integer, default=0, nullable=False)

    programs = db.relationship("Program", back_populates="teacher", lazy=True)


class Program(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    tagline = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    emoji = db.Column(db.String(20), nullable=True)
    color = db.Column(db.String(20), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    age_min = db.Column(db.Float, nullable=True)
    age_max = db.Column(db.Float, nullable=True)
    duration_min = db.Column(db.Integer, nullable=True)
    frequency = db.Column(db.String(120), nullable=True)
    price = db.Column(db.Integer, nullable=True)
    price_unit = db.Column(db.String(50), nullable=True)
    has_landing = db.Column(db.Boolean, default=True, nullable=False)
    landing_json = db.Column(db.Text, nullable=False, default="[]")
    category = db.Column(db.String(50), nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher.id"), nullable=True)
    is_published = db.Column(db.Boolean, default=True, nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)

    teacher = db.relationship("Teacher", back_populates="programs", lazy=True)
    schedule_slots = db.relationship(
        "ScheduleSlot",
        back_populates="program",
        cascade="all, delete-orphan",
        lazy=True,
        order_by="ScheduleSlot.day_of_week",
    )
    subjects = db.relationship(
        "ProgramSubject",
        back_populates="program",
        cascade="all, delete-orphan",
        lazy=True,
    )
    reviews = db.relationship("Review", back_populates="program", lazy=True)

    @property
    def landing_blocks(self) -> list[dict]:
        return json.loads(self.landing_json or "[]")

    @landing_blocks.setter
    def landing_blocks(self, value: list[dict]) -> None:
        self.landing_json = json.dumps(value, ensure_ascii=False, indent=2)

    @property
    def price_label(self) -> str:
        if not self.price:
            return "По запросу"
        suffix = f"/{self.price_unit}" if self.price_unit else ""
        return f"от {self.price:,} ₽{suffix}".replace(",", " ")

    @property
    def age_label(self) -> str:
        if self.age_min is None and self.age_max is None:
            return "Для разных возрастов"
        if self.age_min is not None and self.age_max is not None:
            return f"{self.age_min:g}–{self.age_max:g} лет"
        if self.age_min is not None:
            return f"от {self.age_min:g} лет"
        return f"до {self.age_max:g} лет"


class ScheduleSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey("program.id"), nullable=False)
    group_name = db.Column(db.String(120), nullable=True)
    day_of_week = db.Column(db.String(50), nullable=False)
    time_start = db.Column(db.String(20), nullable=False)
    time_end = db.Column(db.String(20), nullable=False)

    program = db.relationship("Program", back_populates="schedule_slots", lazy=True)


class ProgramSubject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey("program.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    frequency = db.Column(db.String(120), nullable=True)
    emoji = db.Column(db.String(20), nullable=True)

    program = db.relationship("Program", back_populates="subjects", lazy=True)


class Review(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(200), nullable=False)
    author_initials = db.Column(db.String(10), nullable=False)
    child_info = db.Column(db.String(200), nullable=True)
    text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5, nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey("program.id"), nullable=True)
    is_published = db.Column(db.Boolean, default=True, nullable=False)

    program = db.relationship("Program", back_populates="reviews", lazy=True)


class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(32), nullable=False)
    name = db.Column(db.String(120), nullable=True)
    child_age = db.Column(db.String(50), nullable=True)
    source_page = db.Column(db.String(255), nullable=True)
    source_block = db.Column(db.String(120), nullable=True)
    utm_source = db.Column(db.String(120), nullable=True)
    utm_medium = db.Column(db.String(120), nullable=True)
    utm_campaign = db.Column(db.String(120), nullable=True)
    status = db.Column(db.String(30), default="new", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    note = db.Column(db.Text, nullable=True)


class Event(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False, index=True)
    excerpt = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    event_date = db.Column(db.Date, nullable=True)
    event_time = db.Column(db.String(50), nullable=True)
    category = db.Column(db.String(80), nullable=True)
    is_published = db.Column(db.Boolean, default=True, nullable=False)

    @property
    def display_date(self) -> str:
        target = self.event_date or self.created_at.date()
        return target.strftime("%d.%m.%Y")
