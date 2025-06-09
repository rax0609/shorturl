// 自訂模態視窗實現
class CustomModal {
    constructor() {
        this.createModalElement();
        this.setupEventListeners();
        this.currentPromiseResolve = null;
        this.currentPromiseReject = null;
    }

    createModalElement() {
        // 創建模態視窗的 DOM 元素
        this.overlay = document.createElement('div');
        this.overlay.className = 'modal-overlay';
        
        this.container = document.createElement('div');
        this.container.className = 'modal-container';
        
        this.header = document.createElement('div');
        this.header.className = 'modal-header';
        
        this.title = document.createElement('h3');
        this.title.className = 'modal-title';
        
        this.body = document.createElement('div');
        this.body.className = 'modal-body';
        
        this.footer = document.createElement('div');
        this.footer.className = 'modal-footer';
        
        // 組合元素
        this.header.appendChild(this.title);
        this.container.appendChild(this.header);
        this.container.appendChild(this.body);
        this.container.appendChild(this.footer);
        this.overlay.appendChild(this.container);
        
        // 添加到 document
        document.body.appendChild(this.overlay);
    }
    
    setupEventListeners() {
        // 點擊遮罩關閉模態視窗（對於 alert 和 prompt 不應該允許，只對 confirm 有效）
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay && this.allowOutsideClick) {
                this.close(false);
            }
        });
        
        // ESC 鍵關閉模態視窗
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.overlay.classList.contains('active') && this.allowOutsideClick) {
                this.close(false);
            }
        });
    }
      alert(message, title = '提示', icon = 'info-circle') {
        return new Promise(resolve => {
            this.title.innerHTML = `<i class="fas fa-${icon}"></i> ${title}`;
            
            // 檢查訊息是否包含 HTML
            if (message.includes('<') && message.includes('>')) {
                this.body.innerHTML = message;
            } else {
                // 如果是純文字，處理換行符
                this.body.innerHTML = message.replace(/\n/g, '<br>');
            }
            
            // 清空並創建確定按鈕
            this.footer.innerHTML = '';
            const okButton = this.createButton('確定', 'success');
            okButton.addEventListener('click', () => {
                this.close(true);
                resolve();
            });
            
            this.footer.appendChild(okButton);
            this.show();
            
            // 焦點設置在確定按鈕上
            setTimeout(() => okButton.focus(), 100);
            
            // alert 模態視窗不允許點擊外部關閉
            this.allowOutsideClick = false;
        });
    }
      confirm(message, title = '確認', icon = 'question-circle') {
        return new Promise(resolve => {
            // 判斷是否為刪除確認，調整樣式
            const isDangerousAction = 
                message.includes('刪除') || 
                message.toLowerCase().includes('delete') || 
                title.includes('刪除') ||
                title.includes('危險');
            
            if (isDangerousAction) {
                this.container.classList.add('modal-danger');
                icon = 'exclamation-triangle';
                title = title || '警告';
            } else {
                this.container.classList.remove('modal-danger');
            }
            
            this.title.innerHTML = `<i class="fas fa-${icon}"></i> ${title}`;
            
            // 處理換行符
            this.body.innerHTML = message.replace(/\n/g, '<br>');
            
            // 清空並創建確定和取消按鈕
            this.footer.innerHTML = '';
            
            const cancelButton = this.createButton('取消', isDangerousAction ? '' : 'danger');
            cancelButton.addEventListener('click', () => {
                this.close(false);
                resolve(false);
            });
            
            const okButton = this.createButton('確定', isDangerousAction ? 'danger' : 'success');
            okButton.addEventListener('click', () => {
                this.close(true);
                resolve(true);
            });
            
            // 危險操作時，按鈕順序調整，讓「取消」更容易被點擊
            if (isDangerousAction) {
                this.footer.appendChild(okButton);
                this.footer.appendChild(cancelButton);
                // 焦點設置在取消按鈕上
                setTimeout(() => cancelButton.focus(), 100);
            } else {
                this.footer.appendChild(cancelButton);
                this.footer.appendChild(okButton);
                // 焦點設置在確定按鈕上
                setTimeout(() => okButton.focus(), 100);
            }
            
            this.show();
            
            // 危險操作不允許點擊外部關閉，避免誤操作
            this.allowOutsideClick = !isDangerousAction;
        });
    }
      prompt(message, defaultValue = '', title = '請輸入', icon = 'edit') {
        return new Promise(resolve => {
            this.title.innerHTML = `<i class="fas fa-${icon}"></i> ${title}`;
            
            // 創建輸入框和說明文字，增加輸入框樣式
            this.body.innerHTML = `
                <p>${message}</p>
                <div class="modal-input-container">
                    <i class="fas fa-${icon}"></i>
                    <input type="text" class="modal-input" value="${defaultValue}" />
                </div>
            `;
            
            const input = this.body.querySelector('.modal-input');
            
            // 清空並創建確定和取消按鈕
            this.footer.innerHTML = '';
            
            const cancelButton = this.createButton('取消', '');
            cancelButton.addEventListener('click', () => {
                this.close(false);
                resolve(null);
            });
            
            const okButton = this.createButton('確定', 'success');
            okButton.addEventListener('click', () => {
                const value = input.value;
                this.close(true);
                resolve(value);
            });
            
            this.footer.appendChild(cancelButton);
            this.footer.appendChild(okButton);
            
            // 添加輸入框變化效果
            const inputContainer = this.body.querySelector('.modal-input-container');
            input.addEventListener('focus', () => {
                inputContainer.classList.add('focused');
            });
            
            input.addEventListener('blur', () => {
                inputContainer.classList.remove('focused');
            });
            
            // 為輸入框添加按 Enter 確認功能
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    const value = input.value;
                    this.close(true);
                    resolve(value);
                }
            });
            
            this.show();
            
            // 焦點設置在輸入框上
            setTimeout(() => input.focus(), 100);
            
            // prompt 模態視窗不允許點擊外部關閉
            this.allowOutsideClick = false;
        });
    }
    
    createButton(text, type = '') {
        const button = document.createElement('button');
        button.className = type ? `btn btn-${type}` : 'btn';
        button.textContent = text;
        return button;
    }
      show() {
        // 顯示模態視窗，添加淡入動畫
        this.overlay.classList.add('active');
        document.body.style.overflow = 'hidden'; // 防止背景滾動
        
        // 添加脈衝動畫效果
        setTimeout(() => this.pulse(), 300);
    }
    
    close(success = true) {
        // 關閉模態視窗，添加淡出動畫
        this.overlay.classList.add('closing');
        
        // 等待動畫完成後再隱藏
        setTimeout(() => {
            this.overlay.classList.remove('active');
            this.overlay.classList.remove('closing');
            document.body.style.overflow = ''; // 恢復背景滾動
            
            // 清除危險模式
            this.container.classList.remove('modal-danger');
            
            if (success && this.currentPromiseResolve) {
                this.currentPromiseResolve();
            } else if (this.currentPromiseReject) {
                this.currentPromiseReject();
            }
            
            this.currentPromiseResolve = null;
            this.currentPromiseReject = null;
        }, 300);
    }
    
    // 添加脈衝動畫效果
    pulse() {
        this.container.classList.add('pulse');
        setTimeout(() => {
            this.container.classList.remove('pulse');
        }, 1000);
    }
}

// 創建單例實例
const modal = new CustomModal();

// 僅替換 confirm 和 prompt 函數，保留 alert 使用右上角通知
window.originalConfirm = window.confirm;
window.originalPrompt = window.prompt;

window.confirm = function(message) {
    return modal.confirm(message);
};

window.prompt = function(message, defaultValue) {
    return modal.prompt(message, defaultValue);
};

// 導出模態視窗實例，以便在其他地方使用
window.customModal = modal;
