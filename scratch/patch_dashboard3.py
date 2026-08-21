import re

with open('frontend/src/pages/Dashboard.tsx', 'r') as f:
    content = f.read()

imports = """import { api } from '@/lib/api';
import { PlayCircle, XCircle } from 'lucide-react';"""

content = content.replace("import { useState", imports + "\nimport { useState, useEffect")

user_state = """  const [isGenerating, setIsGenerating] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [isDemoLoading, setIsDemoLoading] = useState(false);

  useEffect(() => {
    api.get('/auth/me').then(res => setUser(res.data)).catch(console.error);
  }, []);

  const handleEnterDemo = async () => {
    setIsDemoLoading(true);
    try {
      const res = await api.post('/auth/enter-demo');
      localStorage.setItem('access_token', res.data.access_token);
      window.location.reload();
    } catch (e) {
      console.error(e);
      alert('Failed to enter demo mode');
    }
  };

  const handleExitDemo = async () => {
    setIsDemoLoading(true);
    try {
      const res = await api.post('/auth/exit-demo');
      localStorage.setItem('access_token', res.data.access_token);
      window.location.reload();
    } catch (e) {
      console.error(e);
      alert('Failed to exit demo mode');
    }
  };
"""

content = content.replace(
    '  const [isGenerating, setIsGenerating] = useState(false);',
    user_state
)

buttons = """          <div className="flex gap-2">
            {user?.is_demo_mode ? (
              <Button variant="destructive" onClick={handleExitDemo} disabled={isDemoLoading}>
                {isDemoLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <XCircle className="mr-2 h-4 w-4" />}
                Exit Demo Sandbox
              </Button>
            ) : (
              <Button variant="outline" onClick={handleEnterDemo} disabled={isDemoLoading} className="text-amber-600 border-amber-600 hover:bg-amber-50">
                {isDemoLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <PlayCircle className="mr-2 h-4 w-4" />}
                Try Demo Sandbox
              </Button>
            )}
            <Button variant="outline" onClick={() => navigate('/leaves')}>Mark Leave</Button>"""

content = content.replace(
    '          <div className="flex gap-2">\n            <Button variant="outline" onClick={() => navigate(\'/leaves\')}>Mark Leave</Button>',
    buttons
)

# And wait! What about "Manage via Teachers" on the Dashboard?
# Let's fix that too to show actual counts!
dashboard_fetch = """  const [counts, setCounts] = useState({ teachers: 0, classes: 0 });
  useEffect(() => {
    api.get('/teachers/').then(res => setCounts(prev => ({ ...prev, teachers: res.data.length }))).catch(console.error);
    const params = new URLSearchParams();
    params.append('academic_year_id', 'temp-academic-year-id');
    api.get(`/classes/?${params.toString()}`).then(res => setCounts(prev => ({ ...prev, classes: res.data.length }))).catch(console.error);
  }, []);
"""

content = content.replace(
    '  const [isDemoLoading, setIsDemoLoading] = useState(false);',
    '  const [isDemoLoading, setIsDemoLoading] = useState(false);\n' + dashboard_fetch
)

content = content.replace(
    '<div className="text-2xl font-bold">Manage via Teachers</div>',
    '<div className="text-2xl font-bold">{counts.teachers}</div>'
)

content = content.replace(
    '<div className="text-2xl font-bold">Manage via Classes</div>',
    '<div className="text-2xl font-bold">{counts.classes}</div>'
)


with open('frontend/src/pages/Dashboard.tsx', 'w') as f:
    f.write(content)
