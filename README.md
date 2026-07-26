#  💰​📈​ Personal Finance Intelligence Dashboard - Backend ​

A personal Finance Management Application, built to assist users in tracking their income and expenses while encouraging financial discipline through a minimal, intuitive interface. 

## 🎯 Objective
- The application allows users to manually input transactions, categorize expenses, and visualize data using simple graphs. 
- By focusing on core functionalities such as expense tracking, category filtering, and persistent storage, the project targets users who are new to budgeting tools or find existing systems overly complex.

## 🛠✨ Features Implemented
#### 🔐 Auth:
- Sign-Up/User Registration.
- Login.
- Token Renewal.
- Logout.

#### 🏦 Balance
- Create one Balance for each User.
- Update/Delete Balance details.

#### 💵 Transactions
- Create/Update/Delete Transactions 
(Providing additional details such as Expense/Income, Category, Cash/UPI/Other Payments, Notes for adding descriptive texts, etc.)
- Every time a transaction is created/updated/deleted, the balance amount is updated accordingly.

#### 🔧 Additional Features
- ##### Categories: 
  Add categories to each transaction, such as <i>Groceries</i>, or <i>Bills</i>, and add different <i>Colors to each category.</i>
- ##### Payment Options:
  Add payment option to each transaction, such as adding different UPI Apps' name under <i> UPI Payments</i> option, or adding different card details under <i>Debit Card</i> option.
  <u>Example:</u> 
  1. name: "PhonePe", type: "UPI", ...
  2. name: "GooglePay", type: "UPI", ...
  3. name: "Pay on Delivery", type: "Cash", ...
  4. name: "Paid by sister", type: "Cash", ...


## 🛠 Tech Stack
- FastAPI + SQLAlchemy
- JWT + RBAC (Auth)
- PostgresSQL (Database)
- Alembic (Migration Tool)

## 🚧​ Under Construction
The project is still in the development phase, however, major features have been implemented.