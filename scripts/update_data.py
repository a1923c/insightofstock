#!/usr/bin/env python3
"""
Daily data update script for Insight of Stock
This script fetches the latest ticker and holder data from Tushare
"""

import sys
import os
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.data_service import DataService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/insightofstock_update.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def update_daily_data():
    """Main function to update all data"""
    logger.info("Starting daily data update...")
    
    service = DataService()
    
    try:
        # Update ticker information
        logger.info("Updating tickers...")
        success, message = service.update_tickers()
        if not success:
            logger.error(f"Failed to update tickers: {message}")
            return False
        logger.info(message)
        
        # Update top holders
        logger.info("Updating top holders...")
        success, message = service.update_top_holders()
        if not success:
            logger.error(f"Failed to update holders: {message}")
            return False
        logger.info(message)
        
        # Log completion
        logger.info(f"Daily data update completed successfully at {datetime.now()}")
        return True
        
    except Exception as e:
        logger.error(f"Error during data update: {e}")
        return False
    finally:
        service.close()

def main():
    """Entry point for the script"""
    logger.info("=== Insight of Stock Daily Update Started ===")
    
    start_time = datetime.now()
    
    try:
        success = update_daily_data()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if success:
            logger.info(f"Update completed successfully in {duration:.2f} seconds")
            sys.exit(0)
        else:
            logger.error(f"Update failed after {duration:.2f} seconds")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Update interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()