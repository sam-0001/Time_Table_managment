import sys

def patch():
    with open('frontend/src/lib/auth.ts', 'r') as f:
        content = f.read()
    
    old_iface = """export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'SUPER_ADMIN' | 'SCHOOL_ADMIN' | 'PRINCIPAL' | 'TEACHER';
}"""
    new_iface = """export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'SUPER_ADMIN' | 'SCHOOL_ADMIN' | 'PRINCIPAL' | 'TEACHER';
  school_plan?: string;
}"""
    content = content.replace(old_iface, new_iface)
    with open('frontend/src/lib/auth.ts', 'w') as f:
        f.write(content)
patch()
