from sqlalchemy.orm import Session
from . import models, schemas
from sqlalchemy.exc import IntegrityError

# Students
def create_student(db: Session, student: schemas.StudentCreate):
    db_student = models.Student(name=student.name, email=student.email)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def get_student(db: Session, student_id: int):
    return db.query(models.Student).filter(models.Student.id == student_id).first()

def delete_student(db: Session, student_id: int) -> bool:
    s = get_student(db, student_id)
    if not s:
        return False
    db.delete(s)
    db.commit()
    return True

# Teachers
def create_teacher(db: Session, teacher: schemas.TeacherCreate):
    dbt = models.Teacher(name=teacher.name, email=teacher.email)
    db.add(dbt)
    db.commit()
    db.refresh(dbt)
    return dbt

def get_teacher(db: Session, teacher_id: int):
    return db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()

def delete_teacher(db: Session, teacher_id: int) -> bool:
    t = get_teacher(db, teacher_id)
    if not t:
        return False
    db.delete(t)
    db.commit()
    return True

# Courses
def create_course(db: Session, course: schemas.CourseCreate):
    c = models.Course(title=course.title, capacity=course.capacity, teacher_id=course.teacher_id)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

def get_course(db: Session, course_id: int):
    return db.query(models.Course).filter(models.Course.id == course_id).first()

def delete_course(db: Session, course_id: int) -> bool:
    c = get_course(db, course_id)
    if not c:
        return False
    db.delete(c)
    db.commit()
    return True

# Enrollment business rules:
def enroll_student(db: Session, student_id: int, course_id: int):
    course = get_course(db, course_id)
    if not course:
        raise ValueError("Course not found")
    # capacity check
    current = db.query(models.Enrollment).filter(models.Enrollment.course_id == course_id).count()
    if current >= course.capacity:
        raise ValueError("Course is full")
    # duplicate check
    existing = db.query(models.Enrollment).filter(models.Enrollment.course_id == course_id, models.Enrollment.student_id == student_id).first()
    if existing:
        raise ValueError("Student already enrolled")
    e = models.Enrollment(student_id=student_id, course_id=course_id)
    db.add(e)
    db.commit()
    db.refresh(e)
    return e

# Import scraped resources:
def import_scraped(db: Session, items: list[dict]):
    added = []
    for it in items:
        # skip if link exists
        if db.query(models.ScrapedResource).filter(models.ScrapedResource.link == it.get("link")).first():
            continue
        sr = models.ScrapedResource(
            title = it.get("title"),
            link = it.get("link"),
            image_url = it.get("image_url"),
            price = it.get("price"),
            scraped_at = it.get("scraped_at")
        )
        db.add(sr)
        added.append(sr)
    db.commit()
    # refresh to get ids
    for a in added:
        db.refresh(a)
    return added

def list_scraped(db: Session, skip=0, limit=100):
    return db.query(models.ScrapedResource).offset(skip).limit(limit).all()

def delete_scraped(db: Session, scraped_id: int) -> bool:
    row = db.query(models.ScrapedResource).filter(models.ScrapedResource.id == scraped_id).first()
    if not row:
        return False
    db.delete(row)
    db.commit()
    return True
