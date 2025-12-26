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

# Build & Pack
./build.sh
```



## Modifications

- Added a customizable "Video Name" input field for video filename editing
  - Video titles will be automatically parsed into the format `【Display Name | tt@Username】Original Video Title` for easy organization and documentation
- Automatically paste the TikTok URL into the URL box
  - ![](https://github.com/i0Ek3/ttd/blob/main/screenshots/autopaste.jpg)
- Compile and package into the corresponding platform-specific executable version

## License

This project is a modification based on Gary19gts' Hikari TikTok Downloader, originally licensed under AGPLv3 (original license files can be found in docs/LICENSE and docs/DUAL LICENSE.). The copyright of the modified parts belongs to i0Ek3.
