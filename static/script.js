class BillingApp {
    constructor() {
        this.currentEmails = [];
        this.currentSummaries = [];
        this.init();
    }

    init() {
        this.bindEvents();
        this.checkAuthStatus();
        this.initTabs();
    }

    bindEvents() {
        // Button event listeners
        document.getElementById('clio-login-btn').addEventListener('click', () => {
            window.location.href = '/clio/login';
        });

        document.getElementById('clio-status-btn').addEventListener('click', () => {
            this.checkAuthStatus();
        });

        document.getElementById('fetch-emails-btn').addEventListener('click', () => {
            this.fetchEmails();
        });

        document.getElementById('summarize-btn').addEventListener('click', () => {
            this.generateSummaries();
        });

        document.getElementById('push-clio-btn').addEventListener('click', () => {
            this.pushToCliO();
        });
    }

    initTabs() {
        const tabBtns = document.querySelectorAll('.tab-btn');
        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const tabId = btn.dataset.tab;
                this.switchTab(tabId);
            });
        });
    }

    switchTab(tabId) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabId}-tab`).classList.add('active');
    }

    showLoading(show = true) {
        const overlay = document.getElementById('loading-overlay');
        if (show) {
            overlay.classList.add('show');
        } else {
            overlay.classList.remove('show');
        }
    }

    showStatus(message, type = 'info') {
        const statusDiv = document.getElementById('status');
        statusDiv.textContent = message;
        statusDiv.className = `status-message ${type}`;

        // Auto-hide after 5 seconds
        setTimeout(() => {
            statusDiv.textContent = '';
            statusDiv.className = 'status-message';
        }, 5000);
    }

    async checkAuthStatus() {
        try {
            const response = await fetch('/clio/status');
            const data = await response.json();

            const authStatus = document.getElementById('auth-status');
            if (data.authenticated) {
                authStatus.textContent = '✅ Connected to Clio';
                authStatus.className = 'auth-status authenticated';
                this.enableClioFeatures();
            } else {
                authStatus.textContent = '❌ Not connected to Clio';
                authStatus.className = 'auth-status not-authenticated';
                this.disableClioFeatures();
            }
        } catch (error) {
            console.error('Error checking auth status:', error);
            this.showStatus('Error checking Clio status', 'error');
        }
    }

    enableClioFeatures() {
        document.getElementById('push-clio-btn').disabled = false;
    }

    disableClioFeatures() {
        document.getElementById('push-clio-btn').disabled = true;
    }

    async fetchEmails() {
        this.showLoading(true);
        this.showStatus('Fetching emails from Gmail...', 'info');

        try {
            const response = await fetch('/api/emails');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const emails = await response.json();
            this.currentEmails = emails;
            this.renderEmails(emails);

            if (emails.length > 0) {
                document.getElementById('summarize-btn').disabled = false;
                this.showStatus(`✅ Fetched ${emails.length} emails`, 'success');
            } else {
                this.showStatus('No emails found', 'info');
            }
        } catch (error) {
            console.error('Error fetching emails:', error);
            this.showStatus(`❌ Failed to fetch emails: ${error.message}`, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    renderEmails(emails) {
        const emailList = document.getElementById('email-list');

        if (emails.length === 0) {
            emailList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📭</div>
                    <p>No emails found</p>
                </div>
            `;
            return;
        }

        emailList.innerHTML = emails.map((email, index) => `
            <div class="email-item">
                <div class="email-header">
                    <div class="email-subject">${email.subject || 'No Subject'}</div>
                    <div class="email-to">To: ${email.to || 'Unknown'}</div>
                </div>
                <div class="email-body" id="email-body-${index}">
                    ${this.truncateText(email.body, 200)}
                    ${email.body.length > 200 ? `<button class="expand-btn" onclick="app.toggleEmailBody(${index})">Show more</button>` : ''}
                </div>
            </div>
        `).join('');
    }

    toggleEmailBody(index) {
        const bodyElement = document.getElementById(`email-body-${index}`);
        const email = this.currentEmails[index];

        if (bodyElement.classList.contains('expanded')) {
            bodyElement.innerHTML = `
                ${this.truncateText(email.body, 200)}
                <button class="expand-btn" onclick="app.toggleEmailBody(${index})">Show more</button>
            `;
            bodyElement.classList.remove('expanded');
        } else {
            bodyElement.innerHTML = `
                ${email.body}
                <button class="expand-btn" onclick="app.toggleEmailBody(${index})">Show less</button>
            `;
            bodyElement.classList.add('expanded');
        }
    }

    async generateSummaries() {
        this.showLoading(true);
        this.showStatus('Generating AI summaries...', 'info');

        try {
            const response = await fetch('/api/summaries');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const summaries = await response.json();
            this.currentSummaries = summaries;
            this.renderSummaries(summaries);
            this.switchTab('summaries');

            this.showStatus(`✅ Generated ${summaries.length} summaries`, 'success');
        } catch (error) {
            console.error('Error generating summaries:', error);
            this.showStatus(`❌ Failed to generate summaries: ${error.message}`, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    renderSummaries(summaries) {
        const summaryList = document.getElementById('summary-list');

        if (summaries.length === 0) {
            summaryList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📝</div>
                    <p>No summaries generated</p>
                </div>
            `;
            return;
        }

        summaryList.innerHTML = summaries.map(item => {
            if (item.summary.error) {
                return `
                    <div class="summary-item">
                        <div class="email-header">
                            <div class="email-subject">${item.subject || 'No Subject'}</div>
                            <div class="email-to">To: ${item.to || 'Unknown'}</div>
                        </div>
                        <div class="summary-content" style="background: #fed7d7; border-color: #f56565;">
                            <strong>❌ Error:</strong> ${item.summary.error}
                        </div>
                    </div>
                `;
            }

            return `
                <div class="summary-item">
                    <div class="email-header">
                        <div class="email-subject">${item.subject || 'No Subject'}</div>
                        <div class="email-to">To: ${item.to || 'Unknown'}</div>
                    </div>
                    <div class="summary-type ${item.summary.type.toLowerCase().replace('entry', '-entry')}">${item.summary.type}</div>
                    <div class="summary-content">
                        <strong>Summary:</strong> ${item.summary.summary}
                    </div>
                    ${this.renderSummaryDetails(item.summary)}
                </div>
            `;
        }).join('');
    }

    renderSummaryDetails(summary) {
        if (!summary || summary.error) return '';

        let details = [];

        if (summary.type === 'TimeEntry') {
            if (summary.duration) {
                details.push({ label: 'Duration', value: `${summary.duration} hrs` });
            }
            if (summary.rate) {
                details.push({ label: 'Rate', value: `${summary.rate}` });
            }
        } else if (summary.type === 'ExpenseEntry') {
            if (summary.price) {
                details.push({ label: 'Price', value: `${summary.price}` });
            }
            if (summary.quantity) {
                details.push({ label: 'Quantity', value: summary.quantity });
            }
            if (summary.expense_type) {
                details.push({ label: 'Type', value: summary.expense_type });
            }
        }

        if (details.length === 0) return '';

        return `
            <div class="summary-details">
                ${details.map(detail => `
                    <div class="detail-item">
                        <div class="detail-label">${detail.label}</div>
                        <div class="detail-value">${detail.value}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    async pushToCliO() {
        this.showLoading(true);
        this.showStatus('Pushing summaries to Clio...', 'info');

        try {
            const response = await fetch('/clio/push-summary', {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();

            if (result.status === 'success') {
                this.showStatus(`✅ Successfully pushed ${result.activities_created.length} activities to Clio`, 'success');
            } else {
                let errorMsg = 'Failed to push to Clio';
                if (result.errors && result.errors.length > 0) {
                    errorMsg += ': ' + result.errors.join(', ');
                }
                this.showStatus(`❌ ${errorMsg}`, 'error');
            }
        } catch (error) {
            console.error('Error pushing to Clio:', error);
            this.showStatus(`❌ Error pushing to Clio: ${error.message}`, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }
}

// Initialize the app when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new BillingApp();
});