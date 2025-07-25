#!/usr/bin/env python3
"""
Setup script for configuring daily cron job
"""

import os
import sys
import subprocess
import platform
from datetime import datetime

def setup_cron_job():
    """Setup cron job for daily data updates at 8:00 AM"""
    
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'update_data.py'))
    
    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        # Unix-like systems - use cron
        cron_command = f"0 8 * * * cd {os.path.dirname(script_path)} && {sys.executable} update_data.py >> /tmp/insightofstock_cron.log 2>>1"
        
        try:
            # Check if cron job already exists
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            if script_path in result.stdout:
                print("✅ Cron job already exists")
                return True
            
            # Add new cron job
            new_cron = result.stdout + f"\n{cron_command}\n"
            subprocess.run(['crontab', '-'], input=new_cron, text=True)
            print("✅ Cron job added successfully")
            print(f"   Command: {cron_command}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to setup cron job: {e}")
            return False
    
    else:
        print("⚠️  Cron setup not supported on this platform")
        print("   Please manually schedule the script: update_data.py")
        return False

def create_systemd_service():
    """Create systemd timer service for more reliable scheduling"""
    
    if platform.system() != 'Linux':
        print("⚠️  Systemd service setup only available on Linux")
        return False
    
    service_content = f"""[Unit]
Description=Insight of Stock Daily Data Update
After=network.target

[Service]
Type=oneshot
WorkingDirectory={os.path.dirname(os.path.abspath(__file__))}
ExecStart={sys.executable} update_data.py
StandardOutput=journal
StandardError=journal
"""

    timer_content = f"""[Unit]
Description=Run Insight of Stock update daily at 8:00 AM
Requires=insightofstock.service

[Timer]
OnCalendar=*-*-* 08:00:00
Persistent=true

[Install]
WantedBy=timers.target
"""

    try:
        service_path = "/etc/systemd/system/insightofstock.service"
        timer_path = "/etc/systemd/system/insightofstock.timer"
        
        # These commands would need sudo access
        print("To setup systemd timer, run these commands as root:")
        print(f"sudo tee {service_path} << 'EOF'")
        print(service_content)
        print("EOF")
        print()
        print(f"sudo tee {timer_path} << 'EOF'")
        print(timer_content)
        print("EOF")
        print()
        print("sudo systemctl daemon-reload")
        print("sudo systemctl enable insightofstock.timer")
        print("sudo systemctl start insightofstock.timer")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create systemd service: {e}")
        return False

if __name__ == "__main__":
    print("=== Insight of Stock Cron Setup ===")
    print(f"Current time: {datetime.now()}")
    
    # Setup cron job
    success = setup_cron_job()
    
    if success:
        print("\n✅ Setup completed successfully!")
        print("   Data will be updated daily at 8:00 AM")
        print("   Check logs: tail -f /tmp/insightofstock_update.log")
    else:
        print("\n❌ Manual setup required")
        print("   See instructions above for systemd timer setup")