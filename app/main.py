"""
Main entry point for WiseDesktopNoteApp
"""

import sys
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from app.config import get_config, get_ui_config
from app.ui.main_window import MainWindow

logger = logging.getLogger(__name__)


def main():
    """Main application entry point"""
    try:
        # Get configuration (this will initialize logging)
        config = get_config()
        ui_config = get_ui_config()
        
        logger.info(f"Starting {config.name} v{config.version}")
        
        # Create Qt application
        app = QApplication(sys.argv)
        
        # Set application properties from config
        app.setApplicationName(config.name)
        app.setApplicationVersion(config.version)
        app.setOrganizationName(config.organization)
        
        # Set application-wide font - use system default if SF Pro not available
        try:
            # Try to use the configured font, but fallback gracefully
            font_family = ui_config.fonts["primary"]
            font = QFont(font_family, 10)
            
            # Check if font actually exists, if not use system default
            if not font.exactMatch():
                logger.warning(f"Font '{font_family}' not available, using system default")
                font = QFont("Helvetica", 10)  # Better fallback than SF Pro
                
            app.setFont(font)
            
        except Exception as e:
            logger.warning(f"Font setup failed: {e}, using system default")
            font = QFont("Helvetica", 10)
            app.setFont(font)
        
        # Enable high DPI support
        app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        logger.info("Application started successfully")
        
        # Run the application
        return app.exec()
        
    except Exception as e:
        logger.error(f"Fatal error during application startup: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 