"""
Transaction Model - Handles transaction operations and history
Demonstrates: Exception Handling, Encapsulation
"""

from datetime import datetime
from typing import Dict, List
from database import DatabaseManager


class Transaction:
    """
    Transaction class for managing account transactions.
    """
    
    TRANSACTION_TYPES = ['DEPOSIT', 'WITHDRAWAL', 'TRANSFER_OUT', 'TRANSFER_IN']
    
    def __init__(self, transaction_id: int = None, account_id: int = None,
                 transaction_type: str = None, amount: float = None):
        """
        Initialize Transaction object.
        """
        self.__transaction_id = transaction_id
        self.__account_id = account_id
        self.__transaction_type = transaction_type
        self.__amount = amount
        self.__transaction_date = None
        self.__status = "COMPLETED"
        self.__db = DatabaseManager()
    
    @property
    def transaction_id(self) -> int:
        """Get transaction ID"""
        return self.__transaction_id
    
    @property
    def account_id(self) -> int:
        """Get account ID"""
        return self.__account_id
    
    @property
    def amount(self) -> float:
        """Get transaction amount"""
        return self.__amount
    
    def get_transaction_details(self) -> Dict:
        """
        Get detailed transaction information.
        """
        try:
            if not self.__transaction_id:
                return {"status": "error", "message": "Transaction ID not set"}
            
            query = """
                SELECT transaction_id, account_id, transaction_type, amount,
                       TO_CHAR(transaction_date, 'YYYY-MM-DD HH24:MI:SS') as transaction_date,
                       description, balance_after, status
                FROM transactions
                WHERE transaction_id = :1
            """
            
            result = self.__db.execute_query(query, (self.__transaction_id,))
            
            if not result:
                return {"status": "error", "message": "Transaction not found"}
            
            data = result[0]
            
            return {
                "status": "success",
                "transaction_id": data[0],
                "account_id": data[1],
                "type": data[2],
                "amount": data[3],
                "date": data[4],
                "description": data[5],
                "balance_after": data[6],
                "status": data[7]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error retrieving transaction: {str(e)}"
            }
    
    def get_account_transactions(self, account_id: int, limit: int = 20) -> Dict:
        """
        Get all transactions for an account.
        """
        try:
            query = """
                SELECT transaction_id, transaction_type, amount,
                       TO_CHAR(transaction_date, 'YYYY-MM-DD HH24:MI:SS') as transaction_date,
                       description, balance_after, status
                FROM transactions
                WHERE account_id = :1
                ORDER BY transaction_date DESC
                FETCH FIRST :2 ROWS ONLY
            """
            
            results = self.__db.execute_query(query, (account_id, limit))
            
            transactions = []
            for row in results:
                transactions.append({
                    "transaction_id": row[0],
                    "type": row[1],
                    "amount": row[2],
                    "date": row[3],
                    "description": row[4],
                    "balance_after": row[5],
                    "status": row[6]
                })
            
            return {
                "status": "success",
                "account_id": account_id,
                "transactions": transactions,
                "count": len(transactions)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error retrieving transactions: {str(e)}"
            }
    
    def get_transaction_summary(self, account_id: int) -> Dict:
        """
        Get transaction summary for an account.
        """
        try:
            query = """
                SELECT transaction_type, COUNT(*) as count, SUM(amount) as total
                FROM transactions
                WHERE account_id = :1
                GROUP BY transaction_type
            """
            
            results = self.__db.execute_query(query, (account_id,))
            
            summary = {}
            for row in results:
                summary[row[0]] = {
                    "count": row[1],
                    "total": row[2]
                }
            
            return {
                "status": "success",
                "account_id": account_id,
                "summary": summary
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error retrieving transaction summary: {str(e)}"
            }
