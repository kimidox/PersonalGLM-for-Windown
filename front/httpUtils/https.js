// 基础配置
const config = {
  baseURL: 'http://127.0.0.1:8080', // Python 服务地址
  timeout: 10000, // 默认超时时间（毫秒）
  headers: {
    'Content-Type': 'application/json',
  },
};

// 请求拦截器
const requestInterceptor = (config) => {
  // 可以在这里添加 token、修改 headers 等
  // 例如：config.headers['Authorization'] = `Bearer ${token}`;
  return config;
};

// 响应拦截器
const responseInterceptor = async (response) => {
  // 统一处理响应
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: response.statusText }));
    throw new Error(error.message || `HTTP Error: ${response.status}`);
  }
  return response.json();
};

// 超时处理
const fetchWithTimeout = (url, options, timeout) => {
  return Promise.race([
    fetch(url, options),
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error('请求超时')), timeout)
    ),
  ]);
};

// 核心请求方法
const request = async (url, options = {}) => {
  try {
    // 合并配置
    const finalConfig = {
      ...config,
      headers: {
        ...config.headers,
        ...options.headers,
      },
      ...options,
    };

    // 应用请求拦截器
    const interceptedConfig = requestInterceptor(finalConfig);

    // 构建完整 URL
    const fullUrl = url.startsWith('http') 
      ? url 
      : `${interceptedConfig.baseURL}${url.startsWith('/') ? url : '/' + url}`;

    // 发送请求
    const response = await fetchWithTimeout(
      fullUrl,
      {
        method: interceptedConfig.method || 'GET',
        headers: interceptedConfig.headers,
        body: interceptedConfig.body 
          ? JSON.stringify(interceptedConfig.body) 
          : undefined,
      },
      interceptedConfig.timeout
    );

    // 应用响应拦截器
    return await responseInterceptor(response);
  } catch (error) {
    // 统一错误处理
    console.error('请求失败:', error);
    throw error;
  }
};

// 便捷方法
export const http = {
  // GET 请求
  get: (url, params = {}, options = {}) => {
    const queryString = new URLSearchParams(params).toString();
    const fullUrl = queryString ? `${url}?${queryString}` : url;
    return request(fullUrl, { ...options, method: 'GET' });
  },

  // POST 请求
  post: (url, data = {}, options = {}) => {
    return request(url, {
      ...options,
      method: 'POST',
      body: data,
    });
  },

  // PUT 请求
  put: (url, data = {}, options = {}) => {
    return request(url, {
      ...options,
      method: 'PUT',
      body: data,
    });
  },

  // DELETE 请求
  delete: (url, options = {}) => {
    return request(url, {
      ...options,
      method: 'DELETE',
    });
  },

  // PATCH 请求
  patch: (url, data = {}, options = {}) => {
    return request(url, {
      ...options,
      method: 'PATCH',
      body: data,
    });
  },

  // 自定义请求
  request: (options) => {
    return request(options.url || '', options);
  },

  // 更新配置
  setConfig: (newConfig) => {
    Object.assign(config, newConfig);
  },

  // 获取配置
  getConfig: () => ({ ...config }),
};

// 默认导出
export default http;