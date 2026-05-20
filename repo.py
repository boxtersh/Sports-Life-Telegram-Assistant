import aiomysql
from typing import Optional

from constants import DatabaseQueries
from config import settings

query_ = DatabaseQueries()


class Repo:
    def __init__(self, object_queries: DatabaseQueries) -> None:
        self.pool: Optional[aiomysql.Pool] = None
        self.query = object_queries

    async def open(self) -> None:
        if self.pool is None:
            self.pool = await aiomysql.create_pool(
                host=settings.HOST,
                user=settings.USER,
                password=settings.PASSWORD,
                db=settings.DATABASE,
                port=settings.PORT,
                autocommit=True,
                cursorclass=aiomysql.DictCursor,
                minsize=1,
                maxsize=10,
            )

    async def close(self) -> None:
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            self.pool = None

    async def create_table_in_db(self) -> None:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.CREATE_TABLE
                generator_query = (query.strip() for query in query.split(';'))
                for query in generator_query:
                    if query:
                        await cur.execute(query)

    async def login_exists(self, login) -> None | dict:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.GET_LOGIN
                await cur.execute(query, [login])
                res = await cur.fetchone()
                return res

    async def is_login_exists_by_id(self, user_id, login) -> None | dict:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.GET_LOGIN_BY_ID
                await cur.execute(query, [user_id, login])
                res = await cur.fetchone()
                return res

    async def user_id_exists(self, user_id) -> None | dict:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.GET_USER_ID
                await cur.execute(query, [user_id])
                res = await cur.fetchone()
                return res

    async def get_auth_status_user_id(self, user_id) -> None | dict:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.GET_AUTH_STATUS
                await cur.execute(query, [user_id])
                res = await cur.fetchone()
                return res

    async def get_stored(self, user_id, login) -> None | dict:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.GET_STORED
                await cur.execute(query, [user_id, login])
                res = await cur.fetchone()
                return res

    async def add_user(self, user_id, username, stored) -> None:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.REGISTER_USER
                await cur.execute(query, [user_id, username, stored])

    async def add_workout(self, workout_obj) -> None:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.ADD_WORKOUT
                await cur.execute(query, [
                    workout_obj.workout_date,
                    workout_obj.exercise_type,
                    workout_obj.quantity,
                    workout_obj.unit,
                    workout_obj.goal_id,
                    workout_obj.register_user_id])

    async def authorization(self, login) -> None:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.AUTHORIZATION
                await cur.execute(query, [login])

    async def less_6_hours(self, user_id) -> None | bool:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.LESS_6_HOURS
                await cur.execute(query, [user_id])
                res = await cur.fetchone()
                return res

    async def deactivation(self, user_id) -> None:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.DEACTIVATION
                await cur.execute(query, [user_id])

    async def get_goals(self, user_id, status) -> None | list:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.GET_GOALS
                await cur.execute(query, [user_id, status])
                res = await cur.fetchall()
                return res

    async def add_goal(self, goal_model):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.ADD_GOAL
                await cur.execute(query, [
                    goal_model.start_date,
                    goal_model.end_date,
                    goal_model.target_exercise,
                    goal_model.target_quantity,
                    goal_model.unit,
                    goal_model.register_user_id
                ])

    async def changing_status_to_expired(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.CHANGING_STATUS_TO_EXPIRED
                await cur.execute(query, [])

    async def changing_status_to_achieved(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.CHANGING_STATUS_TO_ACHIEVED
                await cur.execute(query, [])

    async def get_by_user_id_by_status_goals_today(self, user_id, status) -> None | list:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.GET_BY_USER_ID_BY_STATUS_GOALS_TODAY
                await cur.execute(query, [user_id, status])
                res = await cur.fetchall()
                return res

    async def get_all_users_expired_goals(self) -> None | list:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.GET_ALL_USERS_EXPIRED_GOALS
                await cur.execute(query, [])
                res = await cur.fetchall()
                return res

    async def get_all_users_achieved_goals(self) -> None | list:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.GET_ALL_USERS_ACHIEVED_GOALS
                await cur.execute(query, [])
                res = await cur.fetchall()
                return res

    async def get_date_start_end_target_goal(self, user_id, id_goal) -> None | dict:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.GET_DATE_START_END_TARGET_GOAL
                await cur.execute(query, [user_id, id_goal])
                res = await cur.fetchone()
                return res

    async def get_progress_by_user_id_id_goal(self, user_id, id_goal) -> None | dict:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.GET_PROGRESS_BY_USER_ID_ID_GOAL
                await cur.execute(query, [user_id, id_goal])
                res = await cur.fetchone()
                return res

    async def changing_status_by_register_user_id_id_goal(self, status, user_id, id_goal):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.CHANGING_STATUS_BY_REGISTER_USER_ID_ID_GOAL
                await cur.execute(query, [status, user_id, id_goal])

    async def view_workouts_filter(self, user_id, target_exercise=None) -> None | list:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.VIEW_WORKOUTS_FILTER
                await cur.execute(query, [user_id, target_exercise, target_exercise])
                res = await cur.fetchall()
                return res

    async def view_workout_detail(self, user_id, exercise_type, goal_id=None) -> None | list:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.VIEW_WORKOUT_DETAIL
                await cur.execute(query, [user_id, exercise_type, goal_id])
                res = await cur.fetchall()
                return res

    async def verification_goal_is_expired(self, user_id: int) -> None | list:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.VERIFICATION_GOAL_IS_EXPIRED
                await cur.execute(query, [user_id])
                res = await cur.fetchall()
                return res

    async def workouts_no_goal_export_json(self, user_id: int) -> None | list:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.WORKOUTS_NO_GOAL_EXPORT_JSON
                await cur.execute(query, [user_id])
                res = await cur.fetchall()
                return res

    async def workouts_goal_export_json(self, user_id: int) -> None | list:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.WORKOUTS_GOAL_EXPORT_JSON
                await cur.execute(query, [user_id])
                res = await cur.fetchall()
                return res

    async def goal_export_json(self, user_id: int) -> None | list:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.GOAL_EXPORT_JSON
                await cur.execute(query, [user_id])
                res = await cur.fetchall()
                return res

    async def get_all_goals(self, user_id: int) -> None | list:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.GET_All_GOALS
                await cur.execute(query, [user_id])
                res = await cur.fetchall()
                return res

    async def archived_status(self, user_id: int):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = self.query.ARCHIVED_STATUS
                await cur.execute(query, [user_id])