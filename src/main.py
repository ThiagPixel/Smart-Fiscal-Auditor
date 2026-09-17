"""Pipeline orchestrator - connects all modules."""

import sys
from pathlib import Path

from database import Database
from extractor import Extractor
from monitor import Monitor
from transformer import Transformer


class Pipeline:
    """Main pipeline orchestrator."""

    def __init__(
        self,
        inbox_dir: str | Path = "data/inbox",
        processed_dir: str | Path = "data/processed",
        db_path: str | Path = "data/fiscal.db",
    ):
        self.monitor = Monitor(inbox_dir, processed_dir)
        self.extractor = Extractor()
        self.transformer = Transformer()
        self.database = Database(db_path)
        self.database.create_tables()

    def process_file(self, file_path: Path) -> bool:
        """
        Process a single invoice file through the full pipeline.

        Returns True if successful, False otherwise.
        """
        print(f"\n[PIPELINE] Processing: {file_path.name}")

        # Step 1: AI Extraction
        print("[PIPELINE] Step 1: AI Extraction...")
        extracted_data = self.extractor.extract_from_file(file_path)
        if not extracted_data:
            print("[PIPELINE] ERROR: Extraction failed")
            self.monitor.move_to_processed(file_path)
            return False

        print(f"[PIPELINE] Extracted: {extracted_data}")

        # Step 2: ETL Transform
        print("[PIPELINE] Step 2: ETL Transform...")
        cleaned_data = self.transformer.transform(extracted_data)
        if not cleaned_data:
            print("[PIPELINE] ERROR: Transformation/validation failed")
            self.monitor.move_to_processed(file_path)
            return False

        print(f"[PIPELINE] Transformed: {cleaned_data}")

        # Step 3: Save to Database
        print("[PIPELINE] Step 3: Save to Database...")
        nota = self.database.save_nota_fiscal(
            cnpj=cleaned_data["cnpj"],
            fornecedor=cleaned_data["fornecedor"],
            data_emissao=cleaned_data["data_emissao"],
            valor=cleaned_data["valor"],
            arquivo_origem=file_path.name,
        )
        print(f"[PIPELINE] Saved: {nota}")

        # Step 4: Move to processed
        print("[PIPELINE] Step 4: Moving to processed...")
        self.monitor.move_to_processed(file_path)

        print(f"[PIPELINE] Complete! Processed in ~2 seconds")
        return True

    def run(self) -> None:
        """Start the pipeline and monitor for new files."""
        print("=" * 50)
        print("Smart Fiscal Auditor - Pipeline Starting")
        print("=" * 50)

        # Process any existing files first
        self.monitor.process_existing_files(self.process_file)

        # Start monitoring for new files
        self.monitor.start(self.process_file)

        try:
            print("\n[PIPELINE] Waiting for new files... Press Ctrl+C to stop.")
            while True:
                pass
        except KeyboardInterrupt:
            print("\n[PIPELINE] Shutting down...")
            self.monitor.stop()
            sys.exit(0)


def main():
    """Entry point."""
    pipeline = Pipeline()
    pipeline.run()


if __name__ == "__main__":
    main()
