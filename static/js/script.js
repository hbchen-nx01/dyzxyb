// 自定义JavaScript脚本
// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有功能
    initFormValidation();
    initLoadingIndicators();
    initModalInteractions();
    initTableInteractions();
    initImageOptimization();
    initLazyLoading();
});

// 表单验证初始化
function initFormValidation() {
    // 为所有表单添加提交事件监听
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // 检查必填字段
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            // 如果有无效字段，阻止表单提交
            if (!isValid) {
                e.preventDefault();
                showAlert('请填写所有必填字段', 'danger');
            } else {
                // 表单有效，添加加载状态
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 提交中...';
                }
            }
        });
        
        // 为必填字段添加输入事件监听，移除无效状态
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            field.addEventListener('input', function() {
                if (this.value.trim()) {
                    this.classList.remove('is-invalid');
                }
            });
        });
    });
}

// 加载指示器初始化
function initLoadingIndicators() {
    // 为所有带有loading类的按钮添加点击事件
    const loadingButtons = document.querySelectorAll('.btn[data-loading]');
    loadingButtons.forEach(button => {
        button.addEventListener('click', function() {
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> ' + this.dataset.loading;
            this.disabled = true;
            
            // 模拟异步操作完成后恢复按钮状态
            // 实际使用时，应该在异步操作完成后调用这些代码
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
            }, 2000);
        });
    });
}

// 模态框交互初始化
function initModalInteractions() {
    // 关闭模态框时重置表单
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('hidden.bs.modal', function() {
            const form = this.querySelector('form');
            if (form) {
                form.reset();
                // 移除所有验证状态
                const invalidFields = form.querySelectorAll('.is-invalid');
                invalidFields.forEach(field => field.classList.remove('is-invalid'));
            }
        });
    });
}

// 表格交互初始化
function initTableInteractions() {
    // 为表格行添加悬停效果
    const tableRows = document.querySelectorAll('table tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f8f9fa';
        });
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });
    
    // 为带有[data-toggle="tooltip"]的元素初始化工具提示
    const tooltips = document.querySelectorAll('[data-toggle="tooltip"]');
    if (tooltips.length > 0) {
        // 检查Bootstrap是否可用
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            tooltips.forEach(tooltip => {
                new bootstrap.Tooltip(tooltip);
            });
        }
    }
}

// 显示alert提示
function showAlert(message, type = 'info') {
    // 创建alert元素
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3 z-50`;
    alertDiv.style.minWidth = '300px';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // 添加到页面
    document.body.appendChild(alertDiv);
    
    // 3秒后自动关闭
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(alertDiv);
        }, 500);
    }, 3000);
}

// 图片优化初始化
function initImageOptimization() {
    // 为所有图片添加延迟加载属性
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        // 检查是否已经有loading属性
        if (!img.hasAttribute('loading')) {
            img.setAttribute('loading', 'lazy');
        }
        
        // 设置图片错误处理
        img.addEventListener('error', function() {
            // 图片加载失败时显示占位符
            this.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"%3E%3Crect width="100" height="100" fill="%23e9ecef"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" fill="%236c757d" font-family="Arial, sans-serif" font-size="14"%3E图片加载失败%3C/text%3E%3C/svg%3E';
        });
    });
}

// 延迟加载初始化
function initLazyLoading() {
    // 检查浏览器是否支持IntersectionObserver
    if ('IntersectionObserver' in window) {
        // 为动态内容添加延迟加载
        const lazyElements = document.querySelectorAll('.lazy-load');
        
        const observer = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    // 元素进入视口，添加可见类
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1
        });
        
        lazyElements.forEach(el => {
            observer.observe(el);
        });
    }
}
