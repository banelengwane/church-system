class Leader:
    def __init__(self, leader_id, name, role):
        self.id = leader_id
        self.name = name
        self.role = role

class Member:
    def __init__(self, member_id, first_name, last_name, assigned_leader_id):
        self.id = member_id
        self.first_name = first_name
        self.last_name = last_name
        self.assigned_leader_id = assigned_leader_id

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Contribution:
    def __init__(self, contribution_id, member_id, amount, contribution_type, date_logged):
        self.id = contribution_id
        self.member_id = member_id
        self.amount = amount
        self.type = contribution_type
        self.date_logged = date_logged