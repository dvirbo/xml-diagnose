import logging

from processors.xml_diagnose import XMLDiagnosePipeline

logging.basicConfig(level=logging.INFO)

def main(directory: str) -> None:
    """Main entry point"""
    logging.info(f"Starting XML diagnosis pipeline for directory: {directory}")
    
    pipeline = XMLDiagnosePipeline(directory)
    result = pipeline.run()
    
    logging.info("Processing completed.")


if __name__ == "__main__":
    INPUT_DIR = "C:\\Users\\dvirbo\\Desktop\\mizrahi\\documents_20250527"
    main(INPUT_DIR)
    
    #TODO: Add dummy data into the DB to test the pipeline