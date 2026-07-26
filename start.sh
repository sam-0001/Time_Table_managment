#!/bin/bash

# Start Script for School Timetable Management System

echo "Starting Backend API..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
echo "Backend running on PID $BACKEND_PID"

echo "Starting Frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo "Frontend running on PID $FRONTEND_PID"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
