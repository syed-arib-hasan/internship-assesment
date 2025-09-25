from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, schemas, database
from .database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

# Students
@router.post("/students", response_model=schemas.StudentOut)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_student(db, student)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/students/{id}", response_model=schemas.StudentOut)
def get_student(id: int, db: Session = Depends(get_db)):
    s = crud.get_student(db, id)
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")
    return s

@router.delete("/students/{id}")
def delete_student(id: int, db: Session = Depends(get_db)):
    ok = crud.delete_student(db, id)
    if not ok:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"deleted": True}

# Teachers
@router.post("/teachers", response_model=schemas.TeacherOut)
def create_teacher(teacher: schemas.TeacherCreate, db: Session = Depends(get_db)):
    return crud.create_teacher(db, teacher)

@router.delete("/teachers/{id}")
def delete_teacher(id: int, db: Session = Depends(get_db)):
    ok = crud.delete_teacher(db, id)
    if not ok:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return {"deleted": True}

# Courses
@router.post("/courses", response_model=schemas.CourseOut)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    return crud.create_course(db, course)

@router.get("/courses/{id}", response_model=schemas.CourseOut)
def get_course(id:int, db: Session = Depends(get_db)):
    c = crud.get_course(db, id)
    if not c:
        raise HTTPException(status_code=404, detail="Course not found")
    return c

@router.delete("/courses/{id}")
def delete_course(id: int, db: Session = Depends(get_db)):
    ok = crud.delete_course(db, id)
    if not ok:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"deleted": True}

# Enroll
@router.post("/students/{id}/enroll")
def enroll(id:int, payload: dict, db: Session = Depends(get_db)):
    # payload must provide course_id
    course_id = payload.get("course_id")
    if course_id is None:
        raise HTTPException(status_code=400, detail="course_id required")
    try:
        e = crud.enroll_student(db, id, course_id)
        return {"enrollment_id": e.id}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

# Scraped import
@router.post("/import/scraped")
def import_scraped(items: list[schemas.ScrapedResourceIn], db: Session = Depends(get_db)):
    added = crud.import_scraped(db, [it.model_dump() for it in items])
    return {"imported": len(added)}

@router.get("/scraped_resources")
def list_scraped(db: Session = Depends(get_db)):
    return crud.list_scraped(db)

@router.delete("/scraped_resources/{id}")
def delete_scraped(id: int, db: Session = Depends(get_db)):
    ok = crud.delete_scraped(db, id)
    if not ok:
        raise HTTPException(status_code=404, detail="Scraped resource not found")
    return {"deleted": True}
