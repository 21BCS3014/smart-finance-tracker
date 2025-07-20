# Smart Personal Finance Tracker

An intelligent expense tracking application built with Python featuring machine learning-powered expense categorization, data visualization dashboard, OCR receipt scanning, and comprehensive financial analytics.

![Finance Tracker](https://img.shields.io/badge/Status-Complete-brightgreen)
![Python Version](https://img.shields.io/badge/Python-3.8+-blue)
![ML Powered](https://img.shields.io/badge/ML-Powered-orange)

## 💰 Key Features

### Intelligent Expense Management
- **ML-Powered Categorization** - Automatically categorize expenses using trained Naive Bayes classifier
- **Receipt OCR Scanning** - Extract expense data from receipt images (Tesseract OCR integration)
- **Multiple Payment Methods** - Track Cash, Credit Card, Debit Card, Bank Transfer, Digital Wallet
- **Smart Data Entry** - Auto-complete and suggestion features

### Advanced Analytics Dashboard
- **Category Distribution** - Pie charts showing spending breakdown by category
- **Trend Analysis** - Line charts tracking daily/monthly spending patterns  
- **Payment Method Analysis** - Bar charts comparing spending across payment types
- **Budget vs Actual** - Visual comparison of budgeted vs actual spending

### Data Management
- **SQLite Database** - Robust local data storage with relational design
- **CSV Export/Import** - Easy data portability and backup options
- **Date Range Filtering** - Flexible time-period analysis
- **Search & Sort** - Quick expense lookup and organization

## 🚀 Installation and Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/simran-dev/smart-finance-tracker.git
cd smart-finance-tracker
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python smart_finance_tracker.py
```

## 📊 Application Interface

### Tab 1: Add Expenses
- **Manual Entry**: Date, amount, description, category, payment method
- **Auto-Categorization**: ML-powered category suggestion based on description
- **Receipt Scanner**: Upload image files for automatic data extraction
- **Smart Validation**: Input validation and error handling

### Tab 2: View Expenses
- **Expense Table**: Sortable table with all expense records
- **Date Filtering**: Custom date range selection
- **Export Options**: CSV export for external analysis
- **Search Functionality**: Quick expense lookup

### Tab 3: Analytics Dashboard
- **Visual Charts**: 4-panel dashboard with multiple chart types
- **Category Analysis**: Spending distribution pie chart
- **Trend Analysis**: Time-series spending patterns
- **Payment Analysis**: Payment method comparison
- **Comparative Views**: Category spending comparison

### Tab 4: Budget Management
- **Budget Setting**: Monthly budget allocation by category
- **Budget Tracking**: Real-time budget vs actual comparison
- **Alert System**: Overspending notifications
- **Goal Setting**: Financial target management

## 🤖 Machine Learning Features

### Expense Categorization Model
```python
# Built-in categories
categories = [
    'Food & Dining', 'Transportation', 'Shopping', 
    'Entertainment', 'Bills & Utilities', 'Healthcare',
    'Education', 'Travel', 'Personal Care', 
    'Home & Garden', 'Miscellaneous'
]
```

### Training Data Examples
- **Food & Dining**: "pizza delivery", "grocery store", "restaurant bill"
- **Transportation**: "gas station", "uber ride", "bus ticket"
- **Shopping**: "amazon purchase", "clothing store", "electronics"
- **Entertainment**: "movie tickets", "concert", "streaming service"

### Model Performance
- **Algorithm**: Multinomial Naive Bayes with TF-IDF vectorization
- **Accuracy**: 85%+ on training data
- **Confidence Threshold**: 30% minimum for auto-categorization
- **Fallback**: "Miscellaneous" category for low-confidence predictions

## 💾 Database Schema

### Expenses Table
```sql
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    payment_method TEXT DEFAULT 'Cash',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Budgets Table
```sql
CREATE TABLE budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT UNIQUE NOT NULL,
    budget_amount REAL NOT NULL,
    month_year TEXT NOT NULL
);
```

### Income Table
```sql
CREATE TABLE income (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    amount REAL NOT NULL,
    source TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 📁 Project Structure

```
smart-finance-tracker/
├── smart_finance_tracker.py    # Main application file
├── requirements.txt           # Python dependencies
├── README.md                 # Project documentation
├── finance_tracker.db        # SQLite database (created on first run)
├── expense_categorizer.pkl   # Trained ML model (created on first run)
├── screenshots/             # Application screenshots
└── sample_data/            # Sample CSV files for testing
    ├── sample_expenses.csv
    └── sample_receipts/
```

## 🔧 Advanced Features

### OCR Receipt Processing
```python
def process_receipt(image_path):
    # Tesseract OCR integration
    extracted_text = pytesseract.image_to_string(Image.open(image_path))

    # Pattern matching for amount, date, merchant
    amount = re.search(r'\$?([0-9]+\.?[0-9]*)', extracted_text)
    date = re.search(r'([0-9]{1,2}/[0-9]{1,2}/[0-9]{4})', extracted_text)

    return {
        'amount': amount.group(1) if amount else '0.00',
        'date': date.group(1) if date else datetime.now().strftime('%Y-%m-%d'),
        'description': 'Receipt Upload'
    }
```

### Data Export/Import
```python
# Export to CSV
def export_expenses():
    df = get_expenses_dataframe()
    df.to_csv('expenses_export.csv', index=False)

# Import from CSV
def import_expenses(csv_file):
    df = pd.read_csv(csv_file)
    for _, row in df.iterrows():
        add_expense(row['date'], row['amount'], row['description'], row['category'])
```

## 📈 Analytics Implementation

### Visualization Engine
- **Matplotlib Integration**: High-quality charts and graphs
- **Real-time Updates**: Dynamic chart refresh on data changes
- **Multiple Chart Types**: Pie, bar, line, scatter plots
- **Interactive Features**: Zoom, pan, and hover tooltips

### Statistical Analysis
- **Spending Trends**: Moving averages and trend detection
- **Category Analysis**: Percentage distribution and growth rates
- **Budget Performance**: Variance analysis and forecasting
- **Seasonal Patterns**: Monthly and yearly spending patterns

## 🎯 Use Cases

### Personal Finance Management
- **Daily Expense Tracking**: Quick and easy expense entry
- **Budget Planning**: Monthly budget allocation and monitoring
- **Spending Analysis**: Identify spending patterns and trends
- **Financial Goals**: Track progress toward savings targets

### Business Applications
- **Small Business Accounting**: Track business expenses and receipts
- **Freelancer Finances**: Monitor income and business expenses
- **Project Budgeting**: Track expenses for specific projects
- **Tax Preparation**: Organize expenses by tax-deductible categories

## 🔐 Data Security

### Local Storage
- **SQLite Database**: All data stored locally on user's machine
- **No Cloud Dependency**: Complete privacy and security
- **Backup Options**: Easy database file backup and restore
- **Encryption Ready**: Database encryption can be easily added

### Privacy Features
- **No Data Transmission**: No data sent to external servers
- **Offline Functionality**: Fully functional without internet connection
- **User Control**: Complete control over personal financial data

## 🛠️ Customization Options

### Adding New Categories
```python
# Modify categories in ExpenseCategorizer class
self.categories = [
    'Food & Dining', 'Transportation', 'Shopping',
    'Your Custom Category'  # Add new category here
]
```

### Custom ML Training
```python
# Add training data for better categorization
training_data.extend([
    ('your expense description', 'Your Custom Category'),
    ('another description', 'Your Custom Category')
])
```

### UI Customization
```python
# Modify themes and colors in the GUI class
root.configure(bg='your_color')
style = ttk.Style()
style.theme_use('clam')  # Change theme
```

## 📋 System Requirements

### Minimum Requirements
- **OS**: Windows 10, macOS 10.14, Ubuntu 18.04+
- **Python**: 3.8+
- **RAM**: 4GB
- **Storage**: 100MB

### Recommended Requirements
- **OS**: Windows 11, macOS 12+, Ubuntu 20.04+
- **Python**: 3.10+
- **RAM**: 8GB
- **Storage**: 500MB

## 🚀 Future Enhancements

### Planned Features
- [ ] **Mobile App Version** using Kivy or React Native
- [ ] **Cloud Sync** with encrypted cloud storage
- [ ] **Multi-Currency Support** with real-time exchange rates
- [ ] **Advanced OCR** with better accuracy and multiple languages
- [ ] **Investment Tracking** for stocks, bonds, and crypto
- [ ] **Bill Reminders** with notification system

### Technical Improvements
- [ ] **Advanced ML Models** using deep learning for better categorization
- [ ] **Real-time Dashboard** with live updates and notifications
- [ ] **API Integration** with bank accounts for automatic transaction import
- [ ] **Reporting Engine** with customizable report generation
- [ ] **Multi-user Support** with user authentication and profiles

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Developer

**Simran**
- Email: ss6773568@gmail.com
- GitHub:https://github.com/21BCS3014/smart-finance-tracker
- LinkedIn:www.linkedin.com/in/simran-3a4786230 
## 🙏 Acknowledgments

- **scikit-learn Team** for excellent machine learning library
- **Matplotlib Community** for powerful visualization tools
- **Pandas Development Team** for data manipulation capabilities
- **Tesseract OCR** for optical character recognition
- **Tkinter Community** for GUI framework support

---

⭐ **Star this repository if it helped you manage your finances better!** ⭐
