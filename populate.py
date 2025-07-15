import asyncio
import logging
import sys
from pathlib import Path

from src.db._model import Base
from src.db.crud import create_record
from src.db.session import get_async_session, async_engine
from src.xml_loader.loader import load_xml

project_root = Path(__file__).resolve().parent

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


async def populate():
    """
    Finds all XML files in ./init_data, loads them, and populates the database.
    """
    print("--- Starting Database Population ---")

    # 1. Find XML files
    print("1. Searching for XML files in ./init_data/...")
    init_data_dir = project_root / "init_data"
    xml_files = list(init_data_dir.glob("*.xml"))

    if not xml_files:
        logging.error("No XML files found in ./init_data/. Aborting.")
        sys.exit(1)

    print(f"   Found {len(xml_files)} XML file(s): {[f.name for f in xml_files]}")

    # 2. Create DB schema
    print("2. Creating database schema...")
    async with async_engine.begin() as conn:
        # This is idempotent, it won't recreate tables that already exist.
        await conn.run_sync(Base.metadata.create_all)
    print("   Schema created/verified.")

    # 3. Load data from all files and save to DB
    print("3. Loading and saving records from all files...")
    total_saved_count = 0
    batch_size = 1000

    async for session in get_async_session():
        for xml_file_path in xml_files:
            print(f"   - Processing file: {xml_file_path.name}")
            try:
                pydantic_records = load_xml(xml_file_path)
                print(f"     Loaded {len(pydantic_records)} records from file.")

                for p_record in pydantic_records:
                    await create_record(session, p_record)
                    total_saved_count += 1
                    if total_saved_count % batch_size == 0:
                        await session.commit()
                        print(
                            f"     ... Committed batch. Total records saved so far: {total_saved_count}"
                        )

            except Exception as e:
                logging.error(
                    f"   Failed to process file {xml_file_path.name}: {e}",
                    exc_info=True,
                )
                await session.rollback()  # Rollback on error for this file
                continue  # Move to the next file

        await session.commit()  # Commit any remaining records

    print(
        f"   Finished saving. Total records saved from all files: {total_saved_count}."
    )
    print("--- Database Population Finished ---")


if __name__ == "__main__":
    asyncio.run(populate())
