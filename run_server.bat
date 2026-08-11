@echo off

cd /d C:\tamilvanan\EEM\Electricity_Power_Monitoring_be

call .env312\Scripts\activate.bat

python -m uvicorn electricity_monitoring_be.asgi:application --host 0.0.0.0 --port 8000

pause