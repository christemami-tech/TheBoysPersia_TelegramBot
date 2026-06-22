ADMINS = [7736093011]  # ادمین اصلی تو

def is_admin(user_id):
    return user_id in ADMINS


def add_admin(user_id):
    if user_id not in ADMINS:
        ADMINS.append(user_id)


def remove_admin(user_id):
    if user_id in ADMINS:
        ADMINS.remove(user_id)
