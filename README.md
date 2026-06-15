## DB Design
> ##### Database Design for Personal Finance Intelligence Dashboard

##### users
- <u>id</u>
- name
- email
- phone_number
- username
- password
- created_at
- updated_at
- <i>role_id</i>

##### roles
- <u>id</u>
- name (name to be updated from role_name to name in DB)
- created_at
- updated_at

##### categories
- <u>id</u>
- name
- color
- created_at
- updated_at (not added to DB yet)
- <i>user_id</i>

##### payment_options
- <u>id</u>
- name
- payment_type (cash / credit card / debit card / mobile banking app / other)
- created_at
- updated_at
- <i>user_id</i>

##### transactions
- <u>id</u>
- title
- transaction_type (income/expense)
- amount
- note (optional)
- created_at
- updated_at
- <i>payment_option_id</i>
- <i>category_id</i>
- <i>user_id</i>

##### balance
- <u>id</u>
- amount
- created_at
- updated_at
- <i>user_id</i>

##### goals
- <u>id</u>
- name
- target_amount
- <i>category_id</i>
- <i>user_id</i>
- <small>** <b>target_achieved</b></small>
- <small>** <b>effect</b> [ Positive / Negative ] </small>


> ###### ** <small>Not to store in DB, fetch data by querying and calculating from transactions table.</small>