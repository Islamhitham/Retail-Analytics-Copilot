#!/usr/bin/env python3
"""Test all SQL queries from training data to ensure they work."""

import sqlite3
import sys

# Test queries
queries = {
    "Total Revenue": 'SELECT SUM(UnitPrice * Quantity * (1 - Discount)) as TotalRevenue FROM "Order Details"',
    
    "Top 5 Products by Price": "SELECT ProductName, UnitPrice FROM Products ORDER BY UnitPrice DESC LIMIT 5",
    
    "Top 3 Products by Revenue": '''SELECT p.ProductName as product, SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)) as revenue 
        FROM "Order Details" od 
        JOIN Products p ON od.ProductID = p.ProductID 
        GROUP BY p.ProductName 
        ORDER BY revenue DESC LIMIT 3''',
    
    "AOV Winter 1997": '''SELECT ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)) / COUNT(DISTINCT o.OrderID), 2) as AOV 
        FROM Orders o 
        JOIN "Order Details" od ON o.OrderID = od.OrderID 
        WHERE o.OrderDate BETWEEN "1997-12-01" AND "1997-12-31"''',
    
    "Revenue Beverages Summer 1997": '''SELECT ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)), 2) as revenue 
        FROM Orders o 
        JOIN "Order Details" od ON o.OrderID = od.OrderID 
        JOIN Products p ON od.ProductID = p.ProductID 
        JOIN Categories c ON p.CategoryID = c.CategoryID 
        WHERE c.CategoryName = "Beverages" 
        AND o.OrderDate BETWEEN "1997-06-01" AND "1997-06-30"''',
    
    "Top Category Summer 1997": '''SELECT c.CategoryName as category, SUM(od.Quantity) as quantity 
        FROM Orders o 
        JOIN "Order Details" od ON o.OrderID = od.OrderID 
        JOIN Products p ON od.ProductID = p.ProductID 
        JOIN Categories c ON p.CategoryID = c.CategoryID 
        WHERE o.OrderDate BETWEEN "1997-06-01" AND "1997-06-30" 
        GROUP BY c.CategoryName 
        ORDER BY quantity DESC LIMIT 1''',
    
    "Top Customer by Margin 1997": '''SELECT c.CompanyName as customer, ROUND(SUM((od.UnitPrice - 0.7 * od.UnitPrice) * od.Quantity * (1 - od.Discount)), 2) as margin 
        FROM Orders o 
        JOIN "Order Details" od ON o.OrderID = od.OrderID 
        JOIN Customers c ON o.CustomerID = c.CustomerID 
        WHERE strftime("%Y", o.OrderDate) = "1997" 
        GROUP BY c.CompanyName 
        ORDER BY margin DESC LIMIT 1'''
}

def test_queries(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("TESTING SQL QUERIES")
    print("=" * 80)
    
    all_passed = True
    
    for name, query in queries.items():
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            print(f"\n✅ {name}")
            print(f"   Result: {result[0] if result else 'No results'}")
        except Exception as e:
            print(f"\n❌ {name}")
            print(f"   Error: {e}")
            all_passed = False
    
    conn.close()
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL QUERIES PASSED!")
    else:
        print("❌ SOME QUERIES FAILED")
    print("=" * 80)
    
    return all_passed

if __name__ == "__main__":
    db_path = "your_project/data/northwind.sqlite"
    success = test_queries(db_path)
    sys.exit(0 if success else 1)
