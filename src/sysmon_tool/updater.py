import subprocess

class PackageUpdater:
    def __init__(self, distro="arch"):
        self.distro = distro

    def get_update_count(self) -> int:
        """Checks how many updates are pending without installing them."""
        try:
            # 'checkupdates' is a safe utility on Arch/CachyOS 
            # It checks sync databases without needing sudo
            result = subprocess.run(['checkupdates'], capture_output=True, text=True)
            if result.returncode == 0:
                updates = result.stdout.splitlines()
                return len(updates)
            return 0
        except FileNotFoundError:
            # Handle case where checkupdates utility isn't installed
            return -1 

    def get_status(self):
        count = self.get_update_count()
        if count == -1:
            return {"status": "Error", "color": "red", "message": "checkupdates not found"}
        elif count == 0:
            return {"status": "Up to date", "color": "green", "message": "System is fresh"}
        else:
            color = "yellow" if count < 20 else "red"
            return {"status": "Updates Available", "color": color, "message": f"{count} packages pending"}