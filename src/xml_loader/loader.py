from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Dict, Any

from pydantic import ValidationError

from src.model import Record
from src.xml_loader._parser import _parse_dcndl_xml


def load_xml(path: Path) -> List[Record]:
    """
    Parses a DC-NDL (Simple) XML file and returns a list of validated Record objects.
    """
    if not path.is_file():
        raise FileNotFoundError(f"XML file not found at path: {path}")

    validated_records: List[Record] = []
    error_count = 0

    def handle_record(record_dict: Dict[str, Any]) -> None:
        nonlocal error_count
        try:
            # Validate the dictionary and create the strict Record model
            final_record = Record.model_validate(record_dict)
            validated_records.append(final_record)
        except ValidationError as e:
            error_count += 1
            if error_count < 10:
                logging.warning(f"Skipping a record due to validation error: {e}")

    logging.info(f"Starting XML parsing for: {path}")
    _parse_dcndl_xml(str(path), handle_record)
    logging.info(f"Finished parsing. Found {len(validated_records)} valid records.")
    if error_count > 0:
        logging.warning(f"Skipped {error_count} records due to validation errors.")

    return validated_records
