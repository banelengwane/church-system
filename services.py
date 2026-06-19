from database import get_connection
from models import Leader, Member, Contribution

class ChurchService:
    @staticmethod
    def seed_initial_data():
        """Populates the database with basic starter records for testing."""
        conn = get_connection()
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
        conn.close()
    
    @staticmethod
    def get_all_leaders():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT leader_id, name, role FROM leaders")
        leaders = [Leader(*row) for row in cursor.fetchall()]
        conn.close()
        return leaders
    
    @staticmethod
    def get_all_members():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT member_id, first_name, last_name, assigned_leader_id FROM members")
        members = [Member(*row) for row in cursor.fetchall()]
        conn.close()
        return members

    @staticmethod
    def add_member(first_name, last_name, leader_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO members (first_name, last_name, assigned_leader_id) VALUES (?, ?, ?)",
            (first_name, last_name, leader_id)
        )
        conn.commit()
        conn.close()
    
    @staticmethod
    def add_contribution(member_id, amount, c_type):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO contributions (member_id, amount, type) VALUES (?, ?, ?)",
            (member_id, amount, c_type)
        )
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_underdeacon_data(leader_id):
        """Returns members assigned to a leader and their combined total tithes."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT member_id, first_name, last_name, assigned_leader_id FROM members WHERE assigned_leader_id = ?", (leader_id,))
        flock = [Member(*row) for row in cursor.fetchall()]

        # calculate total tithes collected from this leader's flock
        # we use a SQL JOIN to look at contributions linked to members assigned to this leader
        cursor.execute('''
        SELECT SUM(c.amount)
        FROM contributions c
        JOIN members m ON c.member_id = m.member_id
        WHERE m.assigned_leader_id = ? AND c.type = 'Tithe'
        ''', (leader_id,))

        total_tithes = cursor.fetchone()[0] or 0.0

        conn.close()
        return flock, total_tithes
    
    @staticmethod
    def get_apostle_data():
        """Returns global system aggregates."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM members")
        total_members = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(amount) FROM contributions WHERE type = 'Tithe'")
        global_thithes = cursor.fetchone()[0] or 0.0

        cursor.execute('''
            SELECT l.name, l.role, SUM(c.amount)
            FROM leaders l
            JOIN members m ON l.leader_id = m.assigned_leader_id
            JOIN contributions c ON m.member_id = c.member_id
            GROUP BY l.leader_id
        ''')
        breakdown = cursor.fetchall()

        conn.close()
        return total_members, global_thithes, breakdown