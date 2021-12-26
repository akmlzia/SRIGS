import sqlite3
from sqlite3 import Error

def initiate_db():
    conn = sqlite3.connect('data.db')
    curs = conn.cursor()
    create_students_table = """ CREATE TABLE IF NOT EXISTS students (
                                id integer PRIMARY KEY,
                                nick_name text NOT NULL,
                                full_name text NOT NULL,
                                group_name text,
                                join_date text NOT NULL
                            );"""
    create_decks_table = """ CREATE TABLE IF NOT EXISTS decks (
                                id integer PRIMARY KEY,
                                deck_name text NOT NULL,
                                deck text NOT NULL,
                                old_deck text,
                                add_date text NOT NULL,
                                current_change_date text
                            );"""
    create_progress_table = """CREATE TABLE IF NOT EXISTS progress_table (
                                        id integer PRIMARY KEY,
                                        begin_date text NOT NULL,
                                        progress text NOT NULL,
                                        student_id integer NOT NULL REFERENCES students(id),
                                        deck_id integer NOT NULL REFERENCES decks(id)
                                    );"""

    commands = [create_students_table, create_decks_table, create_progress_table]
    for command in commands:
        curs.execute(command)

    conn.close()