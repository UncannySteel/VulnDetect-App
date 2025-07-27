import platform
import sys
import subprocess
from typing import Dict, Any

class SystemProfile:
    """
    Collects Windows OS info, kernel version, and key system component versions.
    """
    def __init__(self):
        self.profile = {}

    def collect(self) -> Dict[str, Any]:
        # Collect OS name, version, and architecture
        self.profile['os_name'] = platform.system()
        self.profile['os_version'] = platform.version()
        self.profile['architecture'] = platform.machine()
        # Kernel version
        self.profile['kernel_version'] = platform.release()
        # Key system components
        self.profile['components'] = {
            'PowerShell': self.get_powershell_version(),
            '.NET Framework': self.get_dotnet_version(),
            'Windows Defender': self.get_defender_version(),
            'Windows Update Agent': self.get_wua_version(),
        }
        return self.profile

    def get_powershell_version(self) -> str:
        # Get PowerShell version using subprocess
        try:
            output = subprocess.check_output([
                'powershell', '-Command', "$PSVersionTable.PSVersion.ToString()"
            ], stderr=subprocess.DEVNULL, text=True, timeout=5)
            return output.strip()
        except Exception:
            return 'Unknown'

    def get_dotnet_version(self) -> str:
        # Get .NET Framework version from registry using PowerShell
        try:
            cmd = (
                'powershell', '-Command',
                "Get-ChildItem 'HKLM:SOFTWARE\\Microsoft\\NET Framework Setup\\NDP\\v4\\Full' | "
                "Get-ItemPropertyValue -Name Release"
            )
            output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True, timeout=5)
            release = int(output.strip())
            # Map release key to version
            if release >= 528040:
                return '4.8 or later'
            elif release >= 461808:
                return '4.7.2'
            elif release >= 461308:
                return '4.7.1'
            elif release >= 460798:
                return '4.7'
            elif release >= 394802:
                return '4.6.2'
            elif release >= 394254:
                return '4.6.1'
            elif release >= 393295:
                return '4.6'
            else:
                return f'Release {release}'
        except Exception:
            return 'Unknown'

    def get_defender_version(self) -> str:
        # Get Windows Defender version using PowerShell
        try:
            cmd = [
                'powershell', '-Command',
                "(Get-MpComputerStatus).AMProductVersion"
            ]
            output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True, timeout=5)
            return output.strip() or 'Not Installed'
        except Exception:
            return 'Unknown'

    def get_wua_version(self) -> str:
        # Get Windows Update Agent version using PowerShell
        try:
            cmd = [
                'powershell', '-Command',
                "(New-Object -ComObject Microsoft.Update.AutoUpdate).Version"
            ]
            output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True, timeout=5)
            return output.strip()
        except Exception:
            return 'Unknown'

    def display(self):
        # Print the collected system profile in a readable format
        if not self.profile:
            self.collect()
        print(f"OS: {self.profile['os_name']} {self.profile['os_version']} ({self.profile['architecture']})")
        print(f"Kernel Version: {self.profile['kernel_version']}")
        print("Key Components:")
        for k, v in self.profile['components'].items():
            print(f"  {k}: {v}")

# Test block for standalone run/demo
'''
if __name__ == "__main__":
    # Create and display system profile
    profile = SystemProfile()
    profile.collect()
    profile.display() 
'''