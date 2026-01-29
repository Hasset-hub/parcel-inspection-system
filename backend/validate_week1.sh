#!/bin/bash

echo "========================================"
echo "  WEEK 1 COMPLETION VALIDATION"
echo "========================================"
echo ""

# 1. PostgreSQL
echo "1. PostgreSQL Service:"
if pg_isready -q; then
    echo "   ✅ PostgreSQL is running and accepting connections"
else
    echo "   ❌ PostgreSQL not responding"
    echo "   Trying to start..."
    sudo systemctl start postgresql
    sleep 2
    pg_isready -q && echo "   ✅ Started successfully" || echo "   ❌ Failed to start"
fi
echo ""

# 2. Database & Tables
echo "2. Database Schema:"
if psql -h localhost -U parcel_admin -d parcel_system -c "\dt" 2>/dev/null | grep -q "users"; then
    TABLE_COUNT=$(psql -h localhost -U parcel_admin -d parcel_system -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" 2>/dev/null | tr -d ' ')
    echo "   ✅ Database exists with $TABLE_COUNT tables"
else
    echo "   ❌ Database or tables not found"
fi
echo ""

# 3. Python Environment
echo "3. Python Virtual Environment:"
if python --version 2>&1 | grep -q "3.11"; then
    echo "   ✅ Python 3.11 active in venv"
else
    echo "   ❌ Python 3.11 not found"
fi
echo ""

# 4. FastAPI Server
echo "4. FastAPI Server:"
if curl -s http://localhost:8000/health 2>/dev/null | grep -q "healthy"; then
    echo "   ✅ FastAPI server running and healthy"
else
    echo "   ⚠️  FastAPI server not running"
    echo "   Start with: uvicorn app.main:app --reload"
fi
echo ""

# 5. Authentication
echo "5. Authentication System:"
if command -v jq &> /dev/null; then
    RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=admin&password=Admin123!" 2>/dev/null)
    
    if echo "$RESPONSE" | jq -e '.access_token' > /dev/null 2>&1; then
        TOKEN=$(echo "$RESPONSE" | jq -r '.access_token')
        echo "   ✅ Login successful - JWT token generated"
        
        # Test protected endpoint
        USER_DATA=$(curl -s -X GET "http://localhost:8000/api/v1/auth/me" \
            -H "Authorization: Bearer $TOKEN" 2>/dev/null)
        
        if echo "$USER_DATA" | jq -e '.username' > /dev/null 2>&1; then
            USERNAME=$(echo "$USER_DATA" | jq -r '.username')
            ROLE=$(echo "$USER_DATA" | jq -r '.role')
            echo "   ✅ Protected endpoint works - User: $USERNAME, Role: $ROLE"
        else
            echo "   ⚠️  Protected endpoint failed"
        fi
    else
        echo "   ❌ Login failed: $RESPONSE"
    fi
else
    echo "   ⚠️  jq not installed (run: sudo apt install jq)"
fi
echo ""

# 6. Dependencies
echo "6. Key Python Dependencies:"
python -c "import fastapi; print('   ✅ FastAPI installed')" 2>/dev/null || echo "   ❌ FastAPI not found"
python -c "import sqlalchemy; print('   ✅ SQLAlchemy installed')" 2>/dev/null || echo "   ❌ SQLAlchemy not found"
python -c "import passlib; print('   ✅ Passlib installed')" 2>/dev/null || echo "   ❌ Passlib not found"
python -c "import jose; print('   ✅ python-jose installed')" 2>/dev/null || echo "   ❌ python-jose not found"
echo ""

# 7. Project Structure
echo "7. Project Structure:"
[ -d "app" ] && echo "   ✅ app/ directory exists" || echo "   ❌ app/ missing"
[ -f "app/main.py" ] && echo "   ✅ app/main.py exists" || echo "   ❌ main.py missing"
[ -f "app/core/security.py" ] && echo "   ✅ security.py exists" || echo "   ❌ security.py missing"
[ -f ".env" ] && echo "   ✅ .env file exists" || echo "   ⚠️  .env file missing"
echo ""

# Summary
echo "========================================"
echo "  WEEK 1 STATUS SUMMARY"
echo "========================================"
echo ""
echo "✅ = Working perfectly"
echo "⚠️  = Needs attention"
echo "❌ = Not working"
echo ""
echo "Next steps:"
echo "1. If FastAPI not running: uvicorn app.main:app --reload"
echo "2. If jq missing: sudo apt install jq"
echo "3. Test login: curl http://localhost:8000/docs"
echo ""
