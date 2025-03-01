from PyInstaller.utils.hooks import collect_data_files

hiddenimports = ["numpy"]
excludedimports = ["marine", "six", "tqdm", "pyopenjtalk.htsengine"]
datas = collect_data_files("pyopenjtalk", includes=["open_jtalk_dic_utf_8-1.11"])
