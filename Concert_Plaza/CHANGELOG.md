# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
---

## [0.4] - 2024-05-09

### Fixed
- maps_bot: url prefixes

## [0.3] - 2024-03-19
### Added
- tests: velodrome.html (html file for unit testing)
### Changed
- maps_scraper: New message for search_by_country task
- test_maps_bot: New tests using mocks
- maps_bot: Changes in load_files and search_by_country functions
## [0.2] - 2023-12-06

### Added

- files: Demographic database
- tests: test_country_search (for unit testing)

### Changed

- maps_bot: New function named search_by_country that allows web scraping in important cities of a country
- maps_scrapper: Search by country is a new background task
- main: The code lines to import 'maps_scraper' and '__version__' have been modified to avoid errors
- send_data_to_kinesis: The code line to import 'settings' has been modified to avoid errors
- maps_wrapper: The code line to import 'exceptions' has been modified to avoid errors
- depends: Regular Expressions changed in abbreviated_number_to_int function

## [Released]

## [0.1] - 2023-10-18

### Added

- general: Add typing to variables
- general: Pydantic models and validations
- general: Pydantic settings
- maps_scrapper: FastAPI router for maps_scrapper
- maps_scrapper: Google Maps url generator
- maps_scrapper: Fake HTTP headers generator
- maps_scrapper: Method to remove duplicates
- maps_scrapper: Read company's name
- maps_scrapper: Read user's score
- maps_scrapper: Read user's number of reviews
- maps_scrapper: Read company's address
- maps_scrapper: Read company's phone number
- maps_scrapper: Read company's website
- aws_kinesis: Class to work with data_streams
- aws_kinesis: Class to work with data_analytics
- aws_kinesis: function to manage batch records for data streams

### Changed

- general: Refactor project to three layer architecture
- maps_scrapper: httpx client timeout set to 10s by default
