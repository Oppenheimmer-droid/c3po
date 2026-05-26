"""Seed database with demo data for testing."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uuid import uuid4, UUID
from datetime import datetime, timezone

from app.core.database import AsyncSessionLocal, init_db
from app.core.security import hash_password
from app.models import Tenant, User, Subject, Topic, UserRole, TenantStatus
from app.models import Document, DocumentChunk, ChatSession, ChatMessage
from app.models import Evaluation, Question, EvaluationType, QuestionType


async def seed_tenant_and_users():
    """Create demo tenant with users."""
    async with AsyncSessionLocal() as db:
        # Create superadmin (platform-wide)
        superadmin = User(
            id=uuid4(),
            tenant_id=None,  # Superadmin has no tenant
            email="admin@redrive.edu",
            password_hash=hash_password("admin123"),
            first_name="Super",
            last_name="Admin",
            role=UserRole.SUPERADMIN,
            is_active=True,
            is_verified=True,
        )
        db.add(superadmin)
        
        # Create demo tenant
        tenant = Tenant(
            id=uuid4(),
            name="Demo Academy",
            slug="demo-academy",
            status=TenantStatus.ACTIVE,
        )
        db.add(tenant)
        await db.flush()
        
        # Create admin user
        admin = User(
            id=uuid4(),
            tenant_id=tenant.id,
            email="admin@demo.com",
            password_hash=hash_password("admin123"),
            first_name="Admin",
            last_name="User",
            role=UserRole.ACADEMY_ADMIN,
            is_active=True,
            is_verified=True,
        )
        db.add(admin)
        
        # Create teacher
        teacher = User(
            id=uuid4(),
            tenant_id=tenant.id,
            email="teacher@demo.com",
            password_hash=hash_password("teacher123"),
            first_name="John",
            last_name="Teacher",
            role=UserRole.TEACHER,
            is_active=True,
            is_verified=True,
        )
        db.add(teacher)
        
        # Create students
        for i in range(3):
            student = User(
                id=uuid4(),
                tenant_id=tenant.id,
                email=f"student{i}@demo.com",
                password_hash=hash_password("student123"),
                first_name=f"Student{i}",
                last_name="Demo",
                role=UserRole.STUDENT,
                is_active=True,
                is_verified=True,
            )
            db.add(student)
        
        await db.commit()
        print(f"✓ Created superadmin: admin@redrive.edu / admin123")
        print(f"✓ Created tenant: {tenant.slug}")
        print(f"  Admin: admin@demo.com / admin123")
        print(f"  Teacher: teacher@demo.com / teacher123")
        print(f"  Students: student0@demo.com / student123, etc.")
        
        return tenant.id, admin.id, superadmin.id


async def seed_subjects(tenant_id: UUID):
    """Create demo subjects and topics."""
    async with AsyncSessionLocal() as db:
        subjects_data = [
            {
                "name": "Mathematics",
                "code": "MATH101",
                "topics": [
                    {"name": "Algebra Basics", "difficulty": 1},
                    {"name": "Quadratic Equations", "difficulty": 2},
                    {"name": "Calculus Introduction", "difficulty": 3},
                    {"name": "Linear Algebra", "difficulty": 4},
                ]
            },
            {
                "name": "Physics",
                "code": "PHYS101",
                "topics": [
                    {"name": "Newton's Laws", "difficulty": 1},
                    {"name": "Kinematics", "difficulty": 2},
                    {"name": "Thermodynamics", "difficulty": 3},
                    {"name": "Electromagnetism", "difficulty": 4},
                ]
            },
            {
                "name": "Computer Science",
                "code": "CS101",
                "topics": [
                    {"name": "Programming Basics", "difficulty": 1},
                    {"name": "Data Structures", "difficulty": 2},
                    {"name": "Algorithms", "difficulty": 3},
                    {"name": "Database Systems", "difficulty": 3},
                ]
            },
        ]
        
        created_subjects = []
        for subj_data in subjects_data:
            subject = Subject(
                id=uuid4(),
                tenant_id=tenant_id,
                name=subj_data["name"],
                code=subj_data["code"],
            )
            db.add(subject)
            await db.flush()
            
            for idx, topic_data in enumerate(subj_data["topics"]):
                topic = Topic(
                    id=uuid4(),
                    subject_id=subject.id,
                    name=topic_data["name"],
                    difficulty=topic_data["difficulty"],
                    order_index=idx,
                )
                db.add(topic)
            
            created_subjects.append(subject)
        
        await db.commit()
        print(f"✓ Created {len(created_subjects)} subjects with topics")
        
        return created_subjects


async def seed_demo_document(tenant_id: UUID, user_id: UUID):
    """Create a demo document with content."""
    async with AsyncSessionLocal() as db:
        # Create math document
        document = Document(
            id=uuid4(),
            tenant_id=tenant_id,
            uploaded_by=user_id,
            filename="demo/math_basics.txt",
            original_filename="math_basics.txt",
            file_size=2048,
            mime_type="text/plain",
            file_path="demo/math_basics.txt",
            title="Mathematics Basics - Algebra",
            description="Introduction to algebraic concepts",
            status="completed",
            page_count=1,
            chunk_count=3,
        )
        db.add(document)
        await db.flush()
        
        # Create sample chunks
        chunks_content = [
            {
                "content": "Algebra is a branch of mathematics that deals with symbols and the rules for manipulating those symbols. It is a unifying thread of almost all of mathematics and includes everything from solving elementary equations to studying abstractions such as groups, rings, and fields.",
                "chunk_index": 0,
                "page_number": 1,
            },
            {
                "content": "Variables in algebra are symbols that represent unknown values. Common variable names include x, y, and z. For example, in the equation x + 5 = 10, x is the variable and its value is 5.",
                "chunk_index": 1,
                "page_number": 1,
            },
            {
                "content": "Linear equations are equations of the first degree, meaning they involve only the first power of the variable. The general form is ax + b = 0, where a and b are constants. Example: 2x + 3 = 7 can be solved by subtracting 3 and dividing by 2 to get x = 2.",
                "chunk_index": 2,
                "page_number": 1,
            },
        ]
        
        for chunk_data in chunks_content:
            chunk = DocumentChunk(
                id=uuid4(),
                document_id=document.id,
                tenant_id=tenant_id,
                content=chunk_data["content"],
                chunk_index=chunk_data["chunk_index"],
                page_number=chunk_data["page_number"],
                start_char=0,
                end_char=len(chunk_data["content"]),
            )
            db.add(chunk)
        
        await db.commit()
        print(f"✓ Created demo document: {document.title}")
        
        return document.id


async def seed_demo_evaluation(tenant_id: UUID, document_id: UUID, user_id: UUID):
    """Create a demo evaluation."""
    async with AsyncSessionLocal() as db:
        evaluation = Evaluation(
            id=uuid4(),
            tenant_id=tenant_id,
            document_id=document_id,
            created_by=user_id,
            title="Algebra Basics Quiz",
            description="Test your knowledge of basic algebraic concepts",
            evaluation_type=EvaluationType.QUIZ,
            question_count=3,
            time_limit_minutes=15,
            passing_score=60,
            difficulty=1,
            is_published=True,
        )
        db.add(evaluation)
        await db.flush()
        
        # Create sample questions
        questions_data = [
            {
                "question_text": "What is a variable in algebra?",
                "question_type": QuestionType.MULTIPLE_CHOICE,
                "options": [
                    "A known value",
                    "A symbol representing an unknown value",
                    "A type of equation",
                    "A mathematical operation",
                ],
                "correct_answer": 1,
                "explanation": "Variables are symbols that represent unknown values in algebraic expressions.",
                "difficulty": 1,
            },
            {
                "question_text": "In the equation 2x + 3 = 7, what is the value of x?",
                "question_type": QuestionType.MULTIPLE_CHOICE,
                "options": ["1", "2", "3", "4"],
                "correct_answer": 1,
                "explanation": "2x + 3 = 7 → 2x = 4 → x = 2",
                "difficulty": 2,
            },
            {
                "question_text": "True or False: Linear equations involve variables raised to the first power only.",
                "question_type": QuestionType.TRUE_FALSE,
                "options": ["True", "False"],
                "correct_answer": 0,  # True
                "explanation": "Linear equations are first-degree equations where variables appear only to the first power.",
                "difficulty": 1,
            },
        ]
        
        for idx, q_data in enumerate(questions_data):
            import json
            question = Question(
                id=uuid4(),
                evaluation_id=evaluation.id,
                question_text=q_data["question_text"],
                question_type=q_data["question_type"],
                options=json.dumps(q_data["options"]),
                correct_answer=json.dumps(q_data["correct_answer"]),
                explanation=q_data["explanation"],
                difficulty=q_data["difficulty"],
                points=1,
                order_index=idx,
            )
            db.add(question)
        
        await db.commit()
        print(f"✓ Created demo evaluation: {evaluation.title}")
        print(f"  Contains {len(questions_data)} questions")


async def main():
    """Run all seed operations."""
    print("=" * 60)
    print("ReDrive Edu - Database Seeding")
    print("=" * 60)
    
    # Initialize database tables
    print("\n📦 Initializing database...")
    await init_db()
    print("✓ Database tables created")
    
    # Seed data
    print("\n🌱 Seeding data...")
    tenant_id, admin_id, superadmin_id = await seed_tenant_and_users()
    await seed_subjects(tenant_id)
    doc_id = await seed_demo_document(tenant_id, admin_id)
    await seed_demo_evaluation(tenant_id, doc_id, admin_id)
    
    print("\n" + "=" * 60)
    print("✅ Seeding complete!")
    print("=" * 60)
    print("\nDemo credentials:")
    print("  Superadmin (platform): admin@redrive.edu / admin123")
    print("  Admin: admin@demo.com / admin123")
    print("  Teacher: teacher@demo.com / teacher123")
    print("  Student: student0@demo.com / student123")


if __name__ == "__main__":
    asyncio.run(main())