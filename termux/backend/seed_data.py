"""
Seed script with imaginary subjects for testing.
Run with: python -m seed_data
"""

import asyncio
import uuid
import os
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import _get_session_local, _get_engine
from app.core.base import Base
from app.models import (
    Tenant, User, Subject, Topic, Document, Evaluation, Question,
    EvaluationAttempt, Answer, UserRole, TenantStatus,
    EvaluationType, QuestionType
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


async def create_seed_data():
    """Create seed data with imaginary subjects."""
    
    # Set up database URL if not set
    if not os.environ.get("DATABASE_URL"):
        print("⚠️  DATABASE_URL not set. Using environment variable.")
        print("   Please set DATABASE_URL before running this script.")
        print("   Example: export DATABASE_URL='postgresql://...'")
        return
    
    session_factory = _get_session_local()
    
    async with session_factory() as session:
        # Check if data already exists
        result = await session.execute(select(Tenant).limit(1))
        if result.scalar_one_or_none():
            print("Seed data already exists. Skipping...")
            return

        # 1. Create Tenant (Imaginary Academy)
        tenant = Tenant(
            id=uuid.uuid4(),
            name="Academia Imaginary Knowledge",
            slug="imaginary-academy",
            status=TenantStatus.ACTIVE,
            settings='{"theme": "blue", "features": ["chat", "evaluations", "documents"]}'
        )
        session.add(tenant)
        await session.flush()

        # 2. Create Users
        admin_password = hash_password("admin123")
        teacher_password = hash_password("teacher123")
        student_password = hash_password("student123")

        admin = User(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            email="admin@imaginary.edu",
            password_hash=admin_password,
            first_name="María",
            last_name="González",
            role=UserRole.ACADEMY_ADMIN,
            is_active=True,
            is_verified=True,
            created_at=datetime.now(timezone.utc)
        )

        teacher1 = User(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            email="prof.martinez@imaginary.edu",
            password_hash=teacher_password,
            first_name="Carlos",
            last_name="Martínez",
            role=UserRole.TEACHER,
            is_active=True,
            is_verified=True,
            created_at=datetime.now(timezone.utc)
        )

        teacher2 = User(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            email="prof.rodriguez@imaginary.edu",
            password_hash=teacher_password,
            first_name="Ana",
            last_name="Rodríguez",
            role=UserRole.TEACHER,
            is_active=True,
            is_verified=True,
            created_at=datetime.now(timezone.utc)
        )

        student1 = User(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            email="sofia.perez@imaginary.edu",
            password_hash=student_password,
            first_name="Sofía",
            last_name="Pérez",
            role=UserRole.STUDENT,
            is_active=True,
            is_verified=True,
            created_at=datetime.now(timezone.utc)
        )

        student2 = User(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            email="juan.lopez@imaginary.edu",
            password_hash=student_password,
            first_name="Juan",
            last_name="López",
            role=UserRole.STUDENT,
            is_active=True,
            is_verified=True,
            created_at=datetime.now(timezone.utc)
        )

        student3 = User(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            email="camila.diaz@imaginary.edu",
            password_hash=student_password,
            first_name="Camila",
            last_name="Díaz",
            role=UserRole.STUDENT,
            is_active=True,
            is_verified=True,
            created_at=datetime.now(timezone.utc)
        )

        session.add_all([admin, teacher1, teacher2, student1, student2, student3])
        await session.flush()

        # 3. Create Subjects with Topics
        subjects_data = [
            {
                "name": "Matemáticas",
                "code": "MATH101",
                "description": "Matemáticas básicas para educación secundaria",
                "grade_levels": "[6, 7, 8]",
                "topics": [
                    {"name": "Aritmética Básica", "description": "Operaciones con números enteros y decimales", "difficulty": 1, "order_index": 0},
                    {"name": "Fracciones y Decimales", "description": "Conversiones y operaciones con fracciones", "difficulty": 2, "order_index": 1},
                    {"name": "Ecuaciones Lineales", "description": "Resolución de ecuaciones de primer grado", "difficulty": 2, "order_index": 2},
                    {"name": "Funciones y Gráficas", "description": "Introducción a funciones y representación gráfica", "difficulty": 3, "order_index": 3},
                    {"name": "Geometría Básica", "description": "Figuras planas, perímetros y áreas", "difficulty": 2, "order_index": 4},
                    {"name": "Probabilidad y Estadística", "description": "Conceptos básicos de probabilidad y estadísticas", "difficulty": 3, "order_index": 5},
                ]
            },
            {
                "name": "Física",
                "code": "PHYS101",
                "description": "Física fundamental para estudiantes de secundaria",
                "grade_levels": "[7, 8, 9]",
                "topics": [
                    {"name": "Movimiento y Velocidad", "description": "Conceptos de cinemática básica", "difficulty": 2, "order_index": 0},
                    {"name": "Fuerzas y Leyes de Newton", "description": "Principios de la dinámica", "difficulty": 3, "order_index": 1},
                    {"name": "Energía y Trabajo", "description": "Trabajo, energía cinética y potencial", "difficulty": 3, "order_index": 2},
                    {"name": "Ondas y Sonido", "description": "Propagación de ondas y fenómenos acústicos", "difficulty": 2, "order_index": 3},
                    {"name": "Electricidad Básica", "description": "Circuitos eléctricos simples", "difficulty": 3, "order_index": 4},
                ]
            },
            {
                "name": "Química",
                "code": "CHEM101",
                "description": "Introducción a la química general",
                "grade_levels": "[8, 9, 10]",
                "topics": [
                    {"name": "Tabla Periódica", "description": "Elementos y su organización", "difficulty": 1, "order_index": 0},
                    {"name": "Enlaces Químicos", "description": "Enlaces iónicos, covalentes y metálicos", "difficulty": 3, "order_index": 1},
                    {"name": "Reacciones Químicas", "description": "Tipos de reacciones y balanceo", "difficulty": 3, "order_index": 2},
                    {"name": "Estequiometría", "description": "Cálculos en reacciones químicas", "difficulty": 4, "order_index": 3},
                    {"name": "Ácidos y Bases", "description": "Concepto de pH y neutralización", "difficulty": 3, "order_index": 4},
                ]
            },
            {
                "name": "Historia Universal",
                "code": "HIST101",
                "description": "Historia del mundo desde la antigüedad",
                "grade_levels": "[6, 7, 8, 9]",
                "topics": [
                    {"name": "Civilizaciones Antiguas", "description": "Mesopotamia, Egipto, Grecia y Roma", "difficulty": 2, "order_index": 0},
                    {"name": "Edad Media", "description": "Feudalismo, cruzadas y feudalismo", "difficulty": 2, "order_index": 1},
                    {"name": "Renacimiento y Reforma", "description": "Transformaciones culturales en Europa", "difficulty": 3, "order_index": 2},
                    {"name": "Revolución Industrial", "description": "Cambios económicos y sociales", "difficulty": 3, "order_index": 3},
                    {"name": "Guerras Mundiales", "description": "Conflictos del siglo XX", "difficulty": 3, "order_index": 4},
                ]
            },
            {
                "name": "Biología",
                "code": "BIO101",
                "description": "Ciencias naturales y biología general",
                "grade_levels": "[6, 7, 8, 9, 10]",
                "topics": [
                    {"name": "La Célula", "description": "Estructura y función celular", "difficulty": 2, "order_index": 0},
                    {"name": "Genética Básica", "description": "Herencia y ADN", "difficulty": 3, "order_index": 1},
                    {"name": "Ecosistemas", "description": "Relaciones ecológicas y medio ambiente", "difficulty": 2, "order_index": 2},
                    {"name": "El Cuerpo Humano", "description": "Sistemas y órganos principales", "difficulty": 2, "order_index": 3},
                    {"name": "Evolución", "description": "Teorías de la evolución", "difficulty": 4, "order_index": 4},
                ]
            },
            {
                "name": "Literatura",
                "code": "LIT101",
                "description": "Análisis literario y comprensión lectora",
                "grade_levels": "[6, 7, 8, 9]",
                "topics": [
                    {"name": "Géneros Literarios", "description": "Poesía, narrativa y teatro", "difficulty": 1, "order_index": 0},
                    {"name": "Figuras Retóricas", "description": "Metáforas, símil y otros recursos", "difficulty": 2, "order_index": 1},
                    {"name": "Literatura Hispana", "description": "Obras de la literatura en español", "difficulty": 3, "order_index": 2},
                    {"name": "Análisis de Textos", "description": "Técnicas de análisis literario", "difficulty": 3, "order_index": 3},
                ]
            },
            {
                "name": "Geografía",
                "code": "GEO101",
                "description": "Geografía general y del mundo",
                "grade_levels": "[6, 7, 8]",
                "topics": [
                    {"name": "Continentes y Océanos", "description": "Distribución geográfica mundial", "difficulty": 1, "order_index": 0},
                    {"name": "Climas y Zonas", "description": "Clasificación climática mundial", "difficulty": 2, "order_index": 1},
                    {"name": "Recursos Naturales", "description": "Bienes naturales y su distribución", "difficulty": 2, "order_index": 2},
                    {"name": "Población y Migraciones", "description": "Dinámica poblacional global", "difficulty": 3, "order_index": 3},
                ]
            },
            {
                "name": "Informática",
                "code": "CS101",
                "description": "Fundamentos de computación y programación",
                "grade_levels": "[6, 7, 8, 9, 10]",
                "topics": [
                    {"name": "Conceptos Básicos", "description": "Hardware, software y sistemas operativos", "difficulty": 1, "order_index": 0},
                    {"name": "Programación con Python", "description": "Introducción a la programación", "difficulty": 3, "order_index": 1},
                    {"name": "Algoritmos", "description": "Lógica y diseño de algoritmos", "difficulty": 3, "order_index": 2},
                    {"name": "Bases de Datos", "description": "Conceptos de almacenamiento de datos", "difficulty": 4, "order_index": 3},
                ]
            },
        ]

        subjects = []
        topics = []
        for subj_data in subjects_data:
            subject = Subject(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                name=subj_data["name"],
                code=subj_data["code"],
                description=subj_data["description"],
                grade_levels=subj_data["grade_levels"]
            )
            subjects.append(subject)
            session.add(subject)
            await session.flush()

            for topic_data in subj_data["topics"]:
                topic = Topic(
                    id=uuid.uuid4(),
                    subject_id=subject.id,
                    name=topic_data["name"],
                    description=topic_data["description"],
                    difficulty=topic_data["difficulty"],
                    order_index=topic_data["order_index"]
                )
                topics.append(topic)
                session.add(topic)

        # 4. Create Sample Evaluations for some subjects
        evaluations_data = [
            {
                "subject": subjects[0],  # Matemáticas
                "title": "Quiz de Aritmética Básica",
                "description": "Evaluación sobre operaciones básicas con números enteros",
                "type": EvaluationType.QUIZ,
                "difficulty": 1,
                "time_limit": 30,
                "questions": [
                    {"text": "¿Cuánto es 125 + 347?", "type": QuestionType.SHORT_ANSWER, "correct": "472", "points": 1, "difficulty": 1},
                    {"text": "¿Cuánto es 89 × 12?", "type": QuestionType.SHORT_ANSWER, "correct": "1068", "points": 2, "difficulty": 2},
                    {"text": "¿Cuál es el resultado de 1000 - 234?", "type": QuestionType.SHORT_ANSWER, "correct": "766", "points": 1, "difficulty": 1},
                    {"text": "La división 144 ÷ 12 es igual a:", "type": QuestionType.MULTIPLE_CHOICE, "options": ["10", "11", "12", "14"], "correct": "12", "points": 1, "difficulty": 1},
                    {"text": "El residuo de 157 ÷ 5 es:", "type": QuestionType.MULTIPLE_CHOICE, "options": ["1", "2", "3", "4"], "correct": "2", "points": 2, "difficulty": 2},
                ]
            },
            {
                "subject": subjects[1],  # Física
                "title": "Examen de Cinemática",
                "description": "Evaluación sobre movimiento rectilíneo uniforme",
                "type": EvaluationType.EXAM,
                "difficulty": 2,
                "time_limit": 45,
                "questions": [
                    {"text": "Un auto recorre 120 km en 2 horas. ¿Cuál es su velocidad promedio?", "type": QuestionType.SHORT_ANSWER, "correct": "60 km/h", "points": 2, "difficulty": 2},
                    {"text": "La fórmula de velocidad media es:", "type": QuestionType.MULTIPLE_CHOICE, "options": ["v = d/t", "v = t/d", "v = d×t", "v = d+t"], "correct": "v = d/t", "points": 1, "difficulty": 1},
                    {"text": "Si un objeto cae libremente, ¿qué tipo de movimiento realiza?", "type": QuestionType.MULTIPLE_CHOICE, "options": ["MRU", "MRUV", "Circular", "Parabólico"], "correct": "MRUV", "points": 2, "difficulty": 2},
                    {"text": "La aceleración se mide en:", "type": QuestionType.MULTIPLE_CHOICE, "options": ["m/s", "km/h", "m/s²", "kg"], "correct": "m/s²", "points": 1, "difficulty": 1},
                    {"text": "Un móvil recorre 200 m con velocidad constante de 10 m/s. ¿Cuánto tiempo tarda?", "type": QuestionType.SHORT_ANSWER, "correct": "20 segundos", "points": 2, "difficulty": 2},
                ]
            },
            {
                "subject": subjects[4],  # Biología
                "title": "Quiz de la Célula",
                "description": "Evaluación básica sobre estructuras celulares",
                "type": EvaluationType.QUIZ,
                "difficulty": 1,
                "time_limit": 20,
                "questions": [
                    {"text": "¿Cuál es la unidad básica de la vida?", "type": QuestionType.MULTIPLE_CHOICE, "options": ["El átomo", "La célula", "El órgano", "El tejido"], "correct": "La célula", "points": 1, "difficulty": 1},
                    {"text": "La 'central energética' de la célula es:", "type": QuestionType.MULTIPLE_CHOICE, "options": ["Núcleo", "Ribosoma", "Mitocondria", "Lisosoma"], "correct": "Mitocondria", "points": 1, "difficulty": 1},
                    {"text": "Las células vegetales tienen ___, mientras que las animales no.", "type": QuestionType.SHORT_ANSWER, "correct": "pared celular", "points": 2, "difficulty": 2},
                    {"text": "El ADN se encuentra en:", "type": QuestionType.MULTIPLE_CHOICE, "options": ["Citoplasma", "Núcleo", "Membrana", "Ribosomas"], "correct": "Núcleo", "points": 1, "difficulty": 1},
                ]
            },
            {
                "subject": subjects[3],  # Historia
                "title": "Examen de Civilizaciones Antiguas",
                "description": "Evaluación sobre las grandes civilizaciones de la antigüedad",
                "type": EvaluationType.EXAM,
                "difficulty": 2,
                "time_limit": 40,
                "questions": [
                    {"text": "¿En qué río se desarrolló la civilización egipcia?", "type": QuestionType.MULTIPLE_CHOICE, "options": ["Tigris", "Éufrates", "Nilo", "Indio"], "correct": "Nilo", "points": 1, "difficulty": 1},
                    {"text": "Los sumerios inventaron:", "type": QuestionType.MULTIPLE_CHOICE, "options": ["La escritura cuneiforme", "El alfabeto", "Los jeroglíficos", "El código Morse"], "correct": "La escritura cuneiforme", "points": 2, "difficulty": 2},
                    {"text": "La civilización griega es considerada la base de:", "type": QuestionType.MULTIPLE_CHOICE, "options": ["La democracia", "El feudalismo", "El capitalismo", "El comunismo"], "correct": "La democracia", "points": 1, "difficulty": 1},
                    {"text": "Roma fue fundada aproximadamente en el año:", "type": QuestionType.MULTIPLE_CHOICE, "options": ["1000 a.C.", "753 a.C.", "500 d.C.", "100 d.C."], "correct": "753 a.C.", "points": 2, "difficulty": 2},
                    {"text": "¿Qué pirámide es la más grande de Egipto?", "type": QuestionType.MULTIPLE_CHOICE, "options": ["Kefrén", "Menkaura", "Keops", "Snefru"], "correct": "Keops", "points": 1, "difficulty": 1},
                ]
            },
            {
                "subject": subjects[2],  # Química
                "title": "Quiz de Tabla Periódica",
                "description": "Evaluación sobre elementos químicos",
                "type": EvaluationType.QUIZ,
                "difficulty": 1,
                "time_limit": 25,
                "questions": [
                    {"text": "¿Cuántos elementos tiene la tabla periódica actual?", "type": QuestionType.MULTIPLE_CHOICE, "options": ["92", "108", "118", "120"], "correct": "118", "points": 2, "difficulty": 2},
                    {"text": "El símbolo químico del oxígeno es:", "type": QuestionType.MULTIPLE_CHOICE, "options": ["Ox", "Oxg", "O", "Og"], "correct": "O", "points": 1, "difficulty": 1},
                    {"text": "¿Qué gas forma la mayor parte de la atmósfera?", "type": QuestionType.MULTIPLE_CHOICE, "options": ["Oxígeno", "Nitrógeno", "CO2", "Argón"], "correct": "Nitrógeno", "points": 1, "difficulty": 1},
                    {"text": "Los metales se caracterizan por:", "type": QuestionType.MULTIPLE_CHOICE, "options": ["Ser frágiles", "Conducir electricidad", "Tener baja conductividad", "Ser transparentes"], "correct": "Conducir electricidad", "points": 1, "difficulty": 1},
                ]
            },
        ]

        evaluations = []
        for eval_data in evaluations_data:
            evaluation = Evaluation(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                subject_id=eval_data["subject"].id,
                created_by=teacher1.id,
                title=eval_data["title"],
                description=eval_data["description"],
                evaluation_type=eval_data["type"],
                difficulty=eval_data["difficulty"],
                time_limit_minutes=eval_data["time_limit"],
                passing_score=60,
                question_count=len(eval_data["questions"]),
                total_attempts=0,
                is_published=True,
                created_at=datetime.now(timezone.utc)
            )
            evaluations.append(evaluation)
            session.add(evaluation)
            await session.flush()

            for i, q_data in enumerate(eval_data["questions"]):
                if q_data["type"] == QuestionType.MULTIPLE_CHOICE:
                    options = q_data["options"]
                    correct = q_data["correct"]
                else:
                    options = None
                    correct = q_data["correct"]

                question = Question(
                    id=uuid.uuid4(),
                    evaluation_id=evaluation.id,
                    question_text=q_data["text"],
                    question_type=q_data["type"],
                    options=str(options) if options else None,
                    correct_answer=correct,
                    difficulty=q_data["difficulty"],
                    points=q_data["points"],
                    order_index=i,
                    explanation=f"Respuesta correcta: {correct}"
                )
                session.add(question)

        # 5. Create Sample Evaluation Attempts
        attempt1 = EvaluationAttempt(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            evaluation_id=evaluations[0].id,
            user_id=student1.id,
            started_at=datetime.now(timezone.utc) - timedelta(days=2),
            completed_at=datetime.now(timezone.utc) - timedelta(days=2) + timedelta(minutes=25),
            time_spent_seconds=1500,
            score=80.0,
            passed=True,
            grading_tokens=500
        )

        attempt2 = EvaluationAttempt(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            evaluation_id=evaluations[1].id,
            user_id=student1.id,
            started_at=datetime.now(timezone.utc) - timedelta(days=1),
            completed_at=datetime.now(timezone.utc) - timedelta(days=1) + timedelta(minutes=40),
            time_spent_seconds=2400,
            score=72.0,
            passed=True,
            grading_tokens=750
        )

        attempt3 = EvaluationAttempt(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            evaluation_id=evaluations[2].id,
            user_id=student2.id,
            started_at=datetime.now(timezone.utc) - timedelta(hours=12),
            completed_at=datetime.now(timezone.utc) - timedelta(hours=12) + timedelta(minutes=18),
            time_spent_seconds=1080,
            score=100.0,
            passed=True,
            grading_tokens=300
        )

        attempt4 = EvaluationAttempt(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            evaluation_id=evaluations[0].id,
            user_id=student3.id,
            started_at=datetime.now(timezone.utc) - timedelta(hours=6),
            completed_at=datetime.now(timezone.utc) - timedelta(hours=6) + timedelta(minutes=28),
            time_spent_seconds=1680,
            score=55.0,
            passed=False,
            grading_tokens=450
        )

        session.add_all([attempt1, attempt2, attempt3, attempt4])
        await session.flush()

        # Update evaluation stats
        evaluations[0].total_attempts = 2
        evaluations[0].avg_score = (80.0 + 55.0) / 2
        evaluations[1].total_attempts = 1
        evaluations[1].avg_score = 72.0
        evaluations[2].total_attempts = 1
        evaluations[2].avg_score = 100.0

        await session.commit()

        print("=" * 60)
        print("SEED DATA CREATED SUCCESSFULLY!")
        print("=" * 60)
        print(f"\n📚 Subjects created: {len(subjects_data)}")
        print(f"📝 Topics created: {len(topics)}")
        print(f"👥 Users created: 6 (1 admin, 2 teachers, 3 students)")
        print(f"📋 Evaluations created: {len(evaluations_data)}")
        print(f"✅ Evaluation attempts: 4")
        print("\n" + "=" * 60)
        print("TEST CREDENTIALS")
        print("=" * 60)
        print("\n👤 Admin (Academy Admin):")
        print("   Email: admin@imaginary.edu")
        print("   Password: admin123")
        print("\n👨‍🏫 Teacher 1:")
        print("   Email: prof.martinez@imaginary.edu")
        print("   Password: teacher123")
        print("\n👩‍🏫 Teacher 2:")
        print("   Email: prof.rodriguez@imaginary.edu")
        print("   Password: teacher123")
        print("\n👨‍🎓 Student 1:")
        print("   Email: sofia.perez@imaginary.edu")
        print("   Password: student123")
        print("\n👩‍🎓 Student 2:")
        print("   Email: juan.lopez@imaginary.edu")
        print("   Password: student123")
        print("\n👩‍🎓 Student 3:")
        print("   Email: camila.diaz@imaginary.edu")
        print("   Password: student123")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(create_seed_data())
