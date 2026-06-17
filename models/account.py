"""
Account Models - Demonstrates Inheritance and Polymorphism
Base Account class with specialized SavingsAccount and CurrentAccount subclasses
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from database import DatabaseManager


class Account(ABC):
    """
    Abstract base Account class.
    Demonstrates: Abstraction, Encapsulation, Inheritance
    """
    
    def __init__(self, account_id: int = None, customer_id: int = None,
                 account_type: str = None, account_number: str = None,
                 balance: float = 0.0, branch_id: int = None):
        """
        Initialize Account object.
        """
        # Private attributes (Encapsulation)
        self._Account__account_id = account_id
        self._Account__customer_id = customer_id
        self._Account__account_type = account_type
        self._Account__account_number = account_number
        self._Account__balance = balance
        self._Account__branch_id = branch_id
        self._Account__status = "ACTIVE"
        self._Account__db = DatabaseManager()
    
    # ==================== ABSTRACT METHODS (Abstraction) ====================
    
    @abstractmethod
    def calculate_interest(self) -> float:
        """Abstract method to calculate interest"""
        pass
    
    @abstractmethod
    def apply_charges(self) -> float:
        """Abstract method to apply charges"""
        pass
    
    @abstractmethod
    def get_account_details(self) -> Dict:
        """Abstract method to get account details"""
        pass
    
    # ==================== PROPERTY GETTERS (Encapsulation) ====================
    
    @property
    def account_id(self) -> int:
        """Get account ID"""
        return self._Account__account_id
    
    @property
    def customer_id(self) -> int:
        """Get customer ID"""
        return self._Account__customer_id
    
    @property
    def account_type(self) -> str:
        """Get account type"""
        return self._Account__account_type
    
    @property
    def account_number(self) -> str:
        """Get account number"""
        return self._Account__account_number
    
    @property
    def balance(self) -> float:
        """Get current balance"""
        return self._Account__balance
    
    @property
    def status(self) -> str:
        """Get account status"""
        return self._Account__status
    
    # ==================== COMMON METHODS ====================
    
    def create_account(self) -> Dict:
        """
        Create new account in database.
        """
        try:
            if not self._Account__customer_id or not self._Account__account_number:
                return {"status": "error", "message": "Customer ID and account number are required"}
            
            query = """
                INSERT INTO accounts (
                    account_id, customer_id, account_type, account_number,
                    balance, branch_id, status
                ) VALUES (acc_seq.NEXTVAL, :1, :2, :3, :4, :5, :6)
            """
            
            params = (
                self._Account__customer_id,
                self._Account__account_type,
                self._Account__account_number,
                self._Account__balance,
                self._Account__branch_id,
                self._Account__status
            )
            
            self._Account__db.execute_update(query, params)
            
            query_id = "SELECT acc_seq.CURRVAL FROM dual"
            result = self._Account__db.execute_query(query_id)
            self._Account__account_id = result[0][0]
            
            return {
                "status": "success",
                "message": "Account created successfully",
                "account_id": self._Account__account_id,
                "account_number": self._Account__account_number
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Account creation failed: {str(e)}"
            }
    
    def deposit(self, amount: float) -> Dict:
        """
        Deposit money into account.
        """
        try:
            if amount <= 0:
                return {"status": "error", "message": "Amount must be greater than 0"}
            
            if not self._Account__account_id:
                return {"status": "error", "message": "Account ID not set"}
            
            params = [self._Account__account_id, amount, "Deposit", None]
            self._Account__db.call_procedure("proc_deposit", params)
            
            self._Account__balance = self._fetch_balance()
            
            return {
                "status": "success",
                "message": f"Deposit successful. New balance: {self._Account__balance}",
                "amount": amount,
                "new_balance": self._Account__balance
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Deposit failed: {str(e)}"
            }
    
    def withdraw(self, amount: float) -> Dict:
        """
        Withdraw money from account.
        """
        try:
            if amount <= 0:
                return {"status": "error", "message": "Amount must be greater than 0"}
            
            if not self._Account__account_id:
                return {"status": "error", "message": "Account ID not set"}
            
            params = [self._Account__account_id, amount, "Withdrawal", None]
            self._Account__db.call_procedure("proc_withdraw", params)
            
            self._Account__balance = self._fetch_balance()
            
            return {
                "status": "success",
                "message": f"Withdrawal successful. New balance: {self._Account__balance}",
                "amount": amount,
                "new_balance": self._Account__balance
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Withdrawal failed: {str(e)}"
            }
    
    def get_balance(self) -> Dict:
        """
        Get current account balance.
        """
        try:
            if not self._Account__account_id:
                return {"status": "error", "message": "Account ID not set"}
            
            self._Account__balance = self._fetch_balance()
            
            return {
                "status": "success",
                "balance": self._Account__balance,
                "account_number": self._Account__account_number,
                "account_type": self._Account__account_type
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error retrieving balance: {str(e)}"
            }
    
    def get_transaction_history(self, limit: int = 10) -> Dict:
        """
        Get transaction history for this account.
        """
        try:
            if not self._Account__account_id:
                return {"status": "error", "message": "Account ID not set"}
            
            query = """
                SELECT transaction_id, transaction_type, amount, 
                       TO_CHAR(transaction_date, 'YYYY-MM-DD HH24:MI:SS') as transaction_date,
                       description, balance_after
                FROM transactions
                WHERE account_id = :1
                ORDER BY transaction_date DESC
                FETCH FIRST :2 ROWS ONLY
            """
            
            results = self._Account__db.execute_query(query, (self._Account__account_id, limit))
            
            transactions = []
            for row in results:
                transactions.append({
                    "transaction_id": row[0],
                    "type": row[1],
                    "amount": row[2],
                    "date": row[3],
                    "description": row[4],
                    "balance_after": row[5]
                })
            
            return {
                "status": "success",
                "account_id": self._Account__account_id,
                "transactions": transactions,
                "count": len(transactions)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error retrieving transaction history: {str(e)}"
            }
    
    def _fetch_balance(self) -> float:
        """
        Private method to fetch current balance from database.
        """
        query = "SELECT balance FROM accounts WHERE account_id = :1"
        result = self._Account__db.execute_query(query, (self._Account__account_id,))
        return float(result[0][0]) if result else 0.0
    
    def __str__(self) -> str:
        """String representation"""
        return f"{self._Account__account_type}Account(ID: {self._Account__account_id}, Number: {self._Account__account_number}, Balance: {self._Account__balance})"


class SavingsAccount(Account):
    """
    Savings Account subclass - demonstrates Inheritance and Polymorphism.
    """
    
    INTEREST_RATE = 0.02  # 2% annual interest
    MINIMUM_BALANCE = 1000
    MONTHLY_CHARGE = 5
    
    def __init__(self, account_id: int = None, customer_id: int = None,
                 account_number: str = None, balance: float = 0.0, branch_id: int = None):
        """Initialize Savings Account."""
        super().__init__(account_id, customer_id, "SAVINGS", account_number, balance, branch_id)
    
    def calculate_interest(self) -> float:
        """Calculate interest for savings account (Polymorphism)."""
        monthly_interest = (self.balance * self.INTEREST_RATE) / 12
        return round(monthly_interest, 2)
    
    def apply_charges(self) -> float:
        """Apply monthly charges if balance is below minimum (Polymorphism)."""
        if self.balance < self.MINIMUM_BALANCE:
            return self.MONTHLY_CHARGE
        return 0
    
    def apply_monthly_maintenance(self) -> Dict:
        """Apply interest and charges for the month."""
        try:
            if not self.account_id:
                return {"status": "error", "message": "Account ID not set"}
            
            interest = self.calculate_interest()
            charges = self.apply_charges()
            
            net_amount = interest - charges
            
            if net_amount != 0:
                query = "UPDATE accounts SET balance = balance + :1 WHERE account_id = :2"
                self._Account__db.execute_update(query, (net_amount, self.account_id))
            
            return {
                "status": "success",
                "interest_earned": interest,
                "charges_applied": charges,
                "net_change": net_amount,
                "new_balance": self._fetch_balance()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Monthly maintenance failed: {str(e)}"
            }
    
    def get_account_details(self) -> Dict:
        """Get Savings Account specific details (Polymorphism)."""
        return {
            "status": "success",
            "account_type": "SAVINGS",
            "account_id": self.account_id,
            "account_number": self.account_number,
            "balance": self.balance,
            "interest_rate": f"{self.INTEREST_RATE * 100}%",
            "monthly_interest": self.calculate_interest(),
            "minimum_balance": self.MINIMUM_BALANCE,
            "monthly_charge": self.MONTHLY_CHARGE,
            "overdraft_allowed": False
        }


class CurrentAccount(Account):
    """
    Current Account subclass - demonstrates Inheritance and Polymorphism.
    Designed for business/commercial use with overdraft facility.
    """
    
    INTEREST_RATE = 0.0
    OVERDRAFT_LIMIT = 10000
    MONTHLY_CHARGE = 25
    
    def __init__(self, account_id: int = None, customer_id: int = None,
                 account_number: str = None, balance: float = 0.0, branch_id: int = None):
        """Initialize Current Account."""
        super().__init__(account_id, customer_id, "CURRENT", account_number, balance, branch_id)
    
    def calculate_interest(self) -> float:
        """Calculate interest for current account - always 0 (Polymorphism)."""
        return 0.0
    
    def apply_charges(self) -> float:
        """Apply monthly charges for current account (Polymorphism)."""
        return self.MONTHLY_CHARGE
    
    def withdraw(self, amount: float) -> Dict:
        """Override withdraw method to allow overdraft (Polymorphism)."""
        try:
            if amount <= 0:
                return {"status": "error", "message": "Amount must be greater than 0"}
            
            if not self.account_id:
                return {"status": "error", "message": "Account ID not set"}
            
            if (self.balance - amount) < -self.OVERDRAFT_LIMIT:
                return {
                    "status": "error",
                    "message": f"Withdrawal exceeds overdraft limit. Available: {self.balance + self.OVERDRAFT_LIMIT}"
                }
            
            query = "UPDATE accounts SET balance = balance - :1 WHERE account_id = :2"
            self._Account__db.execute_update(query, (amount, self.account_id))
            
            return {
                "status": "success",
                "message": f"Withdrawal successful. New balance: {self._fetch_balance()}",
                "amount": amount,
                "new_balance": self._fetch_balance()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Withdrawal failed: {str(e)}"
            }
    
    def apply_monthly_charges(self) -> Dict:
        """Apply monthly charges for current account."""
        try:
            if not self.account_id:
                return {"status": "error", "message": "Account ID not set"}
            
            charge = self.apply_charges()
            
            query = "UPDATE accounts SET balance = balance - :1 WHERE account_id = :2"
            self._Account__db.execute_update(query, (charge, self.account_id))
            
            return {
                "status": "success",
                "charge_applied": charge,
                "new_balance": self._fetch_balance()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Charge application failed: {str(e)}"
            }
    
    def get_account_details(self) -> Dict:
        """Get Current Account specific details (Polymorphism)."""
        return {
            "status": "success",
            "account_type": "CURRENT",
            "account_id": self.account_id,
            "account_number": self.account_number,
            "balance": self.balance,
            "interest_rate": f"{self.INTEREST_RATE * 100}%",
            "overdraft_limit": self.OVERDRAFT_LIMIT,
            "available_overdraft": max(0, self.OVERDRAFT_LIMIT + self.balance),
            "monthly_charge": self.MONTHLY_CHARGE,
            "overdraft_allowed": True
        }
