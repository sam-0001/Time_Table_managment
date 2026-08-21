import re

with open('frontend/src/pages/Dashboard.tsx', 'r') as f:
    content = f.read()

user_state = """  const [user, setUser] = useState<any>(null);
  const [isDemoLoading, setIsDemoLoading] = useState(false);
  const [counts, setCounts] = useState({ teachers: 0, classes: 0 });

  useEffect(() => {
    api.get('/auth/me').then(res => setUser(res.data)).catch(console.error);
    api.get('/teachers/').then(res => setCounts(prev => ({ ...prev, teachers: res.data.length }))).catch(console.error);
    const params = new URLSearchParams();
    params.append('academic_year_id', 'temp-academic-year-id');
    api.get(`/classes/?${params.toString()}`).then(res => setCounts(prev => ({ ...prev, classes: res.data.length }))).catch(console.error);
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
      setIsDemoLoading(false);
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
      setIsDemoLoading(false);
    }
  };
"""

content = content.replace(
    '  const [viewMode, setViewMode] = useState<\'division\' | \'teacher\' | \'master\'>(\'division\')',
    user_state + '\n  const [viewMode, setViewMode] = useState<\'division\' | \'teacher\' | \'master\'>(\'division\')'
)

with open('frontend/src/pages/Dashboard.tsx', 'w') as f:
    f.write(content)
