import sys

def patch():
    with open('app/db/models.py', 'r') as f:
        content = f.read()

    new_model = """
class Payment(Base):
    __tablename__ = "payments"
    order_id = Column(String, primary_key=True)
    school_id = Column(String, ForeignKey("schools.id", ondelete="CASCADE"))
    amount = Column(Float, nullable=False)
    status = Column(String, default="PENDING")
    created_at = Column(DateTime, default=datetime.utcnow)
"""
    if "class Payment" not in content:
        content += new_model
        with open('app/db/models.py', 'w') as f:
            f.write(content)

patch()
