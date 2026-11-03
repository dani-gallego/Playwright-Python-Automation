Feature: Create Vehicle Insurance Quote

  As an insurance customer
  I want to create a vehicle insurance quote
  So that I can obtain an insurance quotation

  @smoke
  Scenario: Create vehicle insurance quote with valid data
    Given I am on the application landing page
    When I create a quote using test data "TC001"
    Then I should be navigated to the send quote page
