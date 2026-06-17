"""
DatabaseManager - Singleton class for Oracle Database Operations
Handles all database connections and queries using OOP principles
"""

import cx_Oracle
from typing import List, Tuple, Dict, Optional
import logging
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Singleton DatabaseManager class for managing Oracle database operations.
    Implements Encapsulation and Exception Handling.
    """
    
    _instance = None
    _connection = None
    
    def __new__(cls):
        """Ensure only one instance of DatabaseManager exists (Singleton Pattern)"""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize DatabaseManager with Oracle connection parameters"""
        if self._initialized:
            return
        
        # Database Configuration (Private - Encapsulation)
        self.__host = 'localhost'
        self.__port = 1521
        self.__service_name = 'xe'
        self.__username = 'system'
        self.__password = 'oracle'
        
        self._initialized = True
        self.__connect_database()
    
    def __connect_database(self):
        """
        Private method to establish Oracle database connection.
        Uses encapsulation to hide connection details.
        """
        try:
            dsn = cx_Oracle.makedsn(
                self.__host, 
                self.__port, 
                service_name=self.__service_name
            )
            
            self._connection = cx_Oracle.connect(
                user=self.__username,
                password=self.__password,
                dsn=dsn
            )
            
            logger.info("Database connection established successfully")
            
        except cx_Oracle.DatabaseError as e:
            logger.error(f"Database connection failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during database connection: {e}")
            raise
    
    @contextmanager
    def get_cursor(self):
        """
        Context manager for database cursor operations.
        Ensures proper resource cleanup (Abstraction).
        """
        cursor = self._connection.cursor()
        try:
            yield cursor
            self._connection.commit()
        except Exception as e:
            self._connection.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            cursor.close()
    
    def execute_query(self, query: str, params: Tuple = None) -> List[Tuple]:
        """
        Execute SELECT query and return results.
        
        Args:
            query: SQL SELECT query
            params: Query parameters (tuple)
            
        Returns:
            List of tuples containing query results
        """
        try:
            with self.get_cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_query_dict(self, query: str, params: Tuple = None) -> List[Dict]:
        """
        Execute SELECT query and return results as list of dictionaries.
        
        Args:
            query: SQL SELECT query
            params: Query parameters (tuple)
            
        Returns:
            List of dictionaries containing query results
        """
        try:
            with self.get_cursor() as cursor:
                cursor.rowfactory = lambda *args: dict(zip([d[0] for d in cursor.description], args))
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_update(self, query: str, params: Tuple = None) -> int:
        """
        Execute INSERT, UPDATE, or DELETE query.
        
        Args:
            query: SQL INSERT/UPDATE/DELETE query
            params: Query parameters (tuple)
            
        Returns:
            Number of rows affected
        """
        try:
            with self.get_cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Update execution failed: {e}")
            raise
    
    def call_procedure(self, proc_name: str, params: Tuple) -> List:
        """
        Call Oracle stored procedure.
        
        Args:
            proc_name: Name of stored procedure
            params: Procedure parameters
            
        Returns:
            Procedure output parameters
        """
        try:
            with self.get_cursor() as cursor:
                cursor.callproc(proc_name, params)
                return params
        except Exception as e:
            logger.error(f"Procedure call failed: {e}")
            raise
    
    def get_sequence_value(self, seq_name: str) -> int:
        """
        Get next sequence value from Oracle.
        
        Args:
            seq_name: Name of sequence
            
        Returns:
            Next sequence value
        """
        try:
            query = f"SELECT {seq_name}.NEXTVAL FROM dual"
            result = self.execute_query(query)
            return result[0][0] if result else None
        except Exception as e:
            logger.error(f"Sequence retrieval failed: {e}")
            raise
    
    def close_connection(self):
        """Close database connection"""
        try:
            if self._connection:
                self._connection.close()
                logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing connection: {e}")
    
    def __del__(self):
        """Destructor to ensure connection is closed"""
        self.close_connection()