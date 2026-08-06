"""Sherlock Result Module

This module defines various objects for recording the results of queries.
"""
from enum import Enum


class QueryStatus(Enum):
    """Query Status Enumeration.

    Describes status of query about a given username.
    """
    CLAIMED   = "Claimed"   # Username Detected
    AVAILABLE = "Available" # Username Not Detected
    UNKNOWN   = "Unknown"   # Error Occurred While Trying To Detect Username
    ILLEGAL   = "Illegal"   # Username Not Allowable For This Site
    WAF       = "WAF"       # Request blocked by WAF (i.e. Cloudflare)

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
    def __init__(self, username, site_name, site_url_user, status,
                 query_time=None, context=None):
        """Create Query Result Object.

        Contains information about a specific method of detecting usernames on
        a given type of web sites.

        Keyword Arguments:
        self                   -- This object.
        username               -- String indicating username that query result
                                  was about.
        site_name              -- String which identifies site.
        site_url_user          -- String containing URL for username on site.
                                  NOTE:  The site may or may not exist:  this
                                         just indicates what the name would
                                         be, if it existed.
        status                 -- Enumeration of type QueryStatus() indicating
                                  the status of the query.
        query_time             -- Time (in seconds) required to perform query.
                                  Default of None.
        context                -- String indicating any additional context
                                  about the query.  For example, if there was
                                  an error, this might indicate the type of
                                  error that occurred.
                                  Default of None.

        Return Value:
        Nothing.
        """

        self.username      = username
        self.site_name     = site_name
        self.site_url_user = site_url_user
        self.status        = status
        self.query_time    = query_time
        self.context       = context

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
            # There is extra context information available about the results.
            # Append it to the normal response text.
            status += f" ({self.context})"

        return status
    
    def to_dict(self):
        """
        Converts the QueryResult object to a dictionary format suitable for GUI parsing.
        This prevents the GUI from needing to access raw object attributes directly.
        """
        return {
            "username": self.username,
            "site_name": self.site_name,
            "site_url_user": self.site_url_user,
            "status": str(self.status),
            "query_time": self.query_time,
            "context": self.context,
            "ui_color_code": self.get_ui_color_code()
        }
    
    def get_ui_color_code(self):
        """
        Returns a hex color code based on the query status for UI representation.
        Green for Found, Red for Not Found, Yellow for Unknown/Errors.
        """

        if self.status.name == "CLAIMED":
            return "#28a745" # Success Green
        elif self.status.name == "AVAILABLE":
            return "#dc3545" # Danger Red
        elif self.status.name == "UNKNOWN":
            return "#ffc107" # Warning Yellow
        else:
            return "#6c757d" # Secondary Gray for other statuses (ILLEGAL, WAF, etc.)
