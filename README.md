### Library Management System - README

Explanation video available on youtube on Tara Brothers channel

#### Overview
The Library Management System is a simple, lightweight application to manage books, users, and transactions in a library. It provides essential features for organizing library records and running a small-scale library efficiently.

---

### Features
1. **Book Management**: Add, edit, and delete book records.  
2. **User Management**: Register and manage library users.  
3. **Transaction Management**: Track book issues and returns.  

---

### Installation Instructions

1. **Download the Application**  
   Download the project files and ensure all files are in the same directory.

2. **Install Python Requirements**  
   Open a terminal and navigate to the project directory. Run the following command to install the required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up the Database**  
   Ensure your database (e.g., SQLite) is set up. If necessary, you can use the provided database file or run database migrations as required by your application.

4. **Run the Application**  
   Start the application by executing the following command in the terminal:
   ```bash
   python app.py
   ```
   Replace `app.py` with the main Python file if it has a different name.

5. **Access the Application**  
   Open your web browser and go to `http://127.0.0.1:5000` to access the application.

---

### Common Errors and Solutions

1. **Error**: *ModuleNotFoundError: No module named 'flask'*  
   **Solution**: Ensure you have installed the required modules by running `pip install -r requirements.txt`.

2. **Error**: *Address already in use*  
   **Solution**: Stop any process using port 5000 or specify another port on the terminal with:  
   ```bash
   python app.py --port 8080
   ```

3. **Error**: *OperationalError: unable to open database file*  
   **Solution**: Verify the database file exists in the specified location and the application has write permissions.

---

Enjoy managing your library effortlessly!
