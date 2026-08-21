import re

with open('frontend/src/components/PaymentModal.tsx', 'r') as f:
    content = f.read()

# Add useNavigate
if "useNavigate" not in content:
    content = content.replace(
        "import { toast } from 'sonner'",
        "import { toast } from 'sonner'\nimport { useNavigate } from 'react-router-dom'"
    )

    content = content.replace(
        "const [loading, setLoading] = useState(false)",
        "const [loading, setLoading] = useState(false)\n  const navigate = useNavigate()"
    )

# Add View All Plans button
button_code = """                  <button
                    type="button"
                    className="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0"
                    onClick={() => { setIsOpen(false); navigate('/profile'); }}
                  >
                    View All Plans
                  </button>
                  <button
                    type="button"
                    className="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0"
                    onClick={() => setIsOpen(false)}
                  >
                    Cancel
                  </button>"""

content = content.replace(
    """                  <button
                    type="button"
                    className="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0"
                    onClick={() => setIsOpen(false)}
                  >
                    Cancel
                  </button>""",
    button_code
)

# And make the grid 3 columns? Or just leave it flow row dense
content = content.replace(
    'sm:grid-cols-2',
    'sm:grid-cols-3'
)
content = content.replace(
    'sm:col-start-2',
    'sm:col-start-3'
)

with open('frontend/src/components/PaymentModal.tsx', 'w') as f:
    f.write(content)
