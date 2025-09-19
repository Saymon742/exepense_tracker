const API_BASE = '/api/v1';

class ExpenseTracker {
    constructor() {
        this.chart = null;
        this.init();
    }

    init() {
        this.loadExpenses();
        this.setupEventListeners();
        this.setupTouchOptimizations();
    }

    setupTouchOptimizations() {
        document.addEventListener('touchstart', function() {}, { passive: true });
        
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('touchstart', (e) => {
                e.stopPropagation();
            });
        });
    }

    setupEventListeners() {
        document.getElementById('expenseForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addExpense();
        });

        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.loadExpenses();
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
                e.preventDefault();
            }
        });
    }

    async loadExpenses() {
        this.showLoading(true);
        try {
            const response = await fetch(`${API_BASE}/expenses/`);
            if (!response.ok) throw new Error('Помилка завантаження');
            const expenses = await response.json();
            this.displayExpenses(expenses);
            await this.updateStats();
        } catch (error) {
            this.showNotification('Помилка завантаження даних', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    displayExpenses(expenses) {
        const list = document.getElementById('expensesList');
        list.innerHTML = '<h3>📋 Останні витрати</h3>';
        
        if (!expenses || expenses.length === 0) {
            list.innerHTML += '<p>Немає доданих витрат</p>';
            return;
        }

        expenses.slice(-8).reverse().forEach(expense => {
            const item = document.createElement('div');
            item.className = 'expense-item';
            item.innerHTML = `
                <div class="expense-info">
                    <div class="expense-amount">${expense.amount} грн</div>
                    <div class="expense-category">${this.getCategoryEmoji(expense.category)} ${this.formatCategory(expense.category)}</div>
                    ${expense.description ? `<div class="expense-description">${expense.description}</div>` : ''}
                    <div class="expense-date">${new Date(expense.date).toLocaleDateString('uk-UA')}</div>
                </div>
                <button class="delete-btn" onclick="expenseTracker.deleteExpense(${expense.id})">🗑️ Видалити</button>
            `;
            list.appendChild(item);
        });
    }

    getCategoryEmoji(category) {
        const emojis = {
            'food': '🍕', 'transport': '🚗', 'entertainment': '🎬',
            'utilities': '🏠', 'shopping': '🛍️', 'health': '🏥', 'other': '📦'
        };
        return emojis[category] || '📦';
    }

    formatCategory(category) {
        const categories = {
            'food': 'Їжа', 'transport': 'Транспорт', 'entertainment': 'Розваги',
            'utilities': 'Комунальні', 'shopping': 'Покупки', 'health': 'Здоров\'я', 'other': 'Інше'
        };
        return categories[category] || category;
    }

    async addExpense() {
        const formData = {
            amount: parseFloat(document.getElementById('amount').value),
            category: document.getElementById('category').value,
            description: document.getElementById('description').value
        };

        if (!formData.amount || !formData.category) {
            this.showNotification('Заповніть всі обов\'язкові поля', 'error');
            return;
        }

        try {
            const response = await fetch(`${API_BASE}/expenses/`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                this.showNotification('Витрату успішно додано!');
                document.getElementById('expenseForm').reset();
                await this.loadExpenses();
            } else {
                this.showNotification('Помилка при додаванні витрати', 'error');
            }
        } catch (error) {
            this.showNotification('Помилка з\'єднання', 'error');
        }
    }

    async deleteExpense(expenseId) {
        if (!confirm('Видалити цю витрату?')) return;

        try {
            const response = await fetch(`${API_BASE}/expenses/${expenseId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showNotification('Витрату видалено');
                await this.loadExpenses();
            } else {
                this.showNotification('Помилка при видаленні', 'error');
            }
        } catch (error) {
            this.showNotification('Помилка з\'єднання', 'error');
        }
    }

    async updateStats() {
        try {
            const [totalResponse, summaryResponse] = await Promise.all([
                fetch(`${API_BASE}/analytics/total`),
                fetch(`${API_BASE}/analytics/summary`)
            ]);

            const totalData = await totalResponse.json();
            const summaryData = await summaryResponse.json();

            document.getElementById('totalAmount').textContent = 
                `${totalData.total_amount?.toFixed(2) || '0.00'}`;

            const expensesResponse = await fetch(`${API_BASE}/expenses/`);
            const expenses = await expensesResponse.json();
            document.getElementById('totalCount').textContent = expenses.length;

            this.updateChart(summaryData);
        } catch (error) {
            console.error('Помилка статистики:', error);
        }
    }

    updateChart(summaryData) {
        const ctx = document.getElementById('expenseChart');
        const placeholder = document.getElementById('chartPlaceholder');
        
        if (this.chart) {
            this.chart.destroy();
        }

        if (!summaryData || summaryData.length === 0) {
            placeholder.style.display = 'block';
            ctx.style.display = 'none';
            return;
        }

        placeholder.style.display = 'none';
        ctx.style.display = 'block';

        this.chart = new Chart(ctx.getContext('2d'), {
            type: 'pie',
            data: {
                labels: summaryData.map(item => `${this.getCategoryEmoji(item.category)} ${this.formatCategory(item.category)}`),
                datasets: [{
                    data: summaryData.map(item => item.total_amount),
                    backgroundColor: ['#4facfe', '#00f2fe', '#667eea', '#764ba2', '#f093fb', '#f5576c', '#4ecdc4']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { 
                        position: 'bottom',
                        labels: {
                            font: { size: window.innerWidth < 480 ? 10 : 12 }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => `${context.label}: ${context.raw.toFixed(2)} грн`
                        }
                    }
                }
            }
        });
    }

    showNotification(message, type = 'success') {
        const notification = document.getElementById('notification');
        notification.textContent = message;
        notification.className = `notification ${type}`;
        
        setTimeout(() => {
            notification.className = 'notification';
        }, 3000);
    }

    showLoading(show) {
        const btn = document.querySelector('#expenseForm button[type="submit"]');
        if (show) {
            btn.innerHTML = '<div class="loading"></div>';
            btn.disabled = true;
        } else {
            btn.innerHTML = '💾 Зберегти';
            btn.disabled = false;
        }
    }
}

let expenseTracker;
document.addEventListener('DOMContentLoaded', () => {
    expenseTracker = new ExpenseTracker();
    
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
            .catch(() => {});
    }
});