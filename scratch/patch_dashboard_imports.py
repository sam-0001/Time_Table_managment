import re

with open('frontend/src/pages/Dashboard.tsx', 'r') as f:
    content = f.read()

content = content.replace("import { useState }", "import { useState, useEffect }")
if "from '@/lib/api'" not in content:
    content = content.replace("import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'", "import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'\nimport { api } from '@/lib/api'")
if "PlayCircle" not in content:
    content = content.replace("import { Users, BookOpen, Layers, Settings, CalendarDays, Loader2 } from 'lucide-react'", "import { Users, BookOpen, Layers, Settings, CalendarDays, Loader2, PlayCircle, XCircle } from 'lucide-react'")

with open('frontend/src/pages/Dashboard.tsx', 'w') as f:
    f.write(content)
