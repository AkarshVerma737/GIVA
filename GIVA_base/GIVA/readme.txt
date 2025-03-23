run app.py
In Powershell enter:
Invoke-RestMethod -Method Post -Uri "http://localhost:5000/shorten" -ContentType "application/json" -Body '{"long_url": "https://example/link/edit_it"}'