"""PyInstallerがpyopenjtalkを収集する時の動作を調整する"""

from PyInstaller.utils.hooks import collect_data_files

# marine, tqdm. htsngineはリリースビルドでは不要なので除外する
excludedimports = ["marine", "tqdm", "pyopenjtalk.htsengine"]
# 辞書ディレクトリのみを収集する
datas = collect_data_files("pyopenjtalk", includes=["open_jtalk_dic_utf_8-1.11"])
