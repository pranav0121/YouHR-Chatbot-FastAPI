# YouHR Assistant - HR & Merchant Management System

A comprehensive FastAPI backend system providing both HR Assistant and Merchant Management capabilities through a unified chatbot interface.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Complete System

```bash
python start_comprehensive_system.py
```

This will:

- Create all database tables
- Seed menu data
- Seed sample data
- Start the FastAPI server at http://127.0.0.1:8000

## 🎯 System Overview

### Two Main Systems:

#### 1. **HR Assistant** 👥

- Employee management
- Attendance tracking
- Leave management
- Payroll information

#### 2. **Merchant Management** 🏪

- Sales analytics
- Staff management
- Marketing tools
- Financial tracking

## 📊 API Endpoints

### 🏠 Core Endpoints

- `GET /` - Main chat interface
- `GET /api/chatbot/company-info` - Company information
- `GET /api/chatbot/menus-with-submenus` - Dynamic menu system

### 👥 HR Assistant Endpoints

#### Attendance Management

- `GET /api/attendance/history` - Get attendance history
  - Parameters: `employee_id`, `days` (optional)

#### Leave Management

- `POST /api/leave/apply` - Apply for leave
- `GET /api/leave/applications` - Get leave applications
  - Parameters: `employee_id`

#### Payroll

- `GET /api/payroll/payslips` - Get payslips
  - Parameters: `employee_id`

#### Employee Information

- `GET /api/employee/status` - Get employee status
  - Parameters: `employee_id`

### 🏪 Merchant Management Endpoints

#### Sales Analytics

- `GET /api/merchant/sales/today` - Today's sales data
- `GET /api/merchant/sales/yesterday` - Yesterday's sales comparison
- `GET /api/merchant/sales/weekly` - Weekly sales report

#### Financial Management

- `GET /api/merchant/payments/outstanding` - Outstanding payments
- `GET /api/merchant/expenses/bills` - Expense and bill tracking

#### Staff Management

- `GET /api/merchant/staff/attendance` - Staff attendance overview
- `GET /api/merchant/staff/leave-requests` - Staff leave requests
- `GET /api/merchant/staff/messages` - Staff messages and announcements
- `POST /api/merchant/staff/add-employee` - Add new employee
- `GET /api/merchant/staff/salary` - Salary information
- `POST /api/merchant/staff/hr-support` - Submit HR support request

#### Marketing Tools

- `POST /api/merchant/marketing/whatsapp-campaign` - Create WhatsApp campaign
- `POST /api/merchant/marketing/instant-promotion` - Create instant promotion

## 🗄️ Database Schema

### Core Tables

- `chatbot_menus` - Menu structure
- `chatbot_submenus` - Submenu items
- `employees` - Employee master data

### HR Tables

- `attendance_records` - Daily attendance
- `leave_applications` - Leave requests
- `payslips` - Payroll information

### Merchant Tables

- `hr_support_tickets` - HR support requests
- `marketing_campaigns` - Marketing campaigns
- `promotions` - Sales promotions
- `sales_records` - Sales transactions
- `expense_records` - Business expenses
- `inventory_items` - Inventory management
- `customer_data` - Customer information
- `staff_messages` - Internal messaging
- `work_schedules` - Staff scheduling

## 📝 Request/Response Examples

### Apply for Leave

```bash
POST /api/leave/apply
Content-Type: application/json

{
  "employee_id": "EMP001",
  "employee_name": "John Doe",
  "leave_type": "Annual Leave",
  "from_date": "2024-09-10",
  "to_date": "2024-09-12",
  "reason": "Family vacation"
}
```

### Create WhatsApp Campaign

```bash
POST /api/merchant/marketing/whatsapp-campaign
Content-Type: application/json

{
  "campaign_name": "Weekend Special",
  "target_audience": "All Customers",
  "message_content": "Special 20% discount this weekend!",
  "budget": 1000
}
```

### Add New Employee

```bash
POST /api/merchant/staff/add-employee
Content-Type: application/json

{
  "employee_id": "EMP006",
  "employee_name": "Jane Smith",
  "email": "jane.smith@company.com",
  "department": "Sales",
  "position": "Sales Associate",
  "employment_type": "Full-time",
  "hire_date": "2024-09-01"
}
```

## 🛠️ Development

### Project Structure

```
app/
├── __init__.py
├── main.py          # FastAPI application and routes
├── models.py        # SQLAlchemy database models
├── schemas.py       # Pydantic request/response schemas
├── crud.py          # Database operations
└── database.py      # Database configuration

static/
├── chat.html        # Frontend interface
├── chat.css         # Styling
└── chat.js          # JavaScript functionality

scripts/
├── create_comprehensive_tables.py  # Create all tables
├── seed_merchant_menus.py          # Seed merchant menus
└── start_comprehensive_system.py   # Complete startup script
```

### Manual Setup

1. **Create Tables**

```bash
python create_comprehensive_tables.py
```

2. **Seed Menus**

```bash
python seed_merchant_menus.py
python seed_menus.py  # If exists
```

3. **Seed Sample Data**

```bash
python seed_employees.py
python seed_attendance.py
python seed_payslips.py
```

4. **Start Server**

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## 🔧 Configuration

### Environment Variables

- `DATABASE_URL` - Database connection string (defaults to SQLite)
- `CORS_ORIGINS` - Allowed CORS origins (defaults to all for development)

### Menu System Configuration

The system uses a dynamic menu structure that can be configured through the database:

- Company types: `pos_youhr` (HR), `merchant` (Merchant)
- Roles: `employee`, `admin`

## 📱 Frontend Features

### Chat Interface

- System selection (HR vs Merchant)
- Dynamic menu loading
- Interactive buttons
- Form handling for complex operations
- Real-time API communication

### Responsive Design

- Mobile-friendly interface
- Modern UI components
- Smooth animations
- Error handling

## 🔍 API Documentation

Once the server is running, visit:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 🚨 Error Handling

The API includes comprehensive error handling:

- HTTP 400 for bad requests
- HTTP 404 for not found resources
- HTTP 500 for server errors
- Detailed error messages in responses

## 🔒 Security Features

- CORS protection
- Input validation using Pydantic
- SQL injection protection via SQLAlchemy
- Error message sanitization

## 📈 Performance

- Optimized database queries
- Efficient API endpoints
- Minimal frontend JavaScript
- Fast response times

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

**Built with ❤️ using FastAPI, SQLAlchemy, and modern web technologies.**
