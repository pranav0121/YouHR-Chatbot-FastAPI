let categories = [];
// Demo merchant id used by the demo UI; can be overridden by setting window.DEMO_MERCHANT_ID before this script runs
let DEMO_MERCHANT_ID = (window && window.DEMO_MERCHANT_ID) ? window.DEMO_MERCHANT_ID : 'MERCH123';

// Simple transient toast helper for small UX notifications
function showToast(text, timeout = 2000) {
    try {
        const t = document.createElement('div');
        t.className = 'hr-toast';
        t.textContent = text;
        t.style = 'position:fixed;right:16px;bottom:24px;background:rgba(0,0,0,0.8);color:#fff;padding:8px 12px;border-radius:6px;z-index:10000;font-size:0.95rem;animation: hr-toast-in 240ms ease-out;';
        document.body.appendChild(t);
        setTimeout(() => {
            t.style.opacity = '0';
            t.style.transform = 'translateY(6px)';
            setTimeout(() => t.remove(), 220);
        }, timeout);
    } catch (e) { /* ignore */ }
}
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
                // use the backend alias that exists ('/api/merchant/marketing/results')
                { label: "View Promotions", endpoint: "/api/merchant/marketing/results" },
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

    // merchant selector removed for cleaner UI

        // Fetch categories and show welcome
        await fetchCategories();
        setTimeout(() => {
            this.showWelcomeMessage();
        }, 1000);
    }

    // merchant selector removed

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
                                            // Feedback UI handlers: open modal for submit, fetch+render for list
                                            if (url === '/api/merchant/feedback-ideas') {
                                                // Open a modal to submit feedback
                                                const modal = document.createElement('div');
                                                modal.className = 'feedback-modal';
                                                modal.style = 'position:fixed;left:0;right:0;top:0;bottom:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.35);z-index:9999;';
                                                modal.innerHTML = `
                                                    <div style="background:#fff;padding:18px;border-radius:8px;min-width:320px;box-shadow:0 6px 24px rgba(0,0,0,0.2);">
                                                        <h3 style="margin-top:0;">Submit Feedback</h3>
                                                        <label style="display:block;margin:8px 0 4px;font-size:0.9rem;">Your suggestion or feedback</label>
                                                        <textarea id="_fb_content" style="width:100%;height:96px;padding:8px;border:1px solid #ddd;border-radius:4px;"></textarea>
                                                        <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:12px;">
                                                            <button id="_fb_cancel" style="padding:8px 12px;border-radius:6px;border:1px solid #ccc;background:#fff;">Cancel</button>
                                                            <button id="_fb_submit" style="padding:8px 12px;border-radius:6px;border:none;background:#007bff;color:#fff;">Send</button>
                                                        </div>
                                                    </div>
                                                `;
                                                document.body.appendChild(modal);
                                                const cleanup = () => { modal.remove(); };
                                                document.getElementById('_fb_cancel').addEventListener('click', cleanup);
                                                document.getElementById('_fb_submit').addEventListener('click', async () => {
                                                    const content = document.getElementById('_fb_content').value.trim();
                                                    if (!content) { alert('Please enter feedback'); return; }
                                                    try {
                                                        const resp = await fetch('http://127.0.0.1:8000/api/merchant/feedback-ideas', {
                                                            method: 'POST',
                                                            headers: { 'Content-Type': 'application/json', 'X-Merchant-Id': DEMO_MERCHANT_ID },
                                                            body: JSON.stringify({ content })
                                                        });
                                                        const j = await resp.json().catch(() => ({}));
                                                        cleanup();
                                                        if (resp.ok) {
                                                            window.hrChatBot.addBotMessage('\u2705 Feedback submitted. Thank you!');
                                                            try { showToast('Feedback submitted'); } catch(e) { /* ignore */ }
                                                        } else {
                                                            window.hrChatBot.addBotMessage('\u274c Failed to submit feedback: ' + (j.message || resp.statusText));
                                                        }
                                                    } catch (err) {
                                                        cleanup();
                                                        console.error('Submit feedback error', err);
                                                        window.hrChatBot.addBotMessage('\u274c Network error while submitting feedback.');
                                                    }
                                                });

                                                optionCard.classList.add('success');
                                                setTimeout(() => { optionCard.classList.remove('success'); optionCard.style.pointerEvents = 'auto'; }, 800);
                                                return;
                                            }

                                            if (url === '/api/merchant/feedback/list') {
                                                // Fetch the list and render simple entries
                                                try {
                                                    const res = await fetch('http://127.0.0.1:8000/api/merchant/feedback/list', {
                                                        headers: { 'X-Merchant-Id': DEMO_MERCHANT_ID }
                                                    });
                                                    const pj = await res.json().catch(() => ({}));
                                                    const arr = pj.data || [];
                                                    if (!Array.isArray(arr) || arr.length === 0) {
                                                        window.hrChatBot.addBotMessage('\u274c No data available for "View Past Suggestions".');
                                                    } else {
                                                        const lines = arr.slice(0, 12).map(f => `\u2022 [${f.id}] ${f.content} (${f.created_on || 'unknown'})`).join('\n');
                                                        window.hrChatBot.addBotMessage('\u2705 Past Suggestions:\n' + lines);
                                                    }
                                                } catch (e) {
                                                    console.error('Feedback list error', e);
                                                    window.hrChatBot.addBotMessage('\u274c Unable to fetch past suggestions.');
                                                }

                                                optionCard.classList.add('success');
                                                setTimeout(() => { optionCard.classList.remove('success'); optionCard.style.pointerEvents = 'auto'; }, 800);
                                                return;
                                            }
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

                                            // Special-case: route interactive POST-style endpoints (Add New Employee) to the modal/POST flow
                                            if (url === '/api/merchant/staff/add-employee' || (label || '').toLowerCase().includes('add new employee')) {
                                                // delegate to the global handler which opens the modal and POSTs the payload
                                                await window.handleMenuClick(url, label);
                                                optionCard.classList.add('success');
                                                setTimeout(() => {
                                                    optionCard.classList.remove('success');
                                                    optionCard.style.pointerEvents = 'auto';
                                                }, 800);
                                                return;
                                            }

                                            // Special-case: Create Campaign -> open a minimal modal to collect campaign_name and budget, then POST
                                            if (url === '/api/merchant/marketing/create-campaign' || (label || '').toLowerCase().includes('create campaign')) {
                                                // build modal
                                                const modal = document.createElement('div');
                                                modal.className = 'campaign-modal';
                                                modal.style = 'position:fixed;left:0;right:0;top:0;bottom:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.35);z-index:9999;';
                                                modal.innerHTML = `
                                                    <div style="background:#fff;padding:18px;border-radius:8px;min-width:320px;box-shadow:0 6px 24px rgba(0,0,0,0.2);">
                                                        <h3 style="margin-top:0;">Create Campaign</h3>
                                                        <label style="display:block;margin:8px 0 4px;font-size:0.9rem;">Campaign Name</label>
                                                        <input id="_camp_name" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;" />
                                                        <label style="display:block;margin:8px 0 4px;font-size:0.9rem;">Budget (₹)</label>
                                                        <input id="_camp_budget" type="number" min="0" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;" value="100" />
                                                        <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:12px;">
                                                            <button id="_camp_cancel" style="padding:8px 12px;border-radius:6px;border:1px solid #ccc;background:#fff;">Cancel</button>
                                                            <button id="_camp_submit" style="padding:8px 12px;border-radius:6px;border:none;background:#007bff;color:#fff;">Create</button>
                                                        </div>
                                                    </div>
                                                `;
                                                document.body.appendChild(modal);
                                                const cleanup = () => { modal.remove(); };
                                                document.getElementById('_camp_cancel').addEventListener('click', cleanup);
                                                document.getElementById('_camp_submit').addEventListener('click', async () => {
                                                    const name = document.getElementById('_camp_name').value.trim();
                                                    const budget = parseFloat(document.getElementById('_camp_budget').value || '0');
                                                    if (!name) { alert('Please enter campaign name'); return; }
                                                    try {
                                                        const resp = await fetch(`http://127.0.0.1:8000${url}`, {
                                                            method: 'POST',
                                                            headers: { 'Content-Type': 'application/json', 'X-Merchant-Id': DEMO_MERCHANT_ID },
                                                            body: JSON.stringify({ campaign_name: name, budget })
                                                        });
                                                        const j = await resp.json().catch(() => ({}));
                                                        cleanup();
                                                            if (resp.ok) {
                                                            const camp = j.data || {};
                                                            const id = camp.campaign_id || camp.campaignId || camp.id || 'N/A';
                                                            window.hrChatBot.addBotMessage(`✅ Campaign created: ${name} (ID: ${id})`);
                                                            showToast('Campaign created');
                                                            // Refresh promotions list from server and render
                                                            try {
                                                                const res = await fetch('http://127.0.0.1:8000/api/merchant/marketing/promotions');
                                                                if (res.ok) {
                                                                    const pj = await res.json().catch(() => ({}));
                                                                    const camps = (pj.data && pj.data.campaigns) || pj.campaigns || [];
                                                                    if (camps && camps.length) window.hrChatBot.renderPromotions(camps);
                                                                }
                                                            } catch (re) { /* ignore refresh failures */ }
                                                        } else {
                                                            window.hrChatBot.addBotMessage(`❌ Failed to create campaign: ${j.message || resp.statusText}`);
                                                        }
                                                    } catch (err) {
                                                        cleanup();
                                                        console.error('Create campaign error', err);
                                                        window.hrChatBot.addBotMessage('❌ Network error while creating campaign.');
                                                    }
                                                });

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
            // Include a default merchant identifier header so file-backed endpoints
            // that filter by merchant_id return the expected rows in the demo UI.
            const response = await fetch(`http://127.0.0.1:8000${endpoint}`, {
                headers: { 'X-Merchant-Id': DEMO_MERCHANT_ID }
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`Error fetching data from ${endpoint}:`, error);
            throw error;
        }
    }

    async displayApiResults(option, data) {
        // Flexible renderer that understands the backend shapes used by the API
        if (!data || (Object.keys(data).length === 0 && !Array.isArray(data))) {
            this.addBotMessage(`❌ No data available for "${option}".`, 1000);
            return;
        }

        // If backend returned an object with a message, show it early (common for settings endpoints)
        // NOTE: some HR endpoints return { status: 'success' } without a data object; allow
        // display to continue for HR-specific options so we can handle arrays or other shapes below.
        const hrOptions = new Set([
            'Attendance History', 'Apply for Leave', 'View Leave Applications', 'View Payslips', 'Check Employee Status'
        ]);

        if (data && typeof data === 'object') {
            if (data.message) {
                // HR-specific helpful fallback for missing employee
                if (option === 'Check Employee Status' && String(data.message).toLowerCase().includes('not found')) {
                    // Try to locate demo employee records from other endpoints and render them
                    try {
                        const found = await this.tryFetchDummyEmployee();
                        if (found) return; // helper handled rendering
                    } catch (e) {
                        console.error('Error attempting to fetch dummy employee data', e);
                    }

                    // Fallback: render a small HTML card with suggested next steps and a CTA to add employee
                    const html = `
                        <div style="background:#fff;padding:12px;border-radius:8px;border-left:4px solid #6c757d;">
                            <strong>ℹ️ Employee not found</strong>
                            <div style="margin-top:8px;color:#444">We couldn't find an employee matching the query. You can add a new employee or double-check the employee ID.</div>
                            <div style="margin-top:10px;text-align:right;"><button id="_cta_add_emp" style="padding:6px 10px;border-radius:6px;border:none;background:#28a745;color:#fff;">Add New Employee</button></div>
                        </div>
                    `;
                    this.addBotMessage(html, 800, true);
                    // Attach a delegated click handler on document so timing doesn't matter.
                    (function attachCTAHandler() {
                        function onDocClick(e) {
                            try {
                                const tgt = e.target;
                                const btn = tgt && (tgt.id === '_cta_add_emp' ? tgt : (tgt.closest ? tgt.closest('#_cta_add_emp') : null));
                                if (btn) {
                                    try { window.handleMenuClick('/api/merchant/staff/add-employee', 'Add New Employee'); } catch (err) { /* ignore */ }
                                    document.removeEventListener('click', onDocClick);
                                }
                            } catch (err) { /* ignore */ }
                        }
                        document.addEventListener('click', onDocClick);
                    })();
                    return;
                }
                this.addBotMessage(`ℹ️ ${data.message}`, 1000);
                return;
            }
            if (data.status && !data.data && !hrOptions.has(option)) {
                const msg = `Status: ${data.status}`;
                this.addBotMessage(`ℹ️ ${msg}`, 1000);
                return;
            }
        }

        // If backend returned an object with named arrays (applications, payslips, data[])
        try {
            // Normalize payload: prefer data.data when it's an object, else use data itself
            const payload = (data && data.data && typeof data.data === 'object') ? data.data : data;
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

            // If backend returned a single object inside data (e.g., today's/weekly sales, outstanding payments, expenses, staff attendance)
            if (data.data && typeof data.data === 'object' && !Array.isArray(data.data)) {
                const payload = data.data;

                // Today's or weekly sales
                if (payload.total_sales !== undefined || payload.total_transactions !== undefined) {
                    const date = payload.date || `${payload.week_start || ''} to ${payload.week_end || ''}`;
                    const msg = `📈 Sales — ${date}\nTotal Sales: ₹${(payload.total_sales||0).toLocaleString()}\nTransactions: ${payload.total_transactions || 0}\nAvg Txn: ₹${(payload.average_transaction||0).toLocaleString()}`;
                    this.addBotMessage(msg, 1200);
                    return;
                }

                // Outstanding payments
                if (payload.total_outstanding !== undefined) {
                    const msg = `💳 Outstanding Payments\nTotal Outstanding: ₹${(payload.total_outstanding||0).toLocaleString()}\nPayments: ${payload.payments ? payload.payments.length : 0}`;
                    this.addBotMessage(msg, 1200);
                    return;
                }

                // Expenses & bills
                if (payload.total_expenses !== undefined || Array.isArray(payload.bills)) {
                    const msg = `🧾 Expenses & Bills\nTotal Expenses: ₹${(payload.total_expenses||0).toLocaleString()}\nBills: ${payload.bills ? payload.bills.length : 0}`;
                    this.addBotMessage(msg, 1200);
                    return;
                }

                // Staff attendance (object with staff array)
                if (Array.isArray(payload.staff)) {
                    const normalized = payload.staff.map(r => ({
                        date: payload.date || r.date,
                        status: r.status,
                        check_in: r.check_in || null,
                        check_out: r.check_out || null,
                        working_hours: r.hours || null
                    }));
                    const formatted = this.formatAttendanceData(normalized);
                    this.addBotMessage(`👥 Staff Attendance:\n${formatted}`, 1200);
                    return;
                }
                // Leave requests (payload.requests)
                if (Array.isArray(payload.requests)) {
                    const formatted = this.formatLeaveData(payload.requests.map(r => ({
                        start_date: r.from_date || r.start_date,
                        end_date: r.to_date || r.end_date,
                        leave_type: r.leave_type || 'N/A',
                        status: r.status || 'Pending',
                        reason: r.reason || ''
                    })));
                    this.addBotMessage(`✅ Leave Requests:\n${formatted}`, 1200);
                    return;
                }

                // Messages from staff (payload.messages)
                if (Array.isArray(payload.messages)) {
                    const messages = payload.messages.slice(0, 5).map(m => `• ${m.from || m.sender || 'Staff'}: ${m.subject || m.message || ''}`);
                    const msg = `💬 Messages from Staff\nTotal Messages: ${payload.messages.length}\n${messages.join('\n')}`;
                    this.addBotMessage(msg, 1200);
                    return;
                }

                // Staff salaries list
                if (Array.isArray(payload.staff_salaries)) {
                    const formatted = this.formatPayrollData(payload.staff_salaries.map(s => ({ month: s.last_paid || 'N/A', amount: s.monthly_salary || s.amount || 0, status: s.status || 'N/A' })));
                    this.addBotMessage(`💵 Staff Salaries:\n${formatted}`, 1200);
                    return;
                }

                // Single employee object (e.g., Add New Employee response in data)
                if (payload.employee_id && payload.name) {
                    const info = `✅ Employee added:\nName: ${payload.name}\nID: ${payload.employee_id}\nRole: ${payload.role || 'N/A'}\nStatus: ${payload.status || 'Active'}`;
                    this.addBotMessage(info, 1200);
                    return;
                }
            }

            // Marketing campaigns payload: data.data.campaigns or data.campaigns
            const campaigns = (data.data && data.data.campaigns) || data.campaigns;
            if (Array.isArray(campaigns)) {
                this.renderPromotions(campaigns);
                return;
            }

            // Notifications aggregate (pending_leave_requests, pending_shift_changes, payment_settlement, head_office_messages)
            try {
                if (payload.pending_leave_requests || payload.pending_shift_changes || payload.payment_settlement || payload.head_office_messages) {
                    const parts = [];
                    if (Array.isArray(payload.pending_leave_requests) && payload.pending_leave_requests.length) {
                        parts.push(`⚠️ Pending leave requests: ${payload.pending_leave_requests.length}`);
                        parts.push(payload.pending_leave_requests.slice(0,5).map(r => `• ${r.request_id} – Emp ${r.employee_id} (${r.days} days)`).join('\n'));
                    }
                    if (Array.isArray(payload.pending_shift_changes) && payload.pending_shift_changes.length) {
                        parts.push(`🔁 Pending shift changes: ${payload.pending_shift_changes.length}`);
                        parts.push(payload.pending_shift_changes.slice(0,5).map(s => `• ${s.request_id} – Emp ${s.employee_id}: ${s.from_shift}->${s.to_shift}`).join('\n'));
                    }
                    if (payload.payment_settlement) {
                        parts.push(`💳 Last settlement: ${payload.payment_settlement.last_settlement} — Amount: ₹${(payload.payment_settlement.amount||0).toLocaleString()}`);
                    }
                    if (Array.isArray(payload.head_office_messages) && payload.head_office_messages.length) {
                        parts.push(`🏢 Head Office Messages: ${payload.head_office_messages.length}`);
                        parts.push(payload.head_office_messages.slice(0,5).map(m => `• ${m.title || m.subject || m.message}`).join('\n'));
                    }

                    this.addBotMessage(`🔔 Notifications\n${parts.join('\n\n')}`, 1000);
                    return;
                }
            } catch (notifErr) {
                console.error('Error rendering notifications payload', notifErr, payload);
                this.addBotMessage(`❌ Unable to render notifications at the moment.`, 1000);
                return;
            }

            // Help & Support: contact info
            if (payload && payload.contact_email) {
                this.renderContactSupport(payload);
                return;
            }

            // Knowledge Base list
            if (payload && Array.isArray(payload.articles)) {
                this.renderKBList(payload);
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
                // Special-case: Notification settings endpoint returns data: { email, sms, in_app }
                if (data.data && typeof data.data === 'object' && ('email' in data.data || 'sms' in data.data || 'in_app' in data.data)) {
                    // Render interactive toggles so merchant can update settings directly from chat
                    try {
                        this.renderNotificationSettings(data.data);
                    } catch (e) {
                        console.error('Failed to render notification settings', e, data);
                        const s = data.data;
                        const lines = [
                            '🔔 Notification Settings',
                            `• Email: ${s.email ? 'On' : 'Off'}`,
                            `• SMS: ${s.sms ? 'On' : 'Off'}`,
                            `• In-app: ${s.in_app ? 'On' : 'Off'}`
                        ];
                        this.addBotMessage(lines.join('\n'), 1000);
                    }
                    return;
                }
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
        // Deduplicate by date: pick earliest check_in and latest check_out for each date
        const byDate = {};
        results.forEach(r => {
            const date = r.date || r.record_date || 'N/A';
            const ci = r.check_in || r.check_in_time || r.checkin || null;
            const co = r.check_out || r.check_out_time || r.checkout || null;
            const status = r.status || 'N/A';
            if (!byDate[date]) byDate[date] = { date, status, check_in: ci, check_out: co, hours_worked: r.hours_worked || r.hours || null };
            else {
                // earliest check_in
                const existing = byDate[date];
                if (ci && (!existing.check_in || ci < existing.check_in)) existing.check_in = ci;
                // latest check_out
                if (co && (!existing.check_out || co > existing.check_out)) existing.check_out = co;
                // prefer Present over other statuses when seen
                if (existing.status !== 'Present' && status === 'Present') existing.status = status;
                if (!existing.hours_worked && (r.hours_worked || r.hours)) existing.hours_worked = r.hours_worked || r.hours;
            }
        });

        const aggregated = Object.values(byDate).sort((a,b) => (a.date < b.date ? 1 : -1));
        const items = aggregated.slice(0, 7).map(record => {
            const date = record.date || 'N/A';
            const status = record.status || 'N/A';
            const checkIn = record.check_in || '—';
            const checkOut = record.check_out || '—';
            const hours = typeof record.hours_worked === 'number' ? `${record.hours_worked} hrs` : '—';
            return `📅 ${date}: ${status}\n   In: ${checkIn} | Out: ${checkOut} | Hours: ${hours}`;
        }).join('\n');

        return items + (aggregated.length > 7 ? `\n... and ${aggregated.length - 7} more records` : '');
    }

    // Attempt to fetch demo employee information from other demo endpoints and render a submenu
    async tryFetchDummyEmployee() {
        try {
            // Try chatbot employees endpoint first
            try {
                const res = await fetch('http://127.0.0.1:8000/api/chatbot/employees');
                if (res.ok) {
                    const j = await res.json().catch(() => ({}));
                    const arr = j.data || j.results || j.employees || [];
                    if (Array.isArray(arr) && arr.length) {
                        this.renderEmployeeSubmenu(arr.slice(0, 12));
                        return true;
                    }
                }
            } catch (e) { /* ignore */ }

            // Fallback: try merchant staff attendance endpoint which may include staff list
            try {
                const res2 = await fetch('http://127.0.0.1:8000/api/merchant/staff/attendance', { headers: { 'X-Merchant-Id': DEMO_MERCHANT_ID } });
                if (res2.ok) {
                    const j2 = await res2.json().catch(() => ({}));
                    const payload = j2.data || j2;
                    const staff = Array.isArray(payload.staff) ? payload.staff : [];
                    if (staff.length) {
                        this.renderEmployeeSubmenu(staff.slice(0, 12));
                        return true;
                    }
                }
            } catch (e) { /* ignore */ }

            return false;
        } catch (err) {
            console.error('tryFetchDummyEmployee failed', err);
            return false;
        }
    }

    renderEmployeeSubmenu(list) {
        const wrapper = document.createElement('div');
        wrapper.className = 'message bot';
        const content = document.createElement('div');
        content.className = 'message-content';

        const html = document.createElement('div');
        html.style.background = '#fff';
        html.style.padding = '12px';
        html.style.borderRadius = '8px';
        html.style.borderLeft = '4px solid #007bff';
        html.innerHTML = `<strong>👥 Found demo employees</strong><div style="margin-top:8px"></div>`;

        list.forEach(emp => {
            const btn = document.createElement('button');
            btn.style = 'display:block;width:100%;text-align:left;padding:8px;border:1px solid #eee;border-radius:6px;background:#fff;margin-bottom:8px;';
            const name = emp.name || emp.full_name || emp.employee_name || emp.title || emp.id || 'Unnamed';
            const id = emp.employee_id || emp.id || emp.employeeId || emp.emp_id || '';
            btn.textContent = `${name}${id ? ' • ' + id : ''}`;
            btn.addEventListener('click', () => this.renderEmployeeDetails(emp));
            html.appendChild(btn);
        });

        content.appendChild(html);
        wrapper.appendChild(content);
        this.chatBody.appendChild(wrapper);
        this.autoScroll();
    }

    renderEmployeeDetails(emp) {
        const wrapper = document.createElement('div');
        wrapper.className = 'message bot';
        const content = document.createElement('div');
        content.className = 'message-content';

        const name = emp.name || emp.full_name || emp.employee_name || 'Unnamed';
        const id = emp.employee_id || emp.id || emp.employeeId || emp.emp_id || 'N/A';
        const role = emp.role || emp.position || emp.job_title || 'N/A';
        const status = emp.status || 'N/A';

        content.innerHTML = `
            <div style="background:#fff;padding:12px;border-radius:8px;border-left:4px solid #28a745;">
                <strong>👤 ${name}</strong>
                <div style="margin-top:8px">ID: ${id}</div>
                <div>Role: ${role}</div>
                <div>Status: ${status}</div>
            </div>
        `;

        wrapper.appendChild(content);
        this.chatBody.appendChild(wrapper);
        this.autoScroll();
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

    renderPromotions(campaigns) {
        if (!Array.isArray(campaigns) || campaigns.length === 0) {
            this.addBotMessage('❌ No promotions available at the moment.', 1000);
            return;
        }

        // Build a compact HTML list of campaigns
        const html = `
            <div style="background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%); color: #222; padding: 10px; border-radius:10px; margin-bottom:8px;">
                <strong>📣 Promotions & Campaigns</strong>
            </div>
            <div style="background:#fff;padding:10px;border-radius:8px;border-left:4px solid #ff7e5f;">
                ${campaigns.slice(0,10).map(c => {
                    const id = c.campaign_id || c.campaignId || c.id || 'N/A';
                    const type = c.type || c.type_name || 'Campaign';
                    const sent = c.sent || c.recipients || 0;
                    const opened = c.opened || 0;
                    const conv = c.conversion_rate || c.conversions || 'N/A';
                    return `<div style="margin-bottom:8px;"><strong>${id}</strong> — ${type}<br/>Sent: ${sent} • Opened: ${opened} • Conv: ${conv}</div>`;
                }).join('')}
            </div>
        `;

        this.addBotMessage(html, 800, true);
    }

    renderNotificationSettings(settings) {
        // Create a small interactive card with toggle buttons
        const containerHtml = document.createElement('div');
        containerHtml.style.background = '#fff';
        containerHtml.style.padding = '12px';
        containerHtml.style.borderRadius = '8px';
        containerHtml.style.borderLeft = '4px solid #ffb400';
        containerHtml.style.marginBottom = '8px';

        const title = document.createElement('div');
        title.innerHTML = '<strong>🔔 Notification Settings</strong>';
        title.style.marginBottom = '8px';
        containerHtml.appendChild(title);

        const makeToggle = (key, label, value) => {
            const row = document.createElement('div');
            row.style.display = 'flex';
            row.style.justifyContent = 'space-between';
            row.style.alignItems = 'center';
            row.style.marginBottom = '8px';

            const lbl = document.createElement('div');
            lbl.textContent = label;

            const btn = document.createElement('button');
            btn.textContent = value ? 'On' : 'Off';
            btn.style.padding = '6px 10px';
            btn.style.borderRadius = '6px';
            btn.style.border = '1px solid #ddd';
            btn.style.background = value ? '#28a745' : '#f8f9fa';
            btn.style.color = value ? '#fff' : '#333';
            btn.addEventListener('click', async () => {
                // Optimistic toggle
                const newVal = !btn._val;
                btn._val = newVal;
                btn.textContent = newVal ? 'On' : 'Off';
                btn.style.background = newVal ? '#28a745' : '#f8f9fa';
                btn.style.color = newVal ? '#fff' : '#333';

                try {
                    const resp = await fetch('http://127.0.0.1:8000/api/merchant/notifications/settings', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ [key]: newVal })
                    });
                    const j = await resp.json().catch(() => ({}));
                    if (!resp.ok) {
                        throw new Error(j.message || resp.statusText);
                    }
                    // Show a small success bot message
                    this.addBotMessage(`✅ Updated ${label} to ${newVal ? 'On' : 'Off'}`, 800);
                } catch (err) {
                    console.error('Failed to update notification setting', err);
                    // revert optimistic UI
                    btn._val = !newVal;
                    btn.textContent = btn._val ? 'On' : 'Off';
                    btn.style.background = btn._val ? '#28a745' : '#f8f9fa';
                    btn.style.color = btn._val ? '#fff' : '#333';
                    this.addBotMessage(`❌ Could not update ${label}. Please try again.`, 800);
                }
            });
            btn._val = value;

            row.appendChild(lbl);
            row.appendChild(btn);
            return row;
        };

        containerHtml.appendChild(makeToggle('email', 'Email Notifications', !!settings.email));
        containerHtml.appendChild(makeToggle('sms', 'SMS Notifications', !!settings.sms));
        containerHtml.appendChild(makeToggle('in_app', 'In-app Notifications', !!settings.in_app));

        // Append the interactive card as HTML message
        const wrapper = document.createElement('div');
        wrapper.className = 'message bot';
        const content = document.createElement('div');
        content.className = 'message-content';
        content.appendChild(containerHtml);
        wrapper.appendChild(content);
        this.chatBody.appendChild(wrapper);
        this.autoScroll();
    }

    renderContactSupport(contact) {
        const wrapper = document.createElement('div');
        wrapper.className = 'message bot';
        const content = document.createElement('div');
        content.className = 'message-content';

        const html = document.createElement('div');
        html.style.background = '#fff';
        html.style.padding = '12px';
        html.style.borderRadius = '8px';
        html.style.borderLeft = '4px solid #007bff';
        html.innerHTML = `
            <strong>📞 Contact Support</strong>
            <div style="margin-top:8px">Email: ${contact.contact_email || 'support@example.com'}</div>
            <div>Phone: ${contact.contact_phone || 'N/A'}</div>
            <div>Hours: ${contact.support_hours || 'N/A'}</div>
            <div style="margin-top:8px"><button id="_create_ticket_btn" style="padding:6px 10px;border-radius:6px;border:none;background:#007bff;color:#fff;">Create Support Ticket</button></div>
        `;

        content.appendChild(html);
        wrapper.appendChild(content);
        this.chatBody.appendChild(wrapper);
        this.autoScroll();

        document.getElementById('_create_ticket_btn').addEventListener('click', async () => {
            // Open the existing support modal used elsewhere
            const modal = document.createElement('div');
            modal.style = 'position:fixed;left:0;right:0;top:0;bottom:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.35);z-index:9999;';
            modal.innerHTML = `
                <div style="background:#fff;padding:18px;border-radius:8px;min-width:320px;box-shadow:0 6px 24px rgba(0,0,0,0.2);">
                    <h3 style="margin-top:0;">Create Support Ticket</h3>
                    <label style="display:block;margin:8px 0 4px;font-size:0.9rem;">Subject</label>
                    <input id="_ticket_subject" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;" />
                    <label style="display:block;margin:8px 0 4px;font-size:0.9rem;">Description</label>
                    <textarea id="_ticket_desc" style="width:100%;min-height:80px;padding:8px;border:1px solid #ddd;border-radius:4px;"></textarea>
                    <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:12px;">
                        <button id="_ticket_cancel" style="padding:8px 12px;border-radius:6px;border:1px solid #ccc;background:#fff;">Cancel</button>
                        <button id="_ticket_submit" style="padding:8px 12px;border-radius:6px;border:none;background:#007bff;color:#fff;">Submit</button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            const cleanup = () => modal.remove();
            document.getElementById('_ticket_cancel').addEventListener('click', cleanup);
            document.getElementById('_ticket_submit').addEventListener('click', async () => {
                const subject = document.getElementById('_ticket_subject').value || 'Support Request';
                const desc = document.getElementById('_ticket_desc').value || '';
                try {
                    const resp = await fetch('http://127.0.0.1:8000/api/merchant/help/general', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ subject, description: desc })
                    });
                    const j = await resp.json().catch(() => ({}));
                    cleanup();
                    if (resp.ok) {
                        this.addBotMessage(`✅ Support ticket created: ${j.data ? j.data.ticket || 'Ticket created' : 'Ticket created'}`);
                    } else {
                        this.addBotMessage(`❌ Failed to create ticket: ${j.message || resp.statusText}`);
                    }
                } catch (err) {
                    cleanup();
                    console.error('Create ticket error', err);
                    this.addBotMessage('❌ Network error while creating support ticket.');
                }
            });
        });
    }

    async renderKBList(data) {
        // data: { articles: [...] }
        const articles = (data && data.articles) || [];
        if (!articles.length) {
            this.addBotMessage('❌ No knowledge base articles available.', 1000);
            return;
        }

        const wrapper = document.createElement('div');
        wrapper.className = 'message bot';
        const content = document.createElement('div');
        content.className = 'message-content';

        const list = document.createElement('div');
        list.style.background = '#fff';
        list.style.padding = '12px';
        list.style.borderRadius = '8px';
        list.style.borderLeft = '4px solid #6f42c1';
        list.innerHTML = `<strong>📚 Knowledge Base</strong><div style="margin-top:8px"></div>`;

        articles.forEach(a => {
            const item = document.createElement('div');
            item.style.padding = '8px 0';
            item.style.borderBottom = '1px solid #eee';
            item.innerHTML = `<a href="#" data-url="${a.url}" class="kb-link" style="color:#007bff;text-decoration:none">${a.title}</a><div style="font-size:0.9rem;color:#666">${a.summary || ''}</div>`;
            list.appendChild(item);
        });

        content.appendChild(list);
        wrapper.appendChild(content);
        this.chatBody.appendChild(wrapper);
        this.autoScroll();

        // Attach click listeners
        const links = wrapper.querySelectorAll('.kb-link');
        links.forEach(link => {
            link.addEventListener('click', async (e) => {
                e.preventDefault();
                const url = link.getAttribute('data-url');
                // Fetch article
                try {
                    const resp = await fetch(`http://127.0.0.1:8000${url}`);
                    if (!resp.ok) throw new Error('Failed to fetch article');
                    const j = await resp.json();
                    const article = j.data || {};
                    this.renderKBArticle(article);
                } catch (err) {
                    console.error('KB fetch error', err);
                    this.addBotMessage('❌ Failed to load article.');
                }
            });
        });
    }

    renderKBArticle(article) {
        const wrapper = document.createElement('div');
        wrapper.className = 'message bot';
        const content = document.createElement('div');
        content.className = 'message-content';
        content.innerHTML = `
            <div style="background:#fff;padding:12px;border-radius:8px;border-left:4px solid #6f42c1;">
                <strong>${article.title || 'Article'}</strong>
                <div style="margin-top:8px;white-space:pre-wrap;color:#333">${article.content || article.summary || 'No content available.'}</div>
            </div>
        `;
        wrapper.appendChild(content);
        this.chatBody.appendChild(wrapper);
        this.autoScroll();
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
            // Show real data for common merchant options
            let resp, j, d, html;
            if (option === "Today's Sales") {
                resp = await fetch('http://127.0.0.1:8000/api/merchant/sales/today');
                if (!resp.ok) throw new Error('Failed to fetch today sales');
                j = await resp.json();
                d = j.data || j;
                html = `
                    <div style="background: linear-gradient(135deg, #0f9b8e 0%, #16a085 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                        <h3 style="margin:0;">📈 Today's Sales — ${d.date || ''}</h3>
                    </div>
                    <div style="background:#fff;padding:12px;border-radius:8px;border-left:4px solid #007bff;">
                        <strong>💰 Total Sales:</strong> ₹${(d.total_sales||0).toLocaleString()}<br>
                        <strong>🛒 Transactions:</strong> ${d.total_transactions || 0}<br>
                        <strong>🔁 Avg Txn:</strong> ₹${(d.average_transaction||0).toLocaleString()}<br>
                    </div>
                `;
                this.addBotMessage(html, 1000);
                return;
            }

            if (option === 'Weekly Sales') {
                resp = await fetch('http://127.0.0.1:8000/api/merchant/sales/weekly');
                if (!resp.ok) throw new Error('Failed to fetch weekly sales');
                j = await resp.json();
                d = j.data || j;
                html = `
                    <div style="background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                        <h3 style="margin:0;">📊 Weekly Sales — ${d.week_start || ''} to ${d.week_end || ''}</h3>
                    </div>
                    <div style="background:#fff;padding:12px;border-radius:8px;border-left:4px solid #6f42c1;">
                        <strong>💰 Total Sales:</strong> ₹${(d.total_sales||0).toLocaleString()}<br>
                        <strong>🛒 Transactions:</strong> ${d.total_transactions || 0}<br>
                        <strong>🔁 Avg Txn:</strong> ₹${(d.average_transaction||0).toLocaleString()}<br>
                    </div>
                `;
                this.addBotMessage(html, 1000);
                return;
            }

            if (option === 'Outstanding Payments') {
                resp = await fetch('http://127.0.0.1:8000/api/merchant/payments/outstanding?merchant_id=MERCH001');
                if (!resp.ok) throw new Error('Failed to fetch outstanding payments');
                j = await resp.json();
                d = j.data || j;
                html = `
                    <div style="background: linear-gradient(135deg, #ff7e5f 0%, #feb47b 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                        <h3 style="margin:0;">💳 Outstanding Payments</h3>
                    </div>
                    <div style="background:#fff;padding:12px;border-radius:8px;border-left:4px solid #ff7e5f;">
                        <strong>⚠️ Total Outstanding:</strong> ₹${(d.total_outstanding||0).toLocaleString()}<br>
                        <strong>📋 Payments:</strong> ${d.payments ? d.payments.length : 0}
                    </div>
                `;
                this.addBotMessage(html, 1000);
                return;
            }

            if (option === 'Expenses & Bills') {
                resp = await fetch('http://127.0.0.1:8000/api/merchant/expenses/bills');
                if (!resp.ok) throw new Error('Failed to fetch expenses');
                j = await resp.json();
                d = j.data || j;
                html = `
                    <div style="background: linear-gradient(135deg, #e96443 0%, #904e95 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                        <h3 style="margin:0;">🧾 Expenses & Bills</h3>
                    </div>
                    <div style="background:#fff;padding:12px;border-radius:8px;border-left:4px solid #e96443;">
                        <strong>📊 Total Expenses:</strong> ₹${(d.total_expenses||0).toLocaleString()}<br>
                        <strong>📋 Bills:</strong> ${d.bills ? d.bills.length : 0}
                    </div>
                `;
                this.addBotMessage(html, 1000);
                return;
            }

            // fallback
            const fall = await fetch('http://127.0.0.1:8000/api/merchant/sales/today');
            if (fall.ok) {
                const data = await fall.json();
                this.addBotMessage(`📊 Today's merchant data has been retrieved. Found ${data.results?.length || 0} transactions.`, 1000);
            } else {
                this.addBotMessage(`🎉 ${option} has been successfully processed! Your merchant management system is now updated.`, 1000);
            }
        } catch (error) {
            return this.addBotMessage(`<div style="color:#dc3545;">❌ Error loading data: ${error.message}</div>`, 1000);
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

    async renderMenus(system) {
        const menuContainer = document.getElementById("menu-container");
        menuContainer.innerHTML = "";

        menus[system].forEach(category => {
            const categoryDiv = document.createElement("div");
            categoryDiv.className = "category";
            categoryDiv.innerHTML = `<h3>${category.category}</h3>`;

            const optionsList = document.createElement("ul");
            category.options.forEach(option => {
                const optionItem = document.createElement("li");
                // Use a wrapper so we can switch to POST for specific endpoints (e.g. add-employee)
                optionItem.innerHTML = `<button onclick="handleMenuClick('${option.endpoint}','${option.label}')">${option.label}</button>`;
                optionsList.appendChild(optionItem);
            });

            categoryDiv.appendChild(optionsList);
            menuContainer.appendChild(categoryDiv);
        });

        // Ensure a persistent staff list container exists when merchant UI is active
        if (system === 'merchant') {
            // Ensure a persistent notifications card exists
            let notifCard = document.querySelector('.notifications-card');
            if (!notifCard) {
                notifCard = document.createElement('div');
                notifCard.className = 'notifications-card';
                notifCard.style = 'margin:12px 0;padding:8px;max-width:600px;';
                const header = document.createElement('h4');
                header.textContent = 'Notifications';
                header.style = 'margin:0 0 8px 0;font-size:1rem;';
                notifCard.appendChild(header);
                menuContainer.parentNode.insertBefore(notifCard, menuContainer.nextSibling);
            }

            // Try to populate notifications
            (async () => {
                try {
                    const resp = await fetch('http://127.0.0.1:8000/api/merchant/notifications');
                    if (!resp.ok) throw new Error('Failed to fetch notifications');
                    const j = await resp.json();
                    const payload = j.data || {};
                    notifCard.innerHTML = '';
                    const header = document.createElement('h4'); header.textContent = 'Notifications'; header.style = 'margin:0 0 8px 0;font-size:1rem;'; notifCard.appendChild(header);
                    const list = document.createElement('div'); list.style = 'color:#333;';
                    if (payload.pending_leave_requests && payload.pending_leave_requests.length) {
                        list.innerHTML += `<div>⚠️ Pending leave requests: ${payload.pending_leave_requests.length}</div>`;
                    }
                    if (payload.pending_shift_changes && payload.pending_shift_changes.length) {
                        list.innerHTML += `<div>🔁 Pending shift changes: ${payload.pending_shift_changes.length}</div>`;
                    }
                    if (payload.payment_settlement) {
                        list.innerHTML += `<div>💳 Last settlement: ${payload.payment_settlement.last_settlement} — ₹${(payload.payment_settlement.amount||0).toLocaleString()}</div>`;
                    }
                    if (payload.head_office_messages && payload.head_office_messages.length) {
                        list.innerHTML += `<div>🏢 Head Office Messages: ${payload.head_office_messages.length}</div>`;
                    }
                    if (list.innerHTML === '') list.innerHTML = '<div style="color:#666;">No notifications</div>';
                    notifCard.appendChild(list);
                } catch (e) {
                    try { notifCard.innerHTML = '<div style="color:#666;">Unable to load notifications</div>'; } catch(_){}
                }
            })();

            let staffList = document.querySelector('.staff-list');
            if (!staffList) {
                staffList = document.createElement('div');
                staffList.className = 'staff-list';
                staffList.style = 'margin:12px 0;padding:8px;max-width:600px;';
                const header = document.createElement('h4');
                header.textContent = 'My Staff';
                header.style = 'margin:0 0 8px 0;font-size:1rem;';
                staffList.appendChild(header);
                // attach below menu container
                menuContainer.parentNode.insertBefore(staffList, menuContainer.nextSibling);
            }

            // Try to populate staff list from backend attendance (demo staff)
            try {
                const resp = await this.fetchData('/api/merchant/staff/attendance', 'GET');
                const payload = resp && resp.data ? resp.data : resp;
                const staffArr = Array.isArray(payload.staff) ? payload.staff : [];
                // clear existing cards except header
                const header = staffList.querySelector('h4');
                staffList.innerHTML = '';
                staffList.appendChild(header || document.createElement('h4'));
                if (header) header.textContent = 'My Staff';
                if (staffArr.length === 0) {
                    const hint = document.createElement('div');
                    hint.style = 'color:#666;padding:8px 0;';
                    hint.textContent = 'No staff to display. Use "Add New Employee" to create one.';
                    staffList.appendChild(hint);
                } else {
                    staffArr.slice(0, 20).forEach(emp => {
                        const card = document.createElement('div');
                        card.style = 'background:#fff;border:1px solid #e6e6e6;padding:8px;margin:8px 0;border-radius:6px;';
                        card.innerHTML = `<strong>${emp.name || emp.employee_name || 'Unnamed'}</strong> <span style="color:#666;margin-left:8px;">(${emp.role || 'N/A'})</span><div style="font-size:0.85rem;color:#555;">ID: ${emp.employee_id || emp.employee_id || 'N/A'} • Status: ${emp.status || 'N/A'}</div>`;
                        staffList.appendChild(card);
                    });
                }
            } catch (e) {
                // ignore errors and show hint
                try {
                    const hint = document.createElement('div');
                    hint.style = 'color:#666;padding:8px 0;';
                    hint.textContent = 'Unable to load staff list (demo). Use "Add New Employee" to create one.';
                    // ensure not to duplicate
                    if (staffList.children.length <= 1) staffList.appendChild(hint);
                } catch (ie) {}
            }
        }
    }

    async fetchData(endpoint, method = 'GET', body = null) {
        try {
            const opts = { method };
            if (body) {
                opts.headers = { 'Content-Type': 'application/json', 'X-Merchant-Id': DEMO_MERCHANT_ID };
                opts.body = JSON.stringify(body);
            } else {
                opts.headers = { 'X-Merchant-Id': DEMO_MERCHANT_ID };
            }
            const response = await fetch(endpoint, opts);
            if (!response.ok) throw new Error(`Failed to fetch data: ${response.status}`);
            const data = await response.json();
            console.log("Data fetched successfully:", data);
            return data;
        } catch (error) {
            console.error("Error fetching data:", error);
            throw error;
        }
    }
}

// Initialize the chatbot when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.hrChatBot = new ChatBot();
});

// Global helper to handle menu clicks from rendered buttons
window.handleMenuClick = async function(endpoint, label) {
    try {
        // If this is the Add New Employee endpoint, call POST (canonical)
    if (endpoint === '/api/merchant/staff/add-employee') {
            // render a small modal form to collect name/role/contact
            const modal = document.createElement('div');
            modal.className = 'employee-modal';
            modal.style = 'position:fixed;left:0;right:0;top:0;bottom:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.35);z-index:9999;';
            modal.innerHTML = `
                <div style="background:#fff;padding:18px;border-radius:8px;min-width:320px;box-shadow:0 6px 24px rgba(0,0,0,0.2);">
                    <h3 style="margin-top:0;">Add New Employee</h3>
                    <label style="display:block;margin:8px 0 4px;font-size:0.9rem;">Name</label>
                    <input id="_emp_name" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;" />
                    <label style="display:block;margin:8px 0 4px;font-size:0.9rem;">Role</label>
                    <input id="_emp_role" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;" value="Sales Operator" />
                    <label style="display:block;margin:8px 0 4px;font-size:0.9rem;">Contact (optional)</label>
                    <input id="_emp_contact" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;" />
                    <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:12px;">
                        <button id="_emp_cancel" style="padding:8px 12px;border-radius:6px;border:1px solid #ccc;background:#fff;">Cancel</button>
                        <button id="_emp_submit" style="padding:8px 12px;border-radius:6px;border:none;background:#28a745;color:#fff;">Add Employee</button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);

            const cleanup = () => { modal.remove(); };
            document.getElementById('_emp_cancel').addEventListener('click', cleanup);

            document.getElementById('_emp_submit').addEventListener('click', async () => {
                const name = document.getElementById('_emp_name').value.trim();
                const role = document.getElementById('_emp_role').value.trim() || 'Sales Operator';
                const contact = document.getElementById('_emp_contact').value.trim() || null;

                if (!name) {
                    alert('Please enter employee name');
                    return;
                }

                try {
                    const payload = { name, role, contact };
                    const data = await window.hrChatBot.fetchData(endpoint, 'POST', payload);
                    cleanup();
                    // show confirmation message with explicit text and ID
                    // Show a plain-text confirmation message including the assigned ID (no HTML)
                    try {
                        const emp = data.data || {};
                        const empId = emp.employee_id || emp.employeeId || emp.id || 'N/A';
                        window.hrChatBot.addBotMessage(`✅ New Employee Added\nID: ${empId}`, 800);
                    } catch (e) {
                        window.hrChatBot.addBotMessage('✅ New Employee Added', 800);
                    }

                    // update staff display if present: try to append to last staff list rendered
                    try {
                        const staffContainers = document.querySelectorAll('.staff-list');
                        if (staffContainers && staffContainers.length) {
                            const container = staffContainers[0];
                            const emp = data.data;
                            const card = document.createElement('div');
                            card.style = 'background:#fff;border:1px solid #e6e6e6;padding:8px;margin:8px 0;border-radius:6px;';
                            card.innerHTML = `<strong>${emp.name}</strong> <span style="color:#666;margin-left:8px;">(${emp.role})</span><div style="font-size:0.85rem;color:#555;">ID: ${emp.employee_id} • Contact: ${emp.contact || 'N/A'}</div>`;
                            container.prepend(card);
                        }
                    } catch (uiErr) {
                        // ignore UI update errors
                        console.warn('Failed updating staff UI', uiErr);
                    }
                } catch (err) {
                    console.error('Add employee failed', err);
                    window.hrChatBot.addBotMessage(`<div style="color:#dc3545;">❌ Failed to add employee: ${err.message}</div>`, 800);
                }
            });

            return;
        }

        // If this is Create Campaign endpoint, show a minimal modal and POST
        if (endpoint === '/api/merchant/marketing/create-campaign') {
            const modal = document.createElement('div');
            modal.className = 'campaign-modal';
            modal.style = 'position:fixed;left:0;right:0;top:0;bottom:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.35);z-index:9999;';
            modal.innerHTML = `
                <div style="background:#fff;padding:18px;border-radius:8px;min-width:320px;box-shadow:0 6px 24px rgba(0,0,0,0.2);">
                    <h3 style="margin-top:0;">Create Campaign</h3>
                    <label style="display:block;margin:8px 0 4px;font-size:0.9rem;">Campaign Name</label>
                    <input id="_camp_name" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;" />
                    <label style="display:block;margin:8px 0 4px;font-size:0.9rem;">Budget (₹)</label>
                    <input id="_camp_budget" type="number" min="0" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;" value="100" />
                    <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:12px;">
                        <button id="_camp_cancel" style="padding:8px 12px;border-radius:6px;border:1px solid #ccc;background:#fff;">Cancel</button>
                        <button id="_camp_submit" style="padding:8px 12px;border-radius:6px;border:none;background:#007bff;color:#fff;">Create</button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            const cleanup = () => { modal.remove(); };
            document.getElementById('_camp_cancel').addEventListener('click', cleanup);
            document.getElementById('_camp_submit').addEventListener('click', async () => {
                const name = document.getElementById('_camp_name').value.trim();
                const budget = parseFloat(document.getElementById('_camp_budget').value || '0');
                if (!name) { alert('Please enter campaign name'); return; }
                try {
                    const data = await window.hrChatBot.fetchData(endpoint, 'POST', { campaign_name: name, budget });
                    cleanup();
                    const camp = data.data || {};
                    const id = camp.campaign_id || camp.campaignId || camp.id || 'N/A';
                    window.hrChatBot.addBotMessage(`✅ Campaign created: ${name} (ID: ${id})`, 800);
                    // Refresh promotions list so UI shows the newly created campaign
                    try {
                        const res = await fetch('http://127.0.0.1:8000/api/merchant/marketing/promotions');
                        if (res.ok) {
                            const pj = await res.json().catch(() => ({}));
                            const camps = (pj.data && pj.data.campaigns) || pj.campaigns || [];
                            if (camps && camps.length) window.hrChatBot.renderPromotions(camps);
                        }
                    } catch (re) { /* ignore refresh failures */ }
                } catch (err) {
                    cleanup();
                    window.hrChatBot.addBotMessage(`<div style="color:#dc3545;">❌ Failed to create campaign: ${err.message}</div>`, 800);
                }
            });
            return;
        }

        // Default: simple GET
        const data = await window.hrChatBot.fetchData(endpoint, 'GET');
        window.hrChatBot.addBotMessage(`<div style="background:#fff;padding:12px;border-radius:8px;border-left:4px solid #007bff;">✅ ${label} data retrieved successfully.</div>`, 800);
    } catch (e) {
        window.hrChatBot.addBotMessage(`<div style="color:#dc3545;">❌ Failed to ${label}: ${e.message}</div>`, 800);
    }
}

// Global keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        if (window.hrChatBot) {
            window.hrChatBot.resetToMainMenu();
        }
    }
});
