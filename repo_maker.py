import os
import shutil
import hashlib
import zipfile
import re

script_name = "repo_prep.py"
revision_number = 5
homepage = 'http://forum.xbmc.org/showthread.php?tid=129401'
script_credits = 'All code copyleft (GNU GPL v3) by Unobtanium @ XBMC Forums'

compress_addons = True
repo_root = os.getcwd()  # Se asegura de que repo_root tenga un valor correcto

print(f"{script_name} v{revision_number}")
print(script_credits)
print(f"Homepage and updates: {homepage}\n")


def is_addon_dir(addon):
    return os.path.isdir(addon) and addon != ".svn"


class Generator:
    def __init__(self):
        self.addons_xml = os.path.join(repo_root, "addons.xml")
        self.addons_xml_md5 = os.path.join(repo_root, "addons.xml.md5")
        self._generate_addons_files()

    def _generate_addons_files(self):
        addons = os.listdir(repo_root)
        addons_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n'
        found_an_addon = False

        for addon in addons:
            try:
                if is_addon_dir(addon):
                    _path = os.path.join(addon, "addon.xml")
                    if os.path.exists(_path):
                        found_an_addon = True
                        with open(_path, "r", encoding="utf-8") as f:
                            xml_lines = f.read().splitlines()
                        addon_xml = "\n".join(line for line in xml_lines if "<?xml" not in line)
                        addons_xml += addon_xml.rstrip() + "\n\n"
            except Exception as e:
                print(f"Excluding {_path} for {e}")

        addons_xml = addons_xml.strip() + "\n</addons>\n"
        if found_an_addon:
            self._save_file(addons_xml.encode("utf-8"), self.addons_xml)
            self._generate_md5_file()
            print("Updated addons.xml and addons.xml.md5 files")
        else:
            print("Could not find any addons, so script has done nothing.")

    def _generate_md5_file(self):
        try:
            with open(self.addons_xml, "rb") as f:
                md5_hash = hashlib.md5(f.read()).hexdigest()
            self._save_file(md5_hash.encode("utf-8"), self.addons_xml_md5)
        except Exception as e:
            print(f"An error occurred creating addons.xml.md5 file!\n{e}")

    def _save_file(self, data, the_path):
        try:
            with open(the_path, "wb") as f:
                f.write(data)
        except Exception as e:
            print(f"An error occurred saving {the_path} file!\n{e}")


class Compressor:
    def __init__(self):
        if compress_addons:
            self.master()

    def master(self):
        for addon in os.listdir(repo_root):
            addon_path = os.path.join(repo_root, addon)
            if is_addon_dir(addon_path):
                self.addon_name = addon
                self.addon_path = addon_path
                self.addon_folder_contents = os.listdir(addon_path)

                if not self._read_addon_xml():
                    continue

                if not self._read_version_number():
                    print(f"Skipping {self.addon_name} - No version found")
                    continue

                print(f"Creating compressed addon release for {self.addon_name} v{self.addon_version_number}")
                self._create_compressed_addon_release()

    def _read_addon_xml(self):
        addon_xml_path = os.path.join(self.addon_path, "addon.xml")
        if os.path.exists(addon_xml_path):
            with open(addon_xml_path, "r", encoding="utf-8") as f:
                self.addon_xml = f.read()
            return True
        return False

    def _read_version_number(self):
        match = re.search(r'<addon.*?version="([^"]+)"', self.addon_xml)
        if match:
            self.addon_version_number = match.group(1).strip()
            return True
        return False

    def _create_compressed_addon_release(self):
        zipname = f"{self.addon_name}-{self.addon_version_number}.zip"
        zippath = os.path.join(repo_root, zipname)

        with zipfile.ZipFile(zippath, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(self.addon_path):
                for file in files:
                    filepath = os.path.join(root, file)
                    arcname = os.path.relpath(filepath, self.addon_path)
                    zipf.write(filepath, arcname)

        os.rename(zippath, os.path.join(self.addon_path, zipname))

        # Eliminar archivos innecesarios
        for file in self.addon_folder_contents:
            path = os.path.join(self.addon_path, file)
            if os.path.isdir(path):
                shutil.rmtree(path)
            elif not any(x in file for x in ["addon.xml", "changelog", "fanart", "icon", zipname]):
                os.remove(path)
            elif "changelog" in file.lower():
                new_name = f"changelog-{self.addon_version_number}.txt"
                os.rename(path, os.path.join(self.addon_path, new_name))


def execute():
    Compressor()
    Generator()


if __name__ == "__main__":
    execute()
