import re

with open('frontend/src/pages/Dashboard.tsx', 'r') as f:
    content = f.read()

content = content.replace("import React, { useState } from 'react'", "import React, { useState, useEffect } from 'react'\nimport { api } from '@/lib/api'")
content = content.replace("import { BookOpen, Users, CalendarDays, UserX, Loader2, Printer, Download } from 'lucide-react'", "import { BookOpen, Users, CalendarDays, UserX, Loader2, Printer, Download, PlayCircle, XCircle } from 'lucide-react'")

with open('frontend/src/pages/Dashboard.tsx', 'w') as f:
    f.write(content)
