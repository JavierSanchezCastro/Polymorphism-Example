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
    SingleChoiceQuestion as SingleChoiceQuestionDB,
    ChoiceOption,
)

# Pydantic models (API)
from models import (
    QuestionUnion,
    FormCreate,
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
            question_text="Select the first prime numbers"
        )
        option1 = ChoiceOption(text="2", is_correct=True)
        option2 = ChoiceOption(text="3", is_correct=True)
        option3 = ChoiceOption(text="4", is_correct=False)
        multiple_choice_question.options = [option1, option2, option3]

        single_choice_question = SingleChoiceQuestionDB(
            question_text="What is the capital of Italy?"
        )
        option1 = ChoiceOption(text="Rome", is_correct=True)
        option2 = ChoiceOption(text="Madrid", is_correct=False)
        option3 = ChoiceOption(text="Paris", is_correct=False)
        single_choice_question.options = [option1, option2, option3]

        true_false_question = TrueFalseQuestionDB(
            question_text="Is the earth flat?", answer=False
        )

        form.questions = [
            open_question,
            exact_question,
            multiple_choice_question,
            single_choice_question,
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

# --- Builders to avoid if/elif on question type ---
def _build_open(q):
    return OpenQuestionDB(question_text=q.question_text)

def _build_exact(q):
    return ExactQuestionDB(question_text=q.question_text, exact_answer=q.exact_answer)

def _build_multiple_choice(q):
    qdb = MultipleChoiceQuestionDB(question_text=q.question_text)
    qdb.options = [ChoiceOption(text=o.text, is_correct=o.is_correct) for o in q.options]
    return qdb

def _build_true_false(q):
    return TrueFalseQuestionDB(question_text=q.question_text, answer=q.answer)

def _build_single_choice(q):
    qdb = SingleChoiceQuestionDB(question_text=q.question_text)
    qdb.options = [ChoiceOption(text=o.text, is_correct=o.is_correct) for o in q.options]
    return qdb

QUESTION_BUILDERS = {
    "open": _build_open,
    "exact": _build_exact,
    "single_choice": _build_single_choice,
    "multiple_choice": _build_multiple_choice,
    "true_false": _build_true_false,
}

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


@app.post("/forms", response_model=FormBase, status_code=201)
def create_form(payload: FormCreate, db: Session = Depends(get_db)):
    try:
        created_questions: list[QuestionDB] = []

        # Create and stage questions via registry
        for q in payload.questions:
            builder = QUESTION_BUILDERS.get(q.type)
            if builder is None:
                raise HTTPException(status_code=400, detail=f"Unsupported question type: {q.type}")
            qdb = builder(q)
            db.add(qdb)
            created_questions.append(qdb)

        # Create form and attach questions
        form_db = FormDB(name=payload.name)
        db.add(form_db)
        db.flush()  # ensure form_db has an id

        # Link questions to the form (association table)
        form_db.questions = created_questions

        db.commit()
        db.refresh(form_db)
        return form_db
    except HTTPException:
        # bubble up explicit HTTP errors
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
