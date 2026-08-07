import electricity_monitoring_be.application as app

print(app)
print(hasattr(app, "application"))

if hasattr(app, "application"):
    print(app.application)