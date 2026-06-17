"""
Customer Model - Represents bank customer with OOP principles
Demonstrates: Encapsulation, Abstraction, Exception Handling
"""

from datetime import datetime
from typing import Optional, Dict
import re
from database import DatabaseManager


class Customer:
    """
    Customer class representing a bank customer.
    Demonstrates Encapsulation with private attributes and public methods.
    """
    
    def __init__(self, customer_id: int = None, first_name: str = None, 
                 last_name: str = None, email: str = None, phone: str = None,
                 address: str = None, id_number: str = None, 
                 date_of_birth: str = None):
        """
        Initialize Customer object.
        """
        # Private attributes (Encapsulation)
        self.__customer_id = customer_id
        self.__first_name = first_name
        self.__last_name = last_name
        self.__email = email
        self.__phone = phone
        self.__address = address
        self.__id_number = id_number
        self.__date_of_birth = date_of_birth
        self.__registration_date = None
        self.__status = "ACTIVE"
        self.__db = DatabaseManager()
    
    # ==================== PROPERTY GETTERS (Encapsulation) ====================
    
    @property
    def customer_id(self) -> int:
        """Get customer ID"""
        return self.__customer_id
    
    @property
    def first_name(self) -> str:
        """Get first name"""
        return self.__first_name
    
    @property
    def last_name(self) -> str:
        """Get last name"""
        return self.__last_name
    
    @property
    def email(self) -> str:
        """Get email address"""
        return self.__email
    
    @property
    def phone(self) -> str:
        """Get phone number"""
        return self.__phone
    
    @property
    def address(self) -> str:
        """Get address"""
        return self.__address
    
    @property
    def id_number(self) -> str:
        """Get ID number"""
        return self.__id_number
    
    @property
    def date_of_birth(self) -> str:
        """Get date of birth"""
        return self.__date_of_birth
    
    @property
    def status(self) -> str:
        """Get customer status"""
        return self.__status
    
    # ==================== PROPERTY SETTERS (Encapsulation) ====================
    
    @first_name.setter
    def first_name(self, value: str):
        """Set first name with validation"""
        if not value or len(value) < 2:
            raise ValueError("First name must be at least 2 characters")
        self.__first_name = value
    
    @last_name.setter
    def last_name(self, value: str):
        """Set last name with validation"""
        if not value or len(value) < 2:
            raise ValueError("Last name must be at least 2 characters")
        self.__last_name = value
    
    @email.setter
    def email(self, value: str):
        """Set email with validation"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise ValueError("Invalid email format")
        self.__email = value
    
    @phone.setter
    def phone(self, value: str):
        """Set phone with validation"""
        if not value or len(value) < 10:
            raise ValueError("Phone number must be at least 10 digits")
        self.__phone = value
    
    @address.setter
    def address(self, value: str):
        """Set address with validation"""
        if not value or len(value) < 5:
            raise ValueError("Address must be at least 5 characters")
        self.__address = value
    
    # ==================== BUSINESS METHODS ====================
    
    def register(self) -> Dict:
        """
        Register customer in the database.
        """
        try:
            self._validate_registration()
            
            query = """
                INSERT INTO customers (
                    customer_id, first_name, last_name, email, phone,
                    address, id_number, date_of_birth, status
                ) VALUES (cust_seq.NEXTVAL, :1, :2, :3, :4, :5, :6, 
                          TO_DATE(:7, 'YYYY-MM-DD'), :8)
            """
            
            params = (
                self.__first_name,
                self.__last_name,
                self.__email,
                self.__phone,
                self.__address,
                self.__id_number,
                self.__date_of_birth,
                self.__status
            )
            
            self.__db.execute_update(query, params)
            
            query_id = "SELECT cust_seq.CURRVAL FROM dual"
            result = self.__db.execute_query(query_id)
            self.__customer_id = result[0][0]
            
            return {
                "status": "success",
                "message": f"Customer registered successfully with ID: {self.__customer_id}",
                "customer_id": self.__customer_id
            }
            
        except ValueError as e:
            return {
                "status": "error",
                "message": f"Validation error: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Registration failed: {str(e)}"
            }
    
    def login(self, email: str, id_number: str) -> Dict:
        """
        Authenticate customer login.
        """
        try:
            query = """
                SELECT customer_id, first_name, last_name, status
                FROM customers
                WHERE email = :1 AND id_number = :2
            """
            
            result = self.__db.execute_query(query, (email, id_number))
            
            if not result:
                return {
                    "status": "error",
                    "message": "Invalid credentials"
                }
            
            customer_data = result[0]
            self.__customer_id = customer_data[0]
            self.__first_name = customer_data[1]
            self.__last_name = customer_data[2]
            self.__status = customer_data[3]
            
            if self.__status != "ACTIVE":
                return {
                    "status": "error",
                    "message": f"Account is {self.__status}"
                }
            
            return {
                "status": "success",
                "message": f"Login successful. Welcome {self.__first_name}",
                "customer_id": self.__customer_id
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Login failed: {str(e)}"
            }
    
    def get_customer_details(self) -> Dict:
        """
        Get customer details from database.
        """
        try:
            if not self.__customer_id:
                return {"status": "error", "message": "Customer ID not set"}
            
            query = """
                SELECT customer_id, first_name, last_name, email, phone,
                       address, id_number, date_of_birth, registration_date, status
                FROM customers
                WHERE customer_id = :1
            """
            
            result = self.__db.execute_query(query, (self.__customer_id,))
            
            if not result:
                return {"status": "error", "message": "Customer not found"}
            
            data = result[0]
            
            return {
                "status": "success",
                "customer_id": data[0],
                "first_name": data[1],
                "last_name": data[2],
                "email": data[3],
                "phone": data[4],
                "address": data[5],
                "id_number": data[6],
                "date_of_birth": str(data[7]),
                "registration_date": str(data[8]),
                "status": data[9]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error retrieving customer details: {str(e)}"
            }
    
    def update_profile(self, phone: str = None, address: str = None) -> Dict:
        """
        Update customer profile information.
        """
        try:
            if not self.__customer_id:
                return {"status": "error", "message": "Customer ID not set"}
            
            update_fields = []
            params = []
            
            if phone:
                self.phone = phone
                update_fields.append("phone = :1")
                params.append(phone)
            
            if address:
                self.address = address
                update_fields.append(f"address = :{len(params) + 1}")
                params.append(address)
            
            if not update_fields:
                return {"status": "error", "message": "No fields to update"}
            
            params.append(self.__customer_id)
            
            query = f"UPDATE customers SET {', '.join(update_fields)} WHERE customer_id = :{len(params)}"
            
            self.__db.execute_update(query, tuple(params))
            
            return {
                "status": "success",
                "message": "Profile updated successfully"
            }
            
        except ValueError as e:
            return {
                "status": "error",
                "message": f"Validation error: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Update failed: {str(e)}"
            }
    
    def _validate_registration(self):
        """
        Private method to validate all customer details before registration.
        """
        if not self.__first_name or len(self.__first_name) < 2:
            raise ValueError("First name must be at least 2 characters")
        
        if not self.__last_name or len(self.__last_name) < 2:
            raise ValueError("Last name must be at least 2 characters")
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, self.__email):
            raise ValueError("Invalid email format")
        
        if not self.__phone or len(self.__phone) < 10:
            raise ValueError("Phone number must be at least 10 digits")
        
        if not self.__address or len(self.__address) < 5:
            raise ValueError("Address must be at least 5 characters")
        
        if not self.__id_number or len(self.__id_number) < 5:
            raise ValueError("ID number is required and must be valid")
        
        if not self.__date_of_birth:
            raise ValueError("Date of birth is required")
    
    def __str__(self) -> str:
        """String representation of Customer"""
        return f"Customer(ID: {self.__customer_id}, Name: {self.__first_name} {self.__last_name}, Email: {self.__email})"
