import dspy

# Updated training examples with WORKING SQL queries for Northwind database
train_examples = [
    dspy.Example(
        question="What is the total revenue from Orders?",
        db_schema="Orders (OrderID, CustomerID, EmployeeID, OrderDate), \"Order Details\" (OrderID, ProductID, UnitPrice, Quantity, Discount)",
        constraints="Revenue = SUM(UnitPrice * Quantity * (1 - Discount))",
        sql_query='SELECT SUM(UnitPrice * Quantity * (1 - Discount)) as TotalRevenue FROM "Order Details"'
    ).with_inputs("question", "db_schema", "constraints"),
    
    dspy.Example(
        question="List top 5 products by unit price.",
        db_schema="Products (ProductID, ProductName, UnitPrice, CategoryID)",
        constraints="",
        sql_query="SELECT ProductName, UnitPrice FROM Products ORDER BY UnitPrice DESC LIMIT 5"
    ).with_inputs("question", "db_schema", "constraints"),
    
    dspy.Example(
        question="Top 3 products by total revenue all-time.",
        db_schema="Products (ProductID, ProductName), \"Order Details\" (OrderID, ProductID, UnitPrice, Quantity, Discount)",
        constraints="Revenue = SUM(UnitPrice * Quantity * (1 - Discount))",
        sql_query='SELECT p.ProductName as product, SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)) as revenue FROM "Order Details" od JOIN Products p ON od.ProductID = p.ProductID GROUP BY p.ProductName ORDER BY revenue DESC LIMIT 3'
    ).with_inputs("question", "db_schema", "constraints"),
    
    dspy.Example(
        question="What was the Average Order Value during Winter Classics 1997 (Dec 1-31)?",
        db_schema="Orders (OrderID, OrderDate), \"Order Details\" (OrderID, UnitPrice, Quantity, Discount)",
        constraints="AOV = SUM(UnitPrice * Quantity * (1 - Discount)) / COUNT(DISTINCT OrderID), Dates: 1997-12-01 to 1997-12-31",
        sql_query='SELECT ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)) / COUNT(DISTINCT o.OrderID), 2) as AOV FROM Orders o JOIN "Order Details" od ON o.OrderID = od.OrderID WHERE o.OrderDate BETWEEN "1997-12-01" AND "1997-12-31"'
    ).with_inputs("question", "db_schema", "constraints"),
    
    dspy.Example(
        question="Total revenue from Beverages category during Summer 1997 (June 1-30)?",
        db_schema="Orders (OrderID, OrderDate), \"Order Details\" (OrderID, ProductID, UnitPrice, Quantity, Discount), Products (ProductID, CategoryID), Categories (CategoryID, CategoryName)",
        constraints="Revenue = SUM(UnitPrice * Quantity * (1 - Discount)), Category: Beverages, Dates: 1997-06-01 to 1997-06-30",
        sql_query='SELECT ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)), 2) as revenue FROM Orders o JOIN "Order Details" od ON o.OrderID = od.OrderID JOIN Products p ON od.ProductID = p.ProductID JOIN Categories c ON p.CategoryID = c.CategoryID WHERE c.CategoryName = "Beverages" AND o.OrderDate BETWEEN "1997-06-01" AND "1997-06-30"'
    ).with_inputs("question", "db_schema", "constraints"),
    
    dspy.Example(
        question="Which category had highest total quantity sold during Summer 1997?",
        db_schema="Orders (OrderID, OrderDate), \"Order Details\" (OrderID, ProductID, Quantity), Products (ProductID, CategoryID), Categories (CategoryID, CategoryName)",
        constraints="Dates: 1997-06-01 to 1997-06-30",
        sql_query='SELECT c.CategoryName as category, SUM(od.Quantity) as quantity FROM Orders o JOIN "Order Details" od ON o.OrderID = od.OrderID JOIN Products p ON od.ProductID = p.ProductID JOIN Categories c ON p.CategoryID = c.CategoryID WHERE o.OrderDate BETWEEN "1997-06-01" AND "1997-06-30" GROUP BY c.CategoryName ORDER BY quantity DESC LIMIT 1'
    ).with_inputs("question", "db_schema", "constraints"),
    
    dspy.Example(
        question="Top customer by gross margin in 1997?",
        db_schema="Orders (OrderID, CustomerID, OrderDate), \"Order Details\" (OrderID, UnitPrice, Quantity, Discount), Customers (CustomerID, CompanyName)",
        constraints="Gross Margin = SUM((UnitPrice - CostOfGoods) * Quantity * (1 - Discount)), CostOfGoods approximated as 0.7 * UnitPrice",
        sql_query='SELECT c.CompanyName as customer, ROUND(SUM((od.UnitPrice - 0.7 * od.UnitPrice) * od.Quantity * (1 - od.Discount)), 2) as margin FROM Orders o JOIN "Order Details" od ON o.OrderID = od.OrderID JOIN Customers c ON o.CustomerID = c.CustomerID WHERE strftime("%Y", o.OrderDate) = "1997" GROUP BY c.CompanyName ORDER BY margin DESC LIMIT 1'
    ).with_inputs("question", "db_schema", "constraints"),
]
