from database import initialize_database
from services import ChurchService

def show_underdeacon_dashboard(leader_id, name):
    print(f"\n========================================")
    print(f"📋 UNDERDEACON DASHBOARD: {name}")
    print(f"==========================================")

    flock, total_tithes = ChurchService.get_underdeacon_data(leader_id)

    print(f"\n👥 Your Flock ({len(flock)} Members):")
    for member in flock:
        print(f"    - {member.full_name}")
    
    print(f"\n💰 Total Tithes Collected by You: R {total_tithes:.2f}")
    print(f"==========================================")
    input("\nPress Enter to return to the main menu...")

def show_apostle_dashboard(leader_name):
    print(f"\n==========================================")
    print(f"🏛️ APOSTLE GLOBAL DASHBOARD: {leader_name}")
    print(f"==========================================")

    total_members, global_thithes, breakdown = ChurchService.get_apostle_data()
    
    print(f"\n🌐 Church-wide Overview:")
    print(f"    - Total Registered Members: {total_members}")
    print(f"    - Total Global Tithes Collected: R {global_thithes:.2f}")

    print(f"\n📊 Collection Breakdown by Leader:")
    for l_name, l_role, total in breakdown:
        print(f"    - {l_name} ({l_role}): R {total:.2f}")

    print(f"===========================================")
    input("\nPress Enter to return to the main menu...")

def add_new_member():
    print(f"📝 REGISTER NEW MEMBER")
    first_name = input("Enter first name: ").strip()
    last_name = input("Enter last name: ").strip()

    if not first_name or not last_name:
        print("❌ Error: Names cannot be blank.")
        return

    #show available leaders so the user can assign the member correctly
    print("\nAvailable leaders to assign this member to:")
    leaders = ChurchService.get_all_leaders()
    for leader in leaders:
        print(f"    [{leader.id}] {leader.name} ({leader.role})")
    
    try:
        leader_id = int(input("\nEnter Leader ID: "))
        ChurchService.add_member(first_name, last_name, leader_id)
        print(f"\n✓ Success: {first_name} has been registered!")

    except ValueError:
        print("❌ Error: Invalid ID layout. ID Must be a number.")
    input("\nPress Enter to return...")

def record_contribution():
    print(f"💰 RECORD FINANCIAL CONTRIBUTION")
    members = ChurchService.get_all_members()
    for m in members:
        print(f"    [{m.id}] {m.full_name}")
    
    try:
        member_id = int(input("\nEnter Member ID: "))
        amount = float(input("Enter Amount (e.g., 250.50): R "))
        print("1. Tithe\n2. Offering\n3. Building Fund")
        type_choice = input("Select Type (1-3): ").strip()

        type_map = {'1': 'Tithe', '2': 'Offering', '3': 'Building Fund'}
        contribution_type = type_map.get(type_choice)

        if contribution_type:
            ChurchService.add_contribution(member_id, amount, contribution_type)
            print(f"\n✓ Success: Contribution logged!")
        else:
            print("❌: Invalid type selection.")

    except ValueError:
        print("❌: Invalid input formatting. Numbers only.")
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
    ChurchService.seed_initial_data()
    main_menu()