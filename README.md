# 🎬 TTD - TikTok videos Downloader

> A modified version of [Hikari TikTok Downloader (made by Gary19gts)](https://github.com/gary19gts/Hikari-TikTok-Downloader).



![](https://github.com/i0Ek3/ttd/blob/main/screenshots/main-interface.jpg)



## How-To

```bash
# Run
git clone git@github.com:i0Ek3/ttd.git
cd ttd
python3 setup.py
python3 main.py

# Pack
# 1 Install pack tools
brew install create-dmg
pip3 install pyinstaller pyinstaller-hooks-contrib

# 2 Pack
# 2.1 Automatically pack to current architecture
./build_macos.sh

# 2.2 Specify packaging architecture
./build_macos.sh arm64 # for M chip
./build_macos.sh x86_64 # for Intel chip

# 2.3 Manually packaging
pyinstaller --clean TTD.spec
```



## Modifications

- Added a customizable "Video Name" input field for video filename editing
  - Video titles will be automatically parsed into the format `【Display Name | tt@Username】Original Video Title` for easy organization and documentation
- Automatically paste the TikTok URL into the URL box
  - ![](https://github.com/i0Ek3/ttd/blob/main/screenshots/main-inter.autopaste.jpg)

- Compile and package into the corresponding platform-specific executable version
- [WIP]
  - Batch download and queue management
  - UI interface optimization




## License

This project is a modification based on Gary19gts' Hikari TikTok Downloader, originally licensed under AGPLv3 (original license files can be found in docs/LICENSE and docs/DUAL LICENSE.). The copyright of the modified parts belongs to i0Ek3.
