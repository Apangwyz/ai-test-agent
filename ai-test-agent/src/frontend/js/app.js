// 全局变量
let accessToken = localStorage.getItem('accessToken');

// DOM元素
const loginModal = document.getElementById('login-modal');
const registerModal = document.getElementById('register-modal');
const loginLink = document.getElementById('login-link');
const closeButtons = document.querySelectorAll('.close');
const registerLinks = document.querySelectorAll('.register-link a');
const loginLinks = document.querySelectorAll('.login-link a');

// 表单元素
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const documentForm = document.getElementById('document-form');
const clarificationForm = document.getElementById('clarification-form');
const techDocForm = document.getElementById('tech-doc-form');
const tasksForm = document.getElementById('tasks-form');
const testCasesForm = document.getElementById('test-cases-form');

// 结果元素
const documentResult = document.getElementById('document-result');
const clarificationResult = document.getElementById('clarification-result');
const techDocResult = document.getElementById('tech-doc-result');
const tasksResult = document.getElementById('tasks-result');
const testCasesResult = document.getElementById('test-cases-result');

// 初始化
function init() {
    // 绑定事件监听器
    bindEventListeners();
    // 检查登录状态
    checkLoginStatus();
    // 初始化平滑滚动
    initSmoothScroll();
    // 初始化表单验证
    initFormValidation();
}

// 绑定事件监听器
function bindEventListeners() {
    // 模态框控制
    loginLink.addEventListener('click', (e) => {
        e.preventDefault();
        if (accessToken) {
            logout();
        } else {
            loginModal.style.display = 'block';
        }
    });

    registerLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            loginModal.style.display = 'none';
            registerModal.style.display = 'block';
        });
    });

    loginLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            registerModal.style.display = 'none';
            loginModal.style.display = 'block';
        });
    });

    closeButtons.forEach(button => {
        button.addEventListener('click', () => {
            loginModal.style.display = 'none';
            registerModal.style.display = 'none';
        });
    });

    // 点击模态框外部关闭
    window.addEventListener('click', (e) => {
        if (e.target === loginModal) {
            loginModal.style.display = 'none';
        }
        if (e.target === registerModal) {
            registerModal.style.display = 'none';
        }
    });

    // 表单提交
    loginForm.addEventListener('submit', handleLogin);
    registerForm.addEventListener('submit', handleRegister);
    documentForm.addEventListener('submit', handleDocumentProcess);
    clarificationForm.addEventListener('submit', handleClarification);
    techDocForm.addEventListener('submit', handleTechDoc);
    tasksForm.addEventListener('submit', handleTasks);
    testCasesForm.addEventListener('submit', handleTestCases);

    // 表单输入验证
    const formInputs = document.querySelectorAll('input, textarea');
    formInputs.forEach(input => {
        input.addEventListener('input', () => {
            validateField(input);
        });
    });
}

// 初始化平滑滚动
function initSmoothScroll() {
    const navLinks = document.querySelectorAll('nav a');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            if (link.getAttribute('href').startsWith('#')) {
                e.preventDefault();
                const targetId = link.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
}

// 初始化表单验证
function initFormValidation() {
    // 可以在这里添加更多表单验证逻辑
}

// 验证表单字段
function validateField(field) {
    const errorMessage = field.nextElementSibling;
    if (field.hasAttribute('required') && !field.value.trim()) {
        field.classList.add('error');
        if (errorMessage && errorMessage.classList.contains('error-message')) {
            errorMessage.textContent = '此字段为必填项';
            errorMessage.classList.add('show');
        }
        return false;
    } else if (field.type === 'email' && field.value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(field.value)) {
            field.classList.add('error');
            if (errorMessage && errorMessage.classList.contains('error-message')) {
                errorMessage.textContent = '请输入有效的邮箱地址';
                errorMessage.classList.add('show');
            }
            return false;
        }
    }
    field.classList.remove('error');
    if (errorMessage && errorMessage.classList.contains('error-message')) {
        errorMessage.classList.remove('show');
    }
    return true;
}

// 显示加载动画
function showLoading(message = '处理中...') {
    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'loading-overlay';
    loadingOverlay.innerHTML = `
        <div class="loading-content">
            <div class="loading"></div>
            <p>${message}</p>
        </div>
    `;
    document.body.appendChild(loadingOverlay);
    return loadingOverlay;
}

// 隐藏加载动画
function hideLoading(loadingOverlay) {
    if (loadingOverlay && loadingOverlay.parentNode) {
        loadingOverlay.parentNode.removeChild(loadingOverlay);
    }
}

// 显示通知
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // 3秒后自动移除
    setTimeout(() => {
        notification.style.animation = 'slideInRight 0.3s ease reverse';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// 检查登录状态
function checkLoginStatus() {
    if (accessToken) {
        loginLink.textContent = '退出登录';
    } else {
        loginLink.textContent = '登录';
    }
}

// 退出登录
function logout() {
    localStorage.removeItem('accessToken');
    accessToken = null;
    checkLoginStatus();
    showNotification('已退出登录', 'success');
}

// 处理登录
function handleLogin(e) {
    e.preventDefault();
    
    // 验证表单
    const email = document.getElementById('email');
    const password = document.getElementById('password');
    
    if (!validateField(email) || !validateField(password)) {
        return;
    }
    
    const loadingOverlay = showLoading('登录中...');
    
    axios.post('/api/auth/login', { email: email.value, password: password.value })
        .then(response => {
            accessToken = response.data.access_token;
            localStorage.setItem('accessToken', accessToken);
            loginModal.style.display = 'none';
            checkLoginStatus();
            showNotification('登录成功', 'success');
        })
        .catch(error => {
            showNotification('登录失败: ' + (error.response?.data?.error || '未知错误'), 'error');
        })
        .finally(() => {
            hideLoading(loadingOverlay);
        });
}

// 处理注册
function handleRegister(e) {
    e.preventDefault();
    
    // 验证表单
    const username = document.getElementById('username');
    const email = document.getElementById('register-email');
    const password = document.getElementById('register-password');
    
    if (!validateField(username) || !validateField(email) || !validateField(password)) {
        return;
    }
    
    const loadingOverlay = showLoading('注册中...');
    
    axios.post('/api/auth/register', { 
        username: username.value, 
        email: email.value, 
        password: password.value 
    })
        .then(response => {
            registerModal.style.display = 'none';
            loginModal.style.display = 'block';
            showNotification('注册成功，请登录', 'success');
        })
        .catch(error => {
            showNotification('注册失败: ' + (error.response?.data?.error || '未知错误'), 'error');
        })
        .finally(() => {
            hideLoading(loadingOverlay);
        });
}

// 处理文档处理
function handleDocumentProcess(e) {
    e.preventDefault();
    const file = document.getElementById('document-file').files[0];
    
    if (!file) {
        showNotification('请选择要上传的文档', 'warning');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    const loadingOverlay = showLoading('处理文档中...');
    
    axios.post('/api/documents/process', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': accessToken ? `Bearer ${accessToken}` : ''
        }
    })
    .then(response => {
        documentResult.innerHTML = `
            <h3>处理结果</h3>
            <pre>${JSON.stringify(response.data.structured_data, null, 2)}</pre>
        `;
        // 将结果填充到后续表单
        document.getElementById('structured-data').value = JSON.stringify(response.data.structured_data, null, 2);
        document.getElementById('tech-structured-data').value = JSON.stringify(response.data.structured_data, null, 2);
        document.getElementById('test-structured-data').value = JSON.stringify(response.data.structured_data, null, 2);
        showNotification('文档处理成功', 'success');
    })
    .catch(error => {
        showNotification('文档处理失败: ' + (error.response?.data?.error || '未知错误'), 'error');
    })
    .finally(() => {
        hideLoading(loadingOverlay);
    });
}

// 处理需求澄清
function handleClarification(e) {
    e.preventDefault();
    const structuredData = document.getElementById('structured-data');
    
    if (!validateField(structuredData)) {
        return;
    }
    
    const loadingOverlay = showLoading('生成澄清文档中...');
    
    try {
        const parsedData = JSON.parse(structuredData.value);
        
        axios.post('/api/clarification/generate', { structured_data: parsedData }, {
            headers: {
                'Authorization': accessToken ? `Bearer ${accessToken}` : ''
            }
        })
        .then(response => {
            clarificationResult.innerHTML = `
                <h3>澄清文档</h3>
                <pre>${JSON.stringify(response.data.clarification_doc, null, 2)}</pre>
            `;
            // 将结果填充到技术方案表单
            document.getElementById('clarification-doc').value = JSON.stringify(response.data.clarification_doc, null, 2);
            showNotification('澄清文档生成成功', 'success');
        })
        .catch(error => {
            showNotification('生成澄清文档失败: ' + (error.response?.data?.error || '未知错误'), 'error');
        })
        .finally(() => {
            hideLoading(loadingOverlay);
        });
    } catch (error) {
        showNotification('请输入有效的JSON格式数据', 'error');
        hideLoading(loadingOverlay);
    }
}

// 处理技术方案生成
function handleTechDoc(e) {
    e.preventDefault();
    const structuredData = document.getElementById('tech-structured-data');
    
    if (!validateField(structuredData)) {
        return;
    }
    
    const loadingOverlay = showLoading('生成技术方案中...');
    
    try {
        const parsedData = JSON.parse(structuredData.value);
        const clarificationDoc = document.getElementById('clarification-doc').value ? JSON.parse(document.getElementById('clarification-doc').value) : null;
        
        axios.post('/api/tech-doc/generate', { 
            structured_data: parsedData, 
            clarification_doc: clarificationDoc 
        }, {
            headers: {
                'Authorization': accessToken ? `Bearer ${accessToken}` : ''
            }
        })
        .then(response => {
            techDocResult.innerHTML = `
                <h3>技术方案文档</h3>
                <pre>${JSON.stringify(response.data.tech_doc, null, 2)}</pre>
            `;
            // 将结果填充到编码任务表单
            document.getElementById('tech-doc-input').value = JSON.stringify(response.data.tech_doc, null, 2);
            document.getElementById('test-tech-doc').value = JSON.stringify(response.data.tech_doc, null, 2);
            showNotification('技术方案生成成功', 'success');
        })
        .catch(error => {
            showNotification('生成技术方案失败: ' + (error.response?.data?.error || '未知错误'), 'error');
        })
        .finally(() => {
            hideLoading(loadingOverlay);
        });
    } catch (error) {
        showNotification('请输入有效的JSON格式数据', 'error');
        hideLoading(loadingOverlay);
    }
}

// 处理编码任务生成
function handleTasks(e) {
    e.preventDefault();
    const techDoc = document.getElementById('tech-doc-input');
    
    if (!validateField(techDoc)) {
        return;
    }
    
    const loadingOverlay = showLoading('生成编码任务中...');
    
    try {
        const parsedData = JSON.parse(techDoc.value);
        
        axios.post('/api/tasks/generate', { tech_doc: parsedData }, {
            headers: {
                'Authorization': accessToken ? `Bearer ${accessToken}` : ''
            }
        })
        .then(response => {
            tasksResult.innerHTML = `
                <h3>编码任务文档</h3>
                <pre>${JSON.stringify(response.data.tasks, null, 2)}</pre>
            `;
            showNotification('编码任务生成成功', 'success');
        })
        .catch(error => {
            showNotification('生成编码任务失败: ' + (error.response?.data?.error || '未知错误'), 'error');
        })
        .finally(() => {
            hideLoading(loadingOverlay);
        });
    } catch (error) {
        showNotification('请输入有效的JSON格式数据', 'error');
        hideLoading(loadingOverlay);
    }
}

// 处理测试案例生成
function handleTestCases(e) {
    e.preventDefault();
    const structuredData = document.getElementById('test-structured-data');
    const techDoc = document.getElementById('test-tech-doc');
    
    if (!validateField(structuredData) || !validateField(techDoc)) {
        return;
    }
    
    const loadingOverlay = showLoading('生成测试案例中...');
    
    try {
        const parsedStructuredData = JSON.parse(structuredData.value);
        const parsedTechDoc = JSON.parse(techDoc.value);
        
        axios.post('/api/test-cases/generate', { 
            structured_data: parsedStructuredData, 
            tech_doc: parsedTechDoc 
        }, {
            headers: {
                'Authorization': accessToken ? `Bearer ${accessToken}` : ''
            }
        })
        .then(response => {
            testCasesResult.innerHTML = `
                <h3>测试案例脑图</h3>
                <pre>${JSON.stringify(response.data.test_cases, null, 2)}</pre>
            `;
            showNotification('测试案例生成成功', 'success');
        })
        .catch(error => {
            showNotification('生成测试案例失败: ' + (error.response?.data?.error || '未知错误'), 'error');
        })
        .finally(() => {
            hideLoading(loadingOverlay);
        });
    } catch (error) {
        showNotification('请输入有效的JSON格式数据', 'error');
        hideLoading(loadingOverlay);
    }
}

// 初始化应用
init();