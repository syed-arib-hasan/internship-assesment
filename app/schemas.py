from pydantic import BaseModel
from typing import Optional

class StudentCreate(BaseModel):
    name: str
    email: str

class StudentOut(StudentCreate):
    id: int
    class Config:
        from_attributes = True

class TeacherCreate(BaseModel):
    name: str
    email: str

class TeacherOut(TeacherCreate):
    id: int
    class Config:
        from_attributes = True

class CourseCreate(BaseModel):
    title: str
    capacity: int = 30
    teacher_id: Optional[int] = None

class CourseOut(CourseCreate):
    id: int
    class Config:
        from_attributes = True

class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int

class ScrapedResourceIn(BaseModel):
    title: str
    link: str
    image_url: str = ""
    price: str = ""
    scraped_at: str = ""
