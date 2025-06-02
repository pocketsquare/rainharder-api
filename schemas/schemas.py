# schemas/schemas.py

from pydantic import BaseModel, EmailStr, Field, constr

# Explicit schema definition for email form data
class EmailForm(BaseModel):
    name: constr = Field(..., max_length=50)
    email: EmailStr
    subject: constr = Field(..., max_length=50)
    message: constr = Field(..., max_length=250)
