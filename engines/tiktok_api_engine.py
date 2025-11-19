"""
TikTok API Engine for direct API downloads
Faster but may have limitations compared to yt-dlp

Copyright (C) 2025 Gary19gts

This program is dual-licensed:
1. GNU Affero General Public License v3 (AGPLv3) for open source use
2. Proprietary license for commercial/closed source use

For open source use:
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

For commercial licensing, contact Gary19gts.

Author: Gary19gts
"""

import requests
import re
import os
from pathlib import Path
import json
from html import unescape
from urllib.parse import unquote

class TikTokApiEngine:
    def __init__(self):
        self.name = "tiktok-api"
        self.description = "Direct API access for faster downloads"
        self.advantages = [
            "Faster download speed",
            "Lower resource usage",
            "Direct API access",
            "Lightweight"
        ]
        self.recommended = False
        
    def download(self, url, output_path, quality="best", progress_callback=None, status_callback=None):
        """Download TikTok content using direct API"""
        try:
            if status_callback:
                status_callback("Extracting video information...")
            
            # Extract video ID from URL
            video_id = self._extract_video_id(url)
            if not video_id:
                return False, "Could not extract video ID from URL"
            
            # Get video info
            video_info = self._get_video_info(video_id)
            if not video_info:
                return False, "Could not retrieve video information"
            
            # Get download URL
            download_url = self._get_download_url(video_info, quality)
            if not download_url:
                return False, "Could not get download URL"
            
            # Download the file
            filename = self._generate_filename(video_info)
            filepath = os.path.join(output_path, filename)
            
            if status_callback:
                status_callback(f"Downloading: {video_info.get('title', 'Unknown')}")
            
            success = self._download_file(download_url, filepath, progress_callback, status_callback)
            
            if success:
                if status_callback:
                    status_callback("Download completed successfully!")
                return True, "Download completed successfully"
            else:
                return False, "Download failed"
                
        except Exception as e:
            error_msg = f"Download failed: {str(e)}"
            if status_callback:
                status_callback(error_msg)
            return False, error_msg
    
    def _extract_video_id(self, url):
        """Extract TikTok video ID from URL"""
        patterns = [
            r'tiktok\.com/@[\w\.-]+/video/(\d+)',
            r'tiktok\.com/.*?/video/(\d+)',
            r'vm\.tiktok\.com/(\w+)',
            r'tiktok\.com/t/(\w+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def _extract_user_id(self, url):
        """
        Extract TikTok user ID (@username) from URL.
        Example: https://www.tiktok.com/@beefy_dan/video/755792...
        returns "beefy_dan"
        """

        match = re.search(r"tiktok\.com/@([\w\.-]+)/video/", url)
        if match:
            return match.group(1)
        return None
    
    def _get_video_info(self, video_id_or_url):
        """
        Try to fetch real video metadata from TikTok page.
        Accepts a video_id (digits) or a full tiktok url.
        Returns a dict like:
        {
            'id': '7557...',
            'title': 'The one and only...',
            'uploader': 'beefy_dan',
            'channel': 'BeefyDan',
            'download_urls': {'best': 'https://...mp4'}
        }
        Or returns None on failure.
        """
        # normalize: if passed only id, build a url guess (this may not always be correct)
        if re.fullmatch(r"\d+", str(video_id_or_url)):
            url = f"https://www.tiktok.com/@/video/{video_id_or_url}"
        else:
            url = video_id_or_url

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.tiktok.com/",
        }

        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            html = resp.text
        except Exception as e:
            # could not fetch page
            return None

        # helper to try loading JSON safely
        def safe_json_load(s):
            try:
                return json.loads(s)
            except Exception:
                try:
                    # sometimes JSON embedded contains HTML escapes
                    return json.loads(unescape(s))
                except Exception:
                    return None

        # Strategy A: look for <script id="__NEXT_DATA__" type="application/json">...</script>
        next_data = None
        m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S)
        if m:
            next_raw = m.group(1).strip()
            next_data = safe_json_load(next_raw)

        # Strategy B: look for a big SIGI_STATE / ItemModule-like JSON blob
        sigi = None
        if not next_data:
            # ItemModule often appears as "ItemModule":{...}
            m2 = re.search(r'"ItemModule":\s*({.+?})\s*,\s*"UserModule"', html, re.S)
            if m2:
                sigi = safe_json_load("{" + m2.group(1) + "}")
            else:
                # try a looser match: "ItemModule":{...}}
                m3 = re.search(r'"ItemModule":\s*({.+?})\s*}\s*,\s*"VideoModule"', html, re.S)
                if m3:
                    sigi = safe_json_load("{" + m3.group(1) + "}")

        # Strategy C: legacy window['SIGI_STATE'] or window['__INIT_PROPS__'] patterns
        if not next_data and not sigi:
            m4 = re.search(r'window\.__INIT_PROPS__\s*=\s*({.+?});\s*</script>', html, re.S)
            if m4:
                next_data = safe_json_load(m4.group(1))

        # Try to extract from next_data first
        info = {}
        # 1) From __NEXT_DATA__ structure
        if next_data:
            try:
                # Deep search for item info - Next data structure may vary, try common paths
                props = next_data.get('props') or next_data.get('initialProps') or {}
                pageProps = props.get('pageProps') or {}
                # itemInfo.itemStruct path (commonly)
                item_info = None
                if 'itemInfo' in pageProps and 'itemStruct' in pageProps['itemInfo']:
                    item_info = pageProps['itemInfo']['itemStruct']
                else:
                    # some variants: check for 'itemInfos' or other keys
                    # try search recursively for something that looks like an item object
                    def find_itemobj(obj):
                        if isinstance(obj, dict):
                            if 'id' in obj and 'video' in obj:
                                return obj
                            for v in obj.values():
                                res = find_itemobj(v)
                                if res:
                                    return res
                        elif isinstance(obj, list):
                            for el in obj:
                                res = find_itemobj(el)
                                if res:
                                    return res
                        return None
                    item_info = find_itemobj(pageProps)

                if item_info:
                    vid = item_info.get('id') or item_info.get('video', {}).get('id')
                    title = item_info.get('desc') or item_info.get('description') or item_info.get('title')
                    # uploader (username) often at author or authorMeta or author.id etc
                    uploader = None
                    channel = None
                    # try multiple common positions
                    for key in ('author', 'authorMeta', 'authorName', 'authorNickname'):
                        candidate = item_info.get(key)
                        if isinstance(candidate, dict):
                            uploader = candidate.get('uniqueId') or candidate.get('secUid') or candidate.get('id') or uploader
                            channel = candidate.get('nickname') or channel
                        elif isinstance(candidate, str) and not uploader:
                            uploader = candidate
                    # sometimes author fields are nested elsewhere:
                    if not uploader:
                        # try pageProps.user or other places
                        up = pageProps.get('userInfo') or pageProps.get('user')
                        if isinstance(up, dict):
                            uploader = up.get('uniqueId') or up.get('secUid') or up.get('id')
                            channel = up.get('nickname') or channel

                    # video play / download urls
                    video_obj = item_info.get('video') or {}
                    play_addr = None
                    download_addr = None
                    # playAddr or downloadAddr might be nested strings or lists
                    if isinstance(video_obj, dict):
                        play_addr = video_obj.get('playAddr') or video_obj.get('playAddrLow') or video_obj.get('playAddrCulture')
                        download_addr = video_obj.get('downloadAddr') or video_obj.get('downloadUrl')
                    # sometimes urls are nested inside 'urls' or 'progressive' keys
                    # fallback: search for anything that looks like mp4 url in the item_info
                    if not download_addr:
                        text = json.dumps(item_info)
                        m_url = re.search(r'https?://[^\s"\']+\.mp4[^\s"\']*', text)
                        if m_url:
                            download_addr = unescape(m_url.group(0))

                    # finalize
                    if vid:
                        info['id'] = vid
                    if title:
                        info['title'] = title
                    if uploader:
                        # ensure uploader doesn't include leading @
                        info['uploader'] = uploader.lstrip('@')
                    if channel:
                        info['channel'] = channel
                    if download_addr or play_addr:
                        # prefer download_addr if valid, else play_addr
                        chosen = download_addr or play_addr
                        # try unquote if escaped
                        chosen = unquote(chosen) if isinstance(chosen, str) else chosen
                        info['download_urls'] = {'best': chosen}

            except Exception:
                pass

        # 2) if not found via next_data, try ItemModule (sigi)
        if (not info.get('id') or not info.get('download_urls')) and sigi:
            try:
                # ItemModule keys are video IDs mapping to video objects
                # take first item
                if isinstance(sigi, dict):
                    # If sigi looks like {"123456": {...}}
                    for k, v in sigi.items():
                        item = v
                        info['id'] = k
                        # item may contain 'video' and 'author'
                        title = item.get('desc') or item.get('title')
                        if title:
                            info['title'] = title
                        # author info
                        author = item.get('author') or item.get('authorMeta') or {}
                        if isinstance(author, dict):
                            info['uploader'] = author.get('name') or author.get('uniqueId') or author.get('secUid')
                            info['channel'] = author.get('nickName') or author.get('nickname') or info.get('channel')
                        elif isinstance(author, str):
                            info['uploader'] = author
                        # video urls
                        vobj = item.get('video') or {}
                        dl = vobj.get('downloadAddr') or vobj.get('playAddr')
                        if dl:
                            dl = unquote(dl)
                            info['download_urls'] = {'best': dl}
                        break
            except Exception:
                pass

        # 3) final fallback: try find in page HTML via regex (raw mp4 links)
        if 'download_urls' not in info or not info.get('download_urls'):
            m_mp4 = re.search(r'https://[^\s"\']+\.mp4[^\s"\']*', html)
            if m_mp4:
                link = unquote(m_mp4.group(0))
                info.setdefault('download_urls', {})['best'] = link

        # make sure we have minimally id and a url
        if not info.get('id'):
            # try extract id from url path
            m_id = re.search(r'/video/(\d+)', url)
            if m_id:
                info['id'] = m_id.group(1)

        # if uploader not found, try extract from URL like /@username/
        if not info.get('uploader'):
            m_user = re.search(r'tiktok\.com/@([\w\.-]+)', url)
            if m_user:
                info['uploader'] = m_user.group(1)

        # fill defaults
        if 'title' not in info:
            info['title'] = f'TikTok_Video_{info.get("id","unknown")}'
        if 'channel' not in info:
            # attempt to derive a nicer display name from uploader if absent
            uid = info.get('uploader')
            if uid:
                info['channel'] = uid.replace('_', ' ').title()

        # final validation
        if 'download_urls' not in info or not info['download_urls'].get('best'):
            # no usable video url found
            return None

        return info
    
    def _get_download_url(self, video_info, quality):
        """Get highest quality download URL available"""
        download_urls = video_info.get('download_urls', {})
        
        # Always return the best available quality
        if 'best' in download_urls:
            return download_urls['best']
        else:
            return None
    
    def _generate_filename(self, video_info):
        """
        Generate filename in format:【 channel | tt@uploader】title.mp4
        """

        channel = video_info.get('channel', None)
        uploader = video_info.get('uploader', None)
        title = video_info.get('title', 'TikTok_Video')

        if not channel:
            channel = uploader or "UnknownUser"
        if not uploader:
            uploader = "unknown_id"

        # Clean illegal filename characters
        def safe(text):
            return re.sub(r'[<>:"/\\|?*]', '_', text)

        channel_safe = safe(channel)
        uploader_safe = safe(uploader)
        title_safe = safe(title)

        filename = f"【{channel_safe} | tt@{uploader_safe}】{title_safe}.mp4"
        return filename
    
    def _download_file(self, url, filepath, progress_callback=None, status_callback=None):
        """Download file with progress tracking"""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            percent = (downloaded / total_size) * 100
                            progress_callback(percent)
                            
                        if status_callback and total_size > 0:
                            percent = (downloaded / total_size) * 100
                            status_callback(f"Downloading... {percent:.1f}%")
            
            return True
            
        except Exception:
            return False
    
    def validate_url(self, url):
        """Validate if URL is supported"""
        video_id = self._extract_video_id(url)
        if video_id:
            return True, f"TikTok video detected (ID: {video_id})"
        else:
            return False, "Invalid TikTok URL format"
    
    def get_info(self):
        """Get engine information"""
        return {
            'name': self.name,
            'description': self.description,
            'advantages': self.advantages,
            'recommended': self.recommended
        }