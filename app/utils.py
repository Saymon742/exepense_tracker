import hashlib
import hmac
import base64
import json
import csv
import io
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from typing import List, Tuple, Any

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password, hashed_password):
    salt = hashed_password[:32]
    stored_hash = hashed_password[32:]
    new_hash = hashlib.sha256((salt + plain_password).encode()).hexdigest()
    return new_hash == stored_hash

def get_password_hash(password):
    import secrets
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return salt + hashed

def create_access_token(data: dict):
    header = {"alg": "HS256", "typ": "JWT"}
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expire.timestamp()})
    
    header_encoded = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
    payload_encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
    
    signature = hmac.new(SECRET_KEY.encode(), f"{header_encoded}.{payload_encoded}".encode(), hashlib.sha256).digest()
    signature_encoded = base64.urlsafe_b64encode(signature).decode().rstrip('=')
    
    return f"{header_encoded}.{payload_encoded}.{signature_encoded}"

def verify_token(token: str):
    try:
        parts = token.split('.')
        if len(parts) != 3:
            raise HTTPException(status_code=401, detail="Invalid token format")
        
        header_encoded, payload_encoded, signature_encoded = parts
        
        expected_signature = hmac.new(SECRET_KEY.encode(), f"{header_encoded}.{payload_encoded}".encode(), hashlib.sha256).digest()
        expected_signature_encoded = base64.urlsafe_b64encode(expected_signature).decode().rstrip('=')
        
        if not hmac.compare_digest(signature_encoded, expected_signature_encoded):
            raise HTTPException(status_code=401, detail="Invalid token signature")
        
        payload_json = base64.urlsafe_b64decode(payload_encoded + '===').decode()
        payload = json.loads(payload_json)
        
        if payload.get("exp", 0) < datetime.utcnow().timestamp():
            raise HTTPException(status_code=401, detail="Token expired")
        
        return payload
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def generate_expense_chart(summary: List[Tuple]) -> dict:
    categories = []
    amounts = []
    
    for item in summary:
        categories.append(str(item[0]))
        amounts.append(float(item[1]))
    
    chart_data = {
        "labels": categories,
        "datasets": [
            {
                "data": amounts,
                "backgroundColor": [
                    "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", 
                    "#9966FF", "#FF9F40", "#FF6384", "#C9CBCF"
                ][:len(categories)],
                "hoverBackgroundColor": [
                    "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", 
                    "#9966FF", "#FF9F40", "#FF6384", "#C9CBCF"
                ][:len(categories)]
            }
        ]
    }
    return chart_data

def generate_csv_report(summary: List[Tuple]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["Category", "Total Amount", "Count"])
    for item in summary:
        writer.writerow([str(item[0]), float(item[1]), int(item[2])])
    
    return output.getvalue()