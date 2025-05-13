# -*- coding: utf-8 -*-
"""
EAS503 Mini-projects 2/3

Code developed in Spyder (not Jupyter notebook).

"""
#%% 
import numpy as np
import pandas as pd
import sqlite3
from sqlite3 import Error
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
#%% Create helper functions (credit to course notes)
def create_connection(db_file, delete_db=False):
    import os
    if delete_db and os.path.exists(db_file):
        os.remove(db_file)
        
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        conn.execute("PRAGMA foreign_keys = 1")
    except Error as e:
        print(e)
    
    return conn

def create_table(conn, create_table_sql, drop_table_name=None):

    if drop_table_name: 
        try:
            c = conn.cursor()
            c.execute("""DROP TABLE IF EXISTS %s""" % (drop_table_name))
        except Error as e:
            print(e)

    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)
#%% load data
data_fp = "Coffee Shop Sales.csv"
dataset = pd.read_csv(data_fp)
dataset.info()

#%% Data exploration/pre-processing
print(len(dataset.groupby(list(dataset.columns))) == dataset.shape[0])

for column in dataset.columns:
    print(dataset[column].unique())
    
dataset['product_detail'].replace('Jamacian Coffee River', 'Jamaican Coffee River', inplace=True)
#%%


#%% FIX THIS show some kind of python pre-processing for finding out that price is not inherent to product but transaction?
len(dataset['unit_price'].unique()) == len(dataset['product_id'].unique()) # price is not a property of product.
len(dataset['unit_price'].unique()) == len(dataset['transaction_id'].unique())
#%% save processed file
dataset.to_csv("coffee_shop_sales.csv", index = False)
data_fp = "coffee_shop_sales.csv"
#%% Normalization: Create stores table
def create_store_table(data_fp, normalized_database_filename):
    stores = []
    with open(data_fp) as file:
        header = None
        for line in file:
            if not line.strip():
                continue
            if not header:
                header = line.strip().split(',')
                continue
            
            data = line.strip().split(',')
            store = (data[4], data[5])
            
            if store not in stores:
                stores.append(store)
            
    create_store_table_sql = """
    CREATE TABLE [Store] (
    [StoreID] Integer not null primary key,
    [StoreLoc] Text not null);
    """
    
    def insert_store(conn, values):
        sql = "INSERT INTO Store (StoreID, StoreLoc) VALUES (?, ?)"
        cur = conn.cursor()
        cur.executemany(sql, values)
        return cur.lastrowid
    
    conn = create_connection(normalized_database_filename, True)
    
    with conn:
        create_table(conn, create_store_table_sql, 'Store')
        insert_store(conn, stores)
    conn.close()

create_store_table(data_fp, "coffee_sales.db")
#%% Normalization: Create product category table
def create_prod_cat_table(data_fp, normalized_database_filename):
    prod_cats = []
    with open(data_fp) as file:
        header = None
        for line in file:
            if not line.strip():
                continue
            if not header:
                header = line.strip().split(',')
                continue
            
            data = line.strip().split(',')
            prod_cat = (data[8],)
            
            if prod_cat not in prod_cats:
                prod_cats.append(prod_cat)
            
    create_prod_cat_table_sql = """
    CREATE TABLE [ProdCategory] (
    [ProdCategoryID] Integer not null primary key,
    [ProdCategory] Text not null);
    """
    
    def insert_prod_cat(conn, values):
        sql = "INSERT INTO ProdCategory (ProdCategory) VALUES (?)"
        cur = conn.cursor()
        cur.executemany(sql, values)
        return cur.lastrowid
    
    conn = create_connection(normalized_database_filename)
    
    with conn:
        create_table(conn, create_prod_cat_table_sql, 'ProdCategory')
        insert_prod_cat(conn, prod_cats)
    conn.close()

create_prod_cat_table(data_fp, 'coffee_sales.db')
#%% Normalization: Map product category to product category id
def create_prodcat_to_prodcatid_dict(normalized_database_filename):
    conn = create_connection(normalized_database_filename)
    df = pd.read_sql_query('select * from ProdCategory', conn)
    
    prodcat_to_prodcatid_dict = {}
    for rowid, value in df.iterrows():
        prodcatid, prodcat = value
        prodcat_to_prodcatid_dict[prodcat] = prodcatid
    conn.close()
    return prodcat_to_prodcatid_dict
#%% Normalization: Create product type table
def create_prod_type_table(data_fp, normalized_database_filename):
    prodcat_to_prodcatid_dict = create_prodcat_to_prodcatid_dict(normalized_database_filename)
    prod_types = []
    with open(data_fp) as file:
        header = None
        for line in file:
            if not line.strip():
                continue
            if not header:
                header = line.strip().split(',')
                continue
            
            data = line.strip().split(',')
            prod_type = (data[9], prodcat_to_prodcatid_dict[data[8]])
            
            if prod_type not in prod_types:
                prod_types.append(prod_type)
            
    create_prod_type_table_sql = """CREATE TABLE [ProdType] (
    [ProdTypeID] INTEGER NOT NULL PRIMARY KEY,
    [ProdType] TEXT NOT NULL,
    [ProdCategoryID] INTEGER NOT NULL,
    FOREIGN KEY (ProdCategoryID) REFERENCES ProdCategory (ProdCategoryID)
    );"""
    
    def insert_prod_type(conn, values):
        sql = "INSERT INTO ProdType (ProdType, ProdCategoryID) VALUES (?, ?)"
        cur = conn.cursor()
        cur.executemany(sql, values)
        return cur.lastrowid
    
    conn = create_connection(normalized_database_filename)
    with conn:
        create_table(conn, create_prod_type_table_sql, 'ProdType')
        insert_prod_type(conn, prod_types)
    conn.close()

create_prod_type_table(data_fp, 'coffee_sales.db')
#%% Normalization: Map product type to product type id
def create_prodtype_to_prodtypeid_dict(normalized_database_filename):
    conn = create_connection(normalized_database_filename)
    df = pd.read_sql_query('select * from ProdType', conn)
    
    prodtype_to_prodtypeid_dict = {}
    for rowid, value in df.iterrows():
        prodtypeid, prodtype, prodcatid = value
        prodtype_to_prodtypeid_dict[prodtype] = prodtypeid
    conn.close()
    return prodtype_to_prodtypeid_dict

#%% Normalization: Create product detail table
def create_proddetail_table(data_fp, normalized_database_filename):
    prodtype_to_prodtypeid_dict = create_prodtype_to_prodtypeid_dict(normalized_database_filename)
    products = []
    with open(data_fp) as file:
        header = None
        for line in file:
            if not line.strip():
                continue
            if not header:
                header = line.strip().split(',')
                continue
            
            data = line.strip().split(',')
            product = (data[6], prodtype_to_prodtypeid_dict[data[9]], data[10])
            
            if product not in products:
                products.append(product)

    create_proddetail_table_sql = """CREATE TABLE [ProdDetail] (
    [ProdID] INTEGER NOT NULL PRIMARY KEY,
    [ProdTypeID] INTEGER NOT NULL,
    [ProdDetail] TEXT NOT NULL,
    FOREIGN KEY (ProdTypeID) REFERENCES ProdType (ProdTypeID)
    );"""
    
    def insert_proddetail(conn, values):
        sql = "INSERT INTO ProdDetail (ProdID, ProdTypeID, ProdDetail) VALUES (?, ?, ?)"
        cur = conn.cursor()
        cur.executemany(sql, values)
        return cur.lastrowid
    
    conn = create_connection(normalized_database_filename)
    with conn:
        create_table(conn, create_proddetail_table_sql, "ProdDetail")
        insert_proddetail(conn, products)
    conn.close()

create_proddetail_table(data_fp, "coffee_sales.db")

#%% Normalization: Create transaction table 
def create_trans_table(data_fp, normalized_database_filename):
    transactions = []
    with open(data_fp) as file:
        header = None
        for line in file:
            if not line.strip():
                continue
            if not header:
                header = line.strip().split(',')
                continue
            
            data = line.strip().split(',')
            date = datetime.datetime.strptime(data[1], '%m/%d/%Y').strftime('%Y-%m-%d')
            time = datetime.datetime.strptime(data[2], '%H:%M:%S').strftime('%H:%M:%S')
            transaction = (data[0], date, time, data[3], data[4], data[6], data[7])
            
            if transaction not in transactions:
                transactions.append(transaction)
                
    create_trans_table_sql = """CREATE TABLE [Trans] (
    [TransID] INTEGER NOT NULL PRIMARY KEY,
    [Date] INTEGER NOT NULL,
    [Time] INTEGER NOT NULL,
    [Qty] INTEGER NOT NULL,
    [StoreID] INTEGER NOT NULL,
    [ProdID] INTEGER NOT NULL,
    [Price] REAL NOT NULL,
    FOREIGN KEY (StoreID) REFERENCES Store (StoreID), 
    FOREIGN KEY (ProdID) REFERENCES ProdDetail (ProdID)
    );
    """
    
    def insert_transaction(conn, values):
        sql = "INSERT INTO Trans (TransID, Date, Time, Qty, StoreID, ProdID, Price) VALUES (?, ?, ?, ?, ?, ?, ?)"
        cur = conn.cursor()
        cur.executemany(sql, values)
        return cur.lastrowid
    
    conn = create_connection(normalized_database_filename)
    with conn:
        create_table(conn, create_trans_table_sql, "Trans")
        insert_transaction(conn, transactions)
    conn.close()

create_trans_table(data_fp, "coffee_sales.db")

#%% Create dataframes from tables for set up replication of queries using pandas 
conn = sqlite3.connect("coffee_sales.db")
df_prod_category = pd.read_sql_query("SELECT * FROM ProdCategory", conn)
df_prod_detail = pd.read_sql_query("SELECT * FROM ProdDetail", conn)
df_prod_type = pd.read_sql_query("SELECT * FROM ProdType", conn)
df_store = pd.read_sql_query("SELECT * FROM Store", conn)
df_trans = pd.read_sql_query("SELECT * FROM Trans", conn)
conn.close()

df_trans["Sales"] = df_trans["Qty"]*df_trans["Price"]
df_trans["Date"] = pd.to_datetime(df_trans["Date"])
df_trans["Time"] = pd.to_datetime(df_trans["Time"], format = "%H:%M:%S")
      
#%% Question 1 SQL - compare store performance over time
sql_stmt1 = """
SELECT strftime("%m-%Y", t.Date) as "Month-Year", s.StoreLoc, sum(t.Qty*t.Price) as Sales
FROM
Trans t
JOIN
Store s ON t.StoreID = s.StoreID
GROUP BY  s.StoreLoc, strftime("%m-%Y", t.Date)
;"""
        
conn = sqlite3.connect("coffee_sales.db")
df1 = pd.read_sql_query(sql_stmt1, conn)
conn.close()        
print(df1)

#%% Q1 - pandas
q1 = pd.merge(df_trans, df_store, how="outer", on="StoreID")[["Date", "StoreLoc", "Sales"]]
g1 = q1.groupby(["StoreLoc", q1["Date"].dt.month]).agg({"Sales": "sum"})
print(g1)

#%% Q1 - visuals
sns.set_theme(style = "ticks")
sns.set_palette("muted")
plt.figure(figsize = (6, 4))
plt.plot(df1['Month-Year'].unique(), df1[df1["StoreLoc"] == "Astoria"]["Sales"], 
         "-o", alpha = 1, linewidth = 2, markersize = 8, label = "Astoria")
plt.plot(df1['Month-Year'].unique(), df1[df1["StoreLoc"] == "Lower Manhattan"]["Sales"], 
         "-^", alpha = 0.8, linewidth = 2, markersize = 8, label = "Lower Manhattan")
plt.plot(df1['Month-Year'].unique(), df1[df1["StoreLoc"] == "Hell's Kitchen"]["Sales"], 
         "-s", alpha = 0.6, linewidth = 2, markersize = 8, label = "Hell's Kitchen")
plt.xlabel("Month")
plt.ylabel("Sales ($)")
plt.ticklabel_format(axis ="y", style="scientific", scilimits=(3,3))
plt.legend()
plt.title("Monthly Sales by Location")
plt.show()

#%% Question 2 - category performance
sql_stmt2a = """
SELECT pc.ProdCategory, sum(t.Qty) as "Quantity Sold", sum(t.Qty*t.Price) as Sales
FROM
Trans t 
JOIN ProdDetail pd ON t.ProdID = pd.ProdID
JOIN ProdType pt ON pd.ProdTypeID = pt.ProdTypeID
JOIN ProdCategory pc ON pt.ProdCategoryID = pc.ProdCategoryID
GROUP BY pc.ProdCategory
ORDER BY "Sales" DESC
;"""        

sql_stmt2b = """
SELECT pd.ProdDetail
FROM ProdDetail pd
JOIN ProdType pt ON pd.ProdTypeID = pt.ProdTypeID
JOIN ProdCategory pc ON pt.ProdCategoryID = pc.ProdCategoryID
WHERE pc.ProdCategory == "Branded"
;"""

sql_stmt2c = """
SELECT pd.ProdDetail
FROM ProdDetail pd
JOIN ProdType pt ON pd.ProdTypeID = pt.ProdTypeID
JOIN ProdCategory pc ON pt.ProdCategoryID = pc.ProdCategoryID
WHERE pc.ProdCategory == "Tea"
;"""

conn = sqlite3.connect("coffee_sales.db")
df2a = pd.read_sql_query(sql_stmt2a, conn)
df2b = pd.read_sql_query(sql_stmt2b, conn)
df2c = pd.read_sql_query(sql_stmt2c, conn)
conn.close()
          
print(df2a, "\n \n", df2b, "\n \n", df2c)

#%% Q2 - pandas
j1 = pd.merge(df_trans, df_prod_detail, how = "left", on = "ProdID")
j2 = pd.merge(j1, df_prod_type, how = "left", on = "ProdTypeID")
j3 = pd.merge(j2, df_prod_category, how = "left", on = "ProdCategoryID")
q2a = j3[["ProdCategory", "Qty", "Sales"]].groupby(["ProdCategory"]).agg({"Qty": "sum", "Sales": "sum"})
g2a = q2a.sort_values("Sales", ascending = False)
print(g2a)

q2b = j3[j3["ProdCategory"] == "Branded"]["ProdDetail"].unique()
print("\n", q2b)

q2c = j3[j3["ProdCategory"] == "Tea"]["ProdDetail"].unique()
print("\n", q2c)

#%% Q2 visualization
explode = [0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05]
fig, ax = plt.subplots(figsize = (6,6))
pie_values = g2a["Sales"]
pie_labels = g2a.index.to_list()
ax.pie(pie_values, labels=pie_labels, labeldistance=1.1, textprops={'fontsize': 11}, radius=1, explode=explode)
plt.title("Total Sales by Category", x=0.625)
plt.show()

#%% Question 3 - Within the top selling categories, what are the best selling products? 
sql_stmt3a = """
SELECT pd.ProdDetail, sum(t.Qty) as "Quantity Sold", sum(t.Qty*t.Price) as Sales
FROM
Trans t 
JOIN ProdDetail pd ON t.ProdID = pd.ProdID
JOIN ProdType pt ON pd.ProdTypeID = pt.ProdTypeID
JOIN ProdCategory pc ON pt.ProdCategoryID = pc.ProdCategoryID
WHERE pc.ProdCategory == "Coffee"
GROUP BY pd.ProdDetail
ORDER BY "Quantity Sold" DESC
;"""        
                   

sql_stmt3b = """
SELECT pd.ProdDetail, sum(t.Qty) as "Quantity Sold", sum(t.Qty*t.Price) as Sales
FROM
Trans t 
JOIN ProdDetail pd ON t.ProdID = pd.ProdID
JOIN ProdType pt ON pd.ProdTypeID = pt.ProdTypeID
JOIN ProdCategory pc ON pt.ProdCategoryID = pc.ProdCategoryID
WHERE pc.ProdCategory == "Tea"
GROUP BY pd.ProdDetail
ORDER BY "Quantity Sold" DESC
;"""        
                    

sql_stmt3c = """
SELECT pd.ProdDetail, sum(t.Qty) as "Quantity Sold", sum(t.Qty*t.Price) as Sales
FROM
Trans t 
JOIN ProdDetail pd ON t.ProdID = pd.ProdID
JOIN ProdType pt ON pd.ProdTypeID = pt.ProdTypeID
JOIN ProdCategory pc ON pt.ProdCategoryID = pc.ProdCategoryID
WHERE pc.ProdCategory == "Bakery"
GROUP BY pd.ProdDetail
ORDER BY "Quantity Sold" DESC
;"""        
        
conn = sqlite3.connect("coffee_sales.db")
df3a = pd.read_sql_query(sql_stmt3a, conn)
df3b = pd.read_sql_query(sql_stmt3b, conn)
df3c = pd.read_sql_query(sql_stmt3c, conn)
conn.close()           

print(df3a, "\n \n", df3b, "\n \n", df3c)     
  
#%% Q3 - pandas
q3a = j3[j3["ProdCategory"]=="Coffee"]
g3a = q3a[["ProdDetail", "Qty", "Sales"]].groupby(["ProdDetail"]).agg({"Qty": "sum", "Sales": "sum"})
g3a = g3a.sort_values("Qty", ascending = False)
print(g3a)

q3b = j3[j3["ProdCategory"]=="Tea"]
g3b = q3b[["ProdDetail", "Qty", "Sales"]].groupby(["ProdDetail"]).agg({"Qty": "sum", "Sales": "sum"})
g3b = g3b.sort_values("Qty", ascending = False)
print("\n", g3b)

q3c = j3[j3["ProdCategory"]=="Bakery"]
g3c = q3c[["ProdDetail", "Qty", "Sales"]].groupby(["ProdDetail"]).agg({"Qty": "sum", "Sales": "sum"})
g3c = g3c.sort_values("Qty", ascending = False)
print("\n", g3c)

#%% Q3 visualization - top 5 products set of 3 bar plots
num_colors = 7 
blue_color_list = sns.light_palette("blue", n_colors=num_colors)
orange_color_list = sns.light_palette("orange", n_colors=num_colors)
green_color_list = sns.light_palette("green", n_colors=num_colors)

fig, (ax1, ax2, ax3) = plt.subplots(1,3, sharey=True, figsize=(9,6))
norm = min(min(g3a["Qty"][0:5]), min(g3b["Qty"][0:5]), min(g3c["Qty"][0:5]))
increment = 0.1
for i in range(0, 5):
    ax1.bar(g3a.index[i], g3a["Qty"].iloc[i]/norm, label=g3a.index[i], color=blue_color_list[i+2])
    ax2.bar(g3b.index[i], g3b["Qty"].iloc[i]/norm, label=g3b.index[i], color=orange_color_list[i+2])
    ax3.bar(g3c.index[i], g3c["Qty"].iloc[i]/norm, label=g3c.index[i], color=green_color_list[i+2])
ax1.tick_params(axis='x', rotation=90)
ax2.tick_params(axis='x', rotation=90)
ax3.tick_params(axis='x', rotation=90)
ax1.set_ylabel("Normalized Quantity Sold")
ax1.set_title("Coffee")
ax2.set_title("Tea")
ax3.set_title("Bakery")
plt.suptitle("Relative Quantities of Top 5 Products in Best-Selling Categories")
plt.show()

#%% Question 4: Worst categories - time trends? / comparison to other categories
sql_stmt4a = """
SELECT strftime("%m-%Y", t.Date) as "Month-Year", pd.ProdDetail, sum(t.Qty) as "Quantity Sold"
FROM Trans t
JOIN ProdDetail pd ON t.ProdID = pd.ProdID
JOIN ProdType pt ON pd.ProdTypeID = pt.ProdTypeID
JOIN ProdCategory pc ON pt.ProdCategoryID = pc.ProdCategoryID
WHERE pc.ProdCategory == "Packaged Chocolate"
GROUP BY pd.ProdDetail, strftime("%m-%Y", t.Date)
;"""

sql_stmt4b = """
SELECT strftime("%m-%Y", t.Date) as "Month-Year", pd.ProdDetail, sum(t.Qty) as "Quantity Sold"
FROM Trans t
JOIN ProdDetail pd ON t.ProdID = pd.ProdID
WHERE pd.ProdDetail == "Latte Rg"
GROUP BY pd.ProdDetail, strftime("%m-%Y", t.Date)
;"""

conn = sqlite3.connect("coffee_sales.db")
df4a = pd.read_sql_query(sql_stmt4a, conn)
df4b = pd.read_sql_query(sql_stmt4b, conn)
conn.close()

print(df4a, "\n \n", df4b)

# compare growth of all categories
prod_categories = df_prod_category["ProdCategory"].unique()
for cat in prod_categories:
    sql_stmt4c = f"""
    SELECT strftime("%m-%Y", t.Date) as "Month-Year", pc.ProdCategory, sum(t.Qty) as "Quantity Sold"
    FROM Trans t
    JOIN ProdDetail pd ON t.ProdID = pd.ProdID
    JOIN ProdType pt ON pd.ProdTypeID = pt.ProdTypeID
    JOIN ProdCategory pc ON pt.ProdCategoryID = pc.ProdCategoryID
    WHERE pc.ProdCategory = "{cat}"
    GROUP BY strftime("%m-%Y", t.Date)
    ;""" 

    conn = sqlite3.connect("coffee_sales.db")
    df4c = pd.read_sql_query(sql_stmt4c, conn)
    conn.close()

    print(df4c, "\n \n")

#%% Q4 - pandas
q4a = j3[j3["ProdCategory"] == "Packaged Chocolate"]
#g4a = q4a[["Date", "ProdDetail", "Qty"]].groupby([q4a["Date"].dt.month, "ProdDetail"]).agg({"Qty": "sum"})
g4a = q4a[["Date", "ProdDetail", "Qty"]].groupby(["ProdDetail", q4a["Date"].dt.month]).agg({"Qty": "sum"})
print(g4a)

q4b = j1[j1["ProdDetail"] == "Latte Rg"]
g4b = q4b[["Date", "ProdDetail", "Qty"]].groupby(["ProdDetail", q4b["Date"].dt.month]).agg({"Qty": "sum"})
print("\n", g4b)

for cat in df_prod_category["ProdCategory"].unique():
    q4c = j3[j3["ProdCategory"] == cat]
    g4c = q4c[["Date", "ProdCategory", "Qty"]].groupby(["ProdCategory", q4c["Date"].dt.month]).agg({"Qty": "sum"})
    print("\n", g4c)

#%% Q4 - visuals: Visualize category performance
sql_stmt4d = """
SELECT strftime("%m-%Y", t.Date) as "Month-Year", pc.ProdCategory, sum(t.Qty) as "Quantity Sold"
FROM Trans t
JOIN ProdDetail pd ON t.ProdID = pd.ProdID
JOIN ProdType pt ON pd.ProdTypeID = pt.ProdTypeID
JOIN ProdCategory pc ON pt.ProdCategoryID = pc.ProdCategoryID
GROUP BY pc.ProdCategory, strftime("%m-%Y", t.Date)
;""" 


conn = sqlite3.connect("coffee_sales.db")
df4d = pd.read_sql_query(sql_stmt4d, conn)
conn.close()

sns.set_palette("muted")
fig, ax = plt.subplots(figsize=(6,4))
for cat in df_prod_category["ProdCategory"].unique():
    plt.plot(df4d["Month-Year"].unique(), df4d[df4d["ProdCategory"] == cat]["Quantity Sold"], 
             "-o", linewidth=2.5, label = cat)
ax.set_yscale("log")
plt.ylabel("Quantity Sold")
plt.xlabel("Month")
plt.legend(loc="center right", bbox_to_anchor=(1.45,.52))
plt.title("Quantities of Categorized Products Sold over Time")
plt.show()

#%% Q4 - optional visual
plt.figure(figsize = (6, 4))
plt.plot(df4a["Month-Year"].unique(), df4a[df4a["ProdDetail"] == "Chili Mayan"]["Quantity Sold"], 
         "-o", label = "Chili Mayan")
plt.plot(df4a["Month-Year"].unique(), df4a[df4a["ProdDetail"] == "Dark chocolate"]["Quantity Sold"], 
         "-^", label = "Dark Chocolate")
plt.plot(df4a["Month-Year"].unique(), df4a[df4a["ProdDetail"] == "Sustainably Grown Organic"]["Quantity Sold"], 
         "-s", label = "Sustainably Grown Organic")
plt.xlabel("Month")
plt.ylabel("Quantity Sold")
plt.legend()
plt.show() 

#%% Question 5: busiest times? ensure there is enough staffing      
sql_stmt5a = """
SELECT strftime("%H", t.Time) as Time, sum(t.Qty) as "Quantity Sold", sum(t.Qty*t.Price) as "Sales"
FROM Trans t
GROUP BY strftime("%H", t.Time)
ORDER BY Sales DESC
;"""
        
conn = sqlite3.connect("coffee_sales.db")
df5a = pd.read_sql_query(sql_stmt5a, conn)
conn.close()
print(df5a)

# note that sales are quite low at 06:00 and 20:00 hours. Are all stores operating? -- relates to Question 1
sql_stmt5b = """
SELECT DISTINCT strftime("%H", t.Time) as Time, s.StoreLoc
FROM Trans t
JOIN Store s ON t.StoreID = s.StoreID
ORDER BY strftime("%H", t.Time)
;"""

conn = sqlite3.connect("coffee_sales.db")
df5b = pd.read_sql_query(sql_stmt5b, conn)
conn.close()
print("\n", df5b)
 # Astoria location has more limited hours (700-1900). 
 
sql_stmt5c = """
SELECT strftime("%H", t.Time) as Time, s.StoreLoc, sum(t.Qty) as "Quantity Sold", sum(t.Qty*t.Price) as "Sales"
FROM Trans t
JOIN Store s ON t.StoreID = s.StoreID
GROUP BY strftime("%H", t.Time), s.StoreLoc
ORDER BY Sales DESC
;"""
        
conn = sqlite3.connect("coffee_sales.db")
df5c = pd.read_sql_query(sql_stmt5c, conn)
conn.close()
print("\n", df5c)

print("\n Sales at peak times as % of total sales: ", df5a["Sales"].iloc[0:3].sum()/df5a["Sales"].sum())

#%% Q5 - pandas
q5a = df_trans[["Time", "Qty", "Sales"]]
g5a = q5a.groupby([q5a["Time"].dt.hour]).agg({"Qty": "sum", "Sales": "sum"}).sort_values("Sales", ascending = False)
print(g5a)

j5 = pd.merge(df_trans, df_store, how = "left", on = "StoreID")
q5b = j5[["Time", "StoreLoc"]]
g5b = q5b.groupby([q5b["Time"].dt.hour]).agg({"StoreLoc": "unique"})
print("\n", g5b)

q5c = j5[["Time", "StoreLoc", "Qty", "Sales"]]
g5c = q5c.groupby([q5b["Time"].dt.hour, "StoreLoc"]).agg({"Qty": "sum", "Sales": "sum"}).sort_values("Sales", ascending = False)
print("\n", g5c)

#%% Q5 visual
fig, ax = plt.subplots()
muted_colors = sns.color_palette("muted")
color_list = [muted_colors[2], muted_colors[1], muted_colors[0]]
markers = ["-s", "-^", "-o"]

i = 0
for location in df_store["StoreLoc"].sort_values(ascending = False):
    plt.plot(df5c[df5c["StoreLoc"] == location]["Time"].sort_values(), df5c[df5c["StoreLoc"] == location]["Sales"], 
             markers[i], linewidth = 2, markersize = 6, color=color_list[i], label = location)
    i+=1

plt.xlabel("Hour of the Day")
plt.ylabel("Total Sales ($)")
plt.ticklabel_format(axis = "y", style = "scientific", scilimits = (3,3))
plt.legend()
plt.title("Aggregated Hourly Sales by Location")
plt.show()

