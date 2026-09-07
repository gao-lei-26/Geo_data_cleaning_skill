import zipfile
from pathlib import Path
from datetime import datetime

def package_skill():
    skill_path = Path('.')
    zip_name = Path(f"geo_data_cleaning_skill_v1.0_{datetime.now().strftime('%Y%m%d')}.zip")
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in skill_path.rglob('*'):
            if file.is_file() and '__pycache__' not in str(file) and file.name != zip_name.name:
                zipf.write(file, file.relative_to(skill_path.parent))
    print(f"✅ 打包完成: {zip_name}")

if __name__ == '__main__':
    package_skill()