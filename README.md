# Simulated_Municipal_Service_Tool
Introduction: 
A command line interface (CLI) tool developed by a 3-person group, which interacts with a database via the use of SQLite3 module in Python to execute SQL statements and fulfill a series of tasks, like registering a new-born, paying for tickets. :smiley:

User guide:
- To start the program, call "python3 mini1.py <database name>", the program will ask for your username and password, please enter them following the "Username: " and "Password: " prompts. Password is case sensitive, and will not show on screen when typed (e.g. Username: 100, Password: abc12345)
- Prevent injection on database: During logon(), where the username and password is checked so that malicious users cannot inject sql. (e.g. using "'1'='1'" as password will not pass the test in our system)	
- The system will present a list of actions users can choose to execute
- For example, type "birth" to register a new-born
![](https://github.com/Susan-C-a/Simulated_Municipal_Database/blob/master/reg_birth.JPG)
