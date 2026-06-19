import sqlite3

# defining the db filename
DB_NAME = "oac_management.db"

def get_connection():
    """Creates the db file and necessary tables if the dont exist"""
    #connect to th db (creating it if it doesnt exist)
    conn = sqlite3.connect(DB_NAME)

    #enforce foreign key constraints in SQLite
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    print("Initializing database tables...")

    # Create leaders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leaders (
            leader_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT CHECK(role IN ('Underdeacon', 'Priest', 'Elder', 'Overseer', 'Apostle')) NOT NULL           
        )
    ''')
    
    #create members table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            member_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            assigned_leader_id INTEGER,
            FOREIGN KEY (assigned_leader_id) REFERENCES leaders(leader_id)
        )
    ''')

    # create contribution table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contributions (
            contribution_id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            type TEXT CHECK(type IN ('Tithe', 'Offering', 'Building Fund')) NOT NULL,
            date_logged TEXT DEFAULT CURRENT_DATE,
            FOREIGN KEY (member_id) REFERENCES members(member_id)
        )
    ''')

    #save changes and close the connection
    conn.commit()
    conn.close()
