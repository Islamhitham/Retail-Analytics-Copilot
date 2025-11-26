import dspy

# Training examples for GenerateSQL
train_examples = [
    dspy.Example(
        question="What is the total revenue from Orders?",
        db_schema="orders (OrderID, CustomerID, EmployeeID, OrderDate, ...), order_items (OrderID, ProductID, UnitPrice, Quantity, Discount), ...",
        constraints="",
        sql_query="SELECT SUM(UnitPrice * Quantity * (1 - Discount)) as TotalRevenue FROM order_items"
    ).with_inputs("question", "db_schema", "constraints"),
    
    dspy.Example(
        question="List top 5 products by unit price.",
        db_schema="products (ProductID, ProductName, SupplierID, CategoryID, UnitPrice, ...)",
        constraints="",
        sql_query="SELECT ProductName, UnitPrice FROM products ORDER BY UnitPrice DESC LIMIT 5"
    ).with_inputs("question", "db_schema", "constraints"),
    
    dspy.Example(
        question="How many customers are from UK?",
        db_schema="customers (CustomerID, CompanyName, Country, ...)",
        constraints="",
        sql_query="SELECT COUNT(*) FROM customers WHERE Country = 'UK'"
    ).with_inputs("question", "db_schema", "constraints"),
    
    dspy.Example(
        question="What is the average order value?",
        db_schema="orders (OrderID, ...), order_items (OrderID, UnitPrice, Quantity, Discount)",
        constraints="AOV = SUM(UnitPrice * Quantity * (1 - Discount)) / COUNT(DISTINCT OrderID)",
        sql_query="SELECT SUM(UnitPrice * Quantity * (1 - Discount)) / COUNT(DISTINCT OrderID) as AOV FROM order_items"
    ).with_inputs("question", "db_schema", "constraints"),
    
    dspy.Example(
        question="Find total sales for 'Beverages' category.",
        db_schema="products (ProductID, CategoryID, ...), order_items (OrderID, ProductID, UnitPrice, Quantity, Discount), categories (CategoryID, CategoryName, ...)",
        constraints="",
        sql_query="SELECT SUM(t1.UnitPrice * t1.Quantity * (1 - t1.Discount)) FROM order_items AS t1 JOIN products AS t2 ON t1.ProductID = t2.ProductID JOIN categories AS t3 ON t2.CategoryID = t3.CategoryID WHERE t3.CategoryName = 'Beverages'"
    ).with_inputs("question", "db_schema", "constraints")
]
