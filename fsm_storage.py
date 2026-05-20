from aiogram.fsm.state import State, StatesGroup


class FormStates(StatesGroup):
    register_login = State()
    register_password = State()
    login_login = State()
    login_password = State()
    workout_model = State()
    goal_model = State()
    workout_for_goal = State()
    select_goal = State()
    add_workout_goal = State()
    kyb_btn_yes_no = State()
    view_number_workout = State()
    numbering_of_goal = State()