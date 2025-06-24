@ECHO OFF
@x:
@cd "x:/GitHub/ComicDB"
@ECHO
@nuitka --onefile --output-dir=x:/GitHub/ComicDB --output-filename=ComicDB.exe --windows-icon-from-ico=x:/GitHub/ComicDB/icon.ico --plugin-enable=tk-inter --follow-imports --show-progress --windows-dependency-tool=upx --windows-company-name=Tuxxle --windows-product-name=ComicDB --windows-product-version=1.0.0 --windows-file-version=1.0.0 x:/GitHub/ComicDB/main.py
@pause
