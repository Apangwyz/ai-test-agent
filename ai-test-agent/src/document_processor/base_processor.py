from abc import ABC, abstractmethod
import logging

class BaseDocumentProcessor(ABC):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    @abstractmethod
    def process(self, file_path):
        """
        Process a document file and return its content
        """
        pass
    
    @abstractmethod
    def extract_structure(self, content):
        """
        Extract structured information from the document content
        """
        pass
    
    def validate_file(self, file_path):
        """
        Validate if the file is supported by this processor
        """
        return True