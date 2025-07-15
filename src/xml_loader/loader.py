from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from pydantic import ValidationError

from src.xml_loader._parser import _parse_dcndl_xml
from src.xml_loader._schema import _Record
from src.model.record import Record


def load_xml(path: Path) -> List[Record]:
    """
    Parses a DC-NDL (Simple) XML file and returns a list of validated Record objects.
    """
    if not path.is_file():
        raise FileNotFoundError(f"XML file not found at path: {path}")

    validated_records: List[Record] = []
    error_count = 0

    def handle_record(private_record: _Record) -> None:
        nonlocal error_count
        try:
            final_record = _Record.to_public(private_record)
            validated_records.append(final_record)
        except (ValidationError, ValueError) as e:
            error_count += 1
            if error_count < 10:
                logging.warning(f"Skipping a record due to validation error: {e}")

    logging.info(f"Starting XML parsing for: {path}")
    _parse_dcndl_xml(str(path), handle_record)
    logging.info(f"Finished parsing. Found {len(validated_records)} valid records.")
    if error_count > 0:
        logging.warning(f"Skipped {error_count} records due to validation errors.")

    return validated_records
