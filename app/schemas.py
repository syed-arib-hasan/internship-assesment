from pydantic import BaseModel, ConfigDict
from typing import Optional

class StudentCreate(BaseModel):
    name: str
    email: str

class StudentOut(StudentCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class TeacherCreate(BaseModel):
    name: str
    email: str

class TeacherOut(TeacherCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class CourseCreate(BaseModel):
    title: str
    capacity: int = 30
    teacher_id: Optional[int] = None

class CourseOut(CourseCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int

class ScrapedResourceIn(BaseModel):
    title: str
    link: str
    image_url: str = ""
    price: str = ""
    scraped_at: str = ""
