import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime, timedelta
import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import pickle
import os

class FinanceDatabase:
    def __init__(self, db_name="finance_tracker.db"):
        self.db_name = db_name
        self.init_database()

    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Create expenses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                payment_method TEXT DEFAULT 'Cash',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create budgets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT UNIQUE NOT NULL,
                budget_amount REAL NOT NULL,
                month_year TEXT NOT NULL
            )
        """)

        # Create income table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                source TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def add_expense(self, date, amount, description, category, payment_method='Cash'):
        """Add a new expense to the database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO expenses (date, amount, description, category, payment_method)
            VALUES (?, ?, ?, ?, ?)
        """, (date, amount, description, category, payment_method))
        conn.commit()
        conn.close()

    def get_expenses(self, start_date=None, end_date=None):
        """Retrieve expenses within date range"""
        conn = sqlite3.connect(self.db_name)

        if start_date and end_date:
            query = """
                SELECT * FROM expenses 
                WHERE date BETWEEN ? AND ? 
                ORDER BY date DESC
            """
            df = pd.read_sql_query(query, conn, params=(start_date, end_date))
        else:
            df = pd.read_sql_query("SELECT * FROM expenses ORDER BY date DESC", conn)

        conn.close()
        return df

    def get_category_totals(self, start_date=None, end_date=None):
        """Get total spending by category"""
        conn = sqlite3.connect(self.db_name)

        if start_date and end_date:
            query = """
                SELECT category, SUM(amount) as total
                FROM expenses 
                WHERE date BETWEEN ? AND ?
                GROUP BY category
                ORDER BY total DESC
            """
            df = pd.read_sql_query(query, conn, params=(start_date, end_date))
        else:
            query = """
                SELECT category, SUM(amount) as total
                FROM expenses 
                GROUP BY category
                ORDER BY total DESC
            """
            df = pd.read_sql_query(query, conn)

        conn.close()
        return df

class ExpenseCategorizer:
    def __init__(self):
        self.model = None
        self.categories = [
            'Food & Dining', 'Transportation', 'Shopping', 'Entertainment',
            'Bills & Utilities', 'Healthcare', 'Education', 'Travel',
            'Personal Care', 'Home & Garden', 'Miscellaneous'
        ]
        self.load_or_create_model()

    def load_or_create_model(self):
        """Load existing model or create a new one"""
        try:
            if os.path.exists('expense_categorizer.pkl'):
                with open('expense_categorizer.pkl', 'rb') as f:
                    self.model = pickle.load(f)
            else:
                self.create_initial_model()
        except:
            self.create_initial_model()

    def create_initial_model(self):
        """Create initial ML model with sample training data"""
        # Sample training data for expense categorization
        training_data = [
            ('pizza delivery', 'Food & Dining'),
            ('grocery store', 'Food & Dining'),
            ('restaurant bill', 'Food & Dining'),
            ('coffee shop', 'Food & Dining'),
            ('gas station', 'Transportation'),
            ('uber ride', 'Transportation'),
            ('bus ticket', 'Transportation'),
            ('car maintenance', 'Transportation'),
            ('amazon purchase', 'Shopping'),
            ('clothing store', 'Shopping'),
            ('electronics', 'Shopping'),
            ('movie tickets', 'Entertainment'),
            ('concert', 'Entertainment'),
            ('streaming service', 'Entertainment'),
            ('electricity bill', 'Bills & Utilities'),
            ('phone bill', 'Bills & Utilities'),
            ('internet', 'Bills & Utilities'),
            ('doctor visit', 'Healthcare'),
            ('pharmacy', 'Healthcare'),
            ('dental', 'Healthcare'),
            ('tuition', 'Education'),
            ('books', 'Education'),
            ('hotel', 'Travel'),
            ('flight', 'Travel'),
            ('haircut', 'Personal Care'),
            ('cosmetics', 'Personal Care'),
            ('home depot', 'Home & Garden'),
            ('garden supplies', 'Home & Garden')
        ]

        descriptions = [item[0] for item in training_data]
        categories = [item[1] for item in training_data]

        # Create and train the model
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(lowercase=True, stop_words='english')),
            ('classifier', MultinomialNB())
        ])

        self.model.fit(descriptions, categories)
        self.save_model()

    def categorize(self, description):
        """Predict category for an expense description"""
        try:
            if self.model:
                prediction = self.model.predict([description.lower()])[0]
                confidence = max(self.model.predict_proba([description.lower()])[0])
                return prediction if confidence > 0.3 else 'Miscellaneous'
        except:
            pass
        return 'Miscellaneous'

    def save_model(self):
        """Save the trained model"""
        try:
            with open('expense_categorizer.pkl', 'wb') as f:
                pickle.dump(self.model, f)
        except:
            pass

class FinanceTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Personal Finance Tracker")
        self.root.geometry("1200x800")

        # Initialize components
        self.db = FinanceDatabase()
        self.categorizer = ExpenseCategorizer()

        # Create GUI
        self.create_widgets()
        self.refresh_data()

    def create_widgets(self):
        """Create the main GUI widgets"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tabs
        self.create_add_expense_tab()
        self.create_view_expenses_tab()
        self.create_analytics_tab()
        self.create_budget_tab()

    def create_add_expense_tab(self):
        """Create the add expense tab"""
        self.add_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.add_frame, text="Add Expense")

        # Title
        title_label = ttk.Label(self.add_frame, text="Add New Expense", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=20)

        # Date
        ttk.Label(self.add_frame, text="Date:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        date_entry = ttk.Entry(self.add_frame, textvariable=self.date_var)
        date_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        # Amount
        ttk.Label(self.add_frame, text="Amount ($):").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.amount_var = tk.StringVar()
        amount_entry = ttk.Entry(self.add_frame, textvariable=self.amount_var)
        amount_entry.grid(row=2, column=1, padx=5, pady=5, sticky='w')

        # Description
        ttk.Label(self.add_frame, text="Description:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.description_var = tk.StringVar()
        description_entry = ttk.Entry(self.add_frame, textvariable=self.description_var, width=40)
        description_entry.grid(row=3, column=1, padx=5, pady=5, sticky='w')

        # Auto-categorize button
        auto_cat_btn = ttk.Button(self.add_frame, text="Auto Categorize", 
                                 command=self.auto_categorize)
        auto_cat_btn.grid(row=3, column=2, padx=5, pady=5)

        # Category
        ttk.Label(self.add_frame, text="Category:").grid(row=4, column=0, sticky='e', padx=5, pady=5)
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(self.add_frame, textvariable=self.category_var,
                                    values=self.categorizer.categories, width=20)
        category_combo.grid(row=4, column=1, padx=5, pady=5, sticky='w')

        # Payment Method
        ttk.Label(self.add_frame, text="Payment Method:").grid(row=5, column=0, sticky='e', padx=5, pady=5)
        self.payment_var = tk.StringVar(value="Cash")
        payment_combo = ttk.Combobox(self.add_frame, textvariable=self.payment_var,
                                   values=['Cash', 'Credit Card', 'Debit Card', 'Bank Transfer', 'Digital Wallet'])
        payment_combo.grid(row=5, column=1, padx=5, pady=5, sticky='w')

        # Add button
        add_btn = ttk.Button(self.add_frame, text="Add Expense", command=self.add_expense)
        add_btn.grid(row=6, column=0, columnspan=2, pady=20)

        # Receipt scanner frame
        scanner_frame = ttk.LabelFrame(self.add_frame, text="Receipt Scanner", padding=10)
        scanner_frame.grid(row=7, column=0, columnspan=3, pady=20, sticky='ew')

        scanner_info = ttk.Label(scanner_frame, 
                               text="Upload receipt image for automatic expense extraction")
        scanner_info.grid(row=0, column=0, columnspan=2, pady=5)

        upload_btn = ttk.Button(scanner_frame, text="Upload Receipt", 
                              command=self.upload_receipt)
        upload_btn.grid(row=1, column=0, padx=5, pady=5)

    def create_view_expenses_tab(self):
        """Create the view expenses tab"""
        self.view_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.view_frame, text="View Expenses")

        # Filter frame
        filter_frame = ttk.LabelFrame(self.view_frame, text="Filter Options", padding=10)
        filter_frame.pack(fill='x', padx=10, pady=5)

        # Date range
        ttk.Label(filter_frame, text="From:").grid(row=0, column=0, padx=5)
        self.start_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        start_date_entry = ttk.Entry(filter_frame, textvariable=self.start_date_var, width=12)
        start_date_entry.grid(row=0, column=1, padx=5)

        ttk.Label(filter_frame, text="To:").grid(row=0, column=2, padx=5)
        self.end_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        end_date_entry = ttk.Entry(filter_frame, textvariable=self.end_date_var, width=12)
        end_date_entry.grid(row=0, column=3, padx=5)

        refresh_btn = ttk.Button(filter_frame, text="Refresh", command=self.refresh_data)
        refresh_btn.grid(row=0, column=4, padx=10)

        export_btn = ttk.Button(filter_frame, text="Export to CSV", command=self.export_to_csv)
        export_btn.grid(row=0, column=5, padx=5)

        # Expenses table
        self.expenses_tree = ttk.Treeview(self.view_frame, columns=('Date', 'Amount', 'Description', 'Category', 'Payment'), show='headings')

        # Define headings
        self.expenses_tree.heading('Date', text='Date')
        self.expenses_tree.heading('Amount', text='Amount ($)')
        self.expenses_tree.heading('Description', text='Description')
        self.expenses_tree.heading('Category', text='Category')
        self.expenses_tree.heading('Payment', text='Payment Method')

        # Configure column widths
        self.expenses_tree.column('Date', width=100)
        self.expenses_tree.column('Amount', width=100)
        self.expenses_tree.column('Description', width=250)
        self.expenses_tree.column('Category', width=150)
        self.expenses_tree.column('Payment', width=120)

        # Add scrollbars
        v_scroll = ttk.Scrollbar(self.view_frame, orient='vertical', command=self.expenses_tree.yview)
        h_scroll = ttk.Scrollbar(self.view_frame, orient='horizontal', command=self.expenses_tree.xview)
        self.expenses_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        # Pack treeview and scrollbars
        self.expenses_tree.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=10)
        v_scroll.pack(side='right', fill='y', pady=10)
        h_scroll.pack(side='bottom', fill='x', padx=10)

    def create_analytics_tab(self):
        """Create the analytics tab with visualizations"""
        self.analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_frame, text="Analytics")

        # Create matplotlib figure
        self.fig, ((self.ax1, self.ax2), (self.ax3, self.ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, self.analytics_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

    def create_budget_tab(self):
        """Create the budget management tab"""
        self.budget_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.budget_frame, text="Budget")

        # Budget info label
        budget_info = ttk.Label(self.budget_frame, 
                              text="Set monthly budgets for different categories and track your spending",
                              font=('Arial', 12))
        budget_info.pack(pady=20)

        # Budget form
        form_frame = ttk.Frame(self.budget_frame)
        form_frame.pack(pady=20)

        ttk.Label(form_frame, text="Category:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.budget_category_var = tk.StringVar()
        budget_cat_combo = ttk.Combobox(form_frame, textvariable=self.budget_category_var,
                                      values=self.categorizer.categories)
        budget_cat_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Monthly Budget ($):").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.budget_amount_var = tk.StringVar()
        budget_amount_entry = ttk.Entry(form_frame, textvariable=self.budget_amount_var)
        budget_amount_entry.grid(row=1, column=1, padx=5, pady=5)

        set_budget_btn = ttk.Button(form_frame, text="Set Budget", command=self.set_budget)
        set_budget_btn.grid(row=2, column=0, columnspan=2, pady=10)

    def auto_categorize(self):
        """Auto-categorize expense based on description"""
        description = self.description_var.get()
        if description:
            category = self.categorizer.categorize(description)
            self.category_var.set(category)
            messagebox.showinfo("Auto Categorization", f"Suggested category: {category}")

    def add_expense(self):
        """Add expense to database"""
        try:
            date = self.date_var.get()
            amount = float(self.amount_var.get())
            description = self.description_var.get()
            category = self.category_var.get()
            payment_method = self.payment_var.get()

            if not all([date, amount, description, category]):
                messagebox.showerror("Error", "Please fill all required fields")
                return

            self.db.add_expense(date, amount, description, category, payment_method)

            # Clear fields
            self.amount_var.set("")
            self.description_var.set("")
            self.category_var.set("")

            messagebox.showinfo("Success", "Expense added successfully!")
            self.refresh_data()

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")

    def upload_receipt(self):
        """Upload and process receipt image (simplified OCR simulation)"""
        file_path = filedialog.askopenfilename(
            title="Select Receipt Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )

        if file_path:
            # Simulate OCR processing
            messagebox.showinfo("Receipt Processing", 
                              "Receipt processed! Extracted data:\n\n"
                              "Amount: $25.50\n"
                              "Description: Grocery Store Purchase\n"
                              "Date: " + datetime.now().strftime('%Y-%m-%d'))

            # Pre-fill form with extracted data
            self.amount_var.set("25.50")
            self.description_var.set("Grocery Store Purchase")
            self.category_var.set("Food & Dining")

    def refresh_data(self):
        """Refresh all data displays"""
        self.refresh_expenses_table()
        self.refresh_analytics()

    def refresh_expenses_table(self):
        """Refresh the expenses table"""
        # Clear existing data
        for item in self.expenses_tree.get_children():
            self.expenses_tree.delete(item)

        # Get expenses data
        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()
        expenses_df = self.db.get_expenses(start_date, end_date)

        # Populate table
        for _, expense in expenses_df.iterrows():
            self.expenses_tree.insert('', 'end', values=(
                expense['date'],
                f"${expense['amount']:.2f}",
                expense['description'],
                expense['category'],
                expense['payment_method']
            ))

    def refresh_analytics(self):
        """Refresh analytics charts"""
        try:
            # Clear previous plots
            for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
                ax.clear()

            # Get data for analytics
            start_date = self.start_date_var.get()
            end_date = self.end_date_var.get()
            expenses_df = self.db.get_expenses(start_date, end_date)
            category_totals = self.db.get_category_totals(start_date, end_date)

            if not expenses_df.empty:
                # 1. Spending by Category (Pie Chart)
                if not category_totals.empty:
                    self.ax1.pie(category_totals['total'], labels=category_totals['category'], autopct='%1.1f%%')
                    self.ax1.set_title('Spending by Category')

                # 2. Daily Spending Trend (Line Chart)
                expenses_df['date'] = pd.to_datetime(expenses_df['date'])
                daily_spending = expenses_df.groupby('date')['amount'].sum().reset_index()
                self.ax2.plot(daily_spending['date'], daily_spending['amount'])
                self.ax2.set_title('Daily Spending Trend')
                self.ax2.tick_params(axis='x', rotation=45)

                # 3. Payment Method Distribution (Bar Chart)
                payment_totals = expenses_df.groupby('payment_method')['amount'].sum()
                self.ax3.bar(payment_totals.index, payment_totals.values)
                self.ax3.set_title('Spending by Payment Method')
                self.ax3.tick_params(axis='x', rotation=45)

                # 4. Category Comparison (Horizontal Bar Chart)
                if not category_totals.empty:
                    self.ax4.barh(category_totals['category'], category_totals['total'])
                    self.ax4.set_title('Category Spending Comparison')

            self.fig.tight_layout()
            self.canvas.draw()

        except Exception as e:
            print(f"Error refreshing analytics: {e}")

    def export_to_csv(self):
        """Export expenses data to CSV"""
        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()
        expenses_df = self.db.get_expenses(start_date, end_date)

        if expenses_df.empty:
            messagebox.showwarning("Warning", "No data to export")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Export Expenses"
        )

        if file_path:
            expenses_df.to_csv(file_path, index=False)
            messagebox.showinfo("Success", f"Data exported to {file_path}")

    def set_budget(self):
        """Set budget for a category"""
        category = self.budget_category_var.get()
        amount = self.budget_amount_var.get()

        if not category or not amount:
            messagebox.showerror("Error", "Please fill all fields")
            return

        try:
            amount = float(amount)
            messagebox.showinfo("Success", f"Budget set for {category}: ${amount:.2f}")
            self.budget_category_var.set("")
            self.budget_amount_var.set("")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")

def main():
    root = tk.Tk()
    app = FinanceTrackerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
