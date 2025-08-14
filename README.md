# 💼 YouHR Assistant - Employee Portal Chatbot

## 🌟 Project Overview

YouHR Assistant is a modern, interactive chatbot system designed to streamline HR operations for employees. Built with FastAPI backend and vanilla JavaScript frontend, it provides a user-friendly interface for common HR tasks like viewing attendance, applying for leave, checking payslips, and accessing employment information.

## 🎨 Design Theme

The application follows the **YouShop design aesthetic** with:

- 🎯 **Teal/Green Color Scheme** (`#0f9b8e`, `#16a085`, `#1abc9c`)
- ✨ **Modern Gradient Design**
- 🔄 **Smooth Animations & Transitions**
- 📱 **Responsive Layout**
- 💎 **Professional Corporate Look**

---

## 🏗️ Project Architecture

### Backend (FastAPI)

```
app/
├── __init__.py          # Package initialization
├── main.py             # FastAPI application & API endpoints
├── models.py           # SQLAlchemy database models
├── schemas.py          # Pydantic data validation schemas
├── database.py         # Database configuration & session management
└── crud.py            # Database operations (Create, Read, Update, Delete)
```

### Frontend (Vanilla JavaScript)

```
static/
├── chat.html          # Main HTML interface
├── chat.css           # YouShop-themed styling
└── chat.js            # Interactive chatbot logic
```

### Database & Seeding

```
├── chatbot.db         # SQLite database file
├── seed_attendance.py # Sample attendance data
├── seed_employees.py  # Employee records
├── seed_payslips.py   # Payroll data
└── seed_menus.py      # Chatbot menu structure
```

---

## 📊 Database Schema

### 🗂️ Tables Created

#### 1. **ChatbotMenu** - Main menu categories

```sql
- id (Primary Key)
- company_type (pos_youhr)
- role (employee)
- menu_name (e.g., "Leave Management", "Payroll")
- menu_icon
- created_at
```

#### 2. **ChatbotSubmenu** - Sub-options for each menu

```sql
- id (Primary Key)
- menu_id (Foreign Key)
- submenu_name (e.g., "Apply for new leave", "View payslips")
- submenu_icon
- created_at
```

#### 3. **AttendanceRecord** - Employee attendance tracking

```sql
- id (Primary Key)
- employee_id
- employee_name
- date
- check_in_time
- check_out_time
- working_hours
- status (Present/Late/Absent)
- location
- created_at
```

#### 4. **LeaveApplication** - Leave requests management

```sql
- id (Primary Key)
- employee_id
- employee_name
- leave_type (Annual/Sick/Personal/Emergency)
- from_date
- to_date
- total_days
- reason
- status (Pending/Approved/Rejected)
- created_at
```

#### 5. **Payslip** - Salary information

```sql
- id (Primary Key)
- employee_id
- employee_name
- pay_period
- basic_salary
- allowances
- gross_salary
- deductions
- net_salary
- pay_period_start
- pay_period_end
- status (Processed/Pending)
- download_url
- created_at
```

#### 6. **Employee** - Employee master data

```sql
- id (Primary Key)
- employee_id (Unique)
- employee_name
- email
- phone
- department
- position
- employment_type (Full-time/Part-time/Contract)
- employment_status (Active/Inactive/Terminated)
- hire_date
- reporting_manager
- office_location
- salary_grade
- probation_end_date
- last_promotion_date
- created_at
```

---

## 🚀 API Endpoints

### 📋 Menu & Navigation

| Method | Endpoint                           | Description          |
| ------ | ---------------------------------- | -------------------- |
| `GET`  | `/api/chatbot/menus-with-submenus` | Fetch menu structure |

### 👥 Attendance Management

| Method | Endpoint                  | Description            |
| ------ | ------------------------- | ---------------------- |
| `GET`  | `/api/attendance/history` | Get attendance records |

### 🏖️ Leave Management

| Method | Endpoint           | Description              |
| ------ | ------------------ | ------------------------ |
| `POST` | `/api/leave/apply` | Submit leave application |

### 💰 Payroll System

| Method | Endpoint                | Description           |
| ------ | ----------------------- | --------------------- |
| `GET`  | `/api/payroll/payslips` | Get employee payslips |

### 👤 Employee Information

| Method | Endpoint               | Description            |
| ------ | ---------------------- | ---------------------- |
| `GET`  | `/api/employee/status` | Get employment details |

### 📁 Static Files

| Method | Endpoint              | Description               |
| ------ | --------------------- | ------------------------- |
| `GET`  | `/static/{file_path}` | Serve CSS, JS, HTML files |

---

## ✨ Key Features Implemented

### 🎯 **Core Functionality**

#### 1. **📊 Attendance History Viewer**

- **What it does:** Shows employee attendance records with check-in/out times
- **Data shown:** 22 sample attendance records with working hours, status, and location
- **API:** `GET /api/attendance/history?employee_id=EMP001&days=30`

#### 2. **📝 Interactive Leave Application Form**

- **What it does:** Allows employees to apply for different types of leave
- **Features:** Date picker, leave type selection, reason input, automatic day calculation
- **API:** `POST /api/leave/apply`
- **Leave Types:** Annual, Sick, Personal, Emergency

#### 3. **💳 Payslip Management**

- **What it does:** Displays salary breakdown with download options
- **Data shown:** 6 months of payslip data with salary components
- **Features:** PDF download simulation, salary breakdown display
- **API:** `GET /api/payroll/payslips?employee_id=EMP001`

#### 4. **👥 Employment Status Dashboard**

- **What it does:** Shows comprehensive employee information
- **Data shown:** Personal details, job information, manager details, probation status
- **API:** `GET /api/employee/status?employee_id=EMP001`

### 🔧 **Technical Features**

#### 1. **Smart Default Handler**

- **Problem Solved:** Eliminated generic "Request Processed Successfully" messages
- **Solution:** Intelligent option detection that routes to appropriate API calls
- **Implementation:** Uses string matching to detect user intent

#### 2. **Async/Await Pattern**

- **Problem Solved:** Fixed `[object Promise]` display issues
- **Solution:** Proper Promise handling with async/await
- **Impact:** All API calls now display real data instead of Promise objects

#### 3. **Cache-Busting System**

- **Problem Solved:** Browser caching preventing JavaScript updates
- **Solution:** Version parameters in script tags (`?v=VERSION_NUMBER`)
- **Implementation:** `NoCacheStaticFiles` class with no-cache headers

#### 4. **YouShop Theme Integration**

- **Design Update:** Complete visual overhaul to match YouShop aesthetic
- **Colors:** Teal/green gradient color scheme
- **UI Elements:** All buttons, gradients, and interactions themed consistently

---

## 📁 File Changes Made

### 🆕 **New Files Created**

#### Database Seeding Scripts

- `seed_attendance.py` - Creates 22 sample attendance records
- `seed_employees.py` - Creates 5 employee profiles
- `seed_payslips.py` - Creates 6 months of payslip data
- `seed_menus.py` - Sets up chatbot menu structure

#### Documentation

- `README.md` - This comprehensive project documentation

### 🔄 **Modified Files**

#### Backend Changes

- **`app/models.py`** - Added 4 new database models (AttendanceRecord, LeaveApplication, Payslip, Employee)
- **`app/main.py`** - Added 5 new API endpoints with full CRUD operations
- **`app/schemas.py`** - Added Pydantic validation schemas for API requests

#### Frontend Changes

- **`static/chat.html`** - Updated title and theme branding
- **`static/chat.css`** - Complete YouShop theme implementation
- **`static/chat.js`** - Added 4 new feature functions with async/await support

---

## 🎯 Sample Data Overview

### 👥 **Employee Records (5 employees)**

- EMP001: John Smith (HR Specialist)
- EMP002: Jane Doe (Software Developer)
- EMP003: Alice Johnson (Marketing Coordinator)
- EMP004: Robert Wilson (Financial Analyst)
- EMP005: Lisa Brown (Sales Representative)

### 📊 **Attendance Data (22 records)**

- Date range: Recent 30 days
- Status types: Present, Late, Absent
- Working hours: 6-9 hours per day
- Locations: Office, Remote, Client Site

### 💰 **Payslip Data (6 months)**

- Pay periods: Feb 2024 - Jul 2024
- Salary components: Basic, Allowances, Deductions, Net
- All records marked as "Processed"
- Download URLs for PDF access

---

## 🚀 How to Run the Project

### 1. **Install Dependencies**

```bash
pip install fastapi uvicorn sqlalchemy pydantic
```

### 2. **Seed the Database**

```bash
python seed_menus.py
python seed_attendance.py
python seed_employees.py
python seed_payslips.py
```

### 3. **Start the Server**

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 4. **Access the Application**

- Open browser: `http://127.0.0.1:8000/static/chat.html`
- Interact with the YouHR Assistant chatbot

---

## 🔍 User Journey

### **Step 1: Welcome Screen**

User sees the YouHR Assistant with teal-themed interface and menu options

### **Step 2: Menu Selection**

Choose from 4 main categories:

- 📊 Attendance Management
- 🏖️ Leave Management
- 💰 Payroll Information
- 👥 Employee Information

### **Step 3: Feature Interaction**

- **Attendance:** View detailed attendance history with charts
- **Leave:** Fill interactive form with date pickers
- **Payroll:** Browse payslips with download options
- **Employee:** View comprehensive employment dashboard

### **Step 4: Data Display**

All features show real data from the database with professional formatting

---

## 🎨 Design Highlights

### **Color Palette**

- **Primary:** `#0f9b8e` (Teal)
- **Secondary:** `#16a085` (Medium Teal)
- **Accent:** `#1abc9c` (Light Teal)
- **Success:** `#28a745` (Green)
- **Warning:** `#ffc107` (Amber)

### **Typography**

- **Font:** Inter (Google Fonts)
- **Weights:** 300, 400, 500, 600, 700, 800
- **Clean, modern, professional appearance**

### **Animations**

- **Smooth transitions:** 0.3s cubic-bezier easing
- **Hover effects:** Scale, translate, and color transitions
- **Loading states:** Typing indicators and pulse animations

---

## 🛠️ Technical Stack

### **Backend**

- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Data validation and settings management
- **SQLite** - Lightweight database for development

### **Frontend**

- **Vanilla JavaScript** - No framework dependencies
- **CSS3** - Modern styling with gradients and animations
- **HTML5** - Semantic markup structure

### **Development Tools**

- **Uvicorn** - ASGI server for FastAPI
- **VS Code** - Primary development environment
- **Git** - Version control system

---

## 🔮 Future Enhancements

### **Potential Features**

- 🔐 Authentication & Authorization
- 📧 Email Notifications
- 📊 Advanced Analytics Dashboard
- 📱 Mobile App Version
- 🌐 Multi-language Support
- 🔔 Real-time Notifications
- 📋 Performance Reviews Module
- 🎯 Goal Setting & Tracking

### **Technical Improvements**

- 🗄️ PostgreSQL Migration
- 🔄 Redis Caching
- 📦 Docker Containerization
- ☁️ Cloud Deployment
- 🧪 Automated Testing Suite
- 📝 API Documentation (Swagger)

---

## 👥 Project Impact

### **For Employees**

- ⚡ Quick access to HR information
- 📱 Mobile-friendly interface
- 🎯 Intuitive user experience
- 📊 Real-time data visibility

### **For HR Department**

- 🔄 Automated request processing
- 📈 Better data organization
- ⏰ Time-saving operations
- 📊 Comprehensive reporting

### **For Organization**

- 💰 Reduced administrative costs
- 📈 Improved efficiency
- 😊 Enhanced employee satisfaction
- 🔍 Better data insights

---

**Built using FastAPI, JavaScript, and YouShop design principles**

_YouHR Assistant - Making HR interactions simple, efficient, and beautiful._
