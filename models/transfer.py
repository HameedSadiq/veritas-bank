"""
Transfer, BankStaff, and AuditLogger Models
Demonstrates: Encapsulation, Exception Handling, Separation of Concerns
"""

from datetime import datetime
from typing import Dict, List
from database import DatabaseManager


class TransferService:
    """
    TransferService class for managing money transfers between accounts.
    Demonstrates secure transfer handling and transaction rollback.
    """
    
    def __init__(self):
        """Initialize TransferService"""
        self.__db = DatabaseManager()
    
    def transfer_funds(self, from_account_id: int, to_account_id: int, 
                      amount: float, description: str = "Transfer") -> Dict:
        """
        Transfer funds from one account to another.
        Implements ACID transactions with automatic rollback on error.
        
        Args:
            from_account_id: Source account ID
            to_account_id: Destination account ID
            amount: Amount to transfer
            description: Transfer description
            
        Returns:
            Dictionary with transfer status
        """
        try:
            if amount <= 0:
                return {"status": "error", "message": "Amount must be greater than 0"}
            
            if from_account_id == to_account_id:
                return {"status": "error", "message": "Cannot transfer to same account"}
            
            # Call Oracle stored procedure (handles transaction management)
            params = [from_account_id, to_account_id, amount, description, None]
            self.__db.call_procedure("proc_transfer", params)
            
            return {
                "status": "success",
                "message": "Transfer completed successfully",
                "from_account": from_account_id,
                "to_account": to_account_id,
                "amount": amount
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Transfer failed: {str(e)}"
            }
    
    def get_transfer_history(self, account_id: int, limit: int = 10) -> Dict:
        """
        Get transfer history for an account.
        
        Args:
            account_id: Account ID
            limit: Number of records to retrieve
            
        Returns:
            Dictionary with transfer history
        """
        try:
            query = """
                SELECT transfer_id, from_account_id, to_account_id, amount,
                       TO_CHAR(transfer_date, 'YYYY-MM-DD HH24:MI:SS') as transfer_date,
                       transfer_type, status, description
                FROM transfers
                WHERE from_account_id = :1 OR to_account_id = :1
                ORDER BY transfer_date DESC
                FETCH FIRST :2 ROWS ONLY
            """
            
            results = self.__db.execute_query(query, (account_id, limit))
            
            transfers = []
            for row in results:
                transfers.append({
                    "transfer_id": row[0],
                    "from_account": row[1],
                    "to_account": row[2],
                    "amount": row[3],
                    "date": row[4],
                    "type": row[5],
                    "status": row[6],
                    "description": row[7]
                })
            
            return {
                "status": "success",
                "account_id": account_id,
                "transfers": transfers,
                "count": len(transfers)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error retrieving transfer history: {str(e)}"
            }


class BankStaff:
    """
    BankStaff class representing bank employees.
    """
    
    def __init__(self, staff_id: int = None, first_name: str = None,
                 last_name: str = None, email: str = None, position: str = None):
        """Initialize BankStaff object"""
        self.__staff_id = staff_id
        self.__first_name = first_name
        self.__last_name = last_name
        self.__email = email
        self.__position = position
        self.__status = "ACTIVE"
        self.__db = DatabaseManager()
    
    @property
    def staff_id(self) -> int:
        """Get staff ID"""
        return self.__staff_id
    
    @property
    def position(self) -> str:
        """Get position"""
        return self.__position
    
    def get_staff_details(self) -> Dict:
        """
        Get staff member details.
        """
        try:
            if not self.__staff_id:
                return {"status": "error", "message": "Staff ID not set"}
            
            query = """
                SELECT staff_id, first_name, last_name, email, position,
                       TO_CHAR(hire_date, 'YYYY-MM-DD') as hire_date, status
                FROM bank_staff
                WHERE staff_id = :1
            """
            
            result = self.__db.execute_query(query, (self.__staff_id,))
            
            if not result:
                return {"status": "error", "message": "Staff member not found"}
            
            data = result[0]
            
            return {
                "status": "success",
                "staff_id": data[0],
                "first_name": data[1],
                "last_name": data[2],
                "email": data[3],
                "position": data[4],
                "hire_date": data[5],
                "status": data[6]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error retrieving staff details: {str(e)}"
            }


class AuditLogger:
    """
    AuditLogger class for logging all banking operations.
    Demonstrates security and compliance requirements.
    """
    
    def __init__(self):
        """Initialize AuditLogger"""
        self.__db = DatabaseManager()
    
    def log_action(self, account_id: int = None, customer_id: int = None,
                  action_type: str = None, description: str = None,
                  old_value: str = None, new_value: str = None,
                  performed_by: int = None, ip_address: str = None) -> Dict:
        """
        Log an action in the audit log.
        
        Args:
            account_id: Account ID (if applicable)
            customer_id: Customer ID (if applicable)
            action_type: Type of action performed
            description: Detailed description
            old_value: Previous value (for updates)
            new_value: New value (for updates)
            performed_by: Staff ID who performed action
            ip_address: IP address of the request
            
        Returns:
            Dictionary with logging status
        """
        try:
            query = """
                INSERT INTO audit_logs (
                    audit_id, account_id, customer_id, action_type,
                    action_description, old_value, new_value,
                    performed_by, ip_address, action_date
                ) VALUES (
                    audit_seq.NEXTVAL, :1, :2, :3, :4, :5, :6, :7, :8, SYSDATE
                )
            """
            
            params = (
                account_id,
                customer_id,
                action_type,
                description,
                old_value,
                new_value,
                performed_by,
                ip_address
            )
            
            self.__db.execute_update(query, params)
            
            return {
                "status": "success",
                "message": "Action logged successfully"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Audit logging failed: {str(e)}"
            }
    
    def get_audit_logs(self, account_id: int = None, customer_id: int = None,
                      limit: int = 50) -> Dict:
        """
        Retrieve audit logs.
        
        Args:
            account_id: Filter by account ID
            customer_id: Filter by customer ID
            limit: Number of records to retrieve
            
        Returns:
            Dictionary with audit logs
        """
        try:
            if account_id:
                query = """
                    SELECT audit_id, account_id, action_type, action_description,
                           old_value, new_value,
                           TO_CHAR(action_date, 'YYYY-MM-DD HH24:MI:SS') as action_date
                    FROM audit_logs
                    WHERE account_id = :1
                    ORDER BY action_date DESC
                    FETCH FIRST :2 ROWS ONLY
                """
                results = self.__db.execute_query(query, (account_id, limit))
            
            elif customer_id:
                query = """
                    SELECT audit_id, customer_id, action_type, action_description,
                           old_value, new_value,
                           TO_CHAR(action_date, 'YYYY-MM-DD HH24:MI:SS') as action_date
                    FROM audit_logs
                    WHERE customer_id = :1
                    ORDER BY action_date DESC
                    FETCH FIRST :2 ROWS ONLY
                """
                results = self.__db.execute_query(query, (customer_id, limit))
            
            else:
                query = """
                    SELECT audit_id, account_id, customer_id, action_type,
                           action_description, old_value, new_value,
                           TO_CHAR(action_date, 'YYYY-MM-DD HH24:MI:SS') as action_date
                    FROM audit_logs
                    ORDER BY action_date DESC
                    FETCH FIRST :1 ROWS ONLY
                """
                results = self.__db.execute_query(query, (limit,))
            
            logs = []
            for row in results:
                logs.append({
                    "audit_id": row[0],
                    "account_id": row[1] if len(row) > 1 else None,
                    "action_type": row[2] if len(row) > 2 else None,
                    "description": row[3] if len(row) > 3 else None,
                    "old_value": row[4] if len(row) > 4 else None,
                    "new_value": row[5] if len(row) > 5 else None,
                    "timestamp": row[6] if len(row) > 6 else None
                })
            
            return {
                "status": "success",
                "logs": logs,
                "count": len(logs)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error retrieving audit logs: {str(e)}"
            }
