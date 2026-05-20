from dataclasses import dataclass
from datetime import date
import decimal


@dataclass
class Workout:
    workout_date: date
    exercise_type: str
    quantity: float
    unit: str
    goal_id: int = None
    register_user_id: int = None

    def __str__(self):
        return (  # f'Тренировка: {self.exercise_type}\n'
            f'📅 Дата выполнения: {self.workout_date}\n'
            f'💪 Выполнено: {self.quantity}\n'
            f'Ед.измерения: {self.unit}\n'
        )


@dataclass
class Goal:
    start_date: date
    end_date: date
    target_exercise: str
    target_quantity: float
    unit: str
    status: str = 'active'
    register_user_id: int = None

    def __str__(self):
        return (f'📌\n'
                f'Цель по тренировке: {self.target_exercise}\n'
                f'Период цели: с {self.start_date} — по {self.end_date}\n'
                f'План цели: {self.target_quantity}\n'
                f'Ед.измерения: {self.unit}'
                )


@dataclass
class ViewGoal:
    id_goal: int
    start_date: date
    end_date: date
    target_exercise: str
    target_quantity: float
    unit: str
    status: str = 'active'
    register_user_id: int = None

    def __str__(self):
        return (f'📌\n'
                f'Статус: {self.status}\n'
                f'Цель по тренировке: {self.target_exercise}\n'
                f'Период цели: с {self.start_date} — по {self.end_date}\n'
                f'План цели: {self.target_quantity}\n'
                f'Ед.измерения: {self.unit}'
                )


@dataclass
class InfoGoal:
    register_user_id: int
    target_exercise: str
    id_goal: int
    target_quantity: decimal
    start_date: date
    end_date: date
    workout_sessions_count: int
    total_quantity: decimal
    unit: str
    max_quantity_per_session: decimal
    min_quantity_per_session: decimal
    avg_quantity_per_session: decimal
    progress: decimal
    first_workout: date
    last_workout: date

    def __str__(self) -> str:
        return (f'📌\n'
                f'Цель по тренировке: {self.target_exercise}\n'
                f'Период цели: с {self.start_date} — по {self.end_date}\n'
                f'План цели: {self.target_quantity}\n'
                f'Ед. измерения: {self.unit}\n'
                f'Выполнено: {self.total_quantity}\n'
                f'Прогресс: {self.progress:.1f}%\n'
                f'Всего тренировок: {self.workout_sessions_count}\n'
                f'за тренировку:\n'
                f'- максимум: {self.max_quantity_per_session}\n'
                f'- минимум: {self.min_quantity_per_session}\n'
                f'- среднее: {self.avg_quantity_per_session}\n'
                f'Первая тренировка: {self.first_workout}\n'
                f'Последняя тренировка: {self.last_workout}\n\n')


@dataclass
class WorkoutWithoutGoal:
    register_user_id: int
    target_exercise: str
    unit: str
    workout_sessions_count: int
    max_quantity_per_session: decimal
    min_quantity_per_session: decimal
    avg_quantity_per_session: decimal
    first_workout: date
    last_workout: date

    def __str__(self) -> str:
        return (f'📌\n'
                f'Тренировки: {self.target_exercise}\n'
                f'Ед. измерения: {self.unit}\n'
                f'Всего тренировок: {self.workout_sessions_count}\n'
                f'за тренировку:\n'
                f'- максимум: {self.max_quantity_per_session}\n'
                f'- минимум: {self.min_quantity_per_session}\n'
                f'- среднее: {self.avg_quantity_per_session}\n'
                f'Первая тренировка: {self.first_workout}\n'
                f'Последняя тренировка: {self.last_workout}\n\n')
