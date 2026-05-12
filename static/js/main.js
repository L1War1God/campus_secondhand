// =====================================================
// 公共JS - API调用、工具函数
// =====================================================

// API基础地址
const API_BASE = '/api';

// 用户信息存储key
const USER_KEY = 'campus_user';

// ========== 工具函数 ==========

// 获取当前登录用户
function getCurrentUser() {
    const userStr = localStorage.getItem(USER_KEY);
    if (userStr) {
        try {
            return JSON.parse(userStr);
        } catch (e) {
            return null;
        }
    }
    return null;
}

// 保存用户信息
function saveUser(user) {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
}

// 清除用户信息(登出)
function clearUser() {
    localStorage.removeItem(USER_KEY);
}

// 检查是否已登录,未登录则跳转登录页
function requireAuth() {
    const user = getCurrentUser();
    if (!user) {
        window.location.href = '/page/login';
        return false;
    }
    return true;
}

// 通用API请求函数
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        }
    };

    const finalOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };

    try {
        const response = await fetch(API_BASE + url, finalOptions);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API请求失败:', error);
        return { code: 500, message: '网络错误,请稍后重试' };
    }
}

// GET请求
function apiGet(url) {
    return apiRequest(url, { method: 'GET' });
}

// POST请求
function apiPost(url, body) {
    return apiRequest(url, {
        method: 'POST',
        body: JSON.stringify(body)
    });
}

// PUT请求
function apiPut(url, body) {
    return apiRequest(url, {
        method: 'PUT',
        body: JSON.stringify(body)
    });
}

// DELETE请求
function apiDelete(url) {
    return apiRequest(url, { method: 'DELETE' });
}

const FAVORITE_CACHE_PREFIX = 'campus_favorite_ids_';

function getFavoriteCacheKey(userId) {
    return `${FAVORITE_CACHE_PREFIX}${userId}`;
}

function readFavoriteCache(userId) {
    try {
        const cached = localStorage.getItem(getFavoriteCacheKey(userId));
        if (!cached) return [];
        const parsed = JSON.parse(cached);
        return Array.isArray(parsed) ? parsed.map(id => Number(id)).filter(Number.isFinite) : [];
    } catch (error) {
        return [];
    }
}

function writeFavoriteCache(userId, ids) {
    localStorage.setItem(getFavoriteCacheKey(userId), JSON.stringify(Array.from(new Set((ids || []).map(id => Number(id)).filter(Number.isFinite)))));
}

function updateFavoriteCache(userId, productId, isFavorited) {
    if (!userId) return [];
    const favoriteIds = readFavoriteCache(userId);
    const normalizedProductId = Number(productId);
    const existsIndex = favoriteIds.indexOf(normalizedProductId);

    if (isFavorited && existsIndex === -1) {
        favoriteIds.push(normalizedProductId);
    } else if (!isFavorited && existsIndex !== -1) {
        favoriteIds.splice(existsIndex, 1);
    }

    writeFavoriteCache(userId, favoriteIds);
    return favoriteIds;
}

async function getFavoriteIds(userId, forceRefresh = false) {
    if (!userId) return [];
    if (!forceRefresh) {
        const cached = readFavoriteCache(userId);
        if (cached.length > 0) {
            return cached;
        }
    }

    const result = await apiGet(`/favorites?user_id=${userId}`);
    if (result.code === 200 && Array.isArray(result.data)) {
        const favoriteIds = result.data.map(item => Number(item.product_id)).filter(Number.isFinite);
        writeFavoriteCache(userId, favoriteIds);
        return favoriteIds;
    }

    return [];
}

function setFavoriteButtonState(button, isFavorited) {
    if (!button) return;
    button.classList.toggle('favorited', Boolean(isFavorited));
    button.title = isFavorited ? '已收藏' : '收藏';

    const textEl = button.querySelector('.favorite-text');
    if (textEl) {
        textEl.textContent = isFavorited ? '已收藏' : '收藏';
    }
}

async function syncFavoriteButtons(root = document, forceRefresh = false) {
    const user = getCurrentUser();
    if (!user) return;

    const favoriteIds = await getFavoriteIds(user.id, forceRefresh);
    const buttons = root.querySelectorAll('[data-product-id]');
    buttons.forEach(button => {
        const productId = Number(button.dataset.productId);
        if (!Number.isFinite(productId)) return;
        setFavoriteButtonState(button, favoriteIds.includes(productId));
    });
}

window.updateFavoriteCache = updateFavoriteCache;
window.getFavoriteIds = getFavoriteIds;
window.setFavoriteButtonState = setFavoriteButtonState;
window.syncFavoriteButtons = syncFavoriteButtons;

// 显示提示消息
function showMessage(message, type = 'success') {
    // 创建提示元素
    const toast = document.createElement('div');
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        padding: 12px 20px;
        background: ${type === 'success' ? '#4CAF50' : '#f44336'};
        color: white;
        border-radius: 5px;
        z-index: 2000;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// 添加动画样式
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// 加载分类下拉框
async function loadCategories(selectId, parentId = 0) {
    const result = await apiGet('/categories');
    if (result.code === 200 && result.data) {
        let categories = result.data;
        if (parentId === 0) {
            categories = categories.filter(c => c.children);
        }

        const select = document.getElementById(selectId);
        if (select) {
            select.innerHTML = '<option value="">请选择分类</option>';
            categories.forEach(cat => {
                select.innerHTML += `<option value="${cat.id}">${cat.name}</option>`;
                if (cat.children) {
                    cat.children.forEach(sub => {
                        select.innerHTML += `<option value="${sub.id}">　├ ${sub.name}</option>`;
                    });
                }
            });
        }
    }
}

// 加载头部导航
function loadHeader() {
    const user = getCurrentUser();
    const navMenu = document.getElementById('navMenu');
    if (!navMenu) return;

    if (user) {
        navMenu.innerHTML = `
            <span class="user-name">${user.username}</span>
            <a href="/page/index">首页</a>
            <a href="/page/profile">个人中心</a>
            <a href="/page/cart">购物车</a>
            <a href="/page/orders">我的订单</a>
            <a href="/page/publish">发布商品</a>
            ${user.role === 'admin' ? '<a href="/page/admin">后台管理</a>' : ''}
            <button class="logout-btn" onclick="handleLogout()">退出</button>
        `;
    } else {
        navMenu.innerHTML = `
            <a href="/page/index">首页</a>
            <a href="/page/login">登录</a>
            <a href="/page/register">注册</a>
        `;
    }
}

// 退出登录
function handleLogout() {
    clearUser();
    showMessage('已退出登录');
    setTimeout(() => {
        window.location.href = '/page/index';
    }, 1000);
}

// 格式化价格
function formatPrice(price) {
    return '¥' + parseFloat(price).toFixed(2);
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function () {
    loadHeader();
});