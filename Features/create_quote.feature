Feature: Create Vehicle Insurance Quote

  As an insurance customer
  I want to create a vehicle insurance quote
  So that I can obtain an insurance quotation

  @smoke
  Scenario: Create vehicle insurance quote with valid data
    Given I am on the application landing page
    When I create a quote using test data "TC001"
    Then the quote should be sent successfully
    And the Send Quote fields should match the selected test data

  @recovery
  Scenario: Recover a missing required field before filling Send Quote
    Given I am on the application landing page
    When I fill a quote using test data "TC001" without submitting
    And a required field in a completed form is cleared
    Then Send Quote should request a price option
    When I retry filling Send Quote using the selected test data
    Then the Send Quote fields should match the selected test data
    And recovery should report the missing required field
