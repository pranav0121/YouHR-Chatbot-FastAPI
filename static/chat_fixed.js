let categories = [];
let currentSystem = "hr"; // "hr", "merchant", or "retention_executor"

// Fetch categories from API
async function fetchCategories(companyType = "pos_youhr", role = "employee") {
    try {
        let url = `http://127.0.0.1:8000/api/menu/${companyType}`;
        if (role && role !== "employee") {
            url += `?role=${role}`;
        }
        const response = await fetch(url);
        if (!response.ok) throw new Error("Failed to fetch menu data");
        const data = await response.json();
        
        // Handle both direct array and nested data structures
        let menuData = [];
        if (Array.isArray(data)) {
            menuData = data;
        } else if (data.data && Array.isArray(data.data)) {
            menuData = data.data;
        } else if (data.menus && Array.isArray(data.menus)) {
            menuData = data.menus;
        }
        
        // Process menu data
        categories = menuData.map(menu => ({
            key: menu.menu_key || menu.key || menu.name,
            label: menu.menu_title || menu.label || menu.name,
            icon: menu.menu_icon || "",
            color: menu.color || "#4F46E5",
            options: (menu.submenus || []).map(sub => sub.submenu_title || sub.label || sub.name || sub)
        }));
        
    } catch (e) {
        categories = [];
        console.error("Error fetching categories:", e);
    }
}

// Switch between systems
async function switchSystem(system) {
    currentSystem = system;
    if (system === "hr") {
        await fetchCategories("pos_youhr", "employee");
    } else if (system === "merchant") {
        await fetchCategories("merchant", "admin");
    } else if (system === "retention_executor") {
        await fetchCategories("icp_hr", "retention_executor");
    }
}

// Sound effects
const playSound = (type) => {
    try {
        const audio = new Audio();
        switch(type) {
            case 'click':
                audio.src = 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmMcBjiS2PHKYS0E';
                break;
            case 'message':
                audio.src = 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmMcBjiS2PHKYS0E';
                break;
        }
        audio.volume = 0.1;
        audio.play().catch(() => {});
    } catch (e) {
        // Ignore audio errors
    }
};

class ChatBot {
    constructor() {
        this.chatBody = document.querySelector('.chat-body');
        this.currentTypingIndicator = null;
        this.isInitialized = false;
        this.init();
    }

    async init() {
        if (this.isInitialized) return;
        this.isInitialized = true;

        // Add event listeners
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.resetToMainMenu();
            }
        });

        // Fetch categories and show welcome
        await fetchCategories();
        setTimeout(() => {
            this.showWelcomeMessage();
        }, 500);
    }

    resetToMainMenu() {
        this.chatBody.innerHTML = '';
        setTimeout(() => {
            this.showWelcomeMessage();
        }, 300);
    }

    autoScroll() {
        this.chatBody.scrollTop = this.chatBody.scrollHeight;
    }

    showTypingIndicator() {
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'chat-bubble bot typing-indicator';
        typingIndicator.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
        this.chatBody.appendChild(typingIndicator);
        this.autoScroll();
        this.currentTypingIndicator = typingIndicator;
        return typingIndicator;
    }

    removeTypingIndicator() {
        if (this.currentTypingIndicator) {
            this.currentTypingIndicator.remove();
            this.currentTypingIndicator = null;
        }
    }

    addBotMessage(message, delay = 1000, isHTML = false) {
        const typingIndicator = this.showTypingIndicator();
        
        setTimeout(() => {
            this.removeTypingIndicator();
            
            const botBubble = document.createElement('div');
            botBubble.className = 'chat-bubble bot';
            
            if (isHTML) {
                botBubble.innerHTML = message;
            } else {
                botBubble.textContent = message;
            }
            
            this.chatBody.appendChild(botBubble);
            this.autoScroll();
            playSound('message');
        }, delay);
    }

    addUserMessage(message) {
        const userBubble = document.createElement('div');
        userBubble.className = 'chat-bubble user';
        userBubble.textContent = message;
        this.chatBody.appendChild(userBubble);
        this.autoScroll();
        playSound('click');
    }

    showWelcomeMessage() {
        this.chatBody.innerHTML = '';
        
        setTimeout(() => {
            this.addBotMessage('Hi there! 👋\nWelcome to YouHR Management Assistant!\n\nPlease select a system:', 500);
            
            setTimeout(() => {
                this.showSystemSelection();
            }, 2200);
        }, 300);
    }

    showSystemSelection() {
        const systemContainer = document.createElement('div');
        systemContainer.className = 'categories-container';
        systemContainer.style.opacity = '0';
        systemContainer.style.transform = 'translateY(20px)';

        const systems = [
            { key: 'hr', label: 'HR Assistant', icon: '👥', description: 'Employee management, attendance, payroll' },
            { key: 'merchant', label: 'Merchant Management', icon: '🏪', description: 'Sales, staff, payments, marketing' },
            { key: 'retention_executor', label: 'Retention Executor', icon: '🎯', description: 'Merchant follow-up, daily activities, support' }
        ];

        systems.forEach((system, index) => {
            const systemCard = document.createElement('div');
            systemCard.className = 'category-card';
            systemCard.innerHTML = `
                <div class="category-header">
                    <span class="category-icon">${system.icon}</span>
                    <h3>${system.label}</h3>
                </div>
                <p class="category-description">${system.description}</p>
            `;

            systemCard.addEventListener('click', async () => {
                this.addUserMessage(`Selected: ${system.label}`);
                await switchSystem(system.key);
                
                setTimeout(() => {
                    this.addBotMessage(`Great! You've selected ${system.label}. Loading available options...`, 800);
                    
                    setTimeout(() => {
                        this.showCategories();
                    }, 1500);
                }, 500);
            });

            systemContainer.appendChild(systemCard);
        });

        this.chatBody.appendChild(systemContainer);

        // Animate in
        setTimeout(() => {
            systemContainer.style.transition = 'all 0.5s ease';
            systemContainer.style.opacity = '1';
            systemContainer.style.transform = 'translateY(0)';
        }, 100);

        this.autoScroll();
    }

    showCategories() {
        if (categories.length === 0) {
            this.addBotMessage('No categories available for this system.', 500);
            return;
        }

        const categoriesContainer = document.createElement('div');
        categoriesContainer.className = 'categories-container';
        categoriesContainer.style.opacity = '0';
        categoriesContainer.style.transform = 'translateY(20px)';

        categories.forEach((category, index) => {
            const categoryCard = document.createElement('div');
            categoryCard.className = 'category-card';
            categoryCard.innerHTML = `
                <div class="category-header">
                    <span class="category-icon">${category.icon}</span>
                    <h3>${category.label}</h3>
                </div>
                <p class="category-description">${category.options.length} options available</p>
            `;

            categoryCard.addEventListener('click', () => {
                this.addUserMessage(category.label);
                setTimeout(() => {
                    this.showOptions(category);
                }, 500);
            });

            categoriesContainer.appendChild(categoryCard);
        });

        this.chatBody.appendChild(categoriesContainer);

        // Animate in
        setTimeout(() => {
            categoriesContainer.style.transition = 'all 0.5s ease';
            categoriesContainer.style.opacity = '1';
            categoriesContainer.style.transform = 'translateY(0)';
        }, 100);

        this.autoScroll();
    }

    showOptions(category) {
        if (!category.options || category.options.length === 0) {
            this.addBotMessage('No options available for this category.', 500);
            return;
        }

        const optionsContainer = document.createElement('div');
        optionsContainer.className = 'options-container';
        optionsContainer.style.opacity = '0';
        optionsContainer.style.transform = 'translateY(20px)';

        category.options.forEach((option, index) => {
            const optionCard = document.createElement('div');
            optionCard.className = 'option-card';
            optionCard.innerHTML = `
                <span class="option-text">${option}</span>
                <span class="option-arrow">→</span>
            `;

            optionCard.addEventListener('click', async () => {
                this.addUserMessage(option);
                
                setTimeout(async () => {
                    this.addBotMessage('Processing your request...', 800);
                    
                    setTimeout(async () => {
                        await this.handleOptionSelection(option, category);
                    }, 1500);
                }, 500);
            });

            optionsContainer.appendChild(optionCard);
        });

        this.chatBody.appendChild(optionsContainer);

        // Animate in
        setTimeout(() => {
            optionsContainer.style.transition = 'all 0.5s ease';
            optionsContainer.style.opacity = '1';
            optionsContainer.style.transform = 'translateY(0)';
        }, 100);

        this.autoScroll();
    }

    async handleOptionSelection(option, category) {
        try {
            let result = '';
            
            // Handle different options based on current system
            if (currentSystem === "merchant") {
                result = await this.handleMerchantOption(option);
            } else if (currentSystem === "retention_executor") {
                result = await this.handleRetentionExecutorOption(option);
            } else {
                result = await this.handleHROption(option);
            }
            
            this.addBotMessage(result, 800, true);
            
        } catch (error) {
            this.addBotMessage(`❌ Sorry, there was an error processing your request: ${error.message}`, 800);
        }
    }

    async handleMerchantOption(option) {
    const merchantId = (window && window.DEMO_MERCHANT_ID) ? window.DEMO_MERCHANT_ID : 'MERCH123';
        
        switch(option) {
            case "View Yesterday's Sales":
                return await this.fetchYesterdaysSales(merchantId);
            case "View Outstanding Payments":
                return await this.fetchOutstandingPayments(merchantId);
            case "View Expenses & Bills":
                return await this.fetchExpensesBills(merchantId);
            case "View Staff Attendance":
                return await this.fetchStaffAttendance(merchantId);
            case "View Leave Requests":
                return await this.fetchStaffLeaveRequests(merchantId);
            case "View Staff Messages":
                return await this.fetchStaffMessages(merchantId);
            case "View Salary Information":
                return await this.fetchSalarySummary(merchantId);
            case "View Campaign Results":
                return await this.fetchMarketingCampaignResults(merchantId);
            case "View Loan Status":
                return await this.fetchLoanStatus(merchantId);
            default:
                return `Selected: ${option}. This feature is being processed...`;
        }
    }

    async handleRetentionExecutorOption(option) {
        switch(option) {
            case "View Assigned Merchants":
                return await this.fetchAssignedMerchants();
            case "View Today's Tasks":
                return await this.fetchTodaysTasks();
            case "View Follow-up Reminders":
                return await this.fetchFollowupReminders();
            case "View Pending Actions":
                return await this.fetchPendingActions();
            case "Check Pending Documents":
                return await this.fetchPendingDocuments();
            default:
                return `Selected: ${option}. This feature is being processed...`;
        }
    }

    async handleHROption(option) {
        switch(option) {
            case "Attendance & Time Management":
                return await this.fetchAttendanceHistory();
            case "Leave Management":
                return "Leave management options will be displayed here.";
            case "Payroll":
                return await this.fetchPayslips();
            case "Employee Information":
                return await this.fetchEmployeeStatus();
            default:
                return `Selected: ${option}. This feature is being processed...`;
        }
    }

    // Merchant Management API calls
    async fetchYesterdaysSales(merchantId) {
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/merchant/sales/yesterday?merchant_id=${merchantId}`);
            if (!response.ok) throw new Error('Failed to fetch sales data');
            const data = await response.json();
            const salesData = data.data;
            
            return `
                <div style="background: linear-gradient(135deg, #0f9b8e 0%, #16a085 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 16px;">
                    <h3 style="margin: 0 0 12px 0;">📈 Yesterday's Sales - ${salesData.date}</h3>
                </div>
                <div style="display: grid; gap: 12px; margin-bottom: 16px;">
                    <div style="background: #f8f9fa; color: #000; padding: 16px; border-radius: 8px; border-left: 4px solid #007bff;">
                        <strong>💰 Total Sales:</strong> ₹${salesData.total_sales.toLocaleString()}<br>
                        <strong>🛒 Transactions:</strong> ${salesData.total_transactions}
                    </div>
                    <div style="background: #e8f5e8; color: #000; padding: 12px; border-radius: 8px; border-left: 4px solid #28a745;">
                        <strong>🏆 Top Products:</strong><br>
                        ${salesData.top_products.map(product => `• ${product.name}: ₹${product.sales.toLocaleString()}`).join('<br>')}
                    </div>
                </div>
            `;
        } catch (error) {
            return `<div style="color: #dc3545;">❌ Error loading sales data: ${error.message}</div>`;
        }
    }

    async fetchOutstandingPayments(merchantId) {
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/merchant/payments/outstanding?merchant_id=${merchantId}`);
            if (!response.ok) throw new Error('Failed to fetch payment data');
            const data = await response.json();
            const paymentData = data.data;
            
            return `
                <div style="background: linear-gradient(135deg, #0f9b8e 0%, #16a085 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 16px;">
                    <h3 style="margin: 0 0 12px 0;">💳 Outstanding Payments</h3>
                </div>
                <div style="display: grid; gap: 12px; margin-bottom: 16px;">
                    <div style="background: #fff3cd; color: #000; padding: 16px; border-radius: 8px; border-left: 4px solid #ffc107;">
                        <strong>⚠️ Total Outstanding:</strong> ₹${paymentData.total_outstanding.toLocaleString()}<br>
                        <strong>📋 Number of Payments:</strong> ${paymentData.payments.length}
                    </div>
                    ${paymentData.payments.map(payment => `
                        <div style="background: #f8f9fa; color: #000; padding: 12px; border-radius: 8px; border-left: 4px solid ${payment.status === 'Overdue' ? '#dc3545' : '#007bff'};">
                            <strong>Payment ID:</strong> ${payment.payment_id}<br>
                            <strong>Amount:</strong> ₹${payment.amount.toLocaleString()}<br>
                            <strong>Due Date:</strong> ${payment.due_date}<br>
                            <strong>Status:</strong> <span style="color: ${payment.status === 'Overdue' ? '#dc3545' : '#007bff'};">${payment.status}</span>
                        </div>
                    `).join('')}
                </div>
            `;
        } catch (error) {
            return `<div style="color: #dc3545;">❌ Error loading payment data: ${error.message}</div>`;
        }
    }

    async fetchExpensesBills(merchantId) {
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/merchant/expenses/bills?merchant_id=${merchantId}`);
            if (!response.ok) throw new Error('Failed to fetch expense data');
            const data = await response.json();
            const expenseData = data.data;
            
            return `
                <div style="background: linear-gradient(135deg, #0f9b8e 0%, #16a085 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 16px;">
                    <h3 style="margin: 0 0 12px 0;">💰 Expenses & Bills</h3>
                </div>
                <div style="display: grid; gap: 12px; margin-bottom: 16px;">
                    <div style="background: #f8f9fa; color: #000; padding: 16px; border-radius: 8px; border-left: 4px solid #e74c3c;">
                        <strong>📊 Total Expenses:</strong> ₹${expenseData.total_expenses.toLocaleString()}<br>
                        <strong>📋 Number of Bills:</strong> ${expenseData.bills.length}
                    </div>
                    ${expenseData.bills.map(bill => `
                        <div style="background: #f8f9fa; color: #000; padding: 12px; border-radius: 8px; border-left: 4px solid ${bill.status === 'Overdue' ? '#dc3545' : bill.status === 'Paid' ? '#28a745' : '#ffc107'};">
                            <strong>Bill ID:</strong> ${bill.bill_id}<br>
                            <strong>Description:</strong> ${bill.description}<br>
                            <strong>Amount:</strong> ₹${bill.amount.toLocaleString()}<br>
                            <strong>Due Date:</strong> ${bill.due_date}<br>
                            <strong>Status:</strong> <span style="color: ${bill.status === 'Overdue' ? '#dc3545' : bill.status === 'Paid' ? '#28a745' : '#ffc107'};">${bill.status}</span>
                        </div>
                    `).join('')}
                </div>
            `;
        } catch (error) {
            return `<div style="color: #dc3545;">❌ Error loading expense data: ${error.message}</div>`;
        }
    }

    async fetchStaffAttendance(merchantId) {
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/merchant/staff/attendance?merchant_id=${merchantId}`);
            if (!response.ok) throw new Error('Failed to fetch attendance data');
            const data = await response.json();
            const attendanceData = data.data;
            
            return `
                <div style="background: #ffffff; color: #000000; padding: 16px; border-radius: 12px; margin-bottom: 16px; border: 1px solid #ddd;">
                    <h3 style="margin: 0 0 12px 0;">👥 Staff Attendance - ${attendanceData.date}</h3>
                </div>
                <div style="display: grid; gap: 12px; margin-bottom: 16px;">
                    <div style="background: #ffffff; color: #000000; padding: 16px; border-radius: 8px; border-left: 4px solid #28a745;">
                        <strong>📊 Today's Summary:</strong><br>
                        Total Staff: ${attendanceData.staff.length}<br>
                        Present: ${attendanceData.staff.filter(s => s.status === 'Present').length}<br>
                        Absent/Late: ${attendanceData.staff.filter(s => s.status !== 'Present').length}
                    </div>
                    ${attendanceData.staff.map(staff => `
                        <div style="background: #ffffff; color: #000000; padding: 12px; border-radius: 8px; border-left: 4px solid ${staff.status === 'Present' ? '#28a745' : '#dc3545'}; border: 1px solid #ddd;">
                            <strong>${staff.name}</strong> (${staff.employee_id})<br>
                            <strong>Role:</strong> ${staff.role}<br>
                            <strong>Status:</strong> <span style="color: ${staff.status === 'Present' ? '#28a745' : '#dc3545'};">${staff.status}</span><br>
                            ${staff.check_in ? `<strong>Check-in:</strong> ${staff.check_in}` : ''}
                        </div>
                    `).join('')}
                </div>
            `;
        } catch (error) {
            return `<div style="color: #dc3545;">❌ Error loading attendance data: ${error.message}</div>`;
        }
    }

    async fetchStaffLeaveRequests(merchantId) {
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/merchant/staff/leave-requests?merchant_id=${merchantId}`);
            if (!response.ok) throw new Error('Failed to fetch leave data');
            const data = await response.json();
            const leaveData = data.data;
            
            return `
                <div style="background: linear-gradient(135deg, #0f9b8e 0%, #16a085 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 16px;">
                    <h3 style="margin: 0 0 12px 0;">🏖️ Staff Leave Requests</h3>
                </div>
                <div style="display: grid; gap: 12px; margin-bottom: 16px;">
                    <div style="background: #f8f9fa; color: #000; padding: 16px; border-radius: 8px; border-left: 4px solid #ffc107;">
                        <strong>📊 Summary:</strong><br>
                        Total Requests: ${leaveData.requests.length}<br>
                        Pending: ${leaveData.requests.filter(r => r.status === 'Pending').length}<br>
                        Approved: ${leaveData.requests.filter(r => r.status === 'Approved').length}
                    </div>
                    ${leaveData.requests.map(request => `
                        <div style="background: #f8f9fa; color: #000; padding: 12px; border-radius: 8px; border-left: 4px solid ${request.status === 'Approved' ? '#28a745' : request.status === 'Rejected' ? '#dc3545' : '#ffc107'};">
                            <strong>Request ID:</strong> ${request.request_id}<br>
                            <strong>Employee:</strong> ${request.employee_name}<br>
                            <strong>Type:</strong> ${request.leave_type}<br>
                            <strong>Period:</strong> ${request.from_date} to ${request.to_date}<br>
                            <strong>Status:</strong> <span style="color: ${request.status === 'Approved' ? '#28a745' : request.status === 'Rejected' ? '#dc3545' : '#ffc107'};">${request.status}</span><br>
                            <strong>Reason:</strong> ${request.reason}
                        </div>
                    `).join('')}
                </div>
            `;
        } catch (error) {
            return `<div style="color: #dc3545;">❌ Error loading leave data: ${error.message}</div>`;
        }
    }

    async fetchStaffMessages(merchantId) {
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/merchant/staff/messages?merchant_id=${merchantId}`);
            if (!response.ok) throw new Error('Failed to fetch messages');
            const data = await response.json();
            const messageData = data.data;
            
            return `
                <div style="background: linear-gradient(135deg, #0f9b8e 0%, #16a085 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 16px;">
                    <h3 style="margin: 0 0 12px 0;">💬 Staff Messages</h3>
                </div>
                <div style="display: grid; gap: 12px; margin-bottom: 16px;">
                    <div style="background: #f8f9fa; color: #000; padding: 16px; border-radius: 8px; border-left: 4px solid #007bff;">
                        <strong>📊 Summary:</strong><br>
                        Total Messages: ${messageData.messages.length}<br>
                        Unread: ${messageData.messages.filter(m => m.status === 'Unread').length}
                    </div>
                    ${messageData.messages.map(message => `
                        <div style="background: #f8f9fa; color: #000; padding: 12px; border-radius: 8px; border-left: 4px solid ${message.status === 'Unread' ? '#ffc107' : '#28a745'};">
                            <strong>From:</strong> ${message.from} (${message.role})<br>
                            <strong>Subject:</strong> ${message.subject}<br>
                            <strong>Message:</strong> ${message.message}<br>
                            <strong>Time:</strong> ${new Date(message.timestamp).toLocaleString()}<br>
                            <strong>Status:</strong> <span style="color: ${message.status === 'Unread' ? '#ffc107' : '#28a745'};">${message.status}</span>
                        </div>
                    `).join('')}
                </div>
            `;
        } catch (error) {
            return `<div style="color: #dc3545;">❌ Error loading messages: ${error.message}</div>`;
        }
    }

    async fetchSalarySummary(merchantId) {
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/merchant/staff/salary?merchant_id=${merchantId}`);
            if (!response.ok) throw new Error('Failed to fetch salary data');
            const data = await response.json();
            const salaryData = data.data;
            
            return `
                <div style="background: linear-gradient(135deg, #0f9b8e 0%, #16a085 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 16px;">
                    <h3 style="margin: 0 0 12px 0;">💰 Staff Salary Information</h3>
                </div>
                <div style="display: grid; gap: 12px; margin-bottom: 16px;">
                    ${salaryData.staff_salaries.map(salary => `
                        <div style="background: #f8f9fa; color: #000; padding: 12px; border-radius: 8px; border-left: 4px solid ${salary.status === 'Paid' ? '#28a745' : salary.status === 'Overdue' ? '#dc3545' : '#ffc107'};">
                            <strong>Employee:</strong> ${salary.name} (${salary.employee_id})<br>
                            <strong>Monthly Salary:</strong> ₹${salary.monthly_salary.toLocaleString()}<br>
                            <strong>Status:</strong> <span style="color: ${salary.status === 'Paid' ? '#28a745' : salary.status === 'Overdue' ? '#dc3545' : '#ffc107'};">${salary.status}</span><br>
                            <strong>Last Paid:</strong> ${salary.last_paid}
                        </div>
                    `).join('')}
                </div>
            `;
        } catch (error) {
            return `<div style="color: #dc3545;">❌ Error loading salary data: ${error.message}</div>`;
        }
    }

    async fetchMarketingCampaignResults(merchantId) {
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/merchant/marketing/campaign-results?merchant_id=${merchantId}`);
            if (!response.ok) throw new Error('Failed to fetch campaign data');
            const data = await response.json();
            const campaignData = data.data;
            
            return `
                <div style="background: linear-gradient(135deg, #0f9b8e 0%, #16a085 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 16px;">
                    <h3 style="margin: 0 0 12px 0;">📈 Marketing Campaign Results</h3>
                </div>
                <div style="display: grid; gap: 12px; margin-bottom: 16px;">
                    ${campaignData.campaigns.map(campaign => `
                        <div style="background: #f8f9fa; color: #000; padding: 12px; border-radius: 8px; border-left: 4px solid #007bff;">
                            <strong>Campaign ID:</strong> ${campaign.campaign_id}<br>
                            <strong>Type:</strong> ${campaign.type}<br>
                            <strong>Sent:</strong> ${campaign.sent.toLocaleString()}<br>
                            <strong>Opened:</strong> ${campaign.opened.toLocaleString()}<br>
                            <strong>Clicked:</strong> ${campaign.clicked.toLocaleString()}<br>
                            <strong>Conversion Rate:</strong> ${campaign.conversion_rate}<br>
                            <strong>Created:</strong> ${new Date(campaign.created_at).toLocaleDateString()}
                        </div>
                    `).join('')}
                </div>
            `;
        } catch (error) {
            return `<div style="color: #dc3545;">❌ Error loading campaign data: ${error.message}</div>`;
        }
    }

    async fetchLoanStatus(merchantId) {
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/merchant/loan/status?merchant_id=${merchantId}`);
            if (!response.ok) throw new Error('Failed to fetch loan data');
            const data = await response.json();
            const loanData = data.data;
            
            return `
                <div style="background: linear-gradient(135deg, #0f9b8e 0%, #16a085 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 16px;">
                    <h3 style="margin: 0 0 12px 0;">🏦 Loan Status</h3>
                </div>
                <div style="display: grid; gap: 12px; margin-bottom: 16px;">
                    <div style="background: #f8f9fa; color: #000; padding: 16px; border-radius: 8px; border-left: 4px solid ${loanData.status === 'Approved' ? '#28a745' : loanData.status === 'Rejected' ? '#dc3545' : '#ffc107'};">
                        <strong>Loan ID:</strong> ${loanData.loan_id}<br>
                        <strong>Status:</strong> <span style="color: ${loanData.status === 'Approved' ? '#28a745' : loanData.status === 'Rejected' ? '#dc3545' : '#ffc107'};">${loanData.status}</span><br>
                        <strong>Amount Requested:</strong> ₹${loanData.amount_requested.toLocaleString()}<br>
                        <strong>Amount Approved:</strong> ₹${loanData.amount_approved.toLocaleString()}<br>
                        <strong>Interest Rate:</strong> ${loanData.interest_rate}<br>
                        <strong>Applied:</strong> ${new Date(loanData.applied_at).toLocaleDateString()}
                    </div>
                </div>
            `;
        } catch (error) {
            return `<div style="color: #dc3545;">❌ Error loading loan data: ${error.message}</div>`;
        }
    }

    // Retention Executor API calls
    async fetchAssignedMerchants() {
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/icp/executor/assigned-merchants`);
            if (!response.ok) throw new Error('Failed to fetch assigned merchants');
            const data = await response.json();
            const merchantData = data.data;
            
            return `
                <div style="background: linear-gradient(135deg, #0f9b8e 0%, #16a085 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 16px;">
                    <h3 style="margin: 0 0 12px 0;">🎯 Assigned Merchants - ${merchantData.date}</h3>
                </div>
                <div style="display: grid; gap: 12px; margin-bottom: 16px;">
                    ${merchantData.merchants.map(merchant => `
                        <div style="background: #f8f9fa; color: #000; padding: 12px; border-radius: 8px; border-left: 4px solid ${merchant.health_status === 'Healthy' ? '#28a745' : merchant.health_status === 'Limited Activity' ? '#ffc107' : '#dc3545'};">
                            <strong>Merchant:</strong> ${merchant.merchant_name} (${merchant.merchant_id})<br>
                            <strong>Location:</strong> ${merchant.location}<br>
                            <strong>Health Status:</strong> <span style="color: ${merchant.health_status === 'Healthy' ? '#28a745' : merchant.health_status === 'Limited Activity' ? '#ffc107' : '#dc3545'};">${merchant.health_status}</span><br>
                            <strong>Last Contact:</strong> ${merchant.last_contact}<br>
                            <strong>Priority:</strong> ${merchant.priority}<br>
                            <strong>Assigned Activity:</strong> ${merchant.assigned_activity}
                        </div>
                    `).join('')}
                </div>
            `;
        } catch (error) {
            return `<div style="color: #dc3545;">❌ Error loading assigned merchants: ${error.message}</div>`;
        }
    }

    async fetchTodaysTasks() {
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/icp/executor/todays-tasks`);
            if (!response.ok) throw new Error('Failed to fetch tasks');
            const data = await response.json();
            const taskData = data.data;
            
            return `
                <div style="background: linear-gradient(135deg, #0f9b8e 0%, #16a085 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 16px;">
                    <h3 style="margin: 0 0 12px 0;">📋 Today's Tasks - ${taskData.date}</h3>
                </div>
                <div style="display: grid; gap: 12px; margin-bottom: 16px;">
                    ${taskData.tasks.map(task => `
                        <div style="background: #f8f9fa; color: #000; padding: 12px; border-radius: 8px; border-left: 4px solid ${task.status === 'Completed' ? '#28a745' : task.status === 'In Progress' ? '#ffc107' : '#dc3545'};">
                            <strong>Task:</strong> ${task.title} (${task.task_id})<br>
                            <strong>Description:</strong> ${task.description}<br>
                            <strong>Priority:</strong> ${task.priority}<br>
                            <strong>Assigned By:</strong> ${task.assigned_by}<br>
                            <strong>Due Date:</strong> ${task.due_date}<br>
                            <strong>Status:</strong> <span style="color: ${task.status === 'Completed' ? '#28a745' : task.status === 'In Progress' ? '#ffc107' : '#dc3545'};">${task.status}</span>
                        </div>
                    `).join('')}
                </div>
            `;
        } catch (error) {
            return `<div style="color: #dc3545;">❌ Error loading tasks: ${error.message}</div>`;
        }
    }

    async fetchFollowupReminders() {
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/icp/executor/followup-reminders`);
            if (!response.ok) throw new Error('Failed to fetch reminders');
            const data = await response.json();
            const reminderData = data.data;
            
            return `
                <div style="background: linear-gradient(135deg, #0f9b8e 0%, #16a085 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 16px;">
                    <h3 style="margin: 0 0 12px 0;">🔔 Follow-up Reminders</h3>
                </div>
                <div style="display: grid; gap: 12px; margin-bottom: 16px;">
                    ${reminderData.reminders.map(reminder => `
                        <div style="background: #f8f9fa; color: #000; padding: 12px; border-radius: 8px; border-left: 4px solid ${reminder.priority === 'High' ? '#dc3545' : reminder.priority === 'Medium' ? '#ffc107' : '#28a745'};">
                            <strong>Reminder:</strong> ${reminder.type} (${reminder.reminder_id})<br>
                            <strong>Merchant:</strong> ${reminder.merchant_id}<br>
                            <strong>Due Date:</strong> ${reminder.due_date}<br>
                            <strong>Priority:</strong> <span style="color: ${reminder.priority === 'High' ? '#dc3545' : reminder.priority === 'Medium' ? '#ffc107' : '#28a745'};">${reminder.priority}</span><br>
                            <strong>Description:</strong> ${reminder.description}
                        </div>
                    `).join('')}
                </div>
            `;
        } catch (error) {
            return `<div style="color: #dc3545;">❌ Error loading reminders: ${error.message}</div>`;
        }
    }

    async fetchPendingActions() {
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/icp/executor/pending-actions`);
            if (!response.ok) throw new Error('Failed to fetch pending actions');
            const data = await response.json();
            const actionData = data.data;
            
            return `
                <div style="background: linear-gradient(135deg, #0f9b8e 0%, #16a085 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 16px;">
                    <h3 style="margin: 0 0 12px 0;">⏳ Pending Actions</h3>
                </div>
                <div style="display: grid; gap: 12px; margin-bottom: 16px;">
                    ${actionData.actions.map(action => `
                        <div style="background: #f8f9fa; color: #000; padding: 12px; border-radius: 8px; border-left: 4px solid #ffc107;">
                            <strong>Action:</strong> ${action.type} (${action.action_id})<br>
                            <strong>Merchant:</strong> ${action.merchant_id}<br>
                            <strong>Due Date:</strong> ${action.due_date}<br>
                            <strong>Description:</strong> ${action.description}<br>
                            <strong>Status:</strong> <span style="color: #ffc107;">${action.status}</span>
                        </div>
                    `).join('')}
                </div>
            `;
        } catch (error) {
            return `<div style="color: #dc3545;">❌ Error loading pending actions: ${error.message}</div>`;
        }
    }

    async fetchPendingDocuments() {
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/icp/executor/check-pending-documents`);
            if (!response.ok) throw new Error('Failed to fetch pending documents');
            const data = await response.json();
            const docData = data.data;
            
            return `
                <div style="background: linear-gradient(135deg, #0f9b8e 0%, #16a085 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 16px;">
                    <h3 style="margin: 0 0 12px 0;">📄 Pending Documents</h3>
                </div>
                <div style="display: grid; gap: 12px; margin-bottom: 16px;">
                    ${docData.pending_documents.map(doc => `
                        <div style="background: #f8f9fa; color: #000; padding: 12px; border-radius: 8px; border-left: 4px solid ${doc.priority === 'High' ? '#dc3545' : doc.priority === 'Medium' ? '#ffc107' : '#28a745'};">
                            <strong>Merchant:</strong> ${doc.merchant_name} (${doc.merchant_id})<br>
                            <strong>Pending Documents:</strong> ${doc.pending_documents.join(', ')}<br>
                            <strong>Onboarding Stage:</strong> ${doc.onboarding_stage}<br>
                            <strong>Priority:</strong> <span style="color: ${doc.priority === 'High' ? '#dc3545' : doc.priority === 'Medium' ? '#ffc107' : '#28a745'};">${doc.priority}</span>
                        </div>
                    `).join('')}
                </div>
            `;
        } catch (error) {
            return `<div style="color: #dc3545;">❌ Error loading pending documents: ${error.message}</div>`;
        }
    }

    // HR Assistant API calls (basic implementations)
    async fetchAttendanceHistory() {
        return `
            <div style="background: #f8f9fa; color: #000; padding: 16px; border-radius: 8px; border-left: 4px solid #007bff;">
                <h3>📊 Attendance History</h3>
                <p>Your attendance data will be displayed here.</p>
                <p>This feature connects to the HR system for real-time data.</p>
            </div>
        `;
    }

    async fetchPayslips() {
        return `
            <div style="background: #f8f9fa; color: #000; padding: 16px; border-radius: 8px; border-left: 4px solid #28a745;">
                <h3>💰 Payroll Information</h3>
                <p>Your payslip and salary information will be displayed here.</p>
                <p>This feature connects to the payroll system for real-time data.</p>
            </div>
        `;
    }

    async fetchEmployeeStatus() {
        return `
            <div style="background: #f8f9fa; color: #000; padding: 16px; border-radius: 8px; border-left: 4px solid #6f42c1;">
                <h3>👤 Employee Information</h3>
                <p>Your employee profile and status information will be displayed here.</p>
                <p>This feature connects to the HR system for real-time data.</p>
            </div>
        `;
    }
}

// Initialize the chatbot when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.hrChatBot = new ChatBot();
});

// Global keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        if (window.hrChatBot) {
            window.hrChatBot.resetToMainMenu();
        }
    }
});

// Save chat state before page unload
window.addEventListener('beforeunload', () => {
    localStorage.setItem('chatBotLastActive', Date.now());
});
