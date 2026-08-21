import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, Time, Enum, DateTime, Text, JSON, UniqueConstraint, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum
from datetime import datetime, time
from .database import Base

class RoleEnum(enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    SCHOOL_ADMIN = "SCHOOL_ADMIN"
    PRINCIPAL = "PRINCIPAL"
    TIMETABLE_COORDINATOR = "TIMETABLE_COORDINATOR"
    TEACHER = "TEACHER"

class OTPCode(Base):
    __tablename__ = "otp_codes"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, index=True, nullable=False)
    otp = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.TEACHER, nullable=False)
    is_active = Column(Boolean, default=True)
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    school = relationship("School")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    school_id = Column(String, ForeignKey("schools.id", ondelete="CASCADE"), nullable=True)

    # Relationships
    teacher_profile = relationship("Teacher", back_populates="user", uselist=False, cascade="all, delete-orphan")
    school = relationship("School", back_populates="users")

class School(Base):
    __tablename__ = "schools"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    code = Column(String, unique=True, index=True)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    pincode = Column(String)
    phone = Column(String)
    email = Column(String)
    website = Column(String)
    board = Column(String)
    medium = Column(String)
    
    # Relationships
    academic_years = relationship("AcademicYear", back_populates="school", cascade="all, delete-orphan")
    settings = relationship("SchoolSetting", back_populates="school", uselist=False, cascade="all, delete-orphan")
    users = relationship("User", back_populates="school", cascade="all, delete-orphan")
    teachers = relationship("Teacher", back_populates="school", cascade="all, delete-orphan")
    classrooms = relationship("Classroom", back_populates="school", cascade="all, delete-orphan")

class SchoolSetting(Base):
    __tablename__ = "school_settings"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id = Column(String, ForeignKey("schools.id", ondelete="CASCADE"), unique=True)
    
    working_days = Column(Integer, default=5) # Deprecated by weekly_schedule
    start_time = Column(Time, default=time(8, 0))
    end_time = Column(Time, default=time(14, 0))
    number_of_periods = Column(Integer, default=7) # Deprecated by weekly_schedule
    period_duration = Column(Integer, default=45) # minutes
    lunch_break_period = Column(Integer, default=4) # Deprecated by weekly_schedule
    assembly_duration = Column(Integer, default=15) # minutes
    total_weekly_periods = Column(Integer, default=40) # Overall constraint for validating subjects and teachers
    max_weekly_teacher_periods = Column(Integer, default=32) # Global max workload per teacher
    
    # Flexible scheduling definition:
    # [
    #   {"day": 0, "is_working": true, "periods": 7, "lunch_period": 4},
    #   {"day": 1, "is_working": true, "periods": 7, "lunch_period": 4},
    #   {"day": 2, "is_working": true, "periods": 7, "lunch_period": 4},
    #   {"day": 3, "is_working": true, "periods": 7, "lunch_period": 4},
    #   {"day": 4, "is_working": true, "periods": 7, "lunch_period": 4},
    #   {"day": 5, "is_working": true, "periods": 4, "lunch_period": null},
    #   {"day": 6, "is_working": false, "periods": 0, "lunch_period": null}
    # ]
    weekly_schedule = Column(JSON, nullable=True)
    
    # Relationships
    school = relationship("School", back_populates="settings")

class AcademicYear(Base):
    __tablename__ = "academic_years"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id = Column(String, ForeignKey("schools.id", ondelete="CASCADE"))
    name = Column(String, nullable=False) # e.g., "2024-2025"
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=False)
    
    school = relationship("School", back_populates="academic_years")
    classes = relationship("SchoolClass", back_populates="academic_year", cascade="all, delete-orphan")

class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    employee_id = Column(String, unique=True, index=True, nullable=False)
    mobile = Column(String, nullable=True)
    qualification = Column(String, nullable=True)
    max_daily_periods = Column(Integer, default=7)
    max_weekly_periods = Column(Integer, default=32)
    is_active = Column(Boolean, default=True)
    is_demo = Column(Boolean, default=False)
    school_id = Column(String, ForeignKey("schools.id", ondelete="CASCADE"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="teacher_profile")
    class_teacher_of = relationship("Division", back_populates="class_teacher", foreign_keys="Division.class_teacher_id", uselist=False)
    subjects = relationship("TeacherSubject", back_populates="teacher", cascade="all, delete-orphan")
    leaves = relationship("TeacherLeave", back_populates="teacher", cascade="all, delete-orphan")
    slots = relationship("TimetableSlot", back_populates="teacher", cascade="all, delete-orphan")
    school = relationship("School", back_populates="teachers")

class SchoolClass(Base):
    __tablename__ = "classes"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    academic_year_id = Column(String, ForeignKey("academic_years.id", ondelete="CASCADE"))
    name = Column(String, nullable=False) # e.g. "10", "Jr KG"
    level = Column(Integer, nullable=False) # for sorting
    is_demo = Column(Boolean, default=False)
    
    # Relationships
    academic_year = relationship("AcademicYear", back_populates="classes")
    divisions = relationship("Division", back_populates="school_class", cascade="all, delete-orphan")
    subjects = relationship("Subject", back_populates="school_class", cascade="all, delete-orphan")

class Division(Base):
    __tablename__ = "divisions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    class_id = Column(String, ForeignKey("classes.id", ondelete="CASCADE"))
    name = Column(String, nullable=False) # e.g. "A", "B"
    class_teacher_id = Column(String, ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True)
    classroom_id = Column(String, ForeignKey("classrooms.id", ondelete="SET NULL"), nullable=True)
    is_demo = Column(Boolean, default=False)
    
    # Relationships
    school_class = relationship("SchoolClass", back_populates="divisions")
    class_teacher = relationship("Teacher", back_populates="class_teacher_of", foreign_keys=[class_teacher_id])
    classroom = relationship("Classroom", back_populates="divisions")
    slots = relationship("TimetableSlot", back_populates="division", cascade="all, delete-orphan")

class Classroom(Base):
    __tablename__ = "classrooms"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False) # e.g. "Room 101"
    capacity = Column(Integer, default=40)
    is_lab = Column(Boolean, default=False)
    school_id = Column(String, ForeignKey("schools.id", ondelete="CASCADE"), nullable=True)
    
    divisions = relationship("Division", back_populates="classroom")
    school = relationship("School", back_populates="classrooms")

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    class_id = Column(String, ForeignKey("classes.id", ondelete="CASCADE"), nullable=True)
    name = Column(String, nullable=False)
    code = Column(String, index=True)
    weekly_periods = Column(Integer, default=5)
    double_period_allowed = Column(Boolean, default=False)
    is_demo = Column(Boolean, default=False)
    is_demo = Column(Boolean, default=False)
    is_lab = Column(Boolean, default=False)
    
    __table_args__ = (
        UniqueConstraint('code', 'class_id', name='uq_subject_code_class'),
    )
    
    school_class = relationship("SchoolClass", back_populates="subjects")
    teachers = relationship("TeacherSubject", back_populates="subject", cascade="all, delete-orphan")
    slots = relationship("TimetableSlot", back_populates="subject", cascade="all, delete-orphan")

class TeacherSubject(Base):
    __tablename__ = "teacher_subjects"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    teacher_id = Column(String, ForeignKey("teachers.id", ondelete="CASCADE"))
    subject_id = Column(String, ForeignKey("subjects.id", ondelete="CASCADE"))
    division_id = Column(String, ForeignKey("divisions.id", ondelete="CASCADE"))
    
    teacher = relationship("Teacher", back_populates="subjects")
    subject = relationship("Subject", back_populates="teachers")
    division = relationship("Division")

class TimetableSlot(Base):
    __tablename__ = "timetable_slots"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    division_id = Column(String, ForeignKey("divisions.id", ondelete="CASCADE"))
    subject_id = Column(String, ForeignKey("subjects.id", ondelete="CASCADE"))
    teacher_id = Column(String, ForeignKey("teachers.id", ondelete="CASCADE"))
    day_of_week = Column(Integer, nullable=False) # 0=Monday, 6=Sunday
    period_number = Column(Integer, nullable=False)
    is_double_period = Column(Boolean, default=False)
    
    division = relationship("Division", back_populates="slots")
    subject = relationship("Subject", back_populates="slots")
    teacher = relationship("Teacher", back_populates="slots")
    substitutions = relationship("Substitution", back_populates="original_slot", cascade="all, delete-orphan")

class TeacherLeave(Base):
    __tablename__ = "teacher_leaves"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    teacher_id = Column(String, ForeignKey("teachers.id", ondelete="CASCADE"))
    date = Column(DateTime, nullable=False)
    leave_type = Column(String, default="FULL") # FULL, FIRST_HALF, SECOND_HALF
    reason = Column(String, nullable=True)
    
    teacher = relationship("Teacher", back_populates="leaves")

class Substitution(Base):
    __tablename__ = "substitutions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    date = Column(DateTime, nullable=False)
    original_slot_id = Column(String, ForeignKey("timetable_slots.id", ondelete="CASCADE"))
    substitute_teacher_id = Column(String, ForeignKey("teachers.id", ondelete="CASCADE"))
    
    original_slot = relationship("TimetableSlot", back_populates="substitutions")
    substitute_teacher = relationship("Teacher", foreign_keys=[substitute_teacher_id])

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String, nullable=False)
    resource = Column(String, nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Payment(Base):
    __tablename__ = "payments"
    order_id = Column(String, primary_key=True)
    school_id = Column(String, ForeignKey("schools.id", ondelete="CASCADE"))
    amount = Column(Float, nullable=False)
    status = Column(String, default="PENDING")
    created_at = Column(DateTime, default=datetime.utcnow)
    school = relationship("School")
