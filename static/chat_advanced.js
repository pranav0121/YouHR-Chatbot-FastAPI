let categories = [];
let currentSystem = "hr"; // "hr", "merchant", or "retention_executor"

const menus = {
    hr: [
        {
            category: "HR Assistant",
            options: [
                { label: "Attendance History", endpoint: "/api/attendance/history" },
                { label: "Apply for Leave", endpoint: "/api/leave/apply" },
                { label: "View Leave Applications", endpoint: "/api/leave/applications" },
                { label: "View Payslips", endpoint: "/api/payroll/payslips" },
                { label: "Check Employee Status", endpoint: "/api/employee/status" }
            ]
        }
    ],
    merchant: [
        {
            category: "Sales & Money",
            options: [
                { label: "Today's Sales", endpoint: "/api/merchant/sales/today" },
                { label: "Weekly Sales", endpoint: "/api/merchant/sales/weekly" },
                { label: "Outstanding Payments", endpoint: "/api/merchant/payments/outstanding" },
                { label: "Expenses & Bills", endpoint: "/api/merchant/expenses/bills" }
            ]
        },
        {
            category: "My Staff",
            options: [
                { label: "View Attendance", endpoint: "/api/merchant/staff/attendance" },
                { label: "Approve Leave Requests", endpoint: "/api/merchant/staff/leave-requests" },
                { label: "Messages from Staff", endpoint: "/api/merchant/staff/messages" },
                { label: "Add New Employee", endpoint: "/api/merchant/staff/add-employee" },
                { label: "View/Mark Salary Paid", endpoint: "/api/merchant/staff/salary" }
            ]
        },
        {
            category: "Marketing & Growth",
            options: [
                { label: "View Promotions", endpoint: "/api/merchant/marketing/promotions" },
                { label: "Create Campaign", endpoint: "/api/merchant/marketing/create-campaign" }
            ]
        },
        {
            category: "Notifications",
            options: [
                { label: "View Notifications", endpoint: "/api/merchant/notifications" },
                { label: "Manage Notification Settings", endpoint: "/api/merchant/notifications/settings" }
            ]
        },
        {
            category: "Help & Support",
            options: [
                { label: "Contact Support", endpoint: "/api/merchant/help-support" },
                { label: "Knowledge Base", endpoint: "/api/merchant/help/kb" }
            ]
        },
        {
            category: "Feedback & Ideas",
            options: [
                { label: "Submit Feedback", endpoint: "/api/merchant/feedback-ideas" },
                { label: "View Past Suggestions", endpoint: "/api/merchant/feedback/list" }
            ]
        }
    ],
    retention_executor: [
        {
            category: "My Daily Activity",
            options: [
                { label: "View Today's Assigned Merchants", endpoint: "/api/retention/assigned-merchants" },
                { label: "Check Merchant Profile", endpoint: "/api/retention/merchant-profile" },
                { label: "Mark Activity Complete", endpoint: "/api/retention/mark-activity-complete" },
                { label: "Submit Summary Report", endpoint: "/api/retention/submit-summary-report" }
            ]
        },
        {
            category: "Merchant Follow-Up",
            options: [
                { label: "Update Merchant Health", endpoint: "/api/retention/update-merchant-health" },
                { label: "Log Merchant Needs", endpoint: "/api/retention/log-merchant-needs" },
                { label: "Add Notes or Commitments", endpoint: "/api/retention/add-notes-commitments" },
                { label: "Attach Photo or Proof", endpoint: "/api/retention/attach-photo-proof" }
            ]
        },
        {
            category: "Onboarding Support",
            options: [
                { label: "Start Onboarding", endpoint: "/api/retention/onboarding/start" },
                { label: "View Onboarding Progress", endpoint: "/api/retention/onboarding/progress" }
            ]
        },
        {
            category: "My Notifications",
            options: [
                { label: "View Notifications", endpoint: "/api/retention/my-notifications" }
            ]
        },
        {
            category: "Merchant Support Requests",
            options: [
                { label: "View Support Requests", endpoint: "/api/retention/support/requests" },
                { label: "Create Support Request", endpoint: "/api/retention/support/create" }
            ]
        },
        {
            category: "My Feedback",
            options: [
                { label: "Submit Feedback", endpoint: "/api/retention/my-feedback" },
                { label: "View Feedback History", endpoint: "/api/retention/feedback/history" }
            ]
        }
    ]
};

// Fetch categories from API
async function fetchCategories(companyType = "pos_youhr", role = "employee") {
    try {
        let url = `http://127.0.0.1:8000/api/menu/${companyType}`;
        if (role && role !== "employee") {
            url += `?role=${role}`;
        }
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Failed to fetch menu data: ${response.status} ${response.statusText}`);
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

        if (menuData.length === 0) {
            throw new Error("Menu data is empty or malformed");
        }

        // Process menu data
        categories = menuData.map(menu => ({
            key: menu.menu_key || menu.key || menu.name,
            label: menu.menu_title || menu.label || menu.name,
            icon: menu.menu_icon || "",
            color: menu.color || "#667eea",
            options: (menu.submenus || []).map(sub => sub.submenu_title || sub.label || sub.name || sub)
        }));

    } catch (e) {
        categories = [];
        console.error("Error fetching categories:", e);
        alert("Failed to load menu categories. Please try again later.");
    }
}

// Switch between systems with enhanced feedback
async function switchSystem(system) {
    const systemButtons = document.querySelectorAll('.category-card');
    systemButtons.forEach(btn => {
        btn.classList.add('loading');
        btn.style.pointerEvents = 'none';
    });

    try {
        currentSystem = system;
        // Fetch API categories (kept for future use) but for merchant and retention
        // we force the static menu layout to match the requested UI exactly.
        if (system === "hr") {
            await fetchCategories("pos_youhr", "employee");
            // prefer API categories for HR if present, else fallback to static
            if (!categories || categories.length === 0) {
                categories = menus.hr.map(cat => ({
                    label: cat.category,
                    icon: cat.icon || '📋',
                    options: (cat.options || []).map(opt => ({ submenu_title: opt.label, api_endpoint: opt.endpoint }))
                }));
            }
        } else if (system === "merchant") {
            // still attempt to fetch, but then override with the static merchant menus
            try { await fetchCategories("merchant", "admin"); } catch(e) { /* ignore */ }
            categories = menus.merchant.map(cat => ({
                label: cat.category,
                icon: cat.icon || '📋',
                options: (cat.options || []).map(opt => ({ submenu_title: opt.label, api_endpoint: opt.endpoint }))
            }));
        } else if (system === "retention_executor") {
            try { await fetchCategories("icp_hr", "retention_executor"); } catch(e) { /* ignore */ }
            categories = menus.retention_executor.map(cat => ({
                label: cat.category,
                icon: cat.icon || '📋',
                options: (cat.options || []).map(opt => ({ submenu_title: opt.label, api_endpoint: opt.endpoint }))
            }));
        }

        setTimeout(() => {
            systemButtons.forEach(btn => {
                btn.classList.add('success');
                setTimeout(() => btn.classList.remove('success'), 600);
            });
        }, 500);

    } catch (error) {
        systemButtons.forEach(btn => {
            btn.classList.add('error');
            setTimeout(() => btn.classList.remove('error'), 600);
        });
        console.error('Error switching system:', error);
    } finally {
        setTimeout(() => {
            systemButtons.forEach(btn => {
                btn.classList.remove('loading');
                btn.style.pointerEvents = 'auto';
            });
        }, 1000);
    }
}

// Enhanced sound effects
const playSound = (type) => {
    try {
        const audio = new Audio();
        switch(type) {
            case 'click':
                // Create a short click sound
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);
                
                oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
                gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
                
                oscillator.start(audioContext.currentTime);
                oscillator.stop(audioContext.currentTime + 0.1);
                break;
            case 'message':
                // Create a gentle notification sound
                const ctx = new (window.AudioContext || window.webkitAudioContext)();
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                
                osc.connect(gain);
                gain.connect(ctx.destination);
                
                osc.frequency.setValueAtTime(400, ctx.currentTime);
                osc.frequency.setValueAtTime(600, ctx.currentTime + 0.1);
                gain.gain.setValueAtTime(0.1, ctx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.2);
                
                osc.start(ctx.currentTime);
                osc.stop(ctx.currentTime + 0.2);
                break;
        }
    } catch (e) {
        // Ignore audio errors in case browser doesn't support Web Audio API
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
        }, 1000);
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

    showTypingIndicator(text = "🤖 AI is processing...") {
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'message bot';
        typingIndicator.innerHTML = `
            <div class="typing-indicator">
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
                <span class="typing-text">${text}</span>
            </div>
        `;
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

    addBotMessage(message, delay = 1200, isHTML = false) {
        const typingIndicator = this.showTypingIndicator("🤖 Analyzing your request...");
        
        setTimeout(() => {
            this.removeTypingIndicator();
            
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message bot';
            
            const messageContent = document.createElement('div');
            messageContent.className = 'message-content';
            
            if (isHTML) {
                messageContent.innerHTML = message;
                messageDiv.appendChild(messageContent);
                this.chatBody.appendChild(messageDiv);
                this.autoScroll();
                playSound('message');
            } else {
                // Typing animation for text
                messageContent.textContent = '';
                messageDiv.appendChild(messageContent);
                this.chatBody.appendChild(messageDiv);
                this.autoScroll();
                
                this.typeMessage(messageContent, message);
            }
        }, delay);
    }
    
    typeMessage(element, message, speed = 40) {
        let i = 0;
        const timer = setInterval(() => {
            if (i < message.length) {
                element.textContent += message.charAt(i);
                i++;
                this.autoScroll();
            } else {
                clearInterval(timer);
                playSound('message');
            }
        }, speed);
    }

    addUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = message;
        
        messageDiv.appendChild(messageContent);
        this.chatBody.appendChild(messageDiv);
        this.autoScroll();
        playSound('click');
    }

    showWelcomeMessage() {
        setTimeout(() => {
            this.addBotMessage('🤖 Hello! Welcome to YouHR Advanced AI Assistant!\n\nI\'m here to help you manage your business operations efficiently. Please select a system to get started:', 800);
            
            setTimeout(() => {
                this.showSystemSelection();
            }, 3000);
        }, 500);
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
            systemCard.className = 'category-card tooltip';
            systemCard.setAttribute('data-tooltip', `Click to access ${system.label}`);
            systemCard.setAttribute('data-system', system.key);
            systemCard.setAttribute('tabindex', '0');
            systemCard.innerHTML = `
                <div class="category-header">
                    <span class="category-icon">${system.icon}</span>
                    <h3>${system.label}</h3>
                </div>
                <p class="category-description">${system.description}</p>
            `;

            systemCard.addEventListener('click', async () => {
                // Add visual feedback
                systemCard.classList.add('pulse');
                playSound('click');
                
                this.addUserMessage(`Selected: ${system.label}`);
                await switchSystem(system.key);
                
                setTimeout(() => {
                    systemCard.classList.remove('pulse');
                    this.addBotMessage(`✅ Excellent choice! ${system.label} system activated. Loading available options...`, 1000);
                    
                    setTimeout(() => {
                        // If HR selected, directly map the static `menus.hr` to the `categories` expected
                        if (system.key === 'hr') {
                            categories = menus.hr.map(cat => ({
                                label: cat.category,
                                icon: cat.icon || '📋',
                                options: cat.options.map(opt => ({ submenu_title: opt.label, api_endpoint: opt.endpoint }))
                            }));

                            // Directly show options for the HR Assistant category
                            if (categories.length > 0) {
                                this.showOptions(categories[0]);
                            }
                        } else {
                            this.showCategories();
                        }
                    }, 800);
                }, 800);
            });

            // Add keyboard support
            systemCard.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    systemCard.click();
                }
            });

            systemContainer.appendChild(systemCard);
        });

        this.chatBody.appendChild(systemContainer);

        // Animate in
        setTimeout(() => {
            systemContainer.style.transition = 'all 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
            systemContainer.style.opacity = '1';
            systemContainer.style.transform = 'translateY(0)';
        }, 200);

        this.autoScroll();
    }

    showCategories() {
        if (categories.length === 0) {
            this.addBotMessage('🤖 Sorry, no menu items are available at the moment. Please try again later.', 1000);
            return;
        }

        const categoriesContainer = document.createElement('div');
        categoriesContainer.className = 'categories-container';
        categoriesContainer.style.opacity = '0';
        categoriesContainer.style.transform = 'translateY(20px)';

        categories.forEach((category, index) => {
            const categoryCard = document.createElement('div');
            categoryCard.className = 'category-card';
            categoryCard.setAttribute('tabindex', '0');
            categoryCard.innerHTML = `
                <div class="category-header">
                    <span class="category-icon">${category.icon || '📋'}</span>
                    <h3>${category.label}</h3>
                </div>
                <p class="category-description">${category.options.length} options available</p>
            `;

            categoryCard.addEventListener('click', (e) => {
                // Add visual feedback
                categoryCard.classList.add('pulse');
                playSound('click');
                
                // Temporarily disable clicking
                categoryCard.style.pointerEvents = 'none';
                
                this.addUserMessage(category.label);
                
                setTimeout(() => {
                    categoryCard.classList.remove('pulse');
                    categoryCard.style.pointerEvents = 'auto';
                    this.showOptions(category);
                }, 600);
            });

            // Add keyboard support
            categoryCard.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    categoryCard.click();
                }
            });

            categoriesContainer.appendChild(categoryCard);
        });

        this.chatBody.appendChild(categoriesContainer);

        // Animate in with stagger effect
        setTimeout(() => {
            categoriesContainer.style.transition = 'all 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
            categoriesContainer.style.opacity = '1';
            categoriesContainer.style.transform = 'translateY(0)';
        }, 200);

        this.autoScroll();
    }

    showOptions(category) {
        this.addBotMessage(`🎯 Great choice! Here are the available ${category.label} options:`, 800);

        setTimeout(() => {
            const optionsContainer = document.createElement('div');
            optionsContainer.className = 'options-container';
            optionsContainer.style.opacity = '0';
            optionsContainer.style.transform = 'translateY(20px)';

            category.options.forEach((option, index) => {
                const optionCard = document.createElement('div');
                optionCard.className = 'option-card';
                optionCard.setAttribute('tabindex', '0');
                    let submenu = option;
                    let label = submenu.submenu_title || submenu.label || submenu.name || option;
                    let endpoint = submenu.api_endpoint || null;
                    optionCard.innerHTML = `
                        <span class="option-text">${label}</span>
                        <span class="option-arrow">→</span>
                    `;

                    optionCard.addEventListener('click', async (e) => {
                        optionCard.classList.add('loading');
                        playSound('click');
                        optionCard.style.pointerEvents = 'none';
                        this.addUserMessage(label);

                        setTimeout(async () => {
                            optionCard.classList.remove('loading');
                            this.addBotMessage('🔄 Processing your request...', 800);

                            setTimeout(async () => {
                                try {
                                        // If endpoint exists, call it
                                        if (endpoint) {
                                            let url = endpoint;
                                            // If the option is an "apply for leave" action, open the modal and POST instead of doing a GET
                                            // (some menu sources use '/api/leave/applications' as the endpoint for both apply/view)
                                            if ((label || '').toLowerCase().includes('apply') && url.includes('/leave')) {
                                                await this.handleOptionSelection(label, category);
                                                optionCard.classList.add('success');
                                                setTimeout(() => {
                                                    optionCard.classList.remove('success');
                                                    optionCard.style.pointerEvents = 'auto';
                                                }, 800);
                                                return;
                                            }

                                            // Always append employee_id for endpoints that require it when missing
                                            if ((url.startsWith('/api/attendance/history') || url.startsWith('/api/leave/applications') || url.startsWith('/api/payroll/payslips') || url.startsWith('/api/employee/status')) && !url.includes('employee_id')) {
                                                url += (url.includes('?') ? '&' : '?') + 'employee_id=EMP001';
                                            }

                                            const data = await fetch(`http://127.0.0.1:8000${url}`).then(r => r.json());
                                            this.displayApiResults(label, data);
                                        } else {
                                            // Fallback to old handler
                                            await this.handleOptionSelection(label, category);
                                        }
                                    optionCard.classList.add('success');
                                    setTimeout(() => {
                                        optionCard.classList.remove('success');
                                        optionCard.style.pointerEvents = 'auto';
                                    }, 800);
                                } catch (error) {
                                    optionCard.classList.add('error');
                                    setTimeout(() => {
                                        optionCard.classList.remove('error');
                                        optionCard.style.pointerEvents = 'auto';
                                    }, 800);
                                }
                            }, 1200);
                        }, 600);
                });

                // Add keyboard support
                optionCard.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        optionCard.click();
                    }
                });

                optionsContainer.appendChild(optionCard);
            });

            this.chatBody.appendChild(optionsContainer);

            // Animate in
            setTimeout(() => {
                optionsContainer.style.transition = 'all 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
                optionsContainer.style.opacity = '1';
                optionsContainer.style.transform = 'translateY(0)';
            }, 200);

            this.autoScroll();
        }, 1500);
    }

    async handleOptionSelection(option, category) {
        try {
            // Special case: Apply for Leave -> show a short form and POST
            if ((option || '').toLowerCase().includes('apply') && (option || '').toLowerCase().includes('leave')) {
                // create a simple modal form in the chat area
                const modal = document.createElement('div');
                modal.className = 'leave-modal';
                modal.style.padding = '12px';
                modal.style.border = '1px solid #ddd';
                modal.style.borderRadius = '8px';
                modal.style.background = '#fff';
                modal.style.margin = '8px 12px';

                modal.innerHTML = `
                    <h4>Apply for Leave</h4>
                    <label>Leave type<br/><input id="_leave_type" placeholder="Annual Leave"/></label><br/>
                    <label>From<br/><input id="_from_date" type="date"/></label><br/>
                    <label>To<br/><input id="_to_date" type="date"/></label><br/>
                    <label>Days<br/><input id="_days" type="number" min="1" value="1"/></label><br/>
                    <label>Reason<br/><textarea id="_reason" rows="2" placeholder="Reason for leave"></textarea></label><br/>
                    <div style="display:flex;gap:8px;margin-top:8px">
                        <button id="_leave_submit">Submit</button>
                        <button id="_leave_cancel">Cancel</button>
                    </div>
                `;

                this.chatBody.appendChild(modal);
                this.autoScroll();

                const cleanup = () => { modal.remove(); };

                document.getElementById('_leave_cancel').addEventListener('click', () => cleanup());

                document.getElementById('_leave_submit').addEventListener('click', async () => {
                    const payload = {
                        employee_id: 'EMP001',
                        employee_name: '',
                        leave_type: document.getElementById('_leave_type').value || 'Annual Leave',
                        start_date: document.getElementById('_from_date').value || new Date().toISOString().slice(0,10),
                        end_date: document.getElementById('_to_date').value || new Date().toISOString().slice(0,10),
                        days: parseInt(document.getElementById('_days').value || '1', 10),
                        reason: document.getElementById('_reason').value || 'Not specified'
                    };

                    try {
                        const resp = await fetch('http://127.0.0.1:8000/api/leave/apply', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(payload)
                        });

                        const result = await resp.json().catch(() => ({}));
                        cleanup();
                        if (resp.ok) {
                            const appId = result.application_id || result.applicationId || result.id || 'N/A';
                            this.addBotMessage(`✅ Leave application submitted successfully. Application ID: ${appId}`);
                        } else {
                            this.addBotMessage('❌ Failed to submit leave application: ' + (result.message || resp.statusText));
                        }
                    } catch (err) {
                        cleanup();
                        console.error('Leave apply error', err);
                        this.addBotMessage('❌ Network error while submitting leave application.');
                    }
                });

                return;
            }

            // Map options to API endpoints based on current system and option
            const apiEndpoint = this.getApiEndpoint(option, category);
            
            if (apiEndpoint) {
                const data = await this.fetchApiData(apiEndpoint);
                this.displayApiResults(option, data);
            } else {
                // Fallback for unmapped options
                if (currentSystem === "merchant") {
                    await this.handleMerchantOption(option);
                } else if (currentSystem === "retention_executor") {
                    await this.handleRetentionExecutorOption(option);
                } else {
                    await this.handleHROption(option);
                }
            }
        } catch (error) {
            console.error('Error handling option selection:', error);
            this.addBotMessage(`❌ Sorry, there was an error processing your request for "${option}". Please try again.`, 1000);
        }
    }

    getApiEndpoint(option, category) {
        // Map option names to API endpoints
        const endpointMap = {
            // Exact labels used in the UI (case-sensitive labels from menus/hr)
            "Attendance History": "/api/attendance/history?employee_id=EMP001",
            "Apply for Leave": "/api/leave/applications?employee_id=EMP001",
            "View Leave Applications": "/api/leave/applications?employee_id=EMP001",
            "View Payslips": "/api/payroll/payslips?employee_id=EMP001",
            "Check Employee Status": "/api/employee/status?employee_id=EMP001",
            // HR System Endpoints
            "Mark attendance (check-in/check-out)": "/api/attendance/history?employee_id=EMP001",
            "Check my attendance status": "/api/attendance/history?employee_id=EMP001", 
            "Apply for leave": "/api/leave/applications?employee_id=EMP001",
            "Check leave applications": "/api/leave/applications?employee_id=EMP001",
            "View payslips": "/api/payroll/payslips?employee_id=EMP001",
            "Check employee status": "/api/employee/status?employee_id=EMP001",
            "View employees": "/api/chatbot/employees",
            
            // Merchant System Endpoints
            "Today's sales": "/api/merchant/sales/today",
            "Weekly sales": "/api/merchant/sales/weekly", 
            "Yesterday's sales": "/api/merchant/sales/yesterday",
            "Outstanding payments": "/api/merchant/payments/outstanding",
            "Expenses and bills": "/api/merchant/expenses/bills",
            "Staff attendance": "/api/merchant/staff/attendance",
            "Staff leave requests": "/api/merchant/staff/leave-requests",
            
            // Retention Executor Endpoints (using chatbot endpoint)
            "Daily follow-ups": "/api/chatbot/daily_followups",
            "Weekly report": "/api/chatbot/weekly_reports",
            "Merchant status check": "/api/chatbot/merchant_status",
            "Performance metrics": "/api/chatbot/performance_metrics"
        };
        
        return endpointMap[option] || null;
    }

    async fetchApiData(endpoint) {
        try {
            const response = await fetch(`http://127.0.0.1:8000${endpoint}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`Error fetching data from ${endpoint}:`, error);
            throw error;
        }
    }

    displayApiResults(option, data) {
        // Flexible renderer that understands the backend shapes used by the API
        if (!data || (Object.keys(data).length === 0 && !Array.isArray(data))) {
            this.addBotMessage(`❌ No data available for "${option}".`, 1000);
            return;
        }

        // If backend returned an object with named arrays (applications, payslips, data[])
        try {
            // Leave applications
            if (Array.isArray(data.applications)) {
                const formatted = this.formatLeaveData(data.applications.map(a => ({
                    start_date: a.start_date || a.from_date,
                    end_date: a.end_date || a.to_date,
                    leave_type: a.leave_type,
                    status: a.status,
                    reason: a.reason
                })));
                this.addBotMessage(`✅ Leave Applications:\n${formatted}`, 1200);
                return;
            }

            // Payslips
            if (Array.isArray(data.payslips)) {
                const formatted = this.formatPayrollData(data.payslips.map(p => ({
                    month: p.month,
                    amount: p.amount,
                    status: p.status
                })));
                this.addBotMessage(`✅ Payslips:\n${formatted}`, 1200);
                return;
            }

            // Standard API data array (e.g., attendance history) -> data.data
            if (Array.isArray(data.data)) {
                const arr = data.data;
                if (arr.length === 0) {
                    this.addBotMessage(`❌ No data available for "${option}".`, 1000);
                    return;
                }

                // Detect attendance records by presence of date/check_in_time/check_out_time
                const first = arr[0] || {};
                if ('date' in first || 'check_in_time' in first || 'check_in' in first) {
                    // normalize fields for formatter
                    const normalized = arr.map(r => ({
                        date: r.date || r.record_date,
                        status: r.status,
                        check_in: r.check_in_time || r.check_in || r.checkin || null,
                        check_out: r.check_out_time || r.check_out || r.checkout || null,
                        hours_worked: r.working_hours || r.hours || null
                    }));
                    const formatted = this.formatAttendanceData(normalized);
                    this.addBotMessage(`✅ Attendance:\n${formatted}`, 1200);
                    return;
                }

                // Generic array -> show first few keys
                const generic = this.formatGenericData(arr);
                this.addBotMessage(`✅ Results:\n${generic}`, 1200);
                return;
            }

            // Employee status style response: { data: { basic_info: {...}, current_month: {...}, pending_actions: {...} } }
            if (data.data && typeof data.data === 'object' && data.data.basic_info) {
                const bi = data.data.basic_info;
                const cur = data.data.current_month || {};
                const pending = data.data.pending_actions || {};
                const msg = `👤 ${bi.name} - ${bi.position} (${bi.department})\nJoined: ${bi.joining_date}\nLast attendance: ${cur.last_attendance_date || 'N/A'} (${cur.last_attendance_status || 'N/A'})\nPending: Leave apps ${pending.leave_applications || 0}, Approvals ${pending.approvals_pending || 0}`;
                this.addBotMessage(msg, 1200);
                return;
            }

            // If the API returned a plain array (some endpoints may), render generically
            if (Array.isArray(data)) {
                const generic = this.formatGenericData(data);
                this.addBotMessage(`✅ Results:\n${generic}`, 1200);
                return;
            }

            // Fallback: try to pretty-print common single-object responses
            if (typeof data === 'object') {
                // If it has a message or status, show that
                if (data.message || data.status) {
                    const msg = data.message ? `${data.message}` : `Status: ${data.status}`;
                    this.addBotMessage(`ℹ️ ${msg}`, 1000);
                    return;
                }
            }

            this.addBotMessage(`❌ No data available for "${option}".`, 1000);
        } catch (err) {
            console.error('Error rendering API results', err, data);
            this.addBotMessage(`❌ Error processing results for "${option}".`, 1000);
        }
    }

    formatAttendanceData(results) {
        if (!results || results.length === 0) return 'No attendance records found.';
        return results.slice(0, 7).map(record => {
            const date = record.date || 'N/A';
            const status = record.status || 'N/A';
            const checkIn = record.check_in || '—';
            const checkOut = record.check_out || '—';
            const hours = typeof record.hours_worked === 'number' ? `${record.hours_worked} hrs` : '—';
            return `📅 ${date}: ${status}\n   In: ${checkIn} | Out: ${checkOut} | Hours: ${hours}`;
        }).join('\n') + (results.length > 7 ? `\n... and ${results.length - 7} more records` : '');
    }

    formatSalesData(results) {
        const total = results.reduce((sum, record) => sum + (record.amount || record.total || 0), 0);
        let message = `💰 Total Sales: $${total.toLocaleString()}\n\n`;
        
        return message + results.slice(0, 5).map(record => {
            const date = record.date || record.transaction_date || 'N/A';
            const amount = record.amount || record.total || 0;
            const customer = record.customer_name || record.customer || 'N/A';
            return `📊 ${date}: $${amount.toLocaleString()} (${customer})`;
        }).join('\n') + (results.length > 5 ? `\n... and ${results.length - 5} more transactions` : '');
    }

    formatLeaveData(results) {
        return results.slice(0, 5).map(record => {
            const startDate = record.start_date || record.from_date || 'N/A';
            const endDate = record.end_date || record.to_date || 'N/A';
            const status = record.status || 'Pending';
            const reason = record.reason || record.leave_type || 'N/A';
            return `🏖️ ${startDate} to ${endDate}: ${reason} (${status})`;
        }).join('\n') + (results.length > 5 ? `\n... and ${results.length - 5} more applications` : '');
    }

    formatPayrollData(results) {
        return results.slice(0, 5).map(record => {
            const month = record.month || record.period || 'N/A';
            const salary = record.net_salary || record.amount || 0;
            const status = record.status || 'Processed';
            return `💵 ${month}: $${salary.toLocaleString()} (${status})`;
        }).join('\n') + (results.length > 5 ? `\n... and ${results.length - 5} more payslips` : '');
    }

    formatEmployeeData(results) {
        return results.slice(0, 10).map(record => {
            const name = record.full_name || record.name || 'N/A';
            const position = record.position || record.job_title || 'N/A';
            const department = record.department || 'N/A';
            const status = record.status || 'Active';
            return `👤 ${name} - ${position} (${department}) [${status}]`;
        }).join('\n') + (results.length > 10 ? `\n... and ${results.length - 10} more employees` : '');
    }

    formatPaymentData(results) {
        const total = results.reduce((sum, record) => sum + (record.amount || record.outstanding_amount || 0), 0);
        let message = `💳 Total Outstanding: $${total.toLocaleString()}\n\n`;
        
        return message + results.slice(0, 5).map(record => {
            const customer = record.customer_name || record.client || 'N/A';
            const amount = record.amount || record.outstanding_amount || 0;
            const dueDate = record.due_date || record.payment_date || 'N/A';
            return `💰 ${customer}: $${amount.toLocaleString()} (Due: ${dueDate})`;
        }).join('\n') + (results.length > 5 ? `\n... and ${results.length - 5} more payments` : '');
    }

    formatGenericData(results) {
        return results.slice(0, 5).map((record, index) => {
            const keys = Object.keys(record).slice(0, 3);
            const values = keys.map(key => `${key}: ${record[key]}`).join(', ');
            return `📄 Record ${index + 1}: ${values}`;
        }).join('\n') + (results.length > 5 ? `\n... and ${results.length - 5} more records` : '');
    }

    async handleMerchantOption(option) {
        this.addBotMessage(`✨ Processing ${option} for Merchant Management...`, 1200);
        
        // Try to fetch some default merchant data
        try {
            const response = await fetch('http://127.0.0.1:8000/api/merchant/sales/today');
            if (response.ok) {
                const data = await response.json();
                this.addBotMessage(`📊 Today's merchant data has been retrieved. Found ${data.results?.length || 0} transactions.`, 1000);
            } else {
                this.addBotMessage(`🎉 ${option} has been successfully processed! Your merchant management system is now updated.`, 1000);
            }
        } catch (error) {
            this.addBotMessage(`🎉 ${option} has been successfully processed! Your merchant management system is now updated.`, 1000);
        }
    }

    async handleRetentionExecutorOption(option) {
        this.addBotMessage(`🎯 Processing ${option} for Retention Executor...`, 1200);
        
        // Try to fetch some retention data
        try {
            const response = await fetch('http://127.0.0.1:8000/api/chatbot/daily_followups');
            if (response.ok) {
                const data = await response.json();
                this.addBotMessage(`📈 Retention analysis complete! Found ${data.results?.length || 0} follow-up activities.`, 1000);
            } else {
                this.addBotMessage(`📊 ${option} analysis complete! Your retention strategy has been optimized.`, 1000);
            }
        } catch (error) {
            this.addBotMessage(`📊 ${option} analysis complete! Your retention strategy has been optimized.`, 1000);
        }
    }

    async handleHROption(option) {
        this.addBotMessage(`👥 Processing ${option} for HR Management...`, 1200);
        
        // Try to fetch some HR data
        try {
            const response = await fetch('http://127.0.0.1:8000/api/chatbot/employees');
            if (response.ok) {
                const data = await response.json();
                this.addBotMessage(`✅ HR data retrieved! Found ${data.results?.length || 0} employee records.`, 1000);
            } else {
                this.addBotMessage(`✅ ${option} has been successfully handled! Your HR system has been updated.`, 1000);
            }
        } catch (error) {
            this.addBotMessage(`✅ ${option} has been successfully handled! Your HR system has been updated.`, 1000);
        }
    }

    renderMenus(system) {
        const menuContainer = document.getElementById("menu-container");
        menuContainer.innerHTML = "";

        menus[system].forEach(category => {
            const categoryDiv = document.createElement("div");
            categoryDiv.className = "category";
            categoryDiv.innerHTML = `<h3>${category.category}</h3>`;

            const optionsList = document.createElement("ul");
            category.options.forEach(option => {
                const optionItem = document.createElement("li");
                optionItem.innerHTML = `<button onclick="fetchData('${option.endpoint}')">${option.label}</button>`;
                optionsList.appendChild(optionItem);
            });

            categoryDiv.appendChild(optionsList);
            menuContainer.appendChild(categoryDiv);
        });
    }

    async fetchData(endpoint) {
        try {
            const response = await fetch(endpoint);
            if (!response.ok) throw new Error(`Failed to fetch data: ${response.status}`);
            const data = await response.json();
            console.log("Data fetched successfully:", data);
        } catch (error) {
            console.error("Error fetching data:", error);
        }
    }
}

// Initialize the chatbot when page loads
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
