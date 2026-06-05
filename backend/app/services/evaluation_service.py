"""Evaluation service for quiz generation and grading."""

from typing import List, Dict, Any, Optional
from uuid import UUID
import json
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.settings import settings
from app.models import (
    Evaluation, Question, EvaluationAttempt, Answer,
    EvaluationType, QuestionType, Document
)
from app.rag.vector_store import retrieval_pipeline
from openai import OpenAI

logger = logging.getLogger(__name__)


class EvaluationService:
    """Service for generating and grading evaluations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._client = None
    
    def _get_client(self) -> OpenAI:
        """Lazy initialization of OpenAI client."""
        if self._client is None:
            self._client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return self._client
    
    async def generate_evaluation(
        self,
        tenant_id: UUID,
        document_id: UUID,
        created_by: UUID,
        title: str,
        description: Optional[str] = None,
        question_count: int = 10,
        difficulty: int = 1,
        evaluation_type: str = "quiz",
        time_limit_minutes: Optional[int] = None,
        passing_score: int = 60,
        subject_id: Optional[UUID] = None,
    ) -> Evaluation:
        """Create a new evaluation and queue question generation."""
        # Verify document exists
        result = await self.db.execute(
            select(Document).where(
                Document.id == document_id,
                Document.tenant_id == tenant_id,
            )
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise ValueError("Document not found")
        
        if document.status != "completed":
            raise ValueError("Document must be processed before creating evaluation")
        
        # Create evaluation
        evaluation = Evaluation(
            tenant_id=tenant_id,
            document_id=document_id,
            subject_id=subject_id,
            created_by=created_by,
            title=title,
            description=description,
            evaluation_type=EvaluationType(evaluation_type),
            question_count=question_count,
            difficulty=difficulty,
            time_limit_minutes=time_limit_minutes,
            passing_score=passing_score,
        )
        
        self.db.add(evaluation)
        await self.db.flush()
        await self.db.refresh(evaluation)
        
        return evaluation
    
    async def generate_questions(
        self,
        evaluation_id: UUID,
        tenant_id: UUID,
    ) -> int:
        """Generate questions for an evaluation using RAG."""
        result = await self.db.execute(
            select(Evaluation).where(
                Evaluation.id == evaluation_id,
                Evaluation.tenant_id == tenant_id,
            )
        )
        evaluation = result.scalar_one_or_none()
        
        if not evaluation:
            raise ValueError("Evaluation not found")
        
        # Retrieve document chunks
        chunks = await retrieval_pipeline.retrieve_for_evaluation(
            tenant_id=str(tenant_id),
            document_id=str(evaluation.document_id),
            topic="key concepts and topics",
            count=evaluation.question_count * 2,
        )
        
        if not chunks:
            raise ValueError("No document content found")
        
        # Generate questions using LLM
        questions = await self._generate_questions_llm(
            chunks=chunks,
            count=evaluation.question_count,
            difficulty=evaluation.difficulty,
        )
        
        # Save questions to database
        for i, q_data in enumerate(questions):
            question = Question(
                evaluation_id=evaluation_id,
                question_text=q_data["question"],
                question_type=QuestionType(q_data["type"]),
                explanation=q_data.get("explanation"),
                options=json.dumps(q_data["options"]) if q_data.get("options") else None,
                correct_answer=json.dumps(q_data["correct_answer"]) if q_data.get("correct_answer") else None,
                acceptable_answers=json.dumps(q_data.get("acceptable_answers")) if q_data.get("acceptable_answers") else None,
                source_chunk_id=q_data.get("source_chunk_id"),
                difficulty=q_data.get("difficulty", evaluation.difficulty),
                points=q_data.get("points", 1),
                order_index=i,
            )
            self.db.add(question)
        
        await self.db.flush()
        
        # Update evaluation stats
        evaluation.question_count = len(questions)
        await self.db.flush()
        
        return len(questions)
    
    async def _generate_questions_llm(
        self,
        chunks: List[Dict[str, Any]],
        count: int,
        difficulty: int,
    ) -> List[Dict[str, Any]]:
        """Generate questions using OpenAI."""
        client = self._get_client()
        
        # Build context from chunks
        context = "\n\n".join([
            f"[Chunk {i+1}]: {chunk['content'][:500]}..."
            for i, chunk in enumerate(chunks[:5])
        ])
        
        prompt = f"""Generate {count} educational quiz questions based on the following content.
Each question should be related to the material provided.

Difficulty level: {difficulty}/5

Content:
{context}

Generate questions in JSON format with this structure:
[
  {{
    "question": "The question text",
    "type": "multiple_choice",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0,
    "explanation": "Why this is the correct answer",
    "difficulty": {difficulty},
    "points": 1
  }}
]

Make sure questions cover different aspects of the content and vary in difficulty."""
        
        try:
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an educational quiz generator. Output ONLY valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            
            questions = json.loads(content)
            return questions
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing questions JSON: {e}")
            raise ValueError("Failed to generate questions")
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            raise
    
    async def start_attempt(
        self,
        evaluation_id: UUID,
        user_id: UUID,
        tenant_id: UUID,
    ) -> EvaluationAttempt:
        """Start a new evaluation attempt."""
        # Verify evaluation exists
        result = await self.db.execute(
            select(Evaluation).where(
                Evaluation.id == evaluation_id,
                Evaluation.tenant_id == tenant_id,
                Evaluation.is_published == True,
            )
        )
        evaluation = result.scalar_one_or_none()
        
        if not evaluation:
            raise ValueError("Evaluation not found or not published")
        
        # Create attempt
        attempt = EvaluationAttempt(
            tenant_id=tenant_id,
            evaluation_id=evaluation_id,
            user_id=user_id,
        )
        
        self.db.add(attempt)
        
        # Update evaluation stats
        evaluation.total_attempts += 1
        
        await self.db.flush()
        await self.db.refresh(attempt)
        
        return attempt
    
    async def submit_attempt(
        self,
        attempt_id: UUID,
        answers: List[Dict[str, Any]],
        tenant_id: UUID,
    ) -> Dict[str, Any]:
        """Submit answers and get grading results."""
        result = await self.db.execute(
            select(EvaluationAttempt).where(
                EvaluationAttempt.id == attempt_id,
                EvaluationAttempt.tenant_id == tenant_id,
            )
        )
        attempt = result.scalar_one_or_none()
        
        if not attempt:
            raise ValueError("Attempt not found")
        
        if attempt.completed_at:
            raise ValueError("Attempt already submitted")
        
        # Get questions
        questions_result = await self.db.execute(
            select(Question).where(Question.evaluation_id == attempt.evaluation_id)
        )
        questions = {str(q.id): q for q in questions_result.scalars().all()}
        
        total_points = 0
        earned_points = 0
        answer_results = []
        
        for answer_data in answers:
            question_id = answer_data["question_id"]
            answer_text = answer_data["answer_text"]
            
            question = questions.get(str(question_id))
            if not question:
                continue
            
            is_correct = False
            points_earned = 0
            feedback = None
            
            if question.question_type == QuestionType.MULTIPLE_CHOICE:
                # Check multiple choice answer
                correct = json.loads(question.correct_answer) if question.correct_answer else None
                if correct is not None and answer_text.isdigit():
                    selected_idx = int(answer_text)
                    is_correct = selected_idx == correct
                    points_earned = question.points if is_correct else 0
            elif question.question_type == QuestionType.TRUE_FALSE:
                correct = json.loads(question.correct_answer) if question.correct_answer else None
                is_correct = answer_text.lower() in ["true", "false"] and answer_text.lower() == (correct if isinstance(correct, str) else str(correct).lower())
                points_earned = question.points if is_correct else 0
            else:
                # Short answer - use LLM for grading
                is_correct, points_earned, feedback = await self._grade_short_answer(
                    question, answer_text
                )
            
            # Save answer
            answer = Answer(
                attempt_id=attempt_id,
                question_id=question.id,
                answer_text=answer_text,
                is_correct=is_correct,
                points_earned=points_earned,
                ai_grade_feedback=feedback,
            )
            self.db.add(answer)
            
            total_points += question.points
            earned_points += points_earned
            
            answer_results.append({
                "question_id": str(question.id),
                "is_correct": is_correct,
                "points_earned": points_earned,
                "explanation": question.explanation,
            })
        
        # Calculate score
        score = (earned_points / total_points * 100) if total_points > 0 else 0
        passed = score >= attempt.evaluation.passing_score if attempt.evaluation else False
        
        # Update attempt
        attempt.completed_at = datetime.now(timezone.utc)
        attempt.time_spent_seconds = int(
            (attempt.completed_at - attempt.started_at).total_seconds()
        )
        attempt.score = score
        attempt.passed = passed
        attempt.grading_tokens = 0  # Track this in production
        
        await self.db.flush()
        
        # Update evaluation average
        eval_result = await self.db.execute(
            select(Evaluation).where(Evaluation.id == attempt.evaluation_id)
        )
        evaluation = eval_result.scalar_one_or_none()
        if evaluation:
            avg_result = await self.db.execute(
                select(func.avg(EvaluationAttempt.score))
                .where(EvaluationAttempt.evaluation_id == attempt.evaluation_id)
            )
            evaluation.avg_score = avg_result.scalar()
        
        await self.db.flush()
        
        return {
            "attempt_id": str(attempt_id),
            "score": score,
            "passed": passed,
            "time_spent_seconds": attempt.time_spent_seconds,
            "answers": answer_results,
            "feedback": await self._generate_feedback(answer_results, score),
        }
    
    async def _grade_short_answer(
        self,
        question: Question,
        answer: str,
    ) -> tuple[bool, int, Optional[str]]:
        """Grade a short answer question using LLM."""
        acceptable = json.loads(question.acceptable_answers) if question.acceptable_answers else []
        
        # Simple exact match first
        if answer.strip().lower() in [a.lower() for a in acceptable]:
            return True, question.points, None
        
        # Use LLM for fuzzy matching
        client = self._get_client()
        prompt = f"""Grade this answer for correctness.
        
Question: {question.question_text}
Correct answers (any of these are acceptable): {acceptable}
Student's answer: {answer}

Respond with JSON: {{"correct": true/false, "partial_credit": 0-1, "feedback": "explanation"}}
Give partial credit (0.5) for answers that are close but not exact."""
        
        try:
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an educational grading assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
                max_tokens=200,
            )
            
            result = json.loads(response.choices[0].message.content)
            partial = result.get("partial_credit", 0)
            points = int(question.points * partial)
            return result.get("correct", False), points, result.get("feedback")
            
        except Exception as e:
            logger.error(f"Error grading short answer: {e}")
            return False, 0, None
    
    async def _generate_feedback(
        self,
        answer_results: List[Dict],
        score: float,
    ) -> str:
        """Generate overall feedback for the attempt."""
        correct = sum(1 for a in answer_results if a["is_correct"])
        total = len(answer_results)
        
        if score >= 90:
            level = "excellent"
        elif score >= 70:
            level = "good"
        elif score >= 50:
            level = "needs_improvement"
        else:
            level = "needs_study"
        
        feedback_map = {
            "excellent": f"Excellent work! You got {correct}/{total} correct. Keep up the great progress!",
            "good": f"Good job! You got {correct}/{total} correct. Review the explanations for incorrect answers to improve further.",
            "needs_improvement": f"You got {correct}/{total} correct. Review the topics you missed and try again.",
            "needs_study": f"You got {correct}/{total} correct. Consider reviewing the source material more carefully before retaking.",
        }
        
        return feedback_map.get(level, f"Score: {score:.1f}%")
    
    async def get_student_progress(
        self,
        user_id: UUID,
        tenant_id: UUID,
    ) -> Dict[str, Any]:
        """Get progress statistics for a student."""
        result = await self.db.execute(
            select(EvaluationAttempt)
            .where(
                EvaluationAttempt.user_id == user_id,
                EvaluationAttempt.tenant_id == tenant_id,
            )
        )
        attempts = list(result.scalars().all())
        
        if not attempts:
            return {
                "total_evaluations": 0,
                "completed_evaluations": 0,
                "avg_score": 0,
                "weak_topics": [],
                "strong_topics": [],
            }
        
        completed = [a for a in attempts if a.completed_at]
        avg_score = sum(a.score or 0 for a in completed) / len(completed) if completed else 0
        
        return {
            "total_evaluations": len(attempts),
            "completed_evaluations": len(completed),
            "avg_score": round(avg_score, 1),
            "weak_topics": [],  # TODO: Implement topic analysis
            "strong_topics": [],
        }