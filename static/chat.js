let categories = [];
// Force cache refresh - Leave application form implemented - FINAL FIX
// Timestamp: 1755173800

async function fetchCategories(companyType = "pos_youhr", role = "employee") {
    try {
        const response = await fetch(`http://127.0.0.1:8000/api/chatbot/menus-with-submenus?company_type=${companyType}&role=${role}`);
        if (!response.ok) throw new Error("Failed to fetch menu data");
        const data = await response.json();
        console.log("Fetched data:", data); // Debug log
        
        // API returns an array of menu objects
        categories = Array.isArray(data)
            ? data.map(menu => ({
                key: menu.menu_key || menu.key || menu.name,
                label: menu.menu_title || menu.label || menu.name,
                icon: menu.menu_icon || "",
                color: menu.color || "#4F46E5",
                options: (menu.submenus || []).map(sub => sub.submenu_title || sub.label || sub.name || sub)
            }))
            : [];
        
        console.log("Processed categories:", categories); // Debug log
    } catch (e) {
        categories = [];
        console.error("Error fetching categories:", e);
    }
}

// Sound effects (optional)
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
        audio.play().catch(() => {}); // Ignore errors
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

        // Fetch categories from API, then show welcome message
        await fetchCategories();
        this.showWelcomeMessage();
    }

    showTypingIndicator() {
        if (this.currentTypingIndicator) {
            this.removeTypingIndicator();
        }

        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.innerHTML = `
            <span>AI is typing</span>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        
        this.chatBody.appendChild(typingDiv);
        this.currentTypingIndicator = typingDiv;
        this.autoScroll();
        
        return typingDiv;
    }

    removeTypingIndicator() {
        if (this.currentTypingIndicator && this.currentTypingIndicator.parentNode) {
            this.currentTypingIndicator.parentNode.removeChild(this.currentTypingIndicator);
            this.currentTypingIndicator = null;
        }
    }

    autoScroll(smooth = true) {
        if (smooth) {
            this.chatBody.scrollTo({
                top: this.chatBody.scrollHeight,
                behavior: 'smooth'
            });
        } else {
            this.chatBody.scrollTop = this.chatBody.scrollHeight;
        }
    }

    addBotMessage(message, delay = 1500, isHTML = false) {
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
        
        // Welcome message with staggered animation
        setTimeout(() => {
            this.addBotMessage('Hi there! 👋\nHow can I help you today?\n\nPlease select a category:', 500);
            
            // Show categories after welcome message
            setTimeout(() => {
                this.showCategories();
            }, 2200);
        }, 300);
    }

    showCategories() {
        console.log("showCategories called, categories:", categories); // Debug log
        
        const categoriesContainer = document.createElement('div');
        categoriesContainer.className = 'categories-container';
        categoriesContainer.style.opacity = '0';
        categoriesContainer.style.transform = 'translateY(20px)';

        if (!categories.length) {
            console.log("No categories available"); // Debug log
            const errorMsg = document.createElement('div');
            errorMsg.textContent = "No categories available. Please try again later.";
            errorMsg.style.color = "#DC2626";
            categoriesContainer.appendChild(errorMsg);
            
            // Make sure the error message is visible
            categoriesContainer.style.opacity = '1';
            categoriesContainer.style.transform = 'translateY(0)';
        } else {
            console.log("Displaying", categories.length, "categories"); // Debug log
            categories.forEach((category, index) => {
                setTimeout(() => {
                    const categoryButton = document.createElement('button');
                    categoryButton.className = 'category-button';
                    categoryButton.innerHTML = `
                        <span class="category-icon">${category.icon}</span>
                        ${category.label.replace(category.icon, '').trim()}
                    `;

                    // Add click handler
                    categoryButton.addEventListener('click', () => {
                        this.handleCategorySelection(category);
                    });

                    // Add hover effects
                    categoryButton.addEventListener('mouseenter', () => {
                        categoryButton.style.transform = 'translateY(-4px) scale(1.02)';
                    });

                    categoryButton.addEventListener('mouseleave', () => {
                        categoryButton.style.transform = 'translateY(0) scale(1)';
                    });

                    categoriesContainer.appendChild(categoryButton);

                    // Animate container on first item
                    if (index === 0) {
                        setTimeout(() => {
                            categoriesContainer.style.transition = 'all 0.5s ease';
                            categoriesContainer.style.opacity = '1';
                            categoriesContainer.style.transform = 'translateY(0)';
                        }, 100);
                    }

                    this.autoScroll();
                }, index * 200); // Staggered animation
            });
        }

        this.chatBody.appendChild(categoriesContainer);
    }

    handleCategorySelection(category) {
        // Add user message
        this.addUserMessage(category.label);
        
        // Smooth scroll after user message
        setTimeout(() => {
            this.autoScroll();
        }, 100);
        
        // Show typing and then subcategories
        setTimeout(() => {
            this.removeTypingIndicator();
            this.showSubcategories(category);
        }, 1200);
    }

    showSubcategories(category) {
        const botBubble = document.createElement('div');
        botBubble.className = 'chat-bubble bot';
        
        // Create header
        const header = document.createElement('div');
        header.style.marginBottom = '16px';
        header.innerHTML = `
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 1.2em; margin-right: 8px;">${category.icon}</span>
                <strong>${category.label.replace(category.icon, '').trim()}</strong>
            </div>
            <div style="font-size: 0.9em; opacity: 0.9;">Please select an option:</div>
        `;
        botBubble.appendChild(header);
        
        // Create options container
        const optionsContainer = document.createElement('div');
        optionsContainer.style.display = 'flex';
        optionsContainer.style.flexDirection = 'column';
        optionsContainer.style.gap = '8px';
        
        category.options.forEach((option, index) => {
            setTimeout(() => {
                const optionBtn = document.createElement('button');
                optionBtn.className = 'sub-option-btn';
                optionBtn.textContent = option;
                optionBtn.style.opacity = '0';
                optionBtn.style.transform = 'translateX(-10px)';
                
                optionBtn.addEventListener('click', () => {
                    this.handleSubcategorySelection(option, category);
                    
                    // Smooth scroll after selection
                    setTimeout(() => {
                        this.autoScroll();
                    }, 100);
                    
                    // Disable all buttons and highlight selected
                    optionsContainer.querySelectorAll('button').forEach(btn => {
                        btn.disabled = true;
                        btn.style.opacity = '0.5';
                    });
                    optionBtn.style.opacity = '1';
                    optionBtn.style.background = 'linear-gradient(135deg, #10d876 0%, #059669 100%)';
                    optionBtn.style.color = '#fff';
                });
                
                optionsContainer.appendChild(optionBtn);
                
                // Animate button
                setTimeout(() => {
                    optionBtn.style.transition = 'all 0.3s ease';
                    optionBtn.style.opacity = '1';
                    optionBtn.style.transform = 'translateX(0)';
                }, 50);
                
            }, index * 150);
        });
        
        botBubble.appendChild(optionsContainer);
        
        // Add go back button
        setTimeout(() => {
            const goBackBtn = document.createElement('button');
            goBackBtn.className = 'go-back-btn';
            goBackBtn.innerHTML = '← Go Back';
            goBackBtn.addEventListener('click', () => {
                this.resetToMainMenu();
            });
            botBubble.appendChild(goBackBtn);
        }, category.options.length * 150 + 300);
        
        this.chatBody.appendChild(botBubble);
        
        // Smooth scroll to show the new subcategories
        setTimeout(() => {
            this.autoScroll();
        }, 100);
        
        // Additional scroll after all options are loaded
        setTimeout(() => {
            this.autoScroll();
        }, category.options.length * 150 + 500);
    }

    async handleSubcategorySelection(option, category) {
        // Add user message
        this.addUserMessage(option);
        
        // Show processing message
        this.addBotMessage(`Perfect! I'm processing your request for "${option}"...`, 1000);
        
        // Show result based on the specific option
        setTimeout(async () => {
            let resultMessage;
            
            console.log("Processing option:", option); // Debug log
            console.log("Checking for attendance history:", option.toLowerCase().includes('attendance history'));
            console.log("Checking for apply for leave:", option.toLowerCase().includes('apply for leave'));
            console.log("Checking for view payslips:", option.toLowerCase().includes('view payslips'));
            
            // Check if this needs special async handling
            if (option.toLowerCase().includes('attendance history') || option.toLowerCase().includes('view attendance history')) {
                resultMessage = await this.fetchAttendanceHistory();
            } else if (option.toLowerCase().includes('apply for leave') || option.toLowerCase().includes('apply leave')) {
                console.log("Showing leave application form"); // Debug log
                resultMessage = this.showLeaveApplicationForm();
            } else if (option.toLowerCase().includes('view payslips') || option === "View payslips") {
                console.log("Fetching payslips"); // Debug log
                resultMessage = await this.fetchPayslips();
            } else {
                resultMessage = await this.generateResponseForOption(option, category);
            }
            
            this.addBotMessage(resultMessage, 1500, true);
            
            // Show action buttons (only if it's not a form)
            if (!option.toLowerCase().includes('apply for leave')) {
                setTimeout(() => {
                    this.showActionButtons();
                }, 3200);
            }
        }, 2500);
    }

    async generateResponseForOption(option, category) {
        console.log("generateResponseForOption called with:", option, category); // Debug log
        
        // PRIORITY CHECK: Handle leave application form first
        if (option === "Apply for new leave" || option.toLowerCase().includes("apply for new leave")) {
            console.log("LEAVE APPLICATION DETECTED - showing form"); // Debug log
            return this.showLeaveApplicationForm();
        }
        
        // PRIORITY CHECK: Handle payslips view
        if (option === "View payslips" || option.toLowerCase().includes("view payslips")) {
            console.log("PAYSLIPS VIEW DETECTED - fetching payslips"); // Debug log
            return await this.fetchPayslips();
        }
        
        const now = new Date();
        const currentDate = now.toLocaleDateString();
        const currentTime = now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        console.log("Current time:", currentTime, "Hour:", now.getHours()); // Debug log
        
        // Attendance responses
        if (option.toLowerCase().includes('attendance status') || option.toLowerCase().includes('check my attendance')) {
            const hour = now.getHours();
            const isCheckedIn = hour >= 9; // Assume check-in after 9 AM
            const checkInTime = isCheckedIn ? "9:15 AM" : "Not checked in";
            const status = isCheckedIn ? "Present" : "Not checked in";
            const hoursWorked = isCheckedIn ? `${hour - 9}.5 hours` : "0 hours";
            
            return `
                <div style="background: linear-gradient(135deg, #0f9b8e 0%, #16a085 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                    <h4 style="margin: 0 0 8px 0;">📅 Your Attendance Status</h4>
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin: 8px 0;">
                        <strong>Today (${currentDate}):</strong><br>
                        ${isCheckedIn ? '✅' : '❌'} Status: ${status}<br>
                        🕘 Check-in: ${checkInTime}<br>
                        ⏱️ Hours worked: ${hoursWorked}<br>
                        📍 Location: ${isCheckedIn ? 'Office' : 'Not at office'}
                    </div>
                    <div style="font-size: 0.9em; opacity: 0.9;">
                        This week: 32.5 hours | This month: 158 hours
                    </div>
                </div>
                <div>Is there anything else I can help you with?</div>
            `;
        }
        
        if (option.toLowerCase().includes('mark attendance') || option.toLowerCase().includes('check-in') || option.toLowerCase().includes('check-out')) {
            const hour = now.getHours();
            const isWorkingHours = hour >= 9 && hour <= 18;
            const action = hour < 12 ? "Check-in" : "Check-out";
            const message = hour < 12 ? "Good morning! Have a productive day!" : "Good evening! Thanks for your hard work today!";
            
            return `
                <div style="background: linear-gradient(135deg, #10d876 0%, #059669 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                    <h4 style="margin: 0 0 8px 0;">✅ Attendance Marked Successfully!</h4>
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin: 8px 0;">
                        📅 Date: ${currentDate}<br>
                        🕘 Time: ${currentTime}<br>
                        📍 Location: Office<br>
                        💼 Action: ${action} recorded<br>
                        ⏰ Status: ${isWorkingHours ? 'On time' : (hour < 9 ? 'Early arrival' : 'After hours')}
                    </div>
                </div>
                <div>${message} 😊</div>
            `;
        }
        
        if (option.toLowerCase().includes('working hours')) {
            return `
                <div style="background: linear-gradient(135deg, #a29bfe 0%, #6c5ce7 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                    <h4 style="margin: 0 0 8px 0;">⏰ Your Working Hours</h4>
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin: 8px 0;">
                        📅 <strong>Regular Schedule:</strong><br>
                        Monday - Friday: 9:00 AM - 6:00 PM<br>
                        Saturday: 9:00 AM - 1:00 PM<br>
                        Sunday: Off<br><br>
                        ⏱️ <strong>Current Week:</strong><br>
                        Total hours: 42 hours<br>
                        Overtime: 2 hours<br>
                        Break time: 5 hours
                    </div>
                </div>
                <div>Need to request schedule changes? Contact your manager.</div>
            `;
        }
        
        if (option.toLowerCase().includes('late arrival') || option.toLowerCase().includes('late status')) {
            const hour = now.getHours();
            const isLate = hour > 9;
            
            return `
                <div style="background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                    <h4 style="margin: 0 0 8px 0;">⏰ Late Arrival Status</h4>
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin: 8px 0;">
                        📅 <strong>Today:</strong> ${isLate ? '⚠️ Arrived late' : '✅ On time'}<br>
                        🕘 Expected: 9:00 AM<br>
                        🕐 Actual: ${currentTime}<br><br>
                        📊 <strong>This Month:</strong><br>
                        Late arrivals: 3 times<br>
                        Average delay: 15 minutes<br>
                        Status: ${isLate ? 'Needs improvement' : 'Good performance'}
                    </div>
                </div>
                <div>${isLate ? 'Please try to arrive on time. Contact HR if you have scheduling issues.' : 'Great job maintaining punctuality! 👍'}</div>
            `;
        }
        
        if (option.toLowerCase().includes('attendance correction') || option.toLowerCase().includes('request correction')) {
            return `
                <div style="background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                    <h4 style="margin: 0 0 8px 0;">� Attendance Correction Request</h4>
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin: 8px 0;">
                        Your correction request has been submitted:<br><br>
                        📅 Date: ${currentDate}<br>
                        🔄 Requested change: Missing check-out<br>
                        ⏰ Correct time: 6:00 PM<br>
                        📋 Reason: Forgot to mark attendance<br>
                        👨‍💼 Approver: Manager<br>
                        📊 Status: Pending review
                    </div>
                </div>
                <div>Your manager will review and approve the correction within 24 hours.</div>
            `;
        }
        
        if (option.toLowerCase().includes('leave history')) {
            return `
                <div style="background: linear-gradient(135deg, #00b894 0%, #00cec9 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                    <h4 style="margin: 0 0 8px 0;">📋 Recent Leave History</h4>
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin: 8px 0; font-size: 0.9em;">
                        <div style="margin-bottom: 8px;">🏖️ <strong>July 15-19, 2025</strong><br>Annual Leave - 5 days (Approved)</div>
                        <div style="margin-bottom: 8px;">🤒 <strong>June 28, 2025</strong><br>Sick Leave - 1 day (Approved)</div>
                        <div style="margin-bottom: 8px;">👨‍👩‍👧‍� <strong>May 10, 2025</strong><br>Personal Leave - 1 day (Approved)</div>
                        <div>🎉 <strong>April 22, 2025</strong><br>Comp Off - 1 day (Approved)</div>
                    </div>
                    <div style="font-size: 0.9em; opacity: 0.9;">
                        Total leaves taken this year: 8 days
                    </div>
                </div>
                <div>All your leave requests have been approved. Great planning! 👍</div>
            `;
        }
        
        if (option.toLowerCase().includes('cancel leave')) {
            return `
                <div style="background: linear-gradient(135deg, #fab1a0 0%, #e17055 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                    <h4 style="margin: 0 0 8px 0;">❌ Cancel Leave Request</h4>
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin: 8px 0;">
                        Your pending leave request has been cancelled:<br><br>
                        📅 Cancelled dates: Aug 20-22, 2025<br>
                        📋 Type: Annual Leave<br>
                        🕘 Cancelled on: ${currentDate} at ${currentTime}<br>
                        💰 Leave balance restored: 3 days<br>
                        📧 Notification sent to: Manager
                    </div>
                </div>
                <div>You can apply for new leave anytime. Your leave balance has been restored.</div>
            `;
        }
        
        if (option.toLowerCase().includes('leave approval status') || option.toLowerCase().includes('leave status')) {
            return `
                <div style="background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                    <h4 style="margin: 0 0 8px 0;">� Leave Approval Status</h4>
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin: 8px 0;">
                        <div style="margin-bottom: 10px;">
                            📅 <strong>Aug 25-27, 2025</strong><br>
                            📋 Annual Leave - 3 days<br>
                            ⏳ Status: <span style="color: #fdcb6e;">Pending Manager Approval</span>
                        </div>
                        <div style="margin-bottom: 10px;">
                            📅 <strong>Sep 15, 2025</strong><br>
                            📋 Personal Leave - 1 day<br>
                            ✅ Status: <span style="color: #00b894;">Approved</span>
                        </div>
                    </div>
                    <div style="font-size: 0.9em; opacity: 0.9;">
                        You'll receive email notifications when status changes.
                    </div>
                </div>
                <div>Your approved leaves are confirmed. Pending requests are being reviewed.</div>
            `;
        }
        
        if (option.toLowerCase().includes('leave calendar') || option.toLowerCase().includes('download leave calendar')) {
            return `
                <div style="background: linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                    <h4 style="margin: 0 0 8px 0;">📅 Leave Calendar Download</h4>
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin: 8px 0;">
                        Your personalized leave calendar is ready:<br><br>
                        📊 File: Leave_Calendar_2025.pdf<br>
                        📝 Contains: All approved leaves, holidays, planned leaves<br>
                        📅 Period: Jan 2025 - Dec 2025<br>
                        📧 Sent to: your-email@company.com<br>
                        🔗 Download link valid for: 7 days
                    </div>
                </div>
                <div>Check your email for the download link! You can also sync this with your personal calendar. 📱</div>
            `;
        }
        
        // Leave responses
        if (option.toLowerCase().includes('leave balance')) {
            return `
                <div style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: #333; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                    <h4 style="margin: 0 0 8px 0;">🏖️ Your Leave Balance</h4>
                    <div style="background: rgba(255,255,255,0.3); padding: 12px; border-radius: 8px; margin: 8px 0;">
                        <div style="margin-bottom: 6px;">🌴 Annual Leave: 18 days remaining</div>
                        <div style="margin-bottom: 6px;">🤒 Sick Leave: 12 days remaining</div>
                        <div style="margin-bottom: 6px;">👶 Personal Leave: 5 days remaining</div>
                        <div>🎉 Comp Off: 3 days remaining</div>
                    </div>
                    <div style="font-size: 0.9em; opacity: 0.8;">
                        Total: 38 days available | Expires: Dec 31, 2025
                    </div>
                </div>
                <div>Want to apply for leave? Select "Apply for new leave".</div>
            `;
        }
        
        // Payroll responses
        if (option.toLowerCase().includes('salary details') || option.toLowerCase().includes('salary')) {
            return `
                <div style="background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%); color: #333; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                    <h4 style="margin: 0 0 8px 0;">💰 Current Salary Details</h4>
                    <div style="background: rgba(255,255,255,0.3); padding: 12px; border-radius: 8px; margin: 8px 0;">
                        💼 Basic Salary: $4,500<br>
                        🏠 HRA: $900<br>
                        🚗 Transport: $300<br>
                        📱 Special Allowance: $800<br>
                        <hr style="margin: 8px 0; opacity: 0.3;">
                        <strong>💵 Gross Salary: $6,500</strong>
                    </div>
                    <div style="font-size: 0.9em; opacity: 0.8;">
                        Next review: January 2026
                    </div>
                </div>
                <div>Need your payslip? Check "View payslips" option.</div>
            `;
        }
        
        if (option.toLowerCase().includes('tax deductions') || option.toLowerCase().includes('tax')) {
            return `
                <div style="background: linear-gradient(135deg, #00cec9 0%, #55a3ff 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                    <h4 style="margin: 0 0 8px 0;">� Tax Deductions (July 2025)</h4>
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin: 8px 0;">
                        📊 <strong>Tax Breakdown:</strong><br>
                        Federal Tax: $650<br>
                        State Tax: $150<br>
                        Social Security: $403<br>
                        Medicare: $94<br>
                        <hr style="margin: 8px 0; opacity: 0.3;">
                        💰 <strong>Total Deductions: $1,297</strong><br><br>
                        📋 Tax Status: Single<br>
                        🏠 Exemptions: 1<br>
                        📄 Form: W-4 on file
                    </div>
                </div>
                <div>Need tax documents? Contact payroll department. 📧</div>
            `;
        }
        
        if (option.toLowerCase().includes('bonus info') || option.toLowerCase().includes('bonus')) {
            return `
                <div style="background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%); color: #333; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                    <h4 style="margin: 0 0 8px 0;">🎉 Bonus Information</h4>
                    <div style="background: rgba(255,255,255,0.3); padding: 12px; border-radius: 8px; margin: 8px 0;">
                        💰 <strong>2025 Performance Bonus:</strong><br>
                        Q1 Bonus: $1,200 (Paid)<br>
                        Q2 Bonus: $1,500 (Paid)<br>
                        Q3 Bonus: $800 (Pending)<br>
                        Q4 Bonus: TBD<br><br>
                        � <strong>Annual Targets:</strong><br>
                        Performance Rating: 4.2/5<br>
                        Target Achievement: 85%<br>
                        Expected Year-end Bonus: $2,000
                    </div>
                </div>
                <div>Keep up the great work! Your performance is above average. 🌟</div>
            `;
        }
        
        if (option.toLowerCase().includes('bank details') || option.toLowerCase().includes('bank account')) {
            return `
                <div style="background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                    <h4 style="margin: 0 0 8px 0;">🏦 Bank Account Details</h4>
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin: 8px 0;">
                        🏦 <strong>Primary Account:</strong><br>
                        Bank: Chase Bank<br>
                        Account: ****1234<br>
                        Type: Checking<br>
                        Status: Active<br><br>
                        💳 <strong>Salary Deposit:</strong><br>
                        Method: Direct Deposit<br>
                        Frequency: Monthly<br>
                        Next Deposit: Aug 30, 2025
                    </div>
                    <div style="font-size: 0.9em; opacity: 0.9;">
                        Need to update bank details? Contact HR with new account information.
                    </div>
                </div>
                <div>Your salary will be deposited on the last working day of each month. 💰</div>
            `;
        }
        
        if (option.toLowerCase().includes('salary revision') || option.toLowerCase().includes('revision history')) {
            return `
                <div style="background: linear-gradient(135deg, #e17055 0%, #f39c12 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                    <h4 style="margin: 0 0 8px 0;">📈 Salary Revision History</h4>
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin: 8px 0; font-size: 0.9em;">
                        <div style="margin-bottom: 10px;">
                            📅 <strong>Jan 2025:</strong> $6,500 (+8.3%)<br>
                            Reason: Annual performance review
                        </div>
                        <div style="margin-bottom: 10px;">
                            📅 <strong>Jan 2024:</strong> $6,000 (+9.1%)<br>
                            Reason: Promotion to Senior Developer
                        </div>
                        <div>
                            📅 <strong>Jan 2023:</strong> $5,500 (Starting salary)<br>
                            Reason: Initial appointment
                        </div>
                    </div>
                    <div style="font-size: 0.9em; opacity: 0.9;">
                        Next review scheduled: January 2026
                    </div>
                </div>
                <div>Your salary growth: 18.2% over 2 years. Excellent progress! �</div>
            `;
        }
        
        // Employee info responses
        if (option.toLowerCase().includes('my profile') || option.toLowerCase().includes('profile')) {
            return `
                <div style="background: linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%); color: #333; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                    <h4 style="margin: 0 0 8px 0;">👤 Your Profile</h4>
                    <div style="background: rgba(255,255,255,0.3); padding: 12px; border-radius: 8px; margin: 8px 0;">
                        👨‍💼 Name: John Smith<br>
                        🆔 Employee ID: EMP001<br>
                        💼 Department: IT Development<br>
                        🎯 Position: Senior Developer<br>
                        📅 Join Date: Jan 15, 2023<br>
                        📧 Email: john.smith@company.com<br>
                        📱 Phone: +1 (555) 123-4567
                    </div>
                </div>
                <div>Need to update your details? Select "Update personal details".</div>
            `;
        }
        
        if (option.toLowerCase().includes('update details') || option.toLowerCase().includes('update personal')) {
            return `
                <div style="background: linear-gradient(135deg, #a29bfe 0%, #6c5ce7 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                    <h4 style="margin: 0 0 8px 0;">✏️ Update Personal Details</h4>
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin: 8px 0;">
                        You can update the following information:<br><br>
                        📱 Phone Number: +1 (555) 123-4567<br>
                        🏠 Address: 123 Main St, City, State<br>
                        👨‍👩‍👧‍👦 Emergency Contact: Jane Smith<br>
                        🏥 Insurance Beneficiary: John Doe<br>
                        🏦 Bank Account: Update pending<br><br>
                        � <strong>To update:</strong><br>
                        Submit form to HR or call extension 2345
                    </div>
                </div>
                <div>Any changes require manager approval and will be processed within 3 business days. 📋</div>
            `;
        }
        
        if (option.toLowerCase().includes('company policies') || option.toLowerCase().includes('policies')) {
            return `
                <div style="background: linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                    <h4 style="margin: 0 0 8px 0;">📖 Company Policies</h4>
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin: 8px 0; font-size: 0.9em;">
                        📋 <strong>Available Policies:</strong><br><br>
                        🏢 Code of Conduct<br>
                        🕘 Attendance & Leave Policy<br>
                        💻 IT & Data Security Policy<br>
                        🚫 Anti-Harassment Policy<br>
                        🏥 Health & Safety Guidelines<br>
                        🎯 Performance Management<br>
                        💰 Compensation & Benefits<br>
                        🔄 Training & Development
                    </div>
                    <div style="font-size: 0.9em; opacity: 0.9;">
                        All policies are available on the company intranet.
                    </div>
                </div>
                <div>Need specific policy details? Access the employee handbook or contact HR. �</div>
            `;
        }
        
        if (option.toLowerCase().includes('contact hr') || option.toLowerCase().includes('hr team')) {
            return `
                <div style="background: linear-gradient(135deg, #00b894 0%, #00cec9 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                    <h4 style="margin: 0 0 8px 0;">📞 Contact HR Team</h4>
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin: 8px 0;">
                        👥 <strong>HR Department:</strong><br><br>
                        📧 Email: hr@company.com<br>
                        📱 Phone: +1 (555) HR-DESK<br>
                        📱 Extension: 2345<br>
                        💬 Teams: @HR-Support<br><br>
                        🕘 <strong>Office Hours:</strong><br>
                        Monday - Friday: 9:00 AM - 5:00 PM<br>
                        Emergency: 24/7 hotline available<br><br>
                        📍 <strong>Location:</strong> Floor 2, Room 201
                    </div>
                </div>
                <div>For urgent matters, use the emergency hotline or visit the HR office directly. 🚨</div>
            `;
        }
        
        if (option.toLowerCase().includes('emergency contacts') || option.toLowerCase().includes('emergency')) {
            return `
                <div style="background: linear-gradient(135deg, #e17055 0%, #fd79a8 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                    <h4 style="margin: 0 0 8px 0;">🚨 Emergency Contacts</h4>
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin: 8px 0;">
                        👥 <strong>Your Emergency Contacts:</strong><br><br>
                        👨‍👩‍👧‍👦 <strong>Primary:</strong> Jane Smith<br>
                        Relationship: Spouse<br>
                        Phone: +1 (555) 987-6543<br><br>
                        👨‍👩‍👧‍👦 <strong>Secondary:</strong> Mike Johnson<br>
                        Relationship: Brother<br>
                        Phone: +1 (555) 456-7890<br><br>
                        🏥 <strong>Company Emergency:</strong><br>
                        Security: +1 (555) 911-HELP<br>
                        Medical: +1 (555) 000-MEDIC
                    </div>
                </div>
                <div>Keep your emergency contacts updated. Contact HR to make changes. 📝</div>
            `;
        }
        
        // SMART DEFAULT HANDLER - Handle all remaining cases
        console.log("Falling back to smart default handler for:", option);
        
        // Handle View payslips
        if (option.toLowerCase().includes('payslips') || option === "View payslips") {
            console.log("PAYSLIPS DETECTED in default handler");
            return await this.fetchPayslips();
        }
        
        // Handle employment status
        if (option.toLowerCase().includes('employment status') || option === "Check employment status") {
            console.log("EMPLOYMENT STATUS DETECTED in default handler");
            return await this.fetchEmploymentStatus();
        }
        
        // Handle leave application
        if (option.toLowerCase().includes('apply for new leave') || option === "Apply for new leave") {
            console.log("LEAVE APPLICATION DETECTED in default handler");
            return this.showLeaveApplicationForm();
        }
        
        // Default response for truly unknown options
        return `
            <div style="background: linear-gradient(135deg, #0f9b8e 0%, #16a085 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px; text-align: center;">
                ✅ <strong>Request Processed Successfully!</strong><br>
                <small style="opacity: 0.9;">Your request for "${option}" has been completed.</small>
            </div>
            <div style="font-size: 0.95em;">
                Is there anything else I can help you with today?
            </div>
        `;
    }

    showActionButtons() {
        const actionContainer = document.createElement('div');
        actionContainer.className = 'categories-container';
        actionContainer.style.marginTop = '16px';
        
        const buttons = [
            {
                text: '🏠 Back to Main Menu',
                action: () => this.resetToMainMenu()
            },
            {
                text: '❓ Ask Another Question', 
                action: () => this.resetToMainMenu()
            },
            {
                text: '📞 Contact Support',
                action: () => {
                    this.addUserMessage('Contact Support');
                    this.addBotMessage('I\'ll connect you with our support team. Please hold on while I transfer your chat...', 1000);
                }
            }
        ];
        
        buttons.forEach((btn, index) => {
            setTimeout(() => {
                const button = document.createElement('button');
                button.className = 'input-btn';
                button.textContent = btn.text;
                button.addEventListener('click', btn.action);
                actionContainer.appendChild(button);
            }, index * 200);
        });
        
        this.chatBody.appendChild(actionContainer);
        
        // Smooth scroll to show action buttons
        setTimeout(() => {
            this.autoScroll();
        }, buttons.length * 200 + 100);
    }

    resetToMainMenu() {
        this.chatBody.innerHTML = '';
        this.currentTypingIndicator = null;
        
        setTimeout(() => {
            this.showWelcomeMessage();
        }, 300);
    }

    async fetchAttendanceHistory() {
        try {
            const response = await fetch('http://127.0.0.1:8000/api/attendance/history?employee_id=EMP001&days=10');
            
            if (!response.ok) {
                throw new Error('Failed to fetch attendance data');
            }
            
            const data = await response.json();
            
            return this.formatAttendanceHistoryResponse(data);
        } catch (error) {
            console.error('Error fetching attendance history:', error);
            return `
                <div style="background: linear-gradient(135deg, #e17055 0%, #fd79a8 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                    <h4 style="margin: 0 0 8px 0;">❌ Error Loading Attendance History</h4>
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin: 8px 0;">
                        Sorry, I couldn't load your attendance history at the moment. Please try again later or contact IT support.
                    </div>
                </div>
                <div>Is there anything else I can help you with?</div>
            `;
        }
    }

    formatAttendanceHistoryResponse(data) {
        const recordsHtml = data.records.map(record => {
            const statusIcon = {
                'Present': '✅',
                'Late': '⚠️',
                'Absent': '❌',
                'Half Day': '🕐'
            }[record.status] || '📅';

            const statusColor = {
                'Present': '#00b894',
                'Late': '#fdcb6e',
                'Absent': '#e17055',
                'Half Day': '#74b9ff'
            }[record.status] || '#667eea';

            return `
                <div style="background: rgba(255,255,255,0.1); padding: 8px; border-radius: 6px; margin: 4px 0; border-left: 3px solid ${statusColor};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong>${record.date}</strong>
                        <span style="background: ${statusColor}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em;">
                            ${statusIcon} ${record.status}
                        </span>
                    </div>
                    ${record.check_in_time ? `<div style="font-size: 0.9em; margin-top: 4px;">🕘 In: ${record.check_in_time} | Out: ${record.check_out_time || 'Not marked'}</div>` : '<div style="font-size: 0.9em; margin-top: 4px; opacity: 0.7;">No attendance recorded</div>'}
                    ${record.working_hours ? `<div style="font-size: 0.8em; opacity: 0.8;">⏱️ ${record.working_hours}</div>` : ''}
                </div>
            `;
        }).join('');

        return `
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                <h4 style="margin: 0 0 8px 0;">📅 Attendance History - ${data.employee_name}</h4>
                <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin: 8px 0;">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 12px; margin-bottom: 12px;">
                        <div style="text-align: center;">
                            <div style="font-size: 1.2em; font-weight: bold; color: #00b894;">${data.summary.present_days}</div>
                            <div style="font-size: 0.8em; opacity: 0.9;">Present</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 1.2em; font-weight: bold; color: #fdcb6e;">${data.summary.late_days}</div>
                            <div style="font-size: 0.8em; opacity: 0.9;">Late</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 1.2em; font-weight: bold; color: #e17055;">${data.summary.absent_days}</div>
                            <div style="font-size: 0.8em; opacity: 0.9;">Absent</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 1.2em; font-weight: bold; color: #74b9ff;">${data.total_records}</div>
                            <div style="font-size: 0.8em; opacity: 0.9;">Total Days</div>
                        </div>
                    </div>
                    <div style="font-size: 0.9em; opacity: 0.9; text-align: center; margin-bottom: 12px;">
                        📊 Period: ${data.date_range.from} to ${data.date_range.to}
                    </div>
                    <div style="max-height: 300px; overflow-y: auto;">
                        ${recordsHtml}
                    </div>
                </div>
            </div>
            <div>Your attendance record looks good! Is there anything else I can help you with?</div>
        `;
    }

    showLeaveApplicationForm() {
        // Get today's date in YYYY-MM-DD format
        const today = new Date();
        const todayStr = today.toISOString().split('T')[0];
        const nextWeek = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
        const nextWeekStr = nextWeek.toISOString().split('T')[0];

        const formHtml = `
            <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #333; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                <h4 style="margin: 0 0 16px 0;">📝 Leave Application Form</h4>
                <form id="leaveApplicationForm" style="display: flex; flex-direction: column; gap: 12px;">
                    
                    <div style="display: flex; flex-direction: column; gap: 4px;">
                        <label style="font-weight: bold; font-size: 0.9em;">📋 Leave Type:</label>
                        <select id="leaveType" style="padding: 8px; border: 1px solid #ddd; border-radius: 6px; font-size: 0.9em;" required>
                            <option value="">Select leave type</option>
                            <option value="Annual Leave">🏖️ Annual Leave</option>
                            <option value="Sick Leave">🤒 Sick Leave</option>
                            <option value="Personal Leave">👤 Personal Leave</option>
                            <option value="Emergency Leave">🚨 Emergency Leave</option>
                            <option value="Comp Off">🎉 Comp Off</option>
                        </select>
                    </div>

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                        <div style="display: flex; flex-direction: column; gap: 4px;">
                            <label style="font-weight: bold; font-size: 0.9em;">📅 From Date:</label>
                            <input type="date" id="fromDate" min="${todayStr}" style="padding: 8px; border: 1px solid #ddd; border-radius: 6px; font-size: 0.9em;" required>
                        </div>
                        <div style="display: flex; flex-direction: column; gap: 4px;">
                            <label style="font-weight: bold; font-size: 0.9em;">📅 To Date:</label>
                            <input type="date" id="toDate" min="${todayStr}" style="padding: 8px; border: 1px solid #ddd; border-radius: 6px; font-size: 0.9em;" required>
                        </div>
                    </div>

                    <div style="display: flex; flex-direction: column; gap: 4px;">
                        <label style="font-weight: bold; font-size: 0.9em;">✍️ Reason:</label>
                        <textarea id="leaveReason" rows="3" placeholder="Please provide a reason for your leave..." style="padding: 8px; border: 1px solid #ddd; border-radius: 6px; font-size: 0.9em; resize: vertical;" required></textarea>
                    </div>

                    <div id="leaveDays" style="background: rgba(255,255,255,0.5); padding: 8px; border-radius: 6px; text-align: center; font-weight: bold; display: none;">
                        📊 Total Leave Days: <span id="totalDays">0</span>
                    </div>

                    <div style="display: flex; gap: 8px; margin-top: 8px;">
                        <button type="submit" style="flex: 1; background: linear-gradient(135deg, #00b894 0%, #00cec9 100%); color: white; border: none; padding: 12px; border-radius: 6px; font-weight: bold; cursor: pointer; transition: all 0.3s;">
                            ✅ Submit Application
                        </button>
                        <button type="button" id="cancelForm" style="flex: 0 0 auto; background: #e17055; color: white; border: none; padding: 12px 16px; border-radius: 6px; cursor: pointer; transition: all 0.3s;">
                            ❌ Cancel
                        </button>
                    </div>
                </form>
            </div>
        `;

        // Add the form to the chat
        setTimeout(() => {
            this.setupLeaveFormHandlers();
        }, 100);

        return formHtml;
    }

    setupLeaveFormHandlers() {
        const form = document.getElementById('leaveApplicationForm');
        const fromDateInput = document.getElementById('fromDate');
        const toDateInput = document.getElementById('toDate');
        const leaveDaysDiv = document.getElementById('leaveDays');
        const totalDaysSpan = document.getElementById('totalDays');
        const cancelBtn = document.getElementById('cancelForm');

        // Calculate leave days when dates change
        const calculateDays = () => {
            const fromDate = fromDateInput.value;
            const toDate = toDateInput.value;
            
            if (fromDate && toDate) {
                const from = new Date(fromDate);
                const to = new Date(toDate);
                
                if (to >= from) {
                    const timeDiff = to.getTime() - from.getTime();
                    const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24)) + 1;
                    totalDaysSpan.textContent = daysDiff;
                    leaveDaysDiv.style.display = 'block';
                    
                    // Update min date for toDate
                    toDateInput.min = fromDate;
                } else {
                    leaveDaysDiv.style.display = 'none';
                    toDateInput.value = '';
                }
            } else {
                leaveDaysDiv.style.display = 'none';
            }
        };

        fromDateInput.addEventListener('change', calculateDays);
        toDateInput.addEventListener('change', calculateDays);

        // Handle form submission
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.submitLeaveApplication();
        });

        // Handle cancel button
        cancelBtn.addEventListener('click', () => {
            this.showActionButtons();
        });
    }

    async submitLeaveApplication() {
        const formData = {
            employee_id: 'EMP001',
            employee_name: 'John Doe',
            leave_type: document.getElementById('leaveType').value,
            from_date: document.getElementById('fromDate').value,
            to_date: document.getElementById('toDate').value,
            reason: document.getElementById('leaveReason').value
        };

        try {
            // Show loading message
            this.addBotMessage('Submitting your leave application...', 500);

            const response = await fetch('http://127.0.0.1:8000/api/leave/apply', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (response.ok && result.success) {
                const successMessage = `
                    <div style="background: linear-gradient(135deg, #00b894 0%, #00cec9 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                        <h4 style="margin: 0 0 8px 0;">✅ Leave Application Submitted Successfully!</h4>
                        <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin: 8px 0;">
                            📋 <strong>Application Details:</strong><br>
                            Application ID: #${result.application_id}<br>
                            Leave Type: ${result.leave_type}<br>
                            📅 From: ${result.from_date}<br>
                            📅 To: ${result.to_date}<br>
                            📊 Total Days: ${result.total_days}<br>
                            📝 Reason: ${result.reason}<br>
                            ⏰ Status: ${result.status}<br>
                            📅 Applied on: ${result.applied_date}
                        </div>
                        <div style="font-size: 0.9em; opacity: 0.9;">
                            Your manager will review your application. You'll receive an email notification once approved.
                        </div>
                    </div>
                    <div>Track your application status in the "Leave approval status" section. Is there anything else I can help you with?</div>
                `;
                
                this.addBotMessage(successMessage, 1000, true);
                
                // Show action buttons after success
                setTimeout(() => {
                    this.showActionButtons();
                }, 2000);
            } else {
                throw new Error(result.detail || 'Failed to submit leave application');
            }
        } catch (error) {
            console.error('Error submitting leave application:', error);
            const errorMessage = `
                <div style="background: linear-gradient(135deg, #e17055 0%, #fd79a8 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                    <h4 style="margin: 0 0 8px 0;">❌ Error Submitting Application</h4>
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin: 8px 0;">
                        Sorry, there was an error submitting your leave application. Please try again or contact HR if the problem persists.
                    </div>
                </div>
                <div>You can try submitting again or contact HR for assistance.</div>
            `;
            
            this.addBotMessage(errorMessage, 1000, true);
            
            setTimeout(() => {
                this.showActionButtons();
            }, 2000);
        }
    }

    async fetchPayslips() {
        try {
            const response = await fetch('http://127.0.0.1:8000/api/payroll/payslips?employee_id=EMP001');
            
            if (!response.ok) {
                throw new Error('Failed to fetch payslips data');
            }
            
            const data = await response.json();
            
            return this.formatPayslipsResponse(data);
        } catch (error) {
            console.error('Error fetching payslips:', error);
            return `
                <div style="background: linear-gradient(135deg, #e17055 0%, #fd79a8 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                    <h4 style="margin: 0 0 8px 0;">❌ Error Loading Payslips</h4>
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin: 8px 0;">
                        Sorry, I couldn't load your payslips at the moment. Please try again later or contact HR support.
                    </div>
                </div>
                <div>Is there anything else I can help you with?</div>
            `;
        }
    }

    formatPayslipsResponse(data) {
        if (!data.payslips || data.payslips.length === 0) {
            return `
                <div style="background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                    <h4 style="margin: 0 0 8px 0;">📄 No Payslips Found</h4>
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin: 8px 0;">
                        No payslips are available for your account at the moment. Please contact HR if you believe this is an error.
                    </div>
                </div>
                <div>Is there anything else I can help you with?</div>
            `;
        }

        const payslipsHtml = data.payslips.map(payslip => {
            const monthName = new Date(payslip.pay_period + '-01').toLocaleDateString('en-US', { year: 'numeric', month: 'long' });
            
            return `
                <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin: 8px 0; border-left: 3px solid #00b894;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <div style="font-weight: bold; font-size: 1.1em;">${monthName}</div>
                        <div style="background: #00b894; color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.8em;">
                            ${payslip.status}
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px; font-size: 0.9em;">
                        <div>💰 Basic: ${payslip.basic_salary}</div>
                        <div>🎯 Allowances: ${payslip.allowances}</div>
                        <div>📊 Gross: ${payslip.gross_salary}</div>
                        <div>📉 Deductions: ${payslip.deductions}</div>
                    </div>
                    
                    <div style="background: rgba(255,255,255,0.2); padding: 8px; border-radius: 6px; margin-bottom: 12px; text-align: center;">
                        <strong style="font-size: 1.1em; color: #00b894;">💵 Net Salary: ${payslip.net_salary}</strong>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8em;">
                        <span>📅 ${payslip.pay_period_start} to ${payslip.pay_period_end}</span>
                        <button onclick="window.hrChatBot.downloadPayslip(${payslip.payslip_id}, '${monthName}')" 
                                style="background: linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%); color: white; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 0.8em; transition: all 0.3s;">
                            📥 Download PDF
                        </button>
                    </div>
                </div>
            `;
        }).join('');

        return `
            <div style="background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                <h4 style="margin: 0 0 8px 0;">📄 Payslips - ${data.employee_name}</h4>
                <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin: 8px 0;">
                    <div style="text-align: center; margin-bottom: 12px; font-size: 0.9em;">
                        📊 Total Payslips Available: <strong>${data.total_payslips}</strong>
                    </div>
                    <div style="max-height: 400px; overflow-y: auto;">
                        ${payslipsHtml}
                    </div>
                </div>
            </div>
            <div>Your payslips are ready for download! Is there anything else I can help you with?</div>
        `;
    }

    downloadPayslip(payslipId, monthName) {
        // Simulate download - In a real app, this would trigger actual PDF download
        this.addBotMessage(`
            <div style="background: linear-gradient(135deg, #00b894 0%, #00cec9 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                <h4 style="margin: 0 0 8px 0;">📥 Download Started</h4>
                <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin: 8px 0;">
                    Your payslip for <strong>${monthName}</strong> is being prepared for download.<br><br>
                    📧 Download link will be sent to your email<br>
                    📱 You can also access it from the HR portal<br>
                    🔗 Link expires in 7 days
                </div>
            </div>
            <div>Download initiated successfully! Check your email in a few minutes.</div>
        `, 500, true);
        
        // Auto-scroll after adding the message
        setTimeout(() => {
            this.autoScroll();
        }, 600);
    }

    async fetchEmploymentStatus() {
        try {
            const response = await fetch('/api/employee/status?employee_id=EMP001');
            const data = await response.json();
            
            return this.formatEmploymentStatusResponse(data);
        } catch (error) {
            console.error('Error fetching employment status:', error);
            return `
                <div style="background: linear-gradient(135deg, #e17055 0%, #fd79a8 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                    <h4 style="margin: 0 0 8px 0;">❌ Error Loading Employment Status</h4>
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin: 8px 0;">
                        Sorry, I couldn't load your employment information at the moment. Please try again later or contact HR support.
                    </div>
                </div>
                <div>Is there anything else I can help you with?</div>
            `;
        }
    }

    formatEmploymentStatusResponse(employee) {
        const statusColor = employee.employment_status === 'Active' ? '#28a745' : 
                           employee.employment_status === 'On Leave' ? '#ffc107' : '#6c757d';
        
        return `
            <div style="background: linear-gradient(135deg, #0f9b8e 0%, #16a085 100%); color: white; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                <h3 style="margin: 0 0 12px 0; font-size: 1.2em;">👤 Employment Information</h3>
            </div>
            
            <div style="background: #f8f9fa; padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                <div style="display: grid; gap: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #e9ecef;">
                        <span style="font-weight: 500; color: #495057;">Employee ID:</span>
                        <span style="color: #212529;">${employee.employee_id}</span>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #e9ecef;">
                        <span style="font-weight: 500; color: #495057;">Name:</span>
                        <span style="color: #212529;">${employee.employee_name}</span>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #e9ecef;">
                        <span style="font-weight: 500; color: #495057;">Status:</span>
                        <span style="background: ${statusColor}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.9em; font-weight: 500;">
                            ${employee.employment_status}
                        </span>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #e9ecef;">
                        <span style="font-weight: 500; color: #495057;">Department:</span>
                        <span style="color: #212529;">${employee.department}</span>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #e9ecef;">
                        <span style="font-weight: 500; color: #495057;">Position:</span>
                        <span style="color: #212529;">${employee.position}</span>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #e9ecef;">
                        <span style="font-weight: 500; color: #495057;">Employment Type:</span>
                        <span style="color: #212529;">${employee.employment_type}</span>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #e9ecef;">
                        <span style="font-weight: 500; color: #495057;">Hire Date:</span>
                        <span style="color: #212529;">${new Date(employee.hire_date).toLocaleDateString()}</span>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #e9ecef;">
                        <span style="font-weight: 500; color: #495057;">Years of Service:</span>
                        <span style="color: #212529;">${employee.years_of_service} years</span>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #e9ecef;">
                        <span style="font-weight: 500; color: #495057;">Manager:</span>
                        <span style="color: #212529;">${employee.reporting_manager || 'Not assigned'}</span>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #e9ecef;">
                        <span style="font-weight: 500; color: #495057;">Office Location:</span>
                        <span style="color: #212529;">${employee.office_location || 'Not specified'}</span>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #e9ecef;">
                        <span style="font-weight: 500; color: #495057;">Salary Grade:</span>
                        <span style="color: #212529;">${employee.salary_grade || 'Not specified'}</span>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0;">
                        <span style="font-weight: 500; color: #495057;">Probation Status:</span>
                        <span style="color: #212529; background: #d4edda; padding: 2px 8px; border-radius: 4px; font-size: 0.9em;">${employee.probation_status}</span>
                    </div>
                </div>
            </div>
            
            <div style="text-align: center; color: #6c757d; font-size: 0.9em;">
                Need to update your information? Contact HR at hr@company.com
            </div>
        `;
    }
}

// Initialize the chatbot when the page loads
document.addEventListener('DOMContentLoaded', () => {
    // Add a loading animation
    const chatBody = document.querySelector('.chat-body');
    if (chatBody) {
        chatBody.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; flex-direction: column; opacity: 0.7;">
                <div style="display: flex; gap: 4px; margin-bottom: 12px;">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
                <div style="font-size: 0.9em; color: #667eea;">Initializing HR Assistant...</div>
            </div>
        `;
        
        // Initialize the chatbot
        setTimeout(() => {
            window.hrChatBot = new ChatBot();
        }, 1500);
    }
});

// Add some utility functions
window.addEventListener('beforeunload', () => {
    // Save chat state if needed
    localStorage.setItem('chatBotLastActive', Date.now());
});

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        if (window.hrChatBot) {
            window.hrChatBot.resetToMainMenu();
        }
    }
});
