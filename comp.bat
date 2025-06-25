@ECHO ON
@x:
@cd "x:/GitHub/ComicDB"
@ECHO
@python -m nuitka ^ 
--onefile ^
--output-dir=X:/GitHub/ComicDB ^
--output-filename=ComicDB.exe ^
--windows-icon-from-ico=X:/GitHub/ComicDB/images/icon.ico ^
--plugin-enable=tk-inter ^
--follow-imports ^
--show-progress ^
--assume-yes-for-downloads ^
--windows-console-mode=disable ^
--windows-company-name=Tuxxle ^
--windows-product-name=ComicDB ^
--windows-product-version=0.0.3 ^
--windows-file-version=0.0.3 ^
main.py
@pause

