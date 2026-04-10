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
}

// 绑定事件监听器
function bindEventListeners() {
    // 模态框控制
    loginLink.addEventListener('click', (e) => {
        e.preventDefault();
        loginModal.style.display = 'block';
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
}

// 检查登录状态
function checkLoginStatus() {
    if (accessToken) {
        loginLink.textContent = '退出登录';
        loginLink.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    }
}

// 退出登录
function logout() {
    localStorage.removeItem('accessToken');
    accessToken = null;
    loginLink.textContent = '登录';
    loginLink.removeEventListener('click', logout);
    loginLink.addEventListener('click', (e) => {
        e.preventDefault();
        loginModal.style.display = 'block';
    });
    alert('已退出登录');
}

// 处理登录
function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    axios.post('/api/auth/login', { email, password })
        .then(response => {
            accessToken = response.data.access_token;
            localStorage.setItem('accessToken', accessToken);
            loginModal.style.display = 'none';
            checkLoginStatus();
            alert('登录成功');
        })
        .catch(error => {
            alert('登录失败: ' + (error.response?.data?.error || '未知错误'));
        });
}

// 处理注册
function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;

    axios.post('/api/auth/register', { username, email, password })
        .then(response => {
            registerModal.style.display = 'none';
            loginModal.style.display = 'block';
            alert('注册成功，请登录');
        })
        .catch(error => {
            alert('注册失败: ' + (error.response?.data?.error || '未知错误'));
        });
}

// 处理文档处理
function handleDocumentProcess(e) {
    e.preventDefault();
    const file = document.getElementById('document-file').files[0];
    const formData = new FormData();
    formData.append('file', file);

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
    })
    .catch(error => {
        alert('文档处理失败: ' + (error.response?.data?.error || '未知错误'));
    });
}

// 处理需求澄清
function handleClarification(e) {
    e.preventDefault();
    const structuredData = JSON.parse(document.getElementById('structured-data').value);

    axios.post('/api/clarification/generate', { structured_data: structuredData }, {
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
    })
    .catch(error => {
        alert('生成澄清文档失败: ' + (error.response?.data?.error || '未知错误'));
    });
}

// 处理技术方案生成
function handleTechDoc(e) {
    e.preventDefault();
    const structuredData = JSON.parse(document.getElementById('tech-structured-data').value);
    const clarificationDoc = document.getElementById('clarification-doc').value ? JSON.parse(document.getElementById('clarification-doc').value) : null;

    axios.post('/api/tech-doc/generate', { structured_data: structuredData, clarification_doc: clarificationDoc }, {
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
    })
    .catch(error => {
        alert('生成技术方案失败: ' + (error.response?.data?.error || '未知错误'));
    });
}

// 处理编码任务生成
function handleTasks(e) {
    e.preventDefault();
    const techDoc = JSON.parse(document.getElementById('tech-doc-input').value);

    axios.post('/api/tasks/generate', { tech_doc: techDoc }, {
        headers: {
            'Authorization': accessToken ? `Bearer ${accessToken}` : ''
        }
    })
    .then(response => {
        tasksResult.innerHTML = `
            <h3>编码任务文档</h3>
            <pre>${JSON.stringify(response.data.tasks, null, 2)}</pre>
        `;
    })
    .catch(error => {
        alert('生成编码任务失败: ' + (error.response?.data?.error || '未知错误'));
    });
}

// 处理测试案例生成
function handleTestCases(e) {
    e.preventDefault();
    const structuredData = JSON.parse(document.getElementById('test-structured-data').value);
    const techDoc = JSON.parse(document.getElementById('test-tech-doc').value);

    axios.post('/api/test-cases/generate', { structured_data: structuredData, tech_doc: techDoc }, {
        headers: {
            'Authorization': accessToken ? `Bearer ${accessToken}` : ''
        }
    })
    .then(response => {
        testCasesResult.innerHTML = `
            <h3>测试案例脑图</h3>
            <pre>${JSON.stringify(response.data.test_cases, null, 2)}</pre>
        `;
    })
    .catch(error => {
        alert('生成测试案例失败: ' + (error.response?.data?.error || '未知错误'));
    });
}

// 初始化应用
init();