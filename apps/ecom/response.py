from rest_framework.response import Response
from typing import Any, Dict, Optional
from rest_framework import status


class Codenco(Response):
    """
    A custom Response class that standardizes API responses with default messages based on HTTP methods.
    
    This class extends DRF's Response to provide consistent formatting for both
    success and error responses, with support for pagination and additional fields.
    """

    SUCCESS_STATUS = 'success'
    ERROR_STATUS = 'error'
    
    # Default success messages for different HTTP methods
    DEFAULT_SUCCESS_MESSAGES = {
        'GET': 'Data retrieved successfully',
        'POST': 'Data created successfully',
        'PUT': 'Data updated successfully',
        'PATCH': 'Data updated successfully',
        'DELETE': 'Data deleted successfully',
    }
    
    # Default error messages for different HTTP methods
    DEFAULT_ERROR_MESSAGES = {
        'GET': 'Failed to retrieve data',
        'POST': 'Failed to create data',
        'PUT': 'Failed to update data',
        'PATCH': 'Failed to update data',
        'DELETE': 'Failed to delete data',
    }
    
    def __init__(
        self,
        message: Optional[str] = None,
        data: Optional[Any] = None,
        pagination: Optional[Dict] = None,
        error: Optional[str] = None,
        status_code: int = status.HTTP_200_OK,
        request_method: Optional[str] = None,
        **extra_fields: Any
    ) -> None:
        """
        Initialize a new Codenco response.

        Args:
            message (str, optional): Custom response message
            data (Any, optional): The response payload
            pagination (Dict, optional): Pagination information
            error (str, optional): Error details for error responses
            status_code (int, optional): HTTP status code (default: 200)
            request_method (str, optional): HTTP request method
            **extra_fields: Additional fields to include in the response

        Example:
            >>> Codenco(data={"key": "value"}, request_method="GET")
            >>> Codenco("Custom message", error="Details", status_code=400, request_method="POST")
        """
        final_message = self._get_appropriate_message(
            message, 
            status_code, 
            request_method
        )
        
        response_data = self._build_response_data(
            message=final_message,
            data=data,
            pagination=pagination,
            error=error,
            status_code=status_code,
            extra_fields=extra_fields
        )
        super().__init__(data=response_data, status=status_code)

    def _get_appropriate_message(
        self,
        message: Optional[str],
        status_code: int,
        request_method: Optional[str]
    ) -> str:
        """
        Get the appropriate message based on the provided parameters.

        Args:
            message (str, optional): Custom message
            status_code (int): HTTP status code
            request_method (str, optional): HTTP request method

        Returns:
            str: Appropriate message for the response
        """
        if message is not None:
            return message
            
        if request_method is None:
            return "Operation completed successfully" if status_code < 400 else "Operation failed"
            
        method = request_method.upper()
        is_success = status_code < status.HTTP_400_BAD_REQUEST
        
        if is_success:
            return self.DEFAULT_SUCCESS_MESSAGES.get(
                method, 
                "Operation completed successfully"
            )
        return self.DEFAULT_ERROR_MESSAGES.get(
            method, 
            "Operation failed"
        )

    def _build_response_data(
        self,
        message: str,
        data: Optional[Any],
        pagination: Optional[Dict],
        error: Optional[str],
        status_code: int,
        extra_fields: Dict
    ) -> Dict:
        """
        Build the response data structure based on status code and provided parameters.

        Args:
            message (str): The response message
            data (Any): The response payload
            pagination (Dict): Pagination information
            error (str): Error details
            status_code (int): HTTP status code
            extra_fields (Dict): Additional fields to include

        Returns:
            Dict: Formatted response data
        """
        is_success = status_code < status.HTTP_400_BAD_REQUEST

        if is_success:
            return self._build_success_response(
                message=message,
                data=data,
                pagination=pagination,
                extra_fields=extra_fields
            )
        return self._build_error_response(message=message, error=error)

    @classmethod
    def _build_success_response(
        cls,
        message: str,
        data: Optional[Any],
        pagination: Optional[Dict],
        extra_fields: Dict
    ) -> Dict:
        """
        Build a success response structure.
        
        Args:
            message (str): The success message
            data (Any): The response payload
            pagination (Dict): Pagination information
            extra_fields (Dict): Additional fields to include

        Returns:
            Dict: Formatted success response
        """
        response = {
            'status': cls.SUCCESS_STATUS,
            'message': message,
            'data': data if data is not None else []
        }

        if pagination is not None:
            response['pagination'] = pagination

        if extra_fields:
            response.update(extra_fields)

        return response

    @classmethod
    def _build_error_response(
        cls, 
        message: str, 
        error: Optional[str]
    ) -> Dict:
        """
        Build an error response structure.
        
        Args:
            message (str): The error message
            error (str): Detailed error information

        Returns:
            Dict: Formatted error response
        """
        response = {
            'status': cls.ERROR_STATUS,
            'message': message
        }

        if error is not None:
            response['error'] = error

        return response
    
#=== Base Success Response ===#
def base_success_response(message, data=None, pagination=None, **extra_fields):
    response = {
        'status': 'success',
        'message': message,
    }
  
    response['data'] = data if data is not None else []

    if pagination is not None:
        response['pagination'] = pagination
        
    if extra_fields:
        response.update(extra_fields)

    return response

#=== Base Error Response ===#
def base_error_response(message, errors=None):
    response = {
        'status': 'error',
        'message': message,
    }
    
    if errors is not None:
        response['error'] = errors

    return response