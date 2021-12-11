"""Sherlock Tests

This module contains various tests.
"""
from tests.base import SherlockBaseTest
import unittest


class SherlockDetectTests(SherlockBaseTest):
    def test_detect_true_via_message(self):
        """Test Username Does Exist (Via Message).

        This test ensures that the "message" detection mechanism of
        ensuring that a Username does exist works properly.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        Nothing.
        Will trigger an assert if detection mechanism did not work as expected.
        """

        site = "BinarySearch"
        site_data = self.site_data_all[site]

        #Ensure that the site's detection method has not changed.
        self.assertEqual("message", site_data["errorType"])

        self.username_check([site_data["username_claimed"]],
                            [site],
                            exist_check=True
                           )

        return

    def test_detect_false_via_message(self):
        """Test Username Does Not Exist (Via Message).

        This test ensures that the "message" detection mechanism of
        ensuring that a Username does *not* exist works properly.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        Nothing.
        Will trigger an assert if detection mechanism did not work as expected.
        """

        site = "BinarySearch"
        site_data = self.site_data_all[site]

        #Ensure that the site's detection method has not changed.
        self.assertEqual("message", site_data["errorType"])

        self.username_check([site_data["username_unclaimed"]],
                            [site],
                            exist_check=False
                           )

        return

    def test_detect_true_via_status_code(self):
        """Test Username Does Exist (Via Status Code).

        This test ensures that the "status code" detection mechanism of
        ensuring that a Username does exist works properly.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        Nothing.
        Will trigger an assert if detection mechanism did not work as expected.
        """

        site = "Pinterest"
        site_data = self.site_data_all[site]

        #Ensure that the site's detection method has not changed.
        self.assertEqual("status_code", site_data["errorType"])

        self.username_check([site_data["username_claimed"]],
                            [site],
                            exist_check=True
                           )

        return

    def test_detect_false_via_status_code(self):
        """Test Username Does Not Exist (Via Status Code).

        This test ensures that the "status code" detection mechanism of
        ensuring that a Username does *not* exist works properly.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        Nothing.
        Will trigger an assert if detection mechanism did not work as expected.
        """

        site = "Pinterest"
        site_data = self.site_data_all[site]

        #Ensure that the site's detection method has not changed.
        self.assertEqual("status_code", site_data["errorType"])

        self.username_check([site_data["username_unclaimed"]],
                            [site],
                            exist_check=False
                           )

        return

    def test_detect_true_via_response_url(self):
        """Test Username Does Exist (Via Response URL).

        This test ensures that the "response URL" detection mechanism of
        ensuring that a Username does exist works properly.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        Nothing.
        Will trigger an assert if detection mechanism did not work as expected.
        """

        site = "VK"
        site_data = self.site_data_all[site]

        #Ensure that the site's detection method has not changed.
        self.assertEqual("response_url", site_data["errorType"])

        self.username_check([site_data["username_claimed"]],
                            [site],
                            exist_check=True
                           )

        return

    def test_detect_false_via_response_url(self):
        """Test Username Does Not Exist (Via Response URL).

        This test ensures that the "response URL" detection mechanism of
        ensuring that a Username does *not* exist works properly.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        Nothing.
        Will trigger an assert if detection mechanism did not work as expected.
        """

        site = "VK"
        site_data = self.site_data_all[site]

        #Ensure that the site's detection method has not changed.
        self.assertEqual("response_url", site_data["errorType"])

        self.username_check([site_data["username_unclaimed"]],
                            [site],
                            exist_check=False
                           )

        return


class SherlockSiteCoverageTests(SherlockBaseTest):
    def test_coverage_false_via_response_url(self):
        """Test Username Does Not Exist Site Coverage (Via Response URL).

        This test checks all sites with the "response URL" detection mechanism
        to ensure that a Username that does not exist is reported that way.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        Nothing.
        Will trigger an assert if detection mechanism did not work as expected.
        """

        self.detect_type_check("response_url", exist_check=False)

        return

    def test_coverage_true_via_response_url(self):
        """Test Username Does Exist Site Coverage (Via Response URL).

        This test checks all sites with the "response URL" detection mechanism
        to ensure that a Username that does exist is reported that way.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        Nothing.
        Will trigger an assert if detection mechanism did not work as expected.
        """

        self.detect_type_check("response_url", exist_check=True)

        return

    def test_coverage_false_via_status(self):
        """Test Username Does Not Exist Site Coverage (Via HTTP Status).

        This test checks all sites with the "HTTP Status" detection mechanism
        to ensure that a Username that does not exist is reported that way.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        Nothing.
        Will trigger an assert if detection mechanism did not work as expected.
        """

        self.detect_type_check("status_code", exist_check=False)

        return

    def test_coverage_true_via_status(self):
        """Test Username Does Exist Site Coverage (Via HTTP Status).

        This test checks all sites with the "HTTP Status" detection mechanism
        to ensure that a Username that does exist is reported that way.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        Nothing.
        Will trigger an assert if detection mechanism did not work as expected.
        """

        self.detect_type_check("status_code", exist_check=True)

        return

    def test_coverage_false_via_message(self):
        """Test Username Does Not Exist Site Coverage (Via Error Message).

        This test checks all sites with the "Error Message" detection mechanism
        to ensure that a Username that does not exist is reported that way.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        Nothing.
        Will trigger an assert if detection mechanism did not work as expected.
        """

        self.detect_type_check("message", exist_check=False)

        return

    def test_coverage_true_via_message(self):
        """Test Username Does Exist Site Coverage (Via Error Message).

        This test checks all sites with the "Error Message" detection mechanism
        to ensure that a Username that does exist is reported that way.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        Nothing.
        Will trigger an assert if detection mechanism did not work as expected.
        """

        self.detect_type_check("message", exist_check=True)

        return

    def test_coverage_total(self):
        """Test Site Coverage Is Total.

        This test checks that all sites have test data available.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        Nothing.
        Will trigger an assert if we do not have total coverage.
        """

        self.coverage_total_check()

        return
