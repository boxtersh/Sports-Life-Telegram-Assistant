import json
import os

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from fsm_storage import FormStates

from business_logic import crud_logic
from services import crud_db
from keyboards import keyboards as kyb
from models.models import Workout, InfoGoal, WorkoutWithoutGoal

router = Router()


@router.message(Command('add_workout'))
async def add_workout(message: types.Message, user_id, object_info_user, state: FSMContext, f_state: FormStates, dbase):
    result = await crud_db.verification_goal_is_expired(dbase, user_id)
    if not result.success:
        await message.answer(object_info_user.ERROR_DATABASE, result.error)
        await state.clear()
        return
    if result.value:
        all_model_expired = '\n'.join(str(InfoGoal(**crud_logic.replace_none_attributes(object_attributes)))
                                      for object_attributes in result.value)
        await message.answer(f'{object_info_user.LIST_GOAL_EXPIRED}\n'
                             f'{all_model_expired}'
                             f'{object_info_user.EXPIRED_COMMENT}')
        result = await crud_db.changing_status_to_expired(dbase)
        if not result.success:
            await message.answer(object_info_user.ERROR_DATABASE, result.error)
            await state.clear()
            return

    result = await crud_db.get_by_user_id_by_status_goals_today(dbase, user_id,
                                                                object_info_user.STATUS_GOAL[
                                                                    object_info_user.STATUS_ACTIVE])
    response = object_info_user.WORKOUT_DATA_INPUT
    await state.set_state(f_state.workout_model)
    if not result.success:
        await message.answer(object_info_user.ERROR_DATABASE, result.error)
        return None
    if not result.value:
        response = f'{response}\n\n{object_info_user.NOT_ACTIVE_GOALS}'
        await message.answer(response)
        return None
    await message.answer(object_info_user.ACTIVE_GOALS,
                         reply_markup=kyb.btn_add_workout_goal(object_info_user.BTN_YES_FOR_GOAL,
                                                               object_info_user.BTN_NO))
    await state.set_state(f_state.kyb_btn_yes_no)
    return None


@router.callback_query(FormStates.kyb_btn_yes_no)
async def add_workout_goal(callback: types.CallbackQuery, message_text, user_id, object_info_user, state: FSMContext,
                           f_state: FormStates, dbase):
    await state.clear()
    if message_text == 'yes_for_goal':
        result = await crud_db.get_by_user_id_by_status_goals_today(dbase,
                                                                    user_id, object_info_user.STATUS_GOAL[
                                                                        object_info_user.STATUS_ACTIVE])
        if not result.success:
            await callback.message.answer(object_info_user.ERROR_DATABASE, result.error)
            return
        if not result.value:
            await callback.message.answer(f'{object_info_user.ERROR_REPEAT_DATA}\n{object_info_user.NOT_GOAL}')
            await state.clear()
            return
        await callback.message.answer(object_info_user.SHOW_ACTIVE_GOAL)
        dict_number_goals = crud_logic.get_dict_active_goal(result.value)
        for key, goal in dict_number_goals.items():
            await callback.message.answer(f'Номер цели:{key}\n{goal}')
        str_number_goals = ','.join(dict_number_goals)
        await state.update_data(dict_number_goals=dict_number_goals, str_number_goals=str_number_goals)
        await callback.message.answer(text=object_info_user.SELECT_GOAL,
                                      reply_markup=kyb.btn_select_number_goal(str_number_goals))
        await state.set_state(f_state.select_goal)

    else:
        await callback.message.answer(object_info_user.WORKOUT_DATA_INPUT)
        await state.set_state(f_state.workout_model)
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)


@router.message(F.text, FormStates.workout_model)
async def workout_model(message: types.Message, user_id, object_info_user, state: FSMContext, f_state: FormStates,
                        dbase):
    if message.text == '/add_goal':
        await state.clear()
        await message.answer(object_info_user.ADD_GOAL)
        await state.set_state(f_state.goal_model)
        return
    workout = message.text.strip().lower().split()
    if not (3 <= len(workout) <= 4):
        await message.answer(object_info_user.INVALID_FORMAT_DATA)
        return
    if len(workout) == 4:
        attribute_model = dict(zip(object_info_user.WORKOUT_FULL, workout))
    else:
        attribute_model = dict(zip(object_info_user.WORKOUT_SHORT, workout))
    error_set = crud_logic.workout_model_verification(attribute_model, object_info_user)
    if error_set:
        await message.answer(f'{object_info_user.ERROR_REPEAT_DATA}\n{'\n'.join(err for err in error_set)}')
        return
    workout_model_ = crud_logic.create_workout_model(attribute_model, user_id)
    result = await crud_db.add_workout(dbase, workout_model_)
    if not result.success:
        await message.answer(object_info_user.ERROR_DATABASE, result.error)
        return
    await message.answer(f'{workout_model_}\n{object_info_user.WORKOUT_SUCCESS}')
    await state.clear()


@router.message(Command('add_goal'))
async def add_goal(message: types.Message, object_info_user, state: FSMContext, f_state: FormStates):
    await message.answer(object_info_user.ADD_GOAL)
    await state.set_state(f_state.goal_model)


@router.message(F.text, FormStates.goal_model)
async def goal_model(message: types.Message, user_id, object_info_user, state: FSMContext, dbase):
    goal = message.text.strip().lower().split()
    if not (4 <= len(goal) <= 5):
        await message.answer(object_info_user.INVALID_FORMAT_DATA)
        return
    if len(goal) == 4:
        attribute_model = dict(zip(object_info_user.GOAL_SHORT, goal))
    else:
        attribute_model = dict(zip(object_info_user.GOAL_FULL, goal))
    error_set = crud_logic.goal_model_verification(attribute_model, object_info_user)
    if error_set:
        response = '\n'.join(err_str for err_str in error_set)
        await message.answer(f'{object_info_user.ERROR_REPEAT_DATA}\n{response}')
        return
    goal_model = crud_logic.create_goal_model(attribute_model, user_id)
    result = await crud_db.add_goal(dbase, goal_model)
    if not result.success:
        await message.answer(object_info_user.ERROR_DATABASE, result.error)
        return
    await message.answer(f'{goal_model}\n{object_info_user.GOAL_SUCCESS}')
    await state.clear()


@router.callback_query(FormStates.select_goal)
async def select_goal(callback: types.CallbackQuery, user_id, object_info_user, dbase, state: FSMContext,
                      message_text, f_state: FormStates):
    dict_state = await state.get_data()
    model_info = dict_state['dict_number_goals'][message_text]
    await state.clear()
    goal_id = model_info.id_goal
    await state.update_data(model_info=model_info)
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f'{object_info_user.USER_SELECTED_GOAL}{message_text}')
    await callback.message.answer(object_info_user.ADD_WORKOUT_FOR_GOAL)
    await state.set_state(f_state.workout_for_goal)


@router.message(F.text, FormStates.workout_for_goal)
async def workout_for_goal(message: types.Message, user_id, object_info_user, state: FSMContext, dbase,
                           f_state: FormStates):
    dict_state = await state.get_data()
    model_info = dict_state['model_info']
    id_goal = model_info.id_goal
    workout = message.text.strip().lower().split()
    if not (1 <= len(workout) <= 2):
        await message.answer(object_info_user.INVALID_FORMAT_DATA)
        return
    if len(workout) == 1:
        attribute_model = dict(zip(object_info_user.WORKOUT_FOR_GOAL_SHORT, workout))
    else:
        attribute_model = dict(zip(object_info_user.WORKOUT_FOR_GOAL_FULL, workout))
    error_set = crud_logic.workout_model_for_goal_verification(attribute_model, model_info, object_info_user)
    if error_set:
        mistake = '\n'.join(err for err in error_set)
        await message.answer(f'{object_info_user.INVALID_FORMAT_DATA}\n{mistake}')
        return
    workout_model_ = crud_logic.create_workout_model_for_goal(user_id, model_info, attribute_model)
    result = await crud_db.add_workout(dbase, workout_model_)
    if not result.success:
        await message.answer(object_info_user.ERROR_DATABASE, result.error)
        await state.clear()
        return
    await message.answer(f'{workout_model_}\n{object_info_user.WORKOUT_SUCCESS}')
    result = await crud_db.get_progress_by_user_id_id_goal(dbase, user_id, id_goal)
    if not result.success:
        await message.answer(object_info_user.ERROR_DATABASE, result.error)
        await state.clear()
        return
    success, goal_full_info = crud_logic.checking_progress_goal(result.value)
    if success:
        await message.answer(f'{object_info_user.LIST_GOAL_ACHIEVED}\n'
                             f'{goal_full_info}'
                             f'{object_info_user.ACHIEVED_COMMENT}\n')
        await crud_db.changing_status_by_register_user_id_id_goal(dbase,
                                                                  object_info_user.STATUS_GOAL[
                                                                      object_info_user.STATUS_ACHIEVED], user_id,
                                                                  id_goal)
        if not result.success:
            await message.answer(object_info_user.ERROR_DATABASE, result.error)
            await state.clear()
            return

        await state.clear()
        return
    await state.clear()


@router.message(Command('view_workouts_group'))
async def view_workouts(message: types.Message, user_id, dbase, object_info_user, state: FSMContext,
                        f_state: FormStates):
    result = await crud_db.view_workouts_filter(dbase, user_id)
    if not result.success:
        await message.answer(object_info_user.ERROR_DATABASE, result.error)
        return
    if not result.value:
        await message.answer(object_info_user.NOT_VIEW_WORKOUTS_ALL)
        return
    workout_without_goal = f'\n'.join(str(WorkoutWithoutGoal(**atr_dict)) for atr_dict in result.value)
    await message.answer(f'{object_info_user.YES_VIEW_WORKOUTS_ALL}\n{workout_without_goal}')


@router.message(Command('view_workout_detail'))
async def view_number_workout(message: types.Message, user_id, dbase, object_info_user, state: FSMContext,
                              f_state: FormStates):
    result = await crud_db.view_workouts_filter(dbase, user_id)
    if not result.success:
        await message.answer(object_info_user.ERROR_DATABASE, result.error)
        return
    if not result.value:
        await message.answer(object_info_user.NOT_VIEW_WORKOUTS_ALL)
        return
    dict_name_workout = {}
    all_workouts = 'Список ваших тренировок:\n'
    for ind, atr_workout in enumerate(result.value, start=1):
        dict_name_workout[str(ind)] = atr_workout['target_exercise']
        current_string = f"{ind}. тренировка: {atr_workout['target_exercise']}\n"
        all_workouts += current_string
    await message.answer(f'{all_workouts}\n{object_info_user.NUMBER_WORKOUT}')
    await state.update_data(dict_name_workout=dict_name_workout)
    await state.set_state(f_state.view_number_workout)


@router.message(F.text, FormStates.view_number_workout)
async def view_number_workout_select(message: types.Message, user_id, dbase, object_info_user, state: FSMContext,
                                     f_state: FormStates):
    number = message.text.strip()
    dict_state = await state.get_data()
    dict_name_workout = dict_state['dict_name_workout']
    workout = dict_name_workout.get(number)
    if workout is None:
        await message.answer(object_info_user.IS_NO_SPECIFIED_WORKOUT)
        return
    group_result = await crud_db.view_workouts_filter(dbase, user_id, target_exercise=workout)
    if not group_result.success:
        await message.answer(object_info_user.ERROR_DATABASE, group_result.error)
        return
    if not group_result.value:
        await message.answer(object_info_user.NOT_VIEW_WORKOUTS_ALL)
        return
    result = await crud_db.view_workout_detail(dbase, user_id, target_exercise=workout)
    if not result.success:
        await message.answer(object_info_user.ERROR_DATABASE, result.error)
        return
    if not result.value:
        await message.answer(object_info_user.NOT_VIEW_WORKOUTS_ALL)
        return
    group_workout = '\n'.join(str(WorkoutWithoutGoal(**atr_dict)) for atr_dict in group_result.value)
    workout_model_ = '\n'.join(str(Workout(**atr_dict)) for atr_dict in result.value)
    await message.answer(f'{group_workout}\n{workout_model_}')
    await state.clear()
    return


@router.message(Command('workouts_no_goal_export_json'))
async def workouts_no_goal_export_json(message: types.Message, user_id, dbase, object_info_user):
    workouts_data = await crud_db.workouts_no_goal_export_json(dbase, user_id)
    if not workouts_data.success:
        await message.answer(object_info_user.ERROR_DATABASE, workouts_data.error)
        return
    if not workouts_data.value:
        await message.answer(object_info_user.NOT_VIEW_WORKOUTS_ALL)
        return
    crud_logic.workout_data_serializable(workouts_data.value)
    json_data = json.dumps(workouts_data.value, ensure_ascii=False, indent=2)
    file_temp = f"workouts_{user_id}.json"
    with open(file_temp, 'w', encoding='utf-8') as f:
        f.write(json_data)
    try:
        await message.answer_document(
            document=types.BufferedInputFile(
                file=open(file_temp, 'rb').read(),
                filename=file_temp
            ),
            caption=object_info_user.EXPORT_DATA_WORKOUTS
        )
    finally:
        if os.path.exists(file_temp):
            os.remove(file_temp)


@router.message(Command('workouts_goal_export_json'))
async def workouts_goal_export_json(message: types.Message, dbase, object_info_user):
    user_id = message.from_user.id
    goal_data = await crud_db.goal_export_json(dbase, user_id)
    workouts_data = await crud_db.workouts_goal_export_json(dbase, user_id)
    if not (workouts_data.success and goal_data.success):
        await message.answer(f'{object_info_user.ERROR_DATABASE},\n'
                             f'{object_info_user.QUERY_GOAL}{goal_data.error}'
                             f'{object_info_user.QUERY_WORKOUTS}{workouts_data.error}\n')
        return
    if not goal_data.value:
        await message.answer(object_info_user.NOT_GOAL_ALL)
        return
    crud_logic.goal_data_serializable(goal_data.value)
    json_goal = json.dumps(goal_data.value, ensure_ascii=False, indent=2)
    file_temp_goal = f'goal_{user_id}.json'
    with open(file_temp_goal, 'w', encoding='utf-8') as f:
        f.write(json_goal)
    if workouts_data.value:
        crud_logic.workout_data_serializable(workouts_data.value)
        json_workouts = json.dumps(workouts_data.value, ensure_ascii=False, indent=2)
        file_temp_workouts = f"workouts_{user_id}.json"
        with open(file_temp_workouts, 'w', encoding='utf-8') as f:
            f.write(json_workouts)
        try:
            await message.answer_document(
                document=types.BufferedInputFile(
                    file=open(file_temp_goal, 'rb').read(),
                    filename=file_temp_goal
                ),
                caption=object_info_user.EXPORT_DATA_GOALS
            )
            await message.answer_document(
                document=types.BufferedInputFile(
                    file=open(file_temp_workouts, 'rb').read(),
                    filename=file_temp_workouts
                ),
                caption=object_info_user.EXPORT_DATA_WORKOUTS
            )
        finally:
            for file_path in [file_temp_goal, file_temp_workouts]:
                if os.path.exists(file_path):
                    os.remove(file_path)
    else:
        with open(file_temp_goal, 'w', encoding='utf-8') as f:
            f.write(json_goal)
        try:
            await message.answer_document(
                document=types.BufferedInputFile(
                    file=open(file_temp_goal, 'rb').read(),
                    filename=file_temp_goal
                ),
                caption=object_info_user.EXPORT_DATA_GOALS
            )
            await message.answer(object_info_user.NOT_GOAL_WORKOUTS_ALL)
        finally:
            if os.path.exists(file_temp_goal):
                os.remove(file_temp_goal)


@router.message(Command('view_goals'))
async def view_workouts(message: types.Message, user_id, dbase, object_info_user, state: FSMContext,
                        f_state: FormStates):
    result = await crud_db.get_all_goals(dbase, user_id)
    if not result.success:
        await message.answer(object_info_user.ERROR_DATABASE, result.error)
        return
    if not result.value:
        await message.answer(object_info_user.NOT_GOAL)
        return
    str_goals, numbering_of_goal = crud_logic.create_goal_model_id_goal(result.value, object_info_user)
    await message.answer(f'{object_info_user.YES_VIEW_GOAL_ALL}\n{str_goals}')
    await message.answer(object_info_user.NUMBER_STATUS_GOAL)
    await state.set_state(f_state.numbering_of_goal)
    await state.update_data(numbering_of_goal=numbering_of_goal)
    return


@router.message(F.text, FormStates.numbering_of_goal)
async def numbering_of_goal_(message: types.Message, user_id, dbase, object_info_user, state: FSMContext,
                             f_state: FormStates):
    number = message.text.strip()
    dict_state = await state.get_data()
    numbering_of_goal = dict_state.get('numbering_of_goal')
    goal_model_ = numbering_of_goal.get(number)
    if goal_model_ is None:
        await message.answer(object_info_user.IS_NO_SPECIFIED_GOAL)
        return
    result = await crud_db.get_progress_by_user_id_id_goal(dbase, user_id, goal_model_.id_goal)
    if not result.success:
        await message.answer(object_info_user.ERROR_DATABASE, result.error)
        return
    if not result.value:
        await message.answer(object_info_user.NOT_GOAL)
        return
    info_goal_model = crud_logic.create_info_goal_model(result.value)
    result = await crud_db.view_workout_detail(dbase, user_id, goal_model_.target_exercise, goal_model_.id_goal)
    if not result.success:
        await message.answer(object_info_user.ERROR_DATABASE, result.error)
        return
    if not result.value:
        await message.answer(object_info_user.NOT_VIEW_WORKOUTS_ALL)
        return
    workout_model_ = '\n'.join(str(Workout(**atr_dict)) for atr_dict in result.value)
    await message.answer(f'{object_info_user.YES_VIEW_GOAL_WORKOUTS_ALL}\n'
                         f'{info_goal_model}\n'
                         f'{workout_model_}')
    await state.clear()
    return


@router.message(Command('reminder_off_achieved'))
async def reminder_off_achieved(message: types.Message, user_id, dbase, object_info_user, state: FSMContext):
    result = await crud_db.archived_status(dbase, user_id)
    if not result.success:
        await message.answer(object_info_user.ERROR_DATABASE, result.error)
        return
    await message.answer(object_info_user.REMINDER_OFF_ACHIEVED)
    return