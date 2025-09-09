# Polymorphism Example - API Output Formats

## Project Context
This base serves as a foundation for creating exams or test evaluations, allowing various types of questions to be included. It uses SQLAlchemy 2.x with explicit polymorphic identities and Pydantic with discriminators to automatically parse and validate the different question structures. This approach facilitates the creation and management of dynamic, scalable evaluations.

## Endpoint `/form/1` Output Formats

The endpoint `/form/1` returns a sample form.

All fields of each question are returned directly at the top level within the question object:

```json
{
  "id": 1,
  "name": "Sample Form",
  "questions": [
    {
      "id": 1,
      "type": "open",
      "question_text": "What is your name?"
    },
    {
      "id": 2,
      "type": "exact",
      "question_text": "What is the capital of France?",
      "exact_answer": "Paris"
    },
    {
      "id": 3,
      "type": "multiple_choice",
      "question_text": "Which of these is the capital of Italy?",
      "options": [
        {
          "id": 1,
          "text": "Rome",
          "is_correct": true
        },
        {
          "id": 2,
          "text": "Madrid",
          "is_correct": false
        },
        {
          "id": 3,
          "text": "Paris",
          "is_correct": false
        }
      ]
    },
    {
      "id": 4,
      "type": "true_false",
      "question_text": "Is the earth flat?",
      "answer": false
    }
  ]
}
```
