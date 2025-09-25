from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime, timezone

# Person is *abstract* conceptually — we use Python inheritance but each subclass has its own table
class PersonMixin:
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)

class Student(Base, PersonMixin):
    __tablename__ = "students"
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")

class Teacher(Base, PersonMixin):
    __tablename__ = "teachers"
    courses = relationship("Course", back_populates="teacher", cascade="all, delete-orphan")

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    capacity = Column(Integer, default=30)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)
    teacher = relationship("Teacher", back_populates="courses")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")

class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    enrolled_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

    __table_args__ = (UniqueConstraint('student_id', 'course_id', name='uq_student_course'),)

# scraped resources table
class ScrapedResource(Base):
    __tablename__ = "scraped_resources"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    link = Column(String(1024), unique=True, index=True)
    image_url = Column(String(1024))
    price = Column(String(50))
    scraped_at = Column(String(32))
