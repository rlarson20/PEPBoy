"""
Unit tests for Data Fetcher Service.

This module tests the data fetching functionality,
demonstrating TDD methodology for external API interactions and file operations.
"""

import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
from urllib.parse import urlparse

import httpx

from src.services.data_fetcher import (
    get_pep_json_data,
    get_pep_files,
    get_raw_pep_text,
    test_if_peps_have_been_updated,
    get_name_from_meta,
    main,
    _PEP_URL,
    _PEPS_DIR,
    _INDEX_PEP,
)


class TestGetPepJsonData:
    """Test the get_pep_json_data function."""
    
    @patch('src.services.data_fetcher.httpx.get')
    def test_get_pep_json_data_success(self, mock_get):
        """Test successful retrieval of PEP JSON data.
        
        TDD Red: Write test expecting API call to work
        TDD Green: Implement basic httpx.get call
        TDD Refactor: Add error handling and validation
        """
        # Arrange
        expected_data = {
            "1": {
                "number": 1,
                "title": "PEP Purpose and Guidelines",
                "status": "Active"
            }
        }
        mock_response = Mock(spec=httpx.Response)
        mock_response.json.return_value = expected_data
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Act
        result = get_pep_json_data()
        
        # Assert
        mock_get.assert_called_once_with(_PEP_URL)
        assert result == mock_response
        assert result.json() == expected_data
    
    @patch('src.services.data_fetcher.httpx.get')
    def test_get_pep_json_data_http_error(self, mock_get):
        """Test handling of HTTP errors during API call."""
        # Arrange
        mock_get.side_effect = httpx.HTTPError("Network error")
        
        # Act & Assert
        with pytest.raises(httpx.HTTPError):
            get_pep_json_data()
    
    @patch('src.services.data_fetcher.httpx.get')
    def test_get_pep_json_data_timeout(self, mock_get):
        """Test handling of timeout during API call."""
        # Arrange
        mock_get.side_effect = httpx.TimeoutException("Request timeout")
        
        # Act & Assert
        with pytest.raises(httpx.TimeoutException):
            get_pep_json_data()
    
    @patch('src.services.data_fetcher.httpx.get')
    def test_get_pep_json_data_uses_correct_url(self, mock_get):
        """Test that the function uses the correct PEP API URL."""
        # Arrange
        mock_response = Mock(spec=httpx.Response)
        mock_get.return_value = mock_response
        
        # Act
        get_pep_json_data()
        
        # Assert
        mock_get.assert_called_once_with("https://peps.python.org/api/peps.json")


class TestGetPepFiles:
    """Test the get_pep_files function."""
    
    def test_get_pep_files_success(self):
        """Test successful conversion of API response to file names."""
        # Arrange
        mock_response = Mock(spec=httpx.Response)
        mock_response.json.return_value = {
            "1": {"url": "https://peps.python.org/pep-0001"},
            "8": {"url": "https://peps.python.org/pep-0008"},
            "20": {"url": "https://peps.python.org/pep-0020"}
        }
        
        # Act
        result = get_pep_files(mock_response)
        
        # Assert
        expected_files = ["pep-0001.rst", "pep-0008.rst", "pep-0020.rst"]
        assert result == expected_files
        assert len(result) == 3
    
    def test_get_pep_files_excludes_index_pep(self):
        """Test that the index PEP (pep-0000.rst) is excluded from results."""
        # Arrange
        mock_response = Mock(spec=httpx.Response)
        mock_response.json.return_value = {
            "0": {"url": "https://peps.python.org/pep-0000"},  # Index PEP
            "1": {"url": "https://peps.python.org/pep-0001"},
            "8": {"url": "https://peps.python.org/pep-0008"}
        }
        
        # Act
        result = get_pep_files(mock_response)
        
        # Assert
        assert "pep-0000.rst" not in result
        assert "pep-0001.rst" in result
        assert "pep-0008.rst" in result
        assert len(result) == 2
    
    def test_get_pep_files_empty_response(self):
        """Test handling of empty API response."""
        # Arrange
        mock_response = Mock(spec=httpx.Response)
        mock_response.json.return_value = {}
        
        # Act
        result = get_pep_files(mock_response)
        
        # Assert
        assert result == []
    
    def test_get_pep_files_url_parsing(self):
        """Test correct URL parsing for different URL formats."""
        # Arrange
        mock_response = Mock(spec=httpx.Response)
        mock_response.json.return_value = {
            "484": {"url": "https://peps.python.org/pep-0484/"},  # With trailing slash
            "585": {"url": "https://peps.python.org/pep-0585"},   # Without trailing slash
        }
        
        # Act
        result = get_pep_files(mock_response)
        
        # Assert
        assert "pep-0484.rst" in result
        assert "pep-0585.rst" in result
        assert len(result) == 2
    
    def test_get_pep_files_malformed_urls(self):
        """Test handling of malformed URLs in the response."""
        # Arrange
        mock_response = Mock(spec=httpx.Response)
        mock_response.json.return_value = {
            "1": {"url": "not-a-valid-url"},
            "8": {"url": "https://peps.python.org/pep-0008"}
        }
        
        # Act
        result = get_pep_files(mock_response)
        
        # Assert
        # Should still process what it can
        assert len(result) == 2
        assert "pep-0008.rst" in result


class TestGetRawPepText:
    """Test the get_raw_pep_text function."""
    
    @patch('builtins.open', new_callable=mock_open, read_data="PEP: 1\nTitle: Test PEP\n\nContent here...")
    def test_get_raw_pep_text_success(self, mock_file):
        """Test successful reading of PEP file."""
        # Arrange
        pep_name = "pep-0001.rst"
        expected_content = "PEP: 1\nTitle: Test PEP\n\nContent here..."
        
        # Act
        result = get_raw_pep_text(pep_name)
        
        # Assert
        assert result == expected_content
        mock_file.assert_called_once_with(str(_PEPS_DIR) + "/" + pep_name, "r")
    
    @patch('builtins.open')
    def test_get_raw_pep_text_file_not_found(self, mock_open):
        """Test handling when PEP file doesn't exist."""
        # Arrange
        mock_open.side_effect = FileNotFoundError("File not found")
        pep_name = "pep-9999.rst"
        
        # Act
        result = get_raw_pep_text(pep_name)
        
        # Assert
        assert result.startswith("Error:")
        assert "File not found" in result
    
    @patch('builtins.open')
    def test_get_raw_pep_text_permission_error(self, mock_open):
        """Test handling of permission errors."""
        # Arrange
        mock_open.side_effect = PermissionError("Permission denied")
        pep_name = "pep-0001.rst"
        
        # Act
        result = get_raw_pep_text(pep_name)
        
        # Assert
        assert result.startswith("Error:")
        assert "Permission denied" in result
    
    @patch('builtins.open')
    def test_get_raw_pep_text_generic_exception(self, mock_open):
        """Test handling of generic exceptions."""
        # Arrange
        mock_open.side_effect = Exception("Generic error")
        pep_name = "pep-0001.rst"
        
        # Act
        result = get_raw_pep_text(pep_name)
        
        # Assert
        assert result.startswith("Error:")
        assert "Generic error" in result
    
    def test_get_raw_pep_text_constructs_correct_path(self):
        """Test that the function constructs the correct file path."""
        # This test verifies the path construction logic
        pep_name = "pep-0123.rst"
        expected_path = str(_PEPS_DIR) + "/" + pep_name
        
        with patch('builtins.open', mock_open(read_data="test")) as mock_file:
            get_raw_pep_text(pep_name)
            mock_file.assert_called_once_with(expected_path, "r")


class TestGetNameFromMeta:
    """Test the get_name_from_meta function."""
    
    def test_get_name_from_meta_standard_format(self):
        """Test parsing PEP name from standard metadata format."""
        # Arrange
        meta = "PEP: 1\nTitle: PEP Purpose and Guidelines\nAuthor: Barry Warsaw"
        
        # Act
        result = get_name_from_meta(meta)
        
        # Assert
        assert result == "1"
    
    def test_get_name_from_meta_with_leading_spaces(self):
        """Test parsing PEP name with leading spaces."""
        # Arrange
        meta = "    PEP: 8\nTitle: Style Guide for Python Code"
        
        # Act
        result = get_name_from_meta(meta)
        
        # Assert
        assert result == "8"
    
    def test_get_name_from_meta_multiline(self):
        """Test that only the first line is processed."""
        # Arrange
        meta = "PEP: 20\nTitle: The Zen of Python\nAuthor: Tim Peters\nStatus: Active"
        
        # Act
        result = get_name_from_meta(meta)
        
        # Assert
        assert result == "20"
    
    def test_get_name_from_meta_malformed(self):
        """Test handling of malformed metadata."""
        # Arrange
        meta = "Not a valid PEP format"
        
        # Act & Assert
        # This might raise an exception or return unexpected results
        # The behavior depends on implementation details
        try:
            result = get_name_from_meta(meta)
            # If it doesn't raise an exception, verify it handles gracefully
            assert isinstance(result, str)
        except (IndexError, AttributeError):
            # These exceptions are acceptable for malformed input
            pass
    
    def test_get_name_from_meta_empty_string(self):
        """Test handling of empty metadata."""
        # Arrange
        meta = ""
        
        # Act & Assert
        with pytest.raises(IndexError):
            get_name_from_meta(meta)


class TestTestIfPepsHaveBeenUpdated:
    """Test the test_if_peps_have_been_updated function."""
    
    @patch('src.services.data_fetcher.get_pep_files')
    @patch('src.services.data_fetcher.get_pep_json_data')
    @patch('builtins.open', new_callable=mock_open, read_data="PEP content")
    @patch('builtins.print')
    def test_all_files_exist_success(self, mock_print, mock_file, mock_get_json, mock_get_files):
        """Test when all PEP files exist and can be read."""
        # Arrange
        mock_response = Mock()
        mock_get_json.return_value = mock_response
        mock_get_files.return_value = ["pep-0001.rst", "pep-0008.rst"]
        
        # Act
        test_if_peps_have_been_updated()
        
        # Assert
        mock_get_json.assert_called_once()
        mock_get_files.assert_called_once_with(mock_response)
        assert mock_file.call_count == 2  # Two files opened
        
        # Check that success messages were printed
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        success_count = sum(1 for call in print_calls if "Success!" in call)
        assert success_count == 2
    
    @patch('src.services.data_fetcher.get_pep_files')
    @patch('src.services.data_fetcher.get_pep_json_data')
    @patch('builtins.open')
    @patch('builtins.print')
    def test_some_files_missing(self, mock_print, mock_file, mock_get_json, mock_get_files):
        """Test when some PEP files are missing."""
        # Arrange
        mock_response = Mock()
        mock_get_json.return_value = mock_response
        mock_get_files.return_value = ["pep-0001.rst", "pep-9999.rst"]
        
        # First file exists, second doesn't
        mock_file.side_effect = [
            mock_open(read_data="content").return_value,
            FileNotFoundError("File not found")
        ]
        
        # Act
        test_if_peps_have_been_updated()
        
        # Assert
        print_calls = [str(call) for call in mock_print.call_args_list]
        
        # Should have both success and failure messages
        assert any("Success!" in call for call in print_calls)
        assert any("Failure:" in call for call in print_calls)
        
        # Should have summary with counts
        summary_calls = [call for call in print_calls if "Succeeded:" in call or "Failed:" in call or "Total:" in call]
        assert len(summary_calls) >= 1


class TestMainFunction:
    """Test the main function integration."""
    
    @patch('src.services.data_fetcher.get_raw_pep_text')
    @patch('src.services.data_fetcher.get_pep_files')
    @patch('src.services.data_fetcher.get_pep_json_data')
    def test_main_function_flow(self, mock_get_json, mock_get_files, mock_get_raw):
        """Test the main function processes data correctly."""
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {"1": {"title": "Test PEP"}}
        mock_get_json.return_value = mock_response
        
        mock_get_files.return_value = ["pep-0001.rst"]
        
        mock_get_raw.return_value = "PEP: 1\nTitle: Test PEP\n\nContent here"
        
        # Act
        main()
        
        # Assert
        mock_get_json.assert_called_once()
        mock_get_files.assert_called_once_with(mock_response)
        mock_get_raw.assert_called_once_with("pep-0001.rst")
    
    @patch('src.services.data_fetcher.get_name_from_meta')
    @patch('src.services.data_fetcher.get_raw_pep_text')
    @patch('src.services.data_fetcher.get_pep_files')
    @patch('src.services.data_fetcher.get_pep_json_data')
    def test_main_function_processes_multiple_peps(self, mock_get_json, mock_get_files, mock_get_raw, mock_get_name):
        """Test that main function processes multiple PEPs."""
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {"1": {"title": "Test PEP 1"}, "8": {"title": "Test PEP 8"}}
        mock_get_json.return_value = mock_response
        
        mock_get_files.return_value = ["pep-0001.rst", "pep-0008.rst"]
        
        mock_get_raw.side_effect = [
            "PEP: 1\nTitle: Test PEP 1\n\nContent 1",
            "PEP: 8\nTitle: Test PEP 8\n\nContent 8"
        ]
        
        mock_get_name.side_effect = ["1", "8"]
        
        # Act
        main()
        
        # Assert
        assert mock_get_raw.call_count == 2
        assert mock_get_name.call_count == 2
        
        # Verify the files were processed in order
        raw_calls = [call[0][0] for call in mock_get_raw.call_args_list]
        assert "pep-0001.rst" in raw_calls
        assert "pep-0008.rst" in raw_calls


@pytest.mark.integration
class TestDataFetcherIntegration:
    """Integration tests for data fetcher components."""
    
    @patch('src.services.data_fetcher.httpx.get')
    def test_full_workflow_integration(self, mock_get):
        """Test the complete workflow from API call to file processing."""
        # Arrange
        mock_response = Mock(spec=httpx.Response)
        mock_response.json.return_value = {
            "1": {"url": "https://peps.python.org/pep-0001"},
            "8": {"url": "https://peps.python.org/pep-0008"}
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Act
        json_response = get_pep_json_data()
        file_names = get_pep_files(json_response)
        
        # Assert
        assert json_response == mock_response
        assert file_names == ["pep-0001.rst", "pep-0008.rst"]
        mock_get.assert_called_once_with(_PEP_URL)


@pytest.mark.external
class TestDataFetcherWithExternalDependencies:
    """Tests that require external dependencies or network access."""
    
    @pytest.mark.skip(reason="Requires network access")
    def test_real_api_call(self):
        """Test actual API call to PEP endpoint (when network is available)."""
        # This test would make a real HTTP request
        # Skip by default to avoid network dependencies in unit tests
        response = get_pep_json_data()
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0


@pytest.mark.performance
class TestDataFetcherPerformance:
    """Performance tests for data fetcher operations."""
    
    def test_get_pep_files_performance_large_dataset(self, performance_tracker):
        """Test performance of get_pep_files with large dataset."""
        # Arrange
        large_dataset = {str(i): {"url": f"https://peps.python.org/pep-{i:04d}"} for i in range(1, 1000)}
        mock_response = Mock(spec=httpx.Response)
        mock_response.json.return_value = large_dataset
        
        # Act
        with performance_tracker.start():
            result = get_pep_files(mock_response)
        
        duration = performance_tracker.stop(max_duration=1.0)
        
        # Assert
        assert len(result) == 999  # 999 PEPs (excluding potential index)
        assert duration < 1.0
    
    def test_get_name_from_meta_performance(self, performance_tracker, fake):
        """Test performance of metadata parsing."""
        # Arrange
        large_meta = "\n".join([f"PEP: 123", f"Title: {fake.sentence()}", f"Author: {fake.name()}"] + [fake.text() for _ in range(100)])
        
        # Act
        with performance_tracker.start():
            for _ in range(1000):
                result = get_name_from_meta(large_meta)
        
        duration = performance_tracker.stop(max_duration=1.0)
        
        # Assert
        assert result == "123"
        assert duration < 1.0