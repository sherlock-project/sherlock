"""Sherlock Result Module

This module defines various objects for recording the results of queries.
"""
from enum import Enum


class QueryStatus(Enum):
    """Query Status Enumeration.

    Describes status of query about a given username.
    """
    CLAIMED   = "Claimed"   #Username Detected
    AVAILABLE = "Available" #Username Not Detected
    UNKNOWN   = "Unknown"   #Error Occurred While Trying To Detect Username
    ILLEGAL   = "Illegal"   #Username Not Allowable For This Site

    def __str__(self):
        """Convert Object To String.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        Nicely formatted string to get information about this object.
        """
        return self.value

class QueryResult():
    """Query Result Object.

    Describes result of query about a given username.
    """
    def __init__(self, status, context=None):
        """Create Query Result Object.

        Contains information about a specific method of detecting usernames on
        a given type of web sites.

        Keyword Arguments:
        self                   -- This object.
        status                 -- Enumeration of type QueryStatus() indicating
                                  the status of the query.
        context                -- String indicating any additional context
                                  about the query.  For example, if there was
                                  an error, this might indicate the type of
                                  error that occurred.
                                  Default of None.

        Return Value:
        Nothing.
        """

        self.status  = status
        self.context = context

        return

    def __str__(self):
        """Convert Object To String.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        Nicely formatted string to get information about this object.
        """
        status = str(self.status)
        if self.context is not None:
            #There is extra context information available about the results.
            #Append it to the normal response text.
            status += f" ({self.context})"

        return status
