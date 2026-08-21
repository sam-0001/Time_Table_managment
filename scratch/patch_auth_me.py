import sys

def patch():
    with open('app/api/routes/auth.py', 'r') as f:
        content = f.read()
    
    old_me = """@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user"""
    
    new_me = """@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    user_dict = {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "school_plan": current_user.school.plan_type if current_user.school else "DEMO"
    }
    return user_dict"""
    content = content.replace(old_me, new_me)
    with open('app/api/routes/auth.py', 'w') as f:
        f.write(content)

patch()
