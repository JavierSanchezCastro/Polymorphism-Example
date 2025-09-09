from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends

# ORM models (DB)
from tables import (
    Base,
    engine,
    SessionLocal,
    Form as FormDB,
    Question as QuestionDB,
    OpenQuestion as OpenQuestionDB,
    ExactQuestion as ExactQuestionDB,
    MultipleChoiceQuestion as MultipleChoiceQuestionDB,
    TrueFalseQuestion as TrueFalseQuestionDB,
    MultipleChoiceOption,
)

# Pydantic models (API)
from models import (
    QuestionUnion,
)

# Create all tables
Base.metadata.create_all(bind=engine)

"""Seed a sample form once for convenience in dev."""
db = SessionLocal()
try:
    if db.query(FormDB).count() == 0:
        form = FormDB(name="Sample Form")

        open_question = OpenQuestionDB(question_text="What is your name?")
        exact_question = ExactQuestionDB(
            question_text="What is the capital of France?", exact_answer="Paris"
        )
        multiple_choice_question = MultipleChoiceQuestionDB(
            question_text="Which of these is the capital of Italy?"
        )
        option1 = MultipleChoiceOption(text="Rome", is_correct=True)
        option2 = MultipleChoiceOption(text="Madrid", is_correct=False)
        option3 = MultipleChoiceOption(text="Paris", is_correct=False)
        multiple_choice_question.options = [option1, option2, option3]

        true_false_question = TrueFalseQuestionDB(
            question_text="Is the earth flat?", answer=False
        )

        form.questions = [
            open_question,
            exact_question,
            multiple_choice_question,
            true_false_question,
        ]

        db.add(form)
        db.commit()
finally:
    db.close()

print("Form created and questions added successfully!")

# FastAPI setup
app = FastAPI()


class FormBase(BaseModel):
    id: int
    name: str
    questions: list[QuestionUnion]

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/forms/{form_id}", response_model=FormBase)
def get_form(form_id: int, db: Session = Depends(get_db)):
    form = db.query(FormDB).filter(FormDB.id == form_id).first()
    if form is None:
        raise HTTPException(status_code=404, detail="Form not found")
    return form
