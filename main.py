from context import *
import telebot
from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton


bot = telebot.TeleBot("7168775744:AAGQBbAanI72behsaozeothGlKh_fI5NB84")
posrednik_id=-4582381538
posrednik_tokenn=telebot.TeleBot("7320461688:AAEr4r5bg5kuZ54T_z_dZ4YYhMcEiR2E_h8")


def register_user(telegram_id, username):
    conn = open_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO Users (telegram_id, username) VALUES (%s, %s) RETURNING id;", (telegram_id, username))
    user_id = cur.fetchone()[0]
    conn.commit()
    close_connection(conn, cur)
    return user_id

def get_user_by_telegram_id(telegram_id):
    print(f"Fetching user with telegram_id: {telegram_id}")  
    conn = open_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM Users WHERE telegram_id = %s;", (telegram_id,))
        user = cur.fetchone()
    except Exception as e:
        print(f"Error fetching user: {e}")  # Log error
        user = None
    finally:
        close_connection(conn, cur)
    return user


def update_user(telegram_id, username):
    conn = open_connection()
    cur = conn.cursor()
    cur.execute("UPDATE Users SET username = %s WHERE telegram_id = %s;", (username, telegram_id))
    conn.commit()
    close_connection(conn, cur)

def delete_user(telegram_id):
    conn = open_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Users WHERE telegram_id = %s;", (telegram_id,))
    conn.commit()
    close_connection(conn, cur)

@bot.message_handler(commands=['start'])
def start(message):
    telegram_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    
    user = get_user_by_telegram_id(telegram_id)
    if not user:
        register_user(telegram_id, username)

    button5 = KeyboardButton("/User")
    button10 = KeyboardButton("/update_user")
    button11 = KeyboardButton("/delete_user")
    button6 = KeyboardButton("/add_job")
    button7 = KeyboardButton("/view_jobs")
    button8 = KeyboardButton("/add_resume")
    button9 = KeyboardButton("/view_resumes")
    button99 = KeyboardButton("/delete_resume")
    button12 = KeyboardButton("/delete_job")


    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.row(button5)
    markup.row(button10, button11)
    markup.row(button6, button12, button7)
    markup.row(button8, button9, button99)

    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}👋🏻', reply_markup=markup)

@bot.message_handler(commands=['User'])
def user_info(message):
    telegram_id = message.from_user.id
    user = get_user_by_telegram_id(telegram_id)
    
    if user:
        bot.send_message(message.chat.id, f"Ваш ID: {user[0]}, Ваше имя: {user[2]}")  
        bot.send_message(message.chat.id, "Пользователь не найден.")

@bot.message_handler(commands=['update_user'])
def prompt_update_user(message):
    bot.send_message(message.chat.id, "Введите новое имя пользователя:")
    bot.register_next_step_handler(message, process_update_user_name)

def process_update_user_name(message):
    new_username = message.text
    telegram_id = message.from_user.id
    update_user(telegram_id, new_username)
    bot.send_message(message.chat.id, "Имя пользователя обновлено.")


@bot.message_handler(commands=['delete_user'])
def prompt_delete_user(message):
    telegram_id = message.from_user.id
    delete_user(telegram_id)
    bot.send_message(message.chat.id, "Ваш профиль удален. Пожалуйста, зарегистрируйтесь снова.")
    start(message)  


@bot.message_handler(commands=['add_resume'])
def prompt_add_resume(message):
    bot.send_message(message.chat.id, "Введите название резюме:")
    bot.register_next_step_handler(message, process_resume_title)






@bot.message_handler(commands=['add_job'])
def prompt_add_job(message):
    bot.send_message(message.chat.id, "Введите название вакансии:")
    bot.register_next_step_handler(message, process_job_title)

def process_job_title(message):
    job_title = message.text
    bot.send_message(message.chat.id, "Введите описание вакансии:")
    bot.register_next_step_handler(message, process_job_description, job_title)

def process_job_description(message, job_title):
    job_description = message.text
    bot.send_message(message.chat.id, "Введите название компании:")
    bot.register_next_step_handler(message, process_job_company, job_title, job_description)

def process_job_company(message, job_title, job_description):
    job_company = message.text
    telegram_id = message.from_user.id
    user = get_user_by_telegram_id(telegram_id)

    if user:
        add_job_listing(user[0], job_title, job_description, job_company) 
        bot.send_message(message.chat.id, "Вакансия добавлена.")
    else:
        bot.send_message(message.chat.id, "Пользователь не найден.")

def add_job_listing(user_id, title, description, company):
    conn = open_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO JobListing (user_id, title, description, company) VALUES (%s, %s, %s, %s);", 
                (user_id, title, description, company))
    conn.commit()
    close_connection(conn, cur)


def get_all_job_listings():
    conn = open_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM JobListing;")
    listings = cur.fetchall()
    close_connection(conn, cur)
    return listings
@bot.message_handler(commands=['view_jobs'])
def view_jobs(message):
    job_listings = get_all_job_listings()
    if job_listings:
        for job in job_listings:
            bot.send_message(message.chat.id, f"ID: {job[0]}, Название: {job[1]}, Описание: {job[2]}, Компания: {job[3]}")
    else:
        bot.send_message(message.chat.id, "Вакансии не найдены.")
@bot.message_handler(commands=['delete_job'])
def prompt_delete_job(message):
    bot.send_message(message.chat.id, "Введите ID вакансии для удаления:")
    bot.register_next_step_handler(message, process_delete_job_id)

def process_delete_job_id(message):
    job_id = message.text
    try:
        delete_job(job_id)
        bot.send_message(message.chat.id, "Вакансия удалена.")
    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка при удалении вакансии. Проверьте ID и попробуйте снова.")
        print(f"Error deleting job: {e}")  

def delete_job(job_id):
    conn = open_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM JobListing WHERE id = %s;", (job_id,))
    conn.commit()
    close_connection(conn, cur)


def add_resume(user_id, title, description, name):
    conn = open_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO Resume (user_id, title, description, name) VALUES (%s, %s, %s, %s);", (user_id, title, description, name))
    conn.commit()
    close_connection(conn, cur)

def get_all_resumes():
    conn = open_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Resume;")
    resumes = cur.fetchall()
    close_connection(conn, cur)
    return resumes

def update_resume(resume_id, title, description):
    conn = open_connection()
    cur = conn.cursor()
    cur.execute("UPDATE Resume SET title = %s, description = %s WHERE id = %s;", (title, description, resume_id))
    conn.commit()
    close_connection(conn, cur)

def delete_resume(resume_id):
    conn = open_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Resume WHERE id = %s;", (resume_id,))
    conn.commit()
    close_connection(conn, cur)

@bot.message_handler(commands=['start'])
def start(message):
    telegram_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    
    user = get_user_by_telegram_id(telegram_id)
    if not user:
        register_user(telegram_id, username)


    button5 = KeyboardButton("/User")
    button6 = KeyboardButton("/add_job")
    button7 = KeyboardButton("/view_jobs")
    button8 = KeyboardButton("/add_resume")
    button9 = KeyboardButton("/view_resumes")
    button99 = KeyboardButton("/delete_resume")
    button12 = KeyboardButton("/delete_job")



    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.row(button5)
    markup.row(button6, button12, button7)
    markup.row(button8, button9, button99)

    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}👋🏻', reply_markup=markup)


@bot.message_handler(commands=['add_resume'])
def prompt_add_resume(message):
    bot.send_message(message.chat.id, "Введите название резюме:")
    bot.register_next_step_handler(message, process_resume_title)

def process_resume_title(message):
    resume_title = message.text
    bot.send_message(message.chat.id, "Введите описание резюме:")
    bot.register_next_step_handler(message, process_resume_description, resume_title)

def process_resume_description(message, resume_title):
    resume_description = message.text
    bot.send_message(message.chat.id, "Введите ваше имя:")
    bot.register_next_step_handler(message, process_resume_name, resume_title, resume_description)

def process_resume_name(message, resume_title, resume_description):
    resume_name = message.text
    telegram_id = message.from_user.id
    user = get_user_by_telegram_id(telegram_id)

    if user:
        add_resume(user[0], resume_title, resume_description, resume_name) 
        bot.send_message(message.chat.id, "Резюме добавлено.")
    else:
        bot.send_message(message.chat.id, "Пользователь не найден.")


@bot.message_handler(commands=['view_resumes'])
def view_resumes(message):
    resumes = get_all_resumes()
    if resumes:
        for resume in resumes:
            user_id = resume[1]  
            resume_id = resume[0]  
            resume_title = resume[2]  
            resume_description = resume[3] 

            user = get_user_by_telegram_id(user_id)
            user_name = user[2] if user else "Unknown"  
            
            bot.send_message(
                message.chat.id, 
                f"ID: {resume_id}, Имя: {user_name}, Название: {resume_title}, Описание: {resume_description}"
            )
    else:
        bot.send_message(message.chat.id, "Резюме не найдено.")


@bot.message_handler(commands=['update_resume'])
def prompt_update_resume(message):
    bot.send_message(message.chat.id, "Введите ID резюме для обновления:")
    bot.register_next_step_handler(message, process_update_resume_id)

def process_update_resume_id(message):
    resume_id = message.text
    bot.send_message(message.chat.id, "Введите новое название резюме:")
    bot.register_next_step_handler(message, process_update_resume_title, resume_id)

def process_update_resume_title(message, resume_id):
    new_title = message.text
    bot.send_message(message.chat.id, "Введите новое описание резюме:")
    bot.register_next_step_handler(message, process_update_resume_description, resume_id, new_title)

def process_update_resume_description(message, resume_id, new_title):
    new_description = message.text
    update_resume(resume_id, new_title, new_description)
    bot.send_message(message.chat.id, "Резюме обновлено.")

@bot.message_handler(commands=['delete_resume'])
def prompt_delete_resume(message):
    bot.send_message(message.chat.id, "Введите ID резюме для удаления:")
    bot.register_next_step_handler(message, process_delete_resume_id)

def process_delete_resume_id(message):
    resume_id = message.text
    delete_resume(resume_id)
    bot.send_message(message.chat.id, "Резюме удалено.")

bot.infinity_polling()