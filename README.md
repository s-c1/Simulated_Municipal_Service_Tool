# Simulated_Municipal_Database
Introduction: 
A group project that used SQLite3 module in Python to execute SQL statements to fulfill a series of tasks, like registering a new-born, paying for tickets. All actions are done through the console.

User guide:
- To start the program, call "python3 mini1.py <database name>", the program will ask for your username and password, please enter them following the "Username: " and "Password: " prompts. Password is case sensitive, and will not show on screen when typed (e.g. Username: 100, Password: abc12345)
- The system will present a list of actions users can choose to execute

Prevent injection on database:
During logon(), where the username and password is checked so that malicious users cannot inject sql. (e.g. using "'1'='1'" as password will not pass the test in our system)
