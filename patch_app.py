import re
with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

content = content.replace(
    "import TeachersPage from './pages/Teachers'",
    "import TeachersPage from './pages/Teachers'\nimport StudentsPage from './pages/Students'\nimport ParentsPage from './pages/Parents'"
)

content = content.replace(
    "<Route path=\"/classes\" element={<ClassesPage />} />",
    "<Route path=\"/classes\" element={<ClassesPage />} />\n              <Route path=\"/students\" element={<StudentsPage />} />\n              <Route path=\"/parents\" element={<ParentsPage />} />"
)

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
