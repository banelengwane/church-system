import sqlite3
import os

# defining the db filename
DB_NAME = "oac_management.db"

def initialize_database():
    """Creates the db file and necessary tables if the dont exist"""
    #connect to th db (creating it if it doesnt exist)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    #enforce foreign key constraints in SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")

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
    print("Database setup complete!\n")

def seed_initial_data():
    """Populates the database with basic starter records for testing."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    #check if we already have leaders to prevent duplicating data every time we run 
    cursor.execute("SELECT COUNT(*) FROM leaders")
    if cursor.fetchone()[0] == 0:
        print("Seeding started data...")

        #Insert sample leaders
        cursor.execute("INSERT INTO leaders (name, role) VALUES ('Deacon Khumalo', 'Underdeacon')")
        cursor.execute("INSERT INTO leaders (name, role) VALUES ('Priest Naidoo', 'Priest')")
        cursor.execute("INSERT INTO leaders (name, role) VALUES ('Apostle Mkhathali', 'Apostle')")

        # grab the generated IDs
        deacon_id = 1
        priest_id = 2

        #insert sample members and link them to leaders
        cursor.execute("INSERT INTO members (first_name, last_name, assigned_leader_id) VALUES ('Banele', 'Ngwane', ?)", (deacon_id,))
        cursor.execute("INSERT INTO members (first_name, last_name, assigned_leader_id) VALUES ('Sipho', 'Sithole', ?)", (deacon_id,))
        cursor.execute("INSERT INTO members (first_name, last_name, assigned_leader_id) VALUES ('Thabo', 'Vara', ?)", (priest_id,))

        # insert sample tithes/contributions (Member 1 and 2 belong to the underdeacon)
        cursor.execute("INSERT INTO contributions (member_id, amount, type) VALUES (1, 150.00, 'Tithe')")
        cursor.execute("INSERT INTO contributions (member_id, amount, type) VALUES (2, 200.00, 'Tithe')")
        cursor.execute("INSERT INTO contributions (member_id, amount, type) VALUES (3, 350.00, 'Tithe')")

        conn.commit()
        print("Starter data successfully loaded!")
    
    conn.close()

def show_underdeacon_dashboard(leader_id, leader_name):
    """Displays data strictly belonging to the specific Underdeacon's flock."""
    print(f"\n========================================")
    print(f"📋 UNDERDEACON DASHBOARD: {leader_name}")
    print(f"==========================================")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # fetch and count numbers assigned to this leader
    cursor.execute("SELECT first_name, last_name FROM members WHERE assigned_leader_id = ?", (leader_id,))
    members = cursor.fetchall()

    print(f"\n👥 Your Flock ({len(members)} Members):")
    for first, last in members:
        print(f"    - {first} {last}")
    
    # calculate total tithes collected from this leader's flock
    # we use a SQL JOIN to look at contributions linked to members assigned to this leader
    cursor.execute('''
    SELECT SUM(c.amount)
    FROM contributions c
    JOIN members m ON c.member_id = m.member_id
    WHERE m.assigned_leader_id = ? AND c.type = 'Tithe'
    ''', (leader_id,))

    total_tithes = cursor.fetchone()[0] or 0.0
    print(f"\n💰 Total Tithes Collected by You: R {total_tithes:.2f}")
    print(f"==========================================")

    conn.close()
    input("\nPress Enter to return to the main menu...")

def show_apostle_dashboard(leader_name):
    """Displays church-wide aggregated summaries for the Apostle."""
    print(f"\n==========================================")
    print(f"🏛️ APOSTLE GLOBAL DASHBOARD: {leader_name}")
    print(f"==========================================")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # total church metrics
    cursor.execute("SELECT COUNT(*) FROM members")
    total_members = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(amount) FROM contributions WHERE type = 'Tithe'")
    global_thithes = cursor.fetchone()[0] or 0.0

    print(f"\n🌐 Church-wide Overview:")
    print(f"    - Total Registered Members: {total_members}")
    print(f"    - Total Global Tithes Collected: R {global_thithes:.2f}")

    # performance breakdown per leader
    print(f"\n📊 Collection Breakdown by Leader:")
    cursor.execute('''
        SELECT l.name, l.role, SUM(c.amount)
        FROM leaders l
        JOIN members m ON l.leader_id = m.assigned_leader_id
        JOIN contributions c ON m.member_id = c.member_id
        GROUP BY l.leader_id
    ''')
    breakdown = cursor.fetchall()

    for name, role, total in breakdown:
        print(f"    - {name} ({role}): R {total:.2f}")

    print(f"===========================================")
    conn.close()
    input("\nPress Enter to return to the main menu...")

def add_new_member():
    """Allows leaders to register a new member into the system."""
    print(f"\n------------------------------------------")
    print(f"📝 REGISTER NEW MEMBER")
    print(f"------------------------------------------")

    first_name = input("Enter first name: ").strip()
    last_name = input("Enter last name: ").strip()

    if not first_name or not last_name:
        print("❌ Error: First and last names cannot be blank.")
        return
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    #show available leaders so the user can assign the member correctly
    print("\nAvailable leaders to assignn this membe to:")
    cursor.execute("SELECT leader_id, name, role FROM leaders")
    leaders = cursor.fetchall()
    for l_id, name, role in leaders:
        print(f"    [{l_id}] {name} ({role})")
    
    try:
        leader_id = int(input("\nEnter Leader ID number: "))
    except ValueError:
        print("❌ Error: Invalid ID layout. ID Must be a number.")
        conn.close()
        return
    
    #inser the new member into the database
    cursor.execute('''
        INSERT INTO members (first_name, last_name, assigned_leader_id)
        VALUES (?, ?, ?)
    ''', (first_name, last_name, leader_id))

    conn.commit()
    print(f"\n✓ Success: {first_name} {last_name} has been digitally registered!")
    conn.close()
    input("\nPress Enter to return...")

def record_contribution():
    """Allows leaders to capture a paper tithe or collection reception digitally."""
    print(f"\n------------------------------------------")
    print(f"💰 RECORD FINANCIAL CONTRIBUTION")
    print(f"------------------------------------------")    

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # show registered members so the leader can select who paid
    print("Select the member making the contribution:")
    cursor.execute("SELECT member_id, first_name, last_name FROM members")
    members = cursor.fetchall()
    for m_id, first, last in members:
        print(f"    [{m_id}] {first} {last}")
    
    try:
        member_id = int(input("\nEnter Member ID number: "))
        amount = float(input("Enter Amount (e.g., 250.50): R "))
    except ValueError:
        print("❌ Error: Invalid input formatting. Numbers only.")
        conn.close()
        return
    
    print("\nContribution Types:")
    print("1. Tithe\n2. Offering\n3. Building Fund")
    type_choice = input("Select Type (1-3): ").strip()

    # map selection to the restricted database keywords
    type_map = {'1': 'Tithe', '2': 'Offering', '3': 'Building Fund'}
    contribution_type = type_map.get(type_choice)

    if not contribution_type:
        print("❌ Error: Invalid type selection.")
        conn.close()
        return
    
    # insert the transaction log
    cursor.execute('''
        INSERT INTO contributions (member_id, amount, type)
        VALUES (?, ?, ?)
    ''', (member_id, amount, contribution_type))

    conn.commit()
    print(f"\n✓ Success: R {amount:.2f} successfully processed as '{contribution_type}'!")
    conn.close()
    input("\nPress Enter to return...")

def main_menu():
    """The main interface loop running in the console."""
    while True:
        print("\n=== OLD APOSTOLIC CHURCH MANAGEMENT SYSTEM ===")
        print("1. Log in as Deacon Khumalo (Underdeacon)")
        print("2. Log in as Apostle Mkhathali (Apostle)")
        print("3. 📝 Register a New Member")
        print("4. 💰 Capture Member Contribution")
        print("5. Exit System")

        choice = input("\nEnter your choice (1-5):").strip()

        if choice == '1':
            # ID 1 belongs to deacon khumalo from our seed data
            show_underdeacon_dashboard(1, "Deacon Khumalo")
        elif choice == '2':
            #ID 3 belongs to apostle mkhathali from our seed data
            show_apostle_dashboard("Apostle Mkhathali")
        elif choice == '3':
            add_new_member()
        elif choice == '4':
            record_contribution()
        elif choice == '5':
            print("\nExiting system. Thanks for your service!")
            break
        else:
            print("\n❌ Invalid option. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    # runs automatically when you execute the script
    initialize_database()
    seed_initial_data()
    main_menu()