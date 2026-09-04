from src.assistance.llm.groq import create_groq_llm_instance

summary_llm = create_groq_llm_instance(temperature=0.2)


# -- Create the transactions table
# CREATE TABLE transactions (
#     id INT PRIMARY KEY,
#     type VARCHAR(10) CHECK (type IN ('income', 'expense')),
#     date DATE NOT NULL,
# 	category_id INT,
#     amount DECIMAL(10, 2) NOT NULL
# );

# -- Insert 10 rows with income and expense types
# INSERT INTO transactions (id, type, date, category_id, amount) VALUES
# (1, 'income', '2026-08-01', 2, 3500.00),
# (2, 'expense', '2026-08-02', 2, 45.50),
# (3, 'expense', '2026-08-05', 3, 120.00),
# (4, 'income', '2026-08-10', 3, 250.00),
# (5, 'expense', '2026-08-12', 3, 15.20),
# (6, 'expense', '2026-08-15', 1, 850.00),
# (7, 'income', '2026-08-18', 4, 1200.00),
# (8, 'expense', '2026-08-20', 5, 65.00),
# (9, 'expense', '2026-08-25', 6, 200.00),
# (10, 'income', '2026-08-30', 1, 500.00);

# -- SELECT * FROM TRANSACTIONS
# ---------------------------------------------------------------------
# id	    type	    date	        category_id	      amount
# ---------------------------------------------------------------------
# 1	      income	  2026-08-01	      2             3500
# 2	      expense	  2026-08-02	      2	            45.5
# 3	      expense	  2026-08-05	      3	            120
# 4	      income	  2026-08-10	      3	            250
# 5	      expense	  2026-08-12	      3	            15.2
# 6	      expense	  2026-08-15	      1	            850
# 7	      income	  2026-08-18	      4	            1200
# 8	      expense	  2026-08-20	      5	              65
# 9	      expense	  2026-08-25	      6	             200
# 10	    income  	2026-08-30	      1	            500


# select count(category_id), category_id from transactions group by category_id

# ---------------------------------------------------------------------
# count(amount)	  category_id
# ---------------------------------------------------------------------
# 2                	1
# 2                	2
# 3	                3
# 1               	4
# 1	                5
# 1	                6


# select type, category_id, count(category_id), amount, sum(amount)
# from transactions
# where type = 'expense' group by category_id

# ---------------------------------------------------------------------
# type	  category_id	  count(category_id)	  amount	  sum(amount)
# ---------------------------------------------------------------------
# expense	    1	              1	                850	         850
# expense	    2             	1	                45.5	      45.5
# expense	    3	              2	                120	        135.2
# expense	    5	              1	                 65	          65
# expense	    6	              1	                200	          200


# -- Top 5 Largest Transactions
# select category_id, type, amount as top_five_transactions
#  from transactions group by category_id
# order by top_five_transactions DESC Limit 5;
# ---------------------------------------------------------------------
# category_id   	type    	top_five_transactions
# ---------------------------------------------------------------------
#   2	           income	            3500
#   4	           income            	1200
#   1	           expense           	850
#   6	           expense           	200
#   3	           expense           	120


# WITH signed_transactions AS (
#     SELECT
#         date,
#         CASE
#             WHEN type = 'income' THEN amount
#             WHEN type = 'expense' THEN -amount
#             ELSE 0
#         END AS net_amount
#     FROM
#         transactions
# )
# SELECT
#     date,
#     net_amount,
#     SUM(net_amount) OVER (ORDER BY date) AS running_net_balance
# FROM
#     signed_transactions;
