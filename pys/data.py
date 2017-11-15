# -*- coding: utf-8 -*-
import pandas as pd


INPUT_PATH = '../input/'
OUTPUT_PATH = '../output/'


def load_data():

    users = pd.read_csv(INPUT_PATH + 't_user.csv')
    orders = pd.read_csv(INPUT_PATH + 't_order.csv')
    loans = pd.read_csv(INPUT_PATH + 't_loan.csv')
    loans_sum = pd.read_csv(INPUT_PATH + 't_loan_sum.csv')
    clicks = pd.read_csv(INPUT_PATH + 't_click.csv')

    # origin price
    loans.loan_amount = 5**loans.loan_amount
    loans_sum.loan_sum = 5 ** loans_sum.loan_sum
    orders.price = 5 ** orders.price
    orders.discount = 5 ** orders.discount
    users.limit = 5 ** users.limit

    # loans
    loans['Date'] = pd.to_datetime(loans['loan_time'], errors='coerce')
    loans['transaction_month'] = loans['Date'].dt.month
    # fill nan with 0
    loans["loan_count"] = 1
    loans.loan_amount = loans.loan_amount.fillna(0)
    loans_new = loans.groupby(by=["uid", "transaction_month"], as_index=False)["loan_amount", "loan_count"].sum()
    loans_new = loans_new.pivot_table(['loan_amount', "loan_count"], ['uid'], 'transaction_month', fill_value=0)
    loans_new.reset_index(drop=False, inplace=True)
    loans_new.columns = ['{}_{}'.format(i[1], i[0]) for i in loans_new.columns]
    loans_new = loans_new.rename(index=str, columns={"_uid": "uid"})

    # orders
    orders['Date'] = pd.to_datetime(orders['buy_time'], errors='coerce')
    orders['transaction_month'] = orders['Date'].dt.month
    orders["comsume_count"] = 1
    orders["consume_amount"] = orders["price"] * orders["qty"] - orders["discount"]
    orders.consume_amount = orders.consume_amount.fillna(0)
    orders_new = orders.groupby(by=["uid","transaction_month"], as_index=False)["consume_amount", "comsume_count"].sum()
    orders_new = orders_new.pivot_table(['consume_amount', "comsume_count"], ['uid'], 'transaction_month', fill_value=0)
    orders_new.reset_index(drop=False, inplace=True)
    orders_new.columns = ['{}_{}'.format(i[1], i[0]) for i in orders_new.columns]
    orders_new = orders_new.rename(index=str, columns={"_uid": "uid"})

    # clicks
    clicks['Date'] = pd.to_datetime(clicks['click_time'], errors='coerce')
    clicks['transaction_month'] = clicks['Date'].dt.month
    clicks["click_count"] = 1
    clicks_new = clicks.groupby(by=["uid", "transaction_month"], as_index=False)["click_count"].sum()
    clicks_new = clicks_new.pivot_table('click_count', ['uid'], 'transaction_month', fill_value=0)
    clicks_new.reset_index(drop=False, inplace=True)
    clicks_new = clicks_new.rename(index=str, columns={8: "8_click_count", 9: "9_click_count", 10 : "10_click_count", 11 : "11_click_count"})

    return users, orders_new, loans_new, loans_sum, clicks_new

if __name__ == "__main__":
    print('begin to load data')
    users, orders, loans, loan_sum, clicks = load_data()
    print(' load data finished')
    users_orders = users.merge(orders ,how='left', on="uid")
    users_orders_loans = users_orders.merge(loans ,how='left', on="uid")
    user_info = users_orders_loans.merge(clicks ,how='left', on="uid")
    print('to csv ........')
    user_info.to_csv(OUTPUT_PATH +"user_info.csv", index=False)