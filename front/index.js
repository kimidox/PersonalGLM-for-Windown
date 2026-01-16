import { app, BrowserWindow, ipcMain } from 'electron/main';
import { spawn } from 'child_process';
import  path  from 'path';
import  net  from 'net';
import { fileURLToPath } from 'url';
import { createRequire } from 'module';

// 在 ES 模块中获取 __dirname 的等价物
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 创建 require 函数用于加载 CommonJS 模块
const require = createRequire(import.meta.url);

// 1. 引入并配置 electron-reload（仅在开发环境使用）

try {
  const electronReload = require('electron-reload');
  electronReload(__dirname, {
    electron: process.execPath, // 使用当前运行的 electron 路径
    hardResetMethod: 'exit',
    extensions: ['js', 'html', 'css']
  });
  console.log('electron-reload 已启用');
} catch (error) {
  console.warn('electron-reload 加载失败，继续运行:', error.message);
  console.error(error);
}





let mainWindow;
let pythonProcess = null; // Python进程实例
const PYTHON_PORT = 8080; // Python服务端口
const PYTHON_SCRIPT = '../backend/app.py'; // Python脚本名


// 检查Python服务是否已启动（端口检测）
function checkPythonServer(callback) {
  const client = new net.Socket();
  client.setTimeout(1000); // 超时时间1秒

  client.on('connect', () => {
    client.destroy();
    callback(true); // 服务已启动
  });

  client.on('timeout', () => {
    client.destroy();
    callback(false); // 连接超时，服务未启动
  });

  client.on('error', () => {
    client.destroy();
    callback(false); // 连接失败，服务未启动
  });

  client.connect(PYTHON_PORT, '127.0.0.1');
}

// 启动Python HTTP服务
function startPythonServer() {
  // 先检查端口是否被占用
  checkPythonServer((isRunning) => {
    if (isRunning) {
      console.log(`Python服务已在端口 ${PYTHON_PORT} 运行`);
      return;
    }

    // 确定Python脚本路径（兼容开发/打包后环境）
   const scriptPath = path.join(__dirname, PYTHON_SCRIPT);
    // 打包后Python可能是exe文件，这里做兼容判断

   const isPackaged = app.isPackaged;
   let pythonExec;
    if (!isPackaged) {
      // 虚拟环境路径配置（根据你的实际虚拟环境目录调整！）
      // Windows虚拟环境：项目根目录/.venv/Scripts/python.exe
      // macOS/Linux虚拟环境：项目根目录/.venv/bin/python
      const venvDir = path.join(__dirname, '../.venv'); // 虚拟环境根目录
      pythonExec = process.platform === 'win32' 
        ? path.join(venvDir, 'Scripts', 'python.exe') 
        : path.join(venvDir, 'bin', 'python');
    } else {
      // 打包后：使用打包的可执行文件（保持原有逻辑）
      pythonExec = path.join(__dirname, 'backend_api.exe');
    }

    // 启动Python进程
    try {
       // 命令参数：开发环境传脚本路径，打包后不传
      const args = isPackaged ? [] : [scriptPath];
      console.log(`starting Python server,using relation：${pythonExec}`);
      console.log(`Python script path：${scriptPath}`);

      pythonProcess = spawn(pythonExec, args, {
        windowsHide: true, // 隐藏Python控制台窗口（Windows）
        stdio: ['pipe', 'pipe', 'pipe'], // 继承标准输出，便于调试
        cwd: path.dirname(scriptPath) // 切换到Python脚本所在目录（关键！）
      });


      console.log(`starting python server,this scripPath::${scriptPath}`);

      // 监听Python进程输出（调试用）
      pythonProcess.stdout.on('data', (data) => {
        console.log(`Python logs: ${data.toString().trim()}`);
      });

      // 监听Python错误输出
      pythonProcess.stderr.on('data', (data) => {
        console.error(`Python errors: ${data.toString().trim()}`);
      });

      // 监听Python进程退出事件
      pythonProcess.on('exit', (code, signal) => {
        console.log(`Python is brokend ,this code: ${code},signal: ${signal}`);
        pythonProcess = null;
        
        // 如果不是应用退出导致的进程终止，尝试重启（可选）
        if (!app.isQuitting && code !== 0) {
          console.log('Python server exit error,5 seconds after try to restart...');
          setTimeout(startPythonServer, 5000);
        }
      });

      // 监听进程启动失败
      pythonProcess.on('error', (err) => {
        console.error(`start Python server error: ${err.message}`);
        // 提示用户检查Python环境或脚本
        if (mainWindow) {
          mainWindow.webContents.send('python-server-error', err.message);
        }
      });

    } catch (error) {
      console.error(`start Python server exception: ${error}`);
    }
  });
}

// 等待Python服务就绪（轮询端口）
function waitForPythonServer(maxRetries = 10, interval = 500) {
  return new Promise((resolve, reject) => {
    let retries = 0;
    
    const check = () => {
      checkPythonServer((isRunning) => {
        retries++;
        if (isRunning) {
          resolve(true);
        } else if (retries >= maxRetries) {
          reject(new Error(`Python服务启动超时，重试${maxRetries}次后仍未就绪`));
        } else {
          setTimeout(check, interval);
        }
      });
    };

    check();
  });
}


const createWindow = async () => {
  const win = new BrowserWindow({
    width: 800,
    height: 600
  });

  mainWindow = win; // 赋值给全局变量

  // 先等待Python服务就绪，再加载页面（避免前端调用接口时服务未启动）
  try {
    await waitForPythonServer();
    console.log('Python server had ready,loading front views');
    win.loadFile('./views/test.html');
  } catch (error) {
    console.error(error.message);
    // 即使Python启动失败，也加载页面并提示用户
    win.loadFile('./views/test.html');
    // 向渲染进程发送错误信息
    win.webContents.on('did-finish-load', () => {
      win.webContents.send('python-server-error', error.message);
    });
  }

  win.webContents.openDevTools();
};


app.whenReady().then(async () => {
  
  // 第一步：启动Python服务
  startPythonServer();
  
  // 第二步：创建窗口（内部会等待Python服务就绪）
  await createWindow();

});


// 应用退出时优雅关闭Python进程
app.on('before-quit', () => {
  app.isQuitting = true;
  if (pythonProcess) {
    console.log('stoping Python server...');
    // 先尝试优雅终止
    pythonProcess.kill('SIGINT');
    // 500ms后强制终止（防止优雅终止失败）
    setTimeout(() => {
      if (!pythonProcess.killed) {
        pythonProcess.kill('SIGKILL');
      }
    }, 500);
  }
});




app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
  });


// 给渲染进程提供检查Python服务状态的接口
ipcMain.handle('check-python-status', async () => {
  return new Promise((resolve) => {
    checkPythonServer(resolve);
  });
});