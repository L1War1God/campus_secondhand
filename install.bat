@echo off
echo ================================================
echo 校园二手交易平台 - 依赖安装脚本
echo ================================================
echo.

echo 正在安装 Python 依赖...
pip install flask flask-sqlalchemy flask-cors

echo.
echo ================================================
echo 依赖安装完成!
echo 请运行 start.bat 启动程序
echo ================================================
pause