import re
with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

content = content.replace(
    "<Route path=\"/classes\" element={<AppLayout><ClassesPage /></AppLayout>} />",
    "<Route path=\"/classes\" element={<AppLayout><ClassesPage /></AppLayout>} />\n          <Route path=\"/students\" element={<AppLayout><StudentsPage /></AppLayout>} />\n          <Route path=\"/parents\" element={<AppLayout><ParentsPage /></AppLayout>} />"
)

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)

with open("frontend/src/pages/Students.tsx", "r") as f:
    content = f.read()
    content = content.replace("import { Card, CardContent, CardHeader } from '@/components/ui/card'", "import { Card, CardContent } from '@/components/ui/card'")
with open("frontend/src/pages/Students.tsx", "w") as f:
    f.write(content)

with open("frontend/src/pages/Parents.tsx", "r") as f:
    content = f.read()
    content = content.replace("import { Card, CardContent, CardHeader } from '@/components/ui/card'", "import { Card, CardContent } from '@/components/ui/card'")
with open("frontend/src/pages/Parents.tsx", "w") as f:
    f.write(content)
