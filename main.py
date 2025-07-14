import logging

from processors.xml_diagnose import XMLDiagnosePipeline



# Remove all handlers associated with the root logger
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    filename = 'logs/mizrahi.txt',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')

def main(directory: str) -> None:
    """Main entry point"""
    logging.info(f"Starting XML diagnosis pipeline for directory: {directory}")
    
    pipeline = XMLDiagnosePipeline(directory)
    result = pipeline.run()
    
    logging.info("Processing completed.")


if __name__ == "__main__":
    INPUT_DIR = "reports"
    main(INPUT_DIR)

    