from sqlalchemy import create_engine, String, ForeignKey, Boolean, Integer
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
    declared_attr,
)

# SQLAlchemy Base and session setup (SQLAlchemy 2.x style)
class Base(DeclarativeBase):
    pass
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for polymorphic inheritance
class Question(Base):
    __tablename__ = 'questions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String)  # 'open', 'exact', 'test', 'true_false', 'matching', 'order'
    
    @declared_attr
    def __mapper_args__(cls):
        return {
            'polymorphic_on': cls.type
        }

# Open-ended question type
class OpenQuestion(Question):
    __tablename__ = 'open_questions'
    __mapper_args__ = {"polymorphic_identity": "open"}
    id: Mapped[int] = mapped_column(Integer, ForeignKey('questions.id'), primary_key=True)
    question_text: Mapped[str] = mapped_column(String)  # The open-ended question text


# Exact answer question type
class ExactQuestion(Question):
    __tablename__ = 'exact_questions'
    __mapper_args__ = {"polymorphic_identity": "exact"}
    id: Mapped[int] = mapped_column(Integer, ForeignKey('questions.id'), primary_key=True)
    question_text: Mapped[str] = mapped_column(String)
    exact_answer: Mapped[str] = mapped_column(String)  # Exact answer, could be a word or number

class SingleChoiceQuestion(Question):
    __tablename__ = 'single_choice_questions'
    __mapper_args__ = {"polymorphic_identity": "single_choice"}
    id: Mapped[int] = mapped_column(Integer, ForeignKey('questions.id'), primary_key=True)
    question_text: Mapped[str] = mapped_column(String)
    # Only choice-based questions expose options
    options: Mapped[list["ChoiceOption"]] = relationship(
        "ChoiceOption",
        cascade="all, delete-orphan",
        single_parent=True,
        foreign_keys="ChoiceOption.question_id",
        overlaps="question,options",
    )

# Multiple choice question type
class MultipleChoiceQuestion(Question):
    __tablename__ = 'multiple_choice_questions'
    __mapper_args__ = {"polymorphic_identity": "multiple_choice"}
    id: Mapped[int] = mapped_column(Integer, ForeignKey('questions.id'), primary_key=True)
    question_text: Mapped[str] = mapped_column(String)
    
    # Options for the multiple-choice question
    options: Mapped[list["ChoiceOption"]] = relationship(
        "ChoiceOption",
        cascade="all, delete-orphan",
        single_parent=True,
        foreign_keys="ChoiceOption.question_id",
        overlaps="question,options",
    )


# Option table for multiple-choice questions
class ChoiceOption(Base):
    __tablename__ = 'choice_options'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String)  # Option text
    is_correct: Mapped[bool] = mapped_column(Boolean)  # Whether this option is correct or not
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey('questions.id'))  # Foreign key to the question
    
    # Many-to-one to the base Question; unidirectional to avoid adding .options to all subtypes
    question: Mapped["Question"] = relationship("Question", overlaps="options")

# True/False question type
class TrueFalseQuestion(Question):
    __tablename__ = 'true_false_questions'
    __mapper_args__ = {"polymorphic_identity": "true_false"}
    id: Mapped[int] = mapped_column(Integer, ForeignKey('questions.id'), primary_key=True)
    question_text: Mapped[str] = mapped_column(String)
    answer: Mapped[bool] = mapped_column(Boolean)  # True or False answer


# Form table with a relation to the questions
class Form(Base):
    __tablename__ = 'forms'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    
    # Relationship with questions
    questions: Mapped[list["Question"]] = relationship("Question", secondary="form_questions")


# Association table to create many-to-many relationship between forms and questions
class FormQuestion(Base):
    __tablename__ = 'form_questions'
    form_id: Mapped[int] = mapped_column(Integer, ForeignKey('forms.id'), primary_key=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey('questions.id'), primary_key=True)
    #order_by: Mapped[int] = mapped_column(Integer)  # Order of the questions in the form
    #order: Mapped[Optional[int]] = mapped_column(Integer)  # Order of the questions in the form
