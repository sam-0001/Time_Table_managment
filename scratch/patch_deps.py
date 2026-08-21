import re

with open('app/api/deps.py', 'r') as f:
    content = f.read()

new_deps = """    user = db.query(User).filter(User.id == token_data.sub).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Handle demo mode token overrides
    is_demo_mode = payload.get("is_demo_mode", False)
    token_school_id = payload.get("school_id")
    real_school_id = payload.get("real_school_id")
    
    if is_demo_mode and token_school_id:
        db.expunge(user)
        user.real_school_id = user.school_id # Store original
        user.school_id = token_school_id
        user.is_demo_mode = True
    else:
        user.is_demo_mode = False
        user.real_school_id = user.school_id

    return user"""

content = content.replace(
    '    user = db.query(User).filter(User.id == token_data.sub).first()\n    if user is None:\n        raise credentials_exception\n    if not user.is_active:\n        raise HTTPException(status_code=400, detail="Inactive user")\n    return user',
    new_deps
)

with open('app/api/deps.py', 'w') as f:
    f.write(content)
