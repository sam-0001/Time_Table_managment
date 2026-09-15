import re
with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

content = content.replace(
    "import ParentsPage from './pages/Parents'",
    "import ParentsPage from './pages/Parents'\nimport AttendancePage from './pages/Attendance'"
)

content = content.replace(
    "<Route path=\"/parents\" element={<AppLayout><ParentsPage /></AppLayout>} />",
    "<Route path=\"/parents\" element={<AppLayout><ParentsPage /></AppLayout>} />\n          <Route path=\"/attendance\" element={<AppLayout><AttendancePage /></AppLayout>} />"
)

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
    
with open("frontend/src/components/layout/AppLayout.tsx", "r") as f:
    content = f.read()

content = content.replace(
    "{ name: 'Parents', href: '/parents', icon: Users },",
    "{ name: 'Parents', href: '/parents', icon: Users },\n    { name: 'Attendance', href: '/attendance', icon: BookOpen },"
)

with open("frontend/src/components/layout/AppLayout.tsx", "w") as f:
    f.write(content)
