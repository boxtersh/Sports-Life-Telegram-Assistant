class DatabaseQueries:

    CREATE_TABLE = '''
SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Table `seschool_01_RP12_TYA`.`register_user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `register_user` (
  `id` INT UNSIGNED UNIQUE NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT UNSIGNED UNIQUE NOT NULL,
  `login` VARCHAR(19) UNIQUE NOT NULL,
  `password` CHAR(81) NOT NULL,
  `auth_status` TINYINT(1) UNSIGNED NOT NULL DEFAULT 0,
  `time_start_auth` DATETIME NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;
-- -----------------------------------------------------
-- Table `seschool_01_RP12_TYA`.`workouts`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `workouts` (
    `id_workout` INT UNSIGNED UNIQUE NOT NULL AUTO_INCREMENT,
    `workout_date` DATE NOT NULL,
    `exercise_type` VARCHAR(50) NOT NULL,
    `quantity` DECIMAL(10,2) NOT NULL,
    `unit` VARCHAR(20) NOT NULL,
    `goal_id` INT UNSIGNED NULL,
    `register_user_id` BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (`id_workout`),
    INDEX `fk_workouts_user_id_idx` (`register_user_id` ASC),
    CONSTRAINT `fk_workouts_user_id`
        FOREIGN KEY (`register_user_id`)
        REFERENCES `register_user` (`user_id`)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION)
ENGINE = InnoDB;
-- -----------------------------------------------------
-- Table `seschool_01_RP12_TYA`.`goals`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `goals` (
    `id_goal` INT UNSIGNED UNIQUE NOT NULL AUTO_INCREMENT,
    `start_date` DATE NOT NULL,
    `end_date` DATE NOT NULL,
    `target_exercise` VARCHAR(50) NOT NULL,
    `target_quantity` DECIMAL(10,2) NOT NULL,
    `unit` VARCHAR(20) NOT NULL,
    `status` ENUM('active', 'achieved', 'expired', 'archive_expired', 'archive_achieved') DEFAULT 'active',
    `register_user_id` BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (`id_goal`),
    INDEX `fk_goals_user_id_idx` (`register_user_id` ASC),
    CONSTRAINT `fk_goals_register_user_user_id`
        FOREIGN KEY (`register_user_id`)
        REFERENCES `register_user` (`user_id`)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION)
ENGINE = InnoDB;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
'''
    GET_USER_ID = 'SELECT user_id FROM register_user WHERE user_id = %s'
    GET_LOGIN = 'SELECT login FROM register_user WHERE login = %s'
    GET_LOGIN_BY_ID = 'SELECT login FROM register_user WHERE user_id = %s AND `login` = %s'
    GET_AUTH_STATUS = 'SELECT auth_status FROM register_user WHERE user_id = %s'
    GET_STORED = 'SELECT password FROM register_user WHERE user_id = %s AND login = %s'
    REGISTER_USER = 'INSERT INTO register_user (user_id, login, password) VALUES (%s, %s, %s)'
    AUTHORIZATION = 'UPDATE `register_user` SET `auth_status` = 1, `time_start_auth` = NOW() WHERE `login` = %s'
    LESS_6_HOURS= 'SELECT login FROM `register_user` WHERE ADDTIME(`time_start_auth`, "6:00:00") >= NOW() AND `user_id` = %s'
    DEACTIVATION = 'UPDATE `register_user` SET `auth_status` = 0 WHERE `user_id` = %s'

    ADD_WORKOUT = '''INSERT INTO workouts (workout_date, exercise_type, quantity, unit, goal_id, register_user_id) 
    VALUES (%s, %s, %s, %s, %s, %s)
    '''
    GET_GOALS = 'SELECT * FROM goals WHERE register_user_id = %s AND status = %s'
    GET_All_GOALS = 'SELECT * FROM goals WHERE register_user_id = %s'
    GET_DATE_START_END_TARGET_GOAL = '''SELECT start_date, end_date, target_exercise FROM goals '
    'WHERE register_user_id = %s AND id_goal = %s
    '''
    ADD_GOAL = '''INSERT INTO `goals` (`start_date`, `end_date`, `target_exercise`, `target_quantity`, `unit`,
    `register_user_id`) VALUES (%s, %s, %s, %s, %s, %s)
    '''
    GET_BY_USER_ID_BY_STATUS_GOALS_TODAY = '''SELECT g.register_user_id, g.target_exercise, g.id_goal, g.target_quantity,
    g.start_date, g.end_date, COUNT(w.id_workout) AS workout_sessions_count, COALESCE(SUM(w.quantity), 0) AS total_quantity,
    g.unit, COALESCE(MAX(w.quantity), 0) AS max_quantity_per_session, COALESCE(MIN(w.quantity), 0) AS min_quantity_per_session,
    COALESCE(AVG(w.quantity), 0) AS avg_quantity_per_session, CASE WHEN g.target_quantity > 0
    THEN COALESCE(SUM(w.quantity), 0) * 100.0 / g.target_quantity ELSE 0 END AS progress, MIN(w.workout_date) AS first_workout,
    MAX(w.workout_date) AS last_workout FROM goals g LEFT JOIN workouts w ON g.id_goal = w.goal_id
    AND w.exercise_type = g.target_exercise WHERE g.register_user_id = %s AND g.status = %s AND g.start_date <= CURDATE()
    GROUP BY g.register_user_id, g.target_exercise, g.id_goal, g.target_quantity, g.start_date, g.end_date, g.unit;
    '''
    CHANGING_STATUS_TO_EXPIRED = """UPDATE `goals` SET `status` = 'expired' WHERE `end_date` < CURDATE()
    AND `status` != 'expired'"""
    CHANGING_STATUS_TO_ACHIEVED = '''UPDATE `goals` AS g SET g.`status` = 'achieved' WHERE g.`status` = 'active' 
    AND (SELECT COALESCE(SUM(w.`quantity`), 0) FROM `workouts` AS w WHERE w.`goal_id` = g.`id_goal`) >= g.`target_quantity`
    '''
    GET_ALL_USERS_EXPIRED_GOALS = '''SELECT g.register_user_id, g.target_exercise, g.id_goal, g.target_quantity, g.unit, 
    g.start_date, g.end_date, COUNT(w.id_workout) AS workout_sessions_count, COALESCE(SUM(w.quantity), 0) AS total_quantity,
    COALESCE(AVG(w.quantity), 0) AS avg_quantity_per_session, COALESCE(MAX(w.quantity), 0) AS max_quantity_per_session,
    COALESCE(MIN(w.quantity), 0) AS min_quantity_per_session, ROUND(CASE WHEN g.target_quantity = 0 THEN 0
    ELSE COALESCE(SUM(w.quantity), 0) * 100.0 / g.target_quantity END, 2 ) AS progress, MIN(w.workout_date) AS first_workout,
    MAX(w.workout_date) AS last_workout FROM goals g LEFT JOIN workouts w ON g.id_goal = w.goal_id WHERE g.status = 'expired'
    GROUP BY g.register_user_id, g.target_exercise, g.id_goal, g.target_quantity, g.unit, g.start_date, g.end_date
    ORDER BY g.register_user_id, g.id_goal
    '''
    GET_ALL_USERS_ACHIEVED_GOALS = '''SELECT g.register_user_id, g.target_exercise, g.id_goal, g.target_quantity, g.unit,
    g.start_date, g.end_date, COUNT(w.id_workout) AS workout_sessions_count, COALESCE(SUM(w.quantity), 0) AS total_quantity,
    COALESCE(MAX(w.quantity), 0) AS max_quantity_per_session, COALESCE(MIN(w.quantity), 0) AS min_quantity_per_session,
    COALESCE(AVG(w.quantity), 0) AS avg_quantity_per_session, ROUND(COALESCE(SUM(w.quantity), 0) * 100.0 / g.target_quantity, 
    2) AS progress,
    MIN(w.workout_date) AS first_workout, MAX(w.workout_date) AS last_workout FROM goals AS g LEFT JOIN workouts AS w
    ON g.id_goal = w.goal_id AND w.workout_date BETWEEN g.start_date AND g.end_date AND w.register_user_id = g.register_user_id
    WHERE g.status = 'achieved' GROUP BY g.register_user_id, g.target_exercise, g.id_goal, g.target_quantity, g.unit,
    g.start_date, g.end_date ORDER BY g.id_goal
    '''
    GET_PROGRESS_BY_USER_ID_ID_GOAL = '''SELECT g.register_user_id, g.target_exercise, g.id_goal, g.target_quantity,
    g.unit, g.start_date, g.end_date, COUNT(w.id_workout) AS workout_sessions_count, COALESCE(SUM(w.quantity), 0) 
    AS total_quantity, COALESCE(MAX(w.quantity), 0) AS max_quantity_per_session, COALESCE(MIN(w.quantity), 0) 
    AS min_quantity_per_session, COALESCE(AVG(w.quantity), 0) AS avg_quantity_per_session, ROUND( CASE
    WHEN g.target_quantity > 0 THEN COALESCE(SUM(w.quantity), 0) / g.target_quantity * 100 ELSE 0 END, 2) AS progress,
    MIN(w.workout_date) AS first_workout, MAX(w.workout_date) AS last_workout FROM goals g LEFT JOIN workouts w 
    ON g.id_goal = w.goal_id WHERE g.register_user_id = %s AND g.id_goal = %s GROUP BY g.register_user_id,
    g.target_exercise, g.id_goal, g.target_quantity, g.unit, g.start_date, g.end_date
    ORDER BY g.register_user_id, g.id_goal
    '''
    CHANGING_STATUS_BY_REGISTER_USER_ID_ID_GOAL  = '''
    UPDATE `goals` SET `status` = %s WHERE `register_user_id` = %s AND `id_goal` = %s
    '''
    VIEW_WORKOUTS_FILTER = '''SELECT w.register_user_id, w.exercise_type AS target_exercise, w.unit,
    COUNT(*) AS workout_sessions_count, MAX(w.quantity) AS max_quantity_per_session, MIN(w.quantity) 
    AS min_quantity_per_session, AVG(w.quantity) AS avg_quantity_per_session, MIN(w.workout_date) AS first_workout,
    MAX(w.workout_date) AS last_workout FROM workouts w WHERE w.register_user_id = %s
    AND w.goal_id IS NULL AND (%s IS NULL OR w.exercise_type = %s)
    GROUP BY w.exercise_type, w.unit, w.register_user_id ORDER BY w.exercise_type
    '''
    VIEW_WORKOUT_DETAIL = '''SELECT w.workout_date, w.exercise_type, w.quantity, w.unit, w.goal_id, w.register_user_id
    FROM workouts w WHERE w.register_user_id = %s AND w.exercise_type = %s AND COALESCE(w.goal_id, -1) = COALESCE(%s, -1)
    ORDER BY w.workout_date DESC
    '''
    VERIFICATION_GOAL_IS_EXPIRED = '''SELECT g.register_user_id, g.target_exercise, g.id_goal, g.target_quantity,
    g.start_date, g.end_date, COUNT(w.id_workout) AS workout_sessions_count, COALESCE(SUM(w.quantity), 0) 
    AS total_quantity, g.unit, COALESCE(MAX(w.quantity), 0) AS max_quantity_per_session, COALESCE(MIN(w.quantity), 0) 
    AS min_quantity_per_session, COALESCE(AVG(w.quantity), 0) AS avg_quantity_per_session, CASE WHEN 
    g.target_quantity > 0 THEN COALESCE(SUM(w.quantity), 0) * 100.0 / g.target_quantity ELSE 0 END AS progress,
    MIN(w.workout_date) AS first_workout, MAX(w.workout_date) AS last_workout FROM goals g LEFT JOIN workouts w ON
    g.target_exercise = w.exercise_type AND w.workout_date BETWEEN g.start_date AND g.end_date AND 
    g.register_user_id = w.register_user_id WHERE g.register_user_id = %s AND g.status = 'active' 
    AND g.end_date < CURDATE() GROUP BY
    g.register_user_id, g.target_exercise, g.id_goal, g.target_quantity, g.start_date, g.end_date,
    g.unit ORDER BY g.id_goal
    '''
    WORKOUTS_NO_GOAL_EXPORT_JSON = '''SELECT workout_date, exercise_type, quantity ,unit FROM `workouts` 
    WHERE `register_user_id` = %s AND `goal_id` IS NULL ORDER BY exercise_type
    '''
    WORKOUTS_GOAL_EXPORT_JSON = '''SELECT goal_id, workout_date, exercise_type, quantity, unit FROM `workouts` 
        WHERE `register_user_id` = %s AND `goal_id` IS NOT NULL ORDER BY exercise_type
        '''
    GOAL_EXPORT_JSON = '''SELECT `id_goal`, `start_date`, `end_date`, `target_exercise`, `target_quantity`, `unit`, 
    `status` FROM `goals` WHERE `register_user_id` = %s ORDER BY id_goal
    '''
    ARCHIVED_STATUS = ''' UPDATE goals SET status = CASE WHEN status = 'achieved' THEN 'archive_achieved'
    WHEN status = 'expired' THEN 'archive_expired' ELSE status END WHERE status IN ('achieved', 'expired')
    AND register_user_id = %s;
    '''


class InfoForUser:
    # ПРЕДУПРЕЖДЕНИЯ И УВЕДОМЛЕНИЯ
    START = ('🚀 Здравствуйте уважаемый пользователь я Telegram-бот, который поможет вам фиксировать вашу спортивную '
             'активность, отслеживать динамику тренировок и прогресс, а также достигать поставленных целей в спорте. '
             'Я могу предоставлять вам статистику по различным видам активности которые вы зарегистрируете в своей '
             'программе (бег, велосипед, ходьба, плавание и т.д.), поддерживать установку целей и напоминать о '
             'необходимости регулярно заниматься спортом. Для ознакомлением со списком команд введите команду /help\n'
             'Для удобства на клавиатуре есть две основные кнопки\n💡 /help - Список доступных команд\n'
             '🆑 /cancel - Сброс ввода последнй команды\n')
    CANCEL = '🆑 Сброс ввода последнй команды\nДля получения списка доступных команд введите: /help'
    HELP = ('💡 Вот список моих доступных команд:\n'
            '1. /start - Приветственное сообщение, краткая инструкция о возможностях бота и регистрация пользователя, '
            'если он ещё не зарегистрирован.\n'
            '2. /help - Список доступных команд и инструкция по их использованию.\n'     
            '3. /register - Регистрация нового пользователя. Если пользователь уже зарегистрирован, бот сообщает '
            'об этом.\n'
            '4. /login - Авторизация пользователя для доступа к его данным. Ограничение активности, через 6 часов '
            'требуется '
            'повторная авторизация.\n'
            '5. /add_workout\n'
            'Пример добавления новой тренировки:\n'
            '13.03.2025 бег 5 км.\n'
            '6. /add_goal - Установка цели.\n'
            '7. /view_workouts_group - Просмотр истории тренировок без цели с группировкой.\n'
            '8. /view_workout_detail - Просмотр детализации по виду тренировок.\n'
            '9. /view_goals - Просмотр целий и прогресса тренировок по ним.\n'           
            'Пример:\n'
            '13.03.2025 19.07.20265 Пробежать 50 км\n'
            '10. /reminder_off_achieved Отключение ежедневных уведомлений о просроченных и достигнутых целях.\n'
            '11. /workouts_no_goal_export_json - Экспорт данных о тренировках БЕЗ цели.\n'
            '12. /workouts_goal_export_json - Экспорт данных о целевых тренировках.\n')
    NOT_REGISTER = ('⚠️ Уважаемый пользователь вы не зарегистрированы в программе, для использования полного '
                    'функционала зарегистрируйтесь введя команду /register')
    NOT_AUTHORIZED = ('⚠️ Уважаемый пользователь вы не авторизованы в программе, для использования полного функционала '
                      'авторизуйтесь, войдите в программу под своим логином и паролем введя команду /login')
    INPUT_LOGIN = ('Введите желаемый логин для регистрации не меньше 6 и не больше 19 символов. Логин должен начинаться'
                   ' на букву. Логин может содержать только буквы латинского алфавита:\na-z или A-Z, '
                   'цифры: 0-9 и символы -_#&')
    INPUT_PASSWORD = ('Введите желаемый пароль для регистрации не меньше 6 и не больше 19 символов.\n'
                      '🚫 Утерянный пароль ВОССТАНОВЛЕНИЮ НЕ ПОДЛЕЖИТ, доступ к данным будет - НЕВОЗМОЖЕН‼️\n'
                      'Пароль должен начинаться на букву. Пароль может содержать только буквы латинского алфавита:\n'
                      'a-z или A-Z, цифры: 0-9 и символы:  - # _ & ')
    LOGIN_PROMPT = 'Введите логин указанный при регистрации'
    PASSWORD_PROMPT = 'Введите пароль указанный при регистрации'
    LOGIN_IS_BUSY = '⚠️ Пользователь с таким логином уже зарегистрирован, выберете другой, повторите ввод'
    LOGIN_NOT_EXIST = '⚠️ Данного логина не существует, повторите ввод'
    REGISTRATION_SUCCESS_MESSAGE = ('✅ Вы успешно зарегистрированы 👍, запомните свой логин и пароль\n'
                                    'Для использования полного функционала программы авторизуйтесь, войдите в '
                                    'систему под своим логином и паролем используя команду:\n/login')
    AUTHORIZATION_SUCCESS_MESSAGE = ('✅ Вы успешно авторизованы в системе 👍, вам доступен полный функционал\n'
                                     'Для ознакомлением со списком команд введите команду💡 /help\n')
    REGISTRATION_IS_NOT_REQUIRED = 'Вам не требуется повторная регистрация 👌'
    AUTHORIZATION_IS_NOT_REQUIRED = 'Вам не требуется повторная авторизация 👌'
    WORKOUT_DATA_INPUT = ('Введите тренировку в формате:\n'
                          'дата название_тренировки показатель ед.измерения\n'
                          'все данные через пробел, например:\n'
                          '12.11.2026 подтягивание 8 раз\n'
                          'сегодняшнюю дату можно не указывать, например:\n'
                          'бег 2.5 км\n'
                          'Ограничения:\n'
                          'Дата должна быть тождественна или меньше сегодняшней даты\n'
                          'Показатель: число более 0 (нуля)\n'
                          'Название тренировки: не более 50 символов\n'
                          'единицы измерения: не более 20 символов\n')
    ADD_WORKOUT_FOR_GOAL = ('Введите тренировку для цели в следующем формате:\n'
                            'дата показатель\n'
                            '12.11.2026 8\n'
                            'текущую дату можно не указывать:\n'
                            '8\n'
                            'Ограничения:\n'
                            'Показатель: число более 0 (нуля)\n'
                            'Дата тренировки должна быть между датами цели')
    WORKOUT_SUCCESS = '✅ Тренировка успешно добавлена'
    GOAL_SUCCESS = '✅ Цель успешно добавлена'
    RECORD_ADDED_SUCCESS = '✅ Запись успешно добавлена'
    PASSWORD_NOT_FOUND = '⚠️ Ваш пароль не найден, обратитесь к администратору сети'
    INVALID_PASSWORD = '⚠️ Вы неверно ввели пароль Пройдите авторизацию повторно.'
    INACTIVE = ('🚫 Доступ к программе ограничен.\n\n'
                'Вы не авторизованы в системе.\nВойдите в систему под своим логином и паролем используя команду:\n/login')
    DEACTIVATION = ('⚠️ Превышен срок активации.\n\n'
                   'У вас вышел 6 часовой срок активации.\nВойдите в систему под своим логином и паролем используя команду:\n/login')
    UNKNOWN_COMMAND = '''⚠️ Вы ввели команду:\n❗{text}❗\nданная команда мне не известна
    Для получения списка доступных доступных команд введите:\n/help\nповторите ввод'''
    NOT_ACTIVE_GOALS = ('⚠️ На данный момент у вас нет ни одной цели!\n'
                 'Для стимуляции тренировочного процесса добавьте цель.\n'
                 'Это поможет вам оставаться мотивированным и добиваться лучших результатов\n'
                 'Создайте цель командой /add_goal')
    ACTIVE_GOALS = 'У вас есть активные цели!\nТренировка будет проводиться для цели❓\n'
    ADD_GOAL = ('Введите цель достижения в следующем формате:\n'
                'Дата_начала дата_окончания имя_тренировки показатель, единицы измерения например:\n'
                '13.01.26 19.03.26 бег 100 км\n'
                'Ограничения:\n'
                'Показатель: число более 0 (нуля)\n'
                'Название тренировки: не более 50 символов\n'
                'Единицы измерения: не более 20 символов\n'
                'Дата_окончания должна быть больше даты_начала\n'
                'Дата_окончания должна быть позднее сегодняшней даты')
    LIST_GOAL_EXPIRED = '⚠️ У вас просрочена цель:'
    EXPIRED_COMMENT = ('Не отчаивайтесь, не ошибается тот, кто ничего не делает.\n '
                       'Ставьте новую цель и дерзайте, Вы можете больше!')
    LIST_GOAL_ACHIEVED = '✅ У вас достижение цели:'
    ACHIEVED_COMMENT = ('Это прекрасно ‍🔥, но не останавливайтесь на достигнутом. Все что с трудом собирается по '
                        'крупицам легко потерять. Ставим новую цель и дерзайте к новым достижениям 👏')
    IS_NO_SPECIFIED_GOAL = '⚠️ Указанной цели нет в вашем списке'
    NOT_GOAL = '⚠️ Активных целей не обнаружено!\n'
    SELECT_GOAL = 'Нажмите кнопку с номером цели для которой будет заполняться тренировка\n'
    USER_SELECTED_GOAL = 'Вы выбрали цель № '
    NOT_VIEW_WORKOUTS_ALL = '⚠️ У вас нет не целевых тренировок'
    NOT_GOAL_ALL = '⚠️ У вас нет целей по тренировкам'
    NOT_GOAL_WORKOUTS_ALL = '⚠️ У вас нет целевых тренировок'
    EXPORT_DATA_GOALS = "📈 Ваш экспорт данных о целях"
    EXPORT_DATA_WORKOUTS = '📈 Ваш экспорт данных о тренировках'
    YES_VIEW_WORKOUTS_ALL = '📂 Ваши не целевые тренировки'
    YES_VIEW_GOAL_WORKOUTS_ALL = '📂 Ваши целевые тренировки'
    YES_VIEW_GOAL_ALL = '📂 Ваши цели:'
    NUMBER_WORKOUT = 'Введите номер тренировки по которой хотите получить статистику'
    IS_NO_SPECIFIED_WORKOUT = '⚠️ Указанной тренировки нет в вашем списке'
    NOT_WORKOUTS = 'У вас пока нет сохранённых тренировок.'
    NUMBER_STATUS_GOAL = 'Введите номер цели для которой хотите просмотреть прогресс тренировок'
    REMINDER_OFF_ACHIEVED = '⚠️ Вы больше не будете получать уведомлений о ваших достигнутых и просроченных целях'

    # КЛЮЧИ АКТИВАЦИИ пользователя в боте
    ACTIVE = 'ACTIVE'
    INACTIVES = 'INACTIVE'
    DEACTIVATIONS = 'DEACTIVATION'
    ERRORS = 'ERROR'

    # ОШИБКИ
    QUERY_GOAL = '❌ Ошибка запроса целей: '
    QUERY_WORKOUTS = '❌ Ошибка запроса тренировок: '
    ERROR_REPEAT_DATA = '❌ Ошибка, повторите ввод данных\n'
    ERROR = '❌ Ошибка при обращению к серверу.\n\nПовторите попытку позже'
    ERROR_DATABASE = '❌ Ошибка обращения к БД, попробуйте позже.'
    NOT_LEN_STR = '❌ Неверная длинна, повторите ввод'
    LOGIN_START_WITH_LETTER_ERROR = '❌ Логин который вы ввели начинается не с буквы, повторите ввод'
    LOGIN_INVALID_CHARACTERS = '❌ Ваш логин содержит недопустимые символы, повторите ввод'
    INVALID_DATE_START = '🔸 Некорректный формат начальной даты или дата не существует'
    INVALID_DATE_END = '🔸 Некорректный формат конечной даты или дата не существует'
    INVALID_DATE_DIFF = '🔸 Некорректный формат, конечная дата должна быть больше начальной'
    INVALID_DATE_BETWEEN_WORKOUT = ('🔸 Некорректный формат, дата тренировки должна быть в пределах цели и не больше '
                                    'сегодняшней даты')
    INVALID_DATE_WORKOUT = '🔸 Некорректный формат даты тренировки'
    INVALID_DATE_LESS_NOW = '🔸 Некорректный формат, дата тренировки должна быть меньше либо равна сегодняшней дате'


    INVALID_LEN_NAME_WORKOUT = '🔸 Неверная длинна имени тренировки'
    INVALID_LEN_DIMENSION = '🔸 Неверная длинна единиц измерения'
    INVALID_INDICATOR = '🔸 Показатель не удовлетворяет требованиям'
    INVALID_FORMAT_DATA = '❌ Данные в строке не соответствуют указанному требованию'
    ERROR_COMPARING_DATE = '🔸 Конечная дата должна быть больше начальной.'
    ERROR_COMPARING_NOW = '🔸 Конечная и начальная дата не могут быть в прошлом'

    # КОНСТАНТЫ
    ALLOWED_CHARS_PLUS = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                          't', 'u', 'v', 'w', 'x', 'y', 'z',
                          '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-', '_', '#', '&'}
    ALLOWED_CHARS = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                     'u', 'v', 'w', 'x', 'y', 'z'}
    MAX_LEN_NAME_WORKOUT = 50
    MAX_LEN_DIMENSION = 20
    GOAL_FULL = ('start_date', 'end_date', 'target_exercise', 'target_quantity', 'unit')
    GOAL_SHORT = ('end_date', 'target_exercise', 'target_quantity', 'unit')
    WORKOUT_FULL = ('workout_date', 'exercise_type', 'quantity', 'unit')
    WORKOUT_SHORT = ('exercise_type', 'quantity', 'unit')
    WORKOUT_FOR_GOAL_FULL = ('workout_date', 'quantity')
    WORKOUT_FOR_GOAL_SHORT = ('quantity',)

    #STATUS
    STATUS_GOAL = {
        'active': 'active',
        'achieved': 'achieved',
        'expired': 'expired',
        'archive_achieved': 'archive_achieved',
        'archive_expired': 'archive_expired'
    }
    STATUS_MAPPING = {
        'active': 'активная',
        'achieved': 'достигнутая',
        'expired': 'просроченная',
        'archive_expired': 'архивная (просроченная)',
        'archive_achieved': 'архивная (достигнутая)'
    }
    SHOW_ACTIVE_GOAL = 'Вывожу список ваших активных целей:\n'
    STATUS_ACTIVE = 'active'
    STATUS_ACHIEVED = 'achieved'
    STATUS_EXPIRED = 'expired'
    STATUS_ARCHIVE_EXPIRED = 'archive_expired'
    STATUS_ARCHIVE_ACHIEVED = 'archive_achieved'

    #KEYBOARDS
    BTN_YES_FOR_GOAL = 'yes_for_goal'
    BTN_NO = 'no'

